"""
Fetch GitHub user stats via GraphQL and write JSON for the stats card.
Uses GITHUB_TOKEN and GITHUB_USERNAME (or repo owner in Actions).
Stdlib only: urllib, json.
"""

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

# Default output path; can be overridden.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
DEFAULT_OUTPUT = os.path.join(SCRIPT_DIR, "stats.json")
GRAPHQL_URL = "https://api.github.com/graphql"

# Load .env from repo root so GITHUB_TOKEN / GITHUB_USERNAME can be set there.
sys.path.insert(0, SCRIPT_DIR)
import config  # noqa: E402


def get_username() -> str:
    """Username: env GITHUB_USERNAME, else fail with clear message (Actions sets it)."""
    username = os.environ.get("GITHUB_USERNAME", "").strip()
    if not username:
        print("Error: GITHUB_USERNAME is not set.", file=sys.stderr)
        sys.exit(1)
    return username


def get_token() -> str:
    """GITHUB_TOKEN required for GraphQL."""
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if not token:
        print("Error: GITHUB_TOKEN is not set.", file=sys.stderr)
        sys.exit(1)
    return token


def graphql_request(token: str, query: str, variables: dict | None = None) -> dict:
    """POST a GraphQL request and return the JSON body."""
    body = {"query": query}
    if variables:
        body["variables"] = variables
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        GRAPHQL_URL,
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            out = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        print(f"GraphQL HTTP error {e.code}: {body}", file=sys.stderr)
        sys.exit(1)
    if "errors" in out:
        print("GraphQL errors:", out["errors"], file=sys.stderr)
        sys.exit(1)
    return out.get("data", {})


def last_year_dates() -> tuple[str, str]:
    """Return (from, to) in ISO format for the last 365 days."""
    now = datetime.now(timezone.utc)
    to_dt = now.replace(hour=0, minute=0, second=0, microsecond=0)
    from_dt = to_dt.replace(year=to_dt.year - 1)
    return from_dt.strftime("%Y-%m-%dT00:00:00Z"), to_dt.strftime("%Y-%m-%dT23:59:59Z")


def fetch_user_and_contributions(token: str, username: str) -> dict:
    """One query: user name, login, PR/issue counts, and contributionsCollection for last year."""
    from_iso, to_iso = last_year_dates()
    query = """
    query($login: String!, $from: DateTime!, $to: DateTime!) {
      user(login: $login) {
        name
        login
        pullRequests(first: 1) { totalCount }
        issues(first: 1) { totalCount }
        contributionsCollection(from: $from, to: $to) {
          totalCommitContributions
          totalRepositoriesWithContributedCommits
        }
      }
    }
    """
    variables = {"login": username, "from": from_iso, "to": to_iso}
    data = graphql_request(token, query, variables)
    return data.get("user") or {}


def fetch_total_stars(token: str, username: str) -> int:
    """Paginate user.repositories (owner only) and sum stargazerCount."""
    total = 0
    cursor = None
    query = """
    query($login: String!, $after: String) {
      user(login: $login) {
        repositories(first: 100, ownerAffiliations: OWNER, after: $after) {
          nodes { stargazerCount }
          pageInfo { endCursor hasNextPage }
        }
      }
    }
    """
    while True:
        variables = {"login": username, "after": cursor}
        data = graphql_request(token, query, variables)
        user = data.get("user") or {}
        repos = user.get("repositories") or {}
        nodes = repos.get("nodes") or []
        for node in nodes:
            total += node.get("stargazerCount") or 0
        page_info = repos.get("pageInfo") or {}
        if not page_info.get("hasNextPage"):
            break
        cursor = page_info.get("endCursor")
        if not cursor:
            break
    return total


def main() -> None:
    token = get_token()
    username = get_username()

    user = fetch_user_and_contributions(token, username)
    if not user:
        print(f"Error: User '{username}' not found.", file=sys.stderr)
        sys.exit(1)

    stars = fetch_total_stars(token, username)
    collection = (user.get("contributionsCollection") or {})
    commits_last_year = collection.get("totalCommitContributions") or 0
    repos_contributed = collection.get("totalRepositoriesWithContributedCommits") or 0
    pull_requests = (user.get("pullRequests") or {}).get("totalCount") or 0
    issues = (user.get("issues") or {}).get("totalCount") or 0

    display_name = (user.get("name") or user.get("login") or username).strip()

    payload = {
        "username": username,
        "name": display_name,
        "stars": stars,
        "commits_last_year": commits_last_year,
        "pull_requests": pull_requests,
        "issues": issues,
        "repos_contributed_last_year": repos_contributed,
    }

    output_path = os.environ.get("STATS_OUTPUT", DEFAULT_OUTPUT)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"Wrote stats to {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()

"""
Configuration for GitHub profile stats card: theme, dimensions, and grade formula.
Tweak these to change appearance or add/remove metrics without touching core logic.
"""

import os

_script_dir = os.path.dirname(os.path.abspath(__file__))
_repo_root = os.path.dirname(_script_dir)


def load_dotenv() -> None:
    """Load .env from repo root into os.environ (setdefault: existing env wins). Stdlib only."""
    path = os.path.join(_repo_root, ".env")
    if not os.path.isfile(path):
        return
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                k, v = k.strip(), v.strip()
                if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
                    v = v[1:-1]
                os.environ.setdefault(k, v)


load_dotenv()

# ----- Username -----
# Override via GITHUB_USERNAME env or .env; in Actions, workflow passes github.repository_owner.
GITHUB_USERNAME = os.environ.get("GITHUB_USERNAME", "").strip()

# ----- Theme (dark card) -----
THEME = {
    "background": "#0d1117",
    "border": "#30363d",
    "text": "#e6edf3",
    "text_muted": "#8b949e",
    "accent": "#58a6ff",
    "circle_bg": "#21262d",
    "circle_fill": "#58a6ff",
    "icon": "#8b949e",
}

# Optional light theme (set THEME to LIGHT_THEME in render script if desired).
LIGHT_THEME = {
    "background": "#ffffff",
    "border": "#d0d7de",
    "text": "#1f2328",
    "text_muted": "#656d76",
    "accent": "#0969da",
    "circle_bg": "#f6f8fa",
    "circle_fill": "#0969da",
    "icon": "#656d76",
}

# ----- Card dimensions (stats only; no score circle); height fits 5 rows with equal padding -----
CARD_WIDTH = 340
CARD_HEIGHT = 182
BORDER_RADIUS = 12
PADDING = 20

# ----- Grade formula -----
# Each metric is normalized to [0, 1] by min(1, value / cap), then weighted.
# Grade = sum(weight * score) * 100, clamped to 0–100.
FORMULA_CAPS = {
    "stars": 500,
    "commits_last_year": 365,
    "pull_requests": 200,
    "issues": 100,
    "repos_contributed_last_year": 24,
}
FORMULA_WEIGHTS = {
    "stars": 0.25,
    "commits_last_year": 0.30,
    "pull_requests": 0.20,
    "issues": 0.10,
    "repos_contributed_last_year": 0.15,
}

# Letter grade bands (optional display in circle).
GRADE_LETTERS = [
    (90, "A"),
    (80, "B"),
    (70, "C"),
    (60, "D"),
    (0, "F"),
]

# ----- Paths (relative to repo root) -----
DEFAULT_STATS_JSON = "scripts/stats.json"
DEFAULT_OUTPUT_SVG = "assets/github-stats.svg"

"""
Read stats JSON and config, render the GitHub stats card as SVG.
Output: assets/github-stats.svg (path configurable via config or env).
"""

import json
import os
import sys

# Resolve paths relative to repo root (parent of scripts/).
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)

# Import config from scripts/ (same directory as this file).
sys.path.insert(0, SCRIPT_DIR)
import config as cfg


def load_stats(stats_path: str) -> dict:
    """Load stats JSON from path (relative to repo root or absolute)."""
    if not os.path.isabs(stats_path):
        stats_path = os.path.join(REPO_ROOT, stats_path)
    with open(stats_path, encoding="utf-8") as f:
        return json.load(f)


# ----- Inline SVG icons (simple, no external assets) -----
def icon_star(color: str, size: int = 16) -> str:
    # 5-point star (filled).
    s = size / 2
    # Points approximating a star centered at (s,s).
    points = [
        (s, 0),
        (s * 1.2, s * 0.7),
        (size, s),
        (s * 1.2, s * 1.3),
        (s * 1.1, size),
        (s, s * 1.2),
        (s * 0.9, size),
        (s * 0.8, s * 1.3),
        (0, s),
        (s * 0.8, s * 0.7),
    ]
    pts = " ".join(f"{x},{y}" for x, y in points)
    return f'<polygon points="{pts}" fill="{color}" />'


def icon_commit(color: str, size: int = 16) -> str:
    cx = cy = size / 2
    r = size / 4
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color}" stroke-width="2"/>'


def icon_pull_request(color: str, size: int = 16) -> str:
    # Branch + arrow: simple path.
    s = size
    return (
        f'<path d="M{s*0.5} {s*0.2} L{s*0.5} {s*0.5} L{s*0.2} {s*0.5} L{s*0.5} {s*0.2} '
        f'M{s*0.5} {s*0.8} L{s*0.5} {s*0.5} L{s*0.8} {s*0.5}" fill="none" stroke="{color}" stroke-width="1.5" stroke-linecap="round"/>'
    )


def icon_issue(color: str, size: int = 16) -> str:
    cx = cy = size / 2
    r = size / 3
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color}" stroke-width="2"/>'


def icon_repo(color: str, size: int = 16) -> str:
    # Two stacked rectangles (repo/books).
    w, h = size * 0.7, size * 0.35
    x = (size - w) / 2
    return (
        f'<rect x="{x}" y="{size*0.2}" width="{w}" height="{h}" rx="1" fill="none" stroke="{color}" stroke-width="1.5"/>'
        f'<rect x="{x}" y="{size*0.55}" width="{w}" height="{h}" rx="1" fill="none" stroke="{color}" stroke-width="1.5"/>'
    )


# Row: (label, value_key, icon_fn).
STAT_ROWS = [
    ("Stars (my repos)", "stars", icon_star),
    ("Commits (last year)", "commits_last_year", icon_commit),
    ("Pull requests", "pull_requests", icon_pull_request),
    ("Issues", "issues", icon_issue),
    ("Contributed to (last year)", "repos_contributed_last_year", icon_repo),
]


def render_svg(stats: dict, theme: dict) -> str:
    """Build the full SVG string (stats card only, no score circle)."""
    w = cfg.CARD_WIDTH
    h = cfg.CARD_HEIGHT
    r = cfg.BORDER_RADIUS
    pad = cfg.PADDING
    icon_color = theme["icon"]
    text_color = theme["text"]
    text_muted = theme["text_muted"]
    bg = theme["background"]
    border = theme["border"]

    name = stats.get("name") or stats.get("username") or "User"
    title = f"{name}'s GitHub Stats"

    # Equal padding on all sides: value column ends at w - pad (group is translated by pad, so local x = w - 2*pad).
    value_x = w - 2 * pad
    title_y = pad + 16  # baseline so title sits pad from top
    row_height = 26
    row_y_start = title_y + 20  # gap below title; first row content top at row_y_start - 14

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
        f'  <rect width="{w}" height="{h}" rx="{r}" ry="{r}" fill="{bg}" stroke="{border}" stroke-width="1"/>',
        f'  <text x="{pad}" y="{title_y}" font-family="system-ui, -apple-system, sans-serif" font-size="16" font-weight="700" fill="{text_color}">{_escape(title)}</text>',
    ]

    row_y = row_y_start
    for label, key, icon_fn in STAT_ROWS:
        value = stats.get(key, 0)
        if value is None:
            value = 0
        value_str = str(value)
        if len(value_str) > 6:
            value_str = value_str[:5] + "…"
        icon_svg = icon_fn(icon_color, 16)
        lines.append(f'  <g transform="translate({pad}, {row_y - 14})">')
        lines.append(f'    {icon_svg}')
        lines.append(f'    <text x="24" y="12" font-family="system-ui, sans-serif" font-size="13" fill="{text_muted}">{_escape(label)}</text>')
        lines.append(f'    <text x="{value_x}" y="12" text-anchor="end" font-family="system-ui, monospace" font-size="13" font-weight="600" fill="{text_color}">{_escape(value_str)}</text>')
        lines.append("  </g>")
        row_y += row_height

    lines.append("</svg>")
    return "\n".join(lines)


def _escape(s: str) -> str:
    """Escape for SVG text content."""
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def main() -> None:
    stats_path = cfg.DEFAULT_STATS_JSON
    if len(sys.argv) > 1:
        stats_path = sys.argv[1]
    out_path = os.environ.get("STATS_SVG_OUTPUT", cfg.DEFAULT_OUTPUT_SVG)
    if not os.path.isabs(out_path):
        out_path = os.path.join(REPO_ROOT, out_path)

    if not os.path.isfile(os.path.join(REPO_ROOT, stats_path) if not os.path.isabs(stats_path) else stats_path):
        print(f"Error: Stats file not found: {stats_path}", file=sys.stderr)
        sys.exit(1)

    stats = load_stats(stats_path)
    theme = cfg.THEME
    svg = render_svg(stats, theme)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Wrote SVG to {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()

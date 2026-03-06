# Profile stats scripts

This folder contains the scripts that power the self-contained GitHub profile stats card.

## What they do

- **`fetch_stats.py`** — Fetches your GitHub stats via the GraphQL API and writes `stats.json`.
- **`render_stats_svg.py`** — Reads `stats.json` and config, then generates `assets/github-stats.svg`.

Theme, dimensions, and the grade formula are in **`config.py`**; edit that file to change appearance or weights without touching the main logic.

## Run locally

1. **Set credentials (pick one)**
   - **Option A — .env file (recommended):** Copy `.env.example` to `.env` in the repo root and set `GITHUB_TOKEN` and `GITHUB_USERNAME`. `.env` is gitignored.
   - **Option B — environment variables:** Set `GITHUB_TOKEN` and `GITHUB_USERNAME` in your shell before running.

2. **From the repo root**
   ```bash
   python scripts/fetch_stats.py
   python scripts/render_stats_svg.py
   ```

3. **View the card**
   - Open `assets/github-stats.svg` in a browser, or commit and push to see it on your profile README.

## Optional env vars

- `STATS_OUTPUT` — Where `fetch_stats.py` writes JSON (default: `scripts/stats.json`).
- `STATS_SVG_OUTPUT` — Where `render_stats_svg.py` writes the SVG (default: `assets/github-stats.svg`).

## Add or remove metrics

1. In **`fetch_stats.py`**: add/remove the field in the GraphQL query and in the `payload` dict written to JSON.
2. In **`config.py`**: add/remove entries in `FORMULA_CAPS` and `FORMULA_WEIGHTS` (and `GRADE_LETTERS` if you use them).
3. In **`render_stats_svg.py`**: add/remove a row in `STAT_ROWS` (label, value key, icon function).

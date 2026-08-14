#!/usr/bin/env python3
"""Regenerate the live sections of the profile README and the stats strip.

Only the text between <!-- auto:NAME --> / <!-- /auto:NAME --> markers is
touched, so the hand-written prose around them survives every run.
"""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

USER = "Booyaka101"
RADAR = "https://booyaka101.github.io/hass-breakage-radar/index.json"
FABLE = "https://booyaka101.github.io/thedailyfable/feed.xml"
ROOT = Path(__file__).resolve().parent.parent

# Daily Fable palette.
BG, FG, DIM, LINE, ACC = "#05060a", "#d6dbe6", "#8a93a6", "#1a1e28", "#4fb3ff"
BG_L, FG_L, DIM_L, LINE_L, ACC_L = "#ffffff", "#1f2328", "#59636e", "#d1d9e0", "#0969da"


def get(url: str, token: str | None = None) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": f"{USER}-profile"})
    if token:
        req.add_header("Authorization", f"Bearer {token}")
        req.add_header("Accept", "application/vnd.github+json")
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def upstream_stats(token: str | None) -> dict:
    """Merged and open PRs to repos that aren't mine."""
    rows = []
    for page in range(1, 6):
        url = (
            "https://api.github.com/search/issues?per_page=100&page="
            f"{page}&q=type:pr+author:{USER}"
        )
        data = json.loads(get(url, token))
        items = data.get("items", [])
        rows.extend(items)
        if len(items) < 100:
            break

    merged, open_, repos = 0, 0, {}
    for it in rows:
        repo = it["repository_url"].split("/repos/", 1)[1]
        if repo.lower().startswith(f"{USER.lower()}/"):
            continue
        if it.get("pull_request", {}).get("merged_at"):
            merged += 1
            repos[repo] = repos.get(repo, 0) + 1
        elif it.get("state") == "open":
            open_ += 1
    # Rank by upstream reach, not by how many PRs I happened to send. A single
    # fix to a well-known project says more than nine to an obscure one.
    ranked = []
    for repo, n in repos.items():
        try:
            stars = json.loads(get(f"https://api.github.com/repos/{repo}", token)).get(
                "stargazers_count", 0
            )
        except (urllib.error.URLError, json.JSONDecodeError, TimeoutError):
            stars = 0
        ranked.append((repo, n, stars))
    ranked.sort(key=lambda r: (-r[2], -r[1], r[0]))
    return {
        "merged": merged,
        "open": open_,
        "projects": len(repos),
        "top": [(r, n) for r, n, _ in ranked],
    }


def radar_stats() -> dict | None:
    try:
        d = json.loads(get(RADAR))
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError):
        return None
    cov = d.get("coverage", {})
    releases = d.get("releases", {})
    nxt, nxt_n = None, 0
    for rel in sorted(releases):
        if releases[rel]:
            nxt, nxt_n = rel, len(releases[rel])
            break
    return {
        "scanned": cov.get("repos_scanned", 0),
        "affected": cov.get("repos_affected", 0),
        "clean": cov.get("repos_clean", 0),
        "findings": cov.get("findings_total", 0),
        "rules": cov.get("rules_published", 0),
        "core": d.get("core_version", "?"),
        "next_release": nxt,
        "next_count": nxt_n,
        "generated": d.get("generated_utc", ""),
    }


def fable_latest() -> dict | None:
    try:
        root = ET.fromstring(get(FABLE))
    except (urllib.error.URLError, ET.ParseError, TimeoutError):
        return None
    items = root.findall("./channel/item")
    if not items:
        return None
    first = items[0]
    title = (first.findtext("title") or "").strip()
    link = (first.findtext("link") or "").strip()
    raw = (first.findtext("pubDate") or "").strip()
    try:
        date = parsedate_to_datetime(raw).strftime("%Y-%m-%d")
    except (TypeError, ValueError):
        date = ""
    day = 0
    m = re.search(r"Day\s+(\d+)", title)
    if m:
        day = int(m.group(1))
    return {"title": title, "link": link, "date": date, "day": day, "count": len(items)}


def esc(s: str) -> str:
    return (
        s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    )


def strip_svg(cells: list[tuple[str, str]], dark: bool) -> str:
    """A row of value/label tiles in the Daily Fable terminal style."""
    bg, fg, dim, line, acc = (
        (BG, FG, DIM, LINE, ACC) if dark else (BG_L, FG_L, DIM_L, LINE_L, ACC_L)
    )
    pad, gap, h = 20, 30, 78
    # Monospace advance widths for the two type sizes, plus label letter-spacing.
    widths = [
        max(len(value) * 12.7, len(label) * 7.7) for value, label in cells
    ]
    w = int(pad * 2 + sum(widths) + gap * (len(cells) - 1))
    mono = "ui-monospace,'Cascadia Code',Consolas,'DejaVu Sans Mono',monospace"

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-label="Live project stats">',
        f'<rect width="{w}" height="{h}" rx="8" fill="{bg}" stroke="{line}"/>',
    ]
    x = float(pad)
    for i, (value, label) in enumerate(cells):
        if i:
            lx = round(x - gap / 2)
            parts.append(
                f'<line x1="{lx}" y1="18" x2="{lx}" y2="{h - 18}" stroke="{line}"/>'
            )
        x = round(x, 1)
        parts.append(
            f'<text x="{x}" y="34" font-family="{mono}" font-size="21" '
            f'fill="{acc}" font-weight="600">{esc(value)}</text>'
        )
        parts.append(
            f'<text x="{x}" y="55" font-family="{mono}" font-size="11" '
            f'fill="{dim}" letter-spacing="1.1">{esc(label)}</text>'
        )
        x += widths[i] + gap
    parts.append("</svg>")
    return "\n".join(parts)


def replace_block(text: str, name: str, body: str) -> str:
    open_, close = f"<!-- auto:{name} -->", f"<!-- /auto:{name} -->"
    pattern = re.compile(
        re.escape(open_) + r".*?" + re.escape(close), re.DOTALL
    )
    if not pattern.search(text):
        raise SystemExit(f"marker block '{name}' not found in README")
    return pattern.sub(f"{open_}\n{body}\n{close}", text)


def main() -> int:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    up = upstream_stats(token)
    radar = radar_stats()
    fable = fable_latest()

    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    # Upstream ledger.
    named = ", ".join(
        f"{r.split('/')[-1]}{f' ({n})' if n > 1 else ''}" for r, n in up["top"][:10]
    )
    ledger = (
        f"When I depend on something and hit a real bug, I send the fix back. "
        f"**{up['merged']} merged PRs across {up['projects']} projects**, including "
        f"{named}. {up['open']} more open."
    )
    readme = replace_block(readme, "upstream", ledger)

    # Radar telemetry.
    if radar:
        nxt = ""
        if radar["next_release"]:
            nxt = (
                f" Next up: **{radar['next_count']}** break in Home Assistant "
                f"{radar['next_release']}."
            )
        readme = replace_block(
            readme,
            "radar",
            f"> Today's crawl checked **{radar['scanned']:,}** HACS integrations against "
            f"core {radar['core']} and found **{radar['findings']:,}** deprecation hits "
            f"across **{radar['affected']:,}** repos. **{radar['clean']:,}** are clean."
            f"{nxt}",
        )

    # Latest Daily Fable.
    if fable:
        readme = replace_block(
            readme,
            "fable",
            f"> Latest: [{fable['title']}]({fable['link']}) · {fable['date']} · "
            f"{fable['count']} pieces so far.",
        )

    cells = []
    if up["merged"]:
        cells.append((str(up["merged"]), "MERGED UPSTREAM"))
    if radar:
        cells.append((f"{radar['scanned']:,}", "INTEGRATIONS WATCHED"))
        cells.append((f"{radar['affected']:,}", "BREAKING AHEAD"))
    if fable and fable["day"]:
        cells.append((f"DAY {fable['day']}", "DAILY FABLE STREAK"))

    if cells:
        assets = ROOT / "assets"
        assets.mkdir(exist_ok=True)
        (assets / "stats-dark.svg").write_text(strip_svg(cells, True), encoding="utf-8")
        (assets / "stats-light.svg").write_text(
            strip_svg(cells, False), encoding="utf-8"
        )

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    readme = replace_block(readme, "stamp", f"<sub>Live figures, rebuilt {stamp}.</sub>")

    (ROOT / "README.md").write_text(readme, encoding="utf-8")
    print(
        f"upstream merged={up['merged']} projects={up['projects']} open={up['open']}\n"
        f"radar={'ok' if radar else 'unavailable'} fable={'ok' if fable else 'unavailable'}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

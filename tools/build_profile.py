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

import viz

USER = "Booyaka101"
RADAR = "https://booyaka101.github.io/hass-breakage-radar/index.json"
FABLE = "https://booyaka101.github.io/thedailyfable/feed.xml"
CENSUS = ("https://raw.githubusercontent.com/Booyaka101/npm-install-census/"
          "main/data/census.json")
ROOT = Path(__file__).resolve().parent.parent


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


def _relkey(rel: str) -> tuple:
    """Sort '2026.9' before '2026.10' (string sort gets this wrong)."""
    try:
        return tuple(int(p) for p in rel.split("."))
    except ValueError:
        return (9999,)


def radar_stats() -> dict | None:
    try:
        d = json.loads(get(RADAR))
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError):
        return None
    cov = d.get("coverage", {})
    # Bucket each integration by the FIRST release that breaks it. The
    # `releases` map counts an integration once per breaking release, so it
    # over-counts (657 vs 625 affected); this sums to the affected total.
    first: dict[str, int] = {}
    for it in d.get("integrations", []):
        rel = it.get("earliest_breaks_in")
        if rel:
            first[rel] = first.get(rel, 0) + 1
    buckets = sorted(first.items(), key=lambda kv: _relkey(kv[0]))

    nxt, nxt_n = (buckets[0] if buckets else (None, 0))
    return {
        "buckets": buckets,
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


def census_stats() -> dict | None:
    try:
        d = json.loads(get(CENSUS))
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError):
        return None
    if d.get("coverage", 1) < 0.95:  # the census aborts below this; don't show a partial
        return None
    top = (d.get("top_risky") or [{}])[0]
    return {
        "total": d.get("total", 0),
        "scripted": d.get("with_install_scripts", 0),
        "high": (d.get("risk") or {}).get("HIGH", 0),
        "top_name": top.get("name"),
        "top_downloads": top.get("downloads", 0),
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
    census = census_stats()

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

    if census:
        line = (
            f"> Today's census audited **{census['total']:,}** packages from the "
            f"registry: **{census['scripted']}** run an install script, "
            f"**{census['high']}** score HIGH."
        )
        if census["top_name"]:
            line += (
                f" Biggest is `{census['top_name']}` at "
                f"{census['top_downloads'] / 1e6:.1f}M installs a week."
            )
        readme = replace_block(readme, "census", line)

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
    if census:
        cells.append((str(census["scripted"]), "NPM INSTALL SCRIPTS"))
    if fable and fable["day"]:
        cells.append((f"DAY {fable['day']}", "DAILY FABLE STREAK"))

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    assets = ROOT / "assets"
    assets.mkdir(exist_ok=True)

    if cells:
        seed = f"seed {stamp}"
        for dark, name in ((True, "hero-dark.svg"), (False, "hero-light.svg")):
            (assets / name).write_text(
                viz.hero(cells, seed, dark), encoding="utf-8"
            )

    if radar and radar["buckets"]:
        for dark, name in ((True, "breakage-dark.svg"), (False, "breakage-light.svg")):
            (assets / name).write_text(
                viz.breakage_chart(radar["buckets"], radar["core"], dark),
                encoding="utf-8",
            )

    readme = replace_block(readme, "stamp", f"<sub>Live figures, rebuilt {stamp}.</sub>")

    (ROOT / "README.md").write_text(readme, encoding="utf-8")
    print(
        f"upstream merged={up['merged']} projects={up['projects']} open={up['open']}\n"
        f"radar={'ok' if radar else 'unavailable'} fable={'ok' if fable else 'unavailable'}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

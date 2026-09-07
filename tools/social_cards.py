#!/usr/bin/env python3
"""Render an OpenGraph card for every repo I own.

GitHub has no API for the social preview, so this only builds the images;
tools/set_social_preview.mjs uploads them through a signed-in browser.

    python tools/social_cards.py            # every repo
    python tools/social_cards.py ts7-compat-guard uv-cache-warden
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request
from pathlib import Path

import rasterize
import viz

USER = "Booyaka101"
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "cards"
# GitHub rejects a social preview over 1MB.
MAX_BYTES = 1_000_000
# Community health files, never shared as a link.
SKIP = {".github"}


def api(path: str) -> object:
    req = urllib.request.Request(
        f"https://api.github.com{path}",
        headers={
            "User-Agent": f"{USER}-cards",
            "Accept": "application/vnd.github+json",
        },
    )
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def repos() -> list[dict]:
    out, page = [], 1
    while True:
        batch = api(f"/users/{USER}/repos?per_page=100&page={page}&sort=pushed")
        out.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return [
        r
        for r in out
        if not r["fork"]
        and not r["archived"]
        and r["name"] not in SKIP
        and (r.get("description") or "").strip()
    ]


def footer(repo: dict) -> str:
    """One line of how you'd actually get the thing."""
    home = (repo.get("homepage") or "").strip()
    if "npmjs.com/package/" in home:
        return f"npm i {home.split('npmjs.com/package/', 1)[1].strip('/')}"
    if "pypi.org/project/" in home:
        return f"pip install {home.split('pypi.org/project/', 1)[1].strip('/')}"
    if home:
        return home.split("://", 1)[-1].rstrip("/")
    return f"github.com/{repo['full_name']}"


def chips(repo: dict, budget: int = 44) -> list[str]:
    picked: list[str] = []
    for topic in repo.get("topics") or []:
        cand = picked + [topic]
        if len(" · ".join(cand)) > budget:
            break
        picked = cand
    if not picked and repo.get("language"):
        picked = [repo["language"].lower()]
    return picked


def main(argv: list[str]) -> int:
    wanted = set(argv)
    todo = [r for r in repos() if not wanted or r["name"] in wanted]
    if wanted:
        missing = wanted - {r["name"] for r in todo}
        if missing:
            raise SystemExit(f"no such repo (or no description): {sorted(missing)}")
    OUT.mkdir(exist_ok=True)

    for repo in todo:
        name = repo["name"]
        svg = OUT / f"{name}.svg"
        svg.write_text(
            viz.social_card(
                USER, name, repo["description"].strip(), footer(repo), chips(repo)
            ),
            encoding="utf-8",
        )
        png = rasterize.png(svg, OUT / f"{name}.png", 1280, 640, at_ms=400)
        size = png.stat().st_size
        flag = "  OVER 1MB" if size > MAX_BYTES else ""
        print(f"{name:38} {size / 1024:7.0f} KB{flag}")
        svg.unlink()

    print(f"\n{len(todo)} cards in {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

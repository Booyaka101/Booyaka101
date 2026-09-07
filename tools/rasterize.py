#!/usr/bin/env python3
"""Rasterise an SVG to PNG with headless Chrome.

The SVG is loaded through an <img> so it renders under the same restrictions
GitHub applies (no script, no external fetch), and so a virtual-time budget can
advance CSS animations to a chosen frame before the capture.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

CANDIDATES = [
    os.environ.get("CHROME"),
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    "google-chrome",
    "chromium",
]


def chrome() -> str:
    for cand in CANDIDATES:
        if not cand:
            continue
        found = shutil.which(cand) or (cand if Path(cand).exists() else None)
        if found:
            return found
    raise SystemExit("no chrome binary found; set CHROME")


def png(svg: Path, out: Path, w: int, h: int, at_ms: int = 1200) -> Path:
    """Render `svg` at `w`x`h`, `at_ms` into its animation."""
    with tempfile.TemporaryDirectory() as tmp:
        page = Path(tmp) / "page.html"
        page.write_text(
            "<!doctype html><meta charset=utf-8>"
            "<style>html,body{margin:0;padding:0;background:transparent}"
            f"img{{display:block;width:{w}px;height:{h}px}}</style>"
            f'<img src="{svg.resolve().as_uri()}">',
            encoding="utf-8",
        )
        out.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [
                chrome(),
                "--headless=new",
                "--disable-gpu",
                "--hide-scrollbars",
                "--force-device-scale-factor=1",
                "--default-background-color=00000000",
                f"--user-data-dir={tmp}/profile",
                f"--window-size={w},{h}",
                # Virtual time runs the animation forward without waiting for it,
                # so the frame is deterministic rather than whatever the machine
                # happened to be showing when the shot fired.
                f"--virtual-time-budget={at_ms}",
                f"--screenshot={out.resolve()}",
                page.as_uri(),
            ],
            check=True,
            capture_output=True,
            timeout=120,
        )
    if not out.exists():
        raise SystemExit(f"chrome produced no output for {svg}")
    return out

"""Hand-rolled SVG renderers. No dependencies, nothing fetched at display time.

Three pieces, all off the same flow field and the same palette:
  hero()  a deterministic banner, seeded by the date, with the headline figures
          on a scrim along the bottom
  social_card()  a 1280x640 OpenGraph card for one repo
  breakage_chart()  a column chart of when HACS integrations first break
"""
from __future__ import annotations

import math
import random
from typing import Iterator

# Daily Fable palette, plus light-mode steps that clear 3:1 on white.
DARK = {
    "bg": "#05060a",
    "fg": "#d6dbe6",
    "dim": "#8a93a6",
    "line": "#1a1e28",
    "acc": "#4fb3ff",
}
LIGHT = {
    "bg": "#ffffff",
    "fg": "#1f2328",
    "dim": "#59636e",
    "line": "#d1d9e0",
    # #4fb3ff is only 2.28:1 on white, below the 3:1 mark floor, so light mode
    # steps down to a darker blue at 5.19:1.
    "acc": "#0969da",
}
MONO = "ui-monospace,'Cascadia Code',Consolas,'DejaVu Sans Mono',monospace"


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# --------------------------------------------------------------------------
# Value noise. A seeded gradient grid with smoothstep interpolation, which is
# all the flow field needs and avoids pulling in numpy for a 900px banner.
# --------------------------------------------------------------------------
class Noise:
    def __init__(self, rng: random.Random, size: int = 16):
        self.n = size
        self.g = [
            [
                (lambda a: (math.cos(a), math.sin(a)))(rng.uniform(0, math.tau))
                for _ in range(size)
            ]
            for _ in range(size)
        ]

    def _dot(self, ix: int, iy: int, dx: float, dy: float) -> float:
        gx, gy = self.g[iy % self.n][ix % self.n]
        return gx * dx + gy * dy

    def at(self, x: float, y: float) -> float:
        x0, y0 = math.floor(x), math.floor(y)
        dx, dy = x - x0, y - y0
        sx = dx * dx * (3 - 2 * dx)
        sy = dy * dy * (3 - 2 * dy)
        n00 = self._dot(x0, y0, dx, dy)
        n10 = self._dot(x0 + 1, y0, dx - 1, dy)
        n01 = self._dot(x0, y0 + 1, dx, dy - 1)
        n11 = self._dot(x0 + 1, y0 + 1, dx - 1, dy - 1)
        a = n00 + sx * (n10 - n00)
        b = n01 + sx * (n11 - n01)
        return a + sy * (b - a)


def _mix(a: str, b: str, t: float) -> str:
    ar, ag, ab = (int(a[i : i + 2], 16) for i in (1, 3, 5))
    br, bg, bb = (int(b[i : i + 2], 16) for i in (1, 3, 5))
    return "#%02x%02x%02x" % (
        round(ar + (br - ar) * t),
        round(ag + (bg - ag) * t),
        round(ab + (bb - ab) * t),
    )


def streamlines(
    rng: random.Random,
    noise: Noise,
    w: int,
    h: int,
    count: int,
    cells_across: float = 3.0,
) -> "Iterator[list[str]]":
    """Trace `count` particles through the noise field, one point list each.

    Yields lazily, and yields the short lines too, so callers can interleave
    their own rng draws per line and decide what to discard.
    """
    scale = cells_across / w
    for _ in range(count):
        x = rng.uniform(-60, w + 20)
        y = rng.uniform(-30, h + 30)
        pts = []
        for _ in range(70):
            a = noise.at(x * scale, y * scale) * math.tau * 0.8
            x += math.cos(a) * 7.0
            y += math.sin(a) * 7.0
            if -70 < x < w + 70 and -50 < y < h + 50:
                pts.append(f"{x:.0f},{y:.0f}")
            else:
                break
        yield pts


# Motion is an overlay, never the artwork: the motes ride the streamlines the
# field already drew, so reduced-motion drops them and the banner still reads
# exactly as it did before. Pure CSS, because SMIL can't be turned off from a
# media query, and no script, because camo serves this to an <img>.
HERO_CSS = """
.mote{animation:drift linear infinite}
@keyframes drift{to{stroke-dashoffset:-1000}}
.cell{animation:rise .55s cubic-bezier(.2,.8,.3,1) both}
.caret{animation:blink 1.15s steps(1,end) infinite}
@keyframes rise{from{opacity:0;transform:translateY(7px)}}
@keyframes blink{50%{opacity:0}}
@media (prefers-reduced-motion:reduce){
.mote{display:none}
.cell,.caret{animation:none}
}
"""


def hero(cells: list[tuple[str, str]], seed_text: str, dark: bool) -> str:
    """Flow-field banner with the headline figures beneath it.

    The field is seeded from the date, so the art is stable for a whole day and
    genuinely different the next morning. Motes drift along the streamlines the
    field already drew, so the motion follows the same current the art shows.
    """
    c = DARK if dark else LIGHT
    w, art_h, strip_h = 900, 150, 76
    h = art_h + strip_h
    rng = random.Random(seed_text)
    noise = Noise(rng)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-label="{esc(seed_text)}">',
        f"<style>{HERO_CSS}</style>",
        f'<defs><clipPath id="art"><rect width="{w}" height="{art_h}" rx="8"/>'
        "</clipPath></defs>",
        f'<rect width="{w}" height="{h}" rx="8" fill="{c["bg"]}" '
        f'stroke="{c["line"]}"/>',
        '<g clip-path="url(#art)">',
    ]

    # About three noise cells across the banner. Any higher and the streamlines
    # curl into knots instead of reading as a current.
    lines = 110
    streams: list[list[str]] = []
    for i, pts in enumerate(streamlines(rng, noise, w, art_h, lines)):
        if len(pts) < 10:
            continue
        streams.append(pts)
        t = i / lines
        stroke = _mix(c["acc"], c["dim"], 0.15 + 0.5 * t)
        parts.append(
            f'<polyline points="{" ".join(pts)}" fill="none" stroke="{stroke}" '
            f'stroke-width="{0.7 + rng.random() * 0.9:.2f}" '
            f'stroke-opacity="{0.14 + rng.random() * 0.30:.2f}" '
            'stroke-linecap="round"/>'
        )

    # Motes ride the longest streamlines, where there's enough run for the eye
    # to pick up a direction. pathLength normalises every line to 1000 units so
    # one keyframe drives them all; the duration is what keeps the speed even.
    streams.sort(key=len, reverse=True)
    for pts in streams[:34]:
        span = len(pts) * 7.0
        parts.append(
            f'<polyline class="mote" points="{" ".join(pts)}" fill="none" '
            f'stroke="{c["acc"]}" stroke-width="2.1" stroke-opacity="0.9" '
            'stroke-linecap="round" pathLength="1000" '
            # One mote per line, 4.5% of its run. Two shorter ones read as a
            # dashed line rather than as something travelling.
            'stroke-dasharray="45 955" '
            f'style="animation-duration:{span / 46:.1f}s;'
            f'animation-delay:-{rng.uniform(0, 12):.1f}s"/>'
        )

    parts.append("</g>")
    # Scrim so the figures stay legible over whatever the field drew.
    parts.append(
        f'<rect y="{art_h - 26}" width="{w}" height="{strip_h + 26}" '
        f'fill="{c["bg"]}" fill-opacity="0.86"/>'
    )
    parts.append(
        f'<line x1="0" y1="{art_h}" x2="{w}" y2="{art_h}" stroke="{c["line"]}"/>'
    )

    pad, gap = 26, 34
    widths = [max(len(v) * 13.4, len(l) * 7.7) for v, l in cells]
    total = sum(widths) + gap * (len(cells) - 1)
    x = max(pad, (w - total) / 2)
    for i, (value, label) in enumerate(cells):
        if i:
            lx = round(x - gap / 2)
            parts.append(
                f'<line x1="{lx}" y1="{art_h + 20}" x2="{lx}" y2="{h - 20}" '
                f'stroke="{c["line"]}"/>'
            )
        parts.append(
            f'<g class="cell" style="animation-delay:{0.12 + i * 0.09:.2f}s">'
            f'<text x="{x:.0f}" y="{art_h + 34}" font-family="{MONO}" '
            f'font-size="22" fill="{c["acc"]}" font-weight="600">{esc(value)}</text>'
            f'<text x="{x:.0f}" y="{art_h + 56}" font-family="{MONO}" '
            f'font-size="11" fill="{c["dim"]}" letter-spacing="1.1">'
            f"{esc(label)}</text></g>"
        )
        x += widths[i] + gap

    parts.append(
        f'<text x="{w - 24}" y="{art_h - 12}" text-anchor="end" '
        f'font-family="{MONO}" font-size="9.5" fill="{c["dim"]}" '
        f'opacity="0.75">{esc(seed_text)}</text>'
    )
    parts.append(
        f'<rect class="caret" x="{w - 20}" y="{art_h - 20}" width="6" height="9" '
        f'fill="{c["acc"]}" opacity="0.75"/>'
    )
    parts.append("</svg>")
    return "\n".join(parts)


def _wrap(text: str, per_line: int, max_lines: int) -> list[str]:
    """Greedy wrap for a monospace run, ellipsised if it overflows."""
    words, lines, cur = text.split(), [], ""
    for word in words:
        cand = f"{cur} {word}".strip()
        if len(cand) <= per_line:
            cur = cand
            continue
        if cur:
            lines.append(cur)
        cur = word
        if len(lines) == max_lines:
            break
    if cur and len(lines) < max_lines:
        lines.append(cur)
    consumed = len(" ".join(lines))
    if consumed < len(" ".join(words)) and lines:
        lines[-1] = lines[-1][: per_line - 1].rstrip(" ,.") + "…"
    return lines


def social_card(
    owner: str, name: str, tagline: str, footer: str, chips: list[str]
) -> str:
    """1280x640 OpenGraph card for one repo.

    Same field, same palette and same mono as the profile banner, seeded by the
    repo name, so a shared link reads as part of the set rather than as GitHub's
    default grey card.
    """
    c = DARK
    w, h = 1280, 640
    rng = random.Random(f"{owner}/{name}")
    noise = Noise(rng)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" '
        f'aria-label="{esc(name)}. {esc(tagline)}">',
        '<defs><linearGradient id="scrim" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0.15" stop-color="{c["bg"]}" stop-opacity="0"/>'
        f'<stop offset="0.58" stop-color="{c["bg"]}" stop-opacity="0.93"/>'
        f'<stop offset="0.75" stop-color="{c["bg"]}" stop-opacity="1"/>'
        "</linearGradient></defs>",
        f'<rect width="{w}" height="{h}" fill="{c["bg"]}"/>',
    ]

    for i, pts in enumerate(streamlines(rng, noise, w, h, 150, cells_across=2.4)):
        if len(pts) < 10:
            continue
        stroke = _mix(c["acc"], c["dim"], 0.1 + 0.55 * (i / 150))
        parts.append(
            f'<polyline points="{" ".join(pts)}" fill="none" stroke="{stroke}" '
            f'stroke-width="{0.9 + rng.random() * 1.4:.2f}" '
            f'stroke-opacity="{0.16 + rng.random() * 0.34:.2f}" '
            'stroke-linecap="round"/>'
        )

    parts.append(f'<rect width="{w}" height="{h}" fill="url(#scrim)"/>')

    pad = 74
    parts.append(
        f'<text x="{pad}" y="86" font-family="{MONO}" font-size="21" '
        f'fill="{c["dim"]}" letter-spacing="2.4">github.com/{esc(owner)}</text>'
    )

    # The name sets the scale of the whole card, so it gets the width and the
    # rest is placed under whatever size it lands on.
    size = min(78, int((w - 2 * pad - 30) / (len(name) * 0.61)))
    parts.append(
        f'<rect x="{pad}" y="{398 - size + 8}" width="7" height="{size}" '
        f'fill="{c["acc"]}"/>'
    )
    parts.append(
        f'<text x="{pad + 30}" y="398" font-family="{MONO}" font-size="{size}" '
        f'fill="{c["fg"]}" font-weight="600">{esc(name)}</text>'
    )

    per_line = int((w - 2 * pad) / (26 * 0.61))
    for n, line in enumerate(_wrap(tagline, per_line, 3)):
        parts.append(
            f'<text x="{pad}" y="{452 + n * 38}" font-family="{MONO}" '
            f'font-size="26" fill="{c["dim"]}">{esc(line)}</text>'
        )

    parts.append(
        f'<line x1="{pad}" y1="{h - 84}" x2="{w - pad}" y2="{h - 84}" '
        f'stroke="{c["line"]}" stroke-width="2"/>'
    )
    if footer:
        parts.append(
            f'<text x="{pad}" y="{h - 44}" font-family="{MONO}" font-size="23" '
            f'fill="{c["acc"]}">{esc(footer)}</text>'
        )
    # Both sit on the same baseline, so the chips go only if the footer leaves
    # room for them. The footer is the useful half.
    chip_text = " · ".join(chips)
    room = (w - 2 * pad) - len(footer) * 23 * 0.61 - 40
    if chips and len(chip_text) * 20 * 0.72 <= room:
        parts.append(
            f'<text x="{w - pad}" y="{h - 44}" text-anchor="end" '
            f'font-family="{MONO}" font-size="20" fill="{c["dim"]}" '
            f'letter-spacing="1.6">{esc(chip_text)}</text>'
        )

    parts.append("</svg>")
    return "\n".join(parts)


def breakage_chart(buckets: list[tuple[str, int]], core: str, dark: bool) -> str:
    """One series, one hue, values direct-labelled.

    A README image can't carry a tooltip, so the cap labels are the only way to
    read a value. That's why every column is labelled here and the y-axis and
    gridlines are dropped instead: the numbers are already on the marks.
    """
    c = DARK if dark else LIGHT
    w = 620
    pad_l, pad_r, top, base_y = 22, 22, 58, 168
    h = 200
    n = len(buckets)
    if not n:
        return ""
    peak = max(v for _, v in buckets) or 1
    plot_h = base_y - top

    band = (w - pad_l - pad_r) / n
    bar_w = min(24.0, band - 18)

    total = sum(v for _, v in buckets)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-label="When HACS integrations '
        f'first break: '
        + "; ".join(f"{k} {v}" for k, v in buckets)
        + '">',
        f'<rect width="{w}" height="{h}" rx="8" fill="{c["bg"]}" '
        f'stroke="{c["line"]}"/>',
        f'<text x="{pad_l}" y="26" font-family="{MONO}" font-size="13" '
        f'fill="{c["fg"]}" font-weight="600">When your HACS integrations first '
        f"break</text>",
        f'<text x="{pad_l}" y="43" font-family="{MONO}" font-size="10.5" '
        f'fill="{c["dim"]}">{total:,} affected, measured against Home Assistant '
        f"{esc(core)}</text>",
    ]

    for i, (label, value) in enumerate(buckets):
        bh = max(2.0, value / peak * plot_h)
        cx = pad_l + band * i + band / 2
        x = cx - bar_w / 2
        y = base_y - bh
        r = min(4.0, bh)
        # Rounded cap, square where it meets the baseline.
        parts.append(
            f'<path d="M{x:.1f},{base_y} V{y + r:.1f} '
            f"a{r:.1f},{r:.1f} 0 0 1 {r:.1f},-{r:.1f} "
            f"h{bar_w - 2 * r:.1f} "
            f"a{r:.1f},{r:.1f} 0 0 1 {r:.1f},{r:.1f} "
            f'V{base_y} Z" fill="{c["acc"]}"/>'
        )
        parts.append(
            f'<text x="{cx:.0f}" y="{y - 8:.0f}" text-anchor="middle" '
            f'font-family="{MONO}" font-size="12.5" fill="{c["fg"]}" '
            f'font-weight="600">{value:,}</text>'
        )
        parts.append(
            f'<text x="{cx:.0f}" y="{base_y + 18}" text-anchor="middle" '
            f'font-family="{MONO}" font-size="10.5" fill="{c["dim"]}">'
            f"{esc(label)}</text>"
        )

    parts.append(
        f'<line x1="{pad_l}" y1="{base_y}" x2="{w - pad_r}" y2="{base_y}" '
        f'stroke="{c["line"]}"/>'
    )
    parts.append("</svg>")
    return "\n".join(parts)

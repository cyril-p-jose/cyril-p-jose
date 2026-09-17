#!/usr/bin/env python3
"""
Generate a HIGH-CLARITY, TRUE-COLOR, ANIMATED ASCII portrait SVG
from assets/source-photo.jpg for Cyril P Jose.

Key improvements:
  - Correct luminance polarity (bright skin gets solid/textured characters, no holes)
  - True RGB color extraction per character from original photo
  - Exact aspect-ratio scaling to preserve facial proportions perfectly
  - Clean background isolation (transparent space outside portrait)
  - Lightweight SVG (<70 KB) via run-length color grouping
  - Smooth SMIL terminal typing wipe animation and blinking cursor
"""
import html
import os
import sys
from PIL import Image, ImageEnhance, ImageFilter
from rembg import remove

HERE = os.path.dirname(os.path.abspath(__file__))
SRC_PHOTO = os.path.join(HERE, "..", "assets", "source-photo.jpg")
OUT_SVG = os.path.join(HERE, "..", "assets", "portrait-ascii.svg")

# Grid dimensions tuned for 370x440 canvas
COLS = 78
ROWS = 50

PAD = 15
TITLEBAR_H = 30
STATUS_H = 30
CANVAS_W = 370
CANVAS_H = 440

BG = "#0d1117"
BG2 = "#111722"
FRAME = "#30363d"
TITLE_TEXT = "#7d8590"
CURSOR = "#22d3ee"

ROW_DUR = 0.08
STAGGER = 0.075

# Density ramp: fine dot (sparse/dark) -> dense block (bright highlight)
RAMP = ".:-=+*#%@"


def quantize_color(r, g, b, step=8):
    qr = min(255, (r // step) * step + step // 2)
    qg = min(255, (g // step) * step + step // 2)
    qb = min(255, (b // step) * step + step // 2)
    return f"#{qr:02x}{qg:02x}{qb:02x}"


def generate_svg():
    if not os.path.exists(SRC_PHOTO):
        print(f"Error: '{SRC_PHOTO}' not found.", file=sys.stderr)
        sys.exit(1)

    print("Isolating subject background with rembg...")
    orig = Image.open(SRC_PHOTO).convert("RGBA")
    cut = remove(orig)

    # Center-crop head, neck, and upper chest proportionally
    w, h = cut.size
    crop_box = (int(w * 0.06), int(h * 0.01), int(w * 0.94), int(h * 0.92))
    cropped = cut.crop(crop_box)

    # Color enhance
    rgb_full = cropped.convert("RGB")
    alpha_full = cropped.split()[-1]

    enh_color = ImageEnhance.Color(rgb_full).enhance(1.20)
    enh_contrast = ImageEnhance.Contrast(enh_color).enhance(1.15)
    enh_bright = ImageEnhance.Brightness(enh_contrast).enhance(1.02)

    # Resize to character grid
    small_rgb = enh_bright.resize((COLS, ROWS), Image.LANCZOS)
    small_alpha = alpha_full.resize((COLS, ROWS), Image.LANCZOS)
    small_gray = small_rgb.convert("L").filter(ImageFilter.UnsharpMask(radius=1.5, percent=130, threshold=2))

    px_rgb = small_rgb.load()
    px_alpha = small_alpha.load()
    px_gray = small_gray.load()

    rows_spans = []

    for y in range(ROWS):
        spans = []
        current_color = None
        current_text = []

        for x in range(COLS):
            r, g, b = px_rgb[x, y]
            a = px_alpha[x, y]
            lum = px_gray[x, y] / 255.0

            # Transparent background
            if a < 35:
                char = " "
                color = None
            else:
                # Map luminance to density ramp
                idx = int(lum * (len(RAMP) - 1) + 0.5)
                idx = max(0, min(len(RAMP) - 1, idx))
                char = RAMP[idx]
                color = quantize_color(r, g, b)

            if color == current_color:
                current_text.append(char)
            else:
                if current_text:
                    spans.append((current_color, "".join(current_text)))
                current_color = color
                current_text = [char]

        if current_text:
            spans.append((current_color, "".join(current_text)))
        rows_spans.append(spans)

    art_top = TITLEBAR_H + 10
    art_w = CANVAS_W - PAD * 2
    cell_h = (CANVAS_H - TITLEBAR_H - STATUS_H - 16) / ROWS
    font_size = cell_h * 1.05

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS_W}" height="{CANVAS_H}" '
        f'viewBox="0 0 {CANVAS_W} {CANVAS_H}" font-family="ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace">',
        '<defs>',
        f'<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">',
        f'<stop offset="0" stop-color="{BG2}"/>',
        f'<stop offset="1" stop-color="{BG}"/>',
        '</linearGradient>',
        '</defs>',
        f'<rect width="{CANVAS_W}" height="{CANVAS_H}" rx="12" fill="url(#bg)"/>',
        f'<rect x="0.5" y="0.5" width="{CANVAS_W-1}" height="{CANVAS_H-1}" rx="12" fill="none" stroke="{FRAME}" stroke-width="1"/>',
        f'<line x1="0" y1="{TITLEBAR_H}" x2="{CANVAS_W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>',
    ]

    # Terminal buttons
    for i, dotcol in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        parts.append(f'<circle cx="{PAD + i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{dotcol}"/>')

    parts.append(
        f'<text x="{CANVAS_W/2}" y="{TITLEBAR_H/2 + 4}" fill="{TITLE_TEXT}" font-size="11.5" '
        f'text-anchor="middle">cyril-p-jose@github: ~$ ./portrait.sh</text>'
    )

    for ry, spans in enumerate(rows_spans):
        y = art_top + ry * cell_h + cell_h * 0.78
        row_y = art_top + ry * cell_h
        delay = ry * STAGGER

        inner_tspans = []
        for color, text in spans:
            safe = html.escape(text)
            if color is None or text.strip() == "":
                inner_tspans.append(safe)
            else:
                inner_tspans.append(f'<tspan fill="{color}">{safe}</tspan>')

        full_inner = "".join(inner_tspans)
        text_tag = (
            f'<text xml:space="preserve" x="{PAD}" y="{y:.1f}" '
            f'font-size="{font_size:.1f}" textLength="{art_w}" lengthAdjust="spacing">{full_inner}</text>'
        )

        parts.append(
            f'<clipPath id="r{ry}"><rect x="{PAD}" y="{row_y:.1f}" height="{cell_h:.1f}" width="0">'
            f'<animate attributeName="width" from="0" to="{art_w}" begin="{delay:.3f}s" '
            f'dur="{ROW_DUR:.2f}s" fill="freeze"/></rect></clipPath>'
        )
        parts.append(f'<g clip-path="url(#r{ry})">{text_tag}</g>')
        parts.append(
            f'<rect y="{row_y+1:.1f}" width="6" height="{cell_h-1:.1f}" fill="{CURSOR}" opacity="0">'
            f'<animate attributeName="x" from="{PAD}" to="{PAD+art_w}" begin="{delay:.3f}s" '
            f'dur="{ROW_DUR:.2f}s" fill="freeze"/>'
            f'<set attributeName="opacity" to="0.85" begin="{delay:.3f}s"/>'
            f'<set attributeName="opacity" to="0" begin="{delay+ROW_DUR:.3f}s"/>'
            f'</rect>'
        )

    # Status Bar
    status_line_y = CANVAS_H - STATUS_H
    status_y = status_line_y + 19
    parts.append(f'<line x1="0" y1="{status_line_y:.1f}" x2="{CANVAS_W}" y2="{status_line_y:.1f}" stroke="{FRAME}"/>')
    parts.append(
        f'<text x="{PAD}" y="{status_y:.1f}" fill="{TITLE_TEXT}" font-size="12">'
        f'cyril-p-jose@github:~$ <tspan fill="#3fb950">whoami</tspan> <tspan fill="#c9d1d9">Cyril P Jose</tspan></text>'
    )
    parts.append(
        f'<rect x="{PAD+240}" y="{status_y-12:.1f}" width="7.5" height="14" fill="{CURSOR}">'
        f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.51;1" dur="1s" repeatCount="indefinite"/>'
        f'</rect>'
    )

    parts.append("</svg>")
    svg = "".join(parts)

    os.makedirs(os.path.dirname(OUT_SVG), exist_ok=True)
    with open(OUT_SVG, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Generated crystal-clear multi-color ASCII portrait at {OUT_SVG} ({len(svg)} bytes)")


if __name__ == "__main__":
    generate_svg()

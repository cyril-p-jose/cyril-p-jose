#!/usr/bin/env python3
"""
Generate a high-vibrance, MULTI-COLOR animated ASCII art SVG terminal window
from the user's source photo (assets/source-photo.jpg).

Features:
  - Preserves authentic natural skin tones, hair colors, suit, tie, and features
  - Boosts saturation and contrast so colors pop vibrantly on dark terminal background
  - Groups adjacent same/similar colors into <tspan fill="..."> runs for tiny SVG file size
  - Retains the smooth SMIL typing-wipe animation and blinking terminal cursor
"""
import html
import os
import sys
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from rembg import remove

HERE = os.path.dirname(os.path.abspath(__file__))
SRC_PHOTO = os.path.join(HERE, "..", "assets", "source-photo.jpg")
OUT_SVG = os.path.join(HERE, "..", "assets", "portrait-ascii.svg")

COLS = 85
ROWS = 48
CELL_W = 4.0
CELL_H = 7.5
RAMP = " .`:-=+*cs%@"  # Bright (sparse) -> Dark (dense)

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
STAGGER = 0.08


def prep_color_image():
    if not os.path.exists(SRC_PHOTO):
        print(f"Error: '{SRC_PHOTO}' not found.", file=sys.stderr)
        sys.exit(1)

    print("Processing color cutout with rembg...")
    img = Image.open(SRC_PHOTO).convert("RGBA")
    cut = remove(img)

    # Crop head & shoulders if oversized
    w, h = cut.size
    if h > 800 and w > 500:
        cut = cut.crop((int(w * 0.05), int(h * 0.02), int(w * 0.95), int(h * 0.75)))

    # Composite onto white background for luminance extraction
    rgb = cut.convert("RGB")
    alpha = cut.split()[-1]

    # Enhance saturation & contrast for rich vibrant terminal colors
    enh_color = ImageEnhance.Color(rgb).enhance(1.35)
    enh_contrast = ImageEnhance.Contrast(enh_color).enhance(1.25)
    enh_bright = ImageEnhance.Brightness(enh_contrast).enhance(1.05)

    # Make background pure white
    white_bg = Image.new("RGB", cut.size, (255, 255, 255))
    final_rgb = Image.composite(enh_bright, white_bg, alpha)

    return final_rgb, cut.split()[-1]


def quantize_color(r, g, b, step=12):
    # Quantize color slightly to group adjacent characters and reduce SVG size
    qr = min(255, (r // step) * step + step // 2)
    qg = min(255, (g // step) * step + step // 2)
    qb = min(255, (b // step) * step + step // 2)
    return f"#{qr:02x}{qg:02x}{qb:02x}"


def generate_multicolor_svg():
    color_img, alpha_mask = prep_color_image()

    # Resize to COLS x ROWS
    small_color = color_img.resize((COLS, ROWS), Image.LANCZOS)
    small_alpha = alpha_mask.resize((COLS, ROWS), Image.LANCZOS)
    small_gray = small_color.convert("L")

    # Apply unsharp mask to crisp edges
    small_gray = small_gray.filter(ImageFilter.UnsharpMask(radius=2, percent=140, threshold=2))

    px_color = small_color.load()
    px_alpha = small_alpha.load()
    px_gray = small_gray.load()

    rows_spans = []

    for y in range(ROWS):
        spans = []  # List of (color, text)
        current_color = None
        current_text = []

        for x in range(COLS):
            r, g, b = px_color[x, y]
            a = px_alpha[x, y]
            lum = px_gray[x, y] / 255.0

            # Background clearing (transparent/white)
            if a < 30 or lum >= 0.88:
                char = " "
                color = None
            else:
                idx = int((1.0 - lum) * (len(RAMP) - 1) + 0.5)
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

    art_top = TITLEBAR_H + 12
    art_w = CANVAS_W - PAD * 2
    font_size = CELL_H * 0.95

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS_W}" height="{CANVAS_H}" '
        f'viewBox="0 0 {CANVAS_W} {CANVAS_H}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
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
        f'text-anchor="middle">cyril-p-jose@github: ~$ ./portrait.sh --color</text>'
    )

    for ry, spans in enumerate(rows_spans):
        y = art_top + ry * CELL_H + CELL_H * 0.74
        row_y = art_top + ry * CELL_H
        delay = ry * STAGGER

        # Build inner text with tspans
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
            f'<clipPath id="r{ry}"><rect x="{PAD}" y="{row_y:.1f}" height="{CELL_H:.1f}" width="0">'
            f'<animate attributeName="width" from="0" to="{art_w}" begin="{delay:.3f}s" '
            f'dur="{ROW_DUR:.2f}s" fill="freeze"/></rect></clipPath>'
        )
        parts.append(f'<g clip-path="url(#r{ry})">{text_tag}</g>')
        parts.append(
            f'<rect y="{row_y+1:.1f}" width="{CELL_W*1.5}" height="{CELL_H-1:.1f}" fill="{CURSOR}" opacity="0">'
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
    print(f"Generated multi-color ASCII SVG at {OUT_SVG} ({len(svg)} bytes)")


if __name__ == "__main__":
    generate_multicolor_svg()

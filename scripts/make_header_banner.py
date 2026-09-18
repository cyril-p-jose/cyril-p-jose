#!/usr/bin/env python3
"""
Generate an animated Cyberpunk Matrix Code Rain Header Banner SVG
for Cyril P Jose (860x180 px).
Outputs to assets/header-banner.svg.
"""
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_SVG = os.path.join(HERE, "..", "assets", "header-banner.svg")

W = 860
H = 180

BG = "#06090f"
BG2 = "#0d1420"
FRAME = "#1f6feb"
CYAN = "#22d3ee"
GREEN = "#39d353"
NEON_GREEN = "#69f0ae"
MUTED = "#7d8590"
TEXT = "#e6edf3"


def generate_header_banner():
    # Matrix digital rain columns
    random.seed(42)
    matrix_chars = [
        "0", "1", "0", "1", "1", "0", "{", "}", ";", "<", ">", "/", "λ", "π",
        "J", "a", "v", "a", "P", "y", "t", "h", "o", "n", "C", "S", "E", "A", "I"
    ]

    streams = []
    col_width = 24
    num_cols = W // col_width

    for col in range(num_cols):
        x = col * col_width + 6
        dur = random.uniform(2.5, 4.5)
        delay = random.uniform(0.0, 3.0)
        # Sequence of 6-8 chars
        stream_chars = [random.choice(matrix_chars) for _ in range(random.randint(5, 8))]
        streams.append((x, dur, delay, stream_chars))

    css = """
@keyframes rain {
  0% { transform: translateY(-120px); opacity: 0; }
  15% { opacity: 0.85; }
  85% { opacity: 0.85; }
  100% { transform: translateY(220px); opacity: 0; }
}
@keyframes laserScan {
  0% { transform: translateY(0px); opacity: 0.3; }
  50% { transform: translateY(178px); opacity: 0.9; }
  100% { transform: translateY(0px); opacity: 0.3; }
}
@keyframes glowPulse {
  0% { filter: drop-shadow(0 0 6px rgba(34, 211, 238, 0.4)); }
  50% { filter: drop-shadow(0 0 16px rgba(34, 211, 238, 0.85)); }
  100% { filter: drop-shadow(0 0 6px rgba(34, 211, 238, 0.4)); }
}
.stream { animation: rain linear infinite; }
.laser { animation: laserScan 4s ease-in-out infinite; }
.glow-title { animation: glowPulse 3s ease-in-out infinite; }
""".strip()

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'font-family="ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace">',
        f'<style>{css}</style>',
        '<defs>',
        f'<linearGradient id="bbg" x1="0" y1="0" x2="0" y2="1">',
        f'<stop offset="0" stop-color="{BG2}"/>',
        f'<stop offset="100%" stop-color="{BG}"/>',
        '</linearGradient>',
        f'<linearGradient id="laserGrad" x1="0" y1="0" x2="1" y2="0">',
        f'<stop offset="0" stop-color="{CYAN}" stop-opacity="0"/>',
        f'<stop offset="30%" stop-color="{GREEN}" stop-opacity="0.8"/>',
        f'<stop offset="50%" stop-color="{NEON_GREEN}" stop-opacity="1"/>',
        f'<stop offset="70%" stop-color="{CYAN}" stop-opacity="0.8"/>',
        f'<stop offset="100%" stop-color="{CYAN}" stop-opacity="0"/>',
        '</linearGradient>',
        '</defs>',
        # Background & Frame
        f'<rect width="{W}" height="{H}" rx="12" fill="url(#bbg)"/>',
        f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="12" fill="none" stroke="{FRAME}" stroke-width="1" stroke-opacity="0.65"/>',
    ]

    # Matrix Streams (background layer)
    parts.append('<g opacity="0.32">')
    for x, dur, delay, chars in streams:
        t_spans = []
        for ci, ch in enumerate(chars):
            opacity = 0.3 + (ci / len(chars)) * 0.7
            color = NEON_GREEN if ci == len(chars) - 1 else GREEN
            t_spans.append(f'<tspan x="{x}" dy="14" fill="{color}" opacity="{opacity:.2f}">{ch}</tspan>')
        inner = "".join(t_spans)
        parts.append(
            f'<text class="stream" font-size="11" font-weight="700" style="animation-duration:{dur:.2f}s; animation-delay:{delay:.2f}s;">{inner}</text>'
        )
    parts.append('</g>')

    # Laser scanner line
    parts.append(
        f'<line class="laser" x1="2" y1="0" x2="{W-2}" y2="0" stroke="url(#laserGrad)" stroke-width="1.5"/>'
    )

    # Center Cyberpunk Branding Box
    box_w, box_h = 560, 110
    box_x = (W - box_w) / 2
    box_y = (H - box_h) / 2

    parts.append(
        f'<rect x="{box_x}" y="{box_y}" width="{box_w}" height="{box_h}" rx="10" '
        f'fill="{BG}" fill-opacity="0.88" stroke="{CYAN}" stroke-width="1.2" stroke-opacity="0.75"/>'
    )

    # Corner brackets for sci-fi look
    bracket_len = 12
    # Top-Left
    parts.append(f'<path d="M{box_x} {box_y+bracket_len} L{box_x} {box_y} L{box_x+bracket_len} {box_y}" stroke="{NEON_GREEN}" stroke-width="2.5" fill="none"/>')
    # Top-Right
    parts.append(f'<path d="M{box_x+box_w-bracket_len} {box_y} L{box_x+box_w} {box_y} L{box_x+box_w} {box_y+bracket_len}" stroke="{NEON_GREEN}" stroke-width="2.5" fill="none"/>')
    # Bottom-Left
    parts.append(f'<path d="M{box_x} {box_y+box_h-bracket_len} L{box_x} {box_y+box_h} L{box_x+bracket_len} {box_y+box_h}" stroke="{NEON_GREEN}" stroke-width="2.5" fill="none"/>')
    # Bottom-Right
    parts.append(f'<path d="M{box_x+box_w-bracket_len} {box_y+box_h} L{box_x+box_w} {box_y+box_h} L{box_x+box_w} {box_y+box_h-bracket_len}" stroke="{NEON_GREEN}" stroke-width="2.5" fill="none"/>')

    # Status tag
    parts.append(
        f'<text x="{box_x + 18}" y="{box_y + 24}" fill="{GREEN}" font-size="10.5" font-weight="700">'
        f'SYSTEM STATUS: <tspan fill="{NEON_GREEN}">ONLINE [200 OK]</tspan>  &#183;  NODE: <tspan fill="{CYAN}">SJCET_PALAI</tspan></text>'
    )

    # Main glowing title
    parts.append(
        f'<text class="glow-title" x="{W/2}" y="{box_y + 60}" fill="{TEXT}" font-size="28" font-weight="900" '
        f'letter-spacing="4" text-anchor="middle">CYRIL P JOSE</text>'
    )

    # Tagline
    parts.append(
        f'<text x="{W/2}" y="{box_y + 88}" fill="{CYAN}" font-size="12" font-weight="600" '
        f'letter-spacing="1" text-anchor="middle">⚡ B.Tech CSE · Aspiring Teacher &amp; Software Developer</text>'
    )

    parts.append("</svg>")
    svg = "".join(parts)

    os.makedirs(os.path.dirname(OUT_SVG), exist_ok=True)
    with open(OUT_SVG, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Generated header banner at {OUT_SVG} ({len(svg)} bytes)")


if __name__ == "__main__":
    generate_header_banner()

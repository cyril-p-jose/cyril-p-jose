#!/usr/bin/env python3
"""
Build a neofetch-style info card SVG tailored for Cyril P Jose (cyril-p-jose)
featuring exact verified background, education, tech stack, and highlights.
Outputs to assets/info-card.svg.
"""
import html
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "assets", "info-card.svg")

W, H = 490, 440
PAD = 20
TITLEBAR_H = 30
KEY_X = PAD
VAL_X = PAD + 98
LINE_H = 20.5

BG = "#0d1117"
BG2 = "#111722"
FRAME = "#30363d"
MUTED = "#7d8590"
INK = "#c9d1d9"
KEY = "#ffa657"        # warm amber/orange keys
SECTION = "#58a6ff"    # blue section headers
GREEN = "#3fb950"      # terminal green highlights
ACCENT = "#22d3ee"     # cyan accent

HOST = "cyril-p-jose"

ROWS = [
    ("host",),
    ("kv", "Role", "B.Tech CSE Student | Aspiring Developer & Teacher"),
    ("kv", "Edu", "B.Tech Computer Science @ SJCET Palai"),
    ("kv", "Loc", "Kerala, India"),
    ("kv", "Site", "cyril-p-jose-portfolio.vercel.app"),
    ("gap",),
    ("sec", "Technical Stack"),
    ("kv", "Languages", "Java, Python, C, JavaScript"),
    ("kv", "Frontend", "HTML5, CSS3, React"),
    ("kv", "Backend", "Node.js, Express, Flask"),
    ("kv", "Database", "MySQL, MongoDB, SQLite"),
    ("kv", "Java Core", "Core Java, Swing, JDBC"),
    ("kv", "AI / ML", "Generative AI, Gemini, Computer Vision"),
    ("kv", "Tools", "Git, GitHub, Eclipse, VS Code"),
    ("gap",),
    ("sec", "Highlights & Focus"),
    ("bul", "Passionate about Computer Science education & teaching"),
    ("bul", "Developing AI-powered tools & full-stack web applications"),
    ("bul", "Active GitHub contributor with 800+ yearly contributions"),
]


def esc(s):
    return html.escape(s)


def rise(inner, i):
    delay = 0.12 + i * 0.045
    return (
        f'<g opacity="0" transform="translate(0,5)">{inner}'
        f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.3f}s" dur="0.4s" fill="freeze"/>'
        f'<animateTransform attributeName="transform" type="translate" from="0 5" to="0 0" '
        f'begin="{delay:.3f}s" dur="0.4s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1"/>'
        f'</g>'
    )


def generate_svg():
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
        '<defs>',
        f'<linearGradient id="ibg" x1="0" y1="0" x2="0" y2="1">',
        f'<stop offset="0" stop-color="{BG2}"/>',
        f'<stop offset="1" stop-color="{BG}"/>',
        '</linearGradient>',
        '</defs>',
        f'<rect width="{W}" height="{H}" rx="12" fill="url(#ibg)"/>',
        f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="12" fill="none" stroke="{FRAME}"/>',
        f'<line x1="0" y1="{TITLEBAR_H}" x2="{W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>',
    ]

    # Terminal buttons
    for i, dotcol in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        parts.append(f'<circle cx="{PAD + i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{dotcol}"/>')

    parts.append(
        f'<text x="{W/2}" y="{TITLEBAR_H/2 + 4}" fill="{MUTED}" font-size="12" '
        f'text-anchor="middle">{esc(HOST)}@github: ~$ neofetch</text>'
    )

    y = TITLEBAR_H + 26
    for i, row in enumerate(ROWS):
        kind = row[0]
        if kind == "gap":
            y += LINE_H * 0.45
            continue
        if kind == "host":
            host = esc(HOST)
            rule_x = KEY_X + (len(HOST) + 7) * 8 + 8
            inner = (
                f'<text x="{KEY_X}" y="{y:.1f}" font-size="13.5" font-weight="700">'
                f'<tspan fill="{GREEN}">{host}</tspan><tspan fill="{MUTED}">@</tspan>'
                f'<tspan fill="{ACCENT}">github</tspan></text>'
                f'<line x1="{rule_x}" y1="{y-4:.1f}" x2="{W-PAD}" y2="{y-4:.1f}" '
                f'stroke="{FRAME}" stroke-opacity="0.8"/>'
            )
        elif kind == "sec":
            title = esc(row[1])
            rule_start = KEY_X + 16 + len(row[1]) * 8
            inner = (
                f'<text x="{KEY_X}" y="{y:.1f}" fill="{SECTION}" font-size="12" font-weight="700">'
                f'&#8212; {title} &#8212;</text>'
                f'<line x1="{rule_start + 10}" y1="{y-4:.1f}" x2="{W-PAD}" y2="{y-4:.1f}" '
                f'stroke="{FRAME}" stroke-opacity="0.6"/>'
            )
        elif kind == "kv":
            key, val = esc(row[1]), esc(row[2])
            inner = (
                f'<text x="{KEY_X}" y="{y:.1f}" fill="{KEY}" font-size="12" font-weight="700">{key}</text>'
                f'<text x="{VAL_X}" y="{y:.1f}" fill="{INK}" font-size="12">{val}</text>'
            )
        elif kind == "bul":
            txt = esc(row[1])
            inner = (
                f'<circle cx="{KEY_X+3}" cy="{y-4:.1f}" r="2.5" fill="{GREEN}"/>'
                f'<text x="{KEY_X+14}" y="{y:.1f}" fill="{INK}" font-size="11.5">{txt}</text>'
            )
        else:
            continue

        parts.append(rise(inner, i))
        y += LINE_H

    parts.append("</svg>")
    return "".join(parts)


if __name__ == "__main__":
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    svg = generate_svg()
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Generated {OUT} ({len(svg)} bytes)")

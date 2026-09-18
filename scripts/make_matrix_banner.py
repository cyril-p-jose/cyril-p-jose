import random

def generate_matrix_svg(filename="assets/matrix-banner.svg", width=860, height=200):
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*()_+{}|<>?~"
    
    svg = [
        f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">',
        '  <defs>',
        '    <style>',
        '      .matrix-text {',
        '        font-family: monospace;',
        '        font-size: 14px;',
        '        fill: #0F0;',
        '        opacity: 0.8;',
        '      }',
        '      .bg { fill: #000; }',
        '    </style>',
        '  </defs>',
        f'  <rect width="{width}" height="{height}" class="bg"/>'
    ]

    cols = width // 15
    for i in range(cols):
        x = i * 15
        
        # Determine starting y and speed
        start_y = random.randint(-100, 100)
        speed = random.uniform(3, 8)
        
        # Build a column of characters
        length = random.randint(5, 20)
        col_text = "".join(random.choice(chars) for _ in range(length))
        
        # Group with animation
        svg.append(f'  <g transform="translate({x}, {start_y})">')
        svg.append(f'    <animateTransform attributeName="transform" type="translate" from="{x} -200" to="{x} {height + 200}" dur="{speed}s" repeatCount="indefinite"/>')
        
        for j, char in enumerate(col_text):
            opacity = 1.0 if j == length -1 else 0.4 + (0.5 * (j / length))
            color = "#fff" if j == length - 1 else "#0F0"
            y = j * 14
            svg.append(f'    <text x="0" y="{y}" class="matrix-text" fill="{color}" opacity="{opacity}">{char}</text>')
            
        svg.append('  </g>')

    # Add overlay text
    svg.append('  <rect width="100%" height="100%" fill="rgba(0,0,0,0.5)" />')
    svg.append('  <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" font-family="monospace" font-size="32" fill="#0f0" font-weight="bold">CYRIL P JOSE</text>')
    svg.append('  <text x="50%" y="65%" dominant-baseline="middle" text-anchor="middle" font-family="monospace" font-size="16" fill="#fff">SOFTWARE DEVELOPER</text>')
    
    svg.append('</svg>')

    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"Generated {filename}")

if __name__ == "__main__":
    generate_matrix_svg()

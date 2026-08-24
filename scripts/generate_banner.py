import os
import sys

def generate_banner_svg(output_svg_path, name="Cyril P Jose", tag="Aspiring Teacher &amp; Software Developer"):
    svg_w = 800
    svg_h = 240

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="100%" height="auto">
  <style>
    .terminal-bg {{
      fill: #0d1117;
      stroke: #30363d;
      stroke-width: 2;
      rx: 8px;
    }}
    .header-bar {{
      fill: #161b22;
      stroke: #30363d;
      stroke-width: 1;
    }}
    .circle-red {{ fill: #ff5f56; }}
    .circle-yellow {{ fill: #ffbd2e; }}
    .circle-green {{ fill: #27c93f; }}
    .terminal-text {{
      font-family: 'Fira Code', 'Courier New', Courier, monospace;
      font-size: 13px;
      fill: #c9d1d9;
    }}
    
    .scanlines {{
      fill: url(#scanline-pattern);
      opacity: 0.05;
    }}
    
    /* Neon glow effect and text */
    .glow-title {{
      font-family: 'Fira Code', 'Courier New', Courier, monospace;
      font-size: 32px;
      font-weight: bold;
      fill: #ffffff;
      letter-spacing: 2px;
    }}
    .glow-sub {{
      font-family: 'Fira Code', 'Courier New', Courier, monospace;
      font-size: 16px;
      fill: #58a6ff;
    }}
    
    @keyframes blink {{
      50% {{ opacity: 0; }}
    }}
    .cursor {{
      animation: blink 0.8s infinite;
      fill: #58a6ff;
    }}
  </style>

  <defs>
    <!-- Grid/Scanline pattern definition -->
    <pattern id="scanline-pattern" width="100" height="4" patternUnits="userSpaceOnUse">
      <line x1="0" y1="0" x2="100" y2="0" stroke="#ffffff" stroke-width="1.5" />
    </pattern>
  </defs>

  <!-- Window Frame -->
  <rect class="terminal-bg" x="10" y="10" width="{svg_w - 20}" height="{svg_h - 20}" />
  
  <!-- Scanline Overlay -->
  <rect class="scanlines" x="10" y="45" width="{svg_w - 20}" height="{svg_h - 55}" rx="8" />

  <!-- Title bar -->
  <path class="header-bar" d="M 10,18 A 8,8 0 0 1 18,10 L {svg_w - 18},10 A 8,8 0 0 1 {svg_w - 18},18 L {svg_w - 10},45 L 10,45 Z" />
  
  <!-- Window buttons -->
  <circle class="circle-red" cx="30" cy="28" r="6" />
  <circle class="circle-yellow" cx="50" cy="28" r="6" />
  <circle class="circle-green" cx="70" cy="28" r="6" />
  
  <!-- Window Title -->
  <text class="terminal-text" x="{svg_w // 2}" y="32" text-anchor="middle" fill="#8b949e">bash --profile --interactive</text>

  <!-- Banner details -->
  <g transform="translate(60, 110)">
    <!-- Elegant terminal ascii border representation -->
    <text class="glow-title" x="0" y="0">CYRIL P JOSE</text>
    <text class="glow-sub" x="2" y="32">&gt; {tag}</text>
    <rect class="cursor" x="350" y="17" width="10" height="18" />
  </g>

  <!-- Border bottom subtle status -->
  <text class="terminal-text" x="60" y="205" fill="#8b949e" font-size="11">System: v1.0.0 | Status: Active</text>
</svg>
'''

    os.makedirs(os.path.dirname(output_svg_path), exist_ok=True)
    with open(output_svg_path, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    print(f"[OK] Banner SVG generated: {output_svg_path}")

if __name__ == "__main__":
    svg_out = "assets/banner.svg"
    try:
        generate_banner_svg(svg_out)
    except Exception as e:
        print(f"Error in generate_banner: {e}")
        sys.exit(1)

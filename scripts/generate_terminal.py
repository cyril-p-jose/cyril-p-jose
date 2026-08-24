import os
import sys
import json

def generate_terminal_svg(profile_path, output_svg_path):
    if not os.path.exists(profile_path):
        raise FileNotFoundError(f"Profile config not found at {profile_path}")
        
    with open(profile_path, 'r', encoding='utf-8') as f:
        profile = json.load(f)

    # Extract needed variables
    name = profile.get("name", "Cyril P Jose")
    username = profile.get("username", "cyril-p-jose")
    education = profile.get("education", "Student")
    college = profile.get("college", "University")
    goal = profile.get("goal", "Developer")
    skills = profile.get("skills", {})
    interests = profile.get("interests", [])

    # Format skills lists
    languages_str = " ".join(skills.get("languages", []))
    frontend_str = " ".join(skills.get("frontend", []))
    backend_str = " ".join(skills.get("backend", []))
    database_str = " ".join(skills.get("database", []))
    ai_str = " / ".join(skills.get("ai_ml", []))

    svg_w = 600
    svg_h = 360

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
    .key-text {{
      fill: #58a6ff;
      font-weight: bold;
    }}
    .val-text {{
      fill: #ffffff;
    }}
    .title-text {{
      fill: #8b949e;
    }}
    .border-line {{
      stroke: #30363d;
      stroke-width: 1;
    }}
    
    @keyframes blink {{
      50% {{ opacity: 0; }}
    }}
    .cursor {{
      animation: blink 0.8s infinite;
      fill: #58a6ff;
    }}
    
    @keyframes typing {{
      from {{ width: 0; }}
      to {{ width: 100%; }}
    }}
    .typewriter {{
      overflow: hidden;
      white-space: nowrap;
    }}
  </style>

  <!-- Window Frame -->
  <rect class="terminal-bg" x="10" y="10" width="{svg_w - 20}" height="{svg_h - 20}" />
  
  <!-- Title bar -->
  <path class="header-bar" d="M 10,18 A 8,8 0 0 1 18,10 L {svg_w - 18},10 A 8,8 0 0 1 {svg_w - 18},18 L {svg_w - 10},45 L 10,45 Z" />
  
  <!-- Window buttons -->
  <circle class="circle-red" cx="30" cy="28" r="6" />
  <circle class="circle-yellow" cx="50" cy="28" r="6" />
  <circle class="circle-green" cx="70" cy="28" r="6" />
  
  <!-- Window Title -->
  <text class="terminal-text title-text" x="{svg_w // 2}" y="32" text-anchor="middle">neofetch --user {username}</text>

  <!-- Terminal Info Panel Content -->
  <g transform="translate(30, 75)">
    <!-- Header -->
    <text class="terminal-text val-text" x="0" y="0" font-weight="bold" font-size="14">{username}@github</text>
    <line class="border-line" x1="0" y1="10" x2="520" y2="10" />

    <!-- Details -->
    <g transform="translate(0, 35)">
      <text class="terminal-text" x="0" y="0">
        <tspan class="key-text">OS        : </tspan>
        <tspan class="val-text">{education}</tspan>
      </text>

      <text class="terminal-text" x="0" y="22">
        <tspan class="key-text">COLLEGE   : </tspan>
        <tspan class="val-text">{college}</tspan>
      </text>

      <text class="terminal-text" x="0" y="44">
        <tspan class="key-text">ROLE      : </tspan>
        <tspan class="val-text">{goal}</tspan>
      </text>

      <text class="terminal-text" x="0" y="66">
        <tspan class="key-text">FOCUS     : </tspan>
        <tspan class="val-text">AI / Full Stack / CV</tspan>
      </text>

      <!-- Skill Stack divider line -->
      <line class="border-line" x1="0" y1="85" x2="520" y2="85" />

      <!-- Skill Categories -->
      <g transform="translate(0, 105)">
        <text class="terminal-text" x="0" y="0">
          <tspan class="key-text">LANGUAGES : </tspan>
          <tspan class="val-text">{languages_str}</tspan>
        </text>

        <text class="terminal-text" x="0" y="20">
          <tspan class="key-text">FRONTEND  : </tspan>
          <tspan class="val-text">{frontend_str}</tspan>
        </text>

        <text class="terminal-text" x="0" y="40">
          <tspan class="key-text">BACKEND   : </tspan>
          <tspan class="val-text">{backend_str}</tspan>
        </text>

        <text class="terminal-text" x="0" y="60">
          <tspan class="key-text">DATABASE  : </tspan>
          <tspan class="val-text">{database_str}</tspan>
        </text>

        <text class="terminal-text" x="0" y="80">
          <tspan class="key-text">AI &amp; ML   : </tspan>
          <tspan class="val-text">{ai_str}</tspan>
        </text>
      </g>

      <line class="border-line" x1="0" y1="205" x2="520" y2="205" />
      
      <text class="terminal-text" x="0" y="225">
        <tspan class="key-text">STATUS    : </tspan>
        <tspan class="val-text">Learning &amp; Building...</tspan>
        <rect class="cursor" x="235" y="213" width="8" height="13" />
      </text>
    </g>
  </g>
</svg>
'''
    
    os.makedirs(os.path.dirname(output_svg_path), exist_ok=True)
    with open(output_svg_path, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    print(f"[OK] Terminal info SVG generated: {output_svg_path}")

if __name__ == "__main__":
    profile_json = "data/profile.json"
    svg_out = "assets/terminal-info.svg"
    try:
        generate_terminal_svg(profile_json, svg_out)
    except Exception as e:
        print(f"Error in generate_terminal.py: {e}")
        sys.exit(1)

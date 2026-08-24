import os
import sys
import json
import requests
from datetime import datetime, timedelta

def get_contribution_data(username):
    # GitHub GraphQL API requires a token
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("[WARN] GITHUB_TOKEN not found. Contribution fetch will use mock fallback to prevent build failures.")
        return None

    headers = {"Authorization": f"Bearer {token}"}
    
    # Query for the last 12 months of contributions
    query = """
    query($userName: String!) {
      user(login: $userName) {
        contributionsCollection {
          contributionCalendar {
            totalContributions
            weeks {
              contributionDays {
                contributionCount
                date
                color
              }
            }
          }
        }
      }
    }
    """
    variables = {"userName": username}
    
    try:
        response = requests.post(
            "https://api.github.com/graphql",
            json={"query": query, "variables": variables},
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            res_json = response.json()
            if "errors" in res_json:
                print(f"[ERROR] GraphQL errors: {res_json['errors']}")
                return None
            return res_json.get("data", {}).get("user", {}).get("contributionsCollection", {}).get("contributionCalendar")
        else:
            print(f"[ERROR] API HTTP status: {response.status_code}")
            return None
    except Exception as e:
        print(f"[ERROR] Failed connection to GitHub API: {e}")
        return None

def calculate_streaks(weeks_data):
    if not weeks_data:
        return "N/A", "N/A", "N/A", "N/A"
        
    flat_days = []
    for w in weeks_data:
        for d in w.get("contributionDays", []):
            flat_days.append(d)
            
    # Sort days by date
    flat_days.sort(key=lambda x: x["date"])
    
    total_commits = sum(d["contributionCount"] for d in flat_days)
    active_days = sum(1 for d in flat_days if d["contributionCount"] > 0)
    
    # Calculate current and longest streak
    longest_streak = 0
    current_streak = 0
    temp_streak = 0
    
    # Analyze streaks up to today
    today_str = datetime.utcnow().strftime("%Y-%m-%d")
    yesterday_str = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    for d in flat_days:
        date_str = d["date"]
        count = d["contributionCount"]
        
        if count > 0:
            temp_streak += 1
            if temp_streak > longest_streak:
                longest_streak = temp_streak
        else:
            temp_streak = 0
            
    # Calculate current active streak ending today/yesterday
    temp_curr = 0
    # Walk backwards
    for d in reversed(flat_days):
        date_str = d["date"]
        count = d["contributionCount"]
        # Allow today or yesterday to preserve the streak
        if count > 0:
            temp_curr += 1
        elif date_str in (today_str, yesterday_str):
            # Streak might not have been updated today yet, skip check
            continue
        else:
            break
    current_streak = temp_curr

    return str(current_streak), str(longest_streak), str(active_days), str(total_commits)

def generate_contributions_svg(profile_path, output_svg_path):
    if not os.path.exists(profile_path):
        raise FileNotFoundError(f"Profile config not found at {profile_path}")
        
    with open(profile_path, 'r', encoding='utf-8') as f:
        profile = json.load(f)
        
    username = profile.get("username", "cyril-p-jose")
    calendar = get_contribution_data(username)
    
    if calendar:
        weeks = calendar.get("weeks", [])
        total_contributions = calendar.get("totalContributions", 0)
        curr_streak, max_streak, active, total_commits = calculate_streaks(weeks)
    else:
        # Fallback to N/A if API fails
        weeks = []
        curr_streak, max_streak, active, total_commits = "N/A", "N/A", "N/A", "N/A"
        total_contributions = "N/A"
        # Generate dummy week structures for rendering pattern
        for i in range(16):
            days = []
            for j in range(7):
                days.append({"contributionCount": (i + j) % 4, "date": ""})
            weeks.append({"contributionDays": days})

    # Render Terminal contribution grid
    svg_w = 600
    svg_h = 320

    # We show the last 20 weeks of data for responsive compact design
    display_weeks = weeks[-24:] if len(weeks) >= 24 else weeks
    
    cell_size = 14
    cell_gap = 4
    start_x = 40
    start_y = 95

    # Intensity ramp: ░ (0), ▒ (1-2), ▓ (3-5), █ (6+)
    def get_char_for_count(count):
        if count == 0:
            return "░", "#30363d"
        elif count <= 2:
            return "▒", "#8b949e"
        elif count <= 5:
            return "▓", "#c9d1d9"
        else:
            return "█", "#ffffff"

    # SVG Creation
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
    .matrix-title {{
      font-weight: bold;
      fill: #58a6ff;
    }}
    .metric-name {{
      fill: #8b949e;
    }}
    .metric-value {{
      fill: #ffffff;
      font-weight: bold;
    }}
    .border-line {{
      stroke: #30363d;
      stroke-width: 1;
    }}
    
    /* Individual cell animations */
    @keyframes pulse {{
      0% {{ opacity: 0.3; }}
      50% {{ opacity: 1.0; }}
      100% {{ opacity: 0.3; }}
    }}
    .cell-anim {{
      animation: pulse 3s infinite ease-in-out;
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
  <text class="terminal-text" x="{svg_w // 2}" y="32" text-anchor="middle" fill="#8b949e">./contributions.sh</text>

  <g transform="translate(30, 70)">
    <text class="terminal-text matrix-title" x="0" y="0">CONTRIBUTION MATRIX (LAST 24 WEEKS)</text>
    
    <!-- Render matrix cells -->
'''

    # Render cell blocks
    for col_idx, week in enumerate(display_weeks):
        x = start_x + (col_idx * (cell_size + cell_gap))
        days = week.get("contributionDays", [])
        for row_idx, day in enumerate(days):
            y = start_y + (row_idx * (cell_size + cell_gap))
            count = day.get("contributionCount", 0)
            char, color = get_char_for_count(count)
            # Add micro-animation offset based on coordinates
            delay = (col_idx * 0.05) + (row_idx * 0.1)
            
            # Using rect blocks instead of chars for visual precision, styled with color
            svg_content += f'    <rect class="cell-anim" x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" fill="{color}" rx="2" style="animation-delay: {delay:.2f}s" />\n'

    # Add metrics summary below matrix
    y_metrics = start_y + 7 * (cell_size + cell_gap) + 40
    svg_content += f'''
    <line class="border-line" x1="0" y1="{y_metrics - 20}" x2="540" y2="{y_metrics - 20}" />

    <text class="terminal-text" x="0" y="{y_metrics}">
      <tspan class="metric-name">CURRENT STREAK : </tspan>
      <tspan class="metric-value">{curr_streak} DAYS</tspan>
      <tspan class="metric-name" dx="40">LONGEST STREAK : </tspan>
      <tspan class="metric-value">{max_streak} DAYS</tspan>
    </text>

    <text class="terminal-text" x="0" y="{y_metrics + 22}">
      <tspan class="metric-name">ACTIVE DAYS    : </tspan>
      <tspan class="metric-value">{active}</tspan>
      <tspan class="metric-name" dx="95">TOTAL COMMITS  : </tspan>
      <tspan class="metric-value">{total_commits}</tspan>
    </text>
  </g>
</svg>
'''

    os.makedirs(os.path.dirname(output_svg_path), exist_ok=True)
    with open(output_svg_path, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    print(f"[OK] Contributions matrix SVG generated: {output_svg_path}")

if __name__ == "__main__":
    profile_json = "data/profile.json"
    svg_out = "assets/contributions.svg"
    try:
        generate_contributions_svg(profile_json, svg_out)
    except Exception as e:
        print(f"Error in generate_contributions.py: {e}")
        sys.exit(1)

import os
import sys
import json
import requests
from datetime import datetime

def fetch_recent_activity(username):
    url = f"https://api.github.com/users/{username}/events/public"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"[WARN] Failed to fetch events (HTTP {response.status_code})")
            return None
    except Exception as e:
        print(f"[WARN] Error connection to GitHub events: {e}")
        return None

def format_activities(events):
    if not events:
        return [
            "ACTIVITY STATUS",
            "Live data unavailable (Check connectivity or GITHUB_TOKEN)"
        ]

    formatted = []
    # Limit to top 5 activity items
    count = 0
    for event in events:
        if count >= 4:
            break
        etype = event.get("type")
        repo_name = event.get("repo", {}).get("name", "")
        # Remove username prefix from repo name
        if "/" in repo_name:
            repo_name = repo_name.split("/", 1)[1]
            
        created_at = event.get("created_at", "")
        # Parse date
        try:
            dt = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")
            date_str = dt.strftime("%b %d")
        except:
            date_str = created_at[:10]

        if etype == "PushEvent":
            commits = event.get("payload", {}).get("commits", [])
            commit_msg = commits[0].get("message", "Commit") if commits else "Commit"
            # Truncate msg
            if len(commit_msg) > 30:
                commit_msg = commit_msg[:27] + "..."
            formatted.append(f"[{date_str}]  PUSHED to {repo_name}: {commit_msg}")
            count += 1
        elif etype == "CreateEvent":
            ref_type = event.get("payload", {}).get("ref_type", "repo")
            formatted.append(f"[{date_str}]  CREATED {ref_type} on {repo_name}")
            count += 1
        elif etype == "PullRequestEvent":
            action = event.get("payload", {}).get("action", "opened")
            num = event.get("payload", {}).get("number", "")
            formatted.append(f"[{date_str}]  PR #{num} {action} in {repo_name}")
            count += 1
        elif etype == "IssuesEvent":
            action = event.get("payload", {}).get("action", "opened")
            num = event.get("payload", {}).get("issue", {}).get("number", "")
            formatted.append(f"[{date_str}]  ISSUE #{num} {action} in {repo_name}")
            count += 1

    if not formatted:
        formatted.append("No recent activity found.")
    return formatted

def generate_activity_svg(profile_path, output_svg_path):
    if not os.path.exists(profile_path):
        raise FileNotFoundError(f"Profile config not found at {profile_path}")
        
    with open(profile_path, 'r', encoding='utf-8') as f:
        profile = json.load(f)
        
    username = profile.get("username", "cyril-p-jose")
    events = fetch_recent_activity(username)
    activities = format_activities(events)

    svg_w = 600
    svg_h = 200

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
    .prompt-text {{
      fill: #58a6ff;
      font-weight: bold;
    }}
    .cmd-text {{
      fill: #8b949e;
    }}
    .activity-title {{
      font-weight: bold;
      fill: #3fb950;
    }}
    
    @keyframes blink {{
      50% {{ opacity: 0; }}
    }}
    .cursor {{
      animation: blink 0.8s infinite;
      fill: #3fb950;
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
  <text class="terminal-text" x="{svg_w // 2}" y="32" text-anchor="middle" fill="#8b949e">git log --oneline</text>

  <g transform="translate(30, 75)">
    <text class="terminal-text prompt-text" x="0" y="0">$</text>
    <text class="terminal-text cmd-text" x="15" y="0">git log -n 4 --oneline</text>
'''

    # Add activity lines
    y_offset = 25
    for idx, act in enumerate(activities):
        # Escape characters
        act_escaped = act.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        svg_content += f'    <text class="terminal-text" x="15" y="{y_offset}">{act_escaped}</text>\n'
        y_offset += 22

    # Blinking cursor after content
    svg_content += f'''
    <rect class="cursor" x="15" y="{y_offset - 10}" width="8" height="12" />
  </g>
</svg>
'''

    os.makedirs(os.path.dirname(output_svg_path), exist_ok=True)
    with open(output_svg_path, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    print(f"[OK] Activity log SVG generated: {output_svg_path}")

if __name__ == "__main__":
    profile_json = "data/profile.json"
    svg_out = "assets/activity.svg"
    try:
        generate_activity_svg(profile_json, svg_out)
    except Exception as e:
        print(f"Error in generate_activity.py: {e}")
        sys.exit(1)

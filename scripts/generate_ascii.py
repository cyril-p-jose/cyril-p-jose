import os
import sys
import cv2
import numpy as np
from PIL import Image

def generate_ascii_svg(image_path, output_svg_path, cols=60, scale=0.45):
    # Contrast ramp from dark to light representing terminal intensity
    # Best ASCII ramp for rich features:
    ramp = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. "
    
    # Read Image
    if not os.path.exists(image_path):
        print(f"Error: Image {image_path} does not exist. Creating a fallback pattern.")
        create_fallback_image(image_path)

    # Load Image
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not load image at {image_path}")

    # Remove background using rembg if available
    try:
        from rembg import remove
        print("[INFO] Attempting background removal using rembg...")
        pil_img = Image.open(image_path)
        no_bg_img = remove(pil_img)
        # Convert PIL back to CV2
        img = cv2.cvtColor(np.array(no_bg_img), cv2.COLOR_RGBA2BGRA)
        # Separate mask
        alpha = img[:, :, 3]
        img = img[:, :, :3]
        # Make transparent parts black
        img[alpha == 0] = [0, 0, 0]
    except Exception as e:
        print(f"[WARN] rembg could not be used (falling back to simple grayscale): {e}")

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Improve contrast using CLAHE
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)

    # Resize keeping aspect ratio
    h, w = gray.shape
    img_w = cols
    img_h = int(h / w * img_w * scale)
    gray_resized = cv2.resize(gray, (img_w, img_h))

    # Calculate sizes for SVG
    # A single monospace character is roughly 8px wide, 14px high
    char_w = 8
    char_h = 14
    svg_w = img_w * char_w + 40
    svg_h = img_h * char_h + 160

    # Build ASCII strings
    ascii_rows = []
    for r in range(img_h):
        row_chars = []
        for c in range(img_w):
            val = gray_resized[r, c]
            char_idx = int((val / 255.0) * (len(ramp) - 1))
            row_chars.append(ramp[char_idx])
        ascii_rows.append("".join(row_chars))

    # Generate SVGs with CSS terminal styling & animation
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
      font-size: 11px;
      fill: #c9d1d9;
    }}
    .ascii-text {{
      font-family: 'Fira Code', 'Courier New', Courier, monospace;
      font-size: 11.5px;
      font-weight: bold;
      fill: #ffffff;
      white-space: pre;
    }}
    .green-text {{
      fill: #58a6ff;
    }}
    .prompt-text {{
      fill: #58a6ff;
      font-weight: bold;
    }}
    .cmd-text {{
      fill: #8b949e;
    }}
    .status-text {{
      fill: #3fb950;
      font-weight: bold;
    }}

    /* Animation effects */
    @keyframes typing {{
      from {{ width: 0; }}
      to {{ width: 100%; }}
    }}
    @keyframes blink {{
      50% {{ opacity: 0; }}
    }}
    @keyframes reveal {{
      from {{ opacity: 0; transform: translateY(10px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}
    
    .cursor {{
      animation: blink 0.8s infinite;
      fill: #58a6ff;
    }}

    .anim-line-1 {{
      opacity: 0;
      animation: reveal 0.4s ease-out forwards;
      animation-delay: 0.2s;
    }}
    .anim-line-2 {{
      opacity: 0;
      animation: reveal 0.4s ease-out forwards;
      animation-delay: 0.8s;
    }}
    .anim-line-3 {{
      opacity: 0;
      animation: reveal 0.4s ease-out forwards;
      animation-delay: 1.4s;
    }}
    .anim-line-4 {{
      opacity: 0;
      animation: reveal 0.4s ease-out forwards;
      animation-delay: 2.0s;
    }}
    
    .ascii-art-group {{
      opacity: 0;
      animation: reveal 1.0s cubic-bezier(0.16, 1, 0.3, 1) forwards;
      animation-delay: 2.8s;
    }}

    .anim-line-ready {{
      opacity: 0;
      animation: reveal 0.4s ease-out forwards;
      animation-delay: 4.0s;
    }}
  </style>

  <!-- Window Frame -->
  <rect class="terminal-bg" x="10" y="10" width="{svg_w - 20}" height="{svg_h - 20}" />
  
  <!-- Title bar -->
  <path class="header-bar" d="M 10,18 A 8,8 0 0 1 18,10 L {svg_w - 18},10 A 8,8 0 0 1 {svg_w - 10},18 L {svg_w - 10},45 L 10,45 Z" />
  
  <!-- Window buttons -->
  <circle class="circle-red" cx="30" cy="28" r="6" />
  <circle class="circle-yellow" cx="50" cy="28" r="6" />
  <circle class="circle-green" cx="70" cy="28" r="6" />
  
  <!-- Window Title -->
  <text class="terminal-text" x="{svg_w // 2}" y="32" text-anchor="middle" fill="#8b949e">cyril@github: ~/profile_pic</text>

  <!-- CLI Prompt animations -->
  <g class="anim-line-1">
    <text class="terminal-text prompt-text" x="30" y="75">$</text>
    <text class="terminal-text cmd-text" x="50" y="75">loading profile_photo.png...</text>
  </g>

  <g class="anim-line-2">
    <text class="terminal-text prompt-text" x="30" y="95">&gt;</text>
    <text class="terminal-text cmd-text" x="50" y="95">rendering grayscale matrix...</text>
  </g>

  <g class="anim-line-3">
    <text class="terminal-text prompt-text" x="30" y="115">&gt;</text>
    <text class="terminal-text cmd-text" x="50" y="115">running contrast equalization (CLAHE)...</text>
  </g>

  <g class="anim-line-4">
    <text class="terminal-text prompt-text" x="30" y="135">&gt;</text>
    <text class="terminal-text cmd-text" x="50" y="135">mapping pixels to character ramp...</text>
  </g>

  <!-- ASCII Art Output -->
  <g class="ascii-art-group">
'''

    # Add each line of ASCII art
    y_start = 165
    for idx, row in enumerate(ascii_rows):
        y_pos = y_start + (idx * char_h)
        # Escape any SVG entities in row
        row_escaped = row.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        svg_content += f'    <text class="ascii-text" x="30" y="{y_pos}">{row_escaped}</text>\n'

    # Finish SVG body
    y_ready = y_start + (img_h * char_h) + 20
    svg_content += f'''  </g>

  <g class="anim-line-ready">
    <text class="terminal-text prompt-text" x="30" y="{y_ready}">&gt;</text>
    <text class="terminal-text status-text" x="50" y="{y_ready}">SYSTEM ONLINE (ASCII RENDER COMPLETED)</text>
    <rect class="cursor" x="350" y="{y_ready - 10}" width="8" height="12" />
  </g>
</svg>
'''
    
    # Save SVG
    os.makedirs(os.path.dirname(output_svg_path), exist_ok=True)
    with open(output_svg_path, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    print(f"[OK] ASCII portrait SVG generated: {output_svg_path}")

def create_fallback_image(image_path):
    # Generates a dummy monochrome template image with a circular face design if none exists
    os.makedirs(os.path.dirname(image_path), exist_ok=True)
    img = np.zeros((300, 300, 3), dtype=np.uint8)
    # Draw simple hacker icon face
    cv2.circle(img, (150, 150), 90, (255, 255, 255), -1)
    cv2.circle(img, (150, 150), 80, (0, 0, 0), -1)
    # Eyes
    cv2.circle(img, (115, 130), 12, (255, 255, 255), -1)
    cv2.circle(img, (185, 130), 12, (255, 255, 255), -1)
    # Smile
    cv2.ellipse(img, (150, 175), (40, 25), 0, 0, 180, (255, 255, 255), 5)
    cv2.imwrite(image_path, img)
    print(f"[INFO] Created a fallback dummy profile photo at {image_path}")

if __name__ == "__main__":
    img_in = "input/profile-photo.png"
    svg_out = "assets/ascii-profile.svg"
    try:
        generate_ascii_svg(img_in, svg_out)
    except Exception as e:
        print(f"Error in generate_ascii.py: {e}")
        sys.exit(1)

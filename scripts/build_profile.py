import os
import sys
import json
import subprocess

def run_script(script_name):
    script_path = os.path.join("scripts", script_name)
    if not os.path.exists(script_path):
        print(f"[FAIL] Script {script_name} does not exist!")
        return False
    try:
        print(f"[RUNNING] {script_name}...")
        result = subprocess.run([sys.executable, script_path], capture_output=True, text=True, check=True)
        if result.stdout:
            print(result.stdout.strip())
        return True
    except subprocess.CalledProcessError as e:
        print(f"[FAIL] Script {script_name} exited with error code {e.returncode}")
        if e.stdout:
            print(f"Stdout:\n{e.stdout}")
        if e.stderr:
            print(f"Stderr:\n{e.stderr}")
        return False

def validate_svg(filepath):
    if not os.path.exists(filepath):
        print(f"[FAIL] Expected SVG not found: {filepath}")
        return False
    # Simple check for tags
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    if "<svg" not in content or "</svg>" not in content:
        print(f"[FAIL] SVG format validation failed for {filepath}")
        return False
    return True

def main():
    print("=" * 44)
    print(" CYRIL P JOSE — PROFILE BUILD SYSTEM")
    print("=" * 44)

    # 1. Validate profile.json
    profile_json = os.path.join("data", "profile.json")
    if not os.path.exists(profile_json):
        print("[FAIL] Missing data/profile.json")
        sys.exit(1)
        
    try:
        with open(profile_json, 'r', encoding='utf-8') as f:
            json.load(f)
        print("[OK] Profile data loaded")
    except Exception as e:
        print(f"[FAIL] Invalid JSON inside profile.json: {e}")
        sys.exit(1)

    # 2. Check profile-photo exists or make fallback
    photo_path = os.path.join("input", "profile-photo.png")
    os.makedirs("input", exist_ok=True)
    if not os.path.exists(photo_path):
        print("[INFO] input/profile-photo.png not found, creating a fallback dummy image...")
        # Import internally to avoid dependencies if just checking, but generate_ascii needs it anyway
        try:
            import numpy as np
            import cv2
            img = np.zeros((300, 300, 3), dtype=np.uint8)
            cv2.circle(img, (150, 150), 90, (255, 255, 255), -1)
            cv2.circle(img, (150, 150), 80, (0, 0, 0), -1)
            cv2.circle(img, (115, 130), 12, (255, 255, 255), -1)
            cv2.circle(img, (185, 130), 12, (255, 255, 255), -1)
            cv2.ellipse(img, (150, 175), (40, 25), 0, 0, 180, (255, 255, 255), 5)
            cv2.imwrite(photo_path, img)
            print("[OK] Fallback dummy image created at input/profile-photo.png")
        except Exception as ex:
            print(f"[WARN] Could not create fallback dummy image: {ex}")

    # Run generation scripts
    success = True
    success &= run_script("generate_ascii.py")
    success &= run_script("generate_terminal.py")
    success &= run_script("generate_contributions.py")
    success &= run_script("generate_activity.py")
    success &= run_script("generate_banner.py")

    # Validate output files
    print("\nValidating Assets...")
    svgs = [
        "assets/ascii-profile.svg",
        "assets/terminal-info.svg",
        "assets/contributions.svg",
        "assets/activity.svg",
        "assets/banner.svg"
    ]
    for s in svgs:
        if validate_svg(s):
            print(f"[OK] {os.path.basename(s)} generated &amp; verified")
        else:
            success = False

    print("=" * 44)
    if success:
        print(" BUILD COMPLETE SUCCESSFUL")
    else:
        print(" BUILD FAILED - CHECK ERRORS ABOVE")
        sys.exit(1)
    print("=" * 44)

if __name__ == "__main__":
    main()

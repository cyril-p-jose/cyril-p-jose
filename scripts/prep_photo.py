#!/usr/bin/env python3
"""
Prepare a user portrait photo for high-clarity ASCII conversion:
  1. Remove background (rembg) to isolate subject.
  2. Apply CLAHE local contrast boost so facial contours and features remain distinct.
  3. Feather edges and composite onto pure white (mapping to blank space).

Usage:
  python scripts/prep_photo.py <path_to_photo.jpg> [output_path.png]
"""
import os
import sys
import cv2
import numpy as np
from PIL import Image
from rembg import remove

HERE = os.path.dirname(os.path.abspath(__file__))
INP = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "assets", "source-photo.jpg")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "assets", "source-prepped.png")


def prep_photo():
    if not os.path.exists(INP):
        print(f"Error: Input photo '{INP}' not found. Please provide a valid photo file.", file=sys.stderr)
        sys.exit(1)

    print(f"Loading '{INP}'...")
    img_rgba = Image.open(INP).convert("RGBA")

    print("Removing background with AI (rembg)...")
    cut = remove(img_rgba)
    rgb = np.array(cut.convert("RGB"))
    alpha = np.array(cut.split()[-1])

    print("Enhancing local contrast with CLAHE...")
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.2, tileGridSize=(8, 8))
    gray = clahe.apply(gray)

    # Composite onto white with feathered mask
    mask = alpha.astype(np.float32) / 255.0
    mask = cv2.GaussianBlur(mask, (0, 0), 1.0)
    out = gray.astype(np.float32) * mask + 255.0 * (1.0 - mask)
    out = np.clip(out, 0, 255).astype(np.uint8)

    res_img = Image.fromarray(out, mode="L")

    # Crop head & shoulders if oversized
    h, w = out.shape
    if h > 800 and w > 500:
        res_img = res_img.crop((int(w * 0.05), int(h * 0.02), int(w * 0.95), int(h * 0.75)))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    res_img.save(OUT)
    print(f"Saved prepped image to {OUT} ({res_img.size[0]}x{res_img.size[1]})")


if __name__ == "__main__":
    prep_photo()

#!/usr/bin/env python3
"""Improve the oval face template with better shading."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.canvas import Canvas
import math

BASE = (255, 0, 0, 255)
SHADOW1 = (200, 0, 0, 255)
SHADOW2 = (150, 0, 0, 255)
HIGHLIGHT = (255, 100, 100, 255)
HIGHLIGHT2 = (255, 180, 180, 255)
OUTLINE = (100, 0, 0, 255)

def create_improved_oval():
    """Better oval face with refined shading."""
    WIDTH, HEIGHT = 32, 40
    canvas = Canvas(WIDTH, HEIGHT)

    cx, cy = WIDTH // 2, HEIGHT // 2 + 2
    rx, ry = 13, 17  # Oval radii

    for y in range(HEIGHT):
        for x in range(WIDTH):
            # Oval with chin taper
            dx = (x - cx) / rx

            # Chin narrowing
            if y > cy + 6:
                chin_factor = (y - cy - 6) / 12
                dx = dx / (1 - chin_factor * 0.25)

            dy = (y - cy) / ry
            dist = dx * dx + dy * dy

            if dist <= 1.0:
                # Determine zone for shading

                # Outline
                if dist > 0.92:
                    canvas.set_pixel_solid(x, y, OUTLINE)
                    continue

                # Left side shadow (ambient occlusion)
                if x < cx - 6 and dist > 0.6:
                    canvas.set_pixel_solid(x, y, SHADOW1)
                    continue

                # Deep shadow under chin
                if y > cy + 10 and dist > 0.7:
                    canvas.set_pixel_solid(x, y, SHADOW2)
                    continue

                # Chin shadow
                if y > cy + 8:
                    canvas.set_pixel_solid(x, y, SHADOW1)
                    continue

                # Forehead highlight
                if y < cy - 8 and x > cx - 3:
                    canvas.set_pixel_solid(x, y, HIGHLIGHT)
                    continue

                # Right cheek highlight
                if x > cx + 4 and y > cy - 4 and y < cy + 4:
                    canvas.set_pixel_solid(x, y, HIGHLIGHT)
                    continue

                # Nose bridge shadow hint
                if abs(x - cx) < 2 and y > cy - 2 and y < cy + 4:
                    canvas.set_pixel_solid(x, y, SHADOW1)
                    continue

                # Cheek blush area (subtle highlight)
                cheek_left = (x - (cx - 5)) ** 2 + (y - (cy + 2)) ** 2
                cheek_right = (x - (cx + 5)) ** 2 + (y - (cy + 2)) ** 2
                if cheek_left < 9 or cheek_right < 9:
                    canvas.set_pixel_solid(x, y, HIGHLIGHT)
                    continue

                # Base skin
                canvas.set_pixel_solid(x, y, BASE)

    os.makedirs("templates/anime_standard/faces", exist_ok=True)
    canvas.save("templates/anime_standard/faces/oval.png")
    print("Updated: templates/anime_standard/faces/oval.png")

    import json
    with open("templates/anime_standard/faces/oval.json", "w") as f:
        json.dump({
            "name": "oval",
            "anchor": [16, 22],
            "bounds": {
                "eye_region_y": 16,
                "nose_region_y": 26,
                "mouth_region_y": 32
            }
        }, f, indent=2)

if __name__ == "__main__":
    create_improved_oval()

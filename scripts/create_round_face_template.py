#!/usr/bin/env python3
"""Create round face template."""
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


def create_round_face():
    """Round, softer face shape - more circular than oval."""
    WIDTH, HEIGHT = 32, 36
    canvas = Canvas(WIDTH, HEIGHT)

    cx, cy = WIDTH // 2, HEIGHT // 2
    radius = 14  # More circular

    for y in range(HEIGHT):
        for x in range(WIDTH):
            # Nearly circular with slight chin point
            dx = (x - cx) / radius

            # Slight chin taper at bottom
            if y > cy + 5:
                chin_taper = (y - cy - 5) / 10
                dx = dx / (1 - chin_taper * 0.15)

            dy = (y - cy) / (radius + 2)  # Slightly taller
            dist = dx * dx + dy * dy

            if dist <= 1.0:
                if dist > 0.88:
                    canvas.set_pixel_solid(x, y, OUTLINE)
                elif x < cx - 5 and dist > 0.5:
                    # Left cheek shadow
                    canvas.set_pixel_solid(x, y, SHADOW1)
                elif y > cy + 8:
                    # Chin shadow
                    canvas.set_pixel_solid(x, y, SHADOW1)
                elif x > cx + 3 and y < cy - 3:
                    # Forehead/cheek highlight
                    canvas.set_pixel_solid(x, y, HIGHLIGHT)
                elif x > cx + 5 and y > cy - 5 and y < cy + 3:
                    # Cheek highlight
                    canvas.set_pixel_solid(x, y, HIGHLIGHT)
                else:
                    canvas.set_pixel_solid(x, y, BASE)

    os.makedirs("templates/anime_standard/faces", exist_ok=True)
    canvas.save("templates/anime_standard/faces/round.png")
    print("Created: templates/anime_standard/faces/round.png")

    import json
    with open("templates/anime_standard/faces/round.json", "w") as f:
        json.dump(
            {
                "name": "round",
                "anchor": [16, 18],
                "bounds": {
                    "eye_region_y": 14,
                    "nose_region_y": 22,
                    "mouth_region_y": 28,
                },
            },
            f,
            indent=2,
        )


if __name__ == "__main__":
    create_round_face()

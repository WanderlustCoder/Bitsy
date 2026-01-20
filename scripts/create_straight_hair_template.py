#!/usr/bin/env python3
"""Create straight hair templates (back and front)."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.canvas import Canvas
import math

# Placeholder colors
BASE = (255, 0, 0, 255)
SHADOW1 = (200, 0, 0, 255)
SHADOW2 = (150, 0, 0, 255)
HIGHLIGHT = (255, 100, 100, 255)
HIGHLIGHT2 = (255, 180, 180, 255)
OUTLINE = (100, 0, 0, 255)


def create_straight_back():
    """Straight hair back - long flowing hair."""
    WIDTH, HEIGHT = 60, 75
    canvas = Canvas(WIDTH, HEIGHT)
    cx = WIDTH // 2

    for y in range(HEIGHT):
        for x in range(WIDTH):
            # Hair width tapers slightly at bottom
            y_factor = y / HEIGHT
            half_width = 26 - (y_factor * 4)

            if abs(x - cx) < half_width:
                # Inside hair
                dist_from_center = abs(x - cx) / half_width

                # Top dome
                if y < 12:
                    dome_factor = (12 - y) / 12
                    if abs(x - cx) > half_width * (1 - dome_factor * 0.3):
                        continue

                # Shading - vertical strands
                strand_phase = (x * 0.5) % 8

                if dist_from_center > 0.85:
                    canvas.set_pixel_solid(x, y, OUTLINE)
                elif x < cx - 10:
                    # Left shadow
                    if strand_phase < 2:
                        canvas.set_pixel_solid(x, y, SHADOW2)
                    else:
                        canvas.set_pixel_solid(x, y, SHADOW1)
                elif x > cx + 10:
                    # Right highlight (rim area)
                    if strand_phase < 3:
                        canvas.set_pixel_solid(x, y, HIGHLIGHT2)
                    else:
                        canvas.set_pixel_solid(x, y, HIGHLIGHT)
                else:
                    # Center
                    if y < 15 and strand_phase > 4:
                        canvas.set_pixel_solid(x, y, HIGHLIGHT)
                    elif strand_phase < 2:
                        canvas.set_pixel_solid(x, y, SHADOW1)
                    else:
                        canvas.set_pixel_solid(x, y, BASE)

    os.makedirs("templates/anime_standard/hair", exist_ok=True)
    canvas.save("templates/anime_standard/hair/straight_back.png")
    print("Created: templates/anime_standard/hair/straight_back.png")

    # Create metadata
    import json
    with open("templates/anime_standard/hair/straight_back.json", "w") as f:
        json.dump({"name": "straight_back", "anchor": [30, 12], "layer": "back"}, f)


def create_straight_front():
    """Straight bangs - clean cut across forehead."""
    WIDTH, HEIGHT = 38, 20
    canvas = Canvas(WIDTH, HEIGHT)
    cx = WIDTH // 2

    for y in range(HEIGHT):
        for x in range(WIDTH):
            # Bangs taper toward bottom
            y_factor = y / HEIGHT
            half_width = 18 - (y_factor * 3)

            if abs(x - cx) < half_width and y > 2:
                dist = abs(x - cx) / half_width

                # Clean horizontal cut at bottom
                if y > HEIGHT - 4:
                    if y == HEIGHT - 1 or dist > 0.9:
                        canvas.set_pixel_solid(x, y, OUTLINE)
                    else:
                        canvas.set_pixel_solid(x, y, SHADOW1)
                elif dist > 0.9:
                    canvas.set_pixel_solid(x, y, OUTLINE)
                elif x < cx - 5:
                    canvas.set_pixel_solid(x, y, SHADOW1)
                elif x > cx + 5:
                    canvas.set_pixel_solid(x, y, HIGHLIGHT)
                else:
                    if y < 8:
                        canvas.set_pixel_solid(x, y, HIGHLIGHT)
                    else:
                        canvas.set_pixel_solid(x, y, BASE)

    canvas.save("templates/anime_standard/hair/straight_front.png")
    print("Created: templates/anime_standard/hair/straight_front.png")

    import json
    with open("templates/anime_standard/hair/straight_front.json", "w") as f:
        json.dump({"name": "straight_front", "anchor": [19, 0], "layer": "front"}, f)


if __name__ == "__main__":
    create_straight_back()
    create_straight_front()

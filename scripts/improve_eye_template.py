#!/usr/bin/env python3
"""Improve the large eye template with better detail."""
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
SECONDARY = (0, 255, 0, 255)  # Sclera

def create_improved_eye():
    """Better large anime eye with detailed iris and catchlights."""
    WIDTH, HEIGHT = 14, 12
    canvas = Canvas(WIDTH, HEIGHT)

    cx, cy = 7, 6

    # Eye shape - large anime style
    for y in range(HEIGHT):
        for x in range(WIDTH):
            # Eye opening shape
            dx = abs(x - cx)
            dy = abs(y - cy)

            # Rounded rectangle with pointed corners
            eye_width = 6 - (dy * 0.3)
            eye_height = 5 - (dx * 0.2)

            in_eye = dx < eye_width and dy < eye_height and y > 1 and y < HEIGHT - 1

            if in_eye:
                # Sclera base
                canvas.set_pixel_solid(x, y, SECONDARY)

                # Upper eyelid shadow on sclera
                if y < 4:
                    # Darken sclera near upper lid
                    canvas.set_pixel_solid(x, y, (0, 230, 0, 255))

                # Iris
                iris_cx, iris_cy = 7, 6
                iris_r = 4.5
                iris_dx = x - iris_cx
                iris_dy = y - iris_cy
                iris_dist = math.sqrt(iris_dx * iris_dx + iris_dy * iris_dy)

                if iris_dist < iris_r:
                    # Iris gradient - darker at top
                    if iris_dist < 1.5:
                        # Pupil
                        canvas.set_pixel_solid(x, y, SHADOW2)
                    elif y < iris_cy - 1:
                        # Upper iris - darkest
                        canvas.set_pixel_solid(x, y, SHADOW2)
                    elif y < iris_cy:
                        canvas.set_pixel_solid(x, y, SHADOW1)
                    elif iris_dist > iris_r - 1:
                        # Iris edge ring
                        canvas.set_pixel_solid(x, y, SHADOW1)
                    else:
                        # Mid iris
                        canvas.set_pixel_solid(x, y, BASE)

    # Primary catchlight (large, upper left)
    for dy in range(2):
        for dx in range(2):
            canvas.set_pixel_solid(4 + dx, 3 + dy, HIGHLIGHT2)

    # Secondary catchlight (small, lower right)
    canvas.set_pixel_solid(9, 7, HIGHLIGHT)

    # Upper eyelid line (thick for anime style)
    for x in range(2, 12):
        canvas.set_pixel_solid(x, 1, OUTLINE)
        canvas.set_pixel_solid(x, 2, OUTLINE)

    # Eyelid corners
    canvas.set_pixel_solid(1, 2, OUTLINE)
    canvas.set_pixel_solid(1, 3, OUTLINE)
    canvas.set_pixel_solid(12, 2, OUTLINE)
    canvas.set_pixel_solid(12, 3, OUTLINE)

    # Lower eyelid (subtle)
    canvas.set_pixel_solid(3, 10, OUTLINE)
    canvas.set_pixel_solid(4, 10, OUTLINE)
    canvas.set_pixel_solid(9, 10, OUTLINE)
    canvas.set_pixel_solid(10, 10, OUTLINE)

    # Eyelashes (top)
    canvas.set_pixel_solid(3, 0, OUTLINE)
    canvas.set_pixel_solid(5, 0, OUTLINE)
    canvas.set_pixel_solid(8, 0, OUTLINE)
    canvas.set_pixel_solid(10, 0, OUTLINE)

    os.makedirs("templates/anime_standard/eyes", exist_ok=True)
    canvas.save("templates/anime_standard/eyes/large.png")
    print("Updated: templates/anime_standard/eyes/large.png")

    import json
    with open("templates/anime_standard/eyes/large.json", "w") as f:
        json.dump({
            "name": "large",
            "anchor": [7, 6],
            "symmetric": True,
            "flip_for_right": True
        }, f, indent=2)

if __name__ == "__main__":
    create_improved_eye()

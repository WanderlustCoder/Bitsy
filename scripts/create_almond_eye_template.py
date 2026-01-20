#!/usr/bin/env python3
"""Create almond-shaped eye template."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.canvas import Canvas
import math

BASE = (255, 0, 0, 255)        # Iris base
SHADOW1 = (200, 0, 0, 255)     # Iris dark
SHADOW2 = (150, 0, 0, 255)     # Pupil
HIGHLIGHT = (255, 100, 100, 255)
HIGHLIGHT2 = (255, 180, 180, 255)  # Catchlight
OUTLINE = (100, 0, 0, 255)
SECONDARY = (0, 255, 0, 255)   # Sclera


def create_almond_eye():
    """Almond-shaped eye - narrower, more elegant."""
    WIDTH, HEIGHT = 14, 8
    canvas = Canvas(WIDTH, HEIGHT)

    cx, cy = 7, 4

    # Almond shape - pointed at corners
    for y in range(HEIGHT):
        for x in range(WIDTH):
            # Distance from center with almond shaping
            dx = abs(x - cx)
            dy = abs(y - cy)

            # Almond curve - narrower at edges
            edge_factor = dx / 7
            max_height = 3.5 * (1 - edge_factor * edge_factor)

            if dy < max_height and dx < 7:
                # Inside eye shape
                dist_from_center = math.sqrt(dx * dx + dy * dy) / 4

                # Sclera first
                canvas.set_pixel_solid(x, y, SECONDARY)

                # Iris in center
                iris_dx = abs(x - cx)
                iris_dy = abs(y - cy)
                iris_dist = math.sqrt(iris_dx * iris_dx + iris_dy * iris_dy)

                if iris_dist < 3:
                    if iris_dist < 1.2:
                        # Pupil
                        canvas.set_pixel_solid(x, y, SHADOW2)
                    elif y < cy:
                        # Upper iris - darker
                        canvas.set_pixel_solid(x, y, SHADOW1)
                    else:
                        canvas.set_pixel_solid(x, y, BASE)

    # Catchlights
    canvas.set_pixel_solid(5, 3, HIGHLIGHT2)
    canvas.set_pixel_solid(8, 5, HIGHLIGHT)

    # Eyelid lines
    for x in range(2, 12):
        edge_factor = abs(x - cx) / 7
        lid_y = int(1 + edge_factor * 2)
        if 0 <= lid_y < HEIGHT:
            canvas.set_pixel_solid(x, lid_y, OUTLINE)

    # Lower lid hint at corners
    canvas.set_pixel_solid(2, 5, OUTLINE)
    canvas.set_pixel_solid(11, 5, OUTLINE)

    os.makedirs("templates/anime_standard/eyes", exist_ok=True)
    canvas.save("templates/anime_standard/eyes/almond.png")
    print("Created: templates/anime_standard/eyes/almond.png")

    import json
    with open("templates/anime_standard/eyes/almond.json", "w") as f:
        json.dump({
            "name": "almond",
            "anchor": [7, 4],
            "symmetric": True,
            "flip_for_right": True
        }, f, indent=2)


if __name__ == "__main__":
    create_almond_eye()

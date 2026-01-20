#!/usr/bin/env python3
"""Create short hair templates."""
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

def create_short_back():
    """Short hair back - just covers the head."""
    WIDTH, HEIGHT = 50, 45
    canvas = Canvas(WIDTH, HEIGHT)
    cx = WIDTH // 2

    for y in range(HEIGHT):
        for x in range(WIDTH):
            # Rounded shape that follows head
            dx = (x - cx) / 22
            dy = (y - 18) / 20
            dist = dx * dx + dy * dy

            if dist <= 1.0 and y >= 3:
                if dist > 0.85:
                    canvas.set_pixel_solid(x, y, OUTLINE)
                elif x < cx - 8:
                    canvas.set_pixel_solid(x, y, SHADOW1)
                elif x > cx + 8:
                    if dist > 0.6:
                        canvas.set_pixel_solid(x, y, HIGHLIGHT2)
                    else:
                        canvas.set_pixel_solid(x, y, HIGHLIGHT)
                else:
                    if y < 15:
                        canvas.set_pixel_solid(x, y, HIGHLIGHT)
                    else:
                        canvas.set_pixel_solid(x, y, BASE)

                # Add some texture
                if (x + y) % 7 == 0 and dist < 0.7:
                    canvas.set_pixel_solid(x, y, SHADOW1)

    os.makedirs("templates/anime_standard/hair", exist_ok=True)
    canvas.save("templates/anime_standard/hair/short_back.png")
    print("Created: templates/anime_standard/hair/short_back.png")

    import json
    with open("templates/anime_standard/hair/short_back.json", "w") as f:
        json.dump({"name": "short_back", "anchor": [25, 15], "layer": "back"}, f)

def create_short_front():
    """Short spiky bangs."""
    WIDTH, HEIGHT = 36, 18
    canvas = Canvas(WIDTH, HEIGHT)
    cx = WIDTH // 2

    # Create spiky bangs
    spikes = [
        {"x": 6, "height": 12, "width": 5},
        {"x": 12, "height": 14, "width": 6},
        {"x": 18, "height": 16, "width": 6},
        {"x": 24, "height": 14, "width": 6},
        {"x": 30, "height": 12, "width": 5},
    ]

    for spike in spikes:
        sx, sh, sw = spike["x"], spike["height"], spike["width"]
        for y in range(HEIGHT):
            for x in range(sx - sw//2, sx + sw//2 + 1):
                if 0 <= x < WIDTH:
                    # Spike tapers to point
                    y_factor = y / sh
                    spike_width = sw * (1 - y_factor * 0.8)
                    if abs(x - sx) < spike_width / 2 and y < sh:
                        dist = abs(x - sx) / (spike_width / 2 + 0.1)
                        if dist > 0.8 or y < 2:
                            canvas.set_pixel_solid(x, y, OUTLINE)
                        elif x < sx:
                            canvas.set_pixel_solid(x, y, SHADOW1)
                        else:
                            canvas.set_pixel_solid(x, y, HIGHLIGHT)

    canvas.save("templates/anime_standard/hair/short_front.png")
    print("Created: templates/anime_standard/hair/short_front.png")

    import json
    with open("templates/anime_standard/hair/short_front.json", "w") as f:
        json.dump({"name": "short_front", "anchor": [18, 0], "layer": "front"}, f)

if __name__ == "__main__":
    create_short_back()
    create_short_front()

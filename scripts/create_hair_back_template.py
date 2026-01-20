#!/usr/bin/env python3
"""Create the back hair template - renders behind the face."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.canvas import Canvas
import math

# Template size - should cover area behind and around head
WIDTH, HEIGHT = 60, 70

# Placeholder colors (will be recolored at runtime)
BASE = (255, 0, 0, 255)        # Hair base
SHADOW1 = (200, 0, 0, 255)     # Hair shadow 1
SHADOW2 = (150, 0, 0, 255)     # Hair shadow 2 (deep)
HIGHLIGHT = (255, 100, 100, 255)  # Hair highlight
HIGHLIGHT2 = (255, 180, 180, 255) # Bright highlight (rim)
OUTLINE = (100, 0, 0, 255)     # Hair outline

def draw_wavy_back_hair():
    canvas = Canvas(WIDTH, HEIGHT)

    cx = WIDTH // 2  # Center x

    # Hair mass - large oval shape behind head
    for y in range(HEIGHT):
        for x in range(WIDTH):
            # Distance from center
            dx = (x - cx) / 25  # Horizontal radius ~25

            # Wavy vertical profile - wider at top, narrower at bottom
            y_factor = y / HEIGHT
            width_at_y = 1.0 - (y_factor * 0.3)  # Tapers toward bottom

            # Add waviness
            wave = math.sin(y * 0.15) * 3
            adjusted_x = x - wave
            dx_wavy = (adjusted_x - cx) / (25 * width_at_y)

            # Top curve (dome shape)
            if y < 15:
                dy = (y - 15) / 12
            else:
                dy = 0

            dist = dx_wavy * dx_wavy + dy * dy

            # Check if inside hair shape
            if y >= 3 and dist <= 1.0:
                # Determine shading based on position
                if x < cx - 8:
                    # Left side - shadow
                    if dist > 0.7:
                        canvas.set_pixel_solid(x, y, OUTLINE)
                    else:
                        canvas.set_pixel_solid(x, y, SHADOW1)
                elif x > cx + 8:
                    # Right side - could be rim light area (bright highlight)
                    if dist > 0.85:
                        canvas.set_pixel_solid(x, y, OUTLINE)
                    elif dist > 0.6:
                        canvas.set_pixel_solid(x, y, HIGHLIGHT2)  # Rim
                    else:
                        canvas.set_pixel_solid(x, y, BASE)
                else:
                    # Center
                    if dist > 0.85:
                        canvas.set_pixel_solid(x, y, OUTLINE)
                    elif y < 20:
                        # Top highlight
                        canvas.set_pixel_solid(x, y, HIGHLIGHT)
                    else:
                        canvas.set_pixel_solid(x, y, BASE)

    # Add some strand details
    for strand_x in [cx - 12, cx - 5, cx + 5, cx + 12]:
        for y in range(20, 65, 8):
            if 0 <= strand_x < WIDTH:
                canvas.set_pixel_solid(strand_x, y, SHADOW1)
                if strand_x + 1 < WIDTH:
                    canvas.set_pixel_solid(strand_x + 1, y + 1, SHADOW2)

    # Save
    os.makedirs("templates/anime_standard/hair", exist_ok=True)
    canvas.save("templates/anime_standard/hair/wavy_back.png")
    print("Created: templates/anime_standard/hair/wavy_back.png")

if __name__ == "__main__":
    draw_wavy_back_hair()

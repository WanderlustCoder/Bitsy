#!/usr/bin/env python3
"""Create the body template - shoulders and upper torso."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.canvas import Canvas
import math

# Template size - covers shoulders and upper body
WIDTH, HEIGHT = 70, 80

# Placeholder colors (will become clothing color)
BASE = (255, 0, 0, 255)
SHADOW1 = (200, 0, 0, 255)
SHADOW2 = (150, 0, 0, 255)
HIGHLIGHT = (255, 100, 100, 255)
HIGHLIGHT2 = (255, 180, 180, 255)
OUTLINE = (100, 0, 0, 255)

# Secondary color for skin (neck)
SECONDARY = (0, 255, 0, 255)

def draw_body():
    canvas = Canvas(WIDTH, HEIGHT)

    cx = WIDTH // 2  # Center

    # Neck (secondary color - will become skin)
    neck_width = 10
    neck_height = 12
    for y in range(neck_height):
        for x in range(cx - neck_width // 2, cx + neck_width // 2):
            # Slight taper
            taper = y / neck_height * 2
            if abs(x - cx) < neck_width // 2 - taper:
                if x < cx - 2:
                    # Left shadow
                    canvas.set_pixel_solid(x, y, (0, 200, 0, 255))  # Shadow secondary
                elif x > cx + 2:
                    # Right highlight
                    canvas.set_pixel_solid(x, y, (0, 255, 100, 255))  # Highlight secondary
                else:
                    canvas.set_pixel_solid(x, y, SECONDARY)

    # Shoulders and torso
    for y in range(8, HEIGHT):
        for x in range(WIDTH):
            # Shoulder curve
            shoulder_y = 8

            if y < 25:
                # Shoulders - curved shape
                # Left shoulder
                left_shoulder_cx = 12
                right_shoulder_cx = WIDTH - 12

                shoulder_radius = 15

                # Check if in left shoulder
                dx_left = (x - left_shoulder_cx)
                dy = (y - shoulder_y)
                dist_left = math.sqrt(dx_left * dx_left + dy * dy)

                # Check if in right shoulder
                dx_right = (x - right_shoulder_cx)
                dist_right = math.sqrt(dx_right * dx_right + dy * dy)

                # Center body
                body_half_width = 18 + (y - shoulder_y) * 0.3  # Widens slightly
                in_center = abs(x - cx) < body_half_width and y > 12

                in_shoulder = (dist_left < shoulder_radius and x < cx) or \
                             (dist_right < shoulder_radius and x > cx) or \
                             in_center

                if in_shoulder:
                    # Determine shading
                    if x < cx - 10:
                        # Left - shadow side
                        if dist_left > shoulder_radius - 3:
                            canvas.set_pixel_solid(x, y, OUTLINE)
                        else:
                            canvas.set_pixel_solid(x, y, SHADOW1)
                    elif x > cx + 10:
                        # Right - highlight/rim side
                        if dist_right > shoulder_radius - 3:
                            canvas.set_pixel_solid(x, y, OUTLINE)
                        elif dist_right > shoulder_radius - 6:
                            canvas.set_pixel_solid(x, y, HIGHLIGHT2)  # Rim light
                        else:
                            canvas.set_pixel_solid(x, y, BASE)
                    else:
                        # Center
                        if y < 18:
                            canvas.set_pixel_solid(x, y, HIGHLIGHT)
                        else:
                            canvas.set_pixel_solid(x, y, BASE)
            else:
                # Lower torso
                body_half_width = 22 + (y - 25) * 0.2
                if abs(x - cx) < body_half_width:
                    # Edge outline
                    if abs(x - cx) > body_half_width - 2:
                        canvas.set_pixel_solid(x, y, OUTLINE)
                    elif x < cx - 8:
                        canvas.set_pixel_solid(x, y, SHADOW1)
                    elif x > cx + 8:
                        canvas.set_pixel_solid(x, y, HIGHLIGHT)
                    else:
                        canvas.set_pixel_solid(x, y, BASE)

    # Add collar detail
    collar_y = 12
    for x in range(cx - 12, cx + 12):
        dist = abs(x - cx)
        if dist > 4:
            canvas.set_pixel_solid(x, collar_y, SHADOW2)
            canvas.set_pixel_solid(x, collar_y + 1, SHADOW1)

    # Save
    os.makedirs("templates/anime_standard/bodies", exist_ok=True)
    canvas.save("templates/anime_standard/bodies/neutral.png")
    print("Created: templates/anime_standard/bodies/neutral.png")

if __name__ == "__main__":
    draw_body()

#!/usr/bin/env python3
"""Create the front hair template - bangs that overlay the face."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.canvas import Canvas
import math

# Template size - covers forehead area
WIDTH, HEIGHT = 40, 25

# Placeholder colors
BASE = (255, 0, 0, 255)
SHADOW1 = (200, 0, 0, 255)
SHADOW2 = (150, 0, 0, 255)
HIGHLIGHT = (255, 100, 100, 255)
HIGHLIGHT2 = (255, 180, 180, 255)
OUTLINE = (100, 0, 0, 255)


def draw_wavy_bangs():
    canvas = Canvas(WIDTH, HEIGHT)

    cx = WIDTH // 2

    # Create wavy bangs with multiple strands
    # Bangs sweep from left to right

    for y in range(HEIGHT):
        for x in range(WIDTH):
            # Multiple bang strands
            in_bang = False
            shade = BASE

            # Define several bang strands with different curves
            strands = [
                {"cx": 8, "width": 6, "curve": 0.1, "phase": 0},
                {"cx": 15, "width": 7, "curve": 0.08, "phase": 0.5},
                {"cx": 22, "width": 8, "curve": 0.05, "phase": 1.0},  # Center strand
                {"cx": 28, "width": 7, "curve": 0.08, "phase": 1.5},
                {"cx": 34, "width": 6, "curve": 0.1, "phase": 2.0},
            ]

            for strand in strands:
                # Strand curves based on y position
                curve_offset = math.sin(y * strand["curve"] + strand["phase"]) * 2
                strand_cx = strand["cx"] + curve_offset

                # Strand tapers toward bottom
                y_factor = y / HEIGHT
                strand_width = strand["width"] * (1.0 - y_factor * 0.4)

                dist_from_strand = abs(x - strand_cx)

                if dist_from_strand < strand_width / 2:
                    in_bang = True
                    # Shading within strand
                    if dist_from_strand < strand_width / 4:
                        if y < 8:
                            shade = HIGHLIGHT
                        else:
                            shade = BASE
                    else:
                        shade = SHADOW1

                    # Bottom edge darker
                    if y > HEIGHT - 5:
                        shade = SHADOW2
                    break

            if in_bang:
                # Add outline at edges
                edge_check = False
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < WIDTH and 0 <= ny < HEIGHT:
                            # Check if neighbor would be outside bang
                            neighbor_in = False
                            for strand in strands:
                                curve_offset = math.sin(
                                    ny * strand["curve"] + strand["phase"]
                                ) * 2
                                strand_cx = strand["cx"] + curve_offset
                                y_factor = ny / HEIGHT
                                strand_width = strand["width"] * (1.0 - y_factor * 0.4)
                                if abs(nx - strand_cx) < strand_width / 2:
                                    neighbor_in = True
                                    break
                            if not neighbor_in:
                                edge_check = True
                                break
                    if edge_check:
                        break

                if edge_check and y > 2:
                    canvas.set_pixel_solid(x, y, OUTLINE)
                else:
                    canvas.set_pixel_solid(x, y, shade)

    # Save
    os.makedirs("templates/anime_standard/hair", exist_ok=True)
    canvas.save("templates/anime_standard/hair/wavy_front.png")
    print("Created: templates/anime_standard/hair/wavy_front.png")


if __name__ == "__main__":
    draw_wavy_bangs()

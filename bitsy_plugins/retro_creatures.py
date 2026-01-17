"""
Example generator plugin - Retro creatures.

Demonstrates how to create a GeneratorPlugin.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plugins import GeneratorPlugin
from core import Canvas
import random


class GhostGenerator(GeneratorPlugin):
    """Generates simple ghost sprites."""

    name = "ghost"
    category = "creature"
    description = "Simple ghost with wavy bottom"
    version = "1.0.0"
    author = "Bitsy Examples"
    tags = ["retro", "enemy", "spooky"]

    def generate(self, width=16, height=16, seed=None, **kwargs):
        """Generate a ghost sprite."""
        if seed is not None:
            random.seed(seed)

        canvas = Canvas(width, height)
        color = kwargs.get('color', (200, 200, 255, 255))
        eye_color = kwargs.get('eye_color', (0, 0, 0, 255))

        # Ghost body - rounded top
        center_x = width // 2
        center_y = height // 3

        # Draw body
        for y in range(height):
            for x in range(width):
                # Top dome
                dx = x - center_x
                dy = y - center_y
                radius = width // 3

                if y < height * 2 // 3:
                    # Dome top
                    if dx * dx + dy * dy <= radius * radius:
                        canvas.set_pixel(x, y, color)
                    # Body sides
                    elif y > center_y and abs(dx) <= radius:
                        canvas.set_pixel(x, y, color)
                else:
                    # Wavy bottom
                    if abs(dx) <= radius:
                        wave = int(2 * abs(((x + random.randint(0, 2)) % 4) - 2))
                        if y < height - wave:
                            canvas.set_pixel(x, y, color)

        # Eyes
        eye_y = center_y + 2
        left_eye_x = center_x - width // 6
        right_eye_x = center_x + width // 6

        for eye_x in [left_eye_x, right_eye_x]:
            canvas.set_pixel(eye_x, eye_y, eye_color)
            canvas.set_pixel(eye_x, eye_y + 1, eye_color)

        return canvas


class BatGenerator(GeneratorPlugin):
    """Generates simple bat sprites."""

    name = "bat"
    category = "creature"
    description = "Simple bat with spread wings"
    version = "1.0.0"
    author = "Bitsy Examples"
    tags = ["retro", "enemy", "flying"]

    def generate(self, width=16, height=12, seed=None, **kwargs):
        """Generate a bat sprite."""
        if seed is not None:
            random.seed(seed)

        canvas = Canvas(width, height)
        color = kwargs.get('color', (60, 40, 80, 255))
        eye_color = kwargs.get('eye_color', (255, 0, 0, 255))

        center_x = width // 2
        center_y = height // 2

        # Body (small oval)
        body_w = width // 4
        body_h = height // 3
        for y in range(height):
            for x in range(width):
                dx = (x - center_x) / body_w
                dy = (y - center_y) / body_h
                if dx * dx + dy * dy <= 1:
                    canvas.set_pixel(x, y, color)

        # Wings
        wing_span = width // 2 - 2
        wing_height = height // 3

        # Left wing
        for i in range(wing_span):
            wing_x = center_x - body_w - i
            wing_top = center_y - (i * wing_height // wing_span)
            wing_bottom = center_y + 1
            for y in range(wing_top, wing_bottom + 1):
                if 0 <= wing_x < width and 0 <= y < height:
                    canvas.set_pixel(wing_x, y, color)

        # Right wing
        for i in range(wing_span):
            wing_x = center_x + body_w + i
            wing_top = center_y - (i * wing_height // wing_span)
            wing_bottom = center_y + 1
            for y in range(wing_top, wing_bottom + 1):
                if 0 <= wing_x < width and 0 <= y < height:
                    canvas.set_pixel(wing_x, y, color)

        # Ears
        canvas.set_pixel(center_x - 1, center_y - body_h, color)
        canvas.set_pixel(center_x + 1, center_y - body_h, color)

        # Eyes
        canvas.set_pixel(center_x - 1, center_y, eye_color)
        canvas.set_pixel(center_x + 1, center_y, eye_color)

        return canvas

#!/usr/bin/env python3
"""Test the template-based portrait generator."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from generators.portrait_v2 import TemplatePortraitGenerator


def main():
    print("=" * 60)
    print("TEMPLATE PORTRAIT TEST")
    print("=" * 60)

    # Generate a test portrait
    generator = TemplatePortraitGenerator(
        style_path="templates/anime_standard",
        skin_color=(232, 190, 160),  # Light skin
        eye_color=(80, 60, 180),     # Purple eyes
        hair_color=(140, 100, 180),  # Purple hair
        clothing_color=(80, 70, 130),  # Purple/blue clothing
    )

    canvas = generator.render()

    # Save
    output_path = "output/test_template_portrait.png"
    canvas.save(output_path)

    print(f"Saved to: {output_path}")
    print(f"Canvas size: {canvas.width}x{canvas.height}")

    # Count colors
    colors = set()
    for y in range(canvas.height):
        for x in range(canvas.width):
            pixel = canvas.get_pixel(x, y)
            if pixel and pixel[3] > 0:
                colors.add(pixel)

    print(f"Total colors: {len(colors)}")
    print()
    print("View output/test_template_portrait.png")


if __name__ == "__main__":
    main()

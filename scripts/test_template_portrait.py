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

    # Generate a test portrait without glasses
    generator = TemplatePortraitGenerator(
        style_path="templates/anime_standard",
        skin_color=(232, 190, 160),  # Light skin
        eye_color=(80, 60, 180),     # Purple eyes
        hair_color=(140, 100, 180),  # Purple hair
        clothing_color=(80, 70, 130),  # Purple/blue clothing
    )

    canvas = generator.render()
    output_path = "output/test_template_portrait.png"
    canvas.save(output_path)
    print(f"Without glasses: {output_path}")

    # Generate a test portrait WITH glasses
    generator_glasses = TemplatePortraitGenerator(
        style_path="templates/anime_standard",
        skin_color=(232, 190, 160),
        eye_color=(80, 60, 180),
        hair_color=(140, 100, 180),
        clothing_color=(80, 70, 130),
        accessory_color=(80, 55, 40),  # Brown frames
        has_glasses=True,
        glasses_style="round",
    )

    canvas_glasses = generator_glasses.render()
    output_path_glasses = "output/test_template_portrait_glasses.png"
    canvas_glasses.save(output_path_glasses)
    print(f"With glasses: {output_path_glasses}")

    print(f"Canvas size: {canvas.width}x{canvas.height}")

    # Count colors
    colors = set()
    for y in range(canvas_glasses.height):
        for x in range(canvas_glasses.width):
            pixel = canvas_glasses.get_pixel(x, y)
            if pixel and pixel[3] > 0:
                colors.add(pixel)

    print(f"Total colors (with glasses): {len(colors)}")
    print()
    print("View output/test_template_portrait*.png")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Character Demo - Demonstrates Bitsy's character generation system.

Shows how to create characters with different:
- Hair styles and colors
- Eye types and expressions
- Body types
- Art styles
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Canvas, Style
from generators import CharacterGenerator, generate_character


def create_hair_showcase() -> Canvas:
    """Create a showcase of different hair styles."""
    hair_types = ['fluffy', 'spiky', 'long', 'short', 'ponytail', 'twintails']

    sprite_size = 32
    padding = 4
    cols = len(hair_types)

    canvas = Canvas(
        (sprite_size + padding) * cols + padding,
        sprite_size + padding * 2,
        (40, 40, 50, 255)
    )

    for i, hair_type in enumerate(hair_types):
        gen = CharacterGenerator(width=sprite_size, height=sprite_size, seed=42)
        gen.set_hair(hair_type, 'lavender')
        gen.set_eyes('large', 'blue')

        sprite = gen.render()
        x = padding + i * (sprite_size + padding)
        canvas.blit(sprite, x, padding)

    return canvas


def create_eye_showcase() -> Canvas:
    """Create a showcase of different eye types."""
    eye_types = ['simple', 'round', 'large', 'sparkle']
    eye_colors = ['blue', 'green', 'purple', 'gold']

    sprite_size = 32
    padding = 4
    cols = len(eye_types)
    rows = len(eye_colors)

    canvas = Canvas(
        (sprite_size + padding) * cols + padding,
        (sprite_size + padding) * rows + padding,
        (40, 40, 50, 255)
    )

    for row, color in enumerate(eye_colors):
        for col, eye_type in enumerate(eye_types):
            gen = CharacterGenerator(width=sprite_size, height=sprite_size, seed=42)
            gen.set_hair('fluffy', 'lavender')
            gen.set_eyes(eye_type, color)

            sprite = gen.render()
            x = padding + col * (sprite_size + padding)
            y = padding + row * (sprite_size + padding)
            canvas.blit(sprite, x, y)

    return canvas


def create_hair_color_showcase() -> Canvas:
    """Create a showcase of different hair colors."""
    colors = ['lavender', 'pink', 'blue', 'brown', 'blonde', 'red', 'black']

    sprite_size = 32
    padding = 4
    cols = len(colors)

    canvas = Canvas(
        (sprite_size + padding) * cols + padding,
        sprite_size + padding * 2,
        (40, 40, 50, 255)
    )

    for i, color in enumerate(colors):
        gen = CharacterGenerator(width=sprite_size, height=sprite_size, seed=42)
        gen.set_hair('fluffy', color)
        gen.set_eyes('large', 'blue')

        sprite = gen.render()
        x = padding + i * (sprite_size + padding)
        canvas.blit(sprite, x, padding)

    return canvas


def create_random_characters(count: int = 8) -> Canvas:
    """Create a grid of randomly generated characters."""
    sprite_size = 32
    padding = 4
    cols = 4
    rows = (count + cols - 1) // cols

    canvas = Canvas(
        (sprite_size + padding) * cols + padding,
        (sprite_size + padding) * rows + padding,
        (40, 40, 50, 255)
    )

    for i in range(count):
        gen = CharacterGenerator(width=sprite_size, height=sprite_size, seed=1000 + i)
        gen.randomize()

        sprite = gen.render()
        col = i % cols
        row = i // cols
        x = padding + col * (sprite_size + padding)
        y = padding + row * (sprite_size + padding)
        canvas.blit(sprite, x, y)

    return canvas


def create_expression_showcase() -> Canvas:
    """Create a showcase of different expressions."""
    expressions = ['neutral', 'happy', 'sad', 'angry']

    sprite_size = 32
    padding = 4
    cols = len(expressions)

    canvas = Canvas(
        (sprite_size + padding) * cols + padding,
        sprite_size + padding * 2,
        (40, 40, 50, 255)
    )

    for i, expression in enumerate(expressions):
        gen = CharacterGenerator(width=sprite_size, height=sprite_size, seed=42)
        gen.set_hair('fluffy', 'lavender')
        gen.set_eyes('large', 'blue', expression)

        sprite = gen.render()
        x = padding + i * (sprite_size + padding)
        canvas.blit(sprite, x, padding)

    return canvas


def create_size_comparison() -> Canvas:
    """Create characters at different sizes."""
    sizes = [16, 24, 32, 48, 64]

    padding = 4
    total_width = sum(sizes) + padding * (len(sizes) + 1)
    max_height = max(sizes) + padding * 2

    canvas = Canvas(total_width, max_height, (40, 40, 50, 255))

    x = padding
    for size in sizes:
        gen = CharacterGenerator(width=size, height=size, seed=42)
        gen.set_hair('fluffy', 'lavender')
        gen.set_eyes('large', 'blue')

        sprite = gen.render()
        y = padding + (max_height - padding * 2 - size) // 2  # Center vertically
        canvas.blit(sprite, x, y)
        x += size + padding

    return canvas


def main():
    print("Bitsy - Character Generation Demo")
    print("=" * 40)

    # Create output directory
    output_dir = os.path.join(os.path.dirname(__file__), "..", "output")
    os.makedirs(output_dir, exist_ok=True)

    # Hair styles
    print("\n1. Creating hair style showcase...")
    hair_showcase = create_hair_showcase()
    hair_showcase.save(os.path.join(output_dir, "hair_styles.png"))
    # Scale up for visibility
    hair_showcase.scale(2).save(os.path.join(output_dir, "hair_styles_2x.png"))
    print("   Saved: output/hair_styles.png")

    # Eye types
    print("\n2. Creating eye type showcase...")
    eye_showcase = create_eye_showcase()
    eye_showcase.save(os.path.join(output_dir, "eye_types.png"))
    eye_showcase.scale(2).save(os.path.join(output_dir, "eye_types_2x.png"))
    print("   Saved: output/eye_types.png")

    # Hair colors
    print("\n3. Creating hair color showcase...")
    color_showcase = create_hair_color_showcase()
    color_showcase.save(os.path.join(output_dir, "hair_colors.png"))
    color_showcase.scale(2).save(os.path.join(output_dir, "hair_colors_2x.png"))
    print("   Saved: output/hair_colors.png")

    # Random characters
    print("\n4. Creating random character grid...")
    random_chars = create_random_characters(16)
    random_chars.save(os.path.join(output_dir, "random_characters.png"))
    random_chars.scale(2).save(os.path.join(output_dir, "random_characters_2x.png"))
    print("   Saved: output/random_characters.png")

    # Expressions
    print("\n5. Creating expression showcase...")
    expressions = create_expression_showcase()
    expressions.save(os.path.join(output_dir, "expressions.png"))
    expressions.scale(2).save(os.path.join(output_dir, "expressions_2x.png"))
    print("   Saved: output/expressions.png")

    # Size comparison
    print("\n6. Creating size comparison...")
    sizes = create_size_comparison()
    sizes.save(os.path.join(output_dir, "size_comparison.png"))
    sizes.scale(2).save(os.path.join(output_dir, "size_comparison_2x.png"))
    print("   Saved: output/size_comparison.png")

    # Single high-res character
    print("\n7. Creating high-res character...")
    gen = CharacterGenerator(width=64, height=64, seed=42)
    gen.set_hair('fluffy', 'lavender')
    gen.set_eyes('sparkle', 'purple')
    gen.set_outfit('cloth_purple')

    sprite = gen.render()
    sprite.save(os.path.join(output_dir, "character_64.png"))
    sprite.scale(2).save(os.path.join(output_dir, "character_128.png"))
    print("   Saved: output/character_64.png, output/character_128.png")

    print("\n" + "=" * 40)
    print("Done! Check the output/ directory.")
    print("\nGenerated files:")
    print("  - hair_styles.png / hair_styles_2x.png")
    print("  - eye_types.png / eye_types_2x.png")
    print("  - hair_colors.png / hair_colors_2x.png")
    print("  - random_characters.png / random_characters_2x.png")
    print("  - expressions.png / expressions_2x.png")
    print("  - size_comparison.png / size_comparison_2x.png")
    print("  - character_64.png / character_128.png")


if __name__ == "__main__":
    main()

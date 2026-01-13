#!/usr/bin/env python3
"""
Hello Sprite - A simple example demonstrating Bitsy core features.

Creates a simple animated sprite and exports it as a sprite sheet.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.canvas import Canvas, hex_to_rgba
from core.palette import Palette
from core.animation import Animation


def create_simple_character(size: int = 32) -> Canvas:
    """Create a simple chibi character."""
    canvas = Canvas(size, size, (0, 0, 0, 0))

    # Get palettes
    skin = Palette.skin_warm()
    hair = Palette.hair_lavender()

    cx, cy = size // 2, size // 2

    # Body (simple blob)
    canvas.fill_ellipse(cx, cy + 6, 6, 8, hair.get(4))  # Robe

    # Head
    canvas.fill_circle(cx, cy - 2, 8, skin.get(2))

    # Hair (fluffy)
    canvas.fill_circle(cx, cy - 6, 10, hair.get(5))
    canvas.fill_circle(cx - 5, cy - 4, 6, hair.get(4))
    canvas.fill_circle(cx + 5, cy - 4, 6, hair.get(4))

    # Face hole (show skin through hair)
    canvas.fill_ellipse(cx, cy - 2, 6, 5, skin.get(2))

    # Eyes
    canvas.fill_circle(cx - 3, cy - 2, 2, (255, 255, 255, 255))
    canvas.fill_circle(cx + 3, cy - 2, 2, (255, 255, 255, 255))
    canvas.set_pixel(cx - 3, cy - 2, (40, 60, 80, 255))
    canvas.set_pixel(cx + 3, cy - 2, (40, 60, 80, 255))

    # Catchlights
    canvas.set_pixel(cx - 4, cy - 3, (255, 255, 255, 255))
    canvas.set_pixel(cx + 2, cy - 3, (255, 255, 255, 255))

    # Mouth
    canvas.set_pixel(cx, cy + 1, skin.get(4))

    # Highlight on hair
    canvas.set_pixel(cx - 3, cy - 10, hair.get(1))
    canvas.set_pixel(cx - 2, cy - 9, hair.get(2))

    return canvas


def create_idle_animation(base: Canvas, frames: int = 4) -> Animation:
    """Create a simple idle breathing animation."""
    anim = Animation("idle", fps=8)

    for i in range(frames):
        frame = base.copy()

        # Simple up/down bounce for breathing effect
        # In a real implementation, we'd modify the sprite

        anim.add_frame(frame, duration=2)

    return anim


def create_walk_cycle(base: Canvas, frames: int = 4) -> Animation:
    """Create a simple walk cycle."""
    anim = Animation("walk", fps=8)

    # For now, just duplicate frames
    # In a real implementation, we'd modify limb positions
    for i in range(frames):
        anim.add_frame(base.copy(), duration=1)

    return anim


def main():
    print("Bitsy - Hello Sprite Example")
    print("=" * 40)

    # Create output directory
    output_dir = os.path.join(os.path.dirname(__file__), "..", "output")
    os.makedirs(output_dir, exist_ok=True)

    # Create a simple character
    print("\n1. Creating character sprite...")
    sprite = create_simple_character(32)
    sprite.save(os.path.join(output_dir, "character_32.png"))
    print("   Saved: output/character_32.png")

    # Scale it up
    print("\n2. Scaling sprite...")
    sprite_64 = sprite.scale(2)
    sprite_64.save(os.path.join(output_dir, "character_64.png"))
    print("   Saved: output/character_64.png")

    sprite_128 = sprite.scale(4)
    sprite_128.save(os.path.join(output_dir, "character_128.png"))
    print("   Saved: output/character_128.png")

    # Create flipped version
    print("\n3. Creating flipped version...")
    flipped = sprite.flip_horizontal()
    flipped.save(os.path.join(output_dir, "character_flipped.png"))
    print("   Saved: output/character_flipped.png")

    # Create simple animation
    print("\n4. Creating idle animation...")
    idle = create_idle_animation(sprite, 4)
    idle.save_spritesheet(os.path.join(output_dir, "idle_sheet.png"))
    print("   Saved: output/idle_sheet.png")

    # Create walk cycle
    print("\n5. Creating walk cycle...")
    walk = create_walk_cycle(sprite, 4)
    walk.save_spritesheet(os.path.join(output_dir, "walk_sheet.png"))
    print("   Saved: output/walk_sheet.png")

    # Test palette
    print("\n6. Demonstrating palette system...")
    pal = Palette.hair_lavender()
    print(f"   Lavender hair palette: {len(pal)} colors")

    pal_shifted = pal.shift_all(hue_degrees=30)
    print(f"   Hue-shifted variant created")

    print("\n" + "=" * 40)
    print("Done! Check the output/ directory.")


if __name__ == "__main__":
    main()

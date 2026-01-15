#!/usr/bin/env python3
"""
Style Demo - Demonstrates Bitsy's style system and color operations.

Shows how different art styles affect rendering:
- Chibi (anime/cute)
- Retro NES (8-bit)
- Retro SNES (16-bit)
- Modern HD (high-res)
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import (
    Canvas,
    Style,
    Palette,
    hex_to_rgba,
    lerp_color,
    darken,
    lighten,
    blend_multiply,
    blend_screen,
    blend_overlay,
    dither_color,
    CHIBI,
    RETRO_NES,
    RETRO_SNES,
    MODERN_HD,
)


def draw_shaded_circle(canvas: Canvas, cx: int, cy: int, r: int,
                       base_color: tuple, style: Style) -> None:
    """Draw a circle with style-appropriate shading."""
    # Get shading colors from style
    colors = style.get_shading_colors(base_color, style.shading.levels)

    # Draw from back to front (shadow to highlight)
    for i, color in enumerate(reversed(colors)):
        # Each level is smaller and offset toward light
        level = len(colors) - 1 - i
        offset = level * 1  # Offset toward light source
        level_r = r - level * (r // len(colors))

        canvas.fill_circle(cx - offset, cy + offset, level_r, color)

    # Add outline if enabled
    if style.outline.enabled:
        outline_color = style.get_outline_color(base_color)
        canvas.draw_circle(cx, cy, r, outline_color)


def draw_shaded_rect(canvas: Canvas, x: int, y: int, w: int, h: int,
                     base_color: tuple, style: Style) -> None:
    """Draw a rectangle with style-appropriate shading."""
    colors = style.get_shading_colors(base_color, style.shading.levels)

    if style.shading.mode == 'flat':
        # Just fill with base color
        canvas.fill_rect(x, y, w, h, base_color)
    elif style.shading.mode == 'cel':
        # Horizontal bands
        band_h = h // len(colors)
        for i, color in enumerate(colors):
            canvas.fill_rect(x, y + i * band_h, w, band_h, color)
    elif style.shading.mode == 'gradient':
        # Smooth gradient
        canvas.gradient_vertical(x, y, w, h, colors[0], colors[-1])
    elif style.shading.mode == 'dither':
        # Dithered gradient
        for py in range(y, y + h):
            t = (py - y) / max(h - 1, 1)
            for px in range(x, x + w):
                color = dither_color(colors[0], colors[-1], px, py, t)
                canvas.set_pixel(px, py, color)

    # Outline
    if style.outline.enabled:
        outline_color = style.get_outline_color(base_color)
        canvas.draw_rect(x, y, w, h, outline_color)


def create_style_comparison(size: int = 64) -> Canvas:
    """Create a comparison of different styles side by side."""
    styles = [
        ('Chibi', Style.chibi()),
        ('NES', Style.retro_nes()),
        ('SNES', Style.retro_snes()),
        ('Modern', Style.modern_hd()),
    ]

    padding = 4
    canvas_width = (size + padding) * len(styles) + padding
    canvas_height = size * 2 + padding * 3

    canvas = Canvas(canvas_width, canvas_height, (40, 40, 50, 255))

    base_skin = hex_to_rgba('#f0c090')
    base_cloth = hex_to_rgba('#6080a0')

    for i, (name, style) in enumerate(styles):
        x = padding + i * (size + padding)

        # Draw a circle (head-like) with style shading
        draw_shaded_circle(
            canvas,
            x + size // 2,
            padding + size // 2,
            size // 3,
            base_skin,
            style
        )

        # Draw a rectangle (body-like) with style shading
        draw_shaded_rect(
            canvas,
            x + size // 4,
            size + padding * 2,
            size // 2,
            size - padding,
            base_cloth,
            style
        )

    return canvas


def create_palette_demo() -> Canvas:
    """Create a demo showing palette generation."""
    canvas = Canvas(256, 128, (30, 30, 40, 255))

    # Show different palette types
    palettes = [
        ('Skin Warm', Palette.skin_warm()),
        ('Hair Lavender', Palette.hair_lavender()),
        ('Cloth Blue', Palette.cloth_blue()),
        ('Metal Gold', Palette.metal_gold()),
    ]

    swatch_w = 16
    swatch_h = 24

    for row, (name, palette) in enumerate(palettes):
        y = row * (swatch_h + 8) + 8

        for i, color in enumerate(palette.colors):
            x = i * swatch_w + 8
            canvas.fill_rect(x, y, swatch_w - 2, swatch_h - 2, color)

    return canvas


def create_blend_mode_demo() -> Canvas:
    """Create a demo showing blend modes."""
    canvas = Canvas(200, 120, (60, 60, 70, 255))

    # Base circle
    base_color = hex_to_rgba('#4080c0')
    canvas.fill_circle(50, 60, 30, base_color)

    # Blend layer
    blend_color = hex_to_rgba('#ffa040')

    # Normal
    for y in range(35, 85):
        for x in range(60, 90):
            from core import blend_normal
            bg = canvas.get_pixel(x, y)
            if bg:
                canvas.set_pixel_solid(x, y, blend_normal(bg, (*blend_color[:3], 180)))

    # Multiply
    for y in range(35, 85):
        for x in range(95, 125):
            bg = canvas.get_pixel(x, y)
            if bg:
                canvas.set_pixel_solid(x, y, blend_multiply(bg, blend_color))

    # Screen
    for y in range(35, 85):
        for x in range(130, 160):
            bg = canvas.get_pixel(x, y)
            if bg:
                canvas.set_pixel_solid(x, y, blend_screen(bg, blend_color))

    # Overlay
    for y in range(35, 85):
        for x in range(165, 195):
            bg = canvas.get_pixel(x, y)
            if bg:
                canvas.set_pixel_solid(x, y, blend_overlay(bg, blend_color))

    return canvas


def create_dither_demo() -> Canvas:
    """Create a demo showing dithering patterns."""
    canvas = Canvas(160, 80, (40, 40, 50, 255))

    color1 = hex_to_rgba('#2040a0')
    color2 = hex_to_rgba('#a0c0ff')

    patterns = ['checker', 'bayer2x2', 'bayer4x4', 'bayer8x8']

    for i, pattern in enumerate(patterns):
        x_start = i * 40
        for y in range(80):
            t = y / 79.0
            for x in range(x_start, x_start + 38):
                color = dither_color(color1, color2, x, y, t, pattern)
                canvas.set_pixel(x, y, color)

    return canvas


def main():
    print("Bitsy - Style System Demo")
    print("=" * 40)

    # Create output directory
    output_dir = os.path.join(os.path.dirname(__file__), "..", "output")
    os.makedirs(output_dir, exist_ok=True)

    # Style comparison
    print("\n1. Creating style comparison...")
    comparison = create_style_comparison(64)
    comparison.save(os.path.join(output_dir, "style_comparison.png"))
    print("   Saved: output/style_comparison.png")

    # Palette demo
    print("\n2. Creating palette demo...")
    palette_demo = create_palette_demo()
    palette_demo.save(os.path.join(output_dir, "palette_demo.png"))
    print("   Saved: output/palette_demo.png")

    # Blend modes
    print("\n3. Creating blend mode demo...")
    blend_demo = create_blend_mode_demo()
    blend_demo.save(os.path.join(output_dir, "blend_modes.png"))
    print("   Saved: output/blend_modes.png")

    # Dithering
    print("\n4. Creating dither demo...")
    dither_demo = create_dither_demo()
    dither_demo.save(os.path.join(output_dir, "dither_patterns.png"))
    print("   Saved: output/dither_patterns.png")

    # Show style properties
    print("\n5. Style preset summary:")
    for name, style_cls in [
        ('Chibi', Style.chibi),
        ('NES', Style.retro_nes),
        ('SNES', Style.retro_snes),
        ('Modern HD', Style.modern_hd),
    ]:
        style = style_cls()
        print(f"\n   {name}:")
        print(f"     Outline: {style.outline.mode if style.outline.enabled else 'none'}")
        print(f"     Shading: {style.shading.mode}, {style.shading.levels} levels")
        if style.palette.per_sprite_colors:
            print(f"     Colors: {style.palette.per_sprite_colors} per sprite")

    print("\n" + "=" * 40)
    print("Done! Check the output/ directory.")


if __name__ == "__main__":
    main()

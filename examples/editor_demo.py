#!/usr/bin/env python3
"""
Editor Demo - Demonstrates Bitsy's editing and transformation tools.

Shows:
- Loading existing PNG files
- Layer compositing with blend modes
- Color adjustments
- Palette operations
- Geometric transforms
- Pixel effects (outline, shadow, glow)
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Canvas
from generators import generate_item, generate_character, CharacterConfig
from ui import create_icon, create_panel, render_text
from editor import (
    # Loader
    load_png,
    count_colors,
    has_transparency,
    get_bounding_box,
    trim_canvas,
    # Layers
    LayerStack,
    BlendMode,
    blend_canvases,
    list_blend_modes,
    # Transforms - Color
    adjust_brightness,
    adjust_contrast,
    adjust_saturation,
    adjust_hue,
    invert_colors,
    grayscale,
    sepia,
    posterize,
    # Transforms - Palette
    extract_palette,
    reduce_palette,
    replace_color,
    # Transforms - Geometric
    rotate_90,
    rotate_180,
    rotate_270,
    crop,
    pad,
    tile,
    # Transforms - Pixel
    outline,
    drop_shadow,
    glow,
    dither,
    # Batch
    create_variations,
    create_animation_strip,
)


def create_test_sprite() -> Canvas:
    """Create a test sprite for demonstrations."""
    # Generate a sword as our test sprite
    sprite = generate_item('sword', width=24, height=24)
    return sprite


def create_color_adjustments_demo() -> Canvas:
    """Demonstrate color adjustment transforms."""
    sprite = create_test_sprite()

    adjustments = [
        ("Original", sprite),
        ("Bright +0.3", adjust_brightness(sprite, 0.3)),
        ("Dark -0.3", adjust_brightness(sprite, -0.3)),
        ("High Contrast", adjust_contrast(sprite, 1.5)),
        ("Low Contrast", adjust_contrast(sprite, 0.5)),
        ("Saturated", adjust_saturation(sprite, 1.5)),
        ("Desaturated", adjust_saturation(sprite, 0.5)),
        ("Grayscale", grayscale(sprite)),
        ("Inverted", invert_colors(sprite)),
        ("Sepia", sepia(sprite)),
        ("Posterize 4", posterize(sprite, 4)),
        ("Hue +60", adjust_hue(sprite, 60)),
    ]

    cols = 4
    rows = 3
    cell_w = 40
    cell_h = 36
    padding = 4

    canvas = Canvas(
        cols * cell_w + padding,
        rows * cell_h + padding,
        (30, 30, 40, 255)
    )

    for idx, (name, img) in enumerate(adjustments):
        col = idx % cols
        row = idx // cols
        x = padding + col * cell_w
        y = padding + row * cell_h

        # Background
        for by in range(28):
            for bx in range(36):
                canvas.set_pixel(x + bx, y + by, (40, 40, 50, 255))

        # Sprite
        canvas.blit(img, x + 6, y + 2)

        # Label
        label = render_text(name[:10], color=(180, 180, 180, 255), font='tiny')
        canvas.blit(label, x + 2, y + 28)

    return canvas


def create_pixel_effects_demo() -> Canvas:
    """Demonstrate pixel-level effects."""
    sprite = create_test_sprite()

    effects = [
        ("Original", sprite),
        ("Outline Black", outline(sprite, (0, 0, 0, 255), 1)),
        ("Outline White", outline(sprite, (255, 255, 255, 255), 1)),
        ("Drop Shadow", drop_shadow(sprite, 2, 2, (0, 0, 0, 150))),
        ("Glow Yellow", glow(sprite, (255, 255, 100, 100), 2)),
        ("Glow Blue", glow(sprite, (100, 150, 255, 100), 3)),
        ("Dither 2", dither(sprite, 2)),
        ("Dither 4", dither(sprite, 4)),
    ]

    cols = 4
    rows = 2
    cell_w = 48
    cell_h = 44
    padding = 4

    canvas = Canvas(
        cols * cell_w + padding,
        rows * cell_h + padding,
        (30, 30, 40, 255)
    )

    for idx, (name, img) in enumerate(effects):
        col = idx % cols
        row = idx // cols
        x = padding + col * cell_w
        y = padding + row * cell_h

        # Background
        for by in range(36):
            for bx in range(44):
                canvas.set_pixel(x + bx, y + by, (40, 40, 50, 255))

        # Center sprite in cell
        ox = (44 - img.width) // 2
        oy = (32 - img.height) // 2
        canvas.blit(img, x + ox, y + oy)

        # Label
        label = render_text(name[:12], color=(180, 180, 180, 255), font='tiny')
        canvas.blit(label, x + 2, y + 36)

    return canvas


def create_geometric_transforms_demo() -> Canvas:
    """Demonstrate geometric transforms."""
    sprite = create_test_sprite()

    transforms = [
        ("Original", sprite),
        ("Rotate 90", rotate_90(sprite)),
        ("Rotate 180", rotate_180(sprite)),
        ("Rotate 270", rotate_270(sprite)),
        ("Flip H", sprite.flip_horizontal()),
        ("Flip V", sprite.flip_vertical()),
        ("Cropped", crop(sprite, 4, 4, 16, 16)),
        ("Padded", pad(sprite, 4, 4, 4, 4, (100, 50, 50, 255))),
    ]

    cols = 4
    rows = 2
    cell_w = 44
    cell_h = 40
    padding = 4

    canvas = Canvas(
        cols * cell_w + padding,
        rows * cell_h + padding,
        (30, 30, 40, 255)
    )

    for idx, (name, img) in enumerate(transforms):
        col = idx % cols
        row = idx // cols
        x = padding + col * cell_w
        y = padding + row * cell_h

        # Background
        for by in range(32):
            for bx in range(40):
                canvas.set_pixel(x + bx, y + by, (40, 40, 50, 255))

        # Center sprite
        ox = (40 - img.width) // 2
        oy = (28 - img.height) // 2
        canvas.blit(img, x + max(0, ox), y + max(0, oy))

        # Label
        label = render_text(name, color=(180, 180, 180, 255), font='tiny')
        canvas.blit(label, x + 2, y + 32)

    return canvas


def create_layer_blend_demo() -> Canvas:
    """Demonstrate layer blending modes."""
    # Create base layer (blue square)
    base = Canvas(32, 32, (60, 100, 180, 255))
    for y in range(8, 24):
        for x in range(8, 24):
            base.set_pixel(x, y, (80, 150, 220, 255))

    # Create overlay (red circle)
    overlay = Canvas(32, 32, (0, 0, 0, 0))
    cx, cy = 16, 16
    for y in range(32):
        for x in range(32):
            dist = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
            if dist < 10:
                overlay.set_pixel(x, y, (220, 80, 80, 200))

    modes = [
        BlendMode.NORMAL,
        BlendMode.MULTIPLY,
        BlendMode.SCREEN,
        BlendMode.OVERLAY,
        BlendMode.DARKEN,
        BlendMode.LIGHTEN,
        BlendMode.ADD,
        BlendMode.DIFFERENCE,
    ]

    cols = 4
    rows = 2
    cell_w = 44
    cell_h = 44
    padding = 4

    canvas = Canvas(
        cols * cell_w + padding,
        rows * cell_h + padding,
        (30, 30, 40, 255)
    )

    for idx, mode in enumerate(modes):
        col = idx % cols
        row = idx // cols
        x = padding + col * cell_w
        y = padding + row * cell_h

        # Blend layers
        result = blend_canvases(base, overlay, mode=mode, opacity=0.8)

        # Background
        for by in range(36):
            for bx in range(40):
                canvas.set_pixel(x + bx, y + by, (50, 50, 60, 255))

        canvas.blit(result, x + 4, y + 2)

        # Label
        label = render_text(mode.value[:10], color=(180, 180, 180, 255), font='tiny')
        canvas.blit(label, x + 2, y + 36)

    return canvas


def create_palette_operations_demo() -> Canvas:
    """Demonstrate palette operations."""
    # Create a colorful sprite
    sprite = Canvas(24, 24, (0, 0, 0, 0))

    # Draw rainbow gradient
    colors = [
        (255, 0, 0, 255),
        (255, 127, 0, 255),
        (255, 255, 0, 255),
        (0, 255, 0, 255),
        (0, 0, 255, 255),
        (139, 0, 255, 255),
    ]

    for y in range(24):
        for x in range(24):
            color_idx = (x * len(colors)) // 24
            sprite.set_pixel(x, y, colors[color_idx])

    operations = [
        ("Original", sprite, None),
        ("4 Colors", reduce_palette(sprite, 4), None),
        ("8 Colors", reduce_palette(sprite, 8), None),
        ("16 Colors", reduce_palette(sprite, 16), None),
    ]

    cols = 4
    cell_w = 40
    cell_h = 40
    padding = 4

    canvas = Canvas(
        cols * cell_w + padding,
        cell_h + padding,
        (30, 30, 40, 255)
    )

    for idx, (name, img, _) in enumerate(operations):
        x = padding + idx * cell_w
        y = padding

        # Background
        for by in range(32):
            for bx in range(36):
                canvas.set_pixel(x + bx, y + by, (40, 40, 50, 255))

        canvas.blit(img, x + 6, y + 4)

        # Color count
        num_colors = count_colors(img)
        count_text = f"{num_colors}c"

        label = render_text(name[:8], color=(180, 180, 180, 255), font='tiny')
        canvas.blit(label, x + 2, y + 32)

    return canvas


def create_hue_variations_demo() -> Canvas:
    """Create sprite color variations."""
    sprite = create_test_sprite()

    # Create variations with different hue shifts
    hue_shifts = [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330]
    variations = create_variations(sprite, hue_shifts)

    cols = 6
    rows = 2
    cell_w = 32
    cell_h = 32
    padding = 4

    canvas = Canvas(
        cols * cell_w + padding,
        rows * cell_h + padding,
        (30, 30, 40, 255)
    )

    for idx, img in enumerate(variations):
        col = idx % cols
        row = idx // cols
        x = padding + col * cell_w
        y = padding + row * cell_h

        # Background
        for by in range(28):
            for bx in range(28):
                canvas.set_pixel(x + bx, y + by, (40, 40, 50, 255))

        canvas.blit(img, x + 2, y + 2)

    return canvas


def create_layer_stack_demo() -> Canvas:
    """Demonstrate layer stack usage."""
    # Create a layer stack
    stack = LayerStack(64, 64, background=(40, 40, 50, 255))

    # Add background layer
    bg = Canvas(64, 64, (0, 0, 0, 0))
    for y in range(64):
        for x in range(64):
            if (x + y) % 8 < 4:
                bg.set_pixel(x, y, (50, 50, 60, 255))
            else:
                bg.set_pixel(x, y, (60, 60, 70, 255))

    stack.add_layer("background", bg)

    # Add sprite layer
    sprite = create_test_sprite()
    sprite_layer = stack.add_layer("sprite")
    sprite_layer.canvas.blit(sprite, 20, 20)

    # Add overlay layer with transparency
    overlay = Canvas(64, 64, (0, 0, 0, 0))
    for y in range(20, 44):
        for x in range(20, 44):
            overlay.set_pixel(x, y, (255, 200, 100, 80))

    overlay_layer = stack.add_layer("overlay", overlay)
    overlay_layer.blend_mode = BlendMode.ADD
    overlay_layer.opacity = 0.7

    # Flatten and return
    return stack.flatten()


def create_animation_strip_demo() -> Canvas:
    """Demonstrate animation strip creation."""
    sprite = create_test_sprite()

    # Create frames with different effects
    frames = [
        sprite,
        adjust_brightness(sprite, 0.1),
        adjust_brightness(sprite, 0.2),
        adjust_brightness(sprite, 0.1),
        sprite,
        adjust_brightness(sprite, -0.1),
        adjust_brightness(sprite, -0.2),
        adjust_brightness(sprite, -0.1),
    ]

    # Create horizontal strip
    strip = create_animation_strip(frames, horizontal=True)

    return strip


def create_load_save_roundtrip() -> Canvas:
    """Test loading and saving PNGs."""
    output_dir = os.path.join(os.path.dirname(__file__), "..", "output")

    # Create a sprite and save it
    sprite = create_test_sprite()
    sprite = outline(sprite, (0, 0, 0, 255))

    test_path = os.path.join(output_dir, "test_roundtrip.png")
    sprite.save(test_path)

    # Load it back
    try:
        loaded = load_png(test_path)
        print(f"   Loaded sprite: {loaded.width}x{loaded.height}")
        print(f"   Colors: {count_colors(loaded)}")
        print(f"   Has transparency: {has_transparency(loaded)}")

        bbox = get_bounding_box(loaded)
        if bbox:
            print(f"   Bounding box: {bbox}")

        return loaded
    except Exception as e:
        print(f"   Load failed: {e}")
        return sprite


def main():
    print("Bitsy - Editor System Demo")
    print("=" * 40)

    # Create output directory
    output_dir = os.path.join(os.path.dirname(__file__), "..", "output")
    os.makedirs(output_dir, exist_ok=True)

    # Color adjustments
    print("\n1. Creating color adjustments demo...")
    color_adj = create_color_adjustments_demo()
    color_adj.save(os.path.join(output_dir, "editor_color_adjust.png"))
    color_adj.scale(2).save(os.path.join(output_dir, "editor_color_adjust_2x.png"))
    print("   Saved: output/editor_color_adjust.png")

    # Pixel effects
    print("\n2. Creating pixel effects demo...")
    effects = create_pixel_effects_demo()
    effects.save(os.path.join(output_dir, "editor_effects.png"))
    effects.scale(2).save(os.path.join(output_dir, "editor_effects_2x.png"))
    print("   Saved: output/editor_effects.png")

    # Geometric transforms
    print("\n3. Creating geometric transforms demo...")
    transforms = create_geometric_transforms_demo()
    transforms.save(os.path.join(output_dir, "editor_transforms.png"))
    transforms.scale(2).save(os.path.join(output_dir, "editor_transforms_2x.png"))
    print("   Saved: output/editor_transforms.png")

    # Blend modes
    print("\n4. Creating layer blend modes demo...")
    blends = create_layer_blend_demo()
    blends.save(os.path.join(output_dir, "editor_blend_modes.png"))
    blends.scale(2).save(os.path.join(output_dir, "editor_blend_modes_2x.png"))
    print(f"   Available blend modes: {list_blend_modes()}")
    print("   Saved: output/editor_blend_modes.png")

    # Palette operations
    print("\n5. Creating palette operations demo...")
    palette_ops = create_palette_operations_demo()
    palette_ops.save(os.path.join(output_dir, "editor_palette.png"))
    palette_ops.scale(2).save(os.path.join(output_dir, "editor_palette_2x.png"))
    print("   Saved: output/editor_palette.png")

    # Hue variations
    print("\n6. Creating hue variations demo...")
    variations = create_hue_variations_demo()
    variations.save(os.path.join(output_dir, "editor_hue_variations.png"))
    variations.scale(2).save(os.path.join(output_dir, "editor_hue_variations_2x.png"))
    print("   Saved: output/editor_hue_variations.png")

    # Layer stack
    print("\n7. Creating layer stack demo...")
    layer_result = create_layer_stack_demo()
    layer_result.save(os.path.join(output_dir, "editor_layers.png"))
    layer_result.scale(2).save(os.path.join(output_dir, "editor_layers_2x.png"))
    print("   Saved: output/editor_layers.png")

    # Animation strip
    print("\n8. Creating animation strip demo...")
    strip = create_animation_strip_demo()
    strip.save(os.path.join(output_dir, "editor_anim_strip.png"))
    strip.scale(2).save(os.path.join(output_dir, "editor_anim_strip_2x.png"))
    print("   Saved: output/editor_anim_strip.png")

    # Load/save roundtrip
    print("\n9. Testing PNG load/save roundtrip...")
    loaded = create_load_save_roundtrip()
    print("   Roundtrip test complete!")

    # Summary
    print("\n" + "=" * 40)
    print("Editor System Summary:")
    print("  - PNG loading: Supports RGB, RGBA, Grayscale, Indexed")
    print(f"  - Blend modes: {len(list_blend_modes())} modes")
    print("  - Color adjustments: brightness, contrast, saturation, hue")
    print("  - Effects: invert, grayscale, sepia, posterize")
    print("  - Palette: extract, reduce, remap, replace colors")
    print("  - Geometry: rotate (90/180/270), flip, crop, pad, tile")
    print("  - Pixel: outline, drop shadow, glow, dither")
    print("  - Batch: variations, animation strips")

    print("\nAvailable blend modes:")
    for mode in list_blend_modes():
        print(f"    - {mode}")

    print("\n" + "=" * 40)
    print("Done! Check the output/ directory.")


if __name__ == "__main__":
    main()

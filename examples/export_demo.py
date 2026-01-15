#!/usr/bin/env python3
"""
Export Demo - Demonstrates Bitsy's export capabilities.

Shows:
- Animated GIF export
- Animated PNG (APNG) export
- Sprite sheet generation
- Atlas packing with metadata
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Canvas
from generators import generate_item, ItemPalette
from ui import create_icon, render_text
from editor import adjust_hue, adjust_brightness, outline
from export import (
    # GIF
    save_gif,
    GIFExporter,
    # APNG
    save_apng_simple,
    APNGExporter,
    # Spritesheet
    SpriteAtlas,
    pack_sprites,
    create_grid_sheet,
    create_animation_sheet,
    create_character_sheet,
    split_sheet,
    export_atlas_json,
)


def create_animation_frames() -> list:
    """Create simple animation frames for testing."""
    base = generate_item('sword', width=24, height=24)
    base = outline(base, (0, 0, 0, 255))

    frames = []

    # Create glowing animation
    for i in range(8):
        brightness = 0.1 * (1 + abs(4 - i) / 4)
        frame = adjust_brightness(base, brightness * 0.3)
        frames.append(frame)

    return frames


def create_color_cycling_frames() -> list:
    """Create color cycling animation frames."""
    base = create_icon('star', size=24)

    frames = []
    for hue_shift in range(0, 360, 30):
        frame = adjust_hue(base, hue_shift)
        frames.append(frame)

    return frames


def demo_gif_export():
    """Demonstrate GIF export."""
    print("\n1. Creating animated GIF...")

    output_dir = os.path.join(os.path.dirname(__file__), "..", "output")

    # Simple animation
    frames = create_animation_frames()
    delays = [8] * len(frames)  # 80ms per frame

    save_gif(
        os.path.join(output_dir, "animation.gif"),
        frames,
        delays=delays,
        loop=0
    )
    print(f"   Saved: output/animation.gif ({len(frames)} frames)")

    # Color cycling animation
    color_frames = create_color_cycling_frames()
    save_gif(
        os.path.join(output_dir, "color_cycle.gif"),
        color_frames,
        delays=[10] * len(color_frames),
        loop=0
    )
    print(f"   Saved: output/color_cycle.gif ({len(color_frames)} frames)")

    return len(frames) + len(color_frames)


def demo_apng_export():
    """Demonstrate APNG export."""
    print("\n2. Creating animated PNG (APNG)...")

    output_dir = os.path.join(os.path.dirname(__file__), "..", "output")

    # Same frames but as APNG (better quality)
    frames = create_animation_frames()

    save_apng_simple(
        os.path.join(output_dir, "animation.apng"),
        frames,
        fps=12,
        loop=0
    )
    print(f"   Saved: output/animation.apng ({len(frames)} frames, 12 fps)")

    # Higher quality color cycling
    color_frames = create_color_cycling_frames()
    save_apng_simple(
        os.path.join(output_dir, "color_cycle.apng"),
        color_frames,
        fps=10,
        loop=0
    )
    print(f"   Saved: output/color_cycle.apng ({len(color_frames)} frames)")

    return len(frames) + len(color_frames)


def demo_grid_sheet():
    """Demonstrate grid sprite sheet."""
    print("\n3. Creating grid sprite sheet...")

    output_dir = os.path.join(os.path.dirname(__file__), "..", "output")

    # Create various icons
    icons = []
    icon_names = ['heart', 'star', 'shield', 'sword', 'coin', 'potion',
                  'gear', 'home', 'arrow_right', 'arrow_left',
                  'checkmark', 'cross', 'plus', 'minus', 'search', 'refresh']

    for name in icon_names:
        icon = create_icon(name, size=16)
        icons.append(icon)

    # Create grid sheet
    sheet = create_grid_sheet(icons, columns=4, padding=2)
    sheet.save(os.path.join(output_dir, "icon_grid.png"))
    sheet.scale(2).save(os.path.join(output_dir, "icon_grid_2x.png"))

    print(f"   Saved: output/icon_grid.png ({len(icons)} icons, 4 columns)")

    return len(icons)


def demo_animation_sheet():
    """Demonstrate animation sprite sheet."""
    print("\n4. Creating animation sprite sheet...")

    output_dir = os.path.join(os.path.dirname(__file__), "..", "output")

    # Create multiple animations
    animations = {
        'idle': create_animation_frames()[:4],
        'glow': create_animation_frames()[4:],
        'spin': create_color_cycling_frames()[:6],
    }

    sheet, metadata = create_animation_sheet(animations, columns=8, padding=1)
    sheet.save(os.path.join(output_dir, "animation_sheet.png"))
    sheet.scale(2).save(os.path.join(output_dir, "animation_sheet_2x.png"))

    print(f"   Saved: output/animation_sheet.png")
    print(f"   Animations: {list(animations.keys())}")
    print(f"   Frame size: {metadata['frame_width']}x{metadata['frame_height']}")

    return sum(len(f) for f in animations.values())


def demo_atlas_packing():
    """Demonstrate sprite atlas packing."""
    print("\n5. Creating packed sprite atlas...")

    output_dir = os.path.join(os.path.dirname(__file__), "..", "output")

    # Create sprites of various sizes
    sprites = []

    # Items
    item_types = ['sword', 'axe', 'bow', 'staff', 'shield_round',
                  'potion_health', 'potion_mana', 'gem_red', 'gem_blue',
                  'key', 'coin', 'scroll']

    for item_type in item_types:
        sprite = generate_item(item_type, width=16, height=16)
        sprites.append((item_type, sprite))

    # Icons
    icon_names = ['heart', 'star', 'lightning', 'gear']
    for name in icon_names:
        icon = create_icon(name, size=12)
        sprites.append((f"icon_{name}", icon))

    # Pack into atlas
    atlas, packed = pack_sprites(sprites, max_width=128, max_height=128, padding=2)

    atlas.save(os.path.join(output_dir, "sprite_atlas.png"))
    atlas.scale(2).save(os.path.join(output_dir, "sprite_atlas_2x.png"))

    # Export metadata
    export_atlas_json(
        packed,
        atlas.width,
        atlas.height,
        os.path.join(output_dir, "sprite_atlas.json")
    )

    print(f"   Saved: output/sprite_atlas.png ({atlas.width}x{atlas.height})")
    print(f"   Saved: output/sprite_atlas.json")
    print(f"   Packed {len(sprites)} sprites")

    return len(sprites)


def demo_sprite_atlas_class():
    """Demonstrate SpriteAtlas class usage."""
    print("\n6. Creating atlas with SpriteAtlas class...")

    output_dir = os.path.join(os.path.dirname(__file__), "..", "output")

    # Use the high-level SpriteAtlas class
    atlas = SpriteAtlas(max_width=256, max_height=256, padding=2)

    # Add items with different palettes
    palettes = [
        ('iron', ItemPalette.iron()),
        ('gold', ItemPalette.gold()),
        ('magic', ItemPalette.magic()),
    ]

    from generators import ItemGenerator

    for palette_name, palette in palettes:
        gen = ItemGenerator(20, 20)
        gen.set_palette(palette)

        atlas.add(f"sword_{palette_name}", gen.generate_sword())
        atlas.add(f"shield_{palette_name}", gen.generate_shield('round'))

    # Add some icons
    for name in ['heart', 'star', 'coin']:
        atlas.add(f"icon_{name}", create_icon(name, size=16))

    # Build and save
    atlas.save(
        os.path.join(output_dir, "game_atlas.png"),
        os.path.join(output_dir, "game_atlas.json")
    )

    result, packed = atlas.build()
    print(f"   Saved: output/game_atlas.png ({result.width}x{result.height})")
    print(f"   Saved: output/game_atlas.json")
    print(f"   Total sprites: {len(packed)}")

    return len(packed)


def demo_split_sheet():
    """Demonstrate splitting a sprite sheet."""
    print("\n7. Demonstrating sheet splitting...")

    output_dir = os.path.join(os.path.dirname(__file__), "..", "output")

    # Create a sheet first
    frames = create_animation_frames()
    sheet = create_grid_sheet(frames, columns=4, padding=0)

    # Save the sheet
    sheet.save(os.path.join(output_dir, "to_split.png"))

    # Split it back into frames
    recovered_frames = split_sheet(sheet, 24, 24, count=len(frames))

    print(f"   Created sheet: {sheet.width}x{sheet.height}")
    print(f"   Split into: {len(recovered_frames)} frames of 24x24")

    # Verify by saving first recovered frame
    if recovered_frames:
        recovered_frames[0].scale(4).save(
            os.path.join(output_dir, "split_frame_0.png")
        )
        print(f"   Saved: output/split_frame_0.png (first recovered frame)")

    return len(recovered_frames)


def main():
    print("Bitsy - Export System Demo")
    print("=" * 40)

    # Create output directory
    output_dir = os.path.join(os.path.dirname(__file__), "..", "output")
    os.makedirs(output_dir, exist_ok=True)

    total_items = 0

    # GIF export
    total_items += demo_gif_export()

    # APNG export
    total_items += demo_apng_export()

    # Grid sheet
    total_items += demo_grid_sheet()

    # Animation sheet
    total_items += demo_animation_sheet()

    # Atlas packing
    total_items += demo_atlas_packing()

    # SpriteAtlas class
    total_items += demo_sprite_atlas_class()

    # Sheet splitting
    total_items += demo_split_sheet()

    # Summary
    print("\n" + "=" * 40)
    print("Export System Summary:")
    print("  - GIF export: Animated GIF with palette quantization")
    print("  - APNG export: Full RGBA animated PNG")
    print("  - Grid sheets: Simple uniform grid layout")
    print("  - Animation sheets: Multi-animation with metadata")
    print("  - Atlas packing: Bin-packed sprite atlas")
    print("  - JSON metadata: Sprite positions and dimensions")
    print(f"\n  Total items processed: {total_items}")

    print("\nOutput files generated:")
    for f in sorted(os.listdir(output_dir)):
        if f.startswith(('animation', 'color_cycle', 'icon_grid',
                        'animation_sheet', 'sprite_atlas', 'game_atlas',
                        'to_split', 'split_frame')):
            path = os.path.join(output_dir, f)
            size = os.path.getsize(path)
            print(f"    - {f} ({size:,} bytes)")

    print("\n" + "=" * 40)
    print("Done! Check the output/ directory.")
    print("\nNote: GIF and APNG files can be viewed in a web browser")
    print("or image viewer that supports animated images.")


if __name__ == "__main__":
    main()

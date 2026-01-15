#!/usr/bin/env python3
"""
UI Demo - Demonstrates Bitsy's UI generation system.

Shows:
- 9-patch panels with various presets
- Icon generation
- Text rendering with pixel fonts
- Progress bars
- Item generation
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Canvas
from ui import (
    # Panels
    create_panel,
    list_panel_presets,
    NinePatch,
    NinePatchConfig,
    PanelPresets,
    FrameGenerator,
    # Progress bars
    ProgressBar,
    HealthBar,
    ManaBar,
    # Icons
    create_icon,
    list_icons,
    create_icon_sheet,
    IconGenerator,
    IconPalette,
    # Fonts
    render_text,
    measure_text,
    Fonts,
    Label,
    TextBox,
    TextAlign,
    VerticalAlign,
)
from generators import (
    generate_item,
    list_item_types,
    ItemGenerator,
    ItemPalette,
)


def create_panel_showcase() -> Canvas:
    """Create a showcase of all panel presets."""
    presets = list_panel_presets()
    panel_width = 80
    panel_height = 60
    padding = 8
    cols = 3
    rows = (len(presets) + cols - 1) // cols

    width = cols * (panel_width + padding) + padding
    height = rows * (panel_height + padding + 12) + padding

    canvas = Canvas(width, height, (40, 40, 50, 255))

    for idx, preset_name in enumerate(presets):
        col = idx % cols
        row = idx // cols
        x = padding + col * (panel_width + padding)
        y = padding + row * (panel_height + padding + 12)

        # Create panel
        panel = create_panel(panel_width, panel_height, preset=preset_name)
        canvas.blit(panel, x, y)

        # Add label
        label = render_text(preset_name[:12], color=(200, 200, 200, 255), font='tiny')
        canvas.blit(label, x, y + panel_height + 2)

    return canvas


def create_icon_showcase() -> Canvas:
    """Create a showcase of available icons."""
    # Get a subset of unique icons
    icon_names = [
        'arrow_right', 'arrow_left', 'arrow_up', 'arrow_down',
        'checkmark', 'cross', 'plus', 'minus',
        'gear', 'menu', 'search', 'home',
        'heart', 'star', 'shield', 'lightning',
        'sword', 'potion', 'coin', 'refresh',
    ]

    icon_size = 16
    padding = 4
    cols = 5
    rows = 4

    width = cols * (icon_size + padding) + padding
    height = rows * (icon_size + padding) + padding

    canvas = Canvas(width, height, (30, 30, 40, 255))

    for idx, name in enumerate(icon_names):
        if idx >= cols * rows:
            break
        col = idx % cols
        row = idx // cols
        x = padding + col * (icon_size + padding)
        y = padding + row * (icon_size + padding)

        icon = create_icon(name, size=icon_size)
        canvas.blit(icon, x, y)

    return canvas


def create_colored_icons_demo() -> Canvas:
    """Demonstrate icons with different color palettes."""
    palettes = [
        ('Default', IconPalette.default()),
        ('Dark', IconPalette.dark()),
        ('Gold', IconPalette.gold()),
        ('Green', IconPalette.green()),
        ('Red', IconPalette.red()),
        ('Blue', IconPalette.blue()),
    ]

    icon_size = 16
    padding = 4
    icons_per_row = 4
    icon_names = ['heart', 'star', 'sword', 'shield']

    width = icons_per_row * (icon_size + padding) + padding + 50
    height = len(palettes) * (icon_size + padding) + padding

    canvas = Canvas(width, height, (30, 30, 40, 255))

    for row_idx, (name, palette) in enumerate(palettes):
        y = padding + row_idx * (icon_size + padding)

        # Label
        label = render_text(name, color=(180, 180, 180, 255), font='tiny')
        canvas.blit(label, padding, y + 4)

        # Icons
        gen = IconGenerator(icon_size, palette)
        for col_idx, icon_name in enumerate(icon_names):
            x = 50 + col_idx * (icon_size + padding)

            if icon_name == 'heart':
                icon = gen.heart()
            elif icon_name == 'star':
                icon = gen.star()
            elif icon_name == 'sword':
                icon = gen.sword()
            elif icon_name == 'shield':
                icon = gen.shield()
            else:
                icon = create_icon(icon_name, size=icon_size, palette=palette)

            canvas.blit(icon, x, y)

    return canvas


def create_text_demo() -> Canvas:
    """Demonstrate text rendering."""
    width = 200
    height = 120
    canvas = Canvas(width, height, (30, 30, 40, 255))

    y = 8

    # Title with shadow
    title = render_text("Bitsy Text Demo", color=(255, 220, 100, 255),
                        font='small', shadow=True)
    canvas.blit(title, 8, y)
    y += 16

    # Regular text
    regular = render_text("Regular text in white", color=(255, 255, 255, 255),
                          font='small')
    canvas.blit(regular, 8, y)
    y += 12

    # Colored text
    red = render_text("Red text", color=(255, 100, 100, 255), font='small')
    canvas.blit(red, 8, y)

    green = render_text("Green", color=(100, 255, 100, 255), font='small')
    canvas.blit(green, 60, y)

    blue = render_text("Blue", color=(100, 150, 255, 255), font='small')
    canvas.blit(blue, 110, y)
    y += 12

    # Outlined text
    outlined = render_text("Outlined text", color=(255, 255, 255, 255),
                           font='small', outline=True)
    canvas.blit(outlined, 8, y)
    y += 14

    # Tiny font
    tiny = render_text("TINY 3X5 FONT", color=(180, 180, 200, 255), font='tiny')
    canvas.blit(tiny, 8, y)
    y += 10

    # Small font lowercase
    lowercase = render_text("lowercase text works too!", color=(200, 200, 200, 255),
                            font='small')
    canvas.blit(lowercase, 8, y)
    y += 12

    # Numbers
    numbers = render_text("Score: 12345 HP: 100/100", color=(255, 200, 100, 255),
                          font='small')
    canvas.blit(numbers, 8, y)

    return canvas


def create_progress_bars_demo() -> Canvas:
    """Demonstrate progress bar rendering."""
    width = 150
    height = 80
    canvas = Canvas(width, height, (30, 30, 40, 255))

    bar_width = 100
    bar_height = 8
    padding = 10
    y = padding

    # Health bars at different levels
    health_bar = HealthBar(bar_width, bar_height)

    label = render_text("HP (Full)", color=(200, 200, 200, 255), font='tiny')
    canvas.blit(label, padding, y)
    bar = health_bar.render(1.0)
    canvas.blit(bar, padding + 40, y)
    y += 12

    label = render_text("HP (Med)", color=(200, 200, 200, 255), font='tiny')
    canvas.blit(label, padding, y)
    bar = health_bar.render(0.5)
    canvas.blit(bar, padding + 40, y)
    y += 12

    label = render_text("HP (Low)", color=(200, 200, 200, 255), font='tiny')
    canvas.blit(label, padding, y)
    bar = health_bar.render(0.2)
    canvas.blit(bar, padding + 40, y)
    y += 15

    # Mana bar
    mana_bar = ManaBar(bar_width, bar_height)
    label = render_text("MP", color=(200, 200, 200, 255), font='tiny')
    canvas.blit(label, padding, y)
    bar = mana_bar.render(0.7)
    canvas.blit(bar, padding + 40, y)
    y += 15

    # Custom progress bar
    custom = ProgressBar(bar_width, bar_height,
                         bg_color=(30, 30, 30, 255),
                         fill_color=(200, 150, 50, 255),
                         border_color=(100, 80, 30, 255))
    label = render_text("EXP", color=(200, 200, 200, 255), font='tiny')
    canvas.blit(label, padding, y)
    bar = custom.render(0.35)
    canvas.blit(bar, padding + 40, y)

    return canvas


def create_item_showcase() -> Canvas:
    """Create a showcase of generated items."""
    items = list_item_types()
    item_size = 16
    padding = 4
    cols = 7
    rows = (len(items) + cols - 1) // cols

    width = cols * (item_size + padding) + padding
    height = rows * (item_size + padding) + padding

    canvas = Canvas(width, height, (40, 40, 50, 255))

    for idx, item_name in enumerate(items):
        col = idx % cols
        row = idx // cols
        x = padding + col * (item_size + padding)
        y = padding + row * (item_size + padding)

        # Draw background slot
        for by in range(item_size):
            for bx in range(item_size):
                canvas.set_pixel(x + bx, y + by, (50, 50, 60, 255))

        # Generate item
        item = generate_item(item_name, width=item_size - 2, height=item_size - 2)
        canvas.blit(item, x + 1, y + 1)

    return canvas


def create_item_variations_demo() -> Canvas:
    """Show item variations with different palettes."""
    item_size = 24
    padding = 6

    palettes = [
        ('Iron', ItemPalette.iron()),
        ('Gold', ItemPalette.gold()),
        ('Magic', ItemPalette.magic()),
        ('Fire', ItemPalette.fire()),
        ('Ice', ItemPalette.ice()),
    ]

    items = ['sword', 'shield_round', 'axe', 'staff']

    width = len(items) * (item_size + padding) + padding + 50
    height = len(palettes) * (item_size + padding) + padding

    canvas = Canvas(width, height, (30, 30, 40, 255))

    for row_idx, (name, palette) in enumerate(palettes):
        y = padding + row_idx * (item_size + padding)

        # Label
        label = render_text(name, color=(180, 180, 180, 255), font='tiny')
        canvas.blit(label, padding, y + 8)

        # Items
        gen = ItemGenerator(item_size, item_size)
        gen.set_palette(palette)

        for col_idx, item_type in enumerate(items):
            x = 50 + col_idx * (item_size + padding)

            # Background slot
            for by in range(item_size):
                for bx in range(item_size):
                    canvas.set_pixel(x + bx, y + by, (40, 40, 50, 255))

            # Generate item
            if item_type == 'sword':
                item = gen.generate_sword()
            elif item_type == 'shield_round':
                item = gen.generate_shield('round')
            elif item_type == 'axe':
                item = gen.generate_axe()
            elif item_type == 'staff':
                item = gen.generate_staff()
            else:
                item = gen.generate_key()

            canvas.blit(item, x + 2, y + 2)

    return canvas


def create_dialog_box_demo() -> Canvas:
    """Create a sample dialog box with text."""
    # Create panel
    panel = create_panel(180, 80, preset='dialog')

    # Add text
    text = render_text("Welcome, brave hero!\n\nYour quest begins\nhere...",
                       color=(40, 40, 50, 255), font='small')
    panel.blit(text, 12, 10)

    return panel


def create_inventory_demo() -> Canvas:
    """Create a sample inventory panel."""
    # Create main panel
    panel = create_panel(160, 130, preset='fantasy_wood')

    # Title
    title = render_text("Inventory", color=(255, 220, 150, 255),
                        font='small', shadow=True)
    panel.blit(title, 12, 8)

    # Item slots (3x2 grid)
    slot_size = 24
    slot_padding = 4
    start_x = 12
    start_y = 24

    items = ['sword', 'shield_round', 'potion_health',
             'key', 'gem_blue', 'coin']

    for idx, item_name in enumerate(items):
        col = idx % 3
        row = idx // 3
        x = start_x + col * (slot_size + slot_padding)
        y = start_y + row * (slot_size + slot_padding)

        # Draw slot background
        for sy in range(slot_size):
            for sx in range(slot_size):
                panel.set_pixel(x + sx, y + sy, (80, 60, 40, 255))

        # Border
        for i in range(slot_size):
            panel.set_pixel(x + i, y, (60, 45, 30, 255))
            panel.set_pixel(x + i, y + slot_size - 1, (60, 45, 30, 255))
            panel.set_pixel(x, y + i, (60, 45, 30, 255))
            panel.set_pixel(x + slot_size - 1, y + i, (60, 45, 30, 255))

        # Generate and place item
        item = generate_item(item_name, width=slot_size - 6, height=slot_size - 6)
        panel.blit(item, x + 3, y + 3)

    # Stats section
    stats_y = start_y + 2 * (slot_size + slot_padding) + 8

    # Gold display
    coin_icon = create_icon('coin', size=12)
    panel.blit(coin_icon, 12, stats_y)
    gold_text = render_text("1,234", color=(255, 220, 100, 255), font='small')
    panel.blit(gold_text, 26, stats_y + 2)

    # Health display
    heart_icon = create_icon('heart', size=12)
    panel.blit(heart_icon, 70, stats_y)
    hp_text = render_text("85/100", color=(255, 100, 100, 255), font='small')
    panel.blit(hp_text, 84, stats_y + 2)

    return panel


def create_complete_ui_demo() -> Canvas:
    """Create a complete UI mockup."""
    width = 320
    height = 240
    canvas = Canvas(width, height, (25, 25, 35, 255))

    # Top bar with stats
    top_bar = create_panel(300, 24, preset='modern_dark')

    # Health bar
    health = HealthBar(60, 10)
    top_bar.blit(health.render(0.75), 8, 7)

    # Mana bar
    mana = ManaBar(60, 10)
    top_bar.blit(mana.render(0.9), 78, 7)

    # Gold
    coin = create_icon('coin', size=12)
    top_bar.blit(coin, 150, 6)
    gold = render_text("5,000", color=(255, 220, 100, 255), font='tiny')
    top_bar.blit(gold, 165, 8)

    # Level
    star = create_icon('star', size=12)
    top_bar.blit(star, 210, 6)
    level = render_text("Lv.15", color=(255, 255, 255, 255), font='tiny')
    top_bar.blit(level, 225, 8)

    canvas.blit(top_bar, 10, 8)

    # Action bar at bottom
    action_bar = create_panel(200, 36, preset='fantasy_stone')

    action_icons = ['sword', 'shield', 'potion', 'lightning']
    for idx, icon_name in enumerate(action_icons):
        icon = create_icon(icon_name, size=20)
        x = 12 + idx * 44

        # Slot background
        for y in range(28):
            for sx in range(28):
                action_bar.set_pixel(x - 2 + sx, 4 + y, (60, 60, 70, 255))

        action_bar.blit(icon, x + 2, 8)

        # Key hint
        key = render_text(str(idx + 1), color=(200, 200, 200, 255), font='tiny')
        action_bar.blit(key, x + 8, 26)

    canvas.blit(action_bar, 60, height - 44)

    # Mini dialog
    dialog = create_panel(140, 50, preset='tooltip')
    npc_text = render_text("Greetings!\nNeed supplies?", color=(50, 50, 60, 255), font='tiny')
    dialog.blit(npc_text, 8, 8)
    canvas.blit(dialog, 170, 70)

    return canvas


def main():
    print("Bitsy - UI System Demo")
    print("=" * 40)

    # Create output directory
    output_dir = os.path.join(os.path.dirname(__file__), "..", "output")
    os.makedirs(output_dir, exist_ok=True)

    # Panel showcase
    print("\n1. Creating panel showcase...")
    panels = create_panel_showcase()
    panels.save(os.path.join(output_dir, "panels.png"))
    panels.scale(2).save(os.path.join(output_dir, "panels_2x.png"))
    print(f"   Available presets: {list_panel_presets()}")
    print("   Saved: output/panels.png")

    # Icon showcase
    print("\n2. Creating icon showcase...")
    icons = create_icon_showcase()
    icons.save(os.path.join(output_dir, "icons.png"))
    icons.scale(2).save(os.path.join(output_dir, "icons_2x.png"))
    print(f"   Available icons: {len(list_icons())} total")
    print("   Saved: output/icons.png")

    # Colored icons
    print("\n3. Creating colored icons demo...")
    colored_icons = create_colored_icons_demo()
    colored_icons.save(os.path.join(output_dir, "icons_colored.png"))
    colored_icons.scale(2).save(os.path.join(output_dir, "icons_colored_2x.png"))
    print("   Saved: output/icons_colored.png")

    # Text demo
    print("\n4. Creating text rendering demo...")
    text_demo = create_text_demo()
    text_demo.save(os.path.join(output_dir, "text_demo.png"))
    text_demo.scale(2).save(os.path.join(output_dir, "text_demo_2x.png"))
    print("   Fonts: tiny (3x5), small (4x6)")
    print("   Saved: output/text_demo.png")

    # Progress bars
    print("\n5. Creating progress bars demo...")
    bars = create_progress_bars_demo()
    bars.save(os.path.join(output_dir, "progress_bars.png"))
    bars.scale(2).save(os.path.join(output_dir, "progress_bars_2x.png"))
    print("   Saved: output/progress_bars.png")

    # Item showcase
    print("\n6. Creating item showcase...")
    items = create_item_showcase()
    items.save(os.path.join(output_dir, "items.png"))
    items.scale(2).save(os.path.join(output_dir, "items_2x.png"))
    print(f"   Available items: {list_item_types()}")
    print("   Saved: output/items.png")

    # Item variations
    print("\n7. Creating item variations demo...")
    variations = create_item_variations_demo()
    variations.save(os.path.join(output_dir, "items_variations.png"))
    variations.scale(2).save(os.path.join(output_dir, "items_variations_2x.png"))
    print("   Saved: output/items_variations.png")

    # Dialog box
    print("\n8. Creating dialog box demo...")
    dialog = create_dialog_box_demo()
    dialog.save(os.path.join(output_dir, "dialog_box.png"))
    dialog.scale(2).save(os.path.join(output_dir, "dialog_box_2x.png"))
    print("   Saved: output/dialog_box.png")

    # Inventory panel
    print("\n9. Creating inventory panel demo...")
    inventory = create_inventory_demo()
    inventory.save(os.path.join(output_dir, "inventory.png"))
    inventory.scale(2).save(os.path.join(output_dir, "inventory_2x.png"))
    print("   Saved: output/inventory.png")

    # Complete UI mockup
    print("\n10. Creating complete UI mockup...")
    complete_ui = create_complete_ui_demo()
    complete_ui.save(os.path.join(output_dir, "ui_mockup.png"))
    complete_ui.scale(2).save(os.path.join(output_dir, "ui_mockup_2x.png"))
    print("   Saved: output/ui_mockup.png")

    # Icon sprite sheet
    print("\n11. Creating icon sprite sheet...")
    icon_sheet = create_icon_sheet(size=16, columns=8)
    icon_sheet.save(os.path.join(output_dir, "icon_sheet.png"))
    icon_sheet.scale(2).save(os.path.join(output_dir, "icon_sheet_2x.png"))
    print("   Saved: output/icon_sheet.png")

    # Summary
    print("\n" + "=" * 40)
    print("UI System Summary:")
    print(f"  - Panel presets: {len(list_panel_presets())}")
    print(f"  - Icon types: {len(list_icons())}")
    print(f"  - Item types: {len(list_item_types())}")
    print("  - Fonts: tiny (3x5), small (4x6)")
    print("  - Progress bars: HealthBar, ManaBar, ProgressBar")

    print("\nAll available icons:")
    for icon in sorted(set(list_icons())):
        print(f"    - {icon}")

    print("\nAll available items:")
    for item in sorted(list_item_types()):
        print(f"    - {item}")

    print("\n" + "=" * 40)
    print("Done! Check the output/ directory.")


if __name__ == "__main__":
    main()

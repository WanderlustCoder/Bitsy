# Indoor Environments Recipe

How to draw interior backgrounds in pixel art.

## General Principles

1. **Depth layers**: Background elements should be less detailed
2. **Lighting**: Consistent light source (usually window or lamp)
3. **Perspective**: Slight angle adds depth without complexity
4. **Color palette**: Interiors often use warm, muted tones

## Color Palettes

```python
INDOOR_PALETTES = {
    'cozy': {
        'wall': [(90, 75, 65), (110, 95, 80), (130, 115, 100)],
        'floor': [(70, 55, 45), (90, 75, 60), (110, 95, 80)],
        'wood': [(80, 55, 40), (120, 90, 65), (160, 130, 100)],
        'accent': (180, 140, 80),  # Warm yellow/gold
    },
    'library': {
        'wall': [(60, 50, 55), (80, 70, 75), (100, 90, 95)],
        'floor': [(50, 40, 35), (70, 60, 50), (90, 80, 70)],
        'wood': [(60, 40, 30), (100, 75, 55), (140, 115, 90)],
        'accent': (200, 170, 100),  # Candlelight
    },
    'castle': {
        'wall': [(80, 80, 90), (100, 100, 110), (120, 120, 130)],
        'floor': [(60, 60, 70), (80, 80, 90), (100, 100, 110)],
        'stone': [(70, 70, 80), (90, 90, 100), (110, 110, 120)],
        'accent': (180, 160, 120),  # Torch light
    },
    'tavern': {
        'wall': [(70, 55, 45), (100, 80, 65), (130, 110, 90)],
        'floor': [(50, 40, 30), (80, 65, 50), (110, 95, 75)],
        'wood': [(60, 45, 35), (100, 80, 60), (145, 120, 95)],
        'accent': (220, 180, 100),  # Firelight
    },
    'modern': {
        'wall': [(220, 220, 225), (235, 235, 240), (250, 250, 252)],
        'floor': [(180, 175, 170), (200, 195, 190), (220, 215, 210)],
        'accent': (100, 150, 200),  # Blue accent
    },
    'dark': {
        'wall': [(30, 28, 35), (45, 42, 50), (60, 56, 65)],
        'floor': [(20, 18, 25), (35, 32, 40), (50, 46, 55)],
        'accent': (120, 80, 160),  # Purple magic glow
    },
}
```

## Library / Study

```python
def draw_library_bg(canvas, width, height, style='cozy'):
    """Draw a library background."""
    palette = INDOOR_PALETTES.get(style, INDOOR_PALETTES['library'])

    # Floor (bottom third)
    floor_y = height * 2 // 3
    for y in range(floor_y, height):
        # Gradient darker toward bottom
        t = (y - floor_y) / (height - floor_y)
        idx = min(2, int(t * 3))
        color = palette['floor'][idx]
        canvas.draw_line(0, y, width - 1, y, color)

    # Wall (upper two-thirds)
    for y in range(floor_y):
        # Gradient lighter toward top
        t = y / floor_y
        idx = min(2, int(t * 3))
        color = palette['wall'][2 - idx]  # Reverse for lighter at top
        canvas.draw_line(0, y, width - 1, y, color)

    # Bookshelf silhouettes (background)
    shelf_color = palette['wood'][0]  # Dark wood
    book_colors = [
        (80, 50, 50),   # Red-brown
        (50, 60, 80),   # Blue-gray
        (60, 70, 50),   # Green-brown
        (90, 70, 60),   # Tan
    ]

    # Left bookshelf
    shelf_x = width // 10
    shelf_width = width // 4
    shelf_height = floor_y - 10

    canvas.fill_rect(shelf_x, 10, shelf_width, shelf_height, shelf_color)

    # Books on shelf (vertical lines)
    for i in range(shelf_width // 3):
        bx = shelf_x + 2 + i * 3
        if bx < shelf_x + shelf_width - 2:
            book_h = shelf_height - 4 - (i % 3) * 2
            book_color = book_colors[i % len(book_colors)]
            canvas.fill_rect(bx, 10 + shelf_height - book_h - 2, 2, book_h, book_color)

    # Right bookshelf (smaller, more distant)
    shelf_x2 = width - width // 3
    shelf_width2 = width // 5
    shelf_height2 = floor_y - 20

    canvas.fill_rect(shelf_x2, 20, shelf_width2, shelf_height2, palette['wood'][1])

    # Window (if space)
    if width >= 64:
        win_x = width // 2 - 8
        win_width = 16
        win_height = 24

        # Window frame
        canvas.fill_rect(win_x - 1, floor_y // 4, win_width + 2, win_height + 2, palette['wood'][1])
        # Window pane (light)
        canvas.fill_rect(win_x, floor_y // 4 + 1, win_width, win_height, (180, 200, 220))
        # Cross frame
        canvas.draw_line(win_x + win_width // 2, floor_y // 4 + 1,
                        win_x + win_width // 2, floor_y // 4 + win_height, palette['wood'][2])
        canvas.draw_line(win_x, floor_y // 4 + win_height // 2,
                        win_x + win_width, floor_y // 4 + win_height // 2, palette['wood'][2])

        # Light rays from window
        for i in range(5):
            ray_y = floor_y // 4 + 5 + i * 4
            ray_start = win_x + win_width
            ray_end = min(width - 1, ray_start + 20 + i * 3)
            ray_color = (*palette['accent'][:3], 30)  # Semi-transparent
            # Would need alpha blending
            pass


def draw_desk(canvas, x, y, width, height, palette):
    """Draw a simple desk/table."""
    wood = palette['wood']

    # Tabletop
    canvas.fill_rect(x, y, width, 3, wood[1])
    canvas.draw_line(x, y, x + width - 1, y, wood[2])  # Top highlight

    # Legs
    leg_width = 2
    leg_height = height - 3
    canvas.fill_rect(x + 2, y + 3, leg_width, leg_height, wood[0])
    canvas.fill_rect(x + width - 4, y + 3, leg_width, leg_height, wood[0])
```

## Tavern / Inn

```python
def draw_tavern_bg(canvas, width, height):
    """Draw a tavern interior."""
    palette = INDOOR_PALETTES['tavern']

    # Floor
    floor_y = height * 2 // 3
    for y in range(floor_y, height):
        # Wooden planks
        plank = (y - floor_y) // 4
        color = palette['floor'][1] if plank % 2 == 0 else palette['floor'][0]
        canvas.draw_line(0, y, width - 1, y, color)
        # Plank gaps
        if (y - floor_y) % 4 == 3:
            canvas.draw_line(0, y, width - 1, y, palette['floor'][0])

    # Wall
    for y in range(floor_y):
        t = y / floor_y
        idx = min(2, int(t * 3))
        canvas.draw_line(0, y, width - 1, y, palette['wall'][2 - idx])

    # Fireplace (if large enough)
    if width >= 80:
        fire_x = width - width // 4
        fire_width = width // 5
        fire_height = floor_y // 2

        # Stone fireplace
        stone = INDOOR_PALETTES['castle']['stone']
        canvas.fill_rect(fire_x - 2, floor_y - fire_height - 4, fire_width + 4, fire_height + 4, stone[0])
        canvas.draw_rect(fire_x - 2, floor_y - fire_height - 4, fire_width + 4, fire_height + 4, stone[2])

        # Fire opening
        canvas.fill_rect(fire_x, floor_y - fire_height, fire_width, fire_height, (20, 15, 15))

        # Fire glow
        fire_colors = [(255, 200, 50), (255, 150, 30), (255, 100, 20)]
        for i, color in enumerate(fire_colors):
            fy = floor_y - 4 - i * 3
            fw = fire_width - 4 - i * 2
            if fw > 0:
                canvas.fill_rect(fire_x + 2 + i, fy, fw, 3, color)

    # Bar counter
    bar_y = floor_y - 8
    bar_height = 8
    canvas.fill_rect(0, bar_y, width // 3, bar_height, palette['wood'][1])
    canvas.draw_line(0, bar_y, width // 3, bar_y, palette['wood'][2])

    # Hanging lantern (if space)
    if width >= 64:
        lantern_x = width // 2
        lantern_y = 10
        # Chain
        canvas.draw_line(lantern_x, 0, lantern_x, lantern_y - 2, (80, 80, 90))
        # Lantern
        canvas.fill_rect(lantern_x - 2, lantern_y, 5, 6, (50, 45, 40))
        canvas.fill_rect(lantern_x - 1, lantern_y + 1, 3, 4, palette['accent'])
```

## Castle / Throne Room

```python
def draw_castle_bg(canvas, width, height):
    """Draw a castle interior."""
    palette = INDOOR_PALETTES['castle']

    # Stone floor
    floor_y = height * 2 // 3
    for y in range(floor_y, height):
        canvas.draw_line(0, y, width - 1, y, palette['floor'][1])

    # Stone floor pattern (tiles)
    tile_size = 8
    for ty in range(floor_y, height, tile_size):
        for tx in range(0, width, tile_size):
            # Tile edges
            canvas.draw_line(tx, ty, tx, min(height - 1, ty + tile_size - 1), palette['floor'][0])
            canvas.draw_line(tx, ty, min(width - 1, tx + tile_size - 1), ty, palette['floor'][0])

    # Stone walls
    for y in range(floor_y):
        canvas.draw_line(0, y, width - 1, y, palette['wall'][1])

    # Wall stone pattern
    stone_h = 6
    for sy in range(0, floor_y, stone_h):
        offset = (sy // stone_h) % 2 * 8
        for sx in range(-offset, width, 16):
            canvas.draw_line(sx, sy, sx, min(floor_y - 1, sy + stone_h - 1), palette['wall'][0])
            canvas.draw_line(sx, sy + stone_h - 1, min(width - 1, sx + 15), sy + stone_h - 1, palette['wall'][0])

    # Pillars
    if width >= 100:
        pillar_width = 6
        pillar_positions = [width // 5, width * 4 // 5]
        for px in pillar_positions:
            # Pillar base
            canvas.fill_rect(px - pillar_width // 2 - 1, floor_y - 4, pillar_width + 2, 4, palette['stone'][2])
            # Pillar shaft
            canvas.fill_rect(px - pillar_width // 2, 10, pillar_width, floor_y - 14, palette['stone'][1])
            # Pillar highlight
            canvas.draw_line(px - pillar_width // 2, 10, px - pillar_width // 2, floor_y - 4, palette['stone'][2])
            # Pillar shadow
            canvas.draw_line(px + pillar_width // 2 - 1, 10, px + pillar_width // 2 - 1, floor_y - 4, palette['stone'][0])
            # Capital
            canvas.fill_rect(px - pillar_width // 2 - 1, 6, pillar_width + 2, 4, palette['stone'][2])

    # Torches on walls
    if width >= 64:
        torch_positions = [width // 4, width * 3 // 4]
        for tx in torch_positions:
            ty = floor_y // 2
            # Bracket
            canvas.fill_rect(tx - 1, ty, 3, 2, (60, 50, 45))
            # Torch
            canvas.fill_rect(tx, ty + 2, 1, 6, (80, 60, 45))
            # Flame
            canvas.set_pixel(tx, ty - 1, (255, 200, 50))
            canvas.set_pixel(tx, ty - 2, (255, 150, 30))
```

## Generic Room Template

```python
def draw_simple_room(canvas, width, height, palette_name='cozy',
                     floor_ratio=0.35, has_window=True):
    """
    Draw a generic room background.

    Args:
        floor_ratio: How much of height is floor (0.0 to 1.0)
        has_window: Add a window
    """
    palette = INDOOR_PALETTES.get(palette_name, INDOOR_PALETTES['cozy'])

    floor_y = int(height * (1 - floor_ratio))

    # Draw wall
    for y in range(floor_y):
        gradient_t = y / floor_y
        # Lighter at top
        idx = 2 - min(2, int(gradient_t * 3))
        canvas.draw_line(0, y, width - 1, y, palette['wall'][idx])

    # Draw floor
    for y in range(floor_y, height):
        gradient_t = (y - floor_y) / (height - floor_y)
        idx = min(2, int(gradient_t * 3))
        canvas.draw_line(0, y, width - 1, y, palette['floor'][idx])

    # Wall-floor boundary line
    canvas.draw_line(0, floor_y, width - 1, floor_y, palette['floor'][0])

    # Optional window
    if has_window and width >= 48:
        win_width = min(20, width // 4)
        win_height = min(28, floor_y // 2)
        win_x = (width - win_width) // 2
        win_y = (floor_y - win_height) // 2

        # Frame
        canvas.draw_rect(win_x - 1, win_y - 1, win_width + 2, win_height + 2, palette['wood'][1])
        # Glass
        canvas.fill_rect(win_x, win_y, win_width, win_height, (180, 200, 220))
        # Dividers
        canvas.draw_line(win_x + win_width // 2, win_y, win_x + win_width // 2, win_y + win_height - 1, palette['wood'][1])
        canvas.draw_line(win_x, win_y + win_height // 2, win_x + win_width - 1, win_y + win_height // 2, palette['wood'][1])

    return floor_y  # Return floor level for object placement
```

## Time of Day Modifiers

```python
def apply_time_modifier(canvas, time='day'):
    """Apply color overlay for time of day."""
    modifiers = {
        'day': None,  # No change
        'morning': (255, 240, 220, 20),  # Warm yellow
        'evening': (255, 200, 150, 30),  # Orange
        'sunset': (255, 150, 100, 40),   # Deep orange
        'night': (50, 50, 100, 60),      # Blue
        'midnight': (20, 20, 50, 80),    # Dark blue
    }

    overlay = modifiers.get(time)
    if overlay:
        # Apply tint to entire canvas
        # This would need alpha blending support
        pass
```

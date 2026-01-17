# Potions & Bottles Recipe

How to draw potion bottles, vials, and liquid containers in pixel art.

## General Principles

1. **Glass transparency**: Show contents through bottle
2. **Liquid level**: Visible fill line adds realism
3. **Reflections**: Light spots indicate glass surface
4. **Cork/stopper**: Adds character and closure

## Standard Potion Bottle

Classic round-bottom flask with cork.

### Color Palettes

```python
POTION_COLORS = {
    # Glass
    'glass': {
        'outline': (80, 90, 100),
        'highlight': (200, 220, 240),
        'glint': (255, 255, 255),
    },

    # Liquid types
    'health': {  # Red
        'dark': (120, 20, 30),
        'mid': (180, 40, 50),
        'light': (220, 80, 90),
        'glow': (255, 120, 130),
    },
    'mana': {  # Blue
        'dark': (30, 50, 120),
        'mid': (50, 90, 180),
        'light': (90, 140, 220),
        'glow': (140, 180, 255),
    },
    'poison': {  # Green
        'dark': (30, 80, 30),
        'mid': (50, 140, 50),
        'light': (90, 180, 90),
        'glow': (140, 220, 140),
    },
    'stamina': {  # Yellow/Gold
        'dark': (140, 100, 20),
        'mid': (200, 160, 40),
        'light': (240, 200, 80),
        'glow': (255, 230, 140),
    },
    'magic': {  # Purple
        'dark': (80, 30, 100),
        'mid': (140, 60, 180),
        'light': (180, 100, 220),
        'glow': (220, 160, 255),
    },
    'water': {  # Clear blue
        'dark': (100, 140, 180),
        'mid': (140, 180, 210),
        'light': (180, 210, 235),
        'glow': (220, 240, 255),
    },

    # Cork/stopper
    'cork': {
        'dark': (100, 70, 50),
        'mid': (150, 110, 80),
        'light': (190, 150, 110),
    },
}
```

### Drawing Steps

```python
def draw_potion(canvas, x, y, width, height, liquid_type='health', fill=0.7):
    """
    Draw a potion bottle.

    Args:
        x, y: Top-left position
        width, height: Size of bottle
        liquid_type: Color key from POTION_COLORS
        fill: Liquid fill level (0.0 to 1.0)
    """
    glass = POTION_COLORS['glass']
    liquid = POTION_COLORS[liquid_type]
    cork = POTION_COLORS['cork']

    # Proportions
    neck_height = height // 4
    neck_width = width // 3
    body_height = height - neck_height
    cork_height = max(2, neck_height // 2)

    # Body center
    body_cx = x + width // 2
    body_cy = y + neck_height + body_height // 2
    body_rx = width // 2
    body_ry = body_height // 2

    # 1. BOTTLE BODY (ellipse)
    # Liquid fill first (behind glass)
    if fill > 0:
        liquid_height = int(body_height * fill)
        liquid_top = body_cy + body_ry - liquid_height

        # Draw liquid as clipped ellipse
        for py in range(liquid_top, body_cy + body_ry):
            # Calculate ellipse width at this y
            rel_y = (py - body_cy) / body_ry if body_ry > 0 else 0
            if abs(rel_y) <= 1:
                import math
                half_width = int(body_rx * math.sqrt(1 - rel_y * rel_y))
                # Gradient from dark (bottom) to light (top)
                t = (py - liquid_top) / max(1, liquid_height)
                if t < 0.3:
                    color = liquid['light']
                elif t < 0.7:
                    color = liquid['mid']
                else:
                    color = liquid['dark']
                canvas.draw_line(body_cx - half_width + 1, py, body_cx + half_width - 1, py, color)

    # Glass outline
    canvas.draw_ellipse_aa(body_cx, body_cy, body_rx, body_ry, glass['outline'])

    # 2. NECK
    neck_x = x + (width - neck_width) // 2
    canvas.fill_rect(neck_x, y + cork_height, neck_width, neck_height - cork_height, glass['outline'])
    # Neck inner (transparent/liquid)
    if fill > 0.8:  # Liquid reaches neck
        canvas.fill_rect(neck_x + 1, y + cork_height, neck_width - 2, neck_height - cork_height - 1, liquid['mid'])
    # Neck highlight
    canvas.draw_line(neck_x, y + cork_height, neck_x, y + neck_height, glass['highlight'])

    # 3. CORK
    canvas.fill_rect(neck_x - 1, y, neck_width + 2, cork_height, cork['mid'])
    canvas.draw_line(neck_x - 1, y, neck_x + neck_width, y, cork['light'])
    canvas.draw_line(neck_x - 1, y + cork_height - 1, neck_x + neck_width, y + cork_height - 1, cork['dark'])

    # 4. GLASS HIGHLIGHTS
    # Main highlight (upper left of body)
    highlight_x = body_cx - body_rx // 2
    highlight_y = body_cy - body_ry // 2
    canvas.set_pixel(highlight_x, highlight_y, glass['highlight'])
    canvas.set_pixel(highlight_x + 1, highlight_y, glass['glint'])

    # Secondary highlight (small)
    canvas.set_pixel(body_cx + body_rx // 3, body_cy - body_ry // 3, glass['highlight'])

    # 5. GLOW EFFECT (for magical potions)
    if liquid_type in ('magic', 'mana', 'health'):
        # Subtle glow pixels around bottle
        glow_color = (*liquid['glow'][:3], 100)  # Semi-transparent
        # This would need alpha blending support
        pass
```

## Vial (Small Potion)

Smaller, simpler container.

```python
def draw_vial(canvas, x, y, height, liquid_type='health', fill=0.8):
    """Draw a small vial/test tube style container."""
    width = max(4, height // 3)

    glass = POTION_COLORS['glass']
    liquid = POTION_COLORS[liquid_type]
    cork = POTION_COLORS['cork']

    cork_height = 2
    body_height = height - cork_height

    # Body (simple rectangle with rounded bottom)
    # Liquid
    if fill > 0:
        liquid_height = int(body_height * fill)
        canvas.fill_rect(x + 1, y + cork_height + body_height - liquid_height,
                        width - 2, liquid_height - 1, liquid['mid'])

    # Glass outline
    canvas.draw_rect(x, y + cork_height, width, body_height, glass['outline'])

    # Round bottom
    canvas.set_pixel(x, y + height - 1, (0, 0, 0, 0))  # Clear corners
    canvas.set_pixel(x + width - 1, y + height - 1, (0, 0, 0, 0))

    # Cork
    canvas.fill_rect(x, y, width, cork_height, cork['mid'])

    # Highlight
    canvas.set_pixel(x + 1, y + cork_height + 2, glass['glint'])
```

## Flask (Wide Bottom)

Erlenmeyer/conical flask shape.

```python
def draw_flask(canvas, x, y, width, height, liquid_type='magic', fill=0.6):
    """Draw a wide-bottom flask."""
    glass = POTION_COLORS['glass']
    liquid = POTION_COLORS[liquid_type]
    cork = POTION_COLORS['cork']

    neck_width = width // 3
    neck_height = height // 3
    body_height = height - neck_height

    # Draw as trapezoid body + narrow neck
    # Body (trapezoid - wide at bottom)
    for row in range(body_height):
        # Width increases as we go down
        progress = row / body_height
        row_width = int(neck_width + (width - neck_width) * progress)
        row_x = x + (width - row_width) // 2
        row_y = y + neck_height + row

        # Liquid fill
        if fill > 0 and row >= body_height * (1 - fill):
            canvas.draw_line(row_x + 1, row_y, row_x + row_width - 2, row_y, liquid['mid'])

        # Outline
        canvas.set_pixel(row_x, row_y, glass['outline'])
        canvas.set_pixel(row_x + row_width - 1, row_y, glass['outline'])

    # Bottom edge
    canvas.draw_line(x, y + height - 1, x + width - 1, y + height - 1, glass['outline'])

    # Neck
    neck_x = x + (width - neck_width) // 2
    canvas.fill_rect(neck_x, y + 2, neck_width, neck_height - 2, glass['outline'])
    # Neck highlight
    canvas.draw_line(neck_x, y + 2, neck_x, y + neck_height, glass['highlight'])

    # Cork
    canvas.fill_rect(neck_x - 1, y, neck_width + 2, 2, cork['mid'])

    # Highlight
    canvas.set_pixel(x + width // 3, y + neck_height + body_height // 3, glass['glint'])
```

## Bubbles (Animation Detail)

For animated potions, add bubbles.

```python
def draw_bubble(canvas, x, y, size, liquid_type='health'):
    """Draw a single bubble in liquid."""
    liquid = POTION_COLORS[liquid_type]

    if size == 1:
        canvas.set_pixel(x, y, liquid['light'])
    elif size == 2:
        canvas.set_pixel(x, y, liquid['light'])
        canvas.set_pixel(x + 1, y, liquid['glow'])
    else:
        canvas.fill_ellipse(x, y, size, size, liquid['light'])
        canvas.set_pixel(x, y - size // 2, liquid['glow'])  # Highlight
```

## Scale Reference

At 128x128 with standard character:
- Held potion: 8-12px wide, 14-18px tall
- Small vial: 4-6px wide, 10-12px tall
- Table flask: 16-24px wide, 20-28px tall

At 64x64:
- Held potion: 4-6px wide, 7-9px tall
- Focus on shape silhouette, minimal detail

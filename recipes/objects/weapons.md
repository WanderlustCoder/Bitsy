# Weapons Recipe

How to draw swords, staffs, bows, and other weapons in pixel art.

## General Principles

1. **Metal shading**: Use 3-4 tone gradient for metallic surfaces
2. **Edge highlights**: Sharp edges catch light
3. **Handle wrapping**: Show grip texture
4. **Proportions**: Weapons should fit character scale

## Metal Palettes

```python
METAL_COLORS = {
    'steel': {
        'darkest': (60, 65, 75),
        'dark': (100, 110, 125),
        'mid': (150, 160, 175),
        'light': (200, 210, 225),
        'highlight': (240, 245, 255),
    },
    'iron': {
        'darkest': (50, 50, 55),
        'dark': (80, 80, 90),
        'mid': (120, 120, 130),
        'light': (160, 160, 170),
        'highlight': (200, 200, 210),
    },
    'gold': {
        'darkest': (120, 80, 20),
        'dark': (180, 130, 40),
        'mid': (220, 180, 60),
        'light': (250, 220, 100),
        'highlight': (255, 245, 180),
    },
    'silver': {
        'darkest': (100, 105, 115),
        'dark': (140, 150, 165),
        'mid': (180, 190, 205),
        'light': (220, 225, 235),
        'highlight': (250, 252, 255),
    },
    'bronze': {
        'darkest': (80, 50, 30),
        'dark': (130, 90, 50),
        'mid': (180, 140, 80),
        'light': (210, 180, 120),
        'highlight': (240, 220, 170),
    },
    'dark_steel': {  # For evil/dark weapons
        'darkest': (30, 30, 40),
        'dark': (50, 50, 65),
        'mid': (80, 80, 100),
        'light': (120, 120, 145),
        'highlight': (160, 165, 190),
    },
}

HANDLE_COLORS = {
    'leather': {
        'dark': (50, 35, 25),
        'mid': (90, 65, 45),
        'light': (130, 100, 75),
    },
    'wood': {
        'dark': (60, 40, 30),
        'mid': (110, 80, 55),
        'light': (160, 125, 90),
    },
    'cloth': {
        'dark': (40, 35, 50),
        'mid': (70, 60, 85),
        'light': (110, 100, 130),
    },
    'red_leather': {
        'dark': (80, 30, 30),
        'mid': (140, 50, 45),
        'light': (180, 80, 70),
    },
}

GEM_COLORS = {
    'ruby': (200, 40, 60),
    'sapphire': (40, 80, 200),
    'emerald': (40, 180, 80),
    'amethyst': (160, 60, 200),
    'diamond': (220, 230, 255),
}
```

## Sword

### Standard Sword

```python
def draw_sword(canvas, x, y, length, angle=0, metal='steel', handle='leather'):
    """
    Draw a sword.

    Args:
        x, y: Hilt position (where hand grips)
        length: Total sword length
        angle: Rotation in degrees (0 = pointing up)
        metal: Metal type from METAL_COLORS
        handle: Handle type from HANDLE_COLORS
    """
    import math

    m = METAL_COLORS[metal]
    h = HANDLE_COLORS[handle]

    rad = math.radians(angle)
    cos_a, sin_a = math.cos(rad), math.sin(rad)

    # Proportions
    blade_length = int(length * 0.7)
    handle_length = int(length * 0.2)
    guard_width = max(4, length // 6)

    def offset_point(dist, perp=0):
        """Get point at distance along blade, with perpendicular offset."""
        px = x + int(dist * cos_a - perp * sin_a)
        py = y + int(dist * sin_a + perp * cos_a)
        return px, py

    # 1. HANDLE
    for i in range(-handle_length, 0):
        px, py = offset_point(i)
        # Wrapped texture
        if (i // 2) % 2 == 0:
            canvas.set_pixel(px, py, h['mid'])
        else:
            canvas.set_pixel(px, py, h['dark'])

    # Pommel (end of handle)
    px, py = offset_point(-handle_length - 1)
    canvas.set_pixel(px, py, m['mid'])

    # 2. GUARD (crossguard)
    for i in range(-guard_width // 2, guard_width // 2 + 1):
        px, py = offset_point(0, i)
        if abs(i) == guard_width // 2:
            canvas.set_pixel(px, py, m['dark'])
        else:
            canvas.set_pixel(px, py, m['mid'])

    # 3. BLADE
    blade_width = max(2, length // 10)

    for dist in range(1, blade_length + 1):
        # Taper toward tip
        if dist > blade_length - 4:
            width = max(1, blade_width - (dist - (blade_length - 4)))
        else:
            width = blade_width

        # Draw blade cross-section
        for w in range(-width // 2, width // 2 + 1):
            px, py = offset_point(dist, w)
            if w == -width // 2:
                canvas.set_pixel(px, py, m['dark'])  # Shadow edge
            elif w == width // 2:
                canvas.set_pixel(px, py, m['highlight'])  # Light edge
            elif w == 0:
                canvas.set_pixel(px, py, m['light'])  # Center highlight
            else:
                canvas.set_pixel(px, py, m['mid'])

    # Tip
    px, py = offset_point(blade_length + 1)
    canvas.set_pixel(px, py, m['light'])


def draw_sword_simple(canvas, x, y, length, metal='steel'):
    """Simplified vertical sword for small sizes."""
    m = METAL_COLORS[metal]

    handle_len = length // 5
    guard_width = 4

    # Handle
    for i in range(handle_len):
        canvas.set_pixel(x, y + length - i, (80, 60, 45))

    # Guard
    canvas.draw_line(x - guard_width//2, y + length - handle_len,
                    x + guard_width//2, y + length - handle_len, m['mid'])

    # Blade
    for i in range(length - handle_len - 1):
        canvas.set_pixel(x - 1, y + i + 1, m['dark'])
        canvas.set_pixel(x, y + i + 1, m['light'])
        canvas.set_pixel(x + 1, y + i + 1, m['mid'])

    # Tip
    canvas.set_pixel(x, y, m['highlight'])
```

## Staff / Wand

```python
def draw_staff(canvas, x, y, length, style='wooden', gem_color=None):
    """
    Draw a magic staff.

    Args:
        style: 'wooden', 'crystal', 'dark'
        gem_color: Optional gem at top
    """
    if style == 'wooden':
        colors = {
            'dark': (60, 45, 35),
            'mid': (100, 80, 60),
            'light': (150, 125, 100),
        }
    elif style == 'crystal':
        colors = METAL_COLORS['silver']
    else:  # dark
        colors = {
            'dark': (30, 25, 35),
            'mid': (50, 45, 60),
            'light': (80, 75, 95),
        }

    shaft_width = max(2, length // 15)

    # Main shaft
    for i in range(length):
        progress = i / length
        # Slight taper
        if progress < 0.1 or progress > 0.9:
            width = shaft_width - 1
        else:
            width = shaft_width

        for w in range(width):
            px = x + w - width // 2
            py = y + i

            if w == 0:
                canvas.set_pixel(px, py, colors['dark'])
            elif w == width - 1:
                canvas.set_pixel(px, py, colors['light'])
            else:
                canvas.set_pixel(px, py, colors['mid'])

    # Top ornament
    if gem_color:
        gem = GEM_COLORS.get(gem_color, (200, 100, 200))
        gem_size = max(3, shaft_width + 2)

        # Mounting
        for w in range(-1, 2):
            canvas.set_pixel(x + w, y - 1, colors['mid'])

        # Gem
        canvas.fill_ellipse(x, y - gem_size, gem_size, gem_size, gem)
        # Gem highlight
        canvas.set_pixel(x - 1, y - gem_size - 1, (255, 255, 255))
    else:
        # Simple carved top
        canvas.set_pixel(x, y - 1, colors['light'])
        canvas.set_pixel(x - 1, y - 2, colors['mid'])
        canvas.set_pixel(x + 1, y - 2, colors['mid'])
        canvas.set_pixel(x, y - 3, colors['mid'])


def draw_wand(canvas, x, y, length, style='wooden'):
    """Draw a small wand (simplified staff)."""
    if style == 'wooden':
        color = (120, 90, 65)
        tip = (180, 160, 140)
    else:
        color = (60, 60, 80)
        tip = (150, 150, 200)

    # Simple tapered line
    for i in range(length):
        canvas.set_pixel(x, y + i, color)

    # Sparkle tip
    canvas.set_pixel(x, y - 1, tip)
    canvas.set_pixel(x, y - 2, (255, 255, 255))
```

## Bow

```python
def draw_bow(canvas, x, y, height, style='wooden', drawn=False):
    """
    Draw a bow.

    Args:
        drawn: If True, show with arrow nocked and string pulled
    """
    if style == 'wooden':
        wood = HANDLE_COLORS['wood']
    else:
        wood = METAL_COLORS['dark_steel']

    string_color = (180, 170, 150)

    # Bow width (how curved)
    bow_width = height // 3

    # Draw curved bow body
    for i in range(height):
        # Curve: widest at middle
        progress = abs(i - height // 2) / (height // 2)
        curve = int(bow_width * (1 - progress * progress))

        if drawn:
            curve = curve // 2  # Flattened when drawn

        px = x + curve
        py = y + i

        # Bow limb
        if i < 3 or i > height - 4:
            canvas.set_pixel(px, py, wood['dark'])
        elif i == height // 2:
            canvas.set_pixel(px, py, wood['mid'])  # Handle
            canvas.set_pixel(px - 1, py, wood['dark'])
        else:
            canvas.set_pixel(px, py, wood['mid'])
            canvas.set_pixel(px - 1, py, wood['light'])

    # String
    if drawn:
        # Pulled back string
        mid_y = y + height // 2
        canvas.draw_line(x + bow_width // 2, y, x - bow_width // 2, mid_y, string_color)
        canvas.draw_line(x - bow_width // 2, mid_y, x + bow_width // 2, y + height - 1, string_color)
    else:
        # Relaxed string
        for i in range(height):
            curve = int(bow_width * (1 - (abs(i - height // 2) / (height // 2)) ** 2))
            canvas.set_pixel(x + curve - 1, y + i, string_color)


def draw_arrow(canvas, x, y, length, angle=0):
    """Draw an arrow."""
    import math

    shaft_color = (160, 130, 100)
    head_color = METAL_COLORS['iron']['mid']
    fletching = (200, 50, 50)  # Red feathers

    rad = math.radians(angle)

    # Shaft
    for i in range(length):
        px = x + int(i * math.cos(rad))
        py = y + int(i * math.sin(rad))
        canvas.set_pixel(px, py, shaft_color)

    # Arrowhead (triangle)
    head_len = max(3, length // 5)
    for i in range(head_len):
        px = x + int((length + i) * math.cos(rad))
        py = y + int((length + i) * math.sin(rad))
        canvas.set_pixel(px, py, head_color)
        # Width
        if i < head_len - 1:
            w = head_len - i - 1
            for wi in range(1, w):
                perp_x = int(-wi * math.sin(rad))
                perp_y = int(wi * math.cos(rad))
                canvas.set_pixel(px + perp_x, py + perp_y, head_color)
                canvas.set_pixel(px - perp_x, py - perp_y, head_color)

    # Fletching (back)
    for i in range(3):
        px = x - int((i + 1) * math.cos(rad))
        py = y - int((i + 1) * math.sin(rad))
        canvas.set_pixel(px, py, fletching)
```

## Dagger / Knife

```python
def draw_dagger(canvas, x, y, length, metal='steel'):
    """Draw a small dagger."""
    m = METAL_COLORS[metal]

    blade_len = int(length * 0.7)
    handle_len = length - blade_len

    # Handle
    for i in range(handle_len):
        canvas.set_pixel(x, y + length - i, (80, 60, 45))

    # Small guard
    canvas.set_pixel(x - 1, y + blade_len, m['dark'])
    canvas.set_pixel(x + 1, y + blade_len, m['dark'])

    # Blade (thin)
    for i in range(blade_len):
        # Taper
        if i < 3:
            canvas.set_pixel(x - 1, y + i, m['dark'])
            canvas.set_pixel(x, y + i, m['light'])
            canvas.set_pixel(x + 1, y + i, m['mid'])
        else:
            canvas.set_pixel(x, y + i, m['mid'])

    # Tip
    canvas.set_pixel(x, y - 1, m['highlight'])
```

## Scale Reference

At 128x128 with standard character:
- Sword (held): 40-50px long
- Dagger: 15-20px long
- Staff: 70-90px tall
- Wand: 15-25px long
- Bow: 50-60px tall

At 64x64:
- Sword: 20-25px long
- Keep details minimal
- Focus on recognizable silhouette

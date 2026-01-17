# Books & Writing Objects Recipe

How to draw books, scrolls, and writing implements in pixel art.

## General Principles

1. **Perspective**: Use slight 3/4 view for depth
2. **Pages**: Show page thickness with light edge
3. **Binding**: Visible spine adds realism
4. **Scale**: Books should be proportional to holder's hands

## Book (Standard)

A basic closed or open book.

### Closed Book (Held)
Size: 12-16px wide, 8-12px tall at typical character scale

```
Layers (back to front):
1. Pages edge (light cream/white)
2. Cover back
3. Spine
4. Cover front
5. Details (clasps, title)
```

### Color Palette
```python
BOOK_COLORS = {
    'leather_brown': {
        'dark': (60, 40, 30),
        'mid': (100, 70, 50),
        'light': (140, 100, 75),
    },
    'leather_red': {
        'dark': (90, 30, 30),
        'mid': (140, 50, 45),
        'light': (180, 80, 70),
    },
    'leather_blue': {
        'dark': (30, 40, 70),
        'mid': (50, 70, 120),
        'light': (80, 110, 160),
    },
    'leather_green': {
        'dark': (30, 60, 40),
        'mid': (50, 100, 65),
        'light': (80, 140, 95),
    },
    'pages': {
        'dark': (200, 190, 170),  # shadow
        'mid': (235, 225, 205),   # base
        'light': (250, 245, 235), # highlight
    },
}
```

### Drawing Steps

```python
def draw_book_closed(canvas, x, y, width, height, color='leather_brown'):
    """Draw a closed book at position."""
    colors = BOOK_COLORS[color]
    pages = BOOK_COLORS['pages']

    # Calculate proportions
    spine_width = max(2, width // 6)
    page_thickness = max(1, height // 8)

    # 1. Pages edge (visible on bottom/right)
    canvas.fill_rect(
        x + spine_width, y + height - page_thickness,
        width - spine_width, page_thickness,
        pages['mid']
    )

    # 2. Cover back (slightly visible)
    canvas.fill_rect(x + 1, y + 1, width - 1, height - 1, colors['dark'])

    # 3. Spine
    canvas.fill_rect(x, y, spine_width, height, colors['mid'])
    # Spine highlight
    canvas.draw_line(x, y, x, y + height - 1, colors['light'])

    # 4. Cover front
    canvas.fill_rect(
        x + spine_width, y,
        width - spine_width, height - page_thickness,
        colors['mid']
    )

    # 5. Cover details - edge highlight
    canvas.draw_line(
        x + spine_width, y,
        x + width - 1, y,
        colors['light']
    )

    # Optional: corner decoration
    if width >= 14:
        corner_size = 2
        canvas.fill_rect(
            x + width - corner_size - 1, y + 1,
            corner_size, corner_size,
            colors['light']
        )
```

### Open Book

```python
def draw_book_open(canvas, x, y, width, height, color='leather_brown'):
    """Draw an open book (as if reading)."""
    colors = BOOK_COLORS[color]
    pages = BOOK_COLORS['pages']

    half_width = width // 2
    spine_y = y + height // 2

    # Left page
    canvas.fill_rect(x, y, half_width - 1, height, pages['mid'])
    # Left page shadow (near spine)
    canvas.fill_rect(x + half_width - 3, y, 2, height, pages['dark'])

    # Right page
    canvas.fill_rect(x + half_width + 1, y, half_width - 1, height, pages['mid'])
    # Right page shadow
    canvas.fill_rect(x + half_width + 1, y, 2, height, pages['dark'])

    # Spine (center)
    canvas.draw_line(x + half_width - 1, y, x + half_width - 1, y + height, colors['mid'])
    canvas.draw_line(x + half_width, y, x + half_width, y + height, colors['dark'])

    # Cover edges visible
    canvas.draw_rect(x - 1, y - 1, width + 2, height + 2, colors['mid'])

    # Text lines (subtle)
    for i in range(3):
        line_y = y + 3 + i * 3
        # Left page text
        canvas.draw_line(x + 2, line_y, x + half_width - 5, line_y, pages['dark'])
        # Right page text
        canvas.draw_line(x + half_width + 4, line_y, x + width - 3, line_y, pages['dark'])
```

## Spellbook / Tome

Larger, more ornate book with magical elements.

```python
def draw_spellbook(canvas, x, y, width, height, color='leather_blue'):
    """Draw an ornate magical tome."""
    # Base book
    draw_book_closed(canvas, x, y, width, height, color)

    colors = BOOK_COLORS[color]

    # Add magical elements
    center_x = x + width // 2
    center_y = y + height // 2

    # Glowing gem/clasp in center
    gem_size = max(2, min(width, height) // 4)
    gem_color = (180, 120, 255)  # Purple glow
    gem_highlight = (220, 180, 255)

    canvas.fill_ellipse(center_x, center_y, gem_size, gem_size, gem_color)
    canvas.set_pixel(center_x - 1, center_y - 1, gem_highlight)

    # Corner runes (if large enough)
    if width >= 16:
        rune_color = (150, 100, 200)
        # Top corners
        canvas.set_pixel(x + 2, y + 2, rune_color)
        canvas.set_pixel(x + width - 3, y + 2, rune_color)
        # Bottom corners
        canvas.set_pixel(x + 2, y + height - 3, rune_color)
        canvas.set_pixel(x + width - 3, y + height - 3, rune_color)
```

## Scroll

Rolled parchment, can be open or closed.

```python
SCROLL_COLORS = {
    'parchment': {
        'dark': (180, 160, 120),
        'mid': (220, 200, 160),
        'light': (245, 235, 210),
    },
    'rod': {
        'wood': (100, 70, 50),
        'gold': (200, 170, 80),
    }
}

def draw_scroll_closed(canvas, x, y, width, height):
    """Draw a rolled-up scroll."""
    colors = SCROLL_COLORS['parchment']
    rod = SCROLL_COLORS['rod']['wood']

    # Main roll
    canvas.fill_ellipse(x + width//2, y + height//2, width//2, height//2, colors['mid'])

    # Highlight on roll (curved surface)
    canvas.draw_line(x + 2, y + height//3, x + width - 2, y + height//3, colors['light'])

    # Shadow on bottom
    canvas.draw_line(x + 2, y + height - 2, x + width - 2, y + height - 2, colors['dark'])

    # Rod ends visible
    rod_extend = 2
    canvas.fill_rect(x - rod_extend, y + 1, rod_extend, height - 2, rod)
    canvas.fill_rect(x + width, y + 1, rod_extend, height - 2, rod)


def draw_scroll_open(canvas, x, y, width, height):
    """Draw an unrolled scroll."""
    colors = SCROLL_COLORS['parchment']
    rod = SCROLL_COLORS['rod']['wood']

    roll_size = max(3, height // 4)

    # Main parchment area
    canvas.fill_rect(x, y + roll_size, width, height - roll_size * 2, colors['mid'])

    # Top roll
    canvas.fill_ellipse(x + width//2, y + roll_size//2, width//2, roll_size//2, colors['mid'])
    canvas.draw_line(x, y + roll_size//2, x + width, y + roll_size//2, colors['light'])

    # Bottom roll
    canvas.fill_ellipse(
        x + width//2, y + height - roll_size//2,
        width//2, roll_size//2, colors['mid']
    )
    canvas.draw_line(
        x, y + height - roll_size//2,
        x + width, y + height - roll_size//2,
        colors['dark']
    )

    # Text lines
    for i in range(3):
        line_y = y + roll_size + 3 + i * 4
        if line_y < y + height - roll_size - 2:
            canvas.draw_line(x + 3, line_y, x + width - 3, line_y, colors['dark'])
```

## Writing Implements

### Quill

```python
def draw_quill(canvas, x, y, length, angle=45):
    """Draw a feather quill pen."""
    import math

    # Colors
    feather = (240, 235, 220)
    feather_dark = (180, 170, 150)
    shaft = (200, 190, 170)
    tip = (40, 35, 30)

    # Calculate end points based on angle
    rad = math.radians(angle)
    end_x = x + int(length * math.cos(rad))
    end_y = y + int(length * math.sin(rad))

    # Shaft (main line)
    canvas.draw_line_aa(x, y, end_x, end_y, shaft)

    # Tip (nib)
    nib_len = max(2, length // 6)
    nib_x = x - int(nib_len * math.cos(rad))
    nib_y = y - int(nib_len * math.sin(rad))
    canvas.draw_line(nib_x, nib_y, x, y, tip)

    # Feather barbs (at end)
    barb_len = max(3, length // 4)
    # Left barbs
    for i in range(3):
        offset = length - 4 - i * 3
        bx = x + int(offset * math.cos(rad))
        by = y + int(offset * math.sin(rad))
        canvas.draw_line(bx, by, bx - 2, by - 2, feather)
    # Right barbs
    for i in range(3):
        offset = length - 4 - i * 3
        bx = x + int(offset * math.cos(rad))
        by = y + int(offset * math.sin(rad))
        canvas.draw_line(bx, by, bx + 2, by + 2, feather)
```

## Scale Reference

At 128x128 canvas with standard character:
- Held book: 14-18px wide, 10-14px tall
- Open book on table: 24-32px wide, 16-20px tall
- Scroll rolled: 10-12px diameter, 16-20px long
- Quill: 12-16px long

At 64x64:
- Held book: 7-9px wide, 5-7px tall
- Keep details minimal, focus on silhouette

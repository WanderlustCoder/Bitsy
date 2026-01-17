# Portrait Frame Recipe

How to draw decorative frames for portrait-style pixel art.

Learned from: princess portrait recreation (portrait_princess.png)

## Core Principle

Portrait frames add polish and visual interest. They work through:
1. **Layered bands** - Multiple colored rings creating depth
2. **Corner decorations** - Gold triangles or ornaments
3. **Inner border** - Separates frame from content

## Layered Frame Structure

```
┌─────────────────────┐
│ Outer (darkest)     │
│ ┌─────────────────┐ │
│ │ Mid-dark        │ │
│ │ ┌─────────────┐ │ │
│ │ │ Mid-light   │ │ │
│ │ │ ┌─────────┐ │ │ │
│ │ │ │ Inner   │ │ │ │
│ │ │ │(lightest)│ │ │ │
│ │ │ │ CONTENT │ │ │ │
```

## Basic Frame Recipe

```python
def draw_portrait_frame(canvas, width, height, colors, band_widths=None):
    """
    Draw a layered portrait frame.

    colors: list of colors from outer (darkest) to inner (lightest)
            typically 4 colors for a nice frame
    band_widths: width of each band, or None for auto
    """
    if band_widths is None:
        # Default: proportional to image size
        total_frame = min(width, height) // 8
        band_widths = [total_frame // len(colors)] * len(colors)

    offset = 0
    for i, (color, band_w) in enumerate(zip(colors, band_widths)):
        canvas.fill_rect(offset, offset,
                        width - offset * 2, height - offset * 2,
                        color)
        offset += band_w

    # Return inner bounds for content placement
    return offset, offset, width - offset * 2, height - offset * 2


# Purple royalty frame (from portrait_princess.png)
FRAME_PURPLE_ROYALTY = [
    (50, 30, 65),      # Outer - darkest purple
    (85, 50, 100),     # Mid-dark
    (130, 75, 150),    # Mid-light
    (165, 105, 180),   # Inner - lightest purple
]

# Gold frame
FRAME_GOLD = [
    (120, 90, 30),
    (160, 130, 50),
    (200, 170, 80),
    (230, 200, 120),
]

# Dark elegant frame
FRAME_DARK_ELEGANT = [
    (20, 20, 30),
    (40, 40, 55),
    (60, 55, 75),
    (85, 75, 100),
]

# Wood frame
FRAME_WOOD = [
    (50, 35, 25),
    (80, 55, 40),
    (110, 80, 55),
    (140, 105, 75),
]
```

## Corner Decorations

Corner decorations add elegance. The most common is the gold triangle.

```python
def draw_corner_triangle(canvas, origin_x, origin_y, dx, dy, size, colors):
    """
    Draw a triangular corner decoration.

    origin_x, origin_y: corner position
    dx, dy: direction (1,1 for top-left, -1,1 for top-right, etc.)
    size: triangle size in pixels
    colors: [main_color, highlight_color]
    """
    main_color, highlight_color = colors

    for row in range(size):
        for col in range(size - row):
            x = origin_x + col * dx
            y = origin_y + row * dy

            # Highlight near the corner point
            if col + row < size // 4:
                canvas.set_pixel(x, y, highlight_color)
            else:
                canvas.set_pixel(x, y, main_color)


def draw_all_corners(canvas, width, height, frame_offset, size, colors):
    """Draw triangles in all four corners."""
    # Top-left
    draw_corner_triangle(canvas, frame_offset, frame_offset, 1, 1, size, colors)
    # Top-right
    draw_corner_triangle(canvas, width - frame_offset - 1, frame_offset, -1, 1, size, colors)
    # Bottom-left
    draw_corner_triangle(canvas, frame_offset, height - frame_offset - 1, 1, -1, size, colors)
    # Bottom-right
    draw_corner_triangle(canvas, width - frame_offset - 1, height - frame_offset - 1, -1, -1, size, colors)


# Gold corner colors (from portrait_princess.png)
CORNER_GOLD = [
    (230, 195, 65),    # Main gold
    (255, 235, 120),   # Highlight
]
```

## Complete Portrait Frame

```python
def draw_complete_portrait_frame(canvas, width, height,
                                  frame_colors=None,
                                  corner_colors=None,
                                  background_color=None):
    """
    Draw a complete portrait frame with corners.

    Returns the inner content bounds (x, y, w, h).
    """
    if frame_colors is None:
        frame_colors = FRAME_PURPLE_ROYALTY
    if corner_colors is None:
        corner_colors = CORNER_GOLD
    if background_color is None:
        background_color = (235, 200, 75)  # Golden background

    # Calculate frame band widths
    frame_total = min(width, height) // 8
    band_width = frame_total // len(frame_colors)

    # Draw frame layers
    offset = 0
    for color in frame_colors:
        canvas.fill_rect(offset, offset, width - offset*2, height - offset*2, color)
        offset += band_width

    # Draw corner triangles
    corner_size = int(frame_total * 1.2)  # Slightly larger than frame width
    draw_all_corners(canvas, width, height, band_width, corner_size, corner_colors)

    # Fill background
    inner_offset = offset
    canvas.fill_rect(inner_offset, inner_offset,
                    width - inner_offset*2, height - inner_offset*2,
                    background_color)

    # Inner border line
    border_color = frame_colors[1]  # Use mid-dark
    canvas.draw_rect(inner_offset, inner_offset,
                    width - inner_offset*2, height - inner_offset*2,
                    border_color)

    return inner_offset, inner_offset, width - inner_offset*2, height - inner_offset*2
```

## Frame Size Guidelines

| Image Size | Frame Width | Corner Size | Band Count |
|------------|-------------|-------------|------------|
| 32x32      | 4px         | 5px         | 2-3        |
| 64x64      | 8px         | 10px        | 3-4        |
| 128x128    | 16px        | 18px        | 4          |
| 256x256    | 24px        | 28px        | 4-5        |

## Frame Style Presets

```python
PORTRAIT_PRESETS = {
    'princess': {
        'frame': FRAME_PURPLE_ROYALTY,
        'corners': CORNER_GOLD,
        'background': (235, 200, 75),  # Golden
    },
    'noble': {
        'frame': FRAME_DARK_ELEGANT,
        'corners': [(180, 160, 120), (220, 200, 160)],  # Silver
        'background': (60, 55, 70),  # Dark purple
    },
    'rustic': {
        'frame': FRAME_WOOD,
        'corners': None,  # No corner decorations
        'background': (200, 185, 160),  # Parchment
    },
    'royal': {
        'frame': FRAME_GOLD,
        'corners': [(180, 50, 50), (220, 100, 100)],  # Red gems
        'background': (40, 30, 60),  # Deep purple
    },
}
```

## Usage Example

```python
from core.canvas import Canvas

canvas = Canvas(128, 128)

# Draw frame and get content area
content_x, content_y, content_w, content_h = draw_complete_portrait_frame(
    canvas, 128, 128,
    frame_colors=FRAME_PURPLE_ROYALTY,
    corner_colors=CORNER_GOLD,
    background_color=(235, 200, 75)
)

# Now draw character within content bounds
character_cx = content_x + content_w // 2
character_cy = content_y + content_h // 2
# ... draw character centered at (character_cx, character_cy)

canvas.save('output/portrait.png')
```

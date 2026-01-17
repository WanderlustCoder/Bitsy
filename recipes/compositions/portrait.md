# Portrait Composition Recipe

How to compose a character portrait (head and shoulders style).

Learned from: princess portrait recreation (portrait_princess.png)

## Portrait Anatomy

A portrait shows:
1. **Frame** - Decorative border (optional but adds polish)
2. **Background** - Simple color or gradient
3. **Character** - Head, face, hair, upper body/shoulders

```
┌─────────────────────┐
│      FRAME          │
│  ┌───────────────┐  │
│  │  BACKGROUND   │  │
│  │    ┌───┐      │  │
│  │    │HAI│R     │  │
│  │  ┌─┤FAC├─┐    │  │
│  │  │ └───┘ │    │  │
│  │  │ DRESS │    │  │
│  │  └───────┘    │  │
│  └───────────────┘  │
└─────────────────────┘
```

## Vertical Positioning

The character should fill the content area well:

```python
def calculate_portrait_positions(content_x, content_y, content_w, content_h):
    """
    Calculate key positions for portrait elements.

    Returns dict with positions relative to content area.
    """
    # Center horizontally
    cx = content_x + content_w // 2

    # Vertical zones (as ratios of content height)
    # Hair top: 10-15% from top
    # Face center: 35-40% from top
    # Dress starts: 55-60% from top
    # Dress ends: bottom of content

    return {
        'center_x': cx,
        'hair_top_y': content_y + int(content_h * 0.12),
        'face_center_y': content_y + int(content_h * 0.38),
        'dress_top_y': content_y + int(content_h * 0.58),
        'dress_bottom_y': content_y + content_h - 2,
    }
```

## Proportions by Image Size

| Size    | Head Radius | Eye Size | Hair Width | Dress Width |
|---------|-------------|----------|------------|-------------|
| 32x32   | 6-7px       | 2x2      | 14px       | 12-18px     |
| 64x64   | 12-14px     | 3x3      | 28px       | 24-36px     |
| 128x128 | 18-22px     | 5x5      | 40px       | 50-75px     |
| 256x256 | 35-45px     | 8x8      | 80px       | 100-150px   |

## Layer Order (Back to Front)

1. Background
2. Hair back (behind face)
3. Face/skin
4. Eyes
5. Other face details (blush, mouth)
6. Bangs (front hair, covers forehead)
7. Dress/shoulders

```python
def draw_portrait(canvas, positions, palette, features):
    """
    Draw a portrait in correct layer order.

    positions: from calculate_portrait_positions()
    palette: color palette dict
    features: dict of feature options (hair_style, eye_style, etc.)
    """
    cx = positions['center_x']
    face_cy = positions['face_center_y']

    # 1. Hair back layer
    draw_hair_back(canvas, cx, face_cy, palette['hair'], features['hair_style'])

    # 2. Face
    head_rx = 18  # adjust by size
    head_ry = 20
    canvas.fill_ellipse(cx, face_cy, head_rx, head_ry, palette['skin']['base'])

    # 3. Eyes
    draw_eyes(canvas, cx, face_cy - 2, palette['eyes'], features['eye_style'])

    # 4. Blush
    if features.get('blush', True):
        canvas.fill_ellipse(cx - 14, face_cy + 7, 5, 3, palette['skin']['blush'])
        canvas.fill_ellipse(cx + 14, face_cy + 7, 5, 3, palette['skin']['blush'])

    # 5. Mouth
    canvas.draw_line(cx - 2, face_cy + 12, cx + 2, face_cy + 12, palette['mouth'])

    # 6. Bangs (covers forehead)
    draw_bangs(canvas, cx, face_cy, palette['hair'], features.get('bang_style', 'zigzag'))

    # 7. Dress
    draw_dress(canvas, cx, positions['dress_top_y'], positions['dress_bottom_y'],
               palette['clothing'])
```

## Eye Placement

Eyes are critical for expression. For portraits:

```python
def draw_portrait_eyes(canvas, cx, face_cy, eye_color, highlight_color):
    """
    Simple square eyes with highlights (cute style).

    Learned from: portrait_princess.png uses 5x5 squares with 2x2 highlights
    """
    eye_y = face_cy - 2
    eye_size = 5
    eye_spacing = 19  # Distance between eye centers

    # Left eye
    left_eye_x = cx - eye_spacing // 2
    canvas.fill_rect(left_eye_x - eye_size//2, eye_y - eye_size//2,
                    eye_size, eye_size, eye_color)
    # Highlight (upper left of eye)
    canvas.fill_rect(left_eye_x - eye_size//2 + 1, eye_y - eye_size//2,
                    2, 2, highlight_color)

    # Right eye
    right_eye_x = cx + eye_spacing // 2
    canvas.fill_rect(right_eye_x - eye_size//2, eye_y - eye_size//2,
                    eye_size, eye_size, eye_color)
    # Highlight
    canvas.fill_rect(right_eye_x - eye_size//2 + 1, eye_y - eye_size//2,
                    2, 2, highlight_color)
```

## Dress/Shoulders

For a portrait, only upper body shows. Style options:

### Tiered Dress (Princess Style)

```python
def draw_tiered_dress(canvas, cx, top_y, bottom_y, colors, num_tiers=3):
    """
    Dress with horizontal tiers that expand downward.

    Learned from: portrait_princess.png has 3 color tiers
    """
    total_height = bottom_y - top_y
    tier_height = total_height // num_tiers

    for t in range(num_tiers):
        tier_y = top_y + t * tier_height
        tier_end = min(tier_y + tier_height, bottom_y)

        # Color for this tier (cycles through provided colors)
        color = colors[t % len(colors)]

        # Width expands per tier
        base_width = 30 + t * 16

        for row in range(tier_end - tier_y):
            y = tier_y + row
            w = base_width + row  # Slight expansion within tier
            canvas.draw_line(cx - w, y, cx + w, y, color)
```

### Simple Shoulders

```python
def draw_simple_shoulders(canvas, cx, top_y, bottom_y, colors):
    """
    Simple shoulder/neckline without dress detail.
    """
    color = colors[0] if isinstance(colors, list) else colors

    for y in range(top_y, bottom_y):
        rel = (y - top_y) / (bottom_y - top_y)
        w = int(25 + rel * 40)
        canvas.draw_line(cx - w, y, cx + w, y, color)
```

## Complete Portrait Recipe

```python
def draw_complete_portrait(canvas, width, height, palette_name='princess', features=None):
    """
    Draw a complete framed portrait.

    palette_name: 'princess', 'forest', 'night', etc.
    features: {
        'hair_style': 'bob', 'bun', 'long',
        'bang_style': 'zigzag', 'straight', 'side_swept',
        'eye_style': 'simple', 'detailed',
        'dress_style': 'tiered', 'simple',
        'blush': True/False,
    }
    """
    from recipes.palettes import load_palette
    from recipes.frames.portrait import draw_complete_portrait_frame

    if features is None:
        features = {
            'hair_style': 'bob',
            'bang_style': 'zigzag',
            'eye_style': 'simple',
            'dress_style': 'tiered',
            'blush': True,
        }

    palette = load_palette(palette_name)

    # Draw frame
    content = draw_complete_portrait_frame(
        canvas, width, height,
        frame_colors=palette['frame'],
        corner_colors=[palette['accent']['main'], palette['accent']['highlight']],
        background_color=palette['background']
    )

    # Calculate positions
    positions = calculate_portrait_positions(*content)

    # Draw portrait
    draw_portrait(canvas, positions, palette, features)

    return canvas
```

## Scaling Guidelines

When creating portraits at different sizes:

- **32x32**: Minimal detail. Simple shapes, 2-3 colors per element.
- **64x64**: Basic detail. Can add highlights, simple patterns.
- **128x128**: Good detail. Multiple shading levels, clear features.
- **256x256**: Full detail. Can include fine details, accessories.

The same composition rules apply at all sizes - just scale the proportions.

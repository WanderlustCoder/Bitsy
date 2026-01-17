# Eyes Drawing Recipe

Eyes are the focal point of any character. Get them right and the whole character comes alive.

## Eye Anatomy (Simplified for Pixel Art)

From back to front:
1. **Sclera** (white) - the eye shape
2. **Iris** - colored circle, partially hidden by eyelids
3. **Pupil** - dark center
4. **Highlights** - reflections of light (makes eyes look alive)
5. **Upper shadow** - eyelid casts shadow on top of eye
6. **Lash hints** - at larger sizes only

## Size Guidelines

### Small (4-6px wide) - 32x32 characters
```python
# Just 2-3 pixels
canvas.set_pixel(ex, ey, iris_color)
canvas.set_pixel(ex, ey - 1, highlight_color)  # tiny highlight
```

### Medium (8-12px wide) - 64x64 characters
```python
# White, iris, pupil, one highlight
canvas.fill_ellipse(ex, ey, 5, 6, white)
canvas.fill_ellipse(ex + 1, ey + 1, 3, 4, iris_color)
canvas.fill_ellipse(ex + 1, ey + 2, 1, 1, pupil_color)
canvas.set_pixel(ex - 1, ey - 1, highlight_color)
```

### Large (14-20px wide) - 128x128 characters
Full detail: gradient iris, multiple highlights, lash hints.
See detailed recipe below.

## Large Eye Recipe (128x128)

```python
def draw_eye(canvas, cx, cy, width, height, iris_color, is_left=True):
    """
    Draw a detailed anime-style eye.

    cx, cy: center of eye
    width, height: eye dimensions
    iris_color: (r, g, b, a) base iris color
    is_left: True for left eye (affects highlight position)
    """

    # Derive colors
    white = (255, 255, 255, 255)
    iris_dark = darken(iris_color, 0.3)
    iris_light = lighten(iris_color, 0.2)
    pupil = (20, 15, 25, 255)
    highlight = (255, 255, 255, 255)
    shadow = (200, 190, 195, 255)  # slight purple tint

    rx, ry = width // 2, height // 2

    # --- Layer 1: Sclera (white of eye) ---
    canvas.fill_ellipse_aa(cx, cy, rx, ry, white)

    # --- Layer 2: Upper eyelid shadow ---
    # Top portion of eye is shadowed by lid
    shadow_points = [
        (cx - rx, cy),
        (cx - rx + 2, cy - ry + 2),
        (cx, cy - ry + 1),
        (cx + rx - 2, cy - ry + 2),
        (cx + rx, cy),
    ]
    # Draw as thin ellipse at top
    canvas.fill_ellipse(cx, cy - ry + 3, rx - 1, 4, shadow)

    # --- Layer 3: Iris ---
    iris_cx = cx + (1 if is_left else -1)  # slight offset toward center of face
    iris_cy = cy + 1  # slightly below center (looking slightly down)
    iris_rx = rx - 2
    iris_ry = ry - 1

    # Iris with gradient (darker at top, lighter at bottom)
    if hasattr(canvas, 'fill_ellipse_gradient'):
        canvas.fill_ellipse_gradient(iris_cx, iris_cy, iris_rx, iris_ry,
                                     iris_dark, iris_light, angle=90)
    else:
        canvas.fill_ellipse(iris_cx, iris_cy, iris_rx, iris_ry, iris_color)

    # Iris detail ring (darker ring inside)
    canvas.draw_circle_aa(iris_cx, iris_cy, iris_rx - 2, iris_dark)

    # --- Layer 4: Pupil ---
    pupil_r = max(2, iris_rx // 3)
    canvas.fill_ellipse(iris_cx, iris_cy + 1, pupil_r, pupil_r + 1, pupil)

    # --- Layer 5: Highlights ---
    # Primary highlight: large, top area, toward light source
    h1_x = cx - 2 if is_left else cx + 2
    h1_y = cy - ry // 2
    canvas.fill_ellipse(h1_x, h1_y, 3, 2, highlight)

    # Secondary highlight: small, opposite side, lower
    h2_x = cx + 2 if is_left else cx - 2
    h2_y = cy + ry // 3
    canvas.fill_ellipse(h2_x, h2_y, 1, 1, highlight)

    # --- Layer 6: Lash hints (for large eyes) ---
    if height >= 14:
        # Upper lash - slightly thicker line at top edge
        lash_color = (40, 30, 35, 255)
        # Draw as small triangular ticks at corners
        if is_left:
            canvas.draw_line(cx - rx, cy - 1, cx - rx + 2, cy - ry + 1, lash_color)
        else:
            canvas.draw_line(cx + rx, cy - 1, cx + rx - 2, cy - ry + 1, lash_color)
```

## Expression Variations

### Neutral
- Iris centered vertically
- Round pupil
- Standard highlights

### Happy/Smiling
- Eyes slightly closed (shorter height)
- Curved bottom edge (smile shape)
- Iris shifted up slightly
```python
# Happy eye - reduce height, curve bottom
happy_ry = normal_ry * 0.7
# Draw arc for bottom instead of full ellipse
```

### Sad
- Upper eyelid droops (more visible at top)
- Iris shifted down
- Highlights smaller or dimmer
- Inner eyebrow area down

### Surprised
- Eyes wider (increase height)
- Iris smaller relative to eye (more white visible)
- Pupil contracted (smaller)
- Highlights larger

### Angry
- Upper eyelid angled down toward center
- Iris shifted toward center
- Smaller highlights
- Eyebrow shadow more pronounced

## Iris Colors

### Brown Eyes
```python
iris_colors = [
    (70, 45, 35, 255),   # dark brown
    (100, 65, 50, 255),  # medium brown
    (140, 95, 70, 255),  # light brown/hazel
]
```

### Blue Eyes
```python
iris_colors = [
    (40, 70, 120, 255),  # dark blue
    (70, 110, 170, 255), # medium blue
    (100, 150, 200, 255),# light blue
]
```

### Green Eyes
```python
iris_colors = [
    (35, 80, 50, 255),   # dark green
    (60, 120, 70, 255),  # medium green
    (90, 160, 100, 255), # light green
]
```

### Anime-style (vivid)
```python
# More saturated, larger highlights
vivid_blue = (50, 100, 200, 255)
vivid_red = (180, 50, 60, 255)
vivid_purple = (140, 60, 160, 255)
```

## Eye Spacing and Position

From character_proportions.md:
```python
# Eye position
eye_y = head_cy - head_ry * 0.08  # slightly above center

# Eye spacing
eye_spacing = head_rx * 0.65  # distance between centers
left_eye_cx = head_cx - eye_spacing // 2
right_eye_cx = head_cx + eye_spacing // 2

# Eye size
eye_width = head_rx * 0.4   # each eye
eye_height = eye_width * 1.1  # slightly taller than wide
```

## Common Mistakes

| Problem | Cause | Fix |
|---------|-------|-----|
| Eyes look dead | No highlights or highlights too small | Add 2 highlights, make primary one 2-3px |
| Eyes look flat | No eyelid shadow | Add shadow at top of sclera |
| Eyes look creepy | Pupils too small or too large | Pupil should be ~1/3 of iris |
| Eyes don't match | Different sizes or positions | Use same values for both, mirror x-offset |
| Eyes look crossed | Irises pointing wrong way | Iris offset should be toward nose |

## Quick Reference Code

```python
def draw_simple_eyes(canvas, head_cx, head_cy, head_rx, head_ry, iris_color):
    """Quick eye drawing for 64-128px characters."""

    eye_y = head_cy - int(head_ry * 0.08)
    eye_spacing = int(head_rx * 0.65)
    eye_w = int(head_rx * 0.4)
    eye_h = int(eye_w * 1.1)

    left_cx = head_cx - eye_spacing // 2
    right_cx = head_cx + eye_spacing // 2

    for i, ex in enumerate([left_cx, right_cx]):
        is_left = (i == 0)

        # White
        canvas.fill_ellipse_aa(ex, eye_y, eye_w // 2, eye_h // 2, (255, 255, 255, 255))

        # Shadow at top
        canvas.fill_ellipse(ex, eye_y - eye_h // 3, eye_w // 2 - 1, 3, (210, 205, 210, 255))

        # Iris
        iris_x = ex + (1 if is_left else -1)
        canvas.fill_ellipse(iris_x, eye_y + 1, eye_w // 3, eye_h // 3, iris_color)

        # Pupil
        canvas.fill_ellipse(iris_x, eye_y + 2, 2, 2, (20, 15, 20, 255))

        # Primary highlight
        h_x = ex - 2 if is_left else ex + 2
        canvas.fill_ellipse(h_x, eye_y - 2, 2, 2, (255, 255, 255, 255))

        # Secondary highlight
        canvas.set_pixel(ex + (2 if is_left else -2), eye_y + 2, (255, 255, 255, 255))
```

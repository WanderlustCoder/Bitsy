# Face Details Recipe

Nose, mouth, ears, and blush - the subtle details that complete a face.

## General Principle

In chibi/anime pixel art, face details are **minimal**. Less is more.
- Nose: often just a shadow hint or 1-2 pixels
- Mouth: small, expressive
- Ears: usually hidden by hair
- Blush: soft, adds life

## Nose

### Minimal Nose (Most Common)
Just a shadow dot or small shadow shape below eyes.

```python
def draw_minimal_nose(canvas, head_cx, head_cy, head_ry, skin_shadow):
    """Tiny shadow-dot nose."""
    nose_y = head_cy + int(head_ry * 0.1)  # slightly below center

    # Just 1-2 pixels of shadow
    canvas.set_pixel(head_cx, nose_y, skin_shadow)
    canvas.set_pixel(head_cx, nose_y + 1, skin_shadow)
```

### Small Triangle Nose
Slightly more defined, good for semi-realistic styles.

```python
def draw_small_nose(canvas, head_cx, head_cy, head_ry, skin_shadow, skin_highlight):
    """Small triangular nose with highlight."""
    nose_y = head_cy + int(head_ry * 0.08)

    # Shadow side (right, since light from left)
    canvas.set_pixel(head_cx + 1, nose_y, skin_shadow)
    canvas.set_pixel(head_cx + 1, nose_y + 1, skin_shadow)
    canvas.set_pixel(head_cx, nose_y + 2, skin_shadow)  # tip

    # Highlight side (left)
    canvas.set_pixel(head_cx - 1, nose_y, skin_highlight)
```

### Side-View Nose
When character is turned slightly.

```python
def draw_side_nose(canvas, head_cx, head_cy, head_ry, skin_shadow, facing_left=True):
    """Nose visible in profile."""
    nose_y = head_cy + int(head_ry * 0.05)
    offset = -3 if facing_left else 3

    # Small bump shape
    points = [
        (head_cx + offset, nose_y - 2),
        (head_cx + offset + (2 if facing_left else -2), nose_y),
        (head_cx + offset, nose_y + 2),
    ]
    canvas.draw_bezier(points, skin_shadow, thickness=1)
```

## Mouth

### Neutral Mouth
Small, closed, relaxed expression.

```python
def draw_neutral_mouth(canvas, head_cx, head_cy, head_ry, mouth_color):
    """Simple neutral expression."""
    mouth_y = head_cy + int(head_ry * 0.28)
    mouth_width = 6

    # Simple horizontal line with slight curve
    canvas.draw_line(head_cx - mouth_width // 2, mouth_y,
                    head_cx + mouth_width // 2, mouth_y, mouth_color)
```

### Happy/Smile Mouth
Upward curve, can show as arc or "w" shape for cat-smile.

```python
def draw_smile_mouth(canvas, head_cx, head_cy, head_ry, mouth_color):
    """Happy smile."""
    mouth_y = head_cy + int(head_ry * 0.28)

    # Curved smile using bezier
    smile = [
        (head_cx - 5, mouth_y - 1),
        (head_cx, mouth_y + 3),
        (head_cx + 5, mouth_y - 1),
    ]
    canvas.draw_bezier(smile, mouth_color, thickness=1)
```

### Cat Smile (":3" style)
Anime/chibi staple.

```python
def draw_cat_smile(canvas, head_cx, head_cy, head_ry, mouth_color):
    """Cute cat-mouth smile."""
    mouth_y = head_cy + int(head_ry * 0.28)

    # "w" shape
    canvas.draw_line(head_cx - 4, mouth_y, head_cx - 1, mouth_y + 2, mouth_color)
    canvas.draw_line(head_cx - 1, mouth_y + 2, head_cx, mouth_y, mouth_color)
    canvas.draw_line(head_cx, mouth_y, head_cx + 1, mouth_y + 2, mouth_color)
    canvas.draw_line(head_cx + 1, mouth_y + 2, head_cx + 4, mouth_y, mouth_color)
```

### Open Mouth (Surprised/Talking)
Small oval or circle.

```python
def draw_open_mouth(canvas, head_cx, head_cy, head_ry, mouth_color, tongue_color=None):
    """Open mouth, surprised or talking."""
    mouth_y = head_cy + int(head_ry * 0.3)

    # Dark oval for open mouth
    canvas.fill_ellipse(head_cx, mouth_y, 4, 3, mouth_color)

    # Optional tongue hint
    if tongue_color:
        canvas.fill_ellipse(head_cx, mouth_y + 1, 2, 1, tongue_color)
```

### Sad/Frown Mouth
Downward curve.

```python
def draw_frown_mouth(canvas, head_cx, head_cy, head_ry, mouth_color):
    """Sad frown."""
    mouth_y = head_cy + int(head_ry * 0.28)

    frown = [
        (head_cx - 4, mouth_y + 1),
        (head_cx, mouth_y - 2),
        (head_cx + 4, mouth_y + 1),
    ]
    canvas.draw_bezier(frown, mouth_color, thickness=1)
```

## Blush

Adds warmth and life to a character. Essential for cute styles.

```python
def draw_blush(canvas, head_cx, head_cy, head_rx, head_ry, intensity=0.5):
    """
    Soft cheek blush.
    intensity: 0.0-1.0, affects color saturation
    """
    blush_y = head_cy + int(head_ry * 0.15)  # on cheeks
    blush_x_offset = int(head_rx * 0.45)     # toward edges

    # Blush color: pink/red with transparency based on intensity
    alpha = int(80 + intensity * 100)  # 80-180
    blush_color = (255, 150, 150, alpha)

    # Left cheek
    canvas.fill_ellipse(head_cx - blush_x_offset, blush_y, 8, 4, blush_color)

    # Right cheek
    canvas.fill_ellipse(head_cx + blush_x_offset, blush_y, 8, 4, blush_color)
```

### Blush Lines (Anime Style)
Diagonal lines instead of solid blush.

```python
def draw_blush_lines(canvas, head_cx, head_cy, head_rx, head_ry, blush_color):
    """Anime-style diagonal blush lines."""
    blush_y = head_cy + int(head_ry * 0.18)
    blush_x_offset = int(head_rx * 0.4)

    # 2-3 short diagonal lines per cheek
    for side in [-1, 1]:
        bx = head_cx + side * blush_x_offset
        for i in range(3):
            x = bx + i * 3 * side
            canvas.draw_line(x, blush_y - 1, x + 2 * side, blush_y + 2, blush_color)
```

## Ears

Usually hidden by hair, but when visible:

```python
def draw_ear(canvas, head_cx, head_cy, head_rx, head_ry, skin_base, skin_shadow, is_left=True):
    """
    Draw a visible ear (when hair doesn't cover it).
    """
    side = -1 if is_left else 1
    ear_x = head_cx + side * (head_rx - 2)
    ear_y = head_cy - int(head_ry * 0.1)  # align with eye level

    ear_w, ear_h = 6, 12

    # Ear shape
    canvas.fill_ellipse(ear_x + side * 3, ear_y, ear_w, ear_h, skin_base)

    # Inner ear shadow
    canvas.fill_ellipse(ear_x + side * 4, ear_y, ear_w - 3, ear_h - 4, skin_shadow)
```

## Mouth Colors

```python
# Lip/mouth colors
mouth_neutral = (180, 120, 120, 255)   # muted pink-brown
mouth_pink = (220, 140, 140, 255)      # pinker
mouth_dark = (120, 80, 80, 255)        # for open mouth interior

# Tongue (if visible)
tongue_color = (220, 150, 150, 255)
```

## Complete Face Details Function

```python
def draw_face_details(canvas, head_cx, head_cy, head_rx, head_ry,
                      skin_base, skin_shadow, skin_light,
                      expression='neutral', blush_intensity=0.3):
    """
    Draw nose, mouth, and blush based on expression.
    """
    mouth_color = (170, 110, 110, 255)

    # Nose (minimal for all expressions)
    nose_y = head_cy + int(head_ry * 0.1)
    canvas.set_pixel(head_cx, nose_y, skin_shadow)
    canvas.set_pixel(head_cx, nose_y + 1, skin_shadow)

    # Mouth based on expression
    mouth_y = head_cy + int(head_ry * 0.28)

    if expression == 'neutral':
        canvas.draw_line(head_cx - 3, mouth_y, head_cx + 3, mouth_y, mouth_color)

    elif expression == 'happy':
        smile = [
            (head_cx - 5, mouth_y - 1),
            (head_cx, mouth_y + 3),
            (head_cx + 5, mouth_y - 1),
        ]
        canvas.draw_bezier(smile, mouth_color, thickness=1)

    elif expression == 'sad':
        frown = [
            (head_cx - 4, mouth_y + 1),
            (head_cx, mouth_y - 2),
            (head_cx + 4, mouth_y + 1),
        ]
        canvas.draw_bezier(frown, mouth_color, thickness=1)

    elif expression == 'surprised':
        canvas.fill_ellipse(head_cx, mouth_y + 1, 3, 4, (100, 60, 60, 255))

    # Blush (adds life)
    if blush_intensity > 0:
        blush_y = head_cy + int(head_ry * 0.15)
        blush_x = int(head_rx * 0.45)
        alpha = int(60 + blush_intensity * 120)
        blush = (255, 150, 150, alpha)

        canvas.fill_ellipse(head_cx - blush_x, blush_y, 7, 4, blush)
        canvas.fill_ellipse(head_cx + blush_x, blush_y, 7, 4, blush)
```

## Position Reference

```
         forehead (hair covers)
              |
    ear -- [eyes] -- ear
              |
           (nose)  <- minimal, just shadow
              |
           [mouth] <- small, expressive
              |
           (blush) <- on cheeks, level with mouth
              |
            chin
```

## Common Mistakes

| Problem | Cause | Fix |
|---------|-------|-----|
| Face looks cluttered | Too much detail | Reduce nose/mouth size, simpler shapes |
| Nose dominates | Nose too large or dark | Use skin shadow color, 1-3 pixels max |
| Blush looks like injury | Too saturated or opaque | Lower alpha, use soft pink |
| Expression unclear | Mouth too small | Increase mouth width slightly |
| Face looks flat | No subtle shading | Add light nose highlight, mouth shadow |

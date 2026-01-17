# Glasses Recipe

Glasses add character and are a common accessory. They must sit naturally on the face.

## Placement Rules

Glasses sit:
- **Vertically**: Centered on eyes, bridge at nose level
- **Horizontally**: Frame outer edges align with or slightly beyond eye outer edges
- **Depth**: Drawn AFTER face, BEFORE front hair (so bangs can overlap slightly)

## Frame Types

### Round Glasses
Classic, cute, scholarly look.

```python
def draw_round_glasses(canvas, head_cx, head_cy, head_rx, head_ry,
                       frame_color, lens_color=None):
    """
    Round/circular frame glasses.
    lens_color: optional tint, None for clear
    """
    # Position: centered on eyes
    eye_y = head_cy - int(head_ry * 0.08)
    eye_spacing = int(head_rx * 0.65)

    left_cx = head_cx - eye_spacing // 2
    right_cx = head_cx + eye_spacing // 2

    lens_r = int(head_rx * 0.25)  # radius of each lens

    # Draw lenses (if tinted)
    if lens_color:
        canvas.fill_ellipse(left_cx, eye_y, lens_r, lens_r, lens_color)
        canvas.fill_ellipse(right_cx, eye_y, lens_r, lens_r, lens_color)

    # Draw frames
    canvas.draw_circle_aa(left_cx, eye_y, lens_r, frame_color)
    canvas.draw_circle_aa(right_cx, eye_y, lens_r, frame_color)

    # Bridge (connects lenses over nose)
    bridge_y = eye_y - 2
    canvas.draw_line(left_cx + lens_r - 1, bridge_y,
                    right_cx - lens_r + 1, bridge_y, frame_color)

    # Temples (arms going to ears) - just hints at edge
    temple_y = eye_y
    canvas.draw_line(left_cx - lens_r, temple_y,
                    left_cx - lens_r - 4, temple_y - 1, frame_color)
    canvas.draw_line(right_cx + lens_r, temple_y,
                    right_cx + lens_r + 4, temple_y - 1, frame_color)
```

### Rectangular Glasses
More serious, professional look.

```python
def draw_rectangular_glasses(canvas, head_cx, head_cy, head_rx, head_ry,
                             frame_color, lens_color=None):
    """Rectangular frame glasses."""
    eye_y = head_cy - int(head_ry * 0.08)
    eye_spacing = int(head_rx * 0.65)

    left_cx = head_cx - eye_spacing // 2
    right_cx = head_cx + eye_spacing // 2

    lens_w = int(head_rx * 0.28)
    lens_h = int(head_rx * 0.22)

    # Lens tint
    if lens_color:
        canvas.fill_rect(left_cx - lens_w, eye_y - lens_h,
                        lens_w * 2, lens_h * 2, lens_color)
        canvas.fill_rect(right_cx - lens_w, eye_y - lens_h,
                        lens_w * 2, lens_h * 2, lens_color)

    # Frame rectangles
    canvas.draw_rect(left_cx - lens_w, eye_y - lens_h,
                    lens_w * 2, lens_h * 2, frame_color)
    canvas.draw_rect(right_cx - lens_w, eye_y - lens_h,
                    lens_w * 2, lens_h * 2, frame_color)

    # Bridge
    canvas.draw_line(left_cx + lens_w, eye_y - 2,
                    right_cx - lens_w, eye_y - 2, frame_color)

    # Temples
    canvas.draw_line(left_cx - lens_w, eye_y,
                    left_cx - lens_w - 5, eye_y - 2, frame_color)
    canvas.draw_line(right_cx + lens_w, eye_y,
                    right_cx + lens_w + 5, eye_y - 2, frame_color)
```

### Cat-Eye Glasses
Stylish, retro, often feminine.

```python
def draw_cateye_glasses(canvas, head_cx, head_cy, head_rx, head_ry,
                        frame_color, lens_color=None):
    """Cat-eye frame glasses with upswept corners."""
    eye_y = head_cy - int(head_ry * 0.08)
    eye_spacing = int(head_rx * 0.65)

    left_cx = head_cx - eye_spacing // 2
    right_cx = head_cx + eye_spacing // 2

    lens_w = int(head_rx * 0.26)
    lens_h = int(head_rx * 0.2)

    for cx, is_left in [(left_cx, True), (right_cx, False)]:
        # Cat-eye shape: rectangle with upswept outer corners
        flip = -1 if is_left else 1

        # Main lens area
        if lens_color:
            canvas.fill_rect(cx - lens_w, eye_y - lens_h,
                           lens_w * 2, lens_h * 2, lens_color)

        # Frame with upswept corner
        # Bottom
        canvas.draw_line(cx - lens_w, eye_y + lens_h,
                        cx + lens_w, eye_y + lens_h, frame_color)
        # Inner side
        canvas.draw_line(cx - lens_w * flip, eye_y - lens_h,
                        cx - lens_w * flip, eye_y + lens_h, frame_color)
        # Top with uptick
        canvas.draw_line(cx - lens_w * flip, eye_y - lens_h,
                        cx + lens_w * flip, eye_y - lens_h, frame_color)
        # Upswept outer corner
        canvas.draw_line(cx + lens_w * flip, eye_y - lens_h,
                        cx + lens_w * flip + 3 * flip, eye_y - lens_h - 3, frame_color)
        # Outer side
        canvas.draw_line(cx + lens_w * flip, eye_y + lens_h,
                        cx + lens_w * flip + 3 * flip, eye_y - lens_h - 3, frame_color)

    # Bridge
    canvas.draw_line(left_cx + lens_w, eye_y - 1,
                    right_cx - lens_w, eye_y - 1, frame_color)
```

## Lens Effects

### Clear Lenses
No fill, just frames. Most common.

### Tinted Lenses
Slight color overlay.
```python
# Light tint (semi-transparent)
lens_tint = (200, 220, 255, 40)  # slight blue
lens_tint = (255, 220, 200, 40)  # slight warm
```

### Reflective/Glare
Add small highlight to suggest glass reflection.

```python
def add_lens_glare(canvas, lens_cx, lens_cy, lens_r):
    """Add reflection glare to lens."""
    # Small white highlight, top-left (toward light)
    glare_x = lens_cx - lens_r // 2
    glare_y = lens_cy - lens_r // 2

    canvas.fill_ellipse(glare_x, glare_y, 2, 1, (255, 255, 255, 180))
```

## Frame Colors

```python
# Common frame colors
black_frame = (30, 25, 35, 255)      # classic
brown_frame = (90, 60, 45, 255)      # tortoiseshell base
gold_frame = (180, 150, 80, 255)     # wire rim
silver_frame = (160, 165, 175, 255)  # wire rim
red_frame = (150, 50, 50, 255)       # statement
```

## Tortoiseshell Pattern

For detailed frames at larger sizes:

```python
def draw_tortoiseshell_frame(canvas, cx, cy, r, base_color):
    """Tortoiseshell pattern on round frame."""
    # Draw base frame
    canvas.draw_circle_aa(cx, cy, r, base_color)

    # Add darker spots
    dark_spots = (60, 35, 25, 255)
    # Randomly place 3-5 small darker areas on frame
    import random
    for _ in range(4):
        angle = random.uniform(0, 6.28)
        px = cx + int(r * 0.9 * math.cos(angle))
        py = cy + int(r * 0.9 * math.sin(angle))
        canvas.set_pixel(px, py, dark_spots)
```

## Complete Glasses Function

```python
def draw_glasses(canvas, head_cx, head_cy, head_rx, head_ry,
                 style='round', frame_color=(30, 25, 35, 255),
                 lens_tint=None, add_glare=True):
    """
    Draw glasses on a character face.

    style: 'round', 'rectangular', 'cateye'
    frame_color: (r, g, b, a)
    lens_tint: optional (r, g, b, a) for tinted lenses
    add_glare: whether to add reflection highlights
    """
    eye_y = head_cy - int(head_ry * 0.08)
    eye_spacing = int(head_rx * 0.65)

    left_cx = head_cx - eye_spacing // 2
    right_cx = head_cx + eye_spacing // 2

    if style == 'round':
        lens_r = int(head_rx * 0.25)

        # Lenses
        if lens_tint:
            canvas.fill_ellipse(left_cx, eye_y, lens_r, lens_r, lens_tint)
            canvas.fill_ellipse(right_cx, eye_y, lens_r, lens_r, lens_tint)

        # Frames
        canvas.draw_circle_aa(left_cx, eye_y, lens_r, frame_color)
        canvas.draw_circle_aa(right_cx, eye_y, lens_r, frame_color)

        # Bridge
        canvas.draw_line(left_cx + lens_r - 1, eye_y - 2,
                        right_cx - lens_r + 1, eye_y - 2, frame_color)

        # Temple hints
        canvas.draw_line(left_cx - lens_r, eye_y,
                        left_cx - lens_r - 4, eye_y - 1, frame_color)
        canvas.draw_line(right_cx + lens_r, eye_y,
                        right_cx + lens_r + 4, eye_y - 1, frame_color)

        # Glare
        if add_glare:
            for cx in [left_cx, right_cx]:
                gx = cx - lens_r // 3
                gy = eye_y - lens_r // 3
                canvas.fill_ellipse(gx, gy, 2, 1, (255, 255, 255, 150))

    elif style == 'rectangular':
        lens_w = int(head_rx * 0.26)
        lens_h = int(head_rx * 0.2)

        for cx in [left_cx, right_cx]:
            if lens_tint:
                canvas.fill_rect(cx - lens_w, eye_y - lens_h,
                               lens_w * 2, lens_h * 2, lens_tint)
            canvas.draw_rect(cx - lens_w, eye_y - lens_h,
                           lens_w * 2, lens_h * 2, frame_color)

        canvas.draw_line(left_cx + lens_w, eye_y - 1,
                        right_cx - lens_w, eye_y - 1, frame_color)

    # (cateye implementation similar)
```

## Layer Order with Glasses

```
1. Back hair
2. Head/face
3. Eyes
4. Nose, mouth, blush
5. GLASSES  <-- here
6. Front hair (bangs can overlap glasses slightly)
```

## Common Mistakes

| Problem | Cause | Fix |
|---------|-------|-----|
| Glasses float above eyes | Wrong y position | Use eye_y from proportions |
| Frames too thick | Multiple draw calls or thick lines | Single-pixel frame lines |
| Lenses look opaque | Lens tint alpha too high | Use alpha 30-60 for tint |
| Bridge too long/short | Wrong spacing calculation | Bridge connects inner lens edges |
| Temples look wrong | Going wrong direction | Temples go toward ears (outward and slightly up) |

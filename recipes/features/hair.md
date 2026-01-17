# Hair Drawing Recipe

How to draw pixel art hair that looks professional.

## Core Principle

Hair is NOT individual strands. Hair is **masses with suggested strands**.

At pixel art resolution, you're drawing:
1. Solid color masses (the bulk of the hair)
2. A few strategic strand lines (suggesting texture)
3. Highlights (showing shine/form)
4. Edge detail (where hair meets face/air)

## The Three-Layer Approach

### Layer 1: Mass Shapes
Solid filled shapes defining the overall hair silhouette.

```python
# Back hair mass - extends beyond head
canvas.fill_ellipse(head_cx, head_cy + 5,
                   head_rx + 15, head_ry + 10, shadow_color)
canvas.fill_ellipse(head_cx, head_cy,
                   head_rx + 12, head_ry + 5, base_color)
```

### Layer 2: Gradient Shading
Add depth with directional gradients following hair flow.

```python
# Gradient from highlight side to shadow side
canvas.fill_ellipse_gradient(head_cx, head_cy,
                            head_rx + 10, head_ry,
                            light_color, shadow_color,
                            angle=-45)  # light from top-left
```

### Layer 3: Strand Suggestions
A FEW strategic strands, not hundreds.

```python
# 5-8 strands is usually enough
# Place at: edges, part lines, and flow direction changes
strands = [
    # Each strand: start point, control point, end point
    [(cx-20, top_y), (cx-25, mid_y), (cx-22, bottom_y)],  # left edge
    [(cx-10, top_y), (cx-12, mid_y), (cx-8, bottom_y)],   # left-center
    [(cx, top_y), (cx+2, mid_y), (cx, bottom_y)],         # center
    # ... etc
]

for strand in strands:
    # Dark strand (shadow side)
    canvas.draw_bezier_tapered(strand, dark_color, 2.0, 0.5)
    # Light strand (highlight side) - offset toward light
    light_strand = [(p[0]-1, p[1]-1) for p in strand]
    canvas.draw_bezier_tapered(light_strand, light_color, 1.0, 0.3)
```

## Hair Flow Directions

Hair flows based on style and gravity:

### Straight Down (Long Hair)
```
Start: top of head
Control: slight outward curve
End: below shoulders

Strands curve OUTWARD slightly (hair has volume)
```

### Bun
```
Back strands: flow UP into bun
Bun surface: circular/spiral flow
Loose pieces: flow DOWN from bun
```

### Bangs
```
Start: hairline (forehead)
Flow: down and OUTWARD toward temples
End: just above or beside eyes

Bangs frame the face - curve away from center
```

## Highlight Placement

Hair highlights follow the "shine band" - a curved line where light reflects.

```python
# Main highlight: upper portion, offset toward light source
highlight_y = hair_top_y + hair_height * 0.25
highlight_cx = head_cx - 5  # offset toward light (top-left)

# Draw as soft ellipse or curved band
canvas.fill_ellipse_radial_gradient(
    highlight_cx, highlight_y,
    highlight_rx, highlight_ry,
    highlight_color, base_color  # fades into base
)
```

Secondary highlights:
- Rim light on shadow side (subtle, shows form)
- Small specular spots (1-2 pixels, brightest white-ish)

## Bun Recipe (Step by Step)

```python
def draw_bun_hair(canvas, head_cx, head_cy, head_rx, head_ry, colors):
    """
    colors: [darkest, shadow, base, light, highlight]
    """
    darkest, shadow, base, light, highlight = colors

    # --- BACK LAYER (behind head) ---

    # Back hair mass - visible on sides and bottom
    # Wider than head, creates frame
    back_rx = head_rx + 12
    back_ry = head_ry + 8

    canvas.fill_ellipse(head_cx, head_cy + 5, back_rx, back_ry, darkest)
    canvas.fill_ellipse(head_cx, head_cy + 2, back_rx - 3, back_ry - 3, shadow)

    # Side pieces that hang down (frame the face)
    # LEFT side
    left_x = head_cx - head_rx - 5
    canvas.fill_ellipse(left_x, head_cy + 15, 8, 25, shadow)
    canvas.fill_ellipse(left_x + 1, head_cy + 14, 6, 22, base)

    # RIGHT side
    right_x = head_cx + head_rx + 5
    canvas.fill_ellipse(right_x, head_cy + 15, 8, 25, shadow)
    canvas.fill_ellipse(right_x - 1, head_cy + 14, 6, 22, base)

    # --- HEAD GOES HERE (drawn by caller) ---

    # --- BUN (on top of head) ---
    bun_cx = head_cx
    bun_cy = head_cy - head_ry - 8  # above head
    bun_r = 18

    # Bun shadow (bottom)
    canvas.fill_ellipse(bun_cx + 2, bun_cy + 3, bun_r, bun_r - 2, darkest)
    # Bun main
    canvas.fill_ellipse(bun_cx, bun_cy, bun_r, bun_r - 2, base)
    # Bun highlight (top-left)
    canvas.fill_ellipse(bun_cx - 4, bun_cy - 4, bun_r // 2, bun_r // 3, light)

    # Bun wrap strands (suggest spiral)
    wrap_strands = [
        [(bun_cx - 15, bun_cy), (bun_cx, bun_cy - 12), (bun_cx + 15, bun_cy)],
        [(bun_cx - 12, bun_cy + 5), (bun_cx, bun_cy + 10), (bun_cx + 12, bun_cy + 5)],
    ]
    for strand in wrap_strands:
        canvas.draw_bezier_tapered(strand, shadow, 1.5, 0.5)

    # --- FRONT LAYER (bangs) ---
    bangs_y_start = head_cy - head_ry + 5
    bangs_y_end = head_cy - head_ry * 0.3

    # Bangs mass (covers forehead)
    canvas.fill_ellipse(head_cx, bangs_y_start + 8, head_rx - 5, 15, base)
    canvas.fill_ellipse(head_cx - 3, bangs_y_start + 6, head_rx - 8, 12, light)

    # Bang strands
    bang_strands = [
        [(head_cx - 18, bangs_y_start), (head_cx - 22, bangs_y_end - 10), (head_cx - 20, bangs_y_end + 5)],
        [(head_cx - 8, bangs_y_start - 3), (head_cx - 10, bangs_y_end - 12), (head_cx - 6, bangs_y_end + 3)],
        [(head_cx + 2, bangs_y_start - 5), (head_cx, bangs_y_end - 15), (head_cx + 4, bangs_y_end)],
        [(head_cx + 12, bangs_y_start - 3), (head_cx + 14, bangs_y_end - 12), (head_cx + 16, bangs_y_end + 3)],
        [(head_cx + 22, bangs_y_start), (head_cx + 26, bangs_y_end - 10), (head_cx + 24, bangs_y_end + 5)],
    ]

    for strand in bang_strands:
        canvas.draw_bezier_tapered(strand, shadow, 2.0, 0.5)
        light_strand = [(p[0] - 1, p[1] - 1) for p in strand]
        canvas.draw_bezier_tapered(light_strand, light, 1.0, 0.3)
```

## Bob Hair Recipe (with flip)

Learned from: princess portrait recreation (portrait_princess.png)

The bob hairstyle has three distinct zones:
1. **Dome top** - rounded, starts narrow, expands
2. **Straight sides** - constant width past the face
3. **Flip ends** - subtle outward curve at the bottom

```python
def draw_bob_hair(canvas, head_cx, head_cy, head_rx, head_ry, colors, flip_amount=5):
    """
    Bob hairstyle with characteristic flip at the ends.

    flip_amount: how much the ends curve outward (0 = straight, 10 = dramatic)
    colors: [shadow, base, light, highlight]
    """
    shadow, base, light, highlight = colors

    hair_top = head_cy - head_ry - 5
    hair_bottom = head_cy + head_ry * 0.6  # Ends below chin
    hair_height = hair_bottom - hair_top

    # --- MAIN HAIR MASS ---
    # Draw row by row for precise shape control
    for y in range(int(hair_top), int(hair_bottom) + 1):
        rel = (y - hair_top) / hair_height  # 0 at top, 1 at bottom

        if rel < 0.25:
            # Zone 1: Dome top - starts narrow, expands
            t = rel / 0.25  # normalize to 0-1 within this zone
            half_width = int(head_rx * 0.4 + t * head_rx * 0.8)
        elif rel < 0.75:
            # Zone 2: Straight sides - constant width
            half_width = int(head_rx * 1.2)
        else:
            # Zone 3: Flip ends - subtle outward curve
            t = (rel - 0.75) / 0.25  # normalize to 0-1
            half_width = int(head_rx * 1.2 + t * flip_amount)

        canvas.draw_line(head_cx - half_width, y, head_cx + half_width, y, base)

    # --- HIGHLIGHT STRIPE ---
    # Single horizontal highlight band across top of dome
    highlight_y = hair_top + hair_height * 0.1
    for i in range(4):
        hw = head_rx - i * 3
        if hw > 0:
            canvas.draw_line(head_cx - hw, int(highlight_y) + i,
                           head_cx + hw, int(highlight_y) + i, highlight)

    # --- SHADOW EDGES ---
    # Darken the outer edges for depth
    for y in range(int(hair_top + hair_height * 0.3), int(hair_bottom)):
        rel = (y - hair_top) / hair_height
        if rel < 0.75:
            half_width = int(head_rx * 1.2)
        else:
            t = (rel - 0.75) / 0.25
            half_width = int(head_rx * 1.2 + t * flip_amount)

        # Left edge shadow
        canvas.draw_line(head_cx - half_width, y, head_cx - half_width + 2, y, shadow)
        # Right edge shadow
        canvas.draw_line(head_cx + half_width - 2, y, head_cx + half_width, y, shadow)


def draw_bob_bangs(canvas, head_cx, head_cy, head_rx, head_ry, colors, style='zigzag'):
    """
    Bangs for bob hairstyle.

    style: 'zigzag' (notched), 'straight', 'side_swept'
    """
    shadow, base, light, highlight = colors

    bang_top = head_cy - head_ry + 2
    bang_bottom = head_cy - head_ry * 0.4
    bang_width = head_rx * 0.9

    if style == 'zigzag':
        # Notched bangs - creates cute look
        for x in range(int(head_cx - bang_width), int(head_cx + bang_width) + 1):
            # Create notch pattern every N pixels
            notch = (abs(x - head_cx) % 8 < 3)
            top_y = bang_top + (4 if notch else 0)
            height = int(bang_bottom - bang_top) - (4 if notch else 0)

            for dy in range(height):
                canvas.set_pixel(x, int(top_y) + dy, base)

    elif style == 'straight':
        # Simple straight bangs
        canvas.fill_rect(int(head_cx - bang_width), int(bang_top),
                        int(bang_width * 2), int(bang_bottom - bang_top), base)

    elif style == 'side_swept':
        # Angled bangs
        for x in range(int(head_cx - bang_width), int(head_cx + bang_width) + 1):
            offset = (x - head_cx) * 0.3  # Angle factor
            top_y = bang_top + offset
            height = bang_bottom - top_y
            for dy in range(int(height)):
                canvas.set_pixel(x, int(top_y) + dy, base)
```

### Bob Color Palettes

```python
# Princess blonde (from portrait_princess.png)
princess_blonde = [
    (180, 145, 60),   # shadow
    (235, 195, 90),   # base
    (255, 220, 130),  # light
    (255, 235, 150),  # highlight
]

# Chestnut bob
chestnut_bob = [
    (60, 40, 35),
    (100, 70, 55),
    (140, 100, 75),
    (180, 140, 110),
]

# Black bob (blue undertones)
black_bob = [
    (15, 15, 25),
    (35, 35, 50),
    (55, 55, 75),
    (90, 85, 110),
]
```

## Long Hair Recipe

```python
def draw_long_hair(canvas, head_cx, head_cy, head_rx, head_ry, colors, length_factor=1.5):
    """
    length_factor: 1.0 = shoulder length, 2.0 = very long
    """
    darkest, shadow, base, light, highlight = colors

    hair_bottom = head_cy + head_ry * length_factor

    # --- BACK MASS ---
    # Main back shape - tapers toward bottom
    back_points = [
        (head_cx - head_rx - 10, head_cy - head_ry * 0.3),  # top left
        (head_cx - head_rx - 15, head_cy + head_ry * 0.5),  # mid left (widest)
        (head_cx - 10, hair_bottom),                         # bottom left
        (head_cx + 10, hair_bottom),                         # bottom right
        (head_cx + head_rx + 15, head_cy + head_ry * 0.5),  # mid right
        (head_cx + head_rx + 10, head_cy - head_ry * 0.3),  # top right
    ]
    canvas.fill_polygon(back_points, shadow)

    # Inner gradient layer
    canvas.fill_ellipse_gradient(
        head_cx, head_cy + head_ry * 0.3,
        head_rx + 10, head_ry * length_factor * 0.6,
        light, darkest, angle=-30
    )

    # --- STRAND LINES ---
    strand_count = 7
    for i in range(strand_count):
        t = i / (strand_count - 1)  # 0 to 1
        x_offset = (t - 0.5) * (head_rx * 2 + 15)

        strand = [
            (head_cx + x_offset * 0.8, head_cy - head_ry * 0.4),
            (head_cx + x_offset * 1.1, head_cy + head_ry * 0.3),
            (head_cx + x_offset * 0.95, hair_bottom - 5),
        ]

        canvas.draw_bezier_tapered(strand, darkest, 2.0, 0.5)

        if i % 2 == 0:  # highlight on alternating strands
            light_strand = [(p[0] - 1, p[1] - 1) for p in strand]
            canvas.draw_bezier_tapered(light_strand, light, 1.0, 0.3)

    # --- HEAD GOES HERE ---

    # --- BANGS (front layer) ---
    # Similar to bun recipe bangs
```

## Common Hair Colors

### Brown Ramps
```python
light_brown = [(50, 35, 30), (80, 55, 45), (115, 80, 60), (150, 110, 85), (190, 150, 120)]
dark_brown = [(35, 25, 25), (55, 40, 35), (85, 60, 50), (120, 90, 70), (160, 125, 100)]
```

### Black Hair (not pure black - has blue/purple tint)
```python
black_hair = [(20, 20, 30), (35, 35, 50), (55, 50, 65), (80, 75, 95), (120, 110, 135)]
```

### Blonde
```python
blonde = [(140, 100, 50), (180, 140, 70), (210, 175, 100), (235, 205, 140), (250, 235, 190)]
```

### Red/Auburn
```python
auburn = [(60, 25, 20), (100, 45, 35), (145, 65, 45), (180, 95, 65), (210, 140, 100)]
```

## Debugging Hair Issues

| Problem | Cause | Fix |
|---------|-------|-----|
| Hair looks flat | No gradient/highlights | Add Layer 2 gradient shading |
| Hair looks stringy | Too many strand lines | Reduce strands, emphasize masses |
| Hair floats off head | Wrong positioning | Check proportions recipe, anchor to head |
| Hair doesn't frame face | Side pieces missing | Add side hair that hangs beside face |
| Bun looks like blob | No wrap detail | Add 2-3 curved strands on bun surface |

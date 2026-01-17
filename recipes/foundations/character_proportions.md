# Character Proportions

How to lay out a character so all parts fit together naturally.

## Head-Based Units

Chibi/cute pixel art uses **2-3 head tall** proportions:
- Head: 1 unit
- Body: 1-2 units
- Total: 2-3 heads tall

## Canvas Layout (Portrait/Bust)

For a character portrait in a square canvas:

```
Canvas: W x H

Head center: (W/2, H * 0.42)
Head width: W * 0.55
Head height: H * 0.65

Bun/top hair: above head center by head_height * 0.5
Shoulders: below head center by head_height * 0.45
```

### 128x128 Portrait Example
```python
cx, cy = 64, 54          # head center
head_w, head_h = 70, 83  # head dimensions

# Key anchor points
forehead_y = cy - head_h // 2      # ~12
chin_y = cy + head_h // 2          # ~95
left_cheek_x = cx - head_w // 2    # ~29
right_cheek_x = cx + head_w // 2   # ~99

# Feature placement (relative to head)
eye_y = cy - head_h * 0.08         # slightly above center
eye_spacing = head_w * 0.32        # distance between eye centers
nose_y = cy + head_h * 0.12        # below center
mouth_y = cy + head_h * 0.25       # below nose
```

## Feature Proportions

### Eyes
- Width: head_width * 0.18-0.25 (larger = cuter)
- Height: eye_width * 0.8-1.2
- Spacing: one eye-width between eyes
- Position: slightly above head center (creates youthful look)

### Nose
- Minimal in chibi style: 2-4 pixels wide
- Position: between eyes and mouth
- Often just shadow hint, not full shape

### Mouth
- Width: varies by expression (head_width * 0.15-0.3)
- Position: 1/4 down from center to chin
- Small in neutral expression

### Ears
- Usually hidden by hair
- If visible: align top with eye level, bottom with nose

## Hair Boundaries

Hair should FRAME the face, extending beyond head bounds:

```python
# Hair extends beyond head ellipse
hair_back_width = head_w * 1.15    # wider than head
hair_back_height = head_h * 1.1    # taller than head

# Side hair falls alongside face
side_hair_x_offset = head_w * 0.5 + 5  # just outside face
side_hair_length = head_h * 0.6

# Bangs cover forehead
bangs_y_start = forehead_y - 5     # above hairline
bangs_y_end = eye_y - 3            # just above eyes
```

## Layering Depth Order

From back to front:
1. Back hair (behind head)
2. Ears (if visible)
3. Head/face base
4. Face features (eyes, nose, mouth)
5. Glasses/accessories on face
6. Front hair (bangs, side pieces)
7. Top accessories (bun, bow, hat)

## Coordinate System

```
(0,0) ----→ X increases
  |
  |
  ↓
  Y increases
```

- **Top-left origin**
- X increases rightward
- Y increases downward
- Center of canvas: (width/2, height/2)

## Quick Reference: 128x128 Character

```python
# Canvas
W, H = 128, 128

# Head
head_cx, head_cy = 64, 54
head_rx, head_ry = 35, 42  # ellipse radii

# Eyes (two eyes)
eye_y = 50
left_eye_cx = 52
right_eye_cx = 76
eye_rx, eye_ry = 8, 9

# Hair regions
hair_back_y = 54           # same as head
bun_cx, bun_cy = 64, 15    # top of head
bangs_y_end = 42           # above eyes
side_hair_start_y = 35
side_hair_end_y = 95

# Body (if visible)
neck_y = 96
shoulder_y = 105
shoulder_width = 80
```

"""
High-res recreation of portrait_princess.png - Iteration 6
Hair as connected bob with outward curve at sides
"""
import sys
sys.path.insert(0, '/mnt/c/Users/Werem/Projects/bitsy')

from core.canvas import Canvas

def rgba(color):
    if len(color) == 4:
        return color
    return (*color, 255)

canvas = Canvas(128, 128)

# === COLORS ===
FRAME_OUTER = rgba((50, 30, 65))
FRAME_DARK = rgba((85, 50, 100))
FRAME_MID = rgba((130, 75, 150))
FRAME_LIGHT = rgba((165, 105, 180))

GOLD = rgba((230, 195, 65))
GOLD_LIGHT = rgba((255, 235, 120))

BG = rgba((235, 200, 75))

SKIN = rgba((255, 220, 190))
SKIN_BLUSH = rgba((255, 150, 170))

HAIR = rgba((235, 195, 90))
HAIR_LIGHT = rgba((255, 235, 150))

EYE = rgba((30, 30, 40))
MOUTH = rgba((190, 120, 120))

DRESS_LIGHT = rgba((165, 105, 180))
DRESS_MID = rgba((130, 80, 155))
DRESS_DARK = rgba((95, 55, 115))

# === FRAME ===
canvas.fill_rect(0, 0, 128, 128, FRAME_OUTER)
canvas.fill_rect(4, 4, 120, 120, FRAME_DARK)
canvas.fill_rect(8, 8, 112, 112, FRAME_MID)
canvas.fill_rect(12, 12, 104, 104, FRAME_LIGHT)

# === GOLD CORNERS ===
def draw_corner(ox, oy, dx, dy):
    size = 18
    for row in range(size):
        for col in range(size - row):
            x = ox + col * dx
            y = oy + row * dy
            if col + row < 5:
                canvas.set_pixel(x, y, GOLD_LIGHT)
            else:
                canvas.set_pixel(x, y, GOLD)

draw_corner(4, 4, 1, 1)
draw_corner(123, 4, -1, 1)
draw_corner(4, 123, 1, -1)
draw_corner(123, 123, -1, -1)

# === BACKGROUND ===
inner = 16
canvas.fill_rect(inner, inner, 128 - inner*2, 128 - inner*2, BG)
canvas.draw_rect(inner, inner, 128 - inner*2, 128 - inner*2, FRAME_DARK)

# === CHARACTER ===
cx, cy = 64, 48

# --- HAIR (connected bob with subtle flip at ends) ---
hair_top = cy - 18
hair_bottom = cy + 14

# Draw hair row by row
for y in range(hair_top, hair_bottom + 1):
    rel = (y - hair_top) / (hair_bottom - hair_top)

    # Dome shape at top, then straight sides, then subtle flip
    if rel < 0.25:
        # Top dome
        base_w = int(14 + rel * 100)
    elif rel < 0.75:
        # Straight sides - constant width
        base_w = 38
    else:
        # Subtle flip at bottom
        base_w = 38 + int((rel - 0.75) * 20)

    canvas.draw_line(cx - base_w, y, cx + base_w, y, HAIR)

# Hair top highlight
for i in range(5):
    hw = 18 - i * 3
    if hw > 0:
        canvas.draw_line(cx - hw, hair_top + 2 + i, cx + hw, hair_top + 2 + i, HAIR_LIGHT)

# --- FACE ---
face_cy = cy + 6
canvas.fill_ellipse(cx, face_cy, 18, 20, SKIN)

# --- EYES ---
eye_y = face_cy - 2
eye_size = 5
canvas.fill_rect(cx - 12, eye_y - eye_size//2, eye_size, eye_size, EYE)
canvas.fill_rect(cx + 7, eye_y - eye_size//2, eye_size, eye_size, EYE)

# Eye highlights
canvas.fill_rect(cx - 11, eye_y - 2, 2, 2, rgba((255, 255, 255)))
canvas.fill_rect(cx + 8, eye_y - 2, 2, 2, rgba((255, 255, 255)))

# --- BLUSH ---
canvas.fill_ellipse(cx - 14, face_cy + 7, 5, 3, SKIN_BLUSH)
canvas.fill_ellipse(cx + 14, face_cy + 7, 5, 3, SKIN_BLUSH)

# --- MOUTH ---
canvas.draw_line(cx - 2, face_cy + 12, cx + 2, face_cy + 12, MOUTH)

# --- BANGS ---
bang_y = hair_top + 5
for x in range(cx - 18, cx + 19):
    notch = (abs(x - cx) % 8 < 3)
    by = bang_y + (4 if notch else 0)
    h = 14 - (4 if notch else 0)
    for dy in range(h):
        canvas.set_pixel(x, by + dy, HAIR)

# --- DRESS ---
dress_top = cy + 22
tier_h = 14

space = 128 - inner - dress_top - 2
num_tiers = max(1, space // tier_h)

for t in range(num_tiers):
    tier_y = dress_top + t * tier_h
    base_w = 30 + t * 16

    if t == 0:
        color = DRESS_LIGHT
    elif t == 1:
        color = DRESS_MID
    else:
        color = DRESS_DARK

    for row in range(tier_h):
        if tier_y + row >= 128 - inner:
            break
        w = base_w + row
        canvas.draw_line(cx - w, tier_y + row, cx + w, tier_y + row, color)

# Neckline
canvas.draw_line(cx - 16, dress_top - 2, cx + 16, dress_top - 2, DRESS_LIGHT)
canvas.draw_line(cx - 12, dress_top - 1, cx + 12, dress_top - 1, SKIN)

# === SAVE ===
canvas.save('output/princess_portrait_hires.png')
print("Saved: output/princess_portrait_hires.png")

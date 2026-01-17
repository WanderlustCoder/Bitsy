"""
Test: Generate a portrait using the learned recipes.

This demonstrates the learning loop:
1. We tried to recreate portrait_princess.png
2. We learned patterns (bob hair, frames, palettes, composition)
3. We encoded those into recipes
4. Now we can generate similar portraits programmatically

Recipes used:
- recipes/features/hair.md (bob style)
- recipes/frames/portrait.md (layered frame with corners)
- recipes/palettes.yaml (princess palette)
- recipes/compositions/portrait.md (portrait layout)
"""
import sys
sys.path.insert(0, '/mnt/c/Users/Werem/Projects/bitsy')

from core.canvas import Canvas

def rgba(color):
    """Ensure color is RGBA format."""
    if len(color) == 4:
        return color
    return (*color, 255)


# ============================================================
# PALETTE (from recipes/palettes.yaml - princess theme)
# ============================================================
PALETTE = {
    'frame': [
        rgba((50, 30, 65)),
        rgba((85, 50, 100)),
        rgba((130, 75, 150)),
        rgba((165, 105, 180)),
    ],
    'accent': {
        'main': rgba((230, 195, 65)),
        'highlight': rgba((255, 235, 120)),
    },
    'background': rgba((235, 200, 75)),
    'skin': {
        'base': rgba((255, 220, 190)),
        'blush': rgba((255, 150, 170)),
    },
    'hair': {
        'shadow': rgba((180, 145, 60)),
        'base': rgba((235, 195, 90)),
        'light': rgba((255, 220, 130)),
        'highlight': rgba((255, 235, 150)),
    },
    'clothing': [
        rgba((165, 105, 180)),
        rgba((130, 80, 155)),
        rgba((95, 55, 115)),
    ],
    'eyes': rgba((30, 30, 40)),
    'mouth': rgba((190, 120, 120)),
}


# ============================================================
# FRAME (from recipes/frames/portrait.md)
# ============================================================
def draw_portrait_frame(canvas, width, height, palette):
    """Draw layered frame with corner triangles."""
    # Frame bands
    offset = 0
    band_width = 4
    for color in palette['frame']:
        canvas.fill_rect(offset, offset, width - offset*2, height - offset*2, color)
        offset += band_width

    # Corner triangles
    corner_size = 18
    corners = [
        (offset, offset, 1, 1),          # Top-left
        (width - offset - 1, offset, -1, 1),     # Top-right
        (offset, height - offset - 1, 1, -1),    # Bottom-left
        (width - offset - 1, height - offset - 1, -1, -1),  # Bottom-right
    ]

    for ox, oy, dx, dy in corners:
        for row in range(corner_size):
            for col in range(corner_size - row):
                x = ox + col * dx
                y = oy + row * dy
                color = palette['accent']['highlight'] if col + row < 5 else palette['accent']['main']
                canvas.set_pixel(x, y, color)

    # Background
    inner = offset
    canvas.fill_rect(inner, inner, width - inner*2, height - inner*2, palette['background'])
    canvas.draw_rect(inner, inner, width - inner*2, height - inner*2, palette['frame'][1])

    return inner  # Return content offset


# ============================================================
# HAIR (from recipes/features/hair.md - bob style)
# ============================================================
def draw_bob_hair(canvas, cx, cy, palette, flip_amount=5):
    """Bob hair with dome top, straight sides, flip ends."""
    hair_top = cy - 18
    hair_bottom = cy + 14
    hair_height = hair_bottom - hair_top

    colors = palette['hair']

    # Main hair mass
    for y in range(hair_top, hair_bottom + 1):
        rel = (y - hair_top) / hair_height

        if rel < 0.25:
            # Dome top
            t = rel / 0.25
            half_width = int(14 + t * 24)
        elif rel < 0.75:
            # Straight sides
            half_width = 38
        else:
            # Flip ends
            t = (rel - 0.75) / 0.25
            half_width = 38 + int(t * flip_amount)

        canvas.draw_line(cx - half_width, y, cx + half_width, y, colors['base'])

    # Highlight stripe
    for i in range(5):
        hw = 18 - i * 3
        if hw > 0:
            canvas.draw_line(cx - hw, hair_top + 2 + i, cx + hw, hair_top + 2 + i, colors['highlight'])


def draw_bangs(canvas, cx, cy, palette, style='zigzag'):
    """Bangs with notched pattern."""
    colors = palette['hair']
    bang_top = cy - 18 + 5
    bang_width = 18

    for x in range(cx - bang_width, cx + bang_width + 1):
        notch = (abs(x - cx) % 8 < 3)
        top_y = bang_top + (4 if notch else 0)
        h = 14 - (4 if notch else 0)
        for dy in range(h):
            canvas.set_pixel(x, top_y + dy, colors['base'])


# ============================================================
# FACE (from recipes/compositions/portrait.md)
# ============================================================
def draw_face(canvas, cx, cy, palette):
    """Face with eyes, blush, mouth."""
    # Face shape
    canvas.fill_ellipse(cx, cy + 6, 18, 20, palette['skin']['base'])

    # Eyes (simple squares with highlights)
    eye_y = cy + 4
    eye_size = 5
    canvas.fill_rect(cx - 12, eye_y - eye_size//2, eye_size, eye_size, palette['eyes'])
    canvas.fill_rect(cx + 7, eye_y - eye_size//2, eye_size, eye_size, palette['eyes'])

    # Eye highlights
    white = rgba((255, 255, 255))
    canvas.fill_rect(cx - 11, eye_y - 2, 2, 2, white)
    canvas.fill_rect(cx + 8, eye_y - 2, 2, 2, white)

    # Blush
    canvas.fill_ellipse(cx - 14, cy + 13, 5, 3, palette['skin']['blush'])
    canvas.fill_ellipse(cx + 14, cy + 13, 5, 3, palette['skin']['blush'])

    # Mouth
    canvas.draw_line(cx - 2, cy + 18, cx + 2, cy + 18, palette['mouth'])


# ============================================================
# DRESS (from recipes/compositions/portrait.md - tiered)
# ============================================================
def draw_tiered_dress(canvas, cx, top_y, bottom_y, palette):
    """Tiered dress that expands downward."""
    colors = palette['clothing']
    total_height = bottom_y - top_y
    tier_h = total_height // len(colors)

    for t, color in enumerate(colors):
        tier_y = top_y + t * tier_h
        base_w = 30 + t * 16

        for row in range(tier_h):
            if tier_y + row >= bottom_y:
                break
            w = base_w + row
            canvas.draw_line(cx - w, tier_y + row, cx + w, tier_y + row, color)

    # Neckline
    canvas.draw_line(cx - 16, top_y - 2, cx + 16, top_y - 2, colors[0])
    canvas.draw_line(cx - 12, top_y - 1, cx + 12, top_y - 1, palette['skin']['base'])


# ============================================================
# MAIN: Compose portrait using all recipes
# ============================================================
def generate_portrait(width=128, height=128):
    """Generate a complete portrait using learned recipes."""
    canvas = Canvas(width, height)

    # 1. Draw frame (returns content area offset)
    inner = draw_portrait_frame(canvas, width, height, PALETTE)

    # 2. Calculate character position (from composition recipe)
    cx = width // 2
    cy = inner + (height - inner * 2) // 3  # Upper third of content

    # 3. Draw hair back
    draw_bob_hair(canvas, cx, cy, PALETTE)

    # 4. Draw face
    draw_face(canvas, cx, cy, PALETTE)

    # 5. Draw bangs (front layer)
    draw_bangs(canvas, cx, cy, PALETTE)

    # 6. Draw dress
    dress_top = cy + 22
    dress_bottom = height - inner - 2
    draw_tiered_dress(canvas, cx, dress_top, dress_bottom, PALETTE)

    return canvas


if __name__ == '__main__':
    canvas = generate_portrait(128, 128)
    canvas.save('output/portrait_from_recipes.png')
    print("Generated: output/portrait_from_recipes.png")
    print("\nThis portrait was created using recipes learned from portrait_princess.png:")
    print("  - Bob hair style (dome + straight + flip)")
    print("  - Layered frame with gold corner triangles")
    print("  - Princess color palette")
    print("  - Portrait composition guidelines")

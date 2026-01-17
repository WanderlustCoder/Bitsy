"""
Recipe Loader - Reads character specs and renders using recipe knowledge.

This module bridges the gap between:
- User specs (what they want)
- Recipe knowledge (how to draw it)
- Canvas primitives (the tools)
"""

import yaml
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.canvas import Canvas


# =============================================================================
# COLOR PRESETS (from spec_format.md)
# =============================================================================

SKIN_TONES = {
    'fair': {
        'base': (235, 200, 175, 255),
        'shadow': (200, 160, 140, 255),
        'light': (245, 220, 200, 255),
    },
    'medium': {
        'base': (210, 165, 135, 255),
        'shadow': (175, 130, 105, 255),
        'light': (225, 185, 160, 255),
    },
    'tan': {
        'base': (180, 135, 100, 255),
        'shadow': (145, 105, 75, 255),
        'light': (200, 160, 125, 255),
    },
    'dark': {
        'base': (140, 95, 70, 255),
        'shadow': (105, 70, 50, 255),
        'light': (165, 120, 90, 255),
    },
}

HAIR_COLORS = {
    'brown': [(50,35,30,255), (80,55,45,255), (115,80,60,255), (150,110,85,255), (190,150,120,255)],
    'dark_brown': [(35,25,25,255), (55,40,35,255), (85,60,50,255), (120,90,70,255), (160,125,100,255)],
    'black': [(20,20,30,255), (35,35,50,255), (55,50,65,255), (80,75,95,255), (120,110,135,255)],
    'blonde': [(140,100,50,255), (180,140,70,255), (210,175,100,255), (235,205,140,255), (250,235,190,255)],
    'auburn': [(60,25,20,255), (100,45,35,255), (145,65,45,255), (180,95,65,255), (210,140,100,255)],
    'red': [(80,30,25,255), (130,50,40,255), (175,70,55,255), (210,100,75,255), (240,145,110,255)],
}

EYE_COLORS = {
    'brown': {'base': (100,65,50,255), 'dark': (70,45,35,255), 'light': (140,95,70,255)},
    'blue': {'base': (70,110,170,255), 'dark': (50,80,130,255), 'light': (100,150,200,255)},
    'green': {'base': (60,120,70,255), 'dark': (35,80,50,255), 'light': (90,160,100,255)},
    'gray': {'base': (100,105,115,255), 'dark': (70,75,85,255), 'light': (140,145,155,255)},
}

FRAME_COLORS = {
    'dark': (35, 30, 40, 255),
    'brown': (90, 60, 45, 255),
    'gold': (180, 150, 80, 255),
    'silver': (160, 165, 175, 255),
    'red': (150, 50, 50, 255),
}


# =============================================================================
# SPEC PARSER
# =============================================================================

@dataclass
class CharacterSpec:
    """Parsed character specification with all values resolved."""
    size: int
    background: Tuple[int, int, int, int]

    # Positioning
    head_cx: int
    head_cy: int
    head_rx: int
    head_ry: int

    # Colors
    skin_base: Tuple[int, int, int, int]
    skin_shadow: Tuple[int, int, int, int]
    skin_light: Tuple[int, int, int, int]

    hair_colors: List[Tuple[int, int, int, int]]
    hair_style: str

    eye_color_base: Tuple[int, int, int, int]
    eye_color_dark: Tuple[int, int, int, int]
    eye_color_light: Tuple[int, int, int, int]
    eye_expression: str

    nose_style: str
    mouth_style: str
    blush_intensity: float

    # Accessories
    has_glasses: bool
    glasses_style: str
    glasses_frame_color: Tuple[int, int, int, int]
    glasses_glare: bool


def _ensure_rgba(color) -> Tuple[int, int, int, int]:
    """Convert color to RGBA tuple."""
    if isinstance(color, (list, tuple)):
        if len(color) == 3:
            return (color[0], color[1], color[2], 255)
        return tuple(color)
    return color


def parse_spec(spec: Dict[str, Any]) -> CharacterSpec:
    """Parse a spec dictionary into a resolved CharacterSpec."""

    size = spec.get('size', 128)
    bg = spec.get('background', [45, 40, 55])
    background = _ensure_rgba(bg)

    char = spec.get('character', {})

    # Head positioning (auto-calculate if not specified)
    head_center = char.get('head_center', 'auto')
    head_size = char.get('head_size', 'auto')

    if head_center == 'auto':
        head_cx = size // 2
        head_cy = int(size * 0.42)
    else:
        head_cx, head_cy = head_center

    if head_size == 'auto':
        head_rx = int(size * 0.27)
        head_ry = int(size * 0.33)
    else:
        head_rx = head_size[0] // 2
        head_ry = head_size[1] // 2

    # Skin
    skin_spec = char.get('skin', {})
    if 'tone' in skin_spec:
        tone = SKIN_TONES.get(skin_spec['tone'], SKIN_TONES['fair'])
        skin_base = tone['base']
        skin_shadow = tone['shadow']
        skin_light = tone['light']
    else:
        skin_base = _ensure_rgba(skin_spec.get('base', (235, 200, 175)))
        skin_shadow = _ensure_rgba(skin_spec.get('shadow', (200, 160, 140)))
        skin_light = _ensure_rgba(skin_spec.get('light', (245, 220, 200)))

    # Hair
    hair_spec = char.get('hair', {})
    hair_style = hair_spec.get('style', 'bun')
    if 'colors' in hair_spec:
        hair_colors = [_ensure_rgba(c) for c in hair_spec['colors']]
    else:
        color_name = hair_spec.get('color', 'brown')
        hair_colors = HAIR_COLORS.get(color_name, HAIR_COLORS['brown'])

    # Eyes
    eye_spec = char.get('eyes', {})
    eye_expression = eye_spec.get('expression', 'neutral')
    eye_color_name = eye_spec.get('color', 'brown')

    if isinstance(eye_color_name, (list, tuple)):
        # Custom color
        base = _ensure_rgba(eye_color_name)
        eye_color_base = base
        eye_color_dark = (max(0, base[0]-30), max(0, base[1]-30), max(0, base[2]-20), 255)
        eye_color_light = (min(255, base[0]+30), min(255, base[1]+40), min(255, base[2]+30), 255)
    else:
        colors = EYE_COLORS.get(eye_color_name, EYE_COLORS['brown'])
        eye_color_base = colors['base']
        eye_color_dark = colors['dark']
        eye_color_light = colors['light']

    # Face details
    face_spec = char.get('face', {})
    nose_style = face_spec.get('nose', 'minimal')
    mouth_style = face_spec.get('mouth', 'neutral')
    blush = face_spec.get('blush', 0.2)
    blush_intensity = float(blush) if blush else 0.0

    # Glasses
    accessories = char.get('accessories', {})
    glasses_spec = accessories.get('glasses', None)

    if glasses_spec:
        has_glasses = True
        glasses_style = glasses_spec.get('style', 'round')
        frame_color = glasses_spec.get('frame_color', 'dark')
        if isinstance(frame_color, str):
            glasses_frame_color = FRAME_COLORS.get(frame_color, FRAME_COLORS['dark'])
        else:
            glasses_frame_color = _ensure_rgba(frame_color)
        glasses_glare = glasses_spec.get('glare', True)
    else:
        has_glasses = False
        glasses_style = 'round'
        glasses_frame_color = FRAME_COLORS['dark']
        glasses_glare = False

    return CharacterSpec(
        size=size,
        background=background,
        head_cx=head_cx,
        head_cy=head_cy,
        head_rx=head_rx,
        head_ry=head_ry,
        skin_base=skin_base,
        skin_shadow=skin_shadow,
        skin_light=skin_light,
        hair_colors=hair_colors,
        hair_style=hair_style,
        eye_color_base=eye_color_base,
        eye_color_dark=eye_color_dark,
        eye_color_light=eye_color_light,
        eye_expression=eye_expression,
        nose_style=nose_style,
        mouth_style=mouth_style,
        blush_intensity=blush_intensity,
        has_glasses=has_glasses,
        glasses_style=glasses_style,
        glasses_frame_color=glasses_frame_color,
        glasses_glare=glasses_glare,
    )


def load_spec_file(path: str) -> CharacterSpec:
    """Load a spec from a YAML file."""
    with open(path, 'r') as f:
        spec = yaml.safe_load(f)
    return parse_spec(spec)


# =============================================================================
# RECIPE RENDERERS (applying recipe knowledge)
# =============================================================================

def render_hair_back(canvas: Canvas, spec: CharacterSpec) -> None:
    """Render back hair layer (from hair.md recipe)."""
    cx, cy = spec.head_cx, spec.head_cy
    rx, ry = spec.head_rx, spec.head_ry
    colors = spec.hair_colors
    darkest, shadow, base, light, highlight = colors[0], colors[1], colors[2], colors[3], colors[4]

    # Back hair mass - wider than head
    back_rx = rx + int(rx * 0.35)
    back_ry = ry + int(ry * 0.2)

    canvas.fill_ellipse(cx, cy + 5, back_rx, back_ry, darkest)
    canvas.fill_ellipse(cx, cy + 2, back_rx - 3, back_ry - 3, shadow)

    # Side pieces
    for side in [-1, 1]:
        sx = cx + side * (rx + 5)
        canvas.fill_ellipse(sx, cy + 15, 8, 25, shadow)
        canvas.fill_ellipse(sx - side, cy + 14, 6, 22, base)


def render_head(canvas: Canvas, spec: CharacterSpec) -> None:
    """Render head/face base."""
    cx, cy = spec.head_cx, spec.head_cy
    rx, ry = spec.head_rx, spec.head_ry

    canvas.fill_ellipse(cx + 1, cy + 2, rx, ry, spec.skin_shadow)
    canvas.fill_ellipse(cx, cy, rx - 1, ry - 1, spec.skin_base)
    canvas.fill_ellipse(cx - 3, cy - 5, rx - 8, ry - 10, spec.skin_light)


def render_bun(canvas: Canvas, spec: CharacterSpec) -> None:
    """Render bun hairstyle (from hair.md recipe)."""
    cx, cy = spec.head_cx, spec.head_cy
    ry = spec.head_ry
    colors = spec.hair_colors
    darkest, shadow, base, light = colors[0], colors[1], colors[2], colors[3]

    bun_cx = cx
    bun_cy = cy - ry - 8
    bun_r = 18

    canvas.fill_ellipse(bun_cx + 2, bun_cy + 3, bun_r, bun_r - 2, darkest)
    canvas.fill_ellipse(bun_cx, bun_cy, bun_r, bun_r - 2, base)
    canvas.fill_ellipse(bun_cx - 4, bun_cy - 4, bun_r // 2, bun_r // 3, light)

    # Wrap strands
    for strand in [[(bun_cx - 15, bun_cy), (bun_cx, bun_cy - 12), (bun_cx + 15, bun_cy)],
                   [(bun_cx - 12, bun_cy + 5), (bun_cx, bun_cy + 10), (bun_cx + 12, bun_cy + 5)]]:
        canvas.draw_bezier_tapered(strand, shadow, 1.5, 0.5)


def render_eyes(canvas: Canvas, spec: CharacterSpec) -> None:
    """Render eyes (from eyes.md recipe)."""
    cx, cy = spec.head_cx, spec.head_cy
    rx, ry = spec.head_rx, spec.head_ry

    eye_y = cy - int(ry * 0.08)
    eye_spacing = int(rx * 0.65)
    eye_w, eye_h = int(rx * 0.4), int(rx * 0.44)

    left_cx = cx - eye_spacing // 2
    right_cx = cx + eye_spacing // 2

    for i, ex in enumerate([left_cx, right_cx]):
        is_left = (i == 0)

        # Sclera
        canvas.fill_ellipse_aa(ex, eye_y, eye_w // 2, eye_h // 2, (255, 255, 255, 255))

        # Upper shadow
        canvas.fill_ellipse(ex, eye_y - eye_h // 3, eye_w // 2 - 1, 3, (210, 200, 210, 255))

        # Iris
        iris_x = ex + (1 if is_left else -1)
        canvas.fill_ellipse_gradient(iris_x, eye_y + 1, eye_w // 3, eye_h // 3,
                                     spec.eye_color_dark, spec.eye_color_light, angle=90)
        canvas.draw_circle_aa(iris_x, eye_y + 1, eye_w // 3 - 1, spec.eye_color_dark)

        # Pupil
        canvas.fill_ellipse(iris_x, eye_y + 2, 2, 3, (20, 15, 20, 255))

        # Highlights
        h_x = ex - 2 if is_left else ex + 2
        canvas.fill_ellipse(h_x, eye_y - 2, 2, 2, (255, 255, 255, 255))
        canvas.set_pixel(ex + (2 if is_left else -2), eye_y + 3, (255, 255, 255, 255))


def render_face_details(canvas: Canvas, spec: CharacterSpec) -> None:
    """Render nose, mouth, blush (from face_details.md recipe)."""
    cx, cy = spec.head_cx, spec.head_cy
    rx, ry = spec.head_rx, spec.head_ry

    mouth_color = (170, 110, 110, 255)

    # Nose
    if spec.nose_style != 'none':
        nose_y = cy + int(ry * 0.1)
        canvas.set_pixel(cx, nose_y, spec.skin_shadow)
        canvas.set_pixel(cx, nose_y + 1, spec.skin_shadow)

    # Mouth
    mouth_y = cy + int(ry * 0.28)

    if spec.mouth_style == 'neutral':
        canvas.draw_line(cx - 3, mouth_y, cx + 3, mouth_y, mouth_color)
    elif spec.mouth_style == 'happy':
        smile = [(cx - 5, mouth_y - 1), (cx, mouth_y + 2), (cx + 5, mouth_y - 1)]
        canvas.draw_bezier(smile, mouth_color, thickness=1)
    elif spec.mouth_style == 'sad':
        frown = [(cx - 4, mouth_y + 1), (cx, mouth_y - 2), (cx + 4, mouth_y + 1)]
        canvas.draw_bezier(frown, mouth_color, thickness=1)
    elif spec.mouth_style == 'surprised':
        canvas.fill_ellipse(cx, mouth_y + 1, 3, 4, (100, 60, 60, 255))
    elif spec.mouth_style == 'cat_smile':
        canvas.draw_line(cx - 4, mouth_y, cx - 1, mouth_y + 2, mouth_color)
        canvas.draw_line(cx - 1, mouth_y + 2, cx, mouth_y, mouth_color)
        canvas.draw_line(cx, mouth_y, cx + 1, mouth_y + 2, mouth_color)
        canvas.draw_line(cx + 1, mouth_y + 2, cx + 4, mouth_y, mouth_color)

    # Blush
    if spec.blush_intensity > 0:
        blush_y = cy + int(ry * 0.15)
        blush_x = int(rx * 0.45)
        alpha = int(60 + spec.blush_intensity * 120)
        blush = (255, 150, 150, alpha)
        canvas.fill_ellipse(cx - blush_x, blush_y, 7, 4, blush)
        canvas.fill_ellipse(cx + blush_x, blush_y, 7, 4, blush)


def render_glasses(canvas: Canvas, spec: CharacterSpec) -> None:
    """Render glasses (from glasses.md recipe)."""
    if not spec.has_glasses:
        return

    cx, cy = spec.head_cx, spec.head_cy
    rx, ry = spec.head_rx, spec.head_ry

    eye_y = cy - int(ry * 0.08)
    eye_spacing = int(rx * 0.65)
    left_cx = cx - eye_spacing // 2
    right_cx = cx + eye_spacing // 2

    frame = spec.glasses_frame_color

    if spec.glasses_style == 'round':
        lens_r = int(rx * 0.25)
        canvas.draw_circle_aa(left_cx, eye_y, lens_r, frame)
        canvas.draw_circle_aa(right_cx, eye_y, lens_r, frame)
        canvas.draw_line(left_cx + lens_r - 1, eye_y - 2, right_cx - lens_r + 1, eye_y - 2, frame)
        canvas.draw_line(left_cx - lens_r, eye_y, left_cx - lens_r - 4, eye_y - 1, frame)
        canvas.draw_line(right_cx + lens_r, eye_y, right_cx + lens_r + 4, eye_y - 1, frame)

        if spec.glasses_glare:
            for ecx in [left_cx, right_cx]:
                canvas.fill_ellipse(ecx - lens_r // 3, eye_y - lens_r // 3, 2, 1, (255, 255, 255, 150))

    elif spec.glasses_style == 'rectangular':
        lens_w = int(rx * 0.26)
        lens_h = int(rx * 0.2)
        for ecx in [left_cx, right_cx]:
            canvas.draw_rect(ecx - lens_w, eye_y - lens_h, lens_w * 2, lens_h * 2, frame)
        canvas.draw_line(left_cx + lens_w, eye_y - 1, right_cx - lens_w, eye_y - 1, frame)


def render_hair_front(canvas: Canvas, spec: CharacterSpec) -> None:
    """Render front hair/bangs (from hair.md recipe)."""
    cx, cy = spec.head_cx, spec.head_cy
    rx, ry = spec.head_rx, spec.head_ry
    colors = spec.hair_colors
    shadow, base, light = colors[1], colors[2], colors[3]

    bangs_y_start = cy - ry + 5
    bangs_y_end = cy - int(ry * 0.3)

    # Bangs mass
    canvas.fill_ellipse(cx, bangs_y_start + 8, rx - 5, 15, base)
    canvas.fill_ellipse(cx - 3, bangs_y_start + 6, rx - 8, 12, light)

    # Bang strands
    bang_strands = [
        [(cx - 18, bangs_y_start), (cx - 22, bangs_y_end - 10), (cx - 20, bangs_y_end + 5)],
        [(cx - 8, bangs_y_start - 3), (cx - 10, bangs_y_end - 12), (cx - 6, bangs_y_end + 3)],
        [(cx + 2, bangs_y_start - 5), (cx, bangs_y_end - 15), (cx + 4, bangs_y_end)],
        [(cx + 12, bangs_y_start - 3), (cx + 14, bangs_y_end - 12), (cx + 16, bangs_y_end + 3)],
        [(cx + 22, bangs_y_start), (cx + 26, bangs_y_end - 10), (cx + 24, bangs_y_end + 5)],
    ]

    for strand in bang_strands:
        canvas.draw_bezier_tapered(strand, shadow, 2.0, 0.5)
        canvas.draw_bezier_tapered([(p[0] - 1, p[1] - 1) for p in strand], light, 1.0, 0.3)


# =============================================================================
# MAIN RENDER FUNCTION
# =============================================================================

def render_character(spec: CharacterSpec) -> Canvas:
    """
    Render a complete character from a spec.

    Follows layer order from recipes:
    1. Background
    2. Hair back
    3. Head
    4. Hair style (bun, etc.)
    5. Eyes
    6. Face details
    7. Glasses
    8. Hair front
    """
    canvas = Canvas(spec.size, spec.size)

    # 1. Background
    canvas.fill_rect(0, 0, spec.size, spec.size, spec.background)

    # 2. Hair back
    render_hair_back(canvas, spec)

    # 3. Head
    render_head(canvas, spec)

    # 4. Hair style specific (bun, etc.)
    if spec.hair_style == 'bun':
        render_bun(canvas, spec)

    # 5. Eyes
    render_eyes(canvas, spec)

    # 6. Face details
    render_face_details(canvas, spec)

    # 7. Glasses
    render_glasses(canvas, spec)

    # 8. Hair front
    render_hair_front(canvas, spec)

    return canvas


def render_from_spec(spec_dict: Dict[str, Any]) -> Canvas:
    """Convenience function: parse spec and render."""
    parsed = parse_spec(spec_dict)
    return render_character(parsed)


def render_from_file(path: str) -> Canvas:
    """Convenience function: load spec file and render."""
    parsed = load_spec_file(path)
    return render_character(parsed)


# =============================================================================
# CLI
# =============================================================================

if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: python loader.py <spec.yaml> [output.png]")
        print("\nExample spec:")
        print("""
size: 128
character:
  hair: {style: bun, color: brown}
  eyes: {color: blue, expression: happy}
  accessories:
    glasses: {style: round}
""")
        sys.exit(1)

    spec_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else 'output/from_spec.png'

    canvas = render_from_file(spec_path)
    canvas.save(output_path)
    print(f"Saved: {output_path}")

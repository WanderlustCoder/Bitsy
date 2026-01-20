"""
Facial Feature Rendering - Detailed eyes, nose, and lips.

Provides:
- Multi-layer eye rendering with catchlights
- Nose shading with directional lighting
- Lip gradient with highlight strips
- Eyebrow expression control
"""

import math
from typing import List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.canvas import Canvas
from core.color import Color


class EyeExpression(Enum):
    """Eye expression presets."""
    NEUTRAL = "neutral"
    HAPPY = "happy"        # Slightly closed, curved bottom
    SAD = "sad"            # Droopy, lowered
    SURPRISED = "surprised"  # Wide open
    ANGRY = "angry"        # Narrow, angled brows
    SLEEPY = "sleepy"      # Half-closed


class FacialHairStyle(Enum):
    """Facial hair style options."""
    NONE = "none"
    STUBBLE = "stubble"          # Short texture around chin/jaw
    MUSTACHE = "mustache"        # Above upper lip only
    GOATEE = "goatee"            # Chin area only
    SHORT_BEARD = "short_beard"  # Trimmed short beard
    FULL_BEARD = "full_beard"    # Full coverage beard


@dataclass
class EyeParams:
    """Parameters for eye rendering."""
    center_x: int
    center_y: int
    width: int
    height: int
    iris_color: List[Color]  # Ramp from dark to light
    openness: float = 1.0    # 0.0 = closed, 1.0 = fully open
    gaze_x: float = 0.0      # -1 to 1, pupil horizontal offset
    gaze_y: float = 0.0      # -1 to 1, pupil vertical offset
    has_lashes: bool = True
    lash_length: int = 2


def render_eye(canvas: Canvas, params: EyeParams,
               light_direction: Tuple[float, float] = (1.0, -1.0)) -> None:
    """
    Render a detailed eye with multiple layers.

    Layers:
    1. Eye white (slight off-white)
    2. Iris with radial gradient
    3. Pupil (near-black with blue tint)
    4. Catchlight (white dots)
    5. Eyelid shadow
    6. Lashes (optional)
    """
    cx, cy = params.center_x, params.center_y
    w, h = params.width, int(params.height * params.openness)

    if h < 2:
        # Eye too closed to render
        return

    # Layer 1: Eye white
    white_color = (245, 242, 238, 255)
    canvas.fill_ellipse_aa(cx, cy, w, h, white_color)

    # Layer 2: Iris
    iris_radius = int(w * 0.55)
    gaze_offset_x = int(params.gaze_x * w * 0.15)
    gaze_offset_y = int(params.gaze_y * h * 0.15)
    iris_x = cx + gaze_offset_x
    iris_y = cy + gaze_offset_y

    # Iris gradient (darker at edge)
    if params.iris_color:
        outer_color = params.iris_color[0]
        mid_color = params.iris_color[len(params.iris_color) // 2]
        inner_color = params.iris_color[-1] if len(params.iris_color) > 2 else mid_color

        canvas.fill_circle_aa(iris_x, iris_y, iris_radius, outer_color)
        canvas.fill_circle_aa(iris_x, iris_y, int(iris_radius * 0.75), mid_color)
        canvas.fill_circle_aa(iris_x, iris_y, int(iris_radius * 0.5), inner_color)

    # Layer 3: Pupil
    pupil_radius = int(iris_radius * 0.45)
    pupil_color = (8, 8, 18, 255)  # Near black with blue tint
    canvas.fill_circle_aa(iris_x, iris_y, pupil_radius, pupil_color)

    # Layer 4: Catchlight
    # Primary catchlight (upper-left usually)
    cl_x = iris_x - int(iris_radius * 0.3)
    cl_y = iris_y - int(iris_radius * 0.35)
    catchlight_color = (255, 255, 255, 255)
    canvas.set_pixel(cl_x, cl_y, catchlight_color)
    canvas.set_pixel(cl_x + 1, cl_y, catchlight_color)
    canvas.set_pixel(cl_x, cl_y + 1, (255, 255, 255, 200))

    # Secondary smaller catchlight (lower-right)
    cl2_x = iris_x + int(iris_radius * 0.2)
    cl2_y = iris_y + int(iris_radius * 0.25)
    canvas.set_pixel(cl2_x, cl2_y, (255, 255, 255, 180))

    # Layer 5: Eyelid shadow
    shadow_color = (0, 0, 0, 50)
    for dx in range(-w + 2, w - 1):
        # Top of eye area
        px = cx + dx
        py = cy - h + 1
        existing = canvas.get_pixel(px, py)
        if existing and existing[3] > 50:
            canvas.set_pixel(px, py, shadow_color)

    # Layer 6: Lashes
    if params.has_lashes and params.lash_length > 0:
        lash_color = (30, 25, 25, 255)
        # Top lashes
        for i in range(0, w * 2, 3):
            lash_x = cx - w + i + 1
            lash_base_y = cy - h + 1

            # Curved lash
            for ly in range(params.lash_length):
                curve = int((ly / params.lash_length) * 0.5)
                canvas.set_pixel(lash_x + curve, lash_base_y - ly, lash_color)


def render_nose(canvas: Canvas, center_x: int, center_y: int,
                width: int, height: int,
                skin_ramp: List[Color],
                light_direction: Tuple[float, float] = (1.0, -1.0)) -> None:
    """
    Render nose with directional shading.

    Creates subtle nose indication through:
    - Shadow line on dark side
    - Highlight on nose tip
    - Optional nostril hints at larger sizes
    """
    mid_idx = len(skin_ramp) // 2
    shadow_color = (*skin_ramp[max(0, mid_idx - 1)][:3], 70)
    highlight_color = (*skin_ramp[min(len(skin_ramp)-1, mid_idx + 1)][:3], 60)

    # Determine shadow side
    lx, _ = light_direction
    shadow_side = -1 if lx > 0 else 1

    # Shadow line
    for dy in range(height):
        py = center_y + dy
        px = center_x + shadow_side * 2
        canvas.set_pixel(px, py, shadow_color)
        if dy > height // 2:
            # Widen shadow slightly at bottom
            canvas.set_pixel(px + shadow_side, py, (*shadow_color[:3], 40))

    # Nose tip highlight
    tip_y = center_y + height - 2
    canvas.set_pixel(center_x, tip_y, highlight_color)
    canvas.set_pixel(center_x, tip_y + 1, highlight_color)

    # Nostril hints (for larger sizes)
    if height > 10:
        nostril_color = (*skin_ramp[max(0, mid_idx - 2)][:3], 50)
        nostril_y = center_y + height - 1
        canvas.set_pixel(center_x - 2, nostril_y, nostril_color)
        canvas.set_pixel(center_x + 2, nostril_y, nostril_color)


def render_lips(canvas: Canvas, center_x: int, center_y: int,
                width: int, height: int,
                lip_ramp: List[Color],
                is_smiling: bool = False) -> None:
    """
    Render lips with gradient and highlight.

    Features:
    - Upper lip slightly darker
    - Lower lip with highlight strip
    - Lip line 1px darker
    - Optional smile curve
    """
    if not lip_ramp:
        return

    # Colors
    dark_lip = lip_ramp[0] if lip_ramp else (150, 100, 100, 255)
    mid_lip = lip_ramp[len(lip_ramp) // 2] if lip_ramp else (180, 120, 120, 255)
    light_lip = lip_ramp[-1] if lip_ramp else (200, 150, 150, 255)

    # Upper lip (darker, thinner)
    upper_height = max(1, height // 3)
    for dx in range(-width, width + 1):
        # Curved top edge
        curve_factor = 1 - (dx / width) ** 2
        curve = int(curve_factor * upper_height)
        for dy in range(curve):
            py = center_y - dy - 1
            canvas.set_pixel(center_x + dx, py, dark_lip)

    # Lip line
    lip_line_color = lip_ramp[0] if lip_ramp else (100, 60, 60, 255)
    for dx in range(-width + 1, width):
        # Slight smile curve if enabled
        smile_offset = 0
        if is_smiling:
            smile_offset = int(abs(dx / width) * 2)
        canvas.set_pixel(center_x + dx, center_y - smile_offset, lip_line_color)

    # Lower lip (lighter, fuller)
    lower_height = max(1, int(height * 0.6))
    for dx in range(-width + 1, width):
        curve_factor = 1 - (dx / width) ** 2
        curve = int(curve_factor * lower_height)
        for dy in range(1, curve + 1):
            py = center_y + dy
            # Highlight on top portion
            if dy <= 2:
                color = light_lip
            else:
                color = mid_lip
            canvas.set_pixel(center_x + dx, py, color)


def render_eyebrow(canvas: Canvas, center_x: int, center_y: int,
                   width: int, color: Color,
                   arch_amount: float = 0.3,
                   angle: float = 0.0,
                   thickness: int = 2) -> None:
    """
    Render an eyebrow with adjustable arch and angle.

    Args:
        center_x, center_y: Brow center position
        width: Brow width in pixels
        color: Brow color
        arch_amount: How much the brow arches (0.0-1.0)
        angle: Rotation angle (positive = angry, negative = sad)
        thickness: Brow thickness in pixels
    """
    half_width = width // 2

    for dx in range(-half_width, half_width + 1):
        # Normalized position (-1 to 1)
        t = dx / half_width if half_width > 0 else 0

        # Arch curve
        arch = arch_amount * (1 - t ** 2) * 3

        # Angle offset
        angle_offset = angle * t * 2

        py = int(center_y - arch + angle_offset)
        px = center_x + dx

        # Draw with thickness
        for ty in range(thickness):
            canvas.set_pixel(px, py + ty, color)


def render_facial_hair(canvas: Canvas, cx: int, cy: int,
                       face_width: int, face_height: int,
                       style: FacialHairStyle,
                       color_ramp: List[Color],
                       light_direction: Tuple[float, float] = (1.0, -1.0)) -> None:
    """
    Render facial hair based on style.

    Args:
        canvas: Target canvas
        cx, cy: Face center position
        face_width: Width of face for scaling
        face_height: Height of face for scaling
        style: Facial hair style to render
        color_ramp: Hair color gradient (dark to light)
        light_direction: Direction of light source
    """
    if style == FacialHairStyle.NONE or not color_ramp:
        return

    import random
    rng = random.Random(cx + cy)  # Deterministic based on position

    # Get colors from ramp
    dark = color_ramp[0]
    mid = color_ramp[len(color_ramp) // 2] if len(color_ramp) > 1 else dark
    light = color_ramp[-1] if len(color_ramp) > 2 else mid

    # Chin position (below mouth)
    chin_y = cy + face_height // 3
    jaw_width = face_width // 2

    # Light-facing side gets lighter color
    lx, _ = light_direction

    if style == FacialHairStyle.STUBBLE:
        _render_stubble(canvas, cx, chin_y, jaw_width, face_height // 4,
                        dark, mid, rng, lx)

    elif style == FacialHairStyle.MUSTACHE:
        _render_mustache(canvas, cx, cy + face_height // 8, jaw_width,
                         dark, mid, light, lx)

    elif style == FacialHairStyle.GOATEE:
        _render_goatee(canvas, cx, chin_y, jaw_width // 2, face_height // 4,
                       dark, mid, light, lx)

    elif style == FacialHairStyle.SHORT_BEARD:
        _render_mustache(canvas, cx, cy + face_height // 8, jaw_width,
                         dark, mid, light, lx)
        _render_short_beard(canvas, cx, chin_y, jaw_width, face_height // 4,
                            dark, mid, light, lx)

    elif style == FacialHairStyle.FULL_BEARD:
        _render_mustache(canvas, cx, cy + face_height // 8, jaw_width,
                         dark, mid, light, lx)
        _render_full_beard(canvas, cx, chin_y, jaw_width, face_height // 3,
                           dark, mid, light, rng, lx)


def _render_stubble(canvas: Canvas, cx: int, cy: int, width: int, height: int,
                    dark: Color, mid: Color, rng, light_x: float) -> None:
    """Render stubble texture with scattered dots."""
    for dy in range(-height // 2, height):
        for dx in range(-width, width + 1):
            # Check if within jaw curve
            jaw_curve = 1.0 - (abs(dx) / max(1, width)) ** 1.5
            if dy > height * jaw_curve:
                continue

            # Sparse dots for stubble
            if rng.random() < 0.25:
                color = mid if (dx > 0 and light_x > 0) else dark
                # Add some alpha variation
                alpha = rng.randint(100, 200)
                color = (*color[:3], alpha)
                canvas.set_pixel(cx + dx, cy + dy, color)


def _render_mustache(canvas: Canvas, cx: int, cy: int, width: int,
                     dark: Color, mid: Color, light: Color, light_x: float) -> None:
    """Render a mustache above the upper lip."""
    mustache_width = width * 2 // 3
    mustache_height = 4

    for dy in range(mustache_height):
        row_width = mustache_width - dy * 2
        for dx in range(-row_width, row_width + 1):
            # Taper at edges
            edge_dist = abs(dx) / max(1, row_width)
            if edge_dist > 0.9:
                continue

            # Color based on light
            if dx > 0 and light_x > 0:
                color = mid
            elif dx < 0 and light_x < 0:
                color = mid
            else:
                color = dark

            canvas.set_pixel(cx + dx, cy + dy, color)


def _render_goatee(canvas: Canvas, cx: int, cy: int, width: int, height: int,
                   dark: Color, mid: Color, light: Color, light_x: float) -> None:
    """Render a goatee on the chin."""
    for dy in range(height):
        # Taper toward bottom
        row_width = int(width * (1 - dy / height * 0.5))
        for dx in range(-row_width, row_width + 1):
            # Rounded bottom
            dist_from_center = abs(dx) / max(1, row_width)
            bottom_curve = (1 - dist_from_center ** 2) * height
            if dy > bottom_curve:
                continue

            color = mid if (dx > 0 and light_x > 0) else dark
            canvas.set_pixel(cx + dx, cy + dy, color)


def _render_short_beard(canvas: Canvas, cx: int, cy: int, width: int, height: int,
                        dark: Color, mid: Color, light: Color, light_x: float) -> None:
    """Render a trimmed short beard."""
    for dy in range(-2, height):
        # Jaw contour
        jaw_factor = 1.0 - (dy / max(1, height)) * 0.3
        row_width = int(width * jaw_factor)

        for dx in range(-row_width, row_width + 1):
            # Jaw curve falloff
            edge_dist = abs(dx) / max(1, row_width)
            if edge_dist > 0.95:
                continue

            color = mid if (dx > 0 and light_x > 0) else dark
            canvas.set_pixel(cx + dx, cy + dy, color)


def _render_full_beard(canvas: Canvas, cx: int, cy: int, width: int, height: int,
                       dark: Color, mid: Color, light: Color,
                       rng, light_x: float) -> None:
    """Render a full beard with texture."""
    for dy in range(-3, height):
        # Jaw contour expanding then tapering
        if dy < height // 2:
            jaw_factor = 1.0 + (dy / max(1, height)) * 0.2
        else:
            jaw_factor = 1.2 - ((dy - height // 2) / max(1, height)) * 0.6
        row_width = int(width * jaw_factor)

        for dx in range(-row_width, row_width + 1):
            # Rounded bottom
            edge_dist = abs(dx) / max(1, row_width)
            bottom_y = height * (1 - edge_dist ** 2)
            if dy > bottom_y:
                continue

            # Base color with shading
            if dx > 0 and light_x > 0:
                color = mid
            else:
                color = dark

            # Add texture variation
            if rng.random() < 0.15:
                color = light

            canvas.set_pixel(cx + dx, cy + dy, color)


# =============================================================================
# ANIME-STYLE SIMPLIFIED FACIAL FEATURES
# =============================================================================

class AnimeNoseStyle(Enum):
    """Anime nose style options."""
    DOT = "dot"              # Single dot or small circle
    TRIANGLE = "triangle"    # Minimal triangle shadow
    SIDE_HOOK = "side_hook"  # L-shaped side view hint
    MINIMAL = "minimal"      # Just a tiny shadow
    NONE = "none"            # No nose (very stylized)


class AnimeMouthStyle(Enum):
    """Anime mouth style options."""
    LINE = "line"            # Simple horizontal line
    SMALL = "small"          # Small curved shape
    CAT = "cat"              # :3 cat mouth
    OPEN = "open"            # Open showing darkness inside
    SMILE = "smile"          # Curved smile line
    FROWN = "frown"          # Downturned line


def render_anime_nose(canvas: Canvas, center_x: int, center_y: int,
                      style: AnimeNoseStyle,
                      skin_ramp: List[Color],
                      size: float = 1.0,
                      light_direction: Tuple[float, float] = (1.0, -1.0)) -> None:
    """
    Render a simplified anime-style nose.

    Anime noses are minimal - often just a dot, small shadow, or nothing.

    Args:
        canvas: Target canvas
        center_x, center_y: Nose position
        style: Nose style
        skin_ramp: Skin color palette
        size: Size multiplier
        light_direction: Light direction for shadow placement
    """
    if style == AnimeNoseStyle.NONE or not skin_ramp:
        return

    mid_idx = len(skin_ramp) // 2
    shadow_color = skin_ramp[max(0, mid_idx - 2)]
    shadow_alpha = (*shadow_color[:3], 120)
    highlight_color = (*skin_ramp[min(len(skin_ramp) - 1, mid_idx + 2)][:3], 80)

    lx, _ = light_direction
    shadow_side = -1 if lx > 0 else 1

    if style == AnimeNoseStyle.DOT:
        # Simple dot
        dot_size = max(1, int(2 * size))
        for dy in range(-dot_size // 2, dot_size // 2 + 1):
            for dx in range(-dot_size // 2, dot_size // 2 + 1):
                if dx * dx + dy * dy <= (dot_size // 2) ** 2:
                    canvas.set_pixel(center_x + dx, center_y + dy, shadow_alpha)

    elif style == AnimeNoseStyle.TRIANGLE:
        # Small triangle shadow pointing down
        tri_height = max(2, int(4 * size))
        tri_width = max(1, int(3 * size))

        for dy in range(tri_height):
            row_width = int(tri_width * (1 - dy / tri_height))
            for dx in range(-row_width, row_width + 1):
                alpha = int(120 * (1 - dy / tri_height))
                canvas.set_pixel(center_x + dx, center_y + dy,
                               (*shadow_color[:3], alpha))

    elif style == AnimeNoseStyle.SIDE_HOOK:
        # L-shaped side indicator
        hook_height = max(3, int(5 * size))
        hook_width = max(1, int(2 * size))

        # Vertical line
        for dy in range(hook_height):
            canvas.set_pixel(center_x + shadow_side * hook_width, center_y + dy,
                           shadow_alpha)

        # Horizontal bottom
        for dx in range(hook_width + 1):
            canvas.set_pixel(center_x + shadow_side * dx, center_y + hook_height - 1,
                           shadow_alpha)

        # Small highlight on opposite side
        canvas.set_pixel(center_x - shadow_side, center_y + hook_height - 2,
                        highlight_color)

    elif style == AnimeNoseStyle.MINIMAL:
        # Just a tiny shadow hint
        canvas.set_pixel(center_x + shadow_side, center_y, shadow_alpha)
        canvas.set_pixel(center_x + shadow_side, center_y + 1,
                        (*shadow_color[:3], 80))


def render_anime_mouth(canvas: Canvas, center_x: int, center_y: int,
                       style: AnimeMouthStyle,
                       width: int,
                       lip_color: Color,
                       skin_ramp: List[Color],
                       expression_intensity: float = 0.5) -> None:
    """
    Render a simplified anime-style mouth.

    Anime mouths are simple shapes - lines, curves, or small forms.

    Args:
        canvas: Target canvas
        center_x, center_y: Mouth center position
        style: Mouth style
        width: Mouth width
        lip_color: Lip/line color
        skin_ramp: Skin colors for interior shading
        expression_intensity: How pronounced the expression (0-1)
    """
    half_w = width // 2

    # Mouth line color (darker than lips for contrast)
    line_color = (
        max(0, lip_color[0] - 40),
        max(0, lip_color[1] - 40),
        max(0, lip_color[2] - 30),
        255
    )

    # Interior color for open mouth
    interior_color = (40, 30, 35, 255)

    if style == AnimeMouthStyle.LINE:
        # Simple horizontal line
        for dx in range(-half_w, half_w + 1):
            canvas.set_pixel(center_x + dx, center_y, line_color)

    elif style == AnimeMouthStyle.SMALL:
        # Small curved shape
        small_w = half_w // 2
        for dx in range(-small_w, small_w + 1):
            # Slight curve
            curve = int((1 - (dx / small_w) ** 2) * 1)
            canvas.set_pixel(center_x + dx, center_y - curve, line_color)

    elif style == AnimeMouthStyle.CAT:
        # :3 cat mouth - W shape
        cat_w = half_w * 2 // 3
        # Left curve
        for dx in range(-cat_w, 0):
            curve = int(abs(dx / cat_w) * 2 * expression_intensity)
            canvas.set_pixel(center_x + dx, center_y + curve, line_color)
        # Right curve
        for dx in range(0, cat_w + 1):
            curve = int(abs(dx / cat_w) * 2 * expression_intensity)
            canvas.set_pixel(center_x + dx, center_y + curve, line_color)
        # Center dip
        canvas.set_pixel(center_x, center_y - 1, line_color)

    elif style == AnimeMouthStyle.OPEN:
        # Open mouth showing interior
        open_h = max(2, int(4 * expression_intensity))
        open_w = half_w * 2 // 3

        # Fill interior
        for dy in range(open_h):
            row_w = int(open_w * (1 - (dy / open_h) * 0.3))
            for dx in range(-row_w, row_w + 1):
                canvas.set_pixel(center_x + dx, center_y + dy, interior_color)

        # Top lip line
        for dx in range(-open_w, open_w + 1):
            canvas.set_pixel(center_x + dx, center_y - 1, line_color)

        # Bottom lip hint
        for dx in range(-open_w + 1, open_w):
            canvas.set_pixel(center_x + dx, center_y + open_h, lip_color)

    elif style == AnimeMouthStyle.SMILE:
        # Curved smile
        curve_amount = int(3 * expression_intensity)
        for dx in range(-half_w, half_w + 1):
            norm_x = dx / half_w if half_w > 0 else 0
            curve = int(norm_x ** 2 * curve_amount)
            canvas.set_pixel(center_x + dx, center_y + curve, line_color)

    elif style == AnimeMouthStyle.FROWN:
        # Downturned line
        curve_amount = int(2 * expression_intensity)
        for dx in range(-half_w, half_w + 1):
            norm_x = dx / half_w if half_w > 0 else 0
            curve = -int(norm_x ** 2 * curve_amount)
            canvas.set_pixel(center_x + dx, center_y + curve, line_color)


def _get_wrinkle_color(skin_ramp: List[Color], intensity: float) -> Optional[Color]:
    """Get a subtle wrinkle color slightly darker than skin."""
    if not skin_ramp or intensity <= 0.0:
        return None

    mid_idx = len(skin_ramp) // 2
    shade_idx = max(0, mid_idx - 1)
    base_color = skin_ramp[shade_idx]
    alpha = int(30 + 70 * intensity)
    return (*base_color[:3], min(255, alpha))


def _draw_short_line(canvas: Canvas, start_x: int, start_y: int,
                     dx: int, dy: int, length: int, color: Color) -> None:
    """Draw a short 1-2 pixel line in a direction."""
    for step in range(length):
        canvas.set_pixel(start_x + dx * step, start_y + dy * step, color)


def render_anime_wrinkles(canvas: Canvas,
                          center_x: int,
                          face_top: int,
                          face_width: int,
                          face_height: int,
                          proportions: dict,
                          skin_ramp: List[Color],
                          crows_feet: float = 0.0,
                          forehead_lines: float = 0.0,
                          smile_lines: float = 0.0) -> None:
    """
    Render subtle wrinkle lines for older anime characters.

    Wrinkles are 1-2 pixel lines using a darker skin tone.
    """
    crows_feet = max(0.0, min(1.0, crows_feet))
    forehead_lines = max(0.0, min(1.0, forehead_lines))
    smile_lines = max(0.0, min(1.0, smile_lines))

    if crows_feet <= 0.0 and forehead_lines <= 0.0 and smile_lines <= 0.0:
        return

    # Forehead lines - short horizontal segments
    if forehead_lines > 0.0:
        line_color = _get_wrinkle_color(skin_ramp, forehead_lines)
        if line_color:
            base_y = face_top + proportions.get("brow_y", int(face_height * 0.3))
            base_y -= max(2, face_height // 10)
            base_y = max(face_top + 2, base_y)
            line_length = 1 if forehead_lines < 0.6 else 2
            num_lines = 1 if forehead_lines < 0.7 else 2

            for i in range(num_lines):
                y = base_y + i * 2
                start_x = center_x - line_length // 2
                for dx in range(line_length):
                    canvas.set_pixel(start_x + dx, y, line_color)

    # Crow's feet - tiny radiating lines at outer eye corners
    if crows_feet > 0.0:
        line_color = _get_wrinkle_color(skin_ramp, crows_feet)
        if line_color:
            eye_y = face_top + proportions.get("eye_y", int(face_height * 0.45))
            eye_spacing = proportions.get("eye_spacing", int(face_width * 0.22))
            eye_width = proportions.get("eye_width", max(4, face_width // 6))
            line_length = 1 if crows_feet < 0.6 else 2
            num_lines = 1 if crows_feet < 0.7 else 2

            for side in (-1, 1):
                corner_x = center_x + side * (eye_spacing + eye_width // 2)
                corner_y = eye_y
                directions = [(-1, -1), (-1, 1)] if side < 0 else [(1, -1), (1, 1)]
                for i in range(num_lines):
                    dx, dy = directions[i]
                    _draw_short_line(
                        canvas,
                        corner_x + dx,
                        corner_y + dy,
                        dx,
                        dy,
                        line_length,
                        line_color
                    )

    # Smile lines - short strokes from nose toward mouth corners
    if smile_lines > 0.0:
        line_color = _get_wrinkle_color(skin_ramp, smile_lines)
        if line_color:
            nose_y = face_top + proportions.get("nose_y", int(face_height * 0.55))
            mouth_y = face_top + proportions.get("mouth_y", int(face_height * 0.7))
            mid_y = nose_y + (mouth_y - nose_y) // 2
            line_length = 1 if smile_lines < 0.6 else 2

            for side in (-1, 1):
                start_x = center_x + side * max(2, face_width // 10)
                _draw_short_line(
                    canvas,
                    start_x,
                    mid_y,
                    side,
                    1,
                    line_length,
                    line_color
                )


def render_anime_eyebrows(canvas: Canvas, left_x: int, right_x: int, y: int,
                          width: int, color: Color,
                          expression: str = "neutral",
                          thickness: int = 2) -> None:
    """
    Render simplified anime-style eyebrows.

    Args:
        canvas: Target canvas
        left_x, right_x: X positions for each brow
        y: Y position
        width: Brow width
        color: Brow color
        expression: Expression affecting angle (neutral, angry, sad, surprised)
        thickness: Line thickness
    """
    half_w = width // 2

    # Expression angles
    angles = {
        "neutral": (0.0, 0.0),
        "angry": (0.3, -0.3),      # Inner up, outer down
        "sad": (-0.2, 0.2),        # Inner down, outer up
        "surprised": (-0.1, -0.1), # Both raised
        "determined": (0.15, -0.15),
    }
    inner_angle, outer_angle = angles.get(expression, (0.0, 0.0))

    # Left eyebrow
    for dx in range(-half_w, half_w + 1):
        t = (dx + half_w) / width if width > 0 else 0.5
        # Interpolate angle from inner to outer
        angle_offset = inner_angle * (1 - t) + outer_angle * t
        py = y + int(angle_offset * 4)

        for ty in range(thickness):
            canvas.set_pixel(left_x + dx, py + ty, color)

    # Right eyebrow (mirrored)
    for dx in range(-half_w, half_w + 1):
        t = (dx + half_w) / width if width > 0 else 0.5
        # Mirror the angle
        angle_offset = outer_angle * (1 - t) + inner_angle * t
        py = y + int(angle_offset * 4)

        for ty in range(thickness):
            canvas.set_pixel(right_x + dx, py + ty, color)


def get_anime_face_proportions(face_width: int, face_height: int,
                                eye_scale: float = 2.5) -> dict:
    """
    Calculate anime face feature positions.

    Anime faces have:
    - Larger forehead
    - Eyes lower and larger
    - Smaller nose and mouth
    - Softer jaw

    Args:
        face_width: Face width
        face_height: Face height
        eye_scale: Eye size multiplier

    Returns:
        Dictionary of feature positions and sizes
    """
    return {
        # Eyes are lower on face (more forehead)
        "eye_y": int(face_height * 0.45),
        "eye_spacing": int(face_width * 0.22),
        "eye_width": int(face_width * 0.18 * eye_scale),
        "eye_height": int(face_width * 0.18 * eye_scale * 0.65),

        # Eyebrows just above eyes
        "brow_y": int(face_height * 0.32),
        "brow_width": int(face_width * 0.15),

        # Nose is minimal, centered
        "nose_y": int(face_height * 0.55),

        # Mouth is small and low
        "mouth_y": int(face_height * 0.7),
        "mouth_width": int(face_width * 0.12),

        # Chin point
        "chin_y": int(face_height * 0.9),
    }


def render_anime_blush(canvas: Canvas, left_x: int, right_x: int, y: int,
                       radius: int, color: Color, intensity: float = 0.5) -> None:
    """
    Render anime-style cheek blush (circular or lined).

    Args:
        canvas: Target canvas
        left_x, right_x: X positions for each cheek
        y: Y position
        radius: Blush radius
        color: Blush color
        intensity: Opacity (0-1)
    """
    alpha = int(100 * intensity)
    blush_color = (*color[:3], alpha)

    for cx in [left_x, right_x]:
        # Soft circular blush
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                dist = math.sqrt(dx * dx + dy * dy)
                if dist <= radius:
                    # Fade at edges
                    edge_alpha = int(alpha * (1 - dist / radius))
                    if edge_alpha > 0:
                        canvas.set_pixel(cx + dx, y + dy, (*color[:3], edge_alpha))


def render_anime_blush_lines(canvas: Canvas, left_x: int, right_x: int, y: int,
                              width: int, color: Color, line_count: int = 3) -> None:
    """
    Render anime-style diagonal blush lines.

    Args:
        canvas: Target canvas
        left_x, right_x: X positions
        y: Y position
        width: Line area width
        color: Line color
        line_count: Number of lines
    """
    line_color = (*color[:3], 150)

    for cx in [left_x, right_x]:
        for i in range(line_count):
            offset = (i - line_count // 2) * 3
            # Diagonal line
            for j in range(4):
                canvas.set_pixel(cx + offset + j, y - j, line_color)

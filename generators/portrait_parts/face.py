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

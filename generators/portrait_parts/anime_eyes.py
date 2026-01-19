"""
Anime-Style Eye Rendering

Creates large, expressive anime eyes with:
- Oversized proportions (2-3x realistic)
- Layered structure with catchlights
- Iris gradients with detail rings
- Stylized eyelashes
- Expression support
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


class AnimeEyeExpression(Enum):
    """Anime eye expression presets."""
    NEUTRAL = "neutral"
    HAPPY = "happy"          # Curved bottom, slightly closed
    SAD = "sad"              # Droopy, lowered
    SURPRISED = "surprised"  # Wide open, small iris
    ANGRY = "angry"          # Narrow, sharp angle
    SLEEPY = "sleepy"        # Half-closed
    SPARKLE = "sparkle"      # Extra catchlights
    DETERMINED = "determined"  # Focused, intense


@dataclass
class AnimeEyeParams:
    """Parameters for anime eye rendering."""
    # Position and size
    center_x: int
    center_y: int
    width: int               # Full eye width
    height: int              # Full eye height (typically 60-70% of width)

    # Iris colors (5-color ramp from dark to light)
    iris_ramp: List[Color]

    # Expression and state
    expression: AnimeEyeExpression = AnimeEyeExpression.NEUTRAL
    openness: float = 1.0    # 0.0 = closed, 1.0 = fully open

    # Gaze direction
    gaze_x: float = 0.0      # -1 to 1, horizontal offset
    gaze_y: float = 0.0      # -1 to 1, vertical offset

    # Style options
    iris_size: float = 0.75  # Iris as proportion of eye width (0.6-0.85)
    pupil_size: float = 0.35 # Pupil as proportion of iris
    has_highlight_ring: bool = True
    catchlight_style: str = "large"  # large, double, sparkle

    # Eyelash options
    upper_lash_thickness: int = 3
    has_lower_lashes: bool = True
    lash_color: Color = (20, 15, 25, 255)


def render_anime_eye(canvas: Canvas, params: AnimeEyeParams,
                     light_direction: Tuple[float, float] = (1.0, -1.0),
                     is_left_eye: bool = True) -> None:
    """
    Render a large, expressive anime eye with layered structure.

    Layers (back to front):
    1. Sclera (warm tinted white)
    2. Iris base color
    3. Iris gradient (dark at top)
    4. Pupil
    5. Iris detail rings
    6. Upper eyelid shadow
    7. Catchlights (large primary + secondary)
    8. Eyelid lines and lashes
    """
    cx, cy = params.center_x, params.center_y
    w, h = params.width, params.height

    # Apply expression modifications
    w, h, eye_curve = _apply_expression(w, h, params.expression, params.openness)

    if h < 3:
        # Eye too closed
        _render_closed_eye(canvas, cx, cy, w, params.lash_color)
        return

    # Calculate iris and pupil sizes
    iris_radius = int(w * params.iris_size / 2)
    pupil_radius = int(iris_radius * params.pupil_size)

    # Gaze offset (iris/pupil position)
    max_gaze_offset = int((w / 2 - iris_radius) * 0.6)
    gaze_offset_x = int(params.gaze_x * max_gaze_offset)
    gaze_offset_y = int(params.gaze_y * max_gaze_offset * 0.5)

    iris_x = cx + gaze_offset_x
    iris_y = cy + gaze_offset_y

    # Layer 1: Sclera (warm-tinted white)
    sclera_color = (250, 245, 240, 255)
    _render_anime_sclera(canvas, cx, cy, w, h, sclera_color, eye_curve)

    # Layer 2-5: Iris with gradient and details
    _render_anime_iris(canvas, iris_x, iris_y, iris_radius, pupil_radius,
                       params.iris_ramp, params.has_highlight_ring,
                       light_direction)

    # Layer 6: Upper eyelid shadow
    _render_upper_shadow(canvas, cx, cy, w, h, eye_curve)

    # Layer 7: Catchlights
    _render_catchlights(canvas, iris_x, iris_y, iris_radius,
                        params.catchlight_style, params.expression)

    # Layer 8: Eyelid lines and lashes
    _render_anime_eyelids(canvas, cx, cy, w, h, eye_curve,
                          params.upper_lash_thickness,
                          params.has_lower_lashes,
                          params.lash_color,
                          is_left_eye)


def _apply_expression(w: int, h: int, expression: AnimeEyeExpression,
                      openness: float) -> Tuple[int, int, float]:
    """
    Modify eye dimensions based on expression.

    Returns:
        (width, height, eye_curve) where eye_curve affects bottom lid shape
    """
    eye_curve = 0.0  # 0 = normal, positive = happy curve, negative = sad droop

    if expression == AnimeEyeExpression.HAPPY:
        h = int(h * 0.7 * openness)
        eye_curve = 0.4
    elif expression == AnimeEyeExpression.SAD:
        h = int(h * 0.85 * openness)
        eye_curve = -0.3
    elif expression == AnimeEyeExpression.SURPRISED:
        h = int(h * 1.15 * openness)
        eye_curve = -0.1
    elif expression == AnimeEyeExpression.ANGRY:
        h = int(h * 0.75 * openness)
        eye_curve = -0.2
    elif expression == AnimeEyeExpression.SLEEPY:
        h = int(h * 0.5 * openness)
        eye_curve = 0.1
    elif expression == AnimeEyeExpression.DETERMINED:
        h = int(h * 0.9 * openness)
        eye_curve = -0.15
    else:
        h = int(h * openness)

    return w, max(3, h), eye_curve


def _render_closed_eye(canvas: Canvas, cx: int, cy: int, w: int,
                       lash_color: Color) -> None:
    """Render a closed eye as a curved line."""
    for dx in range(-w // 2, w // 2 + 1):
        # Slight curve
        curve = int((1 - (dx / (w / 2)) ** 2) * 2)
        canvas.set_pixel(cx + dx, cy - curve, lash_color)
        if abs(dx) < w // 2 - 1:
            canvas.set_pixel(cx + dx, cy - curve + 1, lash_color)


def _render_anime_sclera(canvas: Canvas, cx: int, cy: int, w: int, h: int,
                         color: Color, eye_curve: float) -> None:
    """Render the eye white (sclera) with anime shape."""
    half_w = w // 2
    half_h = h // 2

    for dy in range(-half_h, half_h + 1):
        for dx in range(-half_w, half_w + 1):
            # Ellipse test with curve modification for bottom
            norm_x = dx / half_w if half_w > 0 else 0
            norm_y = dy / half_h if half_h > 0 else 0

            # Apply eye curve to bottom half
            if dy > 0 and eye_curve != 0:
                curve_mod = eye_curve * (1 - norm_x ** 2) * 0.3
                norm_y = norm_y - curve_mod

            dist = norm_x ** 2 + norm_y ** 2

            if dist <= 1.0:
                # Anti-alias at edge
                if dist > 0.85:
                    alpha = int(255 * (1.0 - dist) / 0.15)
                    alpha = max(0, min(255, alpha))
                    canvas.set_pixel(cx + dx, cy + dy, (*color[:3], alpha))
                else:
                    canvas.set_pixel(cx + dx, cy + dy, color)


def _render_anime_iris(canvas: Canvas, ix: int, iy: int,
                       iris_r: int, pupil_r: int,
                       iris_ramp: List[Color],
                       has_ring: bool,
                       light_direction: Tuple[float, float]) -> None:
    """
    Render the iris with anime-style gradient and details.

    Structure:
    - Outer ring (darkest)
    - Main iris gradient (dark top, light bottom)
    - Inner highlight ring
    - Pupil
    """
    if not iris_ramp or len(iris_ramp) < 3:
        return

    # Get colors from ramp
    darkest = iris_ramp[0]
    dark = iris_ramp[1] if len(iris_ramp) > 1 else darkest
    mid = iris_ramp[len(iris_ramp) // 2]
    light = iris_ramp[-2] if len(iris_ramp) > 2 else mid
    lightest = iris_ramp[-1]

    # Pupil color (very dark with slight color tint)
    pupil_color = (
        max(0, darkest[0] - 40),
        max(0, darkest[1] - 40),
        max(0, darkest[2] - 30),
        255
    )

    for dy in range(-iris_r, iris_r + 1):
        for dx in range(-iris_r, iris_r + 1):
            dist_sq = dx * dx + dy * dy
            dist = math.sqrt(dist_sq)

            if dist > iris_r:
                continue

            px, py = ix + dx, iy + dy

            # Normalized distance from center (0 = center, 1 = edge)
            norm_dist = dist / iris_r if iris_r > 0 else 0

            # Check if in pupil
            if dist <= pupil_r:
                canvas.set_pixel(px, py, pupil_color)
                continue

            # Iris gradient based on vertical position and distance
            # Top is darker, bottom is lighter (anime convention)
            vert_factor = (dy / iris_r + 1) / 2  # 0 at top, 1 at bottom

            # Combine vertical and radial gradients
            if norm_dist > 0.85:
                # Outer ring - darkest
                color = darkest
            elif norm_dist > 0.7:
                # Transition zone
                t = (norm_dist - 0.7) / 0.15
                color = _blend_colors(dark, darkest, t)
            elif has_ring and 0.5 < norm_dist < 0.6:
                # Highlight ring
                color = lightest
            else:
                # Main iris - gradient from dark (top) to light (bottom)
                if vert_factor < 0.4:
                    color = dark
                elif vert_factor < 0.6:
                    t = (vert_factor - 0.4) / 0.2
                    color = _blend_colors(dark, mid, t)
                else:
                    t = (vert_factor - 0.6) / 0.4
                    color = _blend_colors(mid, light, t)

            # Anti-alias at iris edge
            if norm_dist > 0.9:
                alpha = int(255 * (1.0 - norm_dist) / 0.1)
                alpha = max(0, min(255, alpha))
                color = (*color[:3], alpha)

            canvas.set_pixel(px, py, color)


def _render_upper_shadow(canvas: Canvas, cx: int, cy: int, w: int, h: int,
                         eye_curve: float) -> None:
    """Render shadow from upper eyelid over the eye."""
    shadow_color = (0, 0, 0, 60)
    half_w = w // 2
    shadow_height = max(2, h // 5)

    for dx in range(-half_w + 1, half_w):
        # Shadow follows eye curve
        norm_x = dx / half_w if half_w > 0 else 0
        base_y = cy - h // 2 + 1

        for dy in range(shadow_height):
            # Fade out shadow
            alpha = int(60 * (1 - dy / shadow_height))
            if alpha > 0:
                canvas.set_pixel(cx + dx, base_y + dy, (0, 0, 0, alpha))


def _render_catchlights(canvas: Canvas, ix: int, iy: int, iris_r: int,
                        style: str, expression: AnimeEyeExpression) -> None:
    """
    Render anime-style catchlights (eye sparkles).

    Styles:
    - large: One large primary catchlight
    - double: Large primary + small secondary
    - sparkle: Multiple small sparkles (for sparkle expression)
    """
    white = (255, 255, 255, 255)
    soft_white = (255, 255, 255, 200)

    # Primary catchlight (upper-left quadrant)
    primary_x = ix - int(iris_r * 0.35)
    primary_y = iy - int(iris_r * 0.35)
    primary_size = max(2, iris_r // 3)

    # Draw primary catchlight
    for dy in range(-primary_size, primary_size + 1):
        for dx in range(-primary_size, primary_size + 1):
            dist = math.sqrt(dx * dx + dy * dy)
            if dist <= primary_size:
                alpha = 255 if dist < primary_size * 0.6 else 200
                canvas.set_pixel(primary_x + dx, primary_y + dy, (255, 255, 255, alpha))

    if style in ("double", "sparkle") or expression == AnimeEyeExpression.SPARKLE:
        # Secondary catchlight (lower-right, smaller)
        secondary_x = ix + int(iris_r * 0.25)
        secondary_y = iy + int(iris_r * 0.3)
        secondary_size = max(1, primary_size // 2)

        for dy in range(-secondary_size, secondary_size + 1):
            for dx in range(-secondary_size, secondary_size + 1):
                dist = math.sqrt(dx * dx + dy * dy)
                if dist <= secondary_size:
                    canvas.set_pixel(secondary_x + dx, secondary_y + dy, soft_white)

    if style == "sparkle" or expression == AnimeEyeExpression.SPARKLE:
        # Extra sparkle dots
        sparkle_positions = [
            (ix - int(iris_r * 0.5), iy),
            (ix, iy - int(iris_r * 0.5)),
            (ix + int(iris_r * 0.4), iy - int(iris_r * 0.2)),
        ]
        for sx, sy in sparkle_positions:
            canvas.set_pixel(sx, sy, white)


def _render_anime_eyelids(canvas: Canvas, cx: int, cy: int, w: int, h: int,
                          eye_curve: float, upper_thickness: int,
                          has_lower: bool, lash_color: Color,
                          is_left_eye: bool) -> None:
    """
    Render anime-style eyelid lines and lashes.

    Features:
    - Thick upper lid line
    - Stylized lash clusters at corners
    - Optional thin lower lid line
    """
    half_w = w // 2
    half_h = h // 2

    # Upper eyelid line (thick)
    for dx in range(-half_w, half_w + 1):
        norm_x = dx / half_w if half_w > 0 else 0

        # Upper lid follows ellipse
        lid_y = cy - int(half_h * math.sqrt(max(0, 1 - norm_x ** 2)))

        # Draw thick line
        for t in range(upper_thickness):
            canvas.set_pixel(cx + dx, lid_y - t, lash_color)

    # Upper lash clusters at outer corner
    outer_x = cx + half_w if is_left_eye else cx - half_w
    outer_y = cy - half_h // 2

    # Draw 3-4 lash spikes at outer corner
    lash_dir = 1 if is_left_eye else -1
    for i in range(4):
        lash_len = 3 + i
        angle = math.pi * 0.3 + i * 0.15
        for j in range(lash_len):
            lx = outer_x + int(lash_dir * j * math.cos(angle))
            ly = outer_y - int(j * math.sin(angle)) - i
            canvas.set_pixel(lx, ly, lash_color)

    # Inner corner lash cluster (smaller)
    inner_x = cx - half_w if is_left_eye else cx + half_w
    inner_y = cy - half_h // 3

    for i in range(2):
        lash_len = 2
        for j in range(lash_len):
            lx = inner_x - int(lash_dir * j * 0.5)
            ly = inner_y - j - i
            canvas.set_pixel(lx, ly, lash_color)

    # Lower eyelid (thin line)
    if has_lower:
        lower_color = (*lash_color[:3], 150)  # Slightly transparent

        for dx in range(-half_w + 2, half_w - 1):
            norm_x = dx / half_w if half_w > 0 else 0

            # Lower lid with curve modification
            curve_mod = eye_curve * (1 - norm_x ** 2) * half_h * 0.3
            lid_y = cy + int(half_h * math.sqrt(max(0, 1 - norm_x ** 2)) - curve_mod)

            canvas.set_pixel(cx + dx, lid_y, lower_color)

        # Small lower lashes at outer corner
        for i in range(2):
            lx = outer_x - lash_dir * i
            ly = cy + half_h // 2 + i
            canvas.set_pixel(lx, ly, lower_color)


def _blend_colors(c1: Color, c2: Color, t: float) -> Color:
    """Blend two colors by factor t (0 = c1, 1 = c2)."""
    t = max(0, min(1, t))
    return (
        int(c1[0] * (1 - t) + c2[0] * t),
        int(c1[1] * (1 - t) + c2[1] * t),
        int(c1[2] * (1 - t) + c2[2] * t),
        255
    )


def render_anime_eyes(canvas: Canvas, face_cx: int, face_cy: int,
                      face_width: int, face_height: int,
                      iris_ramp: List[Color],
                      eye_scale: float = 2.5,
                      expression: AnimeEyeExpression = AnimeEyeExpression.NEUTRAL,
                      gaze: Tuple[float, float] = (0.0, 0.0),
                      openness: float = 1.0,
                      eye_spacing: float = 1.0,
                      catchlight_style: str = "double") -> None:
    """
    Render both anime eyes on a face.

    Args:
        canvas: Target canvas
        face_cx, face_cy: Face center position
        face_width, face_height: Face dimensions
        iris_ramp: 5-color iris palette
        eye_scale: Size multiplier vs realistic (2.0-3.0 for anime)
        expression: Eye expression
        gaze: (x, y) gaze direction
        openness: Eye openness (0-1)
        eye_spacing: Spacing multiplier
        catchlight_style: Catchlight type
    """
    # Anime eye proportions
    # Eyes are 30-40% of face width each, positioned lower on face
    eye_width = int(face_width * 0.18 * eye_scale)
    eye_height = int(eye_width * 0.65)  # Tall ellipse

    # Eye positions (wider spacing, lower on face for anime)
    eye_y = face_cy - int(face_height * 0.05)  # Slightly above center
    eye_spacing_px = int(face_width * 0.22 * eye_spacing)

    left_eye_x = face_cx - eye_spacing_px
    right_eye_x = face_cx + eye_spacing_px

    # Create params for each eye
    left_params = AnimeEyeParams(
        center_x=left_eye_x,
        center_y=eye_y,
        width=eye_width,
        height=eye_height,
        iris_ramp=iris_ramp,
        expression=expression,
        openness=openness,
        gaze_x=gaze[0],
        gaze_y=gaze[1],
        catchlight_style=catchlight_style,
    )

    right_params = AnimeEyeParams(
        center_x=right_eye_x,
        center_y=eye_y,
        width=eye_width,
        height=eye_height,
        iris_ramp=iris_ramp,
        expression=expression,
        openness=openness,
        gaze_x=gaze[0],
        gaze_y=gaze[1],
        catchlight_style=catchlight_style,
    )

    # Render both eyes
    render_anime_eye(canvas, left_params, is_left_eye=True)
    render_anime_eye(canvas, right_params, is_left_eye=False)


def get_anime_eye_position(face_cx: int, face_cy: int,
                           face_width: int, face_height: int,
                           eye_scale: float = 2.5,
                           eye_spacing: float = 1.0) -> Tuple[Tuple[int, int], Tuple[int, int], int, int]:
    """
    Calculate anime eye positions and dimensions.

    Returns:
        ((left_x, left_y), (right_x, right_y), eye_width, eye_height)
    """
    eye_width = int(face_width * 0.18 * eye_scale)
    eye_height = int(eye_width * 0.65)

    eye_y = face_cy - int(face_height * 0.05)
    eye_spacing_px = int(face_width * 0.22 * eye_spacing)

    left_eye_x = face_cx - eye_spacing_px
    right_eye_x = face_cx + eye_spacing_px

    return ((left_eye_x, eye_y), (right_eye_x, eye_y), eye_width, eye_height)

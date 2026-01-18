"""
Accessory Rendering - Glasses, jewelry, and other adornments.

Provides:
- Glasses with reflection effects
- Earring rendering
- Hair accessories
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


class GlassesStyle(Enum):
    """Glasses frame styles."""
    ROUND = "round"
    RECTANGULAR = "rectangular"
    CAT_EYE = "cat_eye"
    AVIATOR = "aviator"
    RIMLESS = "rimless"


class EarringStyle(Enum):
    """Earring styles."""
    STUD = "stud"
    HOOP = "hoop"
    DROP = "drop"
    DANGLE = "dangle"


@dataclass
class GlassesParams:
    """Parameters for glasses rendering."""
    left_eye_x: int
    left_eye_y: int
    right_eye_x: int
    right_eye_y: int
    lens_width: int
    lens_height: int
    style: GlassesStyle = GlassesStyle.ROUND
    frame_color: Color = (50, 45, 45, 255)
    lens_tint: Optional[Color] = None  # None for clear
    has_reflection: bool = True


def render_glasses(canvas: Canvas, params: GlassesParams,
                   light_direction: Tuple[float, float] = (1.0, -1.0)) -> None:
    """
    Render glasses with frame and optional lens effects.

    Features:
    - Frame with 3-color shading
    - Lens tint (optional)
    - Reflection highlight strip
    - Bridge connecting lenses
    """
    frame_color = params.frame_color
    frame_dark = (
        max(0, frame_color[0] - 30),
        max(0, frame_color[1] - 30),
        max(0, frame_color[2] - 30),
        frame_color[3]
    )
    frame_light = (
        min(255, frame_color[0] + 40),
        min(255, frame_color[1] + 40),
        min(255, frame_color[2] + 40),
        frame_color[3]
    )

    # Left lens
    _render_lens(canvas, params.left_eye_x, params.left_eye_y,
                 params.lens_width, params.lens_height,
                 params.style, frame_color, frame_dark, frame_light,
                 params.lens_tint, params.has_reflection, light_direction)

    # Right lens
    _render_lens(canvas, params.right_eye_x, params.right_eye_y,
                 params.lens_width, params.lens_height,
                 params.style, frame_color, frame_dark, frame_light,
                 params.lens_tint, params.has_reflection, light_direction)

    # Bridge
    bridge_y = (params.left_eye_y + params.right_eye_y) // 2
    bridge_start_x = params.left_eye_x + params.lens_width // 2
    bridge_end_x = params.right_eye_x - params.lens_width // 2

    for px in range(bridge_start_x, bridge_end_x + 1):
        canvas.set_pixel(px, bridge_y - 1, frame_color)
        canvas.set_pixel(px, bridge_y, frame_dark)


def _render_lens(canvas: Canvas, cx: int, cy: int, w: int, h: int,
                 style: GlassesStyle,
                 frame_color: Color, frame_dark: Color, frame_light: Color,
                 lens_tint: Optional[Color],
                 has_reflection: bool,
                 light_direction: Tuple[float, float]) -> None:
    """Render a single lens with frame."""

    # Lens fill (if tinted)
    if lens_tint:
        tint_with_alpha = (*lens_tint[:3], 60)
        if style == GlassesStyle.ROUND:
            canvas.fill_ellipse_aa(cx, cy, w // 2, h // 2, tint_with_alpha)
        else:
            # Rectangular
            for dy in range(-h // 2, h // 2 + 1):
                for dx in range(-w // 2, w // 2 + 1):
                    canvas.set_pixel(cx + dx, cy + dy, tint_with_alpha)

    # Frame outline
    if style == GlassesStyle.ROUND:
        _draw_ellipse_frame(canvas, cx, cy, w // 2, h // 2,
                            frame_color, frame_dark, frame_light)
    elif style == GlassesStyle.RECTANGULAR:
        _draw_rect_frame(canvas, cx - w // 2, cy - h // 2, w, h,
                         frame_color, frame_dark, frame_light)
    elif style == GlassesStyle.CAT_EYE:
        # Cat eye: round bottom, pointed top corners
        _draw_ellipse_frame(canvas, cx, cy, w // 2, h // 2,
                            frame_color, frame_dark, frame_light)
        # Add pointed corners
        canvas.set_pixel(cx - w // 2 - 1, cy - h // 2, frame_color)
        canvas.set_pixel(cx + w // 2 + 1, cy - h // 2, frame_color)
    else:
        # Default to round
        _draw_ellipse_frame(canvas, cx, cy, w // 2, h // 2,
                            frame_color, frame_dark, frame_light)

    # Reflection highlight
    if has_reflection:
        lx, _ = light_direction
        if lx > 0:
            # Reflection on right side
            ref_x = cx + w // 4
        else:
            ref_x = cx - w // 4

        reflection_color = (255, 255, 255, 80)
        for dy in range(-h // 3, h // 3):
            canvas.set_pixel(ref_x, cy + dy, reflection_color)
            canvas.set_pixel(ref_x + 1, cy + dy, (255, 255, 255, 40))


def _draw_ellipse_frame(canvas: Canvas, cx: int, cy: int, rx: int, ry: int,
                        color: Color, dark: Color, light: Color) -> None:
    """Draw elliptical frame with shading."""
    # Simple ellipse outline
    steps = max(rx, ry) * 4
    for i in range(steps):
        angle = 2 * math.pi * i / steps
        x = int(cx + rx * math.cos(angle))
        y = int(cy + ry * math.sin(angle))

        # Top gets highlight, bottom gets shadow
        if angle < math.pi:
            c = light if angle < math.pi / 2 else color
        else:
            c = dark if angle < 3 * math.pi / 2 else color

        canvas.set_pixel(x, y, c)


def _draw_rect_frame(canvas: Canvas, x: int, y: int, w: int, h: int,
                     color: Color, dark: Color, light: Color) -> None:
    """Draw rectangular frame with shading."""
    # Top edge (light)
    for dx in range(w):
        canvas.set_pixel(x + dx, y, light)

    # Bottom edge (dark)
    for dx in range(w):
        canvas.set_pixel(x + dx, y + h - 1, dark)

    # Left edge
    for dy in range(h):
        canvas.set_pixel(x, y + dy, color)

    # Right edge
    for dy in range(h):
        canvas.set_pixel(x + w - 1, y + dy, color)


def render_earring(canvas: Canvas, x: int, y: int,
                   style: EarringStyle,
                   color: Color = (255, 215, 0, 255),  # Gold default
                   size: int = 3) -> None:
    """
    Render an earring at the specified position.

    Args:
        canvas: Target canvas
        x, y: Earring position (ear lobe)
        style: Earring style
        color: Metal/gem color
        size: Earring size in pixels
    """
    # Shading colors
    dark = (
        max(0, color[0] - 50),
        max(0, color[1] - 50),
        max(0, color[2] - 30),
        color[3]
    )
    light = (
        min(255, color[0] + 30),
        min(255, color[1] + 30),
        min(255, color[2] + 30),
        color[3]
    )

    if style == EarringStyle.STUD:
        # Simple round stud
        canvas.fill_circle_aa(x, y, size, color)
        # Highlight
        canvas.set_pixel(x - 1, y - 1, light)

    elif style == EarringStyle.HOOP:
        # Circular hoop
        radius = size * 2
        steps = radius * 4
        for i in range(steps):
            angle = 2 * math.pi * i / steps
            px = int(x + radius * math.cos(angle))
            py = int(y + radius * math.sin(angle))
            c = light if angle < math.pi else dark
            canvas.set_pixel(px, py, c)

    elif style == EarringStyle.DROP:
        # Teardrop shape
        # Top attachment
        canvas.set_pixel(x, y, color)
        canvas.set_pixel(x, y + 1, color)
        # Gem
        gem_y = y + size + 2
        canvas.fill_circle_aa(x, gem_y, size, color)
        canvas.set_pixel(x - 1, gem_y - 1, light)

    elif style == EarringStyle.DANGLE:
        # Chain with pendant
        # Chain
        for dy in range(size * 2):
            canvas.set_pixel(x, y + dy, color if dy % 2 == 0 else dark)
        # Pendant
        pendant_y = y + size * 2 + 1
        canvas.set_pixel(x - 1, pendant_y, color)
        canvas.set_pixel(x, pendant_y, light)
        canvas.set_pixel(x + 1, pendant_y, color)
        canvas.set_pixel(x, pendant_y + 1, dark)

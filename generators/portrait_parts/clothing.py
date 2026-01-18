"""
Clothing Rendering - Necklines, collars, and fabric folds.

Provides:
- Various neckline styles (crew, v-neck, collared)
- Fabric fold patterns
- Material-appropriate shading
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


class ClothingStyle(Enum):
    """Clothing neckline styles."""
    CREW_NECK = "crew_neck"
    V_NECK = "v_neck"
    COLLARED = "collared"
    TURTLENECK = "turtleneck"
    SCOOP_NECK = "scoop_neck"
    OFF_SHOULDER = "off_shoulder"


class FabricType(Enum):
    """Fabric material types affecting shading."""
    COTTON = "cotton"     # Matte, soft shadows
    SILK = "silk"         # Shiny, sharp highlights
    DENIM = "denim"       # Textured, visible folds
    LEATHER = "leather"   # Very shiny, strong contrast


@dataclass
class ClothingParams:
    """Parameters for clothing rendering."""
    neckline_y: int           # Where neckline starts
    shoulder_left_x: int      # Left shoulder edge
    shoulder_right_x: int     # Right shoulder edge
    center_x: int             # Horizontal center
    canvas_bottom: int        # Canvas height
    style: ClothingStyle = ClothingStyle.CREW_NECK
    fabric: FabricType = FabricType.COTTON
    color_ramp: List[Color] = None  # From dark to light


def create_clothing_ramp(base_color: Color, levels: int = 5) -> List[Color]:
    """Create a color ramp for clothing shading."""
    r, g, b = base_color[0], base_color[1], base_color[2]
    alpha = base_color[3] if len(base_color) > 3 else 255

    ramp = []
    for i in range(levels):
        t = i / (levels - 1) if levels > 1 else 0.5
        # Dark to light
        factor = 0.5 + t * 0.7  # 0.5 to 1.2
        nr = min(255, int(r * factor))
        ng = min(255, int(g * factor))
        nb = min(255, int(b * factor))
        ramp.append((nr, ng, nb, alpha))

    return ramp


def render_neckline(canvas: Canvas, params: ClothingParams,
                    light_direction: Tuple[float, float] = (1.0, -1.0)) -> None:
    """
    Render clothing with neckline and basic folds.

    Args:
        canvas: Target canvas
        params: Clothing parameters
        light_direction: For shading direction
    """
    if not params.color_ramp:
        return

    # Get colors
    mid_idx = len(params.color_ramp) // 2
    base_color = params.color_ramp[mid_idx]
    dark_color = params.color_ramp[max(0, mid_idx - 1)]
    light_color = params.color_ramp[min(len(params.color_ramp) - 1, mid_idx + 1)]

    lx, _ = light_direction

    if params.style == ClothingStyle.CREW_NECK:
        _render_crew_neck(canvas, params, base_color, dark_color, light_color, lx)
    elif params.style == ClothingStyle.V_NECK:
        _render_v_neck(canvas, params, base_color, dark_color, light_color, lx)
    elif params.style == ClothingStyle.COLLARED:
        _render_collared(canvas, params, base_color, dark_color, light_color, lx)
    elif params.style == ClothingStyle.TURTLENECK:
        _render_turtleneck(canvas, params, base_color, dark_color, light_color, lx)
    else:
        # Default to crew neck
        _render_crew_neck(canvas, params, base_color, dark_color, light_color, lx)


def _render_crew_neck(canvas: Canvas, params: ClothingParams,
                      base: Color, dark: Color, light: Color,
                      light_x: float) -> None:
    """Render crew neck style."""
    cx = params.center_x
    ny = params.neckline_y
    width = params.shoulder_right_x - params.shoulder_left_x

    # Neckline opening (elliptical)
    neck_width = width // 4
    neck_height = 6

    # Fill body area
    for y in range(ny, params.canvas_bottom):
        # Narrower at top, wider at bottom
        progress = (y - ny) / max(1, params.canvas_bottom - ny)
        row_width = int(width * 0.4 + width * 0.6 * min(1, progress * 2))

        for x in range(cx - row_width // 2, cx + row_width // 2 + 1):
            # Check if in neckline opening
            if y < ny + neck_height:
                dx = abs(x - cx)
                dy = y - ny
                # Ellipse check
                if (dx / neck_width) ** 2 + (dy / neck_height) ** 2 < 1:
                    continue

            # Basic shading
            if x < cx - row_width // 4:
                color = dark if light_x > 0 else light
            elif x > cx + row_width // 4:
                color = light if light_x > 0 else dark
            else:
                color = base

            canvas.set_pixel(x, y, color)

    # Neckline edge
    edge_color = (*dark[:3], 200)
    for dx in range(-neck_width, neck_width + 1):
        t = dx / neck_width if neck_width > 0 else 0
        dy = int((1 - t ** 2) ** 0.5 * neck_height)
        canvas.set_pixel(cx + dx, ny + neck_height - dy, edge_color)


def _render_v_neck(canvas: Canvas, params: ClothingParams,
                   base: Color, dark: Color, light: Color,
                   light_x: float) -> None:
    """Render v-neck style."""
    cx = params.center_x
    ny = params.neckline_y
    width = params.shoulder_right_x - params.shoulder_left_x

    v_depth = 15
    v_width = width // 5

    # Fill body area
    for y in range(ny, params.canvas_bottom):
        progress = (y - ny) / max(1, params.canvas_bottom - ny)
        row_width = int(width * 0.4 + width * 0.6 * min(1, progress * 2))

        for x in range(cx - row_width // 2, cx + row_width // 2 + 1):
            # V-neck cutout
            if y < ny + v_depth:
                dy = y - ny
                allowed_dx = (dy / v_depth) * v_width if v_depth > 0 else 0
                if abs(x - cx) < allowed_dx:
                    continue

            # Shading
            if x < cx - row_width // 4:
                color = dark if light_x > 0 else light
            elif x > cx + row_width // 4:
                color = light if light_x > 0 else dark
            else:
                color = base

            canvas.set_pixel(x, y, color)

    # V-neck edges
    edge_color = (*dark[:3], 200)
    for dy in range(v_depth):
        dx = int((dy / v_depth) * v_width)
        canvas.set_pixel(cx - dx, ny + dy, edge_color)
        canvas.set_pixel(cx + dx, ny + dy, edge_color)


def _render_collared(canvas: Canvas, params: ClothingParams,
                     base: Color, dark: Color, light: Color,
                     light_x: float) -> None:
    """Render collared shirt style."""
    cx = params.center_x
    ny = params.neckline_y
    width = params.shoulder_right_x - params.shoulder_left_x

    # First render base like crew neck
    _render_crew_neck(canvas, params, base, dark, light, light_x)

    # Add collar
    collar_width = width // 4
    collar_height = 8

    # White collar (or slightly lighter than shirt)
    collar_color = (
        min(255, base[0] + 80),
        min(255, base[1] + 80),
        min(255, base[2] + 80),
        255
    )
    collar_shadow = (
        min(255, base[0] + 40),
        min(255, base[1] + 40),
        min(255, base[2] + 40),
        255
    )

    # Left collar flap
    for dy in range(collar_height):
        flap_width = int((1 - dy / collar_height) * collar_width * 0.6)
        for dx in range(flap_width):
            px = cx - collar_width // 2 - dx
            py = ny + dy
            color = collar_color if dx < flap_width // 2 else collar_shadow
            canvas.set_pixel(px, py, color)

    # Right collar flap
    for dy in range(collar_height):
        flap_width = int((1 - dy / collar_height) * collar_width * 0.6)
        for dx in range(flap_width):
            px = cx + collar_width // 2 + dx
            py = ny + dy
            color = collar_color if dx > flap_width // 2 else collar_shadow
            canvas.set_pixel(px, py, color)


def _render_turtleneck(canvas: Canvas, params: ClothingParams,
                       base: Color, dark: Color, light: Color,
                       light_x: float) -> None:
    """Render turtleneck style."""
    cx = params.center_x
    ny = params.neckline_y
    width = params.shoulder_right_x - params.shoulder_left_x

    turtle_height = 10
    turtle_width = width // 5

    # First render body
    for y in range(ny + turtle_height, params.canvas_bottom):
        progress = (y - ny - turtle_height) / max(1, params.canvas_bottom - ny - turtle_height)
        row_width = int(width * 0.4 + width * 0.6 * min(1, progress * 2))

        for x in range(cx - row_width // 2, cx + row_width // 2 + 1):
            if x < cx - row_width // 4:
                color = dark if light_x > 0 else light
            elif x > cx + row_width // 4:
                color = light if light_x > 0 else dark
            else:
                color = base
            canvas.set_pixel(x, y, color)

    # Turtleneck portion
    for y in range(ny, ny + turtle_height):
        for x in range(cx - turtle_width, cx + turtle_width + 1):
            # Horizontal ribbing effect
            rib_dark = (y % 2 == 0)
            if x < cx:
                color = dark if (light_x > 0 or rib_dark) else base
            else:
                color = light if (light_x > 0 and not rib_dark) else base
            canvas.set_pixel(x, y, color)


def render_collar(canvas: Canvas, cx: int, cy: int, width: int,
                  color_ramp: List[Color],
                  is_popped: bool = False) -> None:
    """Render a standalone collar detail."""
    if not color_ramp:
        return

    mid = len(color_ramp) // 2
    main_color = color_ramp[mid]
    shadow = color_ramp[max(0, mid - 1)]
    highlight = color_ramp[min(len(color_ramp) - 1, mid + 1)]

    collar_height = 6
    half_width = width // 2

    # Left collar point
    for dy in range(collar_height):
        point_width = int((1 - dy / collar_height) * half_width * 0.5)
        for dx in range(point_width):
            canvas.set_pixel(cx - half_width + dx, cy + dy, main_color)

    # Right collar point
    for dy in range(collar_height):
        point_width = int((1 - dy / collar_height) * half_width * 0.5)
        for dx in range(point_width):
            canvas.set_pixel(cx + half_width - dx, cy + dy, main_color)

    # Collar shadows
    canvas.set_pixel(cx - half_width, cy, shadow)
    canvas.set_pixel(cx + half_width, cy, shadow)

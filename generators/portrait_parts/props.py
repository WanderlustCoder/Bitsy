"""
Anime Portrait Props

Provides props (held items) for anime portrait rendering.
Props attach to skeleton bones and render with appropriate depth.
"""

import math
from enum import Enum
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.canvas import Canvas
from generators.color_utils import create_hue_shifted_ramp


class PropType(Enum):
    """Types of props available."""
    BOOK_OPEN = "book_open"
    BOOK_CLOSED = "book_closed"
    CUP = "cup"
    FLOWER = "flower"
    WAND = "wand"
    SCROLL = "scroll"


@dataclass
class Prop:
    """A prop held by the character."""
    type: PropType
    attachment_hand: str = "r"           # "l" or "r" or "both"
    offset: Tuple[int, int] = (0, 0)     # Offset from hand position
    rotation: float = 0.0                 # Rotation in degrees
    scale: float = 1.0                    # Size multiplier
    color: Tuple[int, int, int] = (139, 90, 60)  # Primary color
    secondary_color: Optional[Tuple[int, int, int]] = None


def render_prop(
    canvas: Canvas,
    prop: Prop,
    hand_positions: Dict[str, Tuple[int, int]],
    use_rim_light: bool = True,
    rim_light_color: Tuple[int, int, int] = (180, 200, 255)
) -> None:
    """
    Render a prop at the appropriate hand position.

    Args:
        buffer: Target buffer
        prop: Prop to render
        hand_positions: Dict mapping "l"/"r" to hand positions
        use_rim_light: Whether to apply rim lighting
        rim_light_color: Color for rim light
    """
    # Get attachment position
    if prop.attachment_hand == "both":
        # Between both hands
        pos_l = hand_positions.get("l", (0, 0))
        pos_r = hand_positions.get("r", (0, 0))
        base_pos = ((pos_l[0] + pos_r[0]) // 2, (pos_l[1] + pos_r[1]) // 2)
    else:
        base_pos = hand_positions.get(prop.attachment_hand, (0, 0))

    # Apply offset
    pos = (base_pos[0] + prop.offset[0], base_pos[1] + prop.offset[1])

    # Render based on type
    if prop.type == PropType.BOOK_OPEN:
        _render_book_open(buffer, pos, prop, use_rim_light, rim_light_color)
    elif prop.type == PropType.BOOK_CLOSED:
        _render_book_closed(buffer, pos, prop, use_rim_light, rim_light_color)
    elif prop.type == PropType.CUP:
        _render_cup(buffer, pos, prop, use_rim_light, rim_light_color)
    elif prop.type == PropType.FLOWER:
        _render_flower(buffer, pos, prop, use_rim_light, rim_light_color)
    elif prop.type == PropType.WAND:
        _render_wand(buffer, pos, prop, use_rim_light, rim_light_color)
    elif prop.type == PropType.SCROLL:
        _render_scroll(buffer, pos, prop, use_rim_light, rim_light_color)


def _render_book_open(
    canvas: Canvas,
    pos: Tuple[int, int],
    prop: Prop,
    use_rim_light: bool,
    rim_light_color: Tuple[int, int, int]
):
    """Render an open book."""
    # Book dimensions
    width = int(20 * prop.scale)
    height = int(14 * prop.scale)

    # Create color ramps
    cover_ramp = create_hue_shifted_ramp(prop.color, 6)
    page_color = prop.secondary_color or (250, 245, 235)
    page_ramp = create_hue_shifted_ramp(page_color, 6)

    # Apply rotation
    cos_r = math.cos(math.radians(prop.rotation))
    sin_r = math.sin(math.radians(prop.rotation))

    # Draw book pages (center)
    page_width = width - 4
    page_height = height - 2

    for dy in range(-page_height // 2, page_height // 2 + 1):
        for dx in range(-page_width // 2, page_width // 2 + 1):
            # Rotate
            rx = int(dx * cos_r - dy * sin_r)
            ry = int(dx * sin_r + dy * cos_r)
            px, py = pos[0] + rx, pos[1] + ry

            if 0 <= px < canvas.width and 0 <= py < canvas.height:
                # Page shading
                if abs(dx) > page_width // 2 - 2:
                    color = page_ramp[2]  # Edge shadow
                else:
                    color = page_ramp[4]  # Page white
                canvas.set_pixel(px, py, color)

    # Draw spine
    spine_x = pos[0]
    for dy in range(-height // 2, height // 2 + 1):
        ry = int(dy * cos_r)
        py = pos[1] + ry

        if 0 <= spine_x < canvas.width and 0 <= py < canvas.height:
            canvas.set_pixel(spine_x, py, cover_ramp[2])

    # Draw cover edges (left and right)
    for dy in range(-height // 2, height // 2 + 1):
        # Left cover edge
        dx = -width // 2
        rx = int(dx * cos_r - dy * sin_r)
        ry = int(dx * sin_r + dy * cos_r)
        px, py = pos[0] + rx, pos[1] + ry

        if 0 <= px < canvas.width and 0 <= py < canvas.height:
            if use_rim_light and dy < -height // 2 + 2:
                color = _blend_colors(cover_ramp[4], rim_light_color, 0.3)
            else:
                color = cover_ramp[3]
            canvas.set_pixel(px, py, color)

        # Right cover edge
        dx = width // 2
        rx = int(dx * cos_r - dy * sin_r)
        ry = int(dx * sin_r + dy * cos_r)
        px, py = pos[0] + rx, pos[1] + ry

        if 0 <= px < canvas.width and 0 <= py < canvas.height:
            if use_rim_light and dy < -height // 2 + 2:
                color = _blend_colors(cover_ramp[4], rim_light_color, 0.3)
            else:
                color = cover_ramp[3]
            canvas.set_pixel(px, py, color)


def _render_book_closed(
    canvas: Canvas,
    pos: Tuple[int, int],
    prop: Prop,
    use_rim_light: bool,
    rim_light_color: Tuple[int, int, int]
):
    """Render a closed book."""
    width = int(10 * prop.scale)
    height = int(14 * prop.scale)
    thickness = int(4 * prop.scale)

    cover_ramp = create_hue_shifted_ramp(prop.color, 6)
    page_color = (250, 245, 235)

    cos_r = math.cos(math.radians(prop.rotation))
    sin_r = math.sin(math.radians(prop.rotation))

    # Draw book cover
    for dy in range(-height // 2, height // 2 + 1):
        for dx in range(-width // 2, width // 2 + 1):
            rx = int(dx * cos_r - dy * sin_r)
            ry = int(dx * sin_r + dy * cos_r)
            px, py = pos[0] + rx, pos[1] + ry

            if 0 <= px < canvas.width and 0 <= py < canvas.height:
                # Edge detection
                is_edge = abs(dx) > width // 2 - 2 or abs(dy) > height // 2 - 2

                if is_edge:
                    if use_rim_light and dy < -height // 2 + 2:
                        color = _blend_colors(cover_ramp[4], rim_light_color, 0.3)
                    else:
                        color = cover_ramp[2]
                else:
                    color = cover_ramp[3]

                canvas.set_pixel(px, py, color)

    # Draw page edges
    page_edge_x = pos[0] + int((width // 2 + 1) * cos_r)
    for dy in range(-height // 2 + 2, height // 2 - 1):
        ry = int(dy * cos_r)
        py = pos[1] + ry

        if 0 <= page_edge_x < canvas.width and 0 <= py < canvas.height:
            canvas.set_pixel(page_edge_x, py, (*page_color, 255))


def _render_cup(
    canvas: Canvas,
    pos: Tuple[int, int],
    prop: Prop,
    use_rim_light: bool,
    rim_light_color: Tuple[int, int, int]
):
    """Render a cup/mug."""
    width = int(8 * prop.scale)
    height = int(10 * prop.scale)

    cup_ramp = create_hue_shifted_ramp(prop.color, 6)

    # Cup body (cylinder-ish)
    for dy in range(-height // 2, height // 2 + 1):
        # Width varies - wider at top
        t = (dy + height // 2) / height
        row_width = int(width * (0.8 + 0.2 * (1 - t)))

        for dx in range(-row_width // 2, row_width // 2 + 1):
            px, py = pos[0] + dx, pos[1] + dy

            if 0 <= px < canvas.width and 0 <= py < canvas.height:
                dist = abs(dx) / max(1, row_width // 2)

                if dist > 0.8:
                    if use_rim_light and dx > 0:
                        color = _blend_colors(cup_ramp[4], rim_light_color, 0.3)
                    else:
                        color = cup_ramp[2]
                elif dist < 0.3:
                    color = cup_ramp[4]
                else:
                    color = cup_ramp[3]

                canvas.set_pixel(px, py, color)

    # Handle
    handle_x = pos[0] + width // 2 + 2
    for dy in range(-height // 4, height // 4 + 1):
        py = pos[1] + dy
        if 0 <= handle_x < canvas.width and 0 <= py < canvas.height:
            canvas.set_pixel(handle_x, py, cup_ramp[3])


def _render_flower(
    canvas: Canvas,
    pos: Tuple[int, int],
    prop: Prop,
    use_rim_light: bool,
    rim_light_color: Tuple[int, int, int]
):
    """Render a simple flower."""
    petal_color = prop.color
    center_color = prop.secondary_color or (255, 220, 100)

    petal_ramp = create_hue_shifted_ramp(petal_color, 6)
    center_ramp = create_hue_shifted_ramp(center_color, 6)

    petal_radius = int(4 * prop.scale)
    center_radius = int(2 * prop.scale)

    # Draw petals (5 around center)
    for i in range(5):
        angle = math.radians(72 * i + prop.rotation)
        petal_x = int(pos[0] + math.cos(angle) * petal_radius)
        petal_y = int(pos[1] + math.sin(angle) * petal_radius)

        # Draw petal as small circle
        for dy in range(-petal_radius, petal_radius + 1):
            for dx in range(-petal_radius, petal_radius + 1):
                px, py = petal_x + dx, petal_y + dy

                if 0 <= px < canvas.width and 0 <= py < canvas.height:
                    dist = math.sqrt(dx*dx + dy*dy)
                    if dist <= petal_radius:
                        rel_dist = dist / petal_radius
                        if rel_dist > 0.7:
                            color = petal_ramp[2]
                        elif rel_dist < 0.3:
                            color = petal_ramp[4]
                        else:
                            color = petal_ramp[3]
                        canvas.set_pixel(px, py, color)

    # Draw center
    for dy in range(-center_radius, center_radius + 1):
        for dx in range(-center_radius, center_radius + 1):
            px, py = pos[0] + dx, pos[1] + dy

            if 0 <= px < canvas.width and 0 <= py < canvas.height:
                dist = math.sqrt(dx*dx + dy*dy)
                if dist <= center_radius:
                    canvas.set_pixel(px, py, center_ramp[3])


def _render_wand(
    canvas: Canvas,
    pos: Tuple[int, int],
    prop: Prop,
    use_rim_light: bool,
    rim_light_color: Tuple[int, int, int]
):
    """Render a wand/staff."""
    length = int(16 * prop.scale)
    width = int(2 * prop.scale)

    wand_ramp = create_hue_shifted_ramp(prop.color, 6)

    cos_r = math.cos(math.radians(prop.rotation))
    sin_r = math.sin(math.radians(prop.rotation))

    # Draw wand shaft
    for i in range(length):
        t = i / max(1, length - 1)
        dx = int((i - length // 2) * cos_r)
        dy = int((i - length // 2) * sin_r)

        px, py = pos[0] + dx, pos[1] + dy

        if 0 <= px < canvas.width and 0 <= py < canvas.height:
            # Slightly thicker at base
            local_width = int(width * (1.0 - t * 0.3))
            for w in range(-local_width, local_width + 1):
                wx = int(px - w * sin_r)
                wy = int(py + w * cos_r)
                if 0 <= wx < canvas.width and 0 <= wy < canvas.height:
                    color = wand_ramp[3] if w == 0 else wand_ramp[2]
                    canvas.set_pixel(wx, wy, color)

    # Draw tip sparkle
    tip_x = int(pos[0] + (length // 2) * cos_r)
    tip_y = int(pos[1] + (length // 2) * sin_r)

    if prop.secondary_color:
        sparkle_color = prop.secondary_color
    else:
        sparkle_color = (255, 255, 200)

    if 0 <= tip_x < canvas.width and 0 <= tip_y < canvas.height:
        canvas.set_pixel(tip_x, tip_y, (*sparkle_color, 255))
        # Small cross sparkle
        for d in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            sx, sy = tip_x + d[0], tip_y + d[1]
            if 0 <= sx < canvas.width and 0 <= sy < canvas.height:
                canvas.set_pixel(sx, sy, (*sparkle_color, 255))


def _render_scroll(
    canvas: Canvas,
    pos: Tuple[int, int],
    prop: Prop,
    use_rim_light: bool,
    rim_light_color: Tuple[int, int, int]
):
    """Render a rolled scroll."""
    width = int(12 * prop.scale)
    height = int(8 * prop.scale)

    paper_color = prop.color if prop.color != (139, 90, 60) else (250, 240, 220)
    paper_ramp = create_hue_shifted_ramp(paper_color, 6)

    cos_r = math.cos(math.radians(prop.rotation))
    sin_r = math.sin(math.radians(prop.rotation))

    # Main scroll body
    for dy in range(-height // 2, height // 2 + 1):
        for dx in range(-width // 2, width // 2 + 1):
            rx = int(dx * cos_r - dy * sin_r)
            ry = int(dx * sin_r + dy * cos_r)
            px, py = pos[0] + rx, pos[1] + ry

            if 0 <= px < canvas.width and 0 <= py < canvas.height:
                # Cylindrical shading (horizontal curve)
                curve_t = abs(dy) / max(1, height // 2)
                if curve_t > 0.7:
                    color = paper_ramp[2]
                elif curve_t < 0.3:
                    color = paper_ramp[4]
                else:
                    color = paper_ramp[3]

                canvas.set_pixel(px, py, color)

    # Roll ends (left and right)
    roll_radius = height // 2 + 1
    for side in [-1, 1]:
        roll_x = pos[0] + int(side * (width // 2 + 1) * cos_r)
        roll_y = pos[1] + int(side * (width // 2 + 1) * sin_r)

        for dy in range(-roll_radius, roll_radius + 1):
            ry = int(dy * cos_r)
            py = roll_y + ry

            if 0 <= roll_x < canvas.width and 0 <= py < canvas.height:
                color = paper_ramp[2] if abs(dy) > roll_radius - 1 else paper_ramp[3]
                canvas.set_pixel(roll_x, py, color)


def _blend_colors(
    color1: Tuple[int, int, int, int],
    color2: Tuple[int, int, int],
    blend: float
) -> Tuple[int, int, int, int]:
    """Blend two colors."""
    return (
        int(color1[0] * (1 - blend) + color2[0] * blend),
        int(color1[1] * (1 - blend) + color2[1] * blend),
        int(color1[2] * (1 - blend) + color2[2] * blend),
        color1[3] if len(color1) > 3 else 255
    )


# Pre-defined prop configurations
PRESET_PROPS = {
    "book_brown": Prop(
        type=PropType.BOOK_OPEN,
        attachment_hand="both",
        color=(139, 90, 60),
        secondary_color=(250, 245, 235)
    ),
    "book_red": Prop(
        type=PropType.BOOK_CLOSED,
        attachment_hand="r",
        color=(140, 50, 50),
    ),
    "teacup_white": Prop(
        type=PropType.CUP,
        attachment_hand="r",
        color=(240, 240, 245),
    ),
    "teacup_blue": Prop(
        type=PropType.CUP,
        attachment_hand="r",
        color=(100, 140, 180),
    ),
    "rose": Prop(
        type=PropType.FLOWER,
        attachment_hand="r",
        color=(200, 80, 100),
        secondary_color=(255, 220, 100)
    ),
    "sunflower": Prop(
        type=PropType.FLOWER,
        attachment_hand="r",
        color=(255, 200, 50),
        secondary_color=(100, 70, 40)
    ),
    "magic_wand": Prop(
        type=PropType.WAND,
        attachment_hand="r",
        color=(80, 50, 30),
        secondary_color=(200, 220, 255),
        rotation=-45
    ),
    "scroll": Prop(
        type=PropType.SCROLL,
        attachment_hand="both",
        color=(250, 240, 220),
    ),
}


def get_preset_prop(name: str) -> Optional[Prop]:
    """Get a preset prop configuration by name."""
    return PRESET_PROPS.get(name)

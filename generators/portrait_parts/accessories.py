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


class NecklaceStyle(Enum):
    """Necklace styles."""
    CHAIN = "chain"
    CHOKER = "choker"
    PENDANT = "pendant"
    PEARL = "pearl"


class HairAccessoryStyle(Enum):
    """Hair accessory styles."""
    HEADBAND = "headband"
    BOW = "bow"
    CLIP = "clip"
    SCRUNCHIE = "scrunchie"


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

    # Reflection highlight (improved with gradient)
    if has_reflection:
        lx, _ = light_direction
        if lx > 0:
            ref_x = cx + w // 4
        else:
            ref_x = cx - w // 4

        # Main reflection stripe
        for dy in range(-h // 3, h // 3):
            # Gradient from bright to dim
            dist_from_center = abs(dy) / max(1, h // 3)
            base_alpha = int(100 * (1 - dist_from_center * 0.5))

            canvas.set_pixel(ref_x - 1, cy + dy, (255, 255, 255, base_alpha // 3))
            canvas.set_pixel(ref_x, cy + dy, (255, 255, 255, base_alpha))
            canvas.set_pixel(ref_x + 1, cy + dy, (255, 255, 255, base_alpha // 2))

        # Small secondary reflection
        ref_x2 = cx - w // 5 if lx > 0 else cx + w // 5
        for dy in range(-h // 5, h // 6):
            canvas.set_pixel(ref_x2, cy + dy + h // 8, (255, 255, 255, 30))


def _draw_ellipse_frame(canvas: Canvas, cx: int, cy: int, rx: int, ry: int,
                        color: Color, dark: Color, light: Color) -> None:
    """Draw elliptical frame with thick shading (2-3 pixel rim)."""
    steps = max(rx, ry) * 6

    # Draw multiple rings for thickness
    for ring in range(3):
        ring_rx = rx + ring
        ring_ry = ry + ring

        for i in range(steps):
            angle = 2 * math.pi * i / steps
            x = int(cx + ring_rx * math.cos(angle))
            y = int(cy + ring_ry * math.sin(angle))

            # Determine color based on angle and ring
            if ring == 0:
                # Inner ring: darker
                if angle < math.pi:
                    c = color
                else:
                    c = dark
            elif ring == 1:
                # Middle ring: base color
                if angle < math.pi / 2:
                    c = light
                elif angle < math.pi:
                    c = color
                else:
                    c = dark
            else:
                # Outer ring: highlight on top, dark on bottom
                if angle < math.pi / 2 or angle > 3 * math.pi / 2:
                    c = light
                else:
                    c = dark

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


def render_necklace(canvas: Canvas, cx: int, neck_y: int,
                    neck_width: int,
                    style: NecklaceStyle,
                    color: Color = (255, 215, 0, 255),  # Gold default
                    size: int = 2) -> None:
    """
    Render a necklace at the neck position.

    Args:
        canvas: Target canvas
        cx: Center x position
        neck_y: Y position of the neckline
        neck_width: Width of the neck/neckline
        style: Necklace style
        color: Metal/gem color
        size: Chain/element size
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

    if style == NecklaceStyle.CHAIN:
        _render_chain_necklace(canvas, cx, neck_y, neck_width, color, dark, size)

    elif style == NecklaceStyle.CHOKER:
        _render_choker(canvas, cx, neck_y, neck_width, color, dark, light, size)

    elif style == NecklaceStyle.PENDANT:
        _render_pendant_necklace(canvas, cx, neck_y, neck_width, color, dark, light, size)

    elif style == NecklaceStyle.PEARL:
        _render_pearl_necklace(canvas, cx, neck_y, neck_width, color, light, size)


def _render_chain_necklace(canvas: Canvas, cx: int, y: int, width: int,
                           color: Color, dark: Color, size: int) -> None:
    """Render a simple chain necklace."""
    # Chain follows a gentle curve
    half_width = width // 2

    for dx in range(-half_width, half_width + 1):
        # Curved shape dipping in center
        curve = int((dx / half_width) ** 2 * size * 2)
        py = y + curve

        # Alternating chain links
        if abs(dx) % (size + 1) == 0:
            canvas.set_pixel(cx + dx, py, color)
        else:
            canvas.set_pixel(cx + dx, py, dark)


def _render_choker(canvas: Canvas, cx: int, y: int, width: int,
                   color: Color, dark: Color, light: Color, size: int) -> None:
    """Render a close-fitting choker necklace."""
    half_width = width // 2

    # Choker band (2-3 pixels tall)
    for dy in range(size):
        for dx in range(-half_width, half_width + 1):
            if dy == 0:
                c = light  # Top edge highlight
            elif dy == size - 1:
                c = dark  # Bottom edge shadow
            else:
                c = color
            canvas.set_pixel(cx + dx, y + dy, c)

    # Center decoration
    canvas.set_pixel(cx, y + size // 2, light)


def _render_pendant_necklace(canvas: Canvas, cx: int, y: int, width: int,
                             color: Color, dark: Color, light: Color, size: int) -> None:
    """Render a necklace with a pendant."""
    half_width = width // 2

    # Chain part
    for dx in range(-half_width, half_width + 1):
        curve = int((dx / half_width) ** 2 * size * 3)
        py = y + curve

        # Thinner chain
        if abs(dx) % 2 == 0:
            canvas.set_pixel(cx + dx, py, color)

    # Pendant at center
    pendant_y = y + size * 3 + 1
    pendant_size = max(2, size)

    # Diamond/teardrop shape
    for dy in range(pendant_size * 2):
        pw = pendant_size - abs(dy - pendant_size // 2)
        for ddx in range(-pw, pw + 1):
            if dy < pendant_size:
                c = light if ddx <= 0 else color
            else:
                c = color if ddx <= 0 else dark
            canvas.set_pixel(cx + ddx, pendant_y + dy, c)


def _render_pearl_necklace(canvas: Canvas, cx: int, y: int, width: int,
                           color: Color, light: Color, size: int) -> None:
    """Render a pearl strand necklace."""
    half_width = width // 2
    pearl_spacing = size + 2

    # Place pearls along a curve
    num_pearls = (half_width * 2) // pearl_spacing

    for i in range(num_pearls + 1):
        # Position along necklace
        t = (i / num_pearls) - 0.5  # -0.5 to 0.5
        dx = int(t * half_width * 2)

        # Curved shape
        curve = int((t * 2) ** 2 * size * 2)
        py = y + curve

        # Pearl (small circle with highlight)
        canvas.fill_circle_aa(cx + dx, py, size, color)
        # Highlight
        canvas.set_pixel(cx + dx - 1, py - 1, light)


def render_hair_accessory(canvas: Canvas, cx: int, hair_top_y: int,
                          hair_width: int, style: HairAccessoryStyle,
                          color: Color = (255, 100, 150, 255),  # Pink default
                          size: int = 3) -> None:
    """
    Render a hair accessory at the specified position.

    Args:
        canvas: Target canvas
        cx: Center x position
        hair_top_y: Y position of the top of hair
        hair_width: Width of the hair area
        style: Hair accessory style
        color: Accessory color
        size: Accessory size in pixels
    """
    # Shading colors
    dark = (
        max(0, color[0] - 50),
        max(0, color[1] - 50),
        max(0, color[2] - 50),
        color[3]
    )
    light = (
        min(255, color[0] + 40),
        min(255, color[1] + 40),
        min(255, color[2] + 40),
        color[3]
    )

    if style == HairAccessoryStyle.HEADBAND:
        _render_headband(canvas, cx, hair_top_y, hair_width, color, dark, light, size)
    elif style == HairAccessoryStyle.BOW:
        _render_bow(canvas, cx, hair_top_y, hair_width, color, dark, light, size)
    elif style == HairAccessoryStyle.CLIP:
        _render_clip(canvas, cx, hair_top_y, hair_width, color, dark, light, size)
    elif style == HairAccessoryStyle.SCRUNCHIE:
        _render_scrunchie(canvas, cx, hair_top_y, hair_width, color, dark, light, size)


def _render_headband(canvas: Canvas, cx: int, y: int, width: int,
                     color: Color, dark: Color, light: Color, size: int) -> None:
    """Render a headband across the top of the head."""
    half_width = width // 2 - size

    # Headband follows a slight curve over the head
    band_height = size

    for dx in range(-half_width, half_width + 1):
        # Curved shape (higher at center)
        curve = -int((1 - (dx / half_width) ** 2) * size * 1.5)
        base_y = y + size * 2 + curve

        # Draw band with shading
        for dy in range(band_height):
            if dy == 0:
                c = light  # Top edge highlight
            elif dy == band_height - 1:
                c = dark  # Bottom edge shadow
            else:
                c = color
            canvas.set_pixel(cx + dx, base_y + dy, c)

    # Side decorations or bumps
    for side in [-1, 1]:
        edge_x = cx + side * (half_width - size)
        canvas.set_pixel(edge_x, y + size * 2 - 1, light)
        canvas.set_pixel(edge_x, y + size * 2, color)


def _render_bow(canvas: Canvas, cx: int, y: int, width: int,
                color: Color, dark: Color, light: Color, size: int) -> None:
    """Render a bow on top of the head."""
    # Position bow on top-right of head
    bow_x = cx + width // 4
    bow_y = y + size * 3

    # Bow loops (left and right)
    loop_size = size * 2

    for side in [-1, 1]:
        loop_cx = bow_x + side * loop_size
        # Draw oval loop
        for angle_step in range(24):
            angle = (angle_step / 24) * 2 * math.pi
            px = int(loop_cx + loop_size * math.cos(angle))
            py = int(bow_y + loop_size * 0.6 * math.sin(angle))

            # Shading based on position
            if angle < math.pi:
                c = light if side == 1 else color
            else:
                c = dark if side == 1 else color
            canvas.set_pixel(px, py, c)

        # Fill loop interior
        for dy in range(-loop_size // 2, loop_size // 2 + 1):
            for ddx in range(-loop_size + 1, loop_size):
                # Check if inside ellipse
                if (ddx / loop_size) ** 2 + (dy / (loop_size * 0.6)) ** 2 < 0.8:
                    px, py_pos = loop_cx + ddx, bow_y + dy
                    # Gradient from top-light to bottom-dark
                    if dy < 0:
                        canvas.set_pixel(px, py_pos, light)
                    elif dy > loop_size // 4:
                        canvas.set_pixel(px, py_pos, dark)
                    else:
                        canvas.set_pixel(px, py_pos, color)

    # Center knot
    knot_size = size
    for dy in range(-knot_size, knot_size + 1):
        for ddx in range(-knot_size, knot_size + 1):
            if abs(ddx) + abs(dy) <= knot_size:
                if ddx < 0 and dy < 0:
                    canvas.set_pixel(bow_x + ddx, bow_y + dy, light)
                elif ddx > 0 and dy > 0:
                    canvas.set_pixel(bow_x + ddx, bow_y + dy, dark)
                else:
                    canvas.set_pixel(bow_x + ddx, bow_y + dy, color)

    # Ribbon tails
    for tail in range(2):
        tail_x = bow_x + (tail * 2 - 1) * size // 2
        for t_dy in range(size * 3):
            # Wavy tail
            wave = int(math.sin(t_dy * 0.5) * 2)
            canvas.set_pixel(tail_x + wave, bow_y + knot_size + t_dy, color)
            if t_dy < size:
                canvas.set_pixel(tail_x + wave + 1, bow_y + knot_size + t_dy, dark)


def _render_clip(canvas: Canvas, cx: int, y: int, width: int,
                 color: Color, dark: Color, light: Color, size: int) -> None:
    """Render a hair clip on the side of the head."""
    # Position clip on the side
    clip_x = cx + width // 3
    clip_y = y + size * 4

    clip_width = size * 3
    clip_height = size

    # Clip body (rectangular with rounded edges)
    for dy in range(clip_height):
        for dx in range(clip_width):
            # Skip corners for rounded effect
            if (dx == 0 or dx == clip_width - 1) and (dy == 0 or dy == clip_height - 1):
                continue

            if dy == 0:
                c = light
            elif dy == clip_height - 1:
                c = dark
            else:
                c = color
            canvas.set_pixel(clip_x + dx, clip_y + dy, c)

    # Clip mechanism (small details)
    # Top clasp
    canvas.set_pixel(clip_x + clip_width // 2, clip_y - 1, dark)
    canvas.set_pixel(clip_x + clip_width // 2 + 1, clip_y - 1, dark)

    # Decorative gem/dot in center
    gem_x = clip_x + clip_width // 2
    gem_y = clip_y + clip_height // 2
    canvas.set_pixel(gem_x, gem_y, (255, 255, 255, 200))  # Small sparkle


def _render_scrunchie(canvas: Canvas, cx: int, y: int, width: int,
                      color: Color, dark: Color, light: Color, size: int) -> None:
    """Render a scrunchie/hair tie, typically for ponytail/bun styles."""
    # Position at back of head (for ponytail base)
    scrunchie_x = cx
    scrunchie_y = y + size * 2

    # Scrunchie is a gathered ring
    outer_radius = size * 2
    inner_radius = size

    # Draw gathered fabric ring
    num_gathers = 12
    for i in range(num_gathers):
        angle = (i / num_gathers) * 2 * math.pi
        gather_variation = 1 + 0.3 * math.sin(i * 3)  # Puffy gathers

        # Outer edge of gather
        outer_x = int(scrunchie_x + outer_radius * gather_variation * math.cos(angle))
        outer_y = int(scrunchie_y + outer_radius * gather_variation * 0.6 * math.sin(angle))

        # Inner edge of gather
        inner_x = int(scrunchie_x + inner_radius * math.cos(angle))
        inner_y = int(scrunchie_y + inner_radius * 0.6 * math.sin(angle))

        # Draw gathered segment
        steps = 5
        for t in range(steps + 1):
            t_ratio = t / steps
            px = int(inner_x + (outer_x - inner_x) * t_ratio)
            py = int(inner_y + (outer_y - inner_y) * t_ratio)

            # Shading: top is light, bottom is dark
            if angle < math.pi:
                if t_ratio < 0.3:
                    c = dark
                elif t_ratio > 0.7:
                    c = light
                else:
                    c = color
            else:
                if t_ratio < 0.3:
                    c = light
                elif t_ratio > 0.7:
                    c = dark
                else:
                    c = color

            canvas.set_pixel(px, py, c)

    # Fill in the ring with puffy texture
    for angle_step in range(36):
        angle = (angle_step / 36) * 2 * math.pi
        mid_radius = (outer_radius + inner_radius) / 2
        gather = 1 + 0.15 * math.sin(angle_step * 3)

        px = int(scrunchie_x + mid_radius * gather * math.cos(angle))
        py = int(scrunchie_y + mid_radius * gather * 0.6 * math.sin(angle))

        if angle < math.pi * 0.5 or angle > math.pi * 1.5:
            canvas.set_pixel(px, py, light)
        elif math.pi * 0.5 < angle < math.pi:
            canvas.set_pixel(px, py, color)
        else:
            canvas.set_pixel(px, py, dark)

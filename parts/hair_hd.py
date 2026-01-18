"""
High-Detail Hair Styles - Enhanced hair rendering for HD sprites.

Provides high-detail hair styles with:
- Multiple highlight layers
- Complex shading with many shapes
- Hair strand textures
- Specular highlights

These styles are optimized for 64x64+ sprites where detail is visible.
"""

import math
from typing import Optional, List, Tuple
from dataclasses import dataclass

from .base import Part, PartConfig
from .hair import Hair

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.canvas import Canvas
from core.color import Color, lighten, darken, shift_hue, adjust_saturation


class HDHair(Hair):
    """Base class for high-detail hair with multiple highlight layers."""

    def __init__(self, name: str, config: Optional[PartConfig] = None):
        super().__init__(name, config)
        self.highlight_layers = 3  # Number of highlight gradations
        self.detail_level = 'high'  # 'low', 'medium', 'high'

    def _get_highlight_colors(self, base_colors: List[Color]) -> List[Color]:
        """Get multiple highlight colors for layered effect.

        Creates progressively brighter highlights with slight hue shifts.
        """
        if not base_colors:
            return []

        base_highlight = base_colors[0]
        highlights = [base_highlight]

        for i in range(1, self.highlight_layers):
            # Each layer: lighter, slightly shifted toward warm
            factor = 0.15 * i
            color = lighten(base_highlight, factor)
            color = shift_hue(color, 3 * i)  # Slight warm shift
            highlights.append(color)

        return highlights

    def _draw_hair_strand(self, canvas: Canvas, x1: int, y1: int,
                          x2: int, y2: int, color: Color) -> None:
        """Draw a curved hair strand line."""
        # Use AA line if available, otherwise regular
        if hasattr(canvas, 'draw_line_aa'):
            canvas.draw_line_aa(x1, y1, x2, y2, color)
        else:
            canvas.draw_line(x1, y1, x2, y2, color)


class BunHairHD(HDHair):
    """Complex bun hairstyle with detailed highlights.

    Features:
    - Large bun on top/back with multiple highlight layers
    - Flowing side hair
    - Detailed bangs with layered shading
    - Hair strand texture
    """

    def __init__(self, config: Optional[PartConfig] = None):
        super().__init__("bun_hd", config)

    def draw(self, canvas: Canvas, x: int, y: int,
             width: int, height: int) -> None:
        self.draw_back(canvas, x, y, width, height)
        self.draw_bun(canvas, x, y - height // 3, int(width * 0.4))
        self.draw_front(canvas, x, y, width, height)

    def draw_back(self, canvas: Canvas, x: int, y: int,
                  width: int, height: int) -> None:
        colors = self._get_colors(5)
        if not colors:
            return

        hw, hh = width // 2, height // 2

        # Shadow layer (darkest, largest)
        shadow_color = colors[3] if len(colors) > 3 else colors[-1]
        canvas.fill_ellipse(x, y - hh // 4, int(hw * 1.1), int(hh * 0.7), shadow_color)

        # Mid-shadow layer
        mid_shadow = colors[2] if len(colors) > 2 else colors[-1]
        canvas.fill_ellipse(x - 1, y - hh // 3, int(hw * 1.0), int(hh * 0.6), mid_shadow)

        # Base layer
        base_color = colors[1] if len(colors) > 1 else colors[0]
        canvas.fill_ellipse(x - 2, y - hh // 3 - 1, int(hw * 0.9), int(hh * 0.55), base_color)

        # Side hair flowing down (shadow)
        canvas.fill_ellipse(x - hw - 2, y + hh // 4, hw // 3, int(hh * 0.6), shadow_color)
        canvas.fill_ellipse(x + hw + 2, y + hh // 4, hw // 3, int(hh * 0.6), shadow_color)

        # Side hair (lighter)
        canvas.fill_ellipse(x - hw, y + hh // 4, hw // 3 - 1, int(hh * 0.55), mid_shadow)
        canvas.fill_ellipse(x + hw, y + hh // 4, hw // 3 - 1, int(hh * 0.55), mid_shadow)

    def draw_bun(self, canvas: Canvas, x: int, y: int, size: int) -> None:
        """Draw the bun with complex highlight pattern."""
        colors = self._get_colors(5)
        if not colors:
            return

        highlights = self._get_highlight_colors(colors)

        # Bun base (shadow)
        shadow_color = colors[3] if len(colors) > 3 else colors[-1]
        canvas.fill_circle(x, y, size, shadow_color)

        # Bun mid layer
        mid_color = colors[2] if len(colors) > 2 else colors[-1]
        canvas.fill_circle(x - size // 6, y - size // 6, size - 1, mid_color)

        # Bun base tone
        base_color = colors[1] if len(colors) > 1 else colors[0]
        canvas.fill_circle(x - size // 5, y - size // 5, size - 2, base_color)

        # Primary highlight arc (large, soft)
        if highlights:
            canvas.fill_ellipse(x - size // 3, y - size // 3,
                               size // 2, size // 3, highlights[0])

        # Secondary highlight (smaller, brighter)
        if len(highlights) > 1:
            canvas.fill_ellipse(x - size // 3, y - size // 2,
                               size // 3, size // 5, highlights[1])

        # Tertiary highlight (specular spot)
        if len(highlights) > 2:
            canvas.fill_circle(x - size // 3, y - size // 3, size // 6, highlights[2])

        # Bright specular spot (nearly white)
        bright_spec = lighten(colors[0], 0.5)
        canvas.fill_circle(x - size // 4, y - size // 3, max(1, size // 10), bright_spec)

        # Hair strand texture lines
        strand_color = mid_color
        for i in range(4):
            angle = math.pi * (0.2 + 0.2 * i)
            start_x = x + int(math.cos(angle) * size * 0.2)
            start_y = y + int(math.sin(angle) * size * 0.2)
            end_x = x + int(math.cos(angle + 0.4) * size * 0.7)
            end_y = y + int(math.sin(angle + 0.4) * size * 0.7)
            self._draw_hair_strand(canvas, start_x, start_y, end_x, end_y, strand_color)

    def draw_front(self, canvas: Canvas, x: int, y: int,
                   width: int, height: int) -> None:
        colors = self._get_colors(5)
        if not colors:
            return

        if not self.has_bangs:
            return

        hw, hh = width // 2, height // 2
        highlights = self._get_highlight_colors(colors)

        # Bangs shadow layer (back)
        shadow_color = colors[2] if len(colors) > 2 else colors[-1]
        canvas.fill_ellipse(x, y - hh // 2 + 3, hw, hh // 4 + 3, shadow_color)

        # Bangs base layer
        base_color = colors[1] if len(colors) > 1 else colors[0]
        canvas.fill_ellipse(x, y - hh // 2 + 1, hw - 1, hh // 4 + 1, base_color)

        # Bangs highlight layer
        if highlights:
            canvas.fill_ellipse(x - hw // 4, y - hh // 2 - 1, hw // 2, hh // 6, highlights[0])

        # Bright highlight streak
        if len(highlights) > 1:
            canvas.fill_ellipse(x - hw // 3, y - hh // 2 - 2, hw // 3, hh // 10, highlights[1])

        # Side-swept bangs strands
        for i in range(3):
            strand_x = x - hw // 2 + i * (hw // 3)
            self._draw_hair_strand(canvas, strand_x, y - hh // 2,
                                  strand_x + 2, y - hh // 4, shadow_color)


class LongHairHD(HDHair):
    """Long flowing hair with detailed highlights."""

    def __init__(self, config: Optional[PartConfig] = None):
        super().__init__("long_hd", config)

    def draw(self, canvas: Canvas, x: int, y: int,
             width: int, height: int) -> None:
        self.draw_back(canvas, x, y, width, height)
        self.draw_front(canvas, x, y, width, height)

    def draw_back(self, canvas: Canvas, x: int, y: int,
                  width: int, height: int) -> None:
        colors = self._get_colors(5)
        if not colors:
            return

        hw, hh = width // 2, height // 2

        # Layer 1: Deepest shadow (widest)
        shadow = colors[4] if len(colors) > 4 else colors[-1]
        canvas.fill_ellipse(x, y, int(hw * 1.3), int(hh * 1.2), shadow)

        # Layer 2: Mid shadow
        mid_shadow = colors[3] if len(colors) > 3 else colors[-1]
        canvas.fill_ellipse(x - 1, y - 1, int(hw * 1.2), int(hh * 1.1), mid_shadow)

        # Layer 3: Base
        base = colors[2] if len(colors) > 2 else colors[1]
        canvas.fill_ellipse(x - 2, y - 2, int(hw * 1.1), hh, base)

        # Layer 4: Light base
        light_base = colors[1] if len(colors) > 1 else colors[0]
        canvas.fill_ellipse(x - 3, y - 3, hw, int(hh * 0.9), light_base)

        # Flowing side sections
        canvas.fill_ellipse(x - hw - 3, y + hh // 2, hw // 2, int(hh * 0.7), mid_shadow)
        canvas.fill_ellipse(x + hw + 3, y + hh // 2, hw // 2, int(hh * 0.7), mid_shadow)

        # Hair strand details
        for i in range(5):
            strand_y = y - hh // 2 + i * (hh // 4)
            self._draw_hair_strand(canvas, x - hw, strand_y, x - hw // 2, strand_y + hh // 6, shadow)
            self._draw_hair_strand(canvas, x + hw, strand_y, x + hw // 2, strand_y + hh // 6, shadow)

    def draw_front(self, canvas: Canvas, x: int, y: int,
                   width: int, height: int) -> None:
        colors = self._get_colors(5)
        if not colors:
            return

        if not self.has_bangs:
            return

        hw, hh = width // 2, height // 2
        highlights = self._get_highlight_colors(colors)

        # Layered bangs
        shadow = colors[2] if len(colors) > 2 else colors[-1]
        base = colors[1] if len(colors) > 1 else colors[0]

        # Back bang layer
        canvas.fill_ellipse(x + 2, y - hh // 2 + 2, hw, hh // 4 + 2, shadow)

        # Mid bang layer
        canvas.fill_ellipse(x, y - hh // 2, hw - 2, hh // 4, base)

        # Highlight layers
        if highlights:
            canvas.fill_ellipse(x - hw // 4, y - hh // 2 - 2, hw // 2, hh // 6, highlights[0])

        if len(highlights) > 1:
            canvas.fill_ellipse(x - hw // 3, y - hh // 2 - 3, hw // 4, hh // 10, highlights[1])

        # Side-swept strands
        canvas.fill_ellipse(x - hw + 2, y - hh // 4, hw // 4, hh // 3, shadow)
        canvas.fill_ellipse(x + hw - 2, y - hh // 4, hw // 4, hh // 3, shadow)


class PonytailHairHD(HDHair):
    """Ponytail with detailed tie and flow."""

    def __init__(self, config: Optional[PartConfig] = None):
        super().__init__("ponytail_hd", config)

    def draw(self, canvas: Canvas, x: int, y: int,
             width: int, height: int) -> None:
        self.draw_back(canvas, x, y, width, height)
        self.draw_front(canvas, x, y, width, height)

    def draw_back(self, canvas: Canvas, x: int, y: int,
                  width: int, height: int) -> None:
        colors = self._get_colors(5)
        if not colors:
            return

        hw, hh = width // 2, height // 2
        highlights = self._get_highlight_colors(colors)

        shadow = colors[3] if len(colors) > 3 else colors[-1]
        mid = colors[2] if len(colors) > 2 else colors[-1]
        base = colors[1] if len(colors) > 1 else colors[0]

        # Head hair base (shadow)
        canvas.fill_ellipse(x, y - hh // 3, int(hw * 0.9), int(hh * 0.5), shadow)

        # Head hair (mid)
        canvas.fill_ellipse(x - 1, y - hh // 3 - 1, int(hw * 0.85), int(hh * 0.45), mid)

        # Ponytail tie area
        tie_x = x + hw // 2
        tie_y = y - hh // 4
        canvas.fill_circle(tie_x, tie_y, hw // 4, shadow)
        canvas.fill_circle(tie_x - 1, tie_y - 1, hw // 4 - 1, mid)

        # Ponytail flow (shadow)
        canvas.fill_ellipse(tie_x + hw // 4, tie_y + hh // 2, hw // 3, int(hh * 0.8), shadow)

        # Ponytail flow (mid)
        canvas.fill_ellipse(tie_x + hw // 4 - 1, tie_y + hh // 2 - 2, hw // 3 - 1, int(hh * 0.75), mid)

        # Ponytail flow (base)
        canvas.fill_ellipse(tie_x + hw // 4 - 2, tie_y + hh // 2 - 3, hw // 3 - 2, int(hh * 0.7), base)

        # Ponytail highlight
        if highlights:
            canvas.fill_ellipse(tie_x + hw // 6, tie_y + hh // 3, hw // 5, hh // 4, highlights[0])

        # Hair tie detail
        tie_color = (80, 40, 40, 255)  # Dark red tie
        canvas.fill_rect(tie_x - 2, tie_y - 2, 4, 4, tie_color)

    def draw_front(self, canvas: Canvas, x: int, y: int,
                   width: int, height: int) -> None:
        colors = self._get_colors(5)
        if not colors:
            return

        if not self.has_bangs:
            return

        hw, hh = width // 2, height // 2
        highlights = self._get_highlight_colors(colors)

        shadow = colors[2] if len(colors) > 2 else colors[-1]
        base = colors[1] if len(colors) > 1 else colors[0]

        # Cap-style bangs (shadow)
        canvas.fill_ellipse(x, y - hh // 2 + 2, hw - 2, hh // 5 + 2, shadow)

        # Cap-style bangs (base)
        canvas.fill_ellipse(x - 1, y - hh // 2, hw - 3, hh // 5, base)

        # Highlight
        if highlights:
            canvas.fill_ellipse(x - hw // 4, y - hh // 2 - 1, hw // 3, hh // 8, highlights[0])


class ShortHairHD(HDHair):
    """Short textured hair with detailed shading."""

    def __init__(self, config: Optional[PartConfig] = None):
        super().__init__("short_hd", config)
        self.has_back = False  # Short hair doesn't extend behind head

    def draw(self, canvas: Canvas, x: int, y: int,
             width: int, height: int) -> None:
        colors = self._get_colors(5)
        if not colors:
            return

        hw, hh = width // 2, height // 2
        highlights = self._get_highlight_colors(colors)

        shadow = colors[3] if len(colors) > 3 else colors[-1]
        mid = colors[2] if len(colors) > 2 else colors[-1]
        base = colors[1] if len(colors) > 1 else colors[0]

        # Base cap shape (shadow)
        canvas.fill_ellipse(x, y - hh // 3, hw, int(hh * 0.4), shadow)

        # Base cap (mid)
        canvas.fill_ellipse(x - 1, y - hh // 3 - 1, hw - 1, int(hh * 0.38), mid)

        # Base cap (base)
        canvas.fill_ellipse(x - 2, y - hh // 3 - 2, hw - 2, int(hh * 0.35), base)

        # Texture circles for short hair effect
        for i in range(6):
            tx = x + self._random_int(-hw // 2, hw // 2)
            ty = y - hh // 3 + self._random_int(-hh // 6, hh // 6)
            tr = max(2, self._random_int(2, 4))
            canvas.fill_circle(tx, ty, tr, mid)

        # Highlight
        if highlights:
            canvas.fill_ellipse(x - hw // 4, y - hh // 2, hw // 2, hh // 6, highlights[0])

        # Bright specular
        if len(highlights) > 1:
            canvas.fill_circle(x - hw // 3, y - hh // 2 + 1, 2, highlights[1])

    def draw_back(self, canvas: Canvas, x: int, y: int,
                  width: int, height: int) -> None:
        pass  # Short hair doesn't have back layer

    def draw_front(self, canvas: Canvas, x: int, y: int,
                   width: int, height: int) -> None:
        pass  # Integrated into main draw


# Registry of HD hair types
HD_HAIR_TYPES = {
    'bun_hd': BunHairHD,
    'long_hd': LongHairHD,
    'ponytail_hd': PonytailHairHD,
    'short_hd': ShortHairHD,
}


def create_hd_hair(hair_type: str, config: Optional[PartConfig] = None) -> HDHair:
    """Create an HD hair instance by type name.

    Args:
        hair_type: Type of HD hair ('bun_hd', 'long_hd', etc.)
        config: Optional configuration

    Returns:
        HDHair instance
    """
    if hair_type not in HD_HAIR_TYPES:
        available = ', '.join(HD_HAIR_TYPES.keys())
        raise ValueError(f"Unknown HD hair type '{hair_type}'. Available: {available}")

    return HD_HAIR_TYPES[hair_type](config)


def list_hd_hair_types() -> List[str]:
    """List available HD hair types."""
    return list(HD_HAIR_TYPES.keys())

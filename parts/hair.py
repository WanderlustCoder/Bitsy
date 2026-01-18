"""
Hair - Hair styles and rendering.

Provides various hair styles for character customization.
"""

import math
from typing import Optional, List, Tuple
from dataclasses import dataclass

from .base import Part, PartConfig

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.canvas import Canvas
from core.color import Color


class Hair(Part):
    """Base class for hair parts."""

    def __init__(self, name: str, config: Optional[PartConfig] = None):
        super().__init__(name, config)
        self.has_bangs = True
        self.has_back = True

    def draw_back(self, canvas: Canvas, x: int, y: int,
                  width: int, height: int) -> None:
        """Draw back layer of hair (behind head)."""
        pass  # Subclasses override

    def draw_front(self, canvas: Canvas, x: int, y: int,
                   width: int, height: int) -> None:
        """Draw front layer of hair (bangs, in front of face)."""
        pass  # Subclasses override


class FluffyHair(Hair):
    """Fluffy, rounded hair style."""

    def __init__(self, config: Optional[PartConfig] = None):
        super().__init__("fluffy", config)

    def draw(self, canvas: Canvas, x: int, y: int,
             width: int, height: int) -> None:
        self.draw_back(canvas, x, y, width, height)
        self.draw_front(canvas, x, y, width, height)

    def draw_back(self, canvas: Canvas, x: int, y: int,
                  width: int, height: int) -> None:
        colors = self._get_colors(4)
        if not colors:
            return

        hw, hh = width // 2, height // 2

        # Main back volume - larger fluffy shape
        back_color = colors[2] if len(colors) > 2 else colors[-1]

        # Multiple overlapping circles for fluffy look
        canvas.fill_circle(x, y - hh//3, int(hw * 1.1), back_color)
        canvas.fill_circle(x - hw//2, y - hh//4, int(hw * 0.7), back_color)
        canvas.fill_circle(x + hw//2, y - hh//4, int(hw * 0.7), back_color)

        # Hair flowing down sides
        canvas.fill_ellipse(x - hw, y + hh//4, hw//2, hh//2, back_color)
        canvas.fill_ellipse(x + hw, y + hh//4, hw//2, hh//2, back_color)

    def draw_front(self, canvas: Canvas, x: int, y: int,
                   width: int, height: int) -> None:
        colors = self._get_colors(4)
        if not colors:
            return

        hw, hh = width // 2, height // 2

        # Bangs - fluffy tufts
        if self.has_bangs:
            front_color = colors[1] if len(colors) > 1 else colors[0]
            highlight = colors[0]

            # Central tuft
            canvas.fill_circle(x, y - hh//2, hw//2, front_color)

            # Side tufts
            canvas.fill_circle(x - hw//3, y - hh//3, hw//3, front_color)
            canvas.fill_circle(x + hw//3, y - hh//3, hw//3, front_color)

            # Highlight on top
            canvas.fill_circle(x - hw//4, y - hh//2 - 2, hw//4, highlight)


class SpikyHair(Hair):
    """Spiky, anime-style hair."""

    def __init__(self, config: Optional[PartConfig] = None):
        super().__init__("spiky", config)

    def draw(self, canvas: Canvas, x: int, y: int,
             width: int, height: int) -> None:
        self.draw_back(canvas, x, y, width, height)
        self.draw_front(canvas, x, y, width, height)

    def draw_back(self, canvas: Canvas, x: int, y: int,
                  width: int, height: int) -> None:
        colors = self._get_colors(3)
        if not colors:
            return

        hw, hh = width // 2, height // 2
        back_color = colors[2] if len(colors) > 2 else colors[-1]

        # Back spikes
        spike_count = 5
        for i in range(spike_count):
            angle = math.pi * (0.3 + 0.4 * i / (spike_count - 1))  # Spread across back
            spike_len = hh * (0.6 + self._random() * 0.4)
            sx = x + int(math.cos(angle) * hw * 0.3)
            sy = y - int(hh * 0.2)

            tip_x = sx - int(math.cos(angle - 0.3) * spike_len)
            tip_y = sy - int(math.sin(angle) * spike_len)

            points = [
                (sx - 4, sy),
                (tip_x, tip_y),
                (sx + 4, sy),
            ]
            canvas.fill_polygon(points, back_color)

    def draw_front(self, canvas: Canvas, x: int, y: int,
                   width: int, height: int) -> None:
        colors = self._get_colors(3)
        if not colors:
            return

        hw, hh = width // 2, height // 2
        front_color = colors[1] if len(colors) > 1 else colors[0]
        highlight = colors[0]

        # Front spikes (bangs)
        if self.has_bangs:
            spike_count = 3
            for i in range(spike_count):
                offset = (i - spike_count // 2) * (hw // 2)
                spike_len = hh * (0.4 + self._random() * 0.2)

                points = [
                    (x + offset - 3, y - hh//3),
                    (x + offset, y - hh//3 - int(spike_len)),
                    (x + offset + 3, y - hh//3),
                ]
                canvas.fill_polygon(points, front_color)

            # Highlight streak
            canvas.draw_line(x - 2, y - hh//2, x, y - hh//2 - 4, highlight)


class LongHair(Hair):
    """Long, flowing hair."""

    def __init__(self, config: Optional[PartConfig] = None):
        super().__init__("long", config)

    def draw(self, canvas: Canvas, x: int, y: int,
             width: int, height: int) -> None:
        self.draw_back(canvas, x, y, width, height)
        self.draw_front(canvas, x, y, width, height)

    def draw_back(self, canvas: Canvas, x: int, y: int,
                  width: int, height: int) -> None:
        colors = self._get_colors(4)
        if not colors:
            return

        hw, hh = width // 2, height // 2
        back_color = colors[2] if len(colors) > 2 else colors[-1]
        shadow = colors[3] if len(colors) > 3 else back_color

        # Long flowing back
        # Main mass
        canvas.fill_ellipse(x, y, int(hw * 1.2), hh, back_color)

        # Lower extension
        canvas.fill_ellipse(x, y + hh, int(hw * 0.9), int(hh * 0.7), back_color)

        # Side strands
        canvas.fill_ellipse(x - hw, y + hh//2, hw//3, int(hh * 0.8), shadow)
        canvas.fill_ellipse(x + hw, y + hh//2, hw//3, int(hh * 0.8), shadow)

    def draw_front(self, canvas: Canvas, x: int, y: int,
                   width: int, height: int) -> None:
        colors = self._get_colors(4)
        if not colors:
            return

        hw, hh = width // 2, height // 2
        front_color = colors[1] if len(colors) > 1 else colors[0]
        highlight = colors[0]

        if self.has_bangs:
            # Swept bangs
            canvas.fill_ellipse(x, y - hh//2, hw, hh//4, front_color)

            # Side-swept strands
            canvas.fill_ellipse(x - hw//2, y - hh//3, hw//3, hh//3, front_color)

            # Highlight
            canvas.fill_ellipse(x - hw//3, y - hh//2, hw//4, hh//8, highlight)


class ShortHair(Hair):
    """Short, cropped hair."""

    def __init__(self, config: Optional[PartConfig] = None):
        super().__init__("short", config)
        self.has_back = False

    def draw(self, canvas: Canvas, x: int, y: int,
             width: int, height: int) -> None:
        self.draw_front(canvas, x, y, width, height)

    def draw_front(self, canvas: Canvas, x: int, y: int,
                   width: int, height: int) -> None:
        colors = self._get_colors(3)
        if not colors:
            return

        hw, hh = width // 2, height // 2
        base_color = colors[1] if len(colors) > 1 else colors[0]
        highlight = colors[0]

        # Cap of short hair
        canvas.fill_ellipse(x, y - hh//3, hw, hh//2, base_color)

        # Slight texture with small variations
        for i in range(5):
            tx = x + self._random_int(-hw//2, hw//2)
            ty = y - hh//2 + self._random_int(-hh//4, hh//4)
            tr = self._random_int(2, 4)
            canvas.fill_circle(tx, ty, tr, base_color)

        # Highlight
        canvas.fill_ellipse(x - hw//4, y - hh//2, hw//3, hh//5, highlight)


class BaldHead(Hair):
    """No hair / bald."""

    def __init__(self, config: Optional[PartConfig] = None):
        super().__init__("bald", config)
        self.has_bangs = False
        self.has_back = False

    def draw(self, canvas: Canvas, x: int, y: int,
             width: int, height: int) -> None:
        # Nothing to draw for bald
        pass


class PonytailHair(Hair):
    """Hair with ponytail."""

    def __init__(self, config: Optional[PartConfig] = None):
        super().__init__("ponytail", config)

    def draw(self, canvas: Canvas, x: int, y: int,
             width: int, height: int) -> None:
        self.draw_back(canvas, x, y, width, height)
        self.draw_front(canvas, x, y, width, height)

    def draw_back(self, canvas: Canvas, x: int, y: int,
                  width: int, height: int) -> None:
        colors = self._get_colors(4)
        if not colors:
            return

        hw, hh = width // 2, height // 2
        back_color = colors[2] if len(colors) > 2 else colors[-1]

        # Hair tie area
        canvas.fill_circle(x, y - hh//4, hw//2, back_color)

        # Ponytail flowing down
        ponytail_len = int(hh * 1.5)
        canvas.fill_ellipse(x, y + ponytail_len//2, hw//3, ponytail_len//2, back_color)

        # Tie
        tie_color = colors[3] if len(colors) > 3 else (200, 100, 100, 255)
        canvas.fill_rect(x - 3, y - hh//4 - 2, 6, 4, tie_color)

    def draw_front(self, canvas: Canvas, x: int, y: int,
                   width: int, height: int) -> None:
        colors = self._get_colors(4)
        if not colors:
            return

        hw, hh = width // 2, height // 2
        front_color = colors[1] if len(colors) > 1 else colors[0]
        highlight = colors[0]

        if self.has_bangs:
            # Front hair cap
            canvas.fill_ellipse(x, y - hh//2, int(hw * 0.9), hh//3, front_color)

            # Side strands
            canvas.fill_ellipse(x - hw, y - hh//4, hw//4, hh//3, front_color)
            canvas.fill_ellipse(x + hw, y - hh//4, hw//4, hh//3, front_color)

            # Highlight
            canvas.fill_circle(x - hw//3, y - hh//2, hw//4, highlight)


class TwinTailsHair(Hair):
    """Twin tails / pigtails style."""

    def __init__(self, config: Optional[PartConfig] = None):
        super().__init__("twintails", config)

    def draw(self, canvas: Canvas, x: int, y: int,
             width: int, height: int) -> None:
        self.draw_back(canvas, x, y, width, height)
        self.draw_front(canvas, x, y, width, height)

    def draw_back(self, canvas: Canvas, x: int, y: int,
                  width: int, height: int) -> None:
        colors = self._get_colors(4)
        if not colors:
            return

        hw, hh = width // 2, height // 2
        back_color = colors[2] if len(colors) > 2 else colors[-1]

        # Two tails on sides
        tail_len = int(hh * 1.2)

        # Left tail
        canvas.fill_ellipse(x - hw, y + tail_len//3, hw//3, tail_len//2, back_color)

        # Right tail
        canvas.fill_ellipse(x + hw, y + tail_len//3, hw//3, tail_len//2, back_color)

        # Hair ties
        tie_color = colors[3] if len(colors) > 3 else (255, 100, 150, 255)
        canvas.fill_circle(x - hw, y - hh//4, 3, tie_color)
        canvas.fill_circle(x + hw, y - hh//4, 3, tie_color)

    def draw_front(self, canvas: Canvas, x: int, y: int,
                   width: int, height: int) -> None:
        colors = self._get_colors(4)
        if not colors:
            return

        hw, hh = width // 2, height // 2
        front_color = colors[1] if len(colors) > 1 else colors[0]
        highlight = colors[0]

        if self.has_bangs:
            # Front cap
            canvas.fill_ellipse(x, y - hh//2, hw, hh//3, front_color)

            # Highlight
            canvas.fill_ellipse(x, y - hh//2 - 2, hw//2, hh//6, highlight)


# =============================================================================
# Hair Factory
# =============================================================================

HAIR_TYPES = {
    'fluffy': FluffyHair,
    'spiky': SpikyHair,
    'long': LongHair,
    'short': ShortHair,
    'bald': BaldHead,
    'ponytail': PonytailHair,
    'twintails': TwinTailsHair,
}

# Import HD hair types and merge into registry
try:
    from .hair_hd import HD_HAIR_TYPES
    HAIR_TYPES.update(HD_HAIR_TYPES)
except ImportError:
    pass  # HD hair module not available


def create_hair(hair_type: str, config: Optional[PartConfig] = None) -> Hair:
    """Create a hair part by type name.

    Args:
        hair_type: Hair style name ('fluffy', 'spiky', 'long', 'short', 'bald', 'ponytail', 'twintails')
        config: Part configuration

    Returns:
        Hair instance
    """
    if hair_type not in HAIR_TYPES:
        available = ', '.join(HAIR_TYPES.keys())
        raise ValueError(f"Unknown hair type '{hair_type}'. Available: {available}")

    return HAIR_TYPES[hair_type](config)


def list_hair_types() -> List[str]:
    """Get list of available hair types."""
    return list(HAIR_TYPES.keys())

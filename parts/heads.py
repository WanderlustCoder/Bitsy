"""
Heads - Head shapes and face feature placement.

Provides various head shapes for different character styles.
"""

import math
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass

from .base import Part, PartConfig

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.canvas import Canvas
from core.color import Color


@dataclass
class FaceLayout:
    """Defines where facial features should be placed."""

    # Eye positions (relative to center, as fraction of width/height)
    eye_left_x: float = -0.2
    eye_right_x: float = 0.2
    eye_y: float = -0.1

    # Eye size (as fraction of head width)
    eye_width: float = 0.15
    eye_height: float = 0.12

    # Mouth position
    mouth_x: float = 0.0
    mouth_y: float = 0.25
    mouth_width: float = 0.15

    # Nose position
    nose_x: float = 0.0
    nose_y: float = 0.1

    # Cheek/blush positions
    blush_left_x: float = -0.25
    blush_right_x: float = 0.25
    blush_y: float = 0.15


class Head(Part):
    """Base class for head parts."""

    def __init__(self, name: str, config: Optional[PartConfig] = None):
        super().__init__(name, config)
        self.face_layout = FaceLayout()

    def get_face_layout(self, x: int, y: int, width: int, height: int) -> Dict[str, Tuple[int, int]]:
        """Get absolute positions for facial features.

        Args:
            x, y: Center position
            width, height: Head size

        Returns:
            Dictionary with feature names and (x, y) positions
        """
        fl = self.face_layout
        hw, hh = width // 2, height // 2

        return {
            'eye_left': (int(x + fl.eye_left_x * width), int(y + fl.eye_y * height)),
            'eye_right': (int(x + fl.eye_right_x * width), int(y + fl.eye_y * height)),
            'mouth': (int(x + fl.mouth_x * width), int(y + fl.mouth_y * height)),
            'nose': (int(x + fl.nose_x * width), int(y + fl.nose_y * height)),
            'blush_left': (int(x + fl.blush_left_x * width), int(y + fl.blush_y * height)),
            'blush_right': (int(x + fl.blush_right_x * width), int(y + fl.blush_y * height)),
        }

    def get_eye_size(self, width: int, height: int) -> Tuple[int, int]:
        """Get eye dimensions."""
        return (
            int(width * self.face_layout.eye_width),
            int(height * self.face_layout.eye_height)
        )


class RoundHead(Head):
    """Simple round/circular head shape."""

    def __init__(self, config: Optional[PartConfig] = None):
        super().__init__("round", config)

    def draw(self, canvas: Canvas, x: int, y: int,
             width: int, height: int) -> None:
        colors = self._get_colors(3)
        r = min(width, height) // 2
        self._draw_shaded_circle(canvas, x, y, r, colors)


class OvalHead(Head):
    """Oval/egg-shaped head (taller than wide)."""

    def __init__(self, config: Optional[PartConfig] = None):
        super().__init__("oval", config)

    def draw(self, canvas: Canvas, x: int, y: int,
             width: int, height: int) -> None:
        colors = self._get_colors(3)
        rx = width // 2
        ry = height // 2
        self._draw_shaded_ellipse(canvas, x, y, rx, ry, colors)


class SquareHead(Head):
    """Square/blocky head shape with rounded corners."""

    def __init__(self, config: Optional[PartConfig] = None):
        super().__init__("square", config)

    def draw(self, canvas: Canvas, x: int, y: int,
             width: int, height: int) -> None:
        colors = self._get_colors(3)
        style = self._get_style()

        hw, hh = width // 2, height // 2
        left = x - hw
        top = y - hh

        # Draw rounded rectangle
        corner_r = min(width, height) // 6

        if len(colors) >= 1:
            # Main fill
            canvas.fill_rect(left + corner_r, top, width - 2*corner_r, height, colors[1] if len(colors) > 1 else colors[0])
            canvas.fill_rect(left, top + corner_r, width, height - 2*corner_r, colors[1] if len(colors) > 1 else colors[0])

            # Corners
            canvas.fill_circle(left + corner_r, top + corner_r, corner_r, colors[1] if len(colors) > 1 else colors[0])
            canvas.fill_circle(left + width - corner_r - 1, top + corner_r, corner_r, colors[1] if len(colors) > 1 else colors[0])
            canvas.fill_circle(left + corner_r, top + height - corner_r - 1, corner_r, colors[1] if len(colors) > 1 else colors[0])
            canvas.fill_circle(left + width - corner_r - 1, top + height - corner_r - 1, corner_r, colors[1] if len(colors) > 1 else colors[0])

        # Add highlight
        if len(colors) >= 1 and self.config.shading:
            canvas.fill_ellipse(x - hw//3, y - hh//3, hw//2, hh//3, colors[0])

        # Outline
        if self.config.outline and style.outline.enabled:
            outline_color = self._get_outline_color()
            # Draw outline around rounded rect
            for px in range(left + corner_r, left + width - corner_r):
                canvas.set_pixel(px, top, outline_color)
                canvas.set_pixel(px, top + height - 1, outline_color)
            for py in range(top + corner_r, top + height - corner_r):
                canvas.set_pixel(left, py, outline_color)
                canvas.set_pixel(left + width - 1, py, outline_color)


class ChibiHead(Head):
    """Chibi-style head - extra round with large eye area."""

    def __init__(self, config: Optional[PartConfig] = None):
        super().__init__("chibi", config)
        # Adjust face layout for chibi proportions
        self.face_layout = FaceLayout(
            eye_left_x=-0.22,
            eye_right_x=0.22,
            eye_y=-0.05,
            eye_width=0.2,
            eye_height=0.18,
            mouth_y=0.35,
            mouth_width=0.1,
        )

    def draw(self, canvas: Canvas, x: int, y: int,
             width: int, height: int) -> None:
        colors = self._get_colors(3)
        style = self._get_style()

        # Slightly wider than tall for cute look
        rx = int(width * 0.52)
        ry = int(height * 0.48)

        self._draw_shaded_ellipse(canvas, x, y, rx, ry, colors)

        # Add subtle cheek puff
        if self.config.shading and len(colors) >= 2:
            cheek_y = y + int(height * 0.15)
            cheek_r = int(width * 0.12)
            # Slightly lighter cheek area
            canvas.fill_circle(x - int(width * 0.25), cheek_y, cheek_r, colors[0])
            canvas.fill_circle(x + int(width * 0.25), cheek_y, cheek_r, colors[0])


class TriangleHead(Head):
    """Triangle/pointed chin head shape."""

    def __init__(self, config: Optional[PartConfig] = None):
        super().__init__("triangle", config)

    def draw(self, canvas: Canvas, x: int, y: int,
             width: int, height: int) -> None:
        colors = self._get_colors(3)
        style = self._get_style()

        hw, hh = width // 2, height // 2

        # Triangle points
        points = [
            (x - hw, y - hh//2),      # Top left
            (x + hw, y - hh//2),      # Top right
            (x, y + hh),              # Bottom center (chin)
        ]

        # Draw filled triangle with base color
        if colors:
            canvas.fill_polygon(points, colors[1] if len(colors) > 1 else colors[0])

        # Add curved top
        canvas.fill_ellipse(x, y - hh//2, hw, hh//3, colors[1] if len(colors) > 1 else colors[0])

        # Highlight
        if len(colors) >= 1 and self.config.shading:
            canvas.fill_ellipse(x, y - hh//3, hw//2, hh//4, colors[0])

        # Outline
        if self.config.outline and style.outline.enabled:
            outline_color = self._get_outline_color()
            for i in range(len(points)):
                p1 = points[i]
                p2 = points[(i + 1) % len(points)]
                canvas.draw_line(int(p1[0]), int(p1[1]), int(p2[0]), int(p2[1]), outline_color)


class HeartHead(Head):
    """Heart-shaped face (wide at eyes, pointed chin)."""

    def __init__(self, config: Optional[PartConfig] = None):
        super().__init__("heart", config)
        self.face_layout = FaceLayout(
            eye_left_x=-0.25,
            eye_right_x=0.25,
            eye_y=-0.15,
            mouth_y=0.4,
        )

    def draw(self, canvas: Canvas, x: int, y: int,
             width: int, height: int) -> None:
        colors = self._get_colors(3)
        style = self._get_style()

        hw, hh = width // 2, height // 2

        # Two circles at top
        circle_r = int(width * 0.32)
        left_cx = x - int(width * 0.2)
        right_cx = x + int(width * 0.2)
        circle_y = y - int(height * 0.15)

        base_color = colors[1] if len(colors) > 1 else colors[0]

        canvas.fill_circle(left_cx, circle_y, circle_r, base_color)
        canvas.fill_circle(right_cx, circle_y, circle_r, base_color)

        # Triangle for chin
        chin_points = [
            (x - int(width * 0.45), circle_y),
            (x + int(width * 0.45), circle_y),
            (x, y + hh),
        ]
        canvas.fill_polygon(chin_points, base_color)

        # Highlight
        if len(colors) >= 1 and self.config.shading:
            canvas.fill_circle(left_cx + 2, circle_y - 2, circle_r//2, colors[0])
            canvas.fill_circle(right_cx + 2, circle_y - 2, circle_r//2, colors[0])


# =============================================================================
# Head Factory
# =============================================================================

HEAD_TYPES = {
    'round': RoundHead,
    'oval': OvalHead,
    'square': SquareHead,
    'chibi': ChibiHead,
    'triangle': TriangleHead,
    'heart': HeartHead,
}


def create_head(head_type: str, config: Optional[PartConfig] = None) -> Head:
    """Create a head part by type name.

    Args:
        head_type: Head shape name ('round', 'oval', 'square', 'chibi', 'triangle', 'heart')
        config: Part configuration

    Returns:
        Head instance
    """
    if head_type not in HEAD_TYPES:
        available = ', '.join(HEAD_TYPES.keys())
        raise ValueError(f"Unknown head type '{head_type}'. Available: {available}")

    return HEAD_TYPES[head_type](config)


def list_head_types() -> List[str]:
    """Get list of available head types."""
    return list(HEAD_TYPES.keys())

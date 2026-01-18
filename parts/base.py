"""
Base - Base class for character parts.

Provides common functionality for all body part types.
"""

import math
import random
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass, field

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.canvas import Canvas
from core.color import Color, darken, lighten, shift_hue
from core.style import Style
from core.palette import Palette


@dataclass
class PartConfig:
    """Configuration for rendering a body part."""

    # Base colors
    base_color: Color = (200, 180, 160, 255)
    palette: Optional[Palette] = None

    # Rendering options
    style: Optional[Style] = None
    outline: bool = True
    shading: bool = True

    # Transform
    flip_x: bool = False
    scale: float = 1.0
    rotation: float = 0.0  # Radians

    # Random seed for procedural details
    seed: Optional[int] = None


class Part:
    """Base class for drawable body parts."""

    def __init__(self, name: str, config: Optional[PartConfig] = None):
        self.name = name
        self.config = config or PartConfig()
        self._rng = random.Random(self.config.seed)

    def draw(self, canvas: Canvas, x: int, y: int,
             width: int, height: int) -> None:
        """Draw the part onto a canvas.

        Args:
            canvas: Target canvas
            x, y: Center position
            width, height: Bounding size
        """
        raise NotImplementedError("Subclasses must implement draw()")

    def get_bounds(self, x: int, y: int, width: int, height: int) -> Tuple[int, int, int, int]:
        """Get bounding box after applying transforms.

        Returns:
            (min_x, min_y, max_x, max_y)
        """
        half_w = width // 2
        half_h = height // 2
        return (x - half_w, y - half_h, x + half_w, y + half_h)

    def _get_style(self) -> Style:
        """Get effective style (from config or default)."""
        return self.config.style or Style()

    def _get_colors(self, num_levels: int = 3) -> List[Color]:
        """Get shading colors based on style.

        Args:
            num_levels: Number of shading levels

        Returns:
            List of colors from highlight to shadow
        """
        style = self._get_style()
        if self.config.palette:
            # Use palette colors directly
            return list(self.config.palette.colors[:num_levels])
        else:
            # Generate from base color
            return style.get_shading_colors(self.config.base_color, num_levels)

    def _get_outline_color(self) -> Color:
        """Get outline color based on style."""
        style = self._get_style()
        return style.get_outline_color(self.config.base_color)

    def _random(self) -> float:
        """Get next random value 0-1."""
        return self._rng.random()

    def _random_int(self, a: int, b: int) -> int:
        """Get random integer in range [a, b]."""
        return self._rng.randint(a, b)

    def _draw_shaded_circle(self, canvas: Canvas, cx: int, cy: int, r: int,
                            colors: List[Color], light_dir: Tuple[float, float] = (1, -1)) -> None:
        """Draw a circle with cel shading.

        Args:
            canvas: Target canvas
            cx, cy: Center position
            r: Radius
            colors: Shading colors (highlight to shadow)
            light_dir: Light direction vector
        """
        if not colors:
            return

        style = self._get_style()

        # Normalize light direction
        lx, ly = light_dir
        ll = math.sqrt(lx*lx + ly*ly)
        if ll > 0:
            lx, ly = lx/ll, ly/ll

        # Draw from back (shadow) to front (highlight)
        num_levels = len(colors)
        for i, color in enumerate(reversed(colors)):
            level = num_levels - 1 - i
            # Each level is offset toward light and smaller
            offset = int(level * r * 0.15)
            level_r = r - int(level * r * 0.2)

            if level_r > 0:
                canvas.fill_circle(
                    int(cx + lx * offset),
                    int(cy + ly * offset),
                    level_r,
                    color
                )

        # Outline
        if self.config.outline and style.outline.enabled:
            outline_color = self._get_outline_color()
            canvas.draw_circle(cx, cy, r, outline_color)

    def _draw_shaded_ellipse(self, canvas: Canvas, cx: int, cy: int,
                             rx: int, ry: int, colors: List[Color],
                             light_dir: Tuple[float, float] = (1, -1)) -> None:
        """Draw an ellipse with cel shading."""
        if not colors:
            return

        style = self._get_style()

        lx, ly = light_dir
        ll = math.sqrt(lx*lx + ly*ly)
        if ll > 0:
            lx, ly = lx/ll, ly/ll

        num_levels = len(colors)
        for i, color in enumerate(reversed(colors)):
            level = num_levels - 1 - i
            offset = int(level * max(rx, ry) * 0.12)
            level_rx = rx - int(level * rx * 0.15)
            level_ry = ry - int(level * ry * 0.15)

            if level_rx > 0 and level_ry > 0:
                canvas.fill_ellipse(
                    int(cx + lx * offset),
                    int(cy + ly * offset),
                    level_rx, level_ry,
                    color
                )

        # Outline - draw ellipse outline manually
        if self.config.outline and style.outline.enabled:
            outline_color = self._get_outline_color()
            # Simple outline by drawing at edge
            for angle in range(0, 360, 5):
                rad = math.radians(angle)
                ox = int(cx + rx * math.cos(rad))
                oy = int(cy + ry * math.sin(rad))
                canvas.set_pixel(ox, oy, outline_color)

    def _draw_shaded_rect(self, canvas: Canvas, x: int, y: int,
                          w: int, h: int, colors: List[Color]) -> None:
        """Draw a rectangle with cel shading."""
        if not colors:
            return

        style = self._get_style()

        if style.shading.mode == 'flat' or len(colors) == 1:
            canvas.fill_rect(x, y, w, h, colors[len(colors)//2])
        else:
            # Horizontal bands
            band_h = max(1, h // len(colors))
            for i, color in enumerate(colors):
                by = y + i * band_h
                bh = band_h if i < len(colors) - 1 else (h - i * band_h)
                canvas.fill_rect(x, by, w, bh, color)

        if self.config.outline and style.outline.enabled:
            outline_color = self._get_outline_color()
            canvas.draw_rect(x, y, w, h, outline_color)


def create_part(part_type: str, name: str, config: Optional[PartConfig] = None) -> Part:
    """Factory function to create parts by type.

    This will be extended as more part types are added.
    """
    # Import here to avoid circular imports
    from . import heads, bodies, hair, eyes

    if part_type == 'head':
        return heads.create_head(name, config)
    elif part_type == 'body':
        return bodies.create_body(name, config)
    elif part_type == 'hair':
        return hair.create_hair(name, config)
    elif part_type == 'eyes':
        return eyes.create_eyes(name, config)
    else:
        raise ValueError(f"Unknown part type: {part_type}")

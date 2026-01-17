"""
HD Canvas - High-quality canvas wrapper with anti-aliasing and style support.

Provides a canvas interface that automatically uses HD rendering features
based on the configured style. This allows generators to use the same
drawing API while getting quality upgrades transparently.

Usage:
    from core.hd_canvas import HDCanvas
    from core.style import Style

    canvas = HDCanvas(64, 64, style=Style.professional_hd())
    canvas.fill_circle(32, 32, 20, color)  # Uses AA if style.anti_alias
    result = canvas.finalize()  # Applies selout if enabled
"""

from typing import Optional, Tuple, List
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.canvas import Canvas
from core.style import Style
from core.color import Color


class HDCanvas:
    """Canvas wrapper that applies HD quality features based on style.

    Wraps a standard Canvas and intercepts drawing calls to use
    anti-aliased versions when the style has anti_alias enabled.
    Call finalize() to apply selout and get the final canvas.
    """

    def __init__(self, width: int, height: int,
                 background: Optional[Color] = None,
                 style: Optional[Style] = None):
        """Initialize HD canvas.

        Args:
            width, height: Canvas dimensions
            background: Optional background color
            style: Style controlling quality features (default: professional_hd)
        """
        # Use transparent if no background specified
        bg = background if background is not None else (0, 0, 0, 0)
        self.canvas = Canvas(width, height, bg)
        self.style = style or Style.professional_hd()
        self._use_aa = self.style.anti_alias
        self._use_selout = self.style.outline.selout_enabled

    @property
    def width(self) -> int:
        return self.canvas.width

    @property
    def height(self) -> int:
        return self.canvas.height

    @property
    def pixels(self):
        return self.canvas.pixels

    # =========================================================================
    # Pixel Operations (pass-through)
    # =========================================================================

    def get_pixel(self, x: int, y: int) -> Optional[Color]:
        return self.canvas.get_pixel(x, y)

    def set_pixel(self, x: int, y: int, color: Color) -> None:
        self.canvas.set_pixel(x, y, color)

    def set_pixel_solid(self, x: int, y: int, color: Color) -> None:
        self.canvas.set_pixel_solid(x, y, color)

    # =========================================================================
    # Rectangle Operations (pass-through - no AA needed for rects)
    # =========================================================================

    def fill_rect(self, x: int, y: int, w: int, h: int, color: Color) -> None:
        self.canvas.fill_rect(x, y, w, h, color)

    def draw_rect(self, x: int, y: int, w: int, h: int, color: Color) -> None:
        self.canvas.draw_rect(x, y, w, h, color)

    # =========================================================================
    # Circle Operations (AA-aware)
    # =========================================================================

    def fill_circle(self, cx: int, cy: int, r: int, color: Color) -> None:
        """Fill circle, using AA if enabled."""
        if self._use_aa and hasattr(self.canvas, 'fill_circle_aa'):
            self.canvas.fill_circle_aa(cx, cy, r, color)
        else:
            self.canvas.fill_circle(cx, cy, r, color)

    def draw_circle(self, cx: int, cy: int, r: int, color: Color) -> None:
        """Draw circle outline, using AA if enabled."""
        if self._use_aa and hasattr(self.canvas, 'draw_circle_aa'):
            self.canvas.draw_circle_aa(cx, cy, r, color)
        else:
            self.canvas.draw_circle(cx, cy, r, color)

    # =========================================================================
    # Ellipse Operations (AA-aware)
    # =========================================================================

    def fill_ellipse(self, cx: int, cy: int, rx: int, ry: int, color: Color) -> None:
        """Fill ellipse, using AA if enabled."""
        if self._use_aa and hasattr(self.canvas, 'fill_ellipse_aa'):
            self.canvas.fill_ellipse_aa(cx, cy, rx, ry, color)
        else:
            self.canvas.fill_ellipse(cx, cy, rx, ry, color)

    def draw_ellipse(self, cx: int, cy: int, rx: int, ry: int, color: Color) -> None:
        """Draw ellipse outline."""
        # No AA version for draw_ellipse, use regular
        if hasattr(self.canvas, 'draw_ellipse'):
            self.canvas.draw_ellipse(cx, cy, rx, ry, color)
        else:
            # Fallback: draw using circle approximation
            self.canvas.fill_ellipse(cx, cy, rx, ry, color)

    # =========================================================================
    # Line Operations (AA-aware)
    # =========================================================================

    def draw_line(self, x1: int, y1: int, x2: int, y2: int,
                  color: Color, thickness: int = 1) -> None:
        """Draw line, using AA if enabled."""
        if self._use_aa and thickness == 1 and hasattr(self.canvas, 'draw_line_aa'):
            self.canvas.draw_line_aa(x1, y1, x2, y2, color)
        else:
            self.canvas.draw_line(x1, y1, x2, y2, color, thickness)

    # =========================================================================
    # Polygon Operations (pass-through)
    # =========================================================================

    def fill_polygon(self, points: List[Tuple[int, int]], color: Color) -> None:
        self.canvas.fill_polygon(points, color)

    def draw_polygon(self, points: List[Tuple[int, int]], color: Color) -> None:
        if hasattr(self.canvas, 'draw_polygon'):
            self.canvas.draw_polygon(points, color)
        else:
            # Fallback: draw lines between points
            for i in range(len(points)):
                p1 = points[i]
                p2 = points[(i + 1) % len(points)]
                self.draw_line(p1[0], p1[1], p2[0], p2[1], color)

    # =========================================================================
    # Gradient Operations (pass-through)
    # =========================================================================

    def gradient_vertical(self, x: int, y: int, w: int, h: int,
                          color1: Color, color2: Color) -> None:
        self.canvas.gradient_vertical(x, y, w, h, color1, color2)

    def gradient_horizontal(self, x: int, y: int, w: int, h: int,
                            color1: Color, color2: Color) -> None:
        if hasattr(self.canvas, 'gradient_horizontal'):
            self.canvas.gradient_horizontal(x, y, w, h, color1, color2)
        else:
            self.canvas.gradient_vertical(x, y, w, h, color1, color2)

    def gradient_radial(self, cx: int, cy: int, r: int,
                        color1: Color, color2: Color) -> None:
        self.canvas.gradient_radial(cx, cy, r, color1, color2)

    # =========================================================================
    # Blit Operations (pass-through)
    # =========================================================================

    def blit(self, other: 'Canvas', x: int, y: int) -> None:
        # Handle both Canvas and HDCanvas
        if isinstance(other, HDCanvas):
            self.canvas.blit(other.canvas, x, y)
        else:
            self.canvas.blit(other, x, y)

    def clear(self, color: Optional[Color] = None) -> None:
        self.canvas.clear(color)

    # =========================================================================
    # Style-Aware Shading
    # =========================================================================

    def get_shading_colors(self, base_color: Color,
                           num_levels: Optional[int] = None) -> List[Color]:
        """Get shading colors using the style's shading configuration."""
        return self.style.get_shading_colors(base_color, num_levels)

    def get_outline_color(self, fill_color: Color,
                          neighbor_color: Optional[Color] = None) -> Color:
        """Get outline color using style's outline configuration."""
        return self.style.get_outline_color(fill_color, neighbor_color)

    # =========================================================================
    # Finalization (applies selout)
    # =========================================================================

    def finalize(self) -> Canvas:
        """Finalize the canvas, applying selout if enabled.

        Returns:
            Final Canvas with all post-processing applied
        """
        if self._use_selout:
            from quality.selout import apply_selout
            return apply_selout(
                self.canvas,
                darken_factor=self.style.outline.selout_darken,
                saturation_factor=self.style.outline.selout_saturation
            )
        return self.canvas.copy()

    def to_canvas(self) -> Canvas:
        """Get the underlying canvas without post-processing."""
        return self.canvas

    # =========================================================================
    # Output Operations
    # =========================================================================

    def save(self, path: str) -> None:
        """Save finalized canvas to file."""
        final = self.finalize()
        final.save(path)

    def to_bytes(self) -> bytes:
        """Get finalized canvas as PNG bytes."""
        final = self.finalize()
        return final.to_bytes()

    def copy(self) -> 'HDCanvas':
        """Create a copy of this HD canvas."""
        new_canvas = HDCanvas(self.width, self.height, style=self.style)
        new_canvas.canvas = self.canvas.copy()
        return new_canvas

    # =========================================================================
    # Canvas Method Forwarding
    # =========================================================================

    def scale(self, factor: int) -> Canvas:
        """Scale the finalized canvas."""
        return self.finalize().scale(factor)

    def flip_horizontal(self) -> Canvas:
        return self.canvas.flip_horizontal()

    def flip_vertical(self) -> Canvas:
        return self.canvas.flip_vertical()


def create_hd_canvas(width: int, height: int,
                     background: Optional[Color] = None,
                     hd_enabled: bool = True) -> 'HDCanvas':
    """Create an HD canvas with appropriate style.

    Args:
        width, height: Canvas dimensions
        background: Optional background color
        hd_enabled: If True, use professional_hd style; else use basic style

    Returns:
        HDCanvas configured appropriately
    """
    if hd_enabled:
        style = Style.professional_hd()
    else:
        style = Style()  # Default style without HD features

    return HDCanvas(width, height, background, style)

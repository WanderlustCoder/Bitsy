"""
Professional Hair System - Strand-based hair rendering for maximum quality.

Provides professional-quality hair with:
- Individual strand rendering using bezier curves
- Strand groups with natural flow and spread
- Tapered strand thickness (thicker at root, thinner at tip)
- Multi-layer highlights with artistic control
- Gradient shading within hair mass

Optimized for 64x64+ sprites where strand detail is visible.
"""

import math
import random
from typing import Optional, List, Tuple
from dataclasses import dataclass, field

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.canvas import Canvas
from core.color import Color, lighten, darken, shift_hue, adjust_saturation

from .base import Part, PartConfig
from .hair import Hair


@dataclass
class StrandGroup:
    """Defines a group of hair strands with shared properties.

    Strands in a group flow in similar directions with slight variations.
    """
    # Base bezier curve control points (relative to draw position)
    # Will be scaled to actual hair size
    base_curve: List[Tuple[float, float]]  # 3-4 control points

    # Number of strands in this group
    strand_count: int = 8

    # How much strands spread from the base curve (0-1)
    spread: float = 0.3

    # Thickness range (start, end) for tapered strands
    thickness_start: float = 2.0
    thickness_end: float = 0.5

    # Color offset from base (for variation within group)
    color_offset: int = 0  # Index into palette


@dataclass
class HairHighlight:
    """Defines a highlight zone within the hair.

    Position is relative (0-1) within the hair bounds.
    """
    position: Tuple[float, float]  # Relative position (0-1, 0-1)
    size: float = 0.2  # Relative size
    intensity: float = 0.5  # How much to lighten (0-1)
    hue_shift: float = 5.0  # Degrees of hue shift (warm)


@dataclass
class ProHairConfig(PartConfig):
    """Extended configuration for professional hair."""
    strand_density: int = 10  # Base strands per group
    highlight_positions: List[Tuple[float, float]] = None
    flow_angle: float = -15  # Overall hair flow direction (degrees)
    rim_light: bool = True
    rim_intensity: float = 0.3
    detail_level: str = 'high'  # 'medium', 'high', 'ultra'


class ProfessionalHair(Hair):
    """Base class for professional strand-based hair rendering.

    Uses bezier curves to render individual hair strands with:
    - Natural flow and direction
    - Tapered thickness
    - Color variation
    - Layered highlights
    """

    def __init__(self, name: str, config: Optional[ProHairConfig] = None):
        super().__init__(name, config)
        self.config: ProHairConfig = config or ProHairConfig()
        self.strand_groups: List[StrandGroup] = []
        self.highlights: List[HairHighlight] = []
        self._rng = random.Random(self.config.seed if hasattr(self.config, 'seed') else 42)

    def _get_strand_colors(self, base_color: Color) -> Tuple[Color, Color, Color]:
        """Get shadow, base, and highlight colors for strands."""
        shadow = darken(base_color, 0.25)
        shadow = shift_hue(shadow, -10)  # Cool shadow

        highlight = lighten(base_color, 0.2)
        highlight = shift_hue(highlight, 8)  # Warm highlight

        return (shadow, base_color, highlight)

    def _draw_strand(self, canvas: Canvas, points: List[Tuple[float, float]],
                     color: Color, thickness_start: float = 2.0,
                     thickness_end: float = 0.5) -> None:
        """Draw a single tapered hair strand."""
        if hasattr(canvas, 'draw_bezier_tapered'):
            canvas.draw_bezier_tapered(points, color,
                                       start_thickness=thickness_start,
                                       end_thickness=thickness_end)
        elif hasattr(canvas, 'draw_bezier_aa'):
            canvas.draw_bezier_aa(points, color)
        else:
            canvas.draw_bezier(points, color, thickness=1)

    def _draw_strand_group(self, canvas: Canvas, group: StrandGroup,
                           x: int, y: int, scale_x: float, scale_y: float,
                           base_color: Color) -> None:
        """Draw all strands in a group with variations."""
        shadow_color, mid_color, highlight_color = self._get_strand_colors(base_color)

        for i in range(group.strand_count):
            # Add random variation to the curve
            variation = (i / group.strand_count - 0.5) * 2 * group.spread

            # Perturb control points
            points = []
            for j, (bx, by) in enumerate(group.base_curve):
                # More variation at the end of the strand
                var_factor = j / (len(group.base_curve) - 1) if len(group.base_curve) > 1 else 0
                noise_x = self._rng.uniform(-1, 1) * group.spread * scale_x * var_factor * 0.5
                noise_y = self._rng.uniform(-1, 1) * group.spread * scale_y * var_factor * 0.3

                px = x + (bx + variation * 0.3) * scale_x + noise_x
                py = y + by * scale_y + noise_y
                points.append((px, py))

            # Determine strand color based on position
            t = i / max(group.strand_count - 1, 1)

            # Draw shadow strand (offset)
            shadow_points = [(p[0] + 1, p[1] + 1) for p in points]
            self._draw_strand(canvas, shadow_points, shadow_color,
                            group.thickness_start * 0.8, group.thickness_end * 0.8)

            # Draw main strand
            self._draw_strand(canvas, points, mid_color,
                            group.thickness_start, group.thickness_end)

            # Draw highlight on some strands
            if i % 3 == 0:
                highlight_points = [(p[0] - 0.5, p[1] - 0.5) for p in points]
                self._draw_strand(canvas, highlight_points, highlight_color,
                                group.thickness_start * 0.5, group.thickness_end * 0.3)

    def _draw_highlight_zone(self, canvas: Canvas, highlight: HairHighlight,
                             x: int, y: int, width: int, height: int,
                             base_color: Color) -> None:
        """Draw a highlight zone (ellipse with gradient)."""
        hx = int(x + (highlight.position[0] - 0.5) * width)
        hy = int(y + (highlight.position[1] - 0.5) * height)
        hr = int(highlight.size * min(width, height) / 2)

        highlight_color = lighten(base_color, highlight.intensity)
        highlight_color = shift_hue(highlight_color, highlight.hue_shift)

        # Use radial gradient if available
        if hasattr(canvas, 'fill_ellipse_radial_gradient'):
            # Outer color is semi-transparent
            outer = (highlight_color[0], highlight_color[1], highlight_color[2], 80)
            inner = (highlight_color[0], highlight_color[1], highlight_color[2], 180)
            canvas.fill_ellipse_radial_gradient(hx, hy, hr, int(hr * 0.8), inner, outer)
        else:
            # Fallback to regular ellipse
            canvas.fill_ellipse(hx, hy, hr, int(hr * 0.8), highlight_color)


class ProfessionalBunHair(ProfessionalHair):
    """Professional bun hairstyle with strand-based rendering.

    Features:
    - 8+ strand groups for detailed hair mass
    - Circular bun with wrap-around flow
    - Flowing side strands
    - Multi-layer bangs
    - Natural highlights following hair shape
    """

    def __init__(self, config: Optional[ProHairConfig] = None):
        super().__init__("bun_pro", config)
        self._setup_strand_groups()
        self._setup_highlights()

    def _setup_strand_groups(self) -> None:
        """Define strand groups for bun hairstyle."""
        # Back hair strands (flowing down behind head)
        self.back_strands = [
            # Left back flow
            StrandGroup(
                base_curve=[(-0.4, -0.2), (-0.5, 0.2), (-0.45, 0.5)],
                strand_count=6, spread=0.15, thickness_start=2.0, thickness_end=0.5
            ),
            # Center back flow
            StrandGroup(
                base_curve=[(0.0, -0.1), (0.0, 0.2), (0.0, 0.4)],
                strand_count=8, spread=0.2, thickness_start=2.0, thickness_end=0.5
            ),
            # Right back flow
            StrandGroup(
                base_curve=[(0.4, -0.2), (0.5, 0.2), (0.45, 0.5)],
                strand_count=6, spread=0.15, thickness_start=2.0, thickness_end=0.5
            ),
        ]

        # Bun strands (circular wrap)
        self.bun_strands = [
            # Bun wrap - top arc
            StrandGroup(
                base_curve=[(-0.3, 0.0), (0.0, -0.35), (0.3, 0.0)],
                strand_count=10, spread=0.1, thickness_start=1.5, thickness_end=0.5
            ),
            # Bun wrap - bottom arc
            StrandGroup(
                base_curve=[(-0.25, 0.05), (0.0, 0.3), (0.25, 0.05)],
                strand_count=8, spread=0.1, thickness_start=1.5, thickness_end=0.5
            ),
            # Bun detail strands
            StrandGroup(
                base_curve=[(-0.15, -0.1), (0.0, 0.0), (0.15, -0.1)],
                strand_count=5, spread=0.05, thickness_start=1.0, thickness_end=0.3
            ),
        ]

        # Front bangs
        self.bang_strands = [
            # Left bang sweep
            StrandGroup(
                base_curve=[(-0.3, -0.4), (-0.4, -0.1), (-0.35, 0.1)],
                strand_count=5, spread=0.1, thickness_start=1.8, thickness_end=0.5
            ),
            # Center bangs
            StrandGroup(
                base_curve=[(0.0, -0.45), (-0.05, -0.15), (0.0, 0.05)],
                strand_count=6, spread=0.15, thickness_start=1.8, thickness_end=0.5
            ),
            # Right bang sweep
            StrandGroup(
                base_curve=[(0.3, -0.4), (0.4, -0.1), (0.35, 0.1)],
                strand_count=5, spread=0.1, thickness_start=1.8, thickness_end=0.5
            ),
        ]

        # Side wisps
        self.side_strands = [
            # Left wisp
            StrandGroup(
                base_curve=[(-0.5, -0.1), (-0.55, 0.15), (-0.5, 0.35)],
                strand_count=4, spread=0.08, thickness_start=1.2, thickness_end=0.3
            ),
            # Right wisp
            StrandGroup(
                base_curve=[(0.5, -0.1), (0.55, 0.15), (0.5, 0.35)],
                strand_count=4, spread=0.08, thickness_start=1.2, thickness_end=0.3
            ),
        ]

    def _setup_highlights(self) -> None:
        """Define highlight zones."""
        self.highlights = [
            # Main bun highlight (top)
            HairHighlight(position=(0.5, 0.2), size=0.25, intensity=0.35, hue_shift=8),
            # Secondary bun highlight
            HairHighlight(position=(0.35, 0.3), size=0.15, intensity=0.25, hue_shift=5),
            # Bang highlight
            HairHighlight(position=(0.4, 0.55), size=0.2, intensity=0.3, hue_shift=6),
        ]

    def draw(self, canvas: Canvas, x: int, y: int,
             width: int, height: int) -> None:
        """Draw the complete bun hairstyle."""
        self.draw_back(canvas, x, y, width, height)
        self.draw_bun(canvas, x, y - int(height * 0.35), int(width * 0.5), int(height * 0.4))
        self.draw_front(canvas, x, y, width, height)

    def draw_back(self, canvas: Canvas, x: int, y: int,
                  width: int, height: int) -> None:
        """Draw back hair layer."""
        colors = self._get_colors(5)
        if not colors:
            return

        base_color = colors[2] if len(colors) > 2 else colors[0]
        shadow_color = colors[3] if len(colors) > 3 else darken(base_color, 0.2)
        dark_shadow = colors[4] if len(colors) > 4 else darken(base_color, 0.35)

        # Draw solid hair mass base first (provides full coverage)
        # Multiple layers for depth
        canvas.fill_ellipse(x, y - height // 6, int(width * 0.6), int(height * 0.45), dark_shadow)
        canvas.fill_ellipse(x, y - height // 5, int(width * 0.55), int(height * 0.4), shadow_color)

        # Draw gradient layer on top
        if hasattr(canvas, 'fill_ellipse_gradient'):
            canvas.fill_ellipse_gradient(x, y - height // 4,
                                         int(width * 0.5), int(height * 0.35),
                                         colors[1], shadow_color, angle=-45)
        else:
            canvas.fill_ellipse(x, y - height // 4,
                               int(width * 0.5), int(height * 0.35), colors[2])

        # Draw back strand groups on top of base
        for group in self.back_strands:
            self._draw_strand_group(canvas, group, x, y,
                                   width * 0.6, height * 0.6, base_color)

    def draw_bun(self, canvas: Canvas, x: int, y: int,
                 width: int, height: int) -> None:
        """Draw the hair bun."""
        colors = self._get_colors(5)
        if not colors:
            return

        base_color = colors[1] if len(colors) > 1 else colors[0]
        shadow_color = colors[3] if len(colors) > 3 else darken(base_color, 0.2)

        # Draw solid bun base layers first
        canvas.fill_ellipse(x, y + 2, int(width * 0.5), int(height * 0.5), shadow_color)

        # Draw bun base with radial gradient
        if hasattr(canvas, 'fill_ellipse_radial_gradient'):
            highlight = lighten(base_color, 0.15)
            shadow = darken(base_color, 0.1)
            canvas.fill_ellipse_radial_gradient(x, y, int(width * 0.45), int(height * 0.45),
                                                highlight, shadow)
        else:
            canvas.fill_ellipse(x, y, int(width * 0.45), int(height * 0.45), base_color)

        # Draw bun strand groups on top
        for group in self.bun_strands:
            self._draw_strand_group(canvas, group, x, y,
                                   width * 0.55, height * 0.55, base_color)

        # Draw highlights on bun
        for highlight in self.highlights[:2]:  # First two are bun highlights
            self._draw_highlight_zone(canvas, highlight, x, y, width, height, base_color)

    def draw_front(self, canvas: Canvas, x: int, y: int,
                   width: int, height: int) -> None:
        """Draw front hair layer (bangs, side wisps)."""
        colors = self._get_colors(5)
        if not colors:
            return

        base_color = colors[1] if len(colors) > 1 else colors[0]

        # Draw bang strand groups
        for group in self.bang_strands:
            self._draw_strand_group(canvas, group, x, y - height // 4,
                                   width * 0.5, height * 0.5, base_color)

        # Draw side wisps
        for group in self.side_strands:
            self._draw_strand_group(canvas, group, x, y,
                                   width * 0.5, height * 0.5, base_color)

        # Draw bang highlight
        if len(self.highlights) > 2:
            self._draw_highlight_zone(canvas, self.highlights[2],
                                     x, y - height // 4, width, height, base_color)


class ProfessionalLongHair(ProfessionalHair):
    """Professional long flowing hair with strand-based rendering."""

    def __init__(self, config: Optional[ProHairConfig] = None):
        super().__init__("long_pro", config)
        self._setup_strand_groups()

    def _setup_strand_groups(self) -> None:
        """Define strand groups for long hair."""
        # Back flowing strands
        self.back_strands = [
            StrandGroup(
                base_curve=[(-0.3, -0.3), (-0.35, 0.2), (-0.3, 0.7)],
                strand_count=10, spread=0.2, thickness_start=2.0, thickness_end=0.5
            ),
            StrandGroup(
                base_curve=[(0.0, -0.35), (0.0, 0.2), (0.05, 0.75)],
                strand_count=12, spread=0.25, thickness_start=2.0, thickness_end=0.5
            ),
            StrandGroup(
                base_curve=[(0.3, -0.3), (0.35, 0.2), (0.3, 0.7)],
                strand_count=10, spread=0.2, thickness_start=2.0, thickness_end=0.5
            ),
        ]

        # Front bangs
        self.bang_strands = [
            StrandGroup(
                base_curve=[(-0.25, -0.4), (-0.3, -0.1), (-0.25, 0.1)],
                strand_count=6, spread=0.12, thickness_start=1.8, thickness_end=0.5
            ),
            StrandGroup(
                base_curve=[(0.0, -0.45), (0.0, -0.15), (0.0, 0.05)],
                strand_count=7, spread=0.15, thickness_start=1.8, thickness_end=0.5
            ),
            StrandGroup(
                base_curve=[(0.25, -0.4), (0.3, -0.1), (0.25, 0.1)],
                strand_count=6, spread=0.12, thickness_start=1.8, thickness_end=0.5
            ),
        ]

    def draw(self, canvas: Canvas, x: int, y: int,
             width: int, height: int) -> None:
        """Draw the complete long hairstyle."""
        self.draw_back(canvas, x, y, width, height)
        self.draw_front(canvas, x, y, width, height)

    def draw_back(self, canvas: Canvas, x: int, y: int,
                  width: int, height: int) -> None:
        """Draw back hair layer."""
        colors = self._get_colors(5)
        if not colors:
            return

        base_color = colors[2] if len(colors) > 2 else colors[0]

        # Draw hair mass base
        if hasattr(canvas, 'fill_ellipse_gradient'):
            shadow = darken(base_color, 0.2)
            canvas.fill_ellipse_gradient(x, y, int(width * 0.5), int(height * 0.45),
                                        colors[1], shadow, angle=-30)

        # Draw strand groups
        for group in self.back_strands:
            self._draw_strand_group(canvas, group, x, y,
                                   width * 0.5, height * 0.6, base_color)

    def draw_front(self, canvas: Canvas, x: int, y: int,
                   width: int, height: int) -> None:
        """Draw front hair layer."""
        colors = self._get_colors(5)
        if not colors:
            return

        base_color = colors[1] if len(colors) > 1 else colors[0]

        # Draw bang strands
        for group in self.bang_strands:
            self._draw_strand_group(canvas, group, x, y - height // 4,
                                   width * 0.5, height * 0.5, base_color)


# Factory function
def create_professional_hair(hair_type: str, config: Optional[ProHairConfig] = None) -> ProfessionalHair:
    """Create a professional hair style by type name.

    Args:
        hair_type: Type of hair ('bun_pro', 'long_pro')
        config: Optional configuration

    Returns:
        ProfessionalHair instance
    """
    hair_types = {
        'bun_pro': ProfessionalBunHair,
        'bun': ProfessionalBunHair,
        'long_pro': ProfessionalLongHair,
        'long': ProfessionalLongHair,
    }

    hair_class = hair_types.get(hair_type.lower(), ProfessionalBunHair)
    return hair_class(config)


# Hair type registry
PROFESSIONAL_HAIR_TYPES = {
    'bun_pro': ProfessionalBunHair,
    'long_pro': ProfessionalLongHair,
}

"""
Bodies - Body, torso, and limb shapes.

Provides body parts for different character styles and builds.
"""

import math
from typing import Optional, List, Tuple, Dict
from dataclasses import dataclass
from enum import Enum

from .base import Part, PartConfig

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.canvas import Canvas
from core.color import Color


class BodyType(Enum):
    THIN = "thin"
    AVERAGE = "average"
    MUSCULAR = "muscular"
    STOCKY = "stocky"


@dataclass(frozen=True)
class BodyProportions:
    width_scale: float
    height_scale: float
    shoulder_scale: float
    waist_scale: float


BODY_TYPE_PROPORTIONS: Dict[BodyType, BodyProportions] = {
    BodyType.THIN: BodyProportions(width_scale=0.85, height_scale=1.1, shoulder_scale=0.9, waist_scale=0.75),
    BodyType.AVERAGE: BodyProportions(width_scale=1.0, height_scale=1.0, shoulder_scale=1.0, waist_scale=1.0),
    BodyType.MUSCULAR: BodyProportions(width_scale=1.1, height_scale=1.0, shoulder_scale=1.2, waist_scale=0.9),
    BodyType.STOCKY: BodyProportions(width_scale=1.2, height_scale=0.85, shoulder_scale=1.05, waist_scale=1.15),
}


def _normalize_body_type(body_type: Optional[object]) -> BodyType:
    if body_type is None:
        return BodyType.AVERAGE
    if isinstance(body_type, BodyType):
        return body_type
    if isinstance(body_type, str):
        try:
            return BodyType[body_type.upper()]
        except KeyError as exc:
            available = ", ".join(bt.name for bt in BodyType)
            raise ValueError(f"Unknown body type '{body_type}'. Available: {available}") from exc
    raise TypeError(f"Body type must be BodyType or str, got {type(body_type).__name__}")


def get_body_proportions(body_type: Optional[object] = None) -> BodyProportions:
    """Get body proportions for a body type."""
    normalized = _normalize_body_type(body_type)
    return BODY_TYPE_PROPORTIONS[normalized]


class Body(Part):
    """Base class for body parts."""

    def __init__(self, name: str, config: Optional[PartConfig] = None,
                 body_type: Optional[object] = None):
        super().__init__(name, config)
        self.body_type = _normalize_body_type(body_type)

    def _get_proportions(self) -> BodyProportions:
        return BODY_TYPE_PROPORTIONS[self.body_type]

    def _get_scaled_dimensions(self, width: int, height: int) -> Tuple[int, int]:
        proportions = self._get_proportions()
        scaled_width = max(1, int(width * proportions.width_scale))
        scaled_height = max(1, int(height * proportions.height_scale))
        return scaled_width, scaled_height


class ChibiBody(Body):
    """Small, simple chibi body - blob-like with minimal detail."""

    def __init__(self, config: Optional[PartConfig] = None,
                 body_type: Optional[object] = None):
        super().__init__("chibi", config, body_type)

    def draw(self, canvas: Canvas, x: int, y: int,
             width: int, height: int) -> None:
        colors = self._get_colors(3)

        # Simple blob body
        scaled_width, scaled_height = self._get_scaled_dimensions(width, height)
        rx = max(1, scaled_width // 2)
        ry = max(1, scaled_height // 2)

        self._draw_shaded_ellipse(canvas, x, y, rx, ry, colors)


class SimpleBody(Body):
    """Simple rectangular body with slight taper."""

    def __init__(self, config: Optional[PartConfig] = None,
                 body_type: Optional[object] = None):
        super().__init__("simple", config, body_type)

    def draw(self, canvas: Canvas, x: int, y: int,
             width: int, height: int) -> None:
        colors = self._get_colors(3)
        style = self._get_style()

        proportions = self._get_proportions()
        scaled_width, scaled_height = self._get_scaled_dimensions(width, height)
        hw, hh = scaled_width // 2, scaled_height // 2

        # Trapezoid body (wider at shoulders)
        top_width = int(scaled_width * proportions.shoulder_scale)
        bottom_width = int(scaled_width * 0.7 * proportions.waist_scale)
        left_top = x - top_width // 2
        left_bottom = x - bottom_width // 2

        points = [
            (left_top, y - hh),
            (left_top + top_width, y - hh),
            (left_bottom + bottom_width, y + hh),
            (left_bottom, y + hh),
        ]

        base_color = colors[1] if len(colors) > 1 else colors[0]
        canvas.fill_polygon(points, base_color)

        # Highlight
        if len(colors) >= 1 and self.config.shading:
            h_width = top_width // 3
            canvas.fill_rect(x - h_width//2, y - hh + 2, h_width, scaled_height//3, colors[0])

        # Outline
        if self.config.outline and style.outline.enabled:
            outline_color = self._get_outline_color()
            for i in range(len(points)):
                p1 = points[i]
                p2 = points[(i + 1) % len(points)]
                canvas.draw_line(int(p1[0]), int(p1[1]), int(p2[0]), int(p2[1]), outline_color)


class MuscularBody(Body):
    """Wider, more muscular body shape."""

    def __init__(self, config: Optional[PartConfig] = None,
                 body_type: Optional[object] = None):
        super().__init__("muscular", config, body_type)

    def draw(self, canvas: Canvas, x: int, y: int,
             width: int, height: int) -> None:
        colors = self._get_colors(3)
        style = self._get_style()

        proportions = self._get_proportions()
        scaled_width, scaled_height = self._get_scaled_dimensions(width, height)
        hw, hh = scaled_width // 2, scaled_height // 2
        base_color = colors[1] if len(colors) > 1 else colors[0]

        # Wide shoulders
        shoulder_width = int(scaled_width * 1.1 * proportions.shoulder_scale)
        canvas.fill_ellipse(x, y - hh//2, shoulder_width//2, max(1, hh//3), base_color)

        # Core body
        core_width = max(1, int(scaled_width * proportions.shoulder_scale))
        core_height = max(1, int(scaled_height * 0.7))
        canvas.fill_rect(x - core_width//2, y - hh//3, core_width, core_height, base_color)

        # Waist taper
        waist_width = max(1, int(scaled_width * 0.35 * proportions.waist_scale))
        canvas.fill_ellipse(x, y + hh//2, waist_width, max(1, hh//4), base_color)

        # Chest definition
        if self.config.shading and len(colors) >= 3:
            # Pec shadows
            pec_rx = max(1, hw//4)
            pec_ry = max(1, hh//6)
            canvas.fill_ellipse(x - hw//4, y - hh//4, pec_rx, pec_ry, colors[2])
            canvas.fill_ellipse(x + hw//4, y - hh//4, pec_rx, pec_ry, colors[2])

        # Highlight
        if self.config.shading and len(colors) >= 1:
            canvas.fill_ellipse(x, y - hh//3, max(1, hw//3), max(1, hh//4), colors[0])

        # Outline
        if self.config.outline and style.outline.enabled:
            outline_color = self._get_outline_color()
            # Simplified outline
            canvas.draw_rect(x - hw//2, y - hh, max(1, int(scaled_width * 0.75)), scaled_height, outline_color)


class SlimBody(Body):
    """Thin, elongated body shape."""

    def __init__(self, config: Optional[PartConfig] = None,
                 body_type: Optional[object] = None):
        super().__init__("slim", config, body_type)

    def draw(self, canvas: Canvas, x: int, y: int,
             width: int, height: int) -> None:
        colors = self._get_colors(3)

        # Narrow ellipse
        scaled_width, scaled_height = self._get_scaled_dimensions(width, height)
        rx = max(1, int(scaled_width * 0.35))
        ry = max(1, scaled_height // 2)

        self._draw_shaded_ellipse(canvas, x, y, rx, ry, colors)


# =============================================================================
# Limbs
# =============================================================================

class Limb(Part):
    """Base class for arm/leg parts."""

    def __init__(self, name: str, config: Optional[PartConfig] = None):
        super().__init__(name, config)


class ChibiArm(Limb):
    """Short, simple chibi arm - tube or stub."""

    def __init__(self, config: Optional[PartConfig] = None):
        super().__init__("chibi_arm", config)

    def draw(self, canvas: Canvas, x: int, y: int,
             width: int, height: int) -> None:
        colors = self._get_colors(2)

        # Simple oval/tube
        rx = width // 2
        ry = height // 2

        base_color = colors[0] if colors else self.config.base_color
        canvas.fill_ellipse(x, y, rx, ry, base_color)

        if self.config.outline:
            outline_color = self._get_outline_color()
            for angle in range(0, 360, 8):
                rad = math.radians(angle)
                ox = int(x + rx * math.cos(rad))
                oy = int(y + ry * math.sin(rad))
                canvas.set_pixel(ox, oy, outline_color)


class SimpleArm(Limb):
    """Simple arm with slight taper."""

    def __init__(self, config: Optional[PartConfig] = None):
        super().__init__("simple_arm", config)

    def draw(self, canvas: Canvas, x: int, y: int,
             width: int, height: int) -> None:
        colors = self._get_colors(2)
        style = self._get_style()

        hw, hh = width // 2, height // 2

        # Tapered arm
        top_width = width
        bottom_width = int(width * 0.7)

        points = [
            (x - top_width//2, y - hh),
            (x + top_width//2, y - hh),
            (x + bottom_width//2, y + hh),
            (x - bottom_width//2, y + hh),
        ]

        base_color = colors[0] if colors else self.config.base_color
        canvas.fill_polygon(points, base_color)

        if self.config.outline and style.outline.enabled:
            outline_color = self._get_outline_color()
            for i in range(len(points)):
                p1 = points[i]
                p2 = points[(i + 1) % len(points)]
                canvas.draw_line(int(p1[0]), int(p1[1]), int(p2[0]), int(p2[1]), outline_color)


class ChibiLeg(Limb):
    """Short, stubby chibi leg."""

    def __init__(self, config: Optional[PartConfig] = None):
        super().__init__("chibi_leg", config)

    def draw(self, canvas: Canvas, x: int, y: int,
             width: int, height: int) -> None:
        colors = self._get_colors(2)

        # Simple rounded rectangle
        hw, hh = width // 2, height // 2
        base_color = colors[0] if colors else self.config.base_color

        canvas.fill_rect(x - hw, y - hh, width, height, base_color)
        canvas.fill_circle(x, y + hh, hw, base_color)  # Rounded foot

        if self.config.outline:
            outline_color = self._get_outline_color()
            canvas.draw_rect(x - hw, y - hh, width, height, outline_color)


class SimpleLeg(Limb):
    """Simple leg with slight taper."""

    def __init__(self, config: Optional[PartConfig] = None):
        super().__init__("simple_leg", config)

    def draw(self, canvas: Canvas, x: int, y: int,
             width: int, height: int) -> None:
        colors = self._get_colors(2)
        style = self._get_style()

        hw, hh = width // 2, height // 2

        # Tapered leg
        top_width = int(width * 0.9)
        bottom_width = int(width * 0.6)

        points = [
            (x - top_width//2, y - hh),
            (x + top_width//2, y - hh),
            (x + bottom_width//2, y + hh),
            (x - bottom_width//2, y + hh),
        ]

        base_color = colors[0] if colors else self.config.base_color
        canvas.fill_polygon(points, base_color)

        if self.config.outline and style.outline.enabled:
            outline_color = self._get_outline_color()
            for i in range(len(points)):
                p1 = points[i]
                p2 = points[(i + 1) % len(points)]
                canvas.draw_line(int(p1[0]), int(p1[1]), int(p2[0]), int(p2[1]), outline_color)


class Hand(Part):
    """Simple hand shape."""

    def __init__(self, config: Optional[PartConfig] = None):
        super().__init__("hand", config)

    def draw(self, canvas: Canvas, x: int, y: int,
             width: int, height: int) -> None:
        colors = self._get_colors(2)

        # Simple circle or oval
        r = min(width, height) // 2
        base_color = colors[0] if colors else self.config.base_color

        canvas.fill_circle(x, y, r, base_color)

        if self.config.outline:
            outline_color = self._get_outline_color()
            canvas.draw_circle(x, y, r, outline_color)


class Foot(Part):
    """Simple foot shape."""

    def __init__(self, config: Optional[PartConfig] = None):
        super().__init__("foot", config)

    def draw(self, canvas: Canvas, x: int, y: int,
             width: int, height: int) -> None:
        colors = self._get_colors(2)

        # Oval foot
        rx = width // 2
        ry = height // 3  # Flatter than wide

        base_color = colors[0] if colors else self.config.base_color
        canvas.fill_ellipse(x, y, rx, ry, base_color)

        if self.config.outline:
            outline_color = self._get_outline_color()
            for angle in range(0, 360, 8):
                rad = math.radians(angle)
                ox = int(x + rx * math.cos(rad))
                oy = int(y + ry * math.sin(rad))
                canvas.set_pixel(ox, oy, outline_color)


# =============================================================================
# Body Factory
# =============================================================================

BODY_TYPES = {
    'chibi': ChibiBody,
    'simple': SimpleBody,
    'muscular': MuscularBody,
    'slim': SlimBody,
}

LIMB_TYPES = {
    'chibi_arm': ChibiArm,
    'simple_arm': SimpleArm,
    'chibi_leg': ChibiLeg,
    'simple_leg': SimpleLeg,
    'hand': Hand,
    'foot': Foot,
}


def create_body(body_shape: str, config: Optional[PartConfig] = None,
                body_type: Optional[object] = None) -> Body:
    """Create a body part by type name.

    Args:
        body_shape: Body shape name ('chibi', 'simple', 'muscular', 'slim')
        config: Part configuration
        body_type: Body proportions (BodyType or str)

    Returns:
        Body instance
    """
    if body_shape not in BODY_TYPES:
        available = ', '.join(BODY_TYPES.keys())
        raise ValueError(f"Unknown body type '{body_shape}'. Available: {available}")

    normalized_body_type = _normalize_body_type(body_type)
    return BODY_TYPES[body_shape](config, body_type=normalized_body_type)


def create_limb(limb_type: str, config: Optional[PartConfig] = None) -> Limb:
    """Create a limb part by type name.

    Args:
        limb_type: Limb type name
        config: Part configuration

    Returns:
        Limb instance
    """
    if limb_type not in LIMB_TYPES:
        available = ', '.join(LIMB_TYPES.keys())
        raise ValueError(f"Unknown limb type '{limb_type}'. Available: {available}")

    return LIMB_TYPES[limb_type](config)


def list_body_types() -> List[str]:
    """Get list of available body types."""
    return list(BODY_TYPES.keys())


def list_limb_types() -> List[str]:
    """Get list of available limb types."""
    return list(LIMB_TYPES.keys())

"""
Eyes - Eye types, expressions, and rendering.

Provides various eye styles and expression system for characters.
"""

import math
from typing import Optional, List, Tuple
from dataclasses import dataclass

from .base import Part, PartConfig

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.canvas import Canvas
from core.color import Color, darken, lighten


@dataclass
class EyeColors:
    """Color scheme for eyes."""

    # Main colors
    iris: Color = (80, 120, 200, 255)  # Iris color
    pupil: Color = (20, 20, 30, 255)   # Pupil color
    white: Color = (255, 255, 255, 255)  # Sclera
    highlight: Color = (255, 255, 255, 255)  # Catchlight

    # Optional
    iris_dark: Optional[Color] = None  # Darker iris ring
    iris_light: Optional[Color] = None  # Lighter iris center


class Eyes(Part):
    """Base class for eye parts."""

    def __init__(self, name: str, config: Optional[PartConfig] = None):
        super().__init__(name, config)
        self.eye_colors = EyeColors()
        self.expression = 'neutral'

    def set_colors(self, iris: Color, pupil: Color = (20, 20, 30, 255)) -> 'Eyes':
        """Set eye colors."""
        self.eye_colors.iris = iris
        self.eye_colors.pupil = pupil
        self.eye_colors.iris_dark = darken(iris, 0.3)
        self.eye_colors.iris_light = lighten(iris, 0.3)
        return self

    def set_expression(self, expression: str) -> 'Eyes':
        """Set eye expression."""
        self.expression = expression
        return self

    def draw_pair(self, canvas: Canvas, left_x: int, left_y: int,
                  right_x: int, right_y: int, width: int, height: int) -> None:
        """Draw both eyes at specified positions.

        Args:
            canvas: Target canvas
            left_x, left_y: Left eye center
            right_x, right_y: Right eye center
            width, height: Size of each eye
        """
        # Left eye
        self.draw(canvas, left_x, left_y, width, height, is_left=True)
        # Right eye
        self.draw(canvas, right_x, right_y, width, height, is_left=False)

    def draw(self, canvas: Canvas, x: int, y: int,
             width: int, height: int, is_left: bool = True) -> None:
        """Draw a single eye."""
        raise NotImplementedError("Subclasses must implement draw()")


class SimpleEyes(Eyes):
    """Simple dot eyes - minimal style."""

    def __init__(self, config: Optional[PartConfig] = None):
        super().__init__("simple", config)

    def draw(self, canvas: Canvas, x: int, y: int,
             width: int, height: int, is_left: bool = True) -> None:
        # Simple filled circle
        r = min(width, height) // 2
        canvas.fill_circle(x, y, r, self.eye_colors.pupil)


class RoundEyes(Eyes):
    """Round eyes with iris, pupil, and highlight."""

    def __init__(self, config: Optional[PartConfig] = None):
        super().__init__("round", config)

    def draw(self, canvas: Canvas, x: int, y: int,
             width: int, height: int, is_left: bool = True) -> None:
        r = min(width, height) // 2

        # Expression modifications
        squint = 0
        if self.expression == 'happy':
            squint = r // 3
        elif self.expression == 'angry':
            squint = r // 4

        # White of eye
        if squint == 0:
            canvas.fill_circle(x, y, r, self.eye_colors.white)
        else:
            # Squinted - draw as ellipse
            canvas.fill_ellipse(x, y, r, r - squint, self.eye_colors.white)

        # Iris
        iris_r = int(r * 0.7)
        canvas.fill_circle(x, y, iris_r, self.eye_colors.iris)

        # Iris gradient/detail
        if self.eye_colors.iris_dark:
            canvas.fill_circle(x, y, iris_r - 1, self.eye_colors.iris_dark)
            canvas.fill_circle(x, y - 1, iris_r - 2, self.eye_colors.iris)

        # Pupil
        pupil_r = int(r * 0.35)
        canvas.fill_circle(x, y, pupil_r, self.eye_colors.pupil)

        # Highlight (catchlight)
        hl_r = max(1, r // 4)
        hl_x = x - r // 3 if is_left else x - r // 3
        hl_y = y - r // 3
        canvas.fill_circle(hl_x, hl_y, hl_r, self.eye_colors.highlight)

        # Outline
        if self.config.outline:
            outline_color = darken(self.eye_colors.white, 0.5)
            canvas.draw_circle(x, y, r, outline_color)


class LargeEyes(Eyes):
    """Large anime-style eyes with detailed iris."""

    def __init__(self, config: Optional[PartConfig] = None):
        super().__init__("large", config)

    def draw(self, canvas: Canvas, x: int, y: int,
             width: int, height: int, is_left: bool = True) -> None:
        hw, hh = width // 2, height // 2

        # Expression adjustments
        top_lid = 0
        bottom_lid = 0
        if self.expression == 'happy':
            top_lid = hh // 2
            bottom_lid = hh // 3
        elif self.expression == 'sad':
            if is_left:
                top_lid = hh // 4  # Asymmetric
        elif self.expression == 'angry':
            if is_left:
                top_lid = hh // 3
            else:
                top_lid = hh // 4

        # White (elliptical)
        canvas.fill_ellipse(x, y, hw, hh, self.eye_colors.white)

        # Eyelid coverage (for expressions)
        if top_lid > 0:
            # Draw skin color over top of eye
            skin = self.config.base_color if self.config else (240, 200, 180, 255)
            canvas.fill_rect(x - hw, y - hh, width, top_lid, skin)

        # Iris (large, oval)
        iris_w = int(hw * 0.85)
        iris_h = int(hh * 0.9)
        canvas.fill_ellipse(x, y, iris_w, iris_h, self.eye_colors.iris)

        # Iris detail - darker outer ring
        if self.eye_colors.iris_dark:
            canvas.fill_ellipse(x, y, iris_w - 1, iris_h - 1, self.eye_colors.iris_dark)
            canvas.fill_ellipse(x, y - 1, iris_w - 2, iris_h - 2, self.eye_colors.iris)

        # Light reflection in iris
        if self.eye_colors.iris_light:
            canvas.fill_ellipse(x, y - hh//4, iris_w//2, iris_h//3, self.eye_colors.iris_light)

        # Pupil (vertical oval for anime look)
        pupil_w = int(hw * 0.35)
        pupil_h = int(hh * 0.5)
        canvas.fill_ellipse(x, y, pupil_w, pupil_h, self.eye_colors.pupil)

        # Multiple highlights for sparkle effect
        # Main highlight
        hl_x = x - hw // 3
        hl_y = y - hh // 3
        canvas.fill_circle(hl_x, hl_y, max(2, hw // 3), self.eye_colors.highlight)

        # Secondary smaller highlight
        hl2_x = x + hw // 4
        hl2_y = y + hh // 4
        canvas.fill_circle(hl2_x, hl2_y, max(1, hw // 5), self.eye_colors.highlight)

        # Outline
        if self.config.outline:
            outline_color = (40, 40, 50, 255)
            # Top lid line (thicker)
            for dx in range(-hw, hw + 1):
                canvas.set_pixel(x + dx, y - hh, outline_color)
                canvas.set_pixel(x + dx, y - hh + 1, outline_color)


class SparkleEyes(Eyes):
    """Extra sparkly anime eyes with multiple highlights."""

    def __init__(self, config: Optional[PartConfig] = None):
        super().__init__("sparkle", config)

    def draw(self, canvas: Canvas, x: int, y: int,
             width: int, height: int, is_left: bool = True) -> None:
        hw, hh = width // 2, height // 2

        # White
        canvas.fill_ellipse(x, y, hw, hh, self.eye_colors.white)

        # Iris with gradient
        iris_w = int(hw * 0.9)
        iris_h = int(hh * 0.95)
        canvas.fill_ellipse(x, y, iris_w, iris_h, self.eye_colors.iris)

        # Iris inner glow
        if self.eye_colors.iris_light:
            canvas.fill_ellipse(x, y - 2, iris_w - 2, iris_h - 3, self.eye_colors.iris_light)

        # Pupil
        pupil_w = int(hw * 0.3)
        pupil_h = int(hh * 0.45)
        canvas.fill_ellipse(x, y + 1, pupil_w, pupil_h, self.eye_colors.pupil)

        # Multiple sparkle highlights
        # Large main highlight
        canvas.fill_circle(x - hw//3, y - hh//3, max(2, hw//3), self.eye_colors.highlight)

        # Medium secondary
        canvas.fill_circle(x + hw//4, y + hh//5, max(1, hw//4), self.eye_colors.highlight)

        # Small accent sparkles
        canvas.fill_circle(x - hw//2, y, max(1, hw//6), self.eye_colors.highlight)
        canvas.fill_circle(x + hw//3, y - hh//4, max(1, hw//6), self.eye_colors.highlight)


class ClosedEyes(Eyes):
    """Closed/sleeping eyes - curved lines."""

    def __init__(self, config: Optional[PartConfig] = None):
        super().__init__("closed", config)

    def draw(self, canvas: Canvas, x: int, y: int,
             width: int, height: int, is_left: bool = True) -> None:
        hw = width // 2

        # Draw curved line for closed eye
        line_color = (40, 40, 50, 255)

        # Arc using points
        for i in range(-hw, hw + 1):
            # Gentle curve
            curve_y = int(abs(i) * 0.3)
            if self.expression == 'happy':
                curve_y = -curve_y  # Smile shape (^)
            canvas.set_pixel(x + i, y + curve_y, line_color)


class AngryEyes(Eyes):
    """Angry/determined eyes with angled brows."""

    def __init__(self, config: Optional[PartConfig] = None):
        super().__init__("angry", config)
        self.expression = 'angry'

    def draw(self, canvas: Canvas, x: int, y: int,
             width: int, height: int, is_left: bool = True) -> None:
        hw, hh = width // 2, height // 2

        # Narrowed white
        canvas.fill_ellipse(x, y, hw, hh - 2, self.eye_colors.white)

        # Iris
        iris_r = int(min(hw, hh) * 0.65)
        canvas.fill_circle(x, y + 1, iris_r, self.eye_colors.iris)

        # Pupil (smaller, focused)
        pupil_r = int(iris_r * 0.4)
        canvas.fill_circle(x, y + 1, pupil_r, self.eye_colors.pupil)

        # Single sharp highlight
        canvas.fill_circle(x - hw//4, y - hh//4, max(1, hw//4), self.eye_colors.highlight)

        # Angry brow line
        brow_color = (40, 40, 50, 255)
        if is_left:
            # Slopes down toward center
            canvas.draw_line(x - hw, y - hh - 1, x + hw//2, y - hh + 2, brow_color, 2)
        else:
            # Slopes down toward center (mirrored)
            canvas.draw_line(x - hw//2, y - hh + 2, x + hw, y - hh - 1, brow_color, 2)


class SadEyes(Eyes):
    """Sad/worried eyes with upturned brows."""

    def __init__(self, config: Optional[PartConfig] = None):
        super().__init__("sad", config)
        self.expression = 'sad'

    def draw(self, canvas: Canvas, x: int, y: int,
             width: int, height: int, is_left: bool = True) -> None:
        hw, hh = width // 2, height // 2

        # Slightly droopy eye shape
        canvas.fill_ellipse(x, y, hw, hh, self.eye_colors.white)

        # Iris (looking down slightly)
        iris_r = int(min(hw, hh) * 0.7)
        canvas.fill_circle(x, y + 2, iris_r, self.eye_colors.iris)

        # Pupil
        pupil_r = int(iris_r * 0.45)
        canvas.fill_circle(x, y + 2, pupil_r, self.eye_colors.pupil)

        # Slightly dimmer highlight
        hl_color = (230, 230, 240, 255)
        canvas.fill_circle(x - hw//3, y - hh//4, max(1, hw//4), hl_color)

        # Worried brow
        brow_color = (40, 40, 50, 255)
        if is_left:
            # Slopes up toward center
            canvas.draw_line(x - hw, y - hh + 2, x + hw//2, y - hh - 2, brow_color)
        else:
            canvas.draw_line(x - hw//2, y - hh - 2, x + hw, y - hh + 2, brow_color)


# =============================================================================
# Eye Factory
# =============================================================================

EYE_TYPES = {
    'simple': SimpleEyes,
    'round': RoundEyes,
    'large': LargeEyes,
    'sparkle': SparkleEyes,
    'closed': ClosedEyes,
    'angry': AngryEyes,
    'sad': SadEyes,
}


def create_eyes(eye_type: str, config: Optional[PartConfig] = None) -> Eyes:
    """Create an eyes part by type name.

    Args:
        eye_type: Eye style name ('simple', 'round', 'large', 'sparkle', 'closed', 'angry', 'sad')
        config: Part configuration

    Returns:
        Eyes instance
    """
    if eye_type not in EYE_TYPES:
        available = ', '.join(EYE_TYPES.keys())
        raise ValueError(f"Unknown eye type '{eye_type}'. Available: {available}")

    return EYE_TYPES[eye_type](config)


def list_eye_types() -> List[str]:
    """Get list of available eye types."""
    return list(EYE_TYPES.keys())


# =============================================================================
# Eye Color Presets
# =============================================================================

def blue_eyes() -> EyeColors:
    """Classic blue eye colors."""
    return EyeColors(
        iris=(80, 130, 200, 255),
        iris_dark=(50, 90, 160, 255),
        iris_light=(120, 170, 230, 255),
    )


def green_eyes() -> EyeColors:
    """Green eye colors."""
    return EyeColors(
        iris=(80, 160, 100, 255),
        iris_dark=(50, 120, 70, 255),
        iris_light=(120, 200, 140, 255),
    )


def brown_eyes() -> EyeColors:
    """Brown eye colors."""
    return EyeColors(
        iris=(140, 90, 60, 255),
        iris_dark=(100, 60, 40, 255),
        iris_light=(180, 130, 100, 255),
    )


def purple_eyes() -> EyeColors:
    """Purple/violet eye colors."""
    return EyeColors(
        iris=(150, 80, 180, 255),
        iris_dark=(110, 50, 140, 255),
        iris_light=(190, 120, 220, 255),
    )


def red_eyes() -> EyeColors:
    """Red eye colors."""
    return EyeColors(
        iris=(200, 60, 60, 255),
        iris_dark=(160, 40, 40, 255),
        iris_light=(230, 100, 100, 255),
    )


def gold_eyes() -> EyeColors:
    """Gold/amber eye colors."""
    return EyeColors(
        iris=(220, 180, 60, 255),
        iris_dark=(180, 140, 40, 255),
        iris_light=(250, 220, 100, 255),
    )


EYE_COLOR_PRESETS = {
    'blue': blue_eyes,
    'green': green_eyes,
    'brown': brown_eyes,
    'purple': purple_eyes,
    'red': red_eyes,
    'gold': gold_eyes,
}


def get_eye_colors(preset: str) -> EyeColors:
    """Get eye color preset by name."""
    if preset not in EYE_COLOR_PRESETS:
        available = ', '.join(EYE_COLOR_PRESETS.keys())
        raise ValueError(f"Unknown eye color preset '{preset}'. Available: {available}")
    return EYE_COLOR_PRESETS[preset]()

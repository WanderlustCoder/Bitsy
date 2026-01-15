"""
Screen - Full-screen visual effects.

Provides:
- Screen flash (hit flash, damage indicators)
- Screen shake (impact effects)
- Fade in/out transitions
- Color overlays and filters
- Vignette effects
"""

import math
import random
from typing import Tuple, Optional, List, Callable
from dataclasses import dataclass
from enum import Enum

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Canvas


class BlendMode(Enum):
    """Blend modes for screen effects."""
    NORMAL = 'normal'
    ADD = 'add'
    MULTIPLY = 'multiply'
    SCREEN = 'screen'
    OVERLAY = 'overlay'


@dataclass
class ScreenShake:
    """Screen shake effect state.

    Attributes:
        intensity: Maximum shake offset in pixels
        duration: Total shake duration
        frequency: Shake frequency (shakes per second)
        decay: Whether intensity decays over time
        elapsed: Time elapsed since start
        active: Whether shake is active
    """

    intensity: float = 5.0
    duration: float = 0.3
    frequency: float = 30.0
    decay: bool = True
    elapsed: float = 0.0
    active: bool = False

    # Internal state
    _seed: int = 42
    _rng: random.Random = None

    def __post_init__(self):
        self._rng = random.Random(self._seed)

    def start(self, intensity: Optional[float] = None,
              duration: Optional[float] = None) -> None:
        """Start or restart screen shake.

        Args:
            intensity: Override intensity
            duration: Override duration
        """
        if intensity is not None:
            self.intensity = intensity
        if duration is not None:
            self.duration = duration
        self.elapsed = 0.0
        self.active = True

    def update(self, dt: float) -> None:
        """Update shake state.

        Args:
            dt: Delta time in seconds
        """
        if not self.active:
            return

        self.elapsed += dt
        if self.elapsed >= self.duration:
            self.active = False

    def get_offset(self) -> Tuple[int, int]:
        """Get current shake offset.

        Returns:
            (x_offset, y_offset) in pixels
        """
        if not self.active:
            return (0, 0)

        # Calculate current intensity with decay
        if self.decay:
            ratio = 1.0 - (self.elapsed / self.duration)
            current_intensity = self.intensity * ratio
        else:
            current_intensity = self.intensity

        # Generate pseudo-random offset based on time
        t = self.elapsed * self.frequency
        # Use sine waves with different frequencies for organic feel
        offset_x = math.sin(t * 7.3) * current_intensity
        offset_y = math.sin(t * 11.7) * current_intensity

        return (int(offset_x), int(offset_y))

    def stop(self) -> None:
        """Stop screen shake immediately."""
        self.active = False


@dataclass
class ScreenFlash:
    """Screen flash effect state.

    Attributes:
        color: Flash color (RGBA)
        duration: Flash duration
        intensity: Initial intensity (0-1)
        elapsed: Time elapsed
        active: Whether flash is active
        blend_mode: How flash blends with screen
    """

    color: Tuple[int, int, int, int] = (255, 255, 255, 255)
    duration: float = 0.2
    intensity: float = 1.0
    elapsed: float = 0.0
    active: bool = False
    blend_mode: BlendMode = BlendMode.ADD

    def start(self, color: Optional[Tuple[int, int, int, int]] = None,
              duration: Optional[float] = None,
              intensity: Optional[float] = None) -> None:
        """Start or restart screen flash.

        Args:
            color: Override color
            duration: Override duration
            intensity: Override intensity
        """
        if color is not None:
            self.color = color
        if duration is not None:
            self.duration = duration
        if intensity is not None:
            self.intensity = intensity
        self.elapsed = 0.0
        self.active = True

    def update(self, dt: float) -> None:
        """Update flash state."""
        if not self.active:
            return

        self.elapsed += dt
        if self.elapsed >= self.duration:
            self.active = False

    def get_alpha(self) -> int:
        """Get current flash alpha.

        Returns:
            Alpha value 0-255
        """
        if not self.active:
            return 0

        # Fade out over duration
        ratio = 1.0 - (self.elapsed / self.duration)
        return int(self.color[3] * self.intensity * ratio)

    def apply(self, canvas: Canvas) -> None:
        """Apply flash effect to canvas.

        Args:
            canvas: Canvas to apply effect to
        """
        if not self.active:
            return

        alpha = self.get_alpha()
        if alpha <= 0:
            return

        flash_color = (self.color[0], self.color[1], self.color[2], alpha)

        for y in range(canvas.height):
            for x in range(canvas.width):
                src = canvas.pixels[y][x]
                if src[3] > 0:  # Only affect visible pixels
                    blended = self._blend(src, flash_color)
                    canvas.set_pixel(x, y, blended)

    def _blend(self, base: Tuple[int, int, int, int],
               overlay: Tuple[int, int, int, int]) -> Tuple[int, int, int, int]:
        """Blend two colors based on blend mode."""
        if self.blend_mode == BlendMode.ADD:
            return (
                min(255, base[0] + overlay[0] * overlay[3] // 255),
                min(255, base[1] + overlay[1] * overlay[3] // 255),
                min(255, base[2] + overlay[2] * overlay[3] // 255),
                base[3]
            )
        elif self.blend_mode == BlendMode.MULTIPLY:
            factor = overlay[3] / 255
            return (
                int(base[0] * (1 - factor + factor * overlay[0] / 255)),
                int(base[1] * (1 - factor + factor * overlay[1] / 255)),
                int(base[2] * (1 - factor + factor * overlay[2] / 255)),
                base[3]
            )
        elif self.blend_mode == BlendMode.SCREEN:
            factor = overlay[3] / 255
            return (
                int(255 - (255 - base[0]) * (1 - factor * overlay[0] / 255)),
                int(255 - (255 - base[1]) * (1 - factor * overlay[1] / 255)),
                int(255 - (255 - base[2]) * (1 - factor * overlay[2] / 255)),
                base[3]
            )
        else:  # NORMAL
            factor = overlay[3] / 255
            return (
                int(base[0] * (1 - factor) + overlay[0] * factor),
                int(base[1] * (1 - factor) + overlay[1] * factor),
                int(base[2] * (1 - factor) + overlay[2] * factor),
                base[3]
            )

    def stop(self) -> None:
        """Stop flash immediately."""
        self.active = False


@dataclass
class ScreenFade:
    """Screen fade in/out effect.

    Attributes:
        color: Fade color (usually black or white)
        duration: Fade duration
        fade_in: True for fade in, False for fade out
        elapsed: Time elapsed
        active: Whether fade is active
        hold: Whether to hold at end state
    """

    color: Tuple[int, int, int, int] = (0, 0, 0, 255)
    duration: float = 0.5
    fade_in: bool = True
    elapsed: float = 0.0
    active: bool = False
    hold: bool = False

    def start_fade_in(self, duration: Optional[float] = None,
                      color: Optional[Tuple[int, int, int, int]] = None) -> None:
        """Start fade in (from color to clear)."""
        self.fade_in = True
        if duration is not None:
            self.duration = duration
        if color is not None:
            self.color = color
        self.elapsed = 0.0
        self.active = True

    def start_fade_out(self, duration: Optional[float] = None,
                       color: Optional[Tuple[int, int, int, int]] = None) -> None:
        """Start fade out (from clear to color)."""
        self.fade_in = False
        if duration is not None:
            self.duration = duration
        if color is not None:
            self.color = color
        self.elapsed = 0.0
        self.active = True

    def update(self, dt: float) -> None:
        """Update fade state."""
        if not self.active:
            return

        self.elapsed += dt
        if self.elapsed >= self.duration:
            if not self.hold:
                self.active = False

    def get_alpha(self) -> int:
        """Get current fade alpha."""
        if not self.active and not self.hold:
            return 0

        ratio = min(1.0, self.elapsed / self.duration)

        if self.fade_in:
            # Fade in: start opaque, end transparent
            return int(self.color[3] * (1.0 - ratio))
        else:
            # Fade out: start transparent, end opaque
            return int(self.color[3] * ratio)

    def apply(self, canvas: Canvas) -> None:
        """Apply fade overlay to canvas."""
        alpha = self.get_alpha()
        if alpha <= 0:
            return

        fade_color = (self.color[0], self.color[1], self.color[2], alpha)

        for y in range(canvas.height):
            for x in range(canvas.width):
                src = canvas.pixels[y][x]
                # Alpha blend
                factor = alpha / 255
                blended = (
                    int(src[0] * (1 - factor) + fade_color[0] * factor),
                    int(src[1] * (1 - factor) + fade_color[1] * factor),
                    int(src[2] * (1 - factor) + fade_color[2] * factor),
                    src[3]
                )
                canvas.set_pixel(x, y, blended)

    @property
    def is_complete(self) -> bool:
        """Check if fade has completed."""
        return self.elapsed >= self.duration

    def stop(self) -> None:
        """Stop fade immediately."""
        self.active = False
        self.hold = False


class Vignette:
    """Vignette effect (darkening around edges)."""

    def __init__(self, intensity: float = 0.5, radius: float = 0.7,
                 color: Tuple[int, int, int, int] = (0, 0, 0, 255)):
        """Initialize vignette.

        Args:
            intensity: Darkness intensity (0-1)
            radius: Inner radius before darkening starts (0-1)
            color: Vignette color
        """
        self.intensity = intensity
        self.radius = radius
        self.color = color

    def apply(self, canvas: Canvas) -> None:
        """Apply vignette effect to canvas."""
        cx = canvas.width / 2
        cy = canvas.height / 2
        max_dist = math.sqrt(cx * cx + cy * cy)

        for y in range(canvas.height):
            for x in range(canvas.width):
                # Calculate distance from center (normalized)
                dx = (x - cx) / cx if cx > 0 else 0
                dy = (y - cy) / cy if cy > 0 else 0
                dist = math.sqrt(dx * dx + dy * dy)

                # Calculate vignette factor
                if dist <= self.radius:
                    factor = 0.0
                else:
                    factor = (dist - self.radius) / (1.0 - self.radius)
                    factor = min(1.0, factor * self.intensity)

                if factor > 0:
                    src = canvas.pixels[y][x]
                    blended = (
                        int(src[0] * (1 - factor) + self.color[0] * factor),
                        int(src[1] * (1 - factor) + self.color[1] * factor),
                        int(src[2] * (1 - factor) + self.color[2] * factor),
                        src[3]
                    )
                    canvas.set_pixel(x, y, blended)


class ColorFilter:
    """Apply color filter/tint to screen."""

    def __init__(self, color: Tuple[int, int, int, int] = (255, 255, 255, 255),
                 blend_mode: BlendMode = BlendMode.MULTIPLY):
        """Initialize color filter.

        Args:
            color: Filter color
            blend_mode: How filter blends
        """
        self.color = color
        self.blend_mode = blend_mode

    def apply(self, canvas: Canvas) -> None:
        """Apply color filter to canvas."""
        for y in range(canvas.height):
            for x in range(canvas.width):
                src = canvas.pixels[y][x]
                if src[3] > 0:
                    filtered = self._apply_filter(src)
                    canvas.set_pixel(x, y, filtered)

    def _apply_filter(self, color: Tuple[int, int, int, int]) -> Tuple[int, int, int, int]:
        """Apply filter to a single color."""
        if self.blend_mode == BlendMode.MULTIPLY:
            return (
                color[0] * self.color[0] // 255,
                color[1] * self.color[1] // 255,
                color[2] * self.color[2] // 255,
                color[3]
            )
        elif self.blend_mode == BlendMode.ADD:
            return (
                min(255, color[0] + self.color[0]),
                min(255, color[1] + self.color[1]),
                min(255, color[2] + self.color[2]),
                color[3]
            )
        elif self.blend_mode == BlendMode.SCREEN:
            return (
                255 - (255 - color[0]) * (255 - self.color[0]) // 255,
                255 - (255 - color[1]) * (255 - self.color[1]) // 255,
                255 - (255 - color[2]) * (255 - self.color[2]) // 255,
                color[3]
            )
        else:  # NORMAL - just tint
            factor = self.color[3] / 255
            return (
                int(color[0] * (1 - factor) + self.color[0] * factor),
                int(color[1] * (1 - factor) + self.color[1] * factor),
                int(color[2] * (1 - factor) + self.color[2] * factor),
                color[3]
            )


class Scanlines:
    """CRT-style scanline effect."""

    def __init__(self, spacing: int = 2, intensity: float = 0.3,
                 color: Tuple[int, int, int, int] = (0, 0, 0, 255)):
        """Initialize scanlines.

        Args:
            spacing: Pixels between scanlines
            intensity: Darkness of scanlines (0-1)
            color: Scanline color
        """
        self.spacing = spacing
        self.intensity = intensity
        self.color = color

    def apply(self, canvas: Canvas) -> None:
        """Apply scanline effect."""
        for y in range(canvas.height):
            if y % self.spacing == 0:
                for x in range(canvas.width):
                    src = canvas.pixels[y][x]
                    if src[3] > 0:
                        darkened = (
                            int(src[0] * (1 - self.intensity)),
                            int(src[1] * (1 - self.intensity)),
                            int(src[2] * (1 - self.intensity)),
                            src[3]
                        )
                        canvas.set_pixel(x, y, darkened)


class ChromaticAberration:
    """RGB channel separation effect."""

    def __init__(self, offset: int = 2):
        """Initialize chromatic aberration.

        Args:
            offset: Pixel offset for R and B channels
        """
        self.offset = offset

    def apply(self, canvas: Canvas) -> None:
        """Apply chromatic aberration effect."""
        # Create copies of channels with offsets
        original = canvas.copy()

        for y in range(canvas.height):
            for x in range(canvas.width):
                # Red channel shifted left
                rx = max(0, x - self.offset)
                r = original.pixels[y][rx][0]

                # Green channel stays
                g = original.pixels[y][x][1]

                # Blue channel shifted right
                bx = min(canvas.width - 1, x + self.offset)
                b = original.pixels[y][bx][2]

                a = original.pixels[y][x][3]

                canvas.set_pixel(x, y, (r, g, b, a))


class ScreenEffects:
    """Manager for multiple screen effects."""

    def __init__(self):
        self.shake = ScreenShake()
        self.flash = ScreenFlash()
        self.fade = ScreenFade()
        self.vignette: Optional[Vignette] = None
        self.color_filter: Optional[ColorFilter] = None
        self.scanlines: Optional[Scanlines] = None
        self.chromatic: Optional[ChromaticAberration] = None

    def update(self, dt: float) -> None:
        """Update all active effects."""
        self.shake.update(dt)
        self.flash.update(dt)
        self.fade.update(dt)

    def apply(self, canvas: Canvas) -> Canvas:
        """Apply all effects and return modified canvas.

        Args:
            canvas: Source canvas

        Returns:
            New canvas with effects applied
        """
        # Apply shake by creating offset canvas
        result = Canvas(canvas.width, canvas.height, (0, 0, 0, 0))
        offset_x, offset_y = self.shake.get_offset()
        result.blit(canvas, offset_x, offset_y)

        # Apply other effects
        self.flash.apply(result)
        self.fade.apply(result)

        if self.vignette:
            self.vignette.apply(result)
        if self.color_filter:
            self.color_filter.apply(result)
        if self.scanlines:
            self.scanlines.apply(result)
        if self.chromatic:
            self.chromatic.apply(result)

        return result

    def trigger_shake(self, intensity: float = 5.0, duration: float = 0.3) -> None:
        """Trigger screen shake."""
        self.shake.start(intensity, duration)

    def trigger_flash(self, color: Tuple[int, int, int, int] = (255, 255, 255, 255),
                      duration: float = 0.2) -> None:
        """Trigger screen flash."""
        self.flash.start(color, duration)

    def trigger_fade_in(self, duration: float = 0.5,
                        color: Tuple[int, int, int, int] = (0, 0, 0, 255)) -> None:
        """Trigger fade in."""
        self.fade.start_fade_in(duration, color)

    def trigger_fade_out(self, duration: float = 0.5,
                         color: Tuple[int, int, int, int] = (0, 0, 0, 255)) -> None:
        """Trigger fade out."""
        self.fade.start_fade_out(duration, color)

    def set_vignette(self, intensity: float = 0.5, radius: float = 0.7) -> None:
        """Enable vignette effect."""
        self.vignette = Vignette(intensity, radius)

    def clear_vignette(self) -> None:
        """Disable vignette effect."""
        self.vignette = None

    def set_color_filter(self, color: Tuple[int, int, int, int],
                         blend_mode: BlendMode = BlendMode.MULTIPLY) -> None:
        """Set color filter."""
        self.color_filter = ColorFilter(color, blend_mode)

    def clear_color_filter(self) -> None:
        """Remove color filter."""
        self.color_filter = None

    def stop_all(self) -> None:
        """Stop all active effects."""
        self.shake.stop()
        self.flash.stop()
        self.fade.stop()


# =============================================================================
# Preset Screen Effects
# =============================================================================

def create_hit_flash() -> ScreenFlash:
    """Create a white hit flash effect."""
    flash = ScreenFlash(
        color=(255, 255, 255, 200),
        duration=0.1,
        intensity=1.0,
        blend_mode=BlendMode.ADD
    )
    return flash


def create_damage_flash() -> ScreenFlash:
    """Create a red damage flash effect."""
    flash = ScreenFlash(
        color=(255, 50, 50, 150),
        duration=0.15,
        intensity=0.8,
        blend_mode=BlendMode.NORMAL
    )
    return flash


def create_heal_flash() -> ScreenFlash:
    """Create a green heal flash effect."""
    flash = ScreenFlash(
        color=(50, 255, 100, 150),
        duration=0.2,
        intensity=0.6,
        blend_mode=BlendMode.ADD
    )
    return flash


def create_impact_shake() -> ScreenShake:
    """Create a heavy impact shake."""
    shake = ScreenShake(
        intensity=8.0,
        duration=0.25,
        frequency=40.0,
        decay=True
    )
    return shake


def create_rumble_shake() -> ScreenShake:
    """Create a continuous rumble shake."""
    shake = ScreenShake(
        intensity=3.0,
        duration=1.0,
        frequency=20.0,
        decay=False
    )
    return shake

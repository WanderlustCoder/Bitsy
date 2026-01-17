"""
Displacement Effects - Spatial distortion for pixel art.

Provides wave, ripple, twirl, bulge, and noise-based
displacement effects.
"""

import math
import random
from typing import Tuple, Optional, List
from dataclasses import dataclass
from abc import ABC, abstractmethod

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Canvas
from core.color import Color


class Displacement(ABC):
    """Base class for displacement effects."""

    @abstractmethod
    def get_displacement(self, x: int, y: int, width: int, height: int) -> Tuple[float, float]:
        """Calculate displacement for a pixel.

        Args:
            x, y: Pixel coordinates
            width, height: Canvas dimensions

        Returns:
            (dx, dy) displacement offset
        """
        pass

    def apply(self, canvas: Canvas) -> Canvas:
        """Apply displacement to canvas.

        Args:
            canvas: Source canvas

        Returns:
            Displaced canvas
        """
        result = Canvas(canvas.width, canvas.height)

        for y in range(canvas.height):
            for x in range(canvas.width):
                # Get displacement
                dx, dy = self.get_displacement(x, y, canvas.width, canvas.height)

                # Sample from displaced position
                sx = x + dx
                sy = y + dy

                # Bilinear interpolation for smooth results
                color = self._sample_bilinear(canvas, sx, sy)
                if color:
                    result.pixels[y][x] = list(color)

        return result

    def _sample_bilinear(self, canvas: Canvas, x: float, y: float) -> Optional[Color]:
        """Sample canvas with bilinear interpolation."""
        x0 = int(x)
        y0 = int(y)
        x1 = x0 + 1
        y1 = y0 + 1

        # Clamp to bounds
        if x0 < 0 or x1 >= canvas.width or y0 < 0 or y1 >= canvas.height:
            # Use nearest if out of bounds
            nx = max(0, min(canvas.width - 1, int(x + 0.5)))
            ny = max(0, min(canvas.height - 1, int(y + 0.5)))
            pixel = canvas.pixels[ny][nx]
            return tuple(pixel) if pixel[3] > 0 else None

        # Get fractional parts
        fx = x - x0
        fy = y - y0

        # Get corner colors
        c00 = canvas.pixels[y0][x0]
        c10 = canvas.pixels[y0][x1]
        c01 = canvas.pixels[y1][x0]
        c11 = canvas.pixels[y1][x1]

        # Check if any corners are transparent
        if c00[3] == 0 or c10[3] == 0 or c01[3] == 0 or c11[3] == 0:
            # Use nearest neighbor for edges
            nx = int(x + 0.5)
            ny = int(y + 0.5)
            if 0 <= nx < canvas.width and 0 <= ny < canvas.height:
                pixel = canvas.pixels[ny][nx]
                return tuple(pixel) if pixel[3] > 0 else None
            return None

        # Bilinear interpolation
        def lerp(a, b, t):
            return int(a + (b - a) * t)

        r = lerp(lerp(c00[0], c10[0], fx), lerp(c01[0], c11[0], fx), fy)
        g = lerp(lerp(c00[1], c10[1], fx), lerp(c01[1], c11[1], fx), fy)
        b = lerp(lerp(c00[2], c10[2], fx), lerp(c01[2], c11[2], fx), fy)
        a = lerp(lerp(c00[3], c10[3], fx), lerp(c01[3], c11[3], fx), fy)

        return (r, g, b, a)


class WaveDisplacement(Displacement):
    """Sinusoidal wave distortion."""

    def __init__(
        self,
        amplitude: float = 3.0,
        frequency: float = 0.2,
        direction: str = "horizontal",
        phase: float = 0.0
    ):
        """Initialize wave displacement.

        Args:
            amplitude: Wave height in pixels
            frequency: Waves per pixel
            direction: "horizontal", "vertical", or "both"
            phase: Wave phase offset (for animation)
        """
        self.amplitude = amplitude
        self.frequency = frequency
        self.direction = direction
        self.phase = phase

    def get_displacement(self, x: int, y: int, width: int, height: int) -> Tuple[float, float]:
        dx = 0.0
        dy = 0.0

        if self.direction in ("horizontal", "both"):
            dx = self.amplitude * math.sin(y * self.frequency * 2 * math.pi + self.phase)

        if self.direction in ("vertical", "both"):
            dy = self.amplitude * math.sin(x * self.frequency * 2 * math.pi + self.phase)

        return (dx, dy)


class RippleDisplacement(Displacement):
    """Circular ripple effect from a point."""

    def __init__(
        self,
        center: Optional[Tuple[int, int]] = None,
        amplitude: float = 4.0,
        wavelength: float = 8.0,
        decay: float = 0.5,
        phase: float = 0.0
    ):
        """Initialize ripple displacement.

        Args:
            center: Ripple center (None = canvas center)
            amplitude: Ripple height in pixels
            wavelength: Distance between ripples
            decay: Amplitude falloff with distance
            phase: Ripple phase offset
        """
        self.center = center
        self.amplitude = amplitude
        self.wavelength = wavelength
        self.decay = decay
        self.phase = phase

    def get_displacement(self, x: int, y: int, width: int, height: int) -> Tuple[float, float]:
        # Use center or default to canvas center
        cx = self.center[0] if self.center else width // 2
        cy = self.center[1] if self.center else height // 2

        # Distance from center
        dx = x - cx
        dy = y - cy
        dist = math.sqrt(dx * dx + dy * dy)

        if dist < 0.1:
            return (0.0, 0.0)

        # Calculate ripple
        ripple = math.sin(dist / self.wavelength * 2 * math.pi + self.phase)

        # Apply decay
        strength = self.amplitude * math.exp(-dist * self.decay / (width + height))

        # Displacement along radial direction
        disp = ripple * strength
        disp_x = disp * dx / dist
        disp_y = disp * dy / dist

        return (disp_x, disp_y)


class TwirlDisplacement(Displacement):
    """Twirl/spiral distortion."""

    def __init__(
        self,
        center: Optional[Tuple[int, int]] = None,
        angle: float = 45.0,
        radius: float = 0.8
    ):
        """Initialize twirl displacement.

        Args:
            center: Twirl center (None = canvas center)
            angle: Maximum rotation in degrees
            radius: Effect radius as fraction of canvas (0-1)
        """
        self.center = center
        self.angle = math.radians(angle)
        self.radius = radius

    def get_displacement(self, x: int, y: int, width: int, height: int) -> Tuple[float, float]:
        cx = self.center[0] if self.center else width // 2
        cy = self.center[1] if self.center else height // 2

        max_radius = min(width, height) * self.radius / 2

        dx = x - cx
        dy = y - cy
        dist = math.sqrt(dx * dx + dy * dy)

        if dist > max_radius or dist < 0.1:
            return (0.0, 0.0)

        # Calculate rotation based on distance
        factor = 1.0 - (dist / max_radius)
        rotation = self.angle * factor * factor

        # Rotate point
        cos_r = math.cos(rotation)
        sin_r = math.sin(rotation)

        new_dx = dx * cos_r - dy * sin_r
        new_dy = dx * sin_r + dy * cos_r

        return (new_dx - dx, new_dy - dy)


class BulgeDisplacement(Displacement):
    """Bulge/pinch effect."""

    def __init__(
        self,
        center: Optional[Tuple[int, int]] = None,
        strength: float = 0.5,
        radius: float = 0.6
    ):
        """Initialize bulge displacement.

        Args:
            center: Effect center (None = canvas center)
            strength: Effect strength (positive = bulge, negative = pinch)
            radius: Effect radius as fraction of canvas
        """
        self.center = center
        self.strength = strength
        self.radius = radius

    def get_displacement(self, x: int, y: int, width: int, height: int) -> Tuple[float, float]:
        cx = self.center[0] if self.center else width // 2
        cy = self.center[1] if self.center else height // 2

        max_radius = min(width, height) * self.radius / 2

        dx = x - cx
        dy = y - cy
        dist = math.sqrt(dx * dx + dy * dy)

        if dist > max_radius or dist < 0.1:
            return (0.0, 0.0)

        # Calculate bulge factor
        normalized_dist = dist / max_radius
        factor = math.pow(normalized_dist, 2)

        # Apply bulge/pinch
        if self.strength > 0:
            # Bulge: pull toward center
            displacement = self.strength * (1 - factor)
        else:
            # Pinch: push away from center
            displacement = self.strength * factor

        disp_x = dx * displacement
        disp_y = dy * displacement

        return (-disp_x, -disp_y)


class NoiseDisplacement(Displacement):
    """Random noise displacement."""

    def __init__(
        self,
        strength: float = 2.0,
        seed: int = 42,
        smoothness: float = 0.5
    ):
        """Initialize noise displacement.

        Args:
            strength: Maximum displacement in pixels
            seed: Random seed
            smoothness: Noise smoothness (0 = random, 1 = perlin-like)
        """
        self.strength = strength
        self.seed = seed
        self.smoothness = max(0, min(1, smoothness))
        self._rng = random.Random(seed)
        self._noise_cache = {}

    def get_displacement(self, x: int, y: int, width: int, height: int) -> Tuple[float, float]:
        if self.smoothness < 0.1:
            # Pure random noise
            dx = (self._rng.random() * 2 - 1) * self.strength
            dy = (self._rng.random() * 2 - 1) * self.strength
        else:
            # Smoothed noise using value noise interpolation
            dx = self._smooth_noise(x, y, 0) * self.strength
            dy = self._smooth_noise(x, y, 1) * self.strength

        return (dx, dy)

    def _smooth_noise(self, x: int, y: int, channel: int) -> float:
        """Get smooth noise value using interpolation."""
        scale = 4 + int(self.smoothness * 12)  # 4-16 pixel scale

        # Get grid coordinates
        gx = x // scale
        gy = y // scale

        # Get fractional position
        fx = (x % scale) / scale
        fy = (y % scale) / scale

        # Get corner noise values
        n00 = self._get_noise(gx, gy, channel)
        n10 = self._get_noise(gx + 1, gy, channel)
        n01 = self._get_noise(gx, gy + 1, channel)
        n11 = self._get_noise(gx + 1, gy + 1, channel)

        # Smoothstep interpolation
        fx = fx * fx * (3 - 2 * fx)
        fy = fy * fy * (3 - 2 * fy)

        # Bilinear interpolation
        n0 = n00 + (n10 - n00) * fx
        n1 = n01 + (n11 - n01) * fx
        return n0 + (n1 - n0) * fy

    def _get_noise(self, gx: int, gy: int, channel: int) -> float:
        """Get cached noise value for grid cell."""
        key = (gx, gy, channel)
        if key not in self._noise_cache:
            # Generate deterministic noise
            self._rng.seed(self.seed + gx * 1000 + gy * 1000000 + channel * 1000000000)
            self._noise_cache[key] = self._rng.random() * 2 - 1
        return self._noise_cache[key]


class BarrelDisplacement(Displacement):
    """Barrel/pincushion lens distortion."""

    def __init__(
        self,
        strength: float = 0.3,
        center: Optional[Tuple[int, int]] = None
    ):
        """Initialize barrel distortion.

        Args:
            strength: Distortion strength (positive = barrel, negative = pincushion)
            center: Distortion center
        """
        self.strength = strength
        self.center = center

    def get_displacement(self, x: int, y: int, width: int, height: int) -> Tuple[float, float]:
        cx = self.center[0] if self.center else width // 2
        cy = self.center[1] if self.center else height // 2

        # Normalize coordinates to -1 to 1
        nx = (x - cx) / (width / 2)
        ny = (y - cy) / (height / 2)

        r2 = nx * nx + ny * ny

        # Apply barrel/pincushion distortion
        factor = 1 + self.strength * r2

        new_nx = nx * factor
        new_ny = ny * factor

        # Convert back to pixel coordinates
        new_x = new_nx * (width / 2) + cx
        new_y = new_ny * (height / 2) + cy

        return (new_x - x, new_y - y)


class ShearDisplacement(Displacement):
    """Shear/skew distortion."""

    def __init__(
        self,
        horizontal: float = 0.0,
        vertical: float = 0.0
    ):
        """Initialize shear displacement.

        Args:
            horizontal: Horizontal shear factor
            vertical: Vertical shear factor
        """
        self.horizontal = horizontal
        self.vertical = vertical

    def get_displacement(self, x: int, y: int, width: int, height: int) -> Tuple[float, float]:
        # Normalize to center
        cx = width / 2
        cy = height / 2
        nx = x - cx
        ny = y - cy

        # Apply shear
        dx = self.horizontal * ny
        dy = self.vertical * nx

        return (dx, dy)


class CompositeDisplacement(Displacement):
    """Combine multiple displacement effects."""

    def __init__(self, *effects: Displacement):
        """Initialize composite displacement.

        Args:
            *effects: Displacement effects to combine
        """
        self.effects = list(effects)

    def add(self, effect: Displacement) -> 'CompositeDisplacement':
        """Add a displacement effect.

        Args:
            effect: Effect to add

        Returns:
            Self for chaining
        """
        self.effects.append(effect)
        return self

    def get_displacement(self, x: int, y: int, width: int, height: int) -> Tuple[float, float]:
        total_dx = 0.0
        total_dy = 0.0

        for effect in self.effects:
            dx, dy = effect.get_displacement(x, y, width, height)
            total_dx += dx
            total_dy += dy

        return (total_dx, total_dy)


# =============================================================================
# Convenience Functions
# =============================================================================

def apply_wave(
    canvas: Canvas,
    amplitude: float = 3.0,
    frequency: float = 0.2,
    direction: str = "horizontal",
    phase: float = 0.0
) -> Canvas:
    """Apply wave displacement.

    Args:
        canvas: Source canvas
        amplitude: Wave height
        frequency: Wave frequency
        direction: Wave direction
        phase: Phase offset

    Returns:
        Displaced canvas
    """
    return WaveDisplacement(amplitude, frequency, direction, phase).apply(canvas)


def apply_ripple(
    canvas: Canvas,
    amplitude: float = 4.0,
    wavelength: float = 8.0,
    phase: float = 0.0
) -> Canvas:
    """Apply ripple displacement.

    Args:
        canvas: Source canvas
        amplitude: Ripple amplitude
        wavelength: Ripple wavelength
        phase: Phase offset

    Returns:
        Displaced canvas
    """
    return RippleDisplacement(None, amplitude, wavelength, 0.5, phase).apply(canvas)


def apply_twirl(
    canvas: Canvas,
    angle: float = 45.0,
    radius: float = 0.8
) -> Canvas:
    """Apply twirl displacement.

    Args:
        canvas: Source canvas
        angle: Twirl angle
        radius: Effect radius

    Returns:
        Displaced canvas
    """
    return TwirlDisplacement(None, angle, radius).apply(canvas)


def apply_bulge(
    canvas: Canvas,
    strength: float = 0.5,
    radius: float = 0.6
) -> Canvas:
    """Apply bulge/pinch displacement.

    Args:
        canvas: Source canvas
        strength: Bulge strength (negative = pinch)
        radius: Effect radius

    Returns:
        Displaced canvas
    """
    return BulgeDisplacement(None, strength, radius).apply(canvas)


def apply_noise(
    canvas: Canvas,
    strength: float = 2.0,
    seed: int = 42
) -> Canvas:
    """Apply noise displacement.

    Args:
        canvas: Source canvas
        strength: Noise strength
        seed: Random seed

    Returns:
        Displaced canvas
    """
    return NoiseDisplacement(strength, seed, 0.5).apply(canvas)


def apply_barrel(
    canvas: Canvas,
    strength: float = 0.3
) -> Canvas:
    """Apply barrel distortion.

    Args:
        canvas: Source canvas
        strength: Distortion strength

    Returns:
        Displaced canvas
    """
    return BarrelDisplacement(strength).apply(canvas)

"""
Glow and Bloom Effects - Light bleeding for pixel art.

Provides glow effects for bright areas and sprite edges.
"""

import math
from typing import Tuple, Optional, List
from dataclasses import dataclass
from enum import Enum

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Canvas
from core.color import Color
from effects.screen import BlendMode


def _get_luminance(color: Color) -> int:
    """Calculate perceived luminance of a color."""
    return int(0.299 * color[0] + 0.587 * color[1] + 0.114 * color[2])


def _blend_add(base: Color, overlay: Color, intensity: float) -> Color:
    """Additive blend with intensity."""
    return (
        min(255, base[0] + int(overlay[0] * intensity)),
        min(255, base[1] + int(overlay[1] * intensity)),
        min(255, base[2] + int(overlay[2] * intensity)),
        base[3]
    )


def _blend_screen(base: Color, overlay: Color, intensity: float) -> Color:
    """Screen blend with intensity."""
    r = 255 - int((255 - base[0]) * (255 - overlay[0] * intensity) / 255)
    g = 255 - int((255 - base[1]) * (255 - overlay[1] * intensity) / 255)
    b = 255 - int((255 - base[2]) * (255 - overlay[2] * intensity) / 255)
    return (r, g, b, base[3])


class GlowEffect:
    """Add glow around bright pixels or specific colors."""

    def __init__(
        self,
        threshold: int = 200,
        radius: int = 3,
        intensity: float = 0.5,
        color: Optional[Color] = None,
        blend_mode: BlendMode = BlendMode.ADD
    ):
        """Initialize glow effect.

        Args:
            threshold: Brightness threshold for glow (0-255)
            radius: Glow spread in pixels
            intensity: Glow brightness (0-1)
            color: Force specific glow color (None = use source color)
            blend_mode: How glow blends with image
        """
        self.threshold = threshold
        self.radius = radius
        self.intensity = intensity
        self.color = color
        self.blend_mode = blend_mode

    def apply(self, canvas: Canvas) -> Canvas:
        """Apply glow effect to canvas.

        Args:
            canvas: Source canvas

        Returns:
            Canvas with glow applied
        """
        result = canvas.copy()

        # Find bright pixels
        bright_pixels = []
        for y in range(canvas.height):
            for x in range(canvas.width):
                pixel = canvas.pixels[y][x]
                if pixel[3] > 0:
                    lum = _get_luminance(pixel)
                    if lum >= self.threshold:
                        bright_pixels.append((x, y, pixel))

        # Create glow map
        glow_map = [[None for _ in range(canvas.width)] for _ in range(canvas.height)]

        for bx, by, pixel in bright_pixels:
            glow_color = self.color if self.color else pixel

            # Spread glow around bright pixel
            for dy in range(-self.radius, self.radius + 1):
                for dx in range(-self.radius, self.radius + 1):
                    nx, ny = bx + dx, by + dy

                    if not (0 <= nx < canvas.width and 0 <= ny < canvas.height):
                        continue

                    # Calculate distance-based falloff
                    dist = math.sqrt(dx * dx + dy * dy)
                    if dist > self.radius:
                        continue

                    falloff = 1.0 - (dist / self.radius)
                    glow_intensity = falloff * self.intensity

                    # Accumulate glow
                    if glow_map[ny][nx] is None:
                        glow_map[ny][nx] = [0.0, 0.0, 0.0, 0.0]

                    glow_map[ny][nx][0] += glow_color[0] * glow_intensity
                    glow_map[ny][nx][1] += glow_color[1] * glow_intensity
                    glow_map[ny][nx][2] += glow_color[2] * glow_intensity
                    glow_map[ny][nx][3] = max(glow_map[ny][nx][3], glow_intensity)

        # Apply glow to result
        for y in range(canvas.height):
            for x in range(canvas.width):
                glow = glow_map[y][x]
                if glow is None or glow[3] == 0:
                    continue

                base = result.pixels[y][x]

                # Normalize accumulated glow
                glow_color = (
                    min(255, int(glow[0])),
                    min(255, int(glow[1])),
                    min(255, int(glow[2])),
                    255
                )

                if base[3] > 0:
                    # Blend glow with existing pixel
                    if self.blend_mode == BlendMode.ADD:
                        blended = _blend_add(base, glow_color, glow[3])
                    else:
                        blended = _blend_screen(base, glow_color, glow[3])
                    result.pixels[y][x] = list(blended)
                else:
                    # Draw glow on transparent area
                    alpha = int(glow[3] * 255 * 0.5)  # Softer on transparent
                    if alpha > 10:
                        result.pixels[y][x] = [
                            glow_color[0], glow_color[1], glow_color[2], alpha
                        ]

        return result


class BloomEffect:
    """Bloom effect - bright areas bleed light."""

    def __init__(
        self,
        threshold: int = 180,
        blur_radius: int = 4,
        intensity: float = 0.4,
        blur_passes: int = 2,
        blend_mode: BlendMode = BlendMode.ADD
    ):
        """Initialize bloom effect.

        Args:
            threshold: Brightness threshold (0-255)
            blur_radius: Blur radius for bloom
            intensity: Bloom brightness (0-1)
            blur_passes: Number of blur iterations
            blend_mode: How bloom blends
        """
        self.threshold = threshold
        self.blur_radius = blur_radius
        self.intensity = intensity
        self.blur_passes = blur_passes
        self.blend_mode = blend_mode

    def apply(self, canvas: Canvas) -> Canvas:
        """Apply bloom effect.

        Args:
            canvas: Source canvas

        Returns:
            Canvas with bloom applied
        """
        # Extract bright areas
        bright = Canvas(canvas.width, canvas.height)

        for y in range(canvas.height):
            for x in range(canvas.width):
                pixel = canvas.pixels[y][x]
                if pixel[3] > 0:
                    lum = _get_luminance(pixel)
                    if lum >= self.threshold:
                        # Scale brightness by how much it exceeds threshold
                        factor = (lum - self.threshold) / (255 - self.threshold)
                        bright.pixels[y][x] = [
                            int(pixel[0] * factor),
                            int(pixel[1] * factor),
                            int(pixel[2] * factor),
                            pixel[3]
                        ]

        # Blur the bright areas
        blurred = bright
        for _ in range(self.blur_passes):
            blurred = self._box_blur(blurred, self.blur_radius)

        # Composite bloom onto original
        result = canvas.copy()

        for y in range(canvas.height):
            for x in range(canvas.width):
                bloom_pixel = blurred.pixels[y][x]
                if bloom_pixel[3] == 0:
                    continue

                base = result.pixels[y][x]

                if self.blend_mode == BlendMode.ADD:
                    blended = _blend_add(base, bloom_pixel, self.intensity)
                else:
                    blended = _blend_screen(bloom_pixel, bloom_pixel, self.intensity)

                if base[3] > 0:
                    result.pixels[y][x] = list(blended)
                else:
                    # Soft bloom on transparent
                    alpha = int(bloom_pixel[3] * self.intensity * 0.3)
                    if alpha > 5:
                        result.pixels[y][x] = [
                            bloom_pixel[0], bloom_pixel[1], bloom_pixel[2], alpha
                        ]

        return result

    def _box_blur(self, canvas: Canvas, radius: int) -> Canvas:
        """Apply fast box blur."""
        result = Canvas(canvas.width, canvas.height)
        size = radius * 2 + 1

        for y in range(canvas.height):
            for x in range(canvas.width):
                r, g, b, a = 0, 0, 0, 0
                count = 0

                for dy in range(-radius, radius + 1):
                    for dx in range(-radius, radius + 1):
                        sx = max(0, min(canvas.width - 1, x + dx))
                        sy = max(0, min(canvas.height - 1, y + dy))
                        pixel = canvas.pixels[sy][sx]

                        if pixel[3] > 0:
                            r += pixel[0]
                            g += pixel[1]
                            b += pixel[2]
                            a += pixel[3]
                            count += 1

                if count > 0:
                    result.pixels[y][x] = [
                        r // count, g // count, b // count, a // count
                    ]

        return result


class InnerGlow:
    """Glow effect from sprite edges inward."""

    def __init__(
        self,
        color: Color = (255, 255, 200, 255),
        radius: int = 2,
        intensity: float = 0.5
    ):
        """Initialize inner glow.

        Args:
            color: Glow color
            radius: Glow depth in pixels
            intensity: Glow brightness
        """
        self.color = color
        self.radius = radius
        self.intensity = intensity

    def apply(self, canvas: Canvas) -> Canvas:
        """Apply inner glow.

        Args:
            canvas: Source canvas

        Returns:
            Canvas with inner glow
        """
        result = canvas.copy()

        # Find edge pixels
        edge_pixels = set()
        for y in range(canvas.height):
            for x in range(canvas.width):
                if canvas.pixels[y][x][3] > 0:
                    if self._is_edge(canvas, x, y):
                        edge_pixels.add((x, y))

        # Calculate distance from edge for each interior pixel
        distance_map = [[float('inf')] * canvas.width for _ in range(canvas.height)]

        for ex, ey in edge_pixels:
            distance_map[ey][ex] = 0

        # Propagate distances inward (simple BFS-like approach)
        for dist in range(self.radius):
            for y in range(canvas.height):
                for x in range(canvas.width):
                    if distance_map[y][x] == dist:
                        for dy in [-1, 0, 1]:
                            for dx in [-1, 0, 1]:
                                nx, ny = x + dx, y + dy
                                if 0 <= nx < canvas.width and 0 <= ny < canvas.height:
                                    if canvas.pixels[ny][nx][3] > 0:
                                        if distance_map[ny][nx] > dist + 1:
                                            distance_map[ny][nx] = dist + 1

        # Apply glow based on distance
        for y in range(canvas.height):
            for x in range(canvas.width):
                dist = distance_map[y][x]
                if dist <= self.radius and canvas.pixels[y][x][3] > 0:
                    falloff = 1.0 - (dist / self.radius)
                    glow_strength = falloff * self.intensity

                    base = canvas.pixels[y][x]
                    blended = _blend_add(base, self.color, glow_strength)
                    result.pixels[y][x] = list(blended)

        return result

    def _is_edge(self, canvas: Canvas, x: int, y: int) -> bool:
        """Check if pixel is on the sprite edge."""
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if not (0 <= nx < canvas.width and 0 <= ny < canvas.height):
                    return True
                if canvas.pixels[ny][nx][3] == 0:
                    return True
        return False


class OuterGlow:
    """Glow effect outward from sprite edges."""

    def __init__(
        self,
        color: Color = (255, 200, 100, 255),
        radius: int = 3,
        intensity: float = 0.6
    ):
        """Initialize outer glow.

        Args:
            color: Glow color
            radius: Glow spread in pixels
            intensity: Glow brightness
        """
        self.color = color
        self.radius = radius
        self.intensity = intensity

    def apply(self, canvas: Canvas) -> Canvas:
        """Apply outer glow.

        Args:
            canvas: Source canvas

        Returns:
            Canvas with outer glow
        """
        result = canvas.copy()

        # Find edge pixels
        edge_pixels = []
        for y in range(canvas.height):
            for x in range(canvas.width):
                if canvas.pixels[y][x][3] > 0:
                    if self._is_edge(canvas, x, y):
                        edge_pixels.append((x, y))

        # Calculate glow for transparent pixels
        glow_map = [[0.0] * canvas.width for _ in range(canvas.height)]

        for ex, ey in edge_pixels:
            for dy in range(-self.radius, self.radius + 1):
                for dx in range(-self.radius, self.radius + 1):
                    nx, ny = ex + dx, ey + dy

                    if not (0 <= nx < canvas.width and 0 <= ny < canvas.height):
                        continue

                    # Only glow on transparent pixels
                    if canvas.pixels[ny][nx][3] > 0:
                        continue

                    dist = math.sqrt(dx * dx + dy * dy)
                    if dist > self.radius:
                        continue

                    falloff = 1.0 - (dist / self.radius)
                    glow_map[ny][nx] = max(glow_map[ny][nx], falloff * self.intensity)

        # Apply glow
        for y in range(canvas.height):
            for x in range(canvas.width):
                glow_strength = glow_map[y][x]
                if glow_strength > 0.01:
                    alpha = int(glow_strength * 255)
                    result.pixels[y][x] = [
                        self.color[0], self.color[1], self.color[2], alpha
                    ]

        return result

    def _is_edge(self, canvas: Canvas, x: int, y: int) -> bool:
        """Check if pixel is on the sprite edge."""
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if not (0 <= nx < canvas.width and 0 <= ny < canvas.height):
                    return True
                if canvas.pixels[ny][nx][3] == 0:
                    return True
        return False


class ColorGlow:
    """Glow effect targeting specific colors."""

    def __init__(
        self,
        target_color: Color,
        tolerance: int = 30,
        radius: int = 3,
        intensity: float = 0.5,
        glow_color: Optional[Color] = None
    ):
        """Initialize color-targeted glow.

        Args:
            target_color: Color to make glow
            tolerance: Color matching tolerance
            radius: Glow spread
            intensity: Glow brightness
            glow_color: Glow color (None = use target color)
        """
        self.target_color = target_color
        self.tolerance = tolerance
        self.radius = radius
        self.intensity = intensity
        self.glow_color = glow_color or target_color

    def apply(self, canvas: Canvas) -> Canvas:
        """Apply color-targeted glow.

        Args:
            canvas: Source canvas

        Returns:
            Canvas with glow applied
        """
        result = canvas.copy()

        # Find matching pixels
        target_pixels = []
        for y in range(canvas.height):
            for x in range(canvas.width):
                pixel = canvas.pixels[y][x]
                if pixel[3] > 0 and self._color_matches(pixel):
                    target_pixels.append((x, y))

        # Create glow
        glow_map = [[0.0] * canvas.width for _ in range(canvas.height)]

        for tx, ty in target_pixels:
            for dy in range(-self.radius, self.radius + 1):
                for dx in range(-self.radius, self.radius + 1):
                    nx, ny = tx + dx, ty + dy

                    if not (0 <= nx < canvas.width and 0 <= ny < canvas.height):
                        continue

                    dist = math.sqrt(dx * dx + dy * dy)
                    if dist > self.radius:
                        continue

                    falloff = 1.0 - (dist / self.radius)
                    glow_map[ny][nx] = max(glow_map[ny][nx], falloff * self.intensity)

        # Apply glow
        for y in range(canvas.height):
            for x in range(canvas.width):
                glow_strength = glow_map[y][x]
                if glow_strength > 0.01:
                    base = result.pixels[y][x]
                    if base[3] > 0:
                        blended = _blend_add(base, self.glow_color, glow_strength)
                        result.pixels[y][x] = list(blended)
                    else:
                        alpha = int(glow_strength * 200)
                        if alpha > 5:
                            result.pixels[y][x] = [
                                self.glow_color[0],
                                self.glow_color[1],
                                self.glow_color[2],
                                alpha
                            ]

        return result

    def _color_matches(self, color: Color) -> bool:
        """Check if color matches target within tolerance."""
        return (
            abs(color[0] - self.target_color[0]) <= self.tolerance and
            abs(color[1] - self.target_color[1]) <= self.tolerance and
            abs(color[2] - self.target_color[2]) <= self.tolerance
        )


# =============================================================================
# Convenience Functions
# =============================================================================

def add_glow(
    canvas: Canvas,
    threshold: int = 200,
    radius: int = 3,
    intensity: float = 0.5
) -> Canvas:
    """Add glow to bright areas.

    Args:
        canvas: Source canvas
        threshold: Brightness threshold
        radius: Glow radius
        intensity: Glow intensity

    Returns:
        Canvas with glow
    """
    return GlowEffect(threshold, radius, intensity).apply(canvas)


def add_bloom(
    canvas: Canvas,
    threshold: int = 180,
    blur_radius: int = 4,
    intensity: float = 0.4
) -> Canvas:
    """Add bloom effect.

    Args:
        canvas: Source canvas
        threshold: Brightness threshold
        blur_radius: Blur radius
        intensity: Bloom intensity

    Returns:
        Canvas with bloom
    """
    return BloomEffect(threshold, blur_radius, intensity).apply(canvas)


def add_outer_glow(
    canvas: Canvas,
    color: Color = (255, 200, 100, 255),
    radius: int = 3,
    intensity: float = 0.6
) -> Canvas:
    """Add outer glow around sprite.

    Args:
        canvas: Source canvas
        color: Glow color
        radius: Glow radius
        intensity: Glow intensity

    Returns:
        Canvas with outer glow
    """
    return OuterGlow(color, radius, intensity).apply(canvas)


def add_inner_glow(
    canvas: Canvas,
    color: Color = (255, 255, 200, 255),
    radius: int = 2,
    intensity: float = 0.5
) -> Canvas:
    """Add inner glow to sprite edges.

    Args:
        canvas: Source canvas
        color: Glow color
        radius: Glow depth
        intensity: Glow intensity

    Returns:
        Canvas with inner glow
    """
    return InnerGlow(color, radius, intensity).apply(canvas)

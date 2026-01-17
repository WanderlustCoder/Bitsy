"""
Post-Processing Effects - Shader-like pixel manipulation.

Provides convolution-based effects (blur, sharpen, emboss) and
pixel-level effects (pixelate, posterize, dither).
"""

import math
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Canvas
from core.color import Color


class Effect(ABC):
    """Base class for post-processing effects."""

    @abstractmethod
    def process(self, canvas: Canvas) -> Canvas:
        """Apply the effect to a canvas.

        Args:
            canvas: Source canvas (not modified)

        Returns:
            New canvas with effect applied
        """
        pass


class ConvolutionKernel:
    """A convolution kernel for image processing."""

    def __init__(self, matrix: List[List[float]], normalize: bool = True):
        """Initialize kernel.

        Args:
            matrix: 2D kernel matrix (must be square with odd dimensions)
            normalize: Whether to normalize kernel sum to 1
        """
        self.matrix = matrix
        self.size = len(matrix)
        self.radius = self.size // 2

        if normalize:
            total = sum(sum(row) for row in matrix)
            if total != 0:
                self.matrix = [[v / total for v in row] for row in matrix]

    def apply(self, canvas: Canvas) -> Canvas:
        """Apply kernel convolution to canvas.

        Args:
            canvas: Source canvas

        Returns:
            Convolved canvas
        """
        result = Canvas(canvas.width, canvas.height)

        for y in range(canvas.height):
            for x in range(canvas.width):
                pixel = canvas.pixels[y][x]

                # Skip fully transparent pixels
                if pixel[3] == 0:
                    continue

                r, g, b = 0.0, 0.0, 0.0

                for ky in range(self.size):
                    for kx in range(self.size):
                        # Sample position
                        sx = x + kx - self.radius
                        sy = y + ky - self.radius

                        # Clamp to canvas bounds
                        sx = max(0, min(canvas.width - 1, sx))
                        sy = max(0, min(canvas.height - 1, sy))

                        sample = canvas.pixels[sy][sx]
                        weight = self.matrix[ky][kx]

                        if sample[3] > 0:  # Only sample opaque pixels
                            r += sample[0] * weight
                            g += sample[1] * weight
                            b += sample[2] * weight

                result.pixels[y][x] = [
                    max(0, min(255, int(r))),
                    max(0, min(255, int(g))),
                    max(0, min(255, int(b))),
                    pixel[3]
                ]

        return result


# =============================================================================
# Convolution-based Effects
# =============================================================================

class GaussianBlur(Effect):
    """Gaussian blur with configurable radius."""

    def __init__(self, radius: int = 2, sigma: Optional[float] = None):
        """Initialize blur.

        Args:
            radius: Blur radius in pixels
            sigma: Gaussian sigma (default: radius / 2)
        """
        self.radius = radius
        self.sigma = sigma if sigma is not None else radius / 2

    def process(self, canvas: Canvas) -> Canvas:
        """Apply Gaussian blur."""
        kernel = self._create_kernel()
        return kernel.apply(canvas)

    def _create_kernel(self) -> ConvolutionKernel:
        """Create Gaussian kernel matrix."""
        size = self.radius * 2 + 1
        matrix = []

        for y in range(size):
            row = []
            for x in range(size):
                dx = x - self.radius
                dy = y - self.radius
                value = math.exp(-(dx*dx + dy*dy) / (2 * self.sigma * self.sigma))
                row.append(value)
            matrix.append(row)

        return ConvolutionKernel(matrix, normalize=True)


class BoxBlur(Effect):
    """Fast box blur (average filter)."""

    def __init__(self, radius: int = 2):
        """Initialize blur.

        Args:
            radius: Blur radius in pixels
        """
        self.radius = radius

    def process(self, canvas: Canvas) -> Canvas:
        """Apply box blur."""
        size = self.radius * 2 + 1
        value = 1.0 / (size * size)
        matrix = [[value] * size for _ in range(size)]
        kernel = ConvolutionKernel(matrix, normalize=False)
        return kernel.apply(canvas)


class Sharpen(Effect):
    """Sharpen image details."""

    def __init__(self, amount: float = 1.0):
        """Initialize sharpen.

        Args:
            amount: Sharpening strength (1.0 = standard)
        """
        self.amount = amount

    def process(self, canvas: Canvas) -> Canvas:
        """Apply sharpening."""
        # Sharpen kernel: emphasize center, subtract neighbors
        center = 1 + 4 * self.amount
        edge = -self.amount

        matrix = [
            [0, edge, 0],
            [edge, center, edge],
            [0, edge, 0]
        ]

        kernel = ConvolutionKernel(matrix, normalize=False)
        return kernel.apply(canvas)


class Emboss(Effect):
    """Emboss/relief effect."""

    DIRECTIONS = {
        "top-left": [[-2, -1, 0], [-1, 1, 1], [0, 1, 2]],
        "top": [[-1, -2, -1], [0, 1, 0], [1, 2, 1]],
        "top-right": [[0, -1, -2], [1, 1, -1], [2, 1, 0]],
        "left": [[-1, 0, 1], [-2, 1, 2], [-1, 0, 1]],
        "right": [[1, 0, -1], [2, 1, -2], [1, 0, -1]],
        "bottom-left": [[0, 1, 2], [-1, 1, 1], [-2, -1, 0]],
        "bottom": [[1, 2, 1], [0, 1, 0], [-1, -2, -1]],
        "bottom-right": [[2, 1, 0], [1, 1, -1], [0, -1, -2]],
    }

    def __init__(self, direction: str = "top-left", strength: float = 1.0):
        """Initialize emboss.

        Args:
            direction: Light direction
            strength: Effect strength
        """
        self.direction = direction
        self.strength = strength

    def process(self, canvas: Canvas) -> Canvas:
        """Apply emboss effect."""
        matrix = self.DIRECTIONS.get(self.direction, self.DIRECTIONS["top-left"])

        # Apply strength
        scaled = [[v * self.strength for v in row] for row in matrix]

        kernel = ConvolutionKernel(scaled, normalize=False)
        embossed = kernel.apply(canvas)

        # Shift to mid-gray and clamp
        result = Canvas(canvas.width, canvas.height)
        for y in range(canvas.height):
            for x in range(canvas.width):
                src = embossed.pixels[y][x]
                orig = canvas.pixels[y][x]

                if orig[3] > 0:
                    r = max(0, min(255, src[0] + 128))
                    g = max(0, min(255, src[1] + 128))
                    b = max(0, min(255, src[2] + 128))
                    result.pixels[y][x] = [r, g, b, orig[3]]

        return result


class EdgeDetect(Effect):
    """Edge detection filter."""

    METHODS = {
        "sobel": {
            "x": [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]],
            "y": [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]
        },
        "prewitt": {
            "x": [[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]],
            "y": [[-1, -1, -1], [0, 0, 0], [1, 1, 1]]
        },
        "laplacian": {
            "single": [[0, 1, 0], [1, -4, 1], [0, 1, 0]]
        }
    }

    def __init__(self, method: str = "sobel"):
        """Initialize edge detection.

        Args:
            method: Detection method (sobel, prewitt, laplacian)
        """
        self.method = method

    def process(self, canvas: Canvas) -> Canvas:
        """Apply edge detection."""
        if self.method == "laplacian":
            kernel = ConvolutionKernel(self.METHODS["laplacian"]["single"], normalize=False)
            return kernel.apply(canvas)

        # Sobel/Prewitt: combine X and Y gradients
        matrices = self.METHODS.get(self.method, self.METHODS["sobel"])

        kernel_x = ConvolutionKernel(matrices["x"], normalize=False)
        kernel_y = ConvolutionKernel(matrices["y"], normalize=False)

        gx = kernel_x.apply(canvas)
        gy = kernel_y.apply(canvas)

        # Combine gradients
        result = Canvas(canvas.width, canvas.height)
        for y in range(canvas.height):
            for x in range(canvas.width):
                px, py = gx.pixels[y][x], gy.pixels[y][x]
                orig = canvas.pixels[y][x]

                if orig[3] > 0:
                    r = min(255, int(math.sqrt(px[0]**2 + py[0]**2)))
                    g = min(255, int(math.sqrt(px[1]**2 + py[1]**2)))
                    b = min(255, int(math.sqrt(px[2]**2 + py[2]**2)))
                    result.pixels[y][x] = [r, g, b, orig[3]]

        return result


# =============================================================================
# Pixel-level Effects
# =============================================================================

class Pixelate(Effect):
    """Mosaic/pixelation effect."""

    def __init__(self, block_size: int = 4):
        """Initialize pixelation.

        Args:
            block_size: Size of pixel blocks
        """
        self.block_size = max(1, block_size)

    def process(self, canvas: Canvas) -> Canvas:
        """Apply pixelation."""
        result = Canvas(canvas.width, canvas.height)

        for by in range(0, canvas.height, self.block_size):
            for bx in range(0, canvas.width, self.block_size):
                # Average colors in block
                r, g, b, a = 0, 0, 0, 0
                count = 0

                for dy in range(self.block_size):
                    for dx in range(self.block_size):
                        x, y = bx + dx, by + dy
                        if x < canvas.width and y < canvas.height:
                            pixel = canvas.pixels[y][x]
                            if pixel[3] > 0:
                                r += pixel[0]
                                g += pixel[1]
                                b += pixel[2]
                                a += pixel[3]
                                count += 1

                if count > 0:
                    avg_color = [r // count, g // count, b // count, a // count]

                    # Fill block with average
                    for dy in range(self.block_size):
                        for dx in range(self.block_size):
                            x, y = bx + dx, by + dy
                            if x < canvas.width and y < canvas.height:
                                if canvas.pixels[y][x][3] > 0:
                                    result.pixels[y][x] = avg_color

        return result


class Posterize(Effect):
    """Reduce color levels (posterization)."""

    def __init__(self, levels: int = 4):
        """Initialize posterization.

        Args:
            levels: Number of levels per channel (2-256)
        """
        self.levels = max(2, min(256, levels))

    def process(self, canvas: Canvas) -> Canvas:
        """Apply posterization."""
        result = Canvas(canvas.width, canvas.height)
        step = 256 // self.levels

        for y in range(canvas.height):
            for x in range(canvas.width):
                pixel = canvas.pixels[y][x]

                if pixel[3] > 0:
                    r = (pixel[0] // step) * step
                    g = (pixel[1] // step) * step
                    b = (pixel[2] // step) * step
                    result.pixels[y][x] = [r, g, b, pixel[3]]

        return result


class DitherMethod(Enum):
    """Dithering methods."""
    ORDERED = "ordered"           # Bayer matrix
    FLOYD_STEINBERG = "floyd_steinberg"
    THRESHOLD = "threshold"


class Dither(Effect):
    """Apply dithering to reduce colors."""

    # 4x4 Bayer matrix
    BAYER_4X4 = [
        [0, 8, 2, 10],
        [12, 4, 14, 6],
        [3, 11, 1, 9],
        [15, 7, 13, 5]
    ]

    def __init__(
        self,
        palette: List[Color],
        method: DitherMethod = DitherMethod.ORDERED,
        threshold: float = 0.5
    ):
        """Initialize dithering.

        Args:
            palette: Target color palette
            method: Dithering algorithm
            threshold: Threshold for ordered dithering
        """
        self.palette = palette
        self.method = method
        self.threshold = threshold

    def process(self, canvas: Canvas) -> Canvas:
        """Apply dithering."""
        if self.method == DitherMethod.ORDERED:
            return self._ordered_dither(canvas)
        elif self.method == DitherMethod.FLOYD_STEINBERG:
            return self._floyd_steinberg(canvas)
        else:
            return self._threshold_dither(canvas)

    def _find_nearest_color(self, color: Color) -> Color:
        """Find nearest palette color."""
        if not self.palette:
            return color

        min_dist = float('inf')
        nearest = self.palette[0]

        for pal_color in self.palette:
            dist = (
                (color[0] - pal_color[0]) ** 2 +
                (color[1] - pal_color[1]) ** 2 +
                (color[2] - pal_color[2]) ** 2
            )
            if dist < min_dist:
                min_dist = dist
                nearest = pal_color

        return nearest

    def _ordered_dither(self, canvas: Canvas) -> Canvas:
        """Apply ordered (Bayer) dithering."""
        result = Canvas(canvas.width, canvas.height)

        for y in range(canvas.height):
            for x in range(canvas.width):
                pixel = canvas.pixels[y][x]

                if pixel[3] == 0:
                    continue

                # Get Bayer threshold
                bayer = self.BAYER_4X4[y % 4][x % 4] / 16.0 - 0.5
                threshold_adj = self.threshold + bayer * 0.5

                # Adjust color based on threshold
                r = pixel[0] + int((threshold_adj - 0.5) * 64)
                g = pixel[1] + int((threshold_adj - 0.5) * 64)
                b = pixel[2] + int((threshold_adj - 0.5) * 64)

                adjusted = (
                    max(0, min(255, r)),
                    max(0, min(255, g)),
                    max(0, min(255, b)),
                    pixel[3]
                )

                nearest = self._find_nearest_color(adjusted)
                result.pixels[y][x] = list(nearest)

        return result

    def _floyd_steinberg(self, canvas: Canvas) -> Canvas:
        """Apply Floyd-Steinberg error diffusion."""
        # Work on a float copy for error accumulation
        errors = [[[0.0, 0.0, 0.0] for _ in range(canvas.width)] for _ in range(canvas.height)]
        result = Canvas(canvas.width, canvas.height)

        for y in range(canvas.height):
            for x in range(canvas.width):
                pixel = canvas.pixels[y][x]

                if pixel[3] == 0:
                    continue

                # Add accumulated error
                old_r = max(0, min(255, pixel[0] + int(errors[y][x][0])))
                old_g = max(0, min(255, pixel[1] + int(errors[y][x][1])))
                old_b = max(0, min(255, pixel[2] + int(errors[y][x][2])))

                # Find nearest palette color
                nearest = self._find_nearest_color((old_r, old_g, old_b, pixel[3]))
                result.pixels[y][x] = list(nearest)

                # Calculate error
                err_r = old_r - nearest[0]
                err_g = old_g - nearest[1]
                err_b = old_b - nearest[2]

                # Distribute error to neighbors
                # Right: 7/16, Bottom-left: 3/16, Bottom: 5/16, Bottom-right: 1/16
                if x + 1 < canvas.width:
                    errors[y][x + 1][0] += err_r * 7 / 16
                    errors[y][x + 1][1] += err_g * 7 / 16
                    errors[y][x + 1][2] += err_b * 7 / 16

                if y + 1 < canvas.height:
                    if x > 0:
                        errors[y + 1][x - 1][0] += err_r * 3 / 16
                        errors[y + 1][x - 1][1] += err_g * 3 / 16
                        errors[y + 1][x - 1][2] += err_b * 3 / 16

                    errors[y + 1][x][0] += err_r * 5 / 16
                    errors[y + 1][x][1] += err_g * 5 / 16
                    errors[y + 1][x][2] += err_b * 5 / 16

                    if x + 1 < canvas.width:
                        errors[y + 1][x + 1][0] += err_r * 1 / 16
                        errors[y + 1][x + 1][1] += err_g * 1 / 16
                        errors[y + 1][x + 1][2] += err_b * 1 / 16

        return result

    def _threshold_dither(self, canvas: Canvas) -> Canvas:
        """Apply simple threshold dithering."""
        result = Canvas(canvas.width, canvas.height)

        for y in range(canvas.height):
            for x in range(canvas.width):
                pixel = canvas.pixels[y][x]

                if pixel[3] > 0:
                    nearest = self._find_nearest_color(pixel)
                    result.pixels[y][x] = list(nearest)

        return result


class Invert(Effect):
    """Invert colors."""

    def __init__(self, preserve_alpha: bool = True):
        """Initialize inversion.

        Args:
            preserve_alpha: Keep original alpha values
        """
        self.preserve_alpha = preserve_alpha

    def process(self, canvas: Canvas) -> Canvas:
        """Apply color inversion."""
        result = Canvas(canvas.width, canvas.height)

        for y in range(canvas.height):
            for x in range(canvas.width):
                pixel = canvas.pixels[y][x]

                if pixel[3] > 0:
                    r = 255 - pixel[0]
                    g = 255 - pixel[1]
                    b = 255 - pixel[2]
                    a = pixel[3] if self.preserve_alpha else 255 - pixel[3]
                    result.pixels[y][x] = [r, g, b, a]

        return result


class Grayscale(Effect):
    """Convert to grayscale."""

    def __init__(self, method: str = "luminosity"):
        """Initialize grayscale.

        Args:
            method: Conversion method (luminosity, average, lightness)
        """
        self.method = method

    def process(self, canvas: Canvas) -> Canvas:
        """Apply grayscale conversion."""
        result = Canvas(canvas.width, canvas.height)

        for y in range(canvas.height):
            for x in range(canvas.width):
                pixel = canvas.pixels[y][x]

                if pixel[3] > 0:
                    if self.method == "luminosity":
                        gray = int(0.299 * pixel[0] + 0.587 * pixel[1] + 0.114 * pixel[2])
                    elif self.method == "average":
                        gray = (pixel[0] + pixel[1] + pixel[2]) // 3
                    else:  # lightness
                        gray = (max(pixel[0], pixel[1], pixel[2]) +
                                min(pixel[0], pixel[1], pixel[2])) // 2

                    result.pixels[y][x] = [gray, gray, gray, pixel[3]]

        return result


class Sepia(Effect):
    """Apply sepia tone."""

    def __init__(self, intensity: float = 1.0):
        """Initialize sepia.

        Args:
            intensity: Effect intensity (0-1)
        """
        self.intensity = max(0.0, min(1.0, intensity))

    def process(self, canvas: Canvas) -> Canvas:
        """Apply sepia effect."""
        result = Canvas(canvas.width, canvas.height)

        for y in range(canvas.height):
            for x in range(canvas.width):
                pixel = canvas.pixels[y][x]

                if pixel[3] > 0:
                    # Sepia transformation
                    r = int(pixel[0] * 0.393 + pixel[1] * 0.769 + pixel[2] * 0.189)
                    g = int(pixel[0] * 0.349 + pixel[1] * 0.686 + pixel[2] * 0.168)
                    b = int(pixel[0] * 0.272 + pixel[1] * 0.534 + pixel[2] * 0.131)

                    # Blend with original based on intensity
                    r = int(pixel[0] * (1 - self.intensity) + min(255, r) * self.intensity)
                    g = int(pixel[1] * (1 - self.intensity) + min(255, g) * self.intensity)
                    b = int(pixel[2] * (1 - self.intensity) + min(255, b) * self.intensity)

                    result.pixels[y][x] = [r, g, b, pixel[3]]

        return result


# =============================================================================
# Post-Processor Manager
# =============================================================================

class PostProcessor:
    """Manages and applies post-processing effects."""

    def __init__(self):
        self.effects: List[Effect] = []

    def add(self, effect: Effect) -> 'PostProcessor':
        """Add an effect to the pipeline.

        Args:
            effect: Effect to add

        Returns:
            Self for chaining
        """
        self.effects.append(effect)
        return self

    def clear(self) -> 'PostProcessor':
        """Remove all effects.

        Returns:
            Self for chaining
        """
        self.effects.clear()
        return self

    def process(self, canvas: Canvas) -> Canvas:
        """Apply all effects in order.

        Args:
            canvas: Source canvas

        Returns:
            Processed canvas
        """
        result = canvas
        for effect in self.effects:
            result = effect.process(result)
        return result


# =============================================================================
# Convenience Functions
# =============================================================================

def blur(canvas: Canvas, radius: int = 2) -> Canvas:
    """Apply Gaussian blur.

    Args:
        canvas: Source canvas
        radius: Blur radius

    Returns:
        Blurred canvas
    """
    return GaussianBlur(radius).process(canvas)


def sharpen(canvas: Canvas, amount: float = 1.0) -> Canvas:
    """Apply sharpening.

    Args:
        canvas: Source canvas
        amount: Sharpening strength

    Returns:
        Sharpened canvas
    """
    return Sharpen(amount).process(canvas)


def pixelate(canvas: Canvas, block_size: int = 4) -> Canvas:
    """Apply pixelation.

    Args:
        canvas: Source canvas
        block_size: Pixel block size

    Returns:
        Pixelated canvas
    """
    return Pixelate(block_size).process(canvas)


def posterize(canvas: Canvas, levels: int = 4) -> Canvas:
    """Apply posterization.

    Args:
        canvas: Source canvas
        levels: Number of color levels

    Returns:
        Posterized canvas
    """
    return Posterize(levels).process(canvas)


def grayscale(canvas: Canvas) -> Canvas:
    """Convert to grayscale.

    Args:
        canvas: Source canvas

    Returns:
        Grayscale canvas
    """
    return Grayscale().process(canvas)


def sepia(canvas: Canvas, intensity: float = 1.0) -> Canvas:
    """Apply sepia tone.

    Args:
        canvas: Source canvas
        intensity: Effect intensity

    Returns:
        Sepia-toned canvas
    """
    return Sepia(intensity).process(canvas)


def invert(canvas: Canvas) -> Canvas:
    """Invert colors.

    Args:
        canvas: Source canvas

    Returns:
        Inverted canvas
    """
    return Invert().process(canvas)


def emboss(canvas: Canvas, direction: str = "top-left") -> Canvas:
    """Apply emboss effect.

    Args:
        canvas: Source canvas
        direction: Light direction

    Returns:
        Embossed canvas
    """
    return Emboss(direction).process(canvas)


def detect_edges(canvas: Canvas, method: str = "sobel") -> Canvas:
    """Apply edge detection.

    Args:
        canvas: Source canvas
        method: Detection method

    Returns:
        Edge-detected canvas
    """
    return EdgeDetect(method).process(canvas)

"""Reference image tracing to pixel art."""

from dataclasses import dataclass
from typing import List, Tuple, Optional
import math

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Canvas
from core.palette import Palette
from .quantize import ColorQuantizer, QuantizeConfig, QuantizeMethod

Color = Tuple[int, int, int, int]


@dataclass
class TraceConfig:
    """Configuration for image tracing."""
    target_width: int = 32
    target_height: Optional[int] = None  # Auto from aspect ratio
    color_count: int = 16
    outline: bool = True
    outline_color: Optional[Color] = None  # Auto-detect dark color
    outline_threshold: float = 0.3  # Edge detection sensitivity
    dither: bool = False
    smooth: bool = True  # Use area averaging vs nearest neighbor
    preserve_details: bool = True  # Enhance edges before downsampling
    contrast_boost: float = 1.0  # Contrast enhancement (1.0 = none)
    saturation_boost: float = 1.0  # Saturation enhancement


class ImageTracer:
    """Converts reference images to pixel art."""

    def __init__(self, config: Optional[TraceConfig] = None):
        self.config = config or TraceConfig()

    def trace(self, canvas: Canvas) -> Canvas:
        """Trace a reference image to pixel art.

        Args:
            canvas: Source image

        Returns:
            Pixel art canvas
        """
        # Calculate target dimensions
        target_w, target_h = self._calculate_dimensions(canvas)

        # Pre-process: enhance contrast and details
        processed = canvas
        if self.config.contrast_boost != 1.0:
            processed = self._adjust_contrast(processed, self.config.contrast_boost)
        if self.config.saturation_boost != 1.0:
            processed = self._adjust_saturation(processed, self.config.saturation_boost)

        # Detect edges before downsampling if preserving details
        edges = None
        if self.config.preserve_details:
            edges = self._detect_edges(processed)

        # Downsample to target resolution
        downsampled = self._downsample(processed, target_w, target_h)

        # Quantize colors
        quantized, palette = self._quantize_colors(downsampled)

        # Add outlines
        if self.config.outline:
            # Downsample edge map
            if edges is not None:
                edges_small = self._downsample(edges, target_w, target_h)
            else:
                edges_small = self._detect_edges(quantized)

            quantized = self._add_outlines(quantized, edges_small, palette)

        return quantized

    def trace_with_palette(self, canvas: Canvas, palette: Palette) -> Canvas:
        """Trace using a specific palette.

        Args:
            canvas: Source image
            palette: Target palette

        Returns:
            Pixel art canvas using the palette
        """
        # Calculate target dimensions
        target_w, target_h = self._calculate_dimensions(canvas)

        # Downsample
        downsampled = self._downsample(canvas, target_w, target_h)

        # Map to palette
        result = self._map_to_palette(downsampled, palette)

        # Add outlines
        if self.config.outline:
            edges = self._detect_edges(result)
            result = self._add_outlines(result, edges, palette)

        return result

    def _calculate_dimensions(self, canvas: Canvas) -> Tuple[int, int]:
        """Calculate target dimensions preserving aspect ratio."""
        target_w = self.config.target_width

        if self.config.target_height is not None:
            target_h = self.config.target_height
        else:
            # Calculate from aspect ratio
            aspect = canvas.height / canvas.width
            target_h = max(1, int(target_w * aspect))

        return target_w, target_h

    def _downsample(self, canvas: Canvas, target_w: int, target_h: int) -> Canvas:
        """Downsample canvas to target size."""
        result = Canvas(target_w, target_h)

        scale_x = canvas.width / target_w
        scale_y = canvas.height / target_h

        for y in range(target_h):
            for x in range(target_w):
                if self.config.smooth:
                    # Area averaging
                    color = self._sample_area(
                        canvas,
                        x * scale_x, y * scale_y,
                        scale_x, scale_y
                    )
                else:
                    # Nearest neighbor
                    src_x = int((x + 0.5) * scale_x)
                    src_y = int((y + 0.5) * scale_y)
                    src_x = min(src_x, canvas.width - 1)
                    src_y = min(src_y, canvas.height - 1)
                    color = canvas.get_pixel(src_x, src_y)

                result.set_pixel(x, y, color)

        return result

    def _sample_area(self, canvas: Canvas, x: float, y: float,
                     w: float, h: float) -> Color:
        """Sample and average a rectangular area."""
        x1 = int(x)
        y1 = int(y)
        x2 = min(int(x + w) + 1, canvas.width)
        y2 = min(int(y + h) + 1, canvas.height)

        total_r = 0
        total_g = 0
        total_b = 0
        total_a = 0
        count = 0

        for sy in range(y1, y2):
            for sx in range(x1, x2):
                color = canvas.get_pixel(sx, sy)
                total_r += color[0]
                total_g += color[1]
                total_b += color[2]
                total_a += color[3]
                count += 1

        if count == 0:
            return (0, 0, 0, 0)

        return (
            total_r // count,
            total_g // count,
            total_b // count,
            total_a // count
        )

    def _quantize_colors(self, canvas: Canvas) -> Tuple[Canvas, Palette]:
        """Quantize canvas colors."""
        quantizer = ColorQuantizer(QuantizeConfig(
            method=QuantizeMethod.MEDIAN_CUT,
            color_count=self.config.color_count
        ))
        return quantizer.quantize(canvas)

    def _detect_edges(self, canvas: Canvas) -> Canvas:
        """Detect edges using Sobel operator."""
        result = Canvas(canvas.width, canvas.height)

        # Sobel kernels
        for y in range(1, canvas.height - 1):
            for x in range(1, canvas.width - 1):
                # Get 3x3 neighborhood luminance
                pixels = []
                for dy in range(-1, 2):
                    row = []
                    for dx in range(-1, 2):
                        color = canvas.get_pixel(x + dx, y + dy)
                        lum = (color[0] * 299 + color[1] * 587 + color[2] * 114) // 1000
                        row.append(lum)
                    pixels.append(row)

                # Sobel X gradient
                gx = (
                    -pixels[0][0] + pixels[0][2] +
                    -2 * pixels[1][0] + 2 * pixels[1][2] +
                    -pixels[2][0] + pixels[2][2]
                )

                # Sobel Y gradient
                gy = (
                    -pixels[0][0] - 2 * pixels[0][1] - pixels[0][2] +
                    pixels[2][0] + 2 * pixels[2][1] + pixels[2][2]
                )

                # Gradient magnitude
                mag = int(math.sqrt(gx * gx + gy * gy))
                mag = min(255, mag)

                result.set_pixel(x, y, (mag, mag, mag, 255))

        return result

    def _add_outlines(self, canvas: Canvas, edges: Canvas, palette: Palette) -> Canvas:
        """Add outlines based on edge detection."""
        result = Canvas(canvas.width, canvas.height)
        threshold = int(self.config.outline_threshold * 255)

        # Find outline color
        outline_color = self.config.outline_color
        if outline_color is None:
            outline_color = self._find_dark_color(palette)

        for y in range(canvas.height):
            for x in range(canvas.width):
                edge_value = edges.get_pixel(x, y)[0]
                original = canvas.get_pixel(x, y)

                if edge_value > threshold:
                    result.set_pixel(x, y, outline_color)
                else:
                    result.set_pixel(x, y, original)

        return result

    def _find_dark_color(self, palette: Palette) -> Color:
        """Find the darkest color in palette for outlines."""
        darkest = (0, 0, 0, 255)
        min_lum = float('inf')

        for color in palette.colors:
            lum = color[0] * 0.299 + color[1] * 0.587 + color[2] * 0.114
            if lum < min_lum:
                min_lum = lum
                darkest = color

        return darkest

    def _map_to_palette(self, canvas: Canvas, palette: Palette) -> Canvas:
        """Map canvas colors to a palette."""
        result = Canvas(canvas.width, canvas.height)
        palette_colors = palette.colors

        for y in range(canvas.height):
            for x in range(canvas.width):
                color = canvas.get_pixel(x, y)

                # Skip transparent
                if color[3] < 128:
                    result.set_pixel(x, y, color)
                    continue

                # Find nearest palette color
                min_dist = float('inf')
                nearest = palette_colors[0]

                for pc in palette_colors:
                    dr = color[0] - pc[0]
                    dg = color[1] - pc[1]
                    db = color[2] - pc[2]
                    dist = dr * dr + dg * dg * 2 + db * db

                    if dist < min_dist:
                        min_dist = dist
                        nearest = pc

                result.set_pixel(x, y, nearest)

        return result

    def _adjust_contrast(self, canvas: Canvas, factor: float) -> Canvas:
        """Adjust canvas contrast."""
        result = Canvas(canvas.width, canvas.height)

        for y in range(canvas.height):
            for x in range(canvas.width):
                color = canvas.get_pixel(x, y)

                r = int(128 + (color[0] - 128) * factor)
                g = int(128 + (color[1] - 128) * factor)
                b = int(128 + (color[2] - 128) * factor)

                r = max(0, min(255, r))
                g = max(0, min(255, g))
                b = max(0, min(255, b))

                result.set_pixel(x, y, (r, g, b, color[3]))

        return result

    def _adjust_saturation(self, canvas: Canvas, factor: float) -> Canvas:
        """Adjust canvas saturation."""
        result = Canvas(canvas.width, canvas.height)

        for y in range(canvas.height):
            for x in range(canvas.width):
                color = canvas.get_pixel(x, y)

                # Convert to grayscale
                gray = (color[0] * 299 + color[1] * 587 + color[2] * 114) // 1000

                r = int(gray + (color[0] - gray) * factor)
                g = int(gray + (color[1] - gray) * factor)
                b = int(gray + (color[2] - gray) * factor)

                r = max(0, min(255, r))
                g = max(0, min(255, g))
                b = max(0, min(255, b))

                result.set_pixel(x, y, (r, g, b, color[3]))

        return result


# Convenience functions

def trace_image(canvas: Canvas, width: int = 32, colors: int = 16,
                outline: bool = True) -> Canvas:
    """Trace a reference image to pixel art.

    Args:
        canvas: Source image
        width: Target width in pixels
        colors: Number of colors in result
        outline: Whether to add outlines

    Returns:
        Traced pixel art canvas
    """
    tracer = ImageTracer(TraceConfig(
        target_width=width,
        color_count=colors,
        outline=outline
    ))
    return tracer.trace(canvas)


def trace_to_palette(canvas: Canvas, palette: Palette, width: int = 32,
                     outline: bool = True) -> Canvas:
    """Trace using a specific palette.

    Args:
        canvas: Source image
        palette: Target palette
        width: Target width in pixels
        outline: Whether to add outlines

    Returns:
        Traced pixel art canvas
    """
    tracer = ImageTracer(TraceConfig(
        target_width=width,
        color_count=len(palette.colors),
        outline=outline
    ))
    return tracer.trace_with_palette(canvas, palette)


def auto_pixelate(canvas: Canvas, target_size: int = 32) -> Canvas:
    """Quick pixelation without quantization.

    Args:
        canvas: Source image
        target_size: Target size (width)

    Returns:
        Pixelated canvas
    """
    tracer = ImageTracer(TraceConfig(
        target_width=target_size,
        color_count=256,  # Keep all colors
        outline=False,
        smooth=True
    ))

    # Just downsample
    target_w, target_h = tracer._calculate_dimensions(canvas)
    return tracer._downsample(canvas, target_w, target_h)


def downsample(canvas: Canvas, width: int, height: Optional[int] = None,
               smooth: bool = True) -> Canvas:
    """Downsample canvas to target size.

    Args:
        canvas: Source canvas
        width: Target width
        height: Target height (auto from aspect if None)
        smooth: Use area averaging vs nearest neighbor

    Returns:
        Downsampled canvas
    """
    tracer = ImageTracer(TraceConfig(
        target_width=width,
        target_height=height,
        smooth=smooth
    ))

    target_w, target_h = tracer._calculate_dimensions(canvas)
    return tracer._downsample(canvas, target_w, target_h)

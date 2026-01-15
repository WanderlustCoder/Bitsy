"""
Transforms - Image transformation and batch operations.

Provides:
- Color adjustments (brightness, contrast, saturation)
- Palette operations (remap, reduce, extract)
- Geometric transforms (rotate, skew)
- Batch processing utilities
- Pixel-level operations
"""

import math
from typing import List, Tuple, Optional, Callable, Dict
from dataclasses import dataclass

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Canvas


# ============ Color Adjustments ============

def adjust_brightness(canvas: Canvas, amount: float) -> Canvas:
    """Adjust image brightness.

    Args:
        canvas: Source canvas
        amount: Brightness adjustment (-1.0 to 1.0)

    Returns:
        New adjusted canvas
    """
    result = canvas.copy()
    factor = int(amount * 255)

    for y in range(result.height):
        for x in range(result.width):
            r, g, b, a = result.pixels[y][x]
            r = max(0, min(255, r + factor))
            g = max(0, min(255, g + factor))
            b = max(0, min(255, b + factor))
            result.pixels[y][x] = (r, g, b, a)

    return result


def adjust_contrast(canvas: Canvas, amount: float) -> Canvas:
    """Adjust image contrast.

    Args:
        canvas: Source canvas
        amount: Contrast factor (0.0 = gray, 1.0 = normal, 2.0 = high)

    Returns:
        New adjusted canvas
    """
    result = canvas.copy()

    for y in range(result.height):
        for x in range(result.width):
            r, g, b, a = result.pixels[y][x]

            # Apply contrast around middle gray
            r = max(0, min(255, int((r - 128) * amount + 128)))
            g = max(0, min(255, int((g - 128) * amount + 128)))
            b = max(0, min(255, int((b - 128) * amount + 128)))

            result.pixels[y][x] = (r, g, b, a)

    return result


def adjust_saturation(canvas: Canvas, amount: float) -> Canvas:
    """Adjust color saturation.

    Args:
        canvas: Source canvas
        amount: Saturation factor (0.0 = grayscale, 1.0 = normal, 2.0 = vivid)

    Returns:
        New adjusted canvas
    """
    result = canvas.copy()

    for y in range(result.height):
        for x in range(result.width):
            r, g, b, a = result.pixels[y][x]

            # Calculate luminance
            lum = int(0.299 * r + 0.587 * g + 0.114 * b)

            # Interpolate between grayscale and original
            r = max(0, min(255, int(lum + (r - lum) * amount)))
            g = max(0, min(255, int(lum + (g - lum) * amount)))
            b = max(0, min(255, int(lum + (b - lum) * amount)))

            result.pixels[y][x] = (r, g, b, a)

    return result


def adjust_hue(canvas: Canvas, degrees: float) -> Canvas:
    """Shift hue by degrees.

    Args:
        canvas: Source canvas
        degrees: Hue shift in degrees

    Returns:
        New adjusted canvas
    """
    result = canvas.copy()

    for y in range(result.height):
        for x in range(result.width):
            r, g, b, a = result.pixels[y][x]

            # Convert to HSV
            h, s, v = _rgb_to_hsv(r, g, b)

            # Shift hue
            h = (h + degrees) % 360

            # Convert back to RGB
            r, g, b = _hsv_to_rgb(h, s, v)
            result.pixels[y][x] = (r, g, b, a)

    return result


def _rgb_to_hsv(r: int, g: int, b: int) -> Tuple[float, float, float]:
    """Convert RGB to HSV."""
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    max_c = max(r, g, b)
    min_c = min(r, g, b)
    delta = max_c - min_c

    # Hue
    if delta == 0:
        h = 0
    elif max_c == r:
        h = 60 * (((g - b) / delta) % 6)
    elif max_c == g:
        h = 60 * (((b - r) / delta) + 2)
    else:
        h = 60 * (((r - g) / delta) + 4)

    # Saturation
    s = 0 if max_c == 0 else delta / max_c

    # Value
    v = max_c

    return h, s, v


def _hsv_to_rgb(h: float, s: float, v: float) -> Tuple[int, int, int]:
    """Convert HSV to RGB."""
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c

    if h < 60:
        r, g, b = c, x, 0
    elif h < 120:
        r, g, b = x, c, 0
    elif h < 180:
        r, g, b = 0, c, x
    elif h < 240:
        r, g, b = 0, x, c
    elif h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x

    return (
        int((r + m) * 255),
        int((g + m) * 255),
        int((b + m) * 255)
    )


def invert_colors(canvas: Canvas) -> Canvas:
    """Invert all colors.

    Args:
        canvas: Source canvas

    Returns:
        New inverted canvas
    """
    result = canvas.copy()

    for y in range(result.height):
        for x in range(result.width):
            r, g, b, a = result.pixels[y][x]
            result.pixels[y][x] = (255 - r, 255 - g, 255 - b, a)

    return result


def grayscale(canvas: Canvas) -> Canvas:
    """Convert to grayscale.

    Args:
        canvas: Source canvas

    Returns:
        New grayscale canvas
    """
    return adjust_saturation(canvas, 0.0)


def sepia(canvas: Canvas, intensity: float = 1.0) -> Canvas:
    """Apply sepia tone.

    Args:
        canvas: Source canvas
        intensity: Effect intensity (0.0 to 1.0)

    Returns:
        New sepia-toned canvas
    """
    result = canvas.copy()

    for y in range(result.height):
        for x in range(result.width):
            r, g, b, a = result.pixels[y][x]

            # Sepia transformation
            tr = int(0.393 * r + 0.769 * g + 0.189 * b)
            tg = int(0.349 * r + 0.686 * g + 0.168 * b)
            tb = int(0.272 * r + 0.534 * g + 0.131 * b)

            # Blend with original based on intensity
            nr = int(r * (1 - intensity) + min(255, tr) * intensity)
            ng = int(g * (1 - intensity) + min(255, tg) * intensity)
            nb = int(b * (1 - intensity) + min(255, tb) * intensity)

            result.pixels[y][x] = (nr, ng, nb, a)

    return result


def posterize(canvas: Canvas, levels: int = 4) -> Canvas:
    """Reduce color levels (posterize effect).

    Args:
        canvas: Source canvas
        levels: Number of levels per channel (2-256)

    Returns:
        New posterized canvas
    """
    result = canvas.copy()
    levels = max(2, min(256, levels))
    step = 256 // levels

    for y in range(result.height):
        for x in range(result.width):
            r, g, b, a = result.pixels[y][x]

            r = (r // step) * step + step // 2
            g = (g // step) * step + step // 2
            b = (b // step) * step + step // 2

            result.pixels[y][x] = (
                min(255, r),
                min(255, g),
                min(255, b),
                a
            )

    return result


# ============ Palette Operations ============

def extract_palette(canvas: Canvas, max_colors: int = 256) -> List[Tuple[int, int, int, int]]:
    """Extract unique colors from canvas.

    Args:
        canvas: Source canvas
        max_colors: Maximum colors to extract

    Returns:
        List of unique RGBA colors
    """
    colors = set()

    for row in canvas.pixels:
        for pixel in row:
            colors.add(pixel)
            if len(colors) >= max_colors:
                break
        if len(colors) >= max_colors:
            break

    return sorted(list(colors))


def reduce_palette(canvas: Canvas, max_colors: int = 16) -> Canvas:
    """Reduce canvas to limited color palette.

    Uses simple median-cut-like quantization.

    Args:
        canvas: Source canvas
        max_colors: Maximum colors in result

    Returns:
        New canvas with reduced palette
    """
    # Extract all colors
    all_colors = []
    for row in canvas.pixels:
        for pixel in row:
            if pixel[3] > 0:  # Skip fully transparent
                all_colors.append(pixel)

    if not all_colors:
        return canvas.copy()

    # Simple quantization: cluster colors
    palette = _quantize_colors(all_colors, max_colors)

    # Remap pixels to nearest palette color
    result = canvas.copy()
    for y in range(result.height):
        for x in range(result.width):
            pixel = result.pixels[y][x]
            if pixel[3] > 0:
                nearest = _find_nearest_color(pixel, palette)
                result.pixels[y][x] = nearest

    return result


def _quantize_colors(colors: List[Tuple[int, int, int, int]],
                     max_colors: int) -> List[Tuple[int, int, int, int]]:
    """Simple color quantization using median cut."""
    if len(colors) <= max_colors:
        return list(set(colors))

    # Simple approach: divide color space
    buckets = [colors]

    while len(buckets) < max_colors:
        # Find bucket with largest range
        max_range = -1
        max_idx = 0
        max_channel = 0

        for i, bucket in enumerate(buckets):
            if len(bucket) < 2:
                continue

            for c in range(3):  # RGB channels
                values = [p[c] for p in bucket]
                color_range = max(values) - min(values)
                if color_range > max_range:
                    max_range = color_range
                    max_idx = i
                    max_channel = c

        if max_range <= 0:
            break

        # Split bucket at median
        bucket = buckets[max_idx]
        bucket.sort(key=lambda p: p[max_channel])
        mid = len(bucket) // 2

        buckets[max_idx] = bucket[:mid]
        buckets.append(bucket[mid:])

    # Calculate average color for each bucket
    palette = []
    for bucket in buckets:
        if bucket:
            avg_r = sum(p[0] for p in bucket) // len(bucket)
            avg_g = sum(p[1] for p in bucket) // len(bucket)
            avg_b = sum(p[2] for p in bucket) // len(bucket)
            avg_a = sum(p[3] for p in bucket) // len(bucket)
            palette.append((avg_r, avg_g, avg_b, avg_a))

    return palette


def _find_nearest_color(color: Tuple[int, int, int, int],
                        palette: List[Tuple[int, int, int, int]]
                        ) -> Tuple[int, int, int, int]:
    """Find nearest color in palette."""
    min_dist = float('inf')
    nearest = palette[0] if palette else color

    for p in palette:
        dist = (
            (color[0] - p[0]) ** 2 +
            (color[1] - p[1]) ** 2 +
            (color[2] - p[2]) ** 2
        )
        if dist < min_dist:
            min_dist = dist
            nearest = p

    return (nearest[0], nearest[1], nearest[2], color[3])  # Keep original alpha


def remap_palette(canvas: Canvas,
                  old_palette: List[Tuple[int, int, int, int]],
                  new_palette: List[Tuple[int, int, int, int]]) -> Canvas:
    """Remap colors from old palette to new palette.

    Args:
        canvas: Source canvas
        old_palette: Original palette colors
        new_palette: New palette colors (same length)

    Returns:
        New remapped canvas
    """
    if len(old_palette) != len(new_palette):
        raise ValueError("Palettes must have same length")

    # Build mapping
    color_map = {}
    for old, new in zip(old_palette, new_palette):
        color_map[old] = new

    result = canvas.copy()
    for y in range(result.height):
        for x in range(result.width):
            pixel = result.pixels[y][x]
            if pixel in color_map:
                result.pixels[y][x] = color_map[pixel]

    return result


def replace_color(canvas: Canvas,
                  old_color: Tuple[int, int, int, int],
                  new_color: Tuple[int, int, int, int],
                  tolerance: int = 0) -> Canvas:
    """Replace one color with another.

    Args:
        canvas: Source canvas
        old_color: Color to replace
        new_color: Replacement color
        tolerance: Color matching tolerance

    Returns:
        New canvas with replaced colors
    """
    result = canvas.copy()

    for y in range(result.height):
        for x in range(result.width):
            pixel = result.pixels[y][x]

            if tolerance == 0:
                if pixel == old_color:
                    result.pixels[y][x] = new_color
            else:
                diff = (
                    abs(pixel[0] - old_color[0]) +
                    abs(pixel[1] - old_color[1]) +
                    abs(pixel[2] - old_color[2]) +
                    abs(pixel[3] - old_color[3])
                )
                if diff <= tolerance * 4:
                    result.pixels[y][x] = new_color

    return result


# ============ Geometric Transforms ============

def rotate_90(canvas: Canvas) -> Canvas:
    """Rotate canvas 90 degrees clockwise.

    Args:
        canvas: Source canvas

    Returns:
        New rotated canvas
    """
    result = Canvas(canvas.height, canvas.width, (0, 0, 0, 0))

    for y in range(canvas.height):
        for x in range(canvas.width):
            result.pixels[x][canvas.height - 1 - y] = canvas.pixels[y][x]

    return result


def rotate_180(canvas: Canvas) -> Canvas:
    """Rotate canvas 180 degrees.

    Args:
        canvas: Source canvas

    Returns:
        New rotated canvas
    """
    result = Canvas(canvas.width, canvas.height, (0, 0, 0, 0))

    for y in range(canvas.height):
        for x in range(canvas.width):
            result.pixels[canvas.height - 1 - y][canvas.width - 1 - x] = \
                canvas.pixels[y][x]

    return result


def rotate_270(canvas: Canvas) -> Canvas:
    """Rotate canvas 270 degrees clockwise (90 counter-clockwise).

    Args:
        canvas: Source canvas

    Returns:
        New rotated canvas
    """
    result = Canvas(canvas.height, canvas.width, (0, 0, 0, 0))

    for y in range(canvas.height):
        for x in range(canvas.width):
            result.pixels[canvas.width - 1 - x][y] = canvas.pixels[y][x]

    return result


def crop(canvas: Canvas, x: int, y: int, width: int, height: int) -> Canvas:
    """Crop a region from canvas.

    Args:
        canvas: Source canvas
        x: Left edge
        y: Top edge
        width: Crop width
        height: Crop height

    Returns:
        New cropped canvas
    """
    # Clamp to valid region
    x = max(0, x)
    y = max(0, y)
    width = min(width, canvas.width - x)
    height = min(height, canvas.height - y)

    if width <= 0 or height <= 0:
        return Canvas(1, 1, (0, 0, 0, 0))

    result = Canvas(width, height, (0, 0, 0, 0))

    for dy in range(height):
        for dx in range(width):
            result.pixels[dy][dx] = canvas.pixels[y + dy][x + dx]

    return result


def pad(canvas: Canvas, left: int, top: int, right: int, bottom: int,
        color: Tuple[int, int, int, int] = (0, 0, 0, 0)) -> Canvas:
    """Add padding around canvas.

    Args:
        canvas: Source canvas
        left: Left padding
        top: Top padding
        right: Right padding
        bottom: Bottom padding
        color: Padding color

    Returns:
        New padded canvas
    """
    new_width = canvas.width + left + right
    new_height = canvas.height + top + bottom

    result = Canvas(new_width, new_height, color)
    result.blit(canvas, left, top)

    return result


def tile(canvas: Canvas, tiles_x: int, tiles_y: int) -> Canvas:
    """Tile canvas into a grid.

    Args:
        canvas: Source canvas
        tiles_x: Number of horizontal tiles
        tiles_y: Number of vertical tiles

    Returns:
        New tiled canvas
    """
    result = Canvas(
        canvas.width * tiles_x,
        canvas.height * tiles_y,
        (0, 0, 0, 0)
    )

    for ty in range(tiles_y):
        for tx in range(tiles_x):
            result.blit(canvas, tx * canvas.width, ty * canvas.height)

    return result


# ============ Pixel Operations ============

def outline(canvas: Canvas,
            color: Tuple[int, int, int, int] = (0, 0, 0, 255),
            thickness: int = 1) -> Canvas:
    """Add outline around non-transparent pixels.

    Args:
        canvas: Source canvas
        color: Outline color
        thickness: Outline thickness

    Returns:
        New canvas with outline
    """
    result = Canvas(canvas.width, canvas.height, (0, 0, 0, 0))

    # First pass: draw outline
    for y in range(canvas.height):
        for x in range(canvas.width):
            if canvas.pixels[y][x][3] > 0:
                # Check neighbors for transparency
                for dy in range(-thickness, thickness + 1):
                    for dx in range(-thickness, thickness + 1):
                        if dx == 0 and dy == 0:
                            continue

                        nx, ny = x + dx, y + dy
                        if 0 <= nx < canvas.width and 0 <= ny < canvas.height:
                            if canvas.pixels[ny][nx][3] == 0:
                                result.pixels[ny][nx] = color

    # Second pass: draw original on top
    for y in range(canvas.height):
        for x in range(canvas.width):
            if canvas.pixels[y][x][3] > 0:
                result.pixels[y][x] = canvas.pixels[y][x]

    return result


def drop_shadow(canvas: Canvas,
                offset_x: int = 2, offset_y: int = 2,
                color: Tuple[int, int, int, int] = (0, 0, 0, 128)) -> Canvas:
    """Add drop shadow to canvas.

    Args:
        canvas: Source canvas
        offset_x: Shadow X offset
        offset_y: Shadow Y offset
        color: Shadow color

    Returns:
        New canvas with shadow
    """
    # Expand canvas if needed
    new_width = canvas.width + abs(offset_x)
    new_height = canvas.height + abs(offset_y)

    result = Canvas(new_width, new_height, (0, 0, 0, 0))

    # Calculate positions
    shadow_x = max(0, offset_x)
    shadow_y = max(0, offset_y)
    image_x = max(0, -offset_x)
    image_y = max(0, -offset_y)

    # Draw shadow
    for y in range(canvas.height):
        for x in range(canvas.width):
            if canvas.pixels[y][x][3] > 0:
                result.pixels[shadow_y + y][shadow_x + x] = color

    # Draw original
    result.blit(canvas, image_x, image_y)

    return result


def glow(canvas: Canvas,
         color: Tuple[int, int, int, int] = (255, 255, 200, 128),
         radius: int = 2) -> Canvas:
    """Add glow effect around non-transparent pixels.

    Args:
        canvas: Source canvas
        color: Glow color
        radius: Glow radius

    Returns:
        New canvas with glow
    """
    # Expand canvas for glow
    result = Canvas(
        canvas.width + radius * 2,
        canvas.height + radius * 2,
        (0, 0, 0, 0)
    )

    # Draw glow layers
    for r in range(radius, 0, -1):
        alpha = int(color[3] * (1 - r / (radius + 1)))
        glow_color = (color[0], color[1], color[2], alpha)

        for y in range(canvas.height):
            for x in range(canvas.width):
                if canvas.pixels[y][x][3] > 0:
                    # Draw glow pixel
                    for dy in range(-r, r + 1):
                        for dx in range(-r, r + 1):
                            dist = (dx * dx + dy * dy) ** 0.5
                            if dist <= r:
                                gx = radius + x + dx
                                gy = radius + y + dy
                                if result.pixels[gy][gx][3] < alpha:
                                    result.pixels[gy][gx] = glow_color

    # Draw original
    result.blit(canvas, radius, radius)

    return result


def dither(canvas: Canvas, levels: int = 2) -> Canvas:
    """Apply ordered dithering to reduce colors.

    Args:
        canvas: Source canvas
        levels: Number of output levels (2-256)

    Returns:
        New dithered canvas
    """
    # 4x4 Bayer matrix
    bayer = [
        [0, 8, 2, 10],
        [12, 4, 14, 6],
        [3, 11, 1, 9],
        [15, 7, 13, 5]
    ]

    result = canvas.copy()
    step = 256 // levels
    threshold_scale = 16

    for y in range(result.height):
        for x in range(result.width):
            r, g, b, a = result.pixels[y][x]

            threshold = bayer[y % 4][x % 4] / threshold_scale - 0.5

            r = int((r / step + threshold) * step)
            g = int((g / step + threshold) * step)
            b = int((b / step + threshold) * step)

            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))

            result.pixels[y][x] = (r, g, b, a)

    return result


# ============ Batch Processing ============

def batch_process(canvases: List[Canvas],
                  operation: Callable[[Canvas], Canvas]) -> List[Canvas]:
    """Apply operation to multiple canvases.

    Args:
        canvases: List of source canvases
        operation: Function to apply

    Returns:
        List of processed canvases
    """
    return [operation(c) for c in canvases]


def create_variations(canvas: Canvas,
                      hue_shifts: List[float]) -> List[Canvas]:
    """Create color variations of a sprite.

    Args:
        canvas: Source canvas
        hue_shifts: List of hue shift values in degrees

    Returns:
        List of color variations
    """
    return [adjust_hue(canvas, shift) for shift in hue_shifts]


def create_animation_strip(frames: List[Canvas],
                           horizontal: bool = True) -> Canvas:
    """Combine frames into animation strip.

    Args:
        frames: List of frame canvases
        horizontal: True for horizontal strip, False for vertical

    Returns:
        Combined strip canvas
    """
    if not frames:
        return Canvas(1, 1, (0, 0, 0, 0))

    frame_w = frames[0].width
    frame_h = frames[0].height

    if horizontal:
        result = Canvas(frame_w * len(frames), frame_h, (0, 0, 0, 0))
        for i, frame in enumerate(frames):
            result.blit(frame, i * frame_w, 0)
    else:
        result = Canvas(frame_w, frame_h * len(frames), (0, 0, 0, 0))
        for i, frame in enumerate(frames):
            result.blit(frame, 0, i * frame_h)

    return result


def split_animation_strip(strip: Canvas, frame_count: int,
                          horizontal: bool = True) -> List[Canvas]:
    """Split animation strip into frames.

    Args:
        strip: Strip canvas
        frame_count: Number of frames
        horizontal: True if horizontal strip

    Returns:
        List of frame canvases
    """
    frames = []

    if horizontal:
        frame_w = strip.width // frame_count
        frame_h = strip.height
        for i in range(frame_count):
            frames.append(crop(strip, i * frame_w, 0, frame_w, frame_h))
    else:
        frame_w = strip.width
        frame_h = strip.height // frame_count
        for i in range(frame_count):
            frames.append(crop(strip, 0, i * frame_h, frame_w, frame_h))

    return frames

"""
Palette Tools - Extract and remap palettes for consistent styling.

Provides:
- Extract palettes from reference images
- Remap sprites to match target palettes
- Palette reduction and optimization
- Color matching and substitution

Example usage:
    from editor.palette_tools import extract_palette, remap_to_palette

    # Extract palette from reference
    ref_palette = extract_palette(reference_image, max_colors=16)

    # Remap a sprite to match
    remapped = remap_to_palette(sprite, ref_palette)
"""

import math
from typing import List, Tuple, Optional, Dict, Set
from dataclasses import dataclass, field

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Canvas, Palette
from core.color import color_distance_rgb, rgb_to_hsv, hsv_to_rgb


@dataclass
class ColorInfo:
    """Information about a color in an image."""
    color: Tuple[int, int, int, int]
    count: int = 0
    percentage: float = 0.0


@dataclass
class PaletteAnalysis:
    """Analysis of a palette extracted from an image."""
    colors: List[Tuple[int, int, int, int]]
    color_info: List[ColorInfo]
    dominant_color: Tuple[int, int, int, int]
    average_color: Tuple[int, int, int, int]
    color_range: Dict[str, Tuple[int, int]]  # min/max for each channel


# ==================== Palette Extraction ====================

def extract_palette(canvas: Canvas, max_colors: int = 16,
                   include_transparent: bool = False,
                   min_percentage: float = 0.01) -> Palette:
    """Extract a palette from a canvas.

    Args:
        canvas: Source canvas
        max_colors: Maximum colors to extract
        include_transparent: Include fully transparent pixels
        min_percentage: Minimum percentage for a color to be included

    Returns:
        Palette with extracted colors
    """
    # Count all colors
    color_counts: Dict[Tuple[int, int, int, int], int] = {}
    total_pixels = 0

    for y in range(canvas.height):
        for x in range(canvas.width):
            pixel = tuple(canvas.get_pixel(x, y))

            if not include_transparent and pixel[3] == 0:
                continue

            total_pixels += 1
            color_counts[pixel] = color_counts.get(pixel, 0) + 1

    if total_pixels == 0:
        return Palette()

    # Filter by minimum percentage
    min_count = int(total_pixels * min_percentage)
    filtered = {c: count for c, count in color_counts.items() if count >= min_count}

    # Sort by count (most common first)
    sorted_colors = sorted(filtered.items(), key=lambda x: x[1], reverse=True)

    # Take top colors
    palette = Palette()
    for color, _ in sorted_colors[:max_colors]:
        palette.add(color)

    return palette


def extract_palette_kmeans(canvas: Canvas, num_colors: int = 8,
                          iterations: int = 10,
                          include_transparent: bool = False) -> Palette:
    """Extract palette using k-means clustering.

    Better for finding representative colors than simple counting.

    Args:
        canvas: Source canvas
        num_colors: Number of colors to extract
        iterations: K-means iterations
        include_transparent: Include transparent pixels

    Returns:
        Palette with clustered colors
    """
    import random

    # Collect all pixels
    pixels = []
    for y in range(canvas.height):
        for x in range(canvas.width):
            pixel = canvas.get_pixel(x, y)
            if include_transparent or pixel[3] > 0:
                pixels.append((pixel[0], pixel[1], pixel[2]))

    if not pixels:
        return Palette()

    # Initialize centroids randomly
    rng = random.Random(42)
    centroids = rng.sample(pixels, min(num_colors, len(pixels)))
    centroids = [list(c) for c in centroids]

    # K-means iterations
    for _ in range(iterations):
        # Assign pixels to nearest centroid
        clusters: List[List[Tuple[int, int, int]]] = [[] for _ in range(len(centroids))]

        for pixel in pixels:
            best_idx = 0
            best_dist = float('inf')

            for i, centroid in enumerate(centroids):
                dist = sum((pixel[j] - centroid[j]) ** 2 for j in range(3))
                if dist < best_dist:
                    best_dist = dist
                    best_idx = i

            clusters[best_idx].append(pixel)

        # Update centroids
        for i, cluster in enumerate(clusters):
            if cluster:
                centroids[i] = [
                    int(sum(p[j] for p in cluster) / len(cluster))
                    for j in range(3)
                ]

    # Create palette from centroids
    palette = Palette()
    for centroid in centroids:
        palette.add((centroid[0], centroid[1], centroid[2], 255))

    return palette


def analyze_palette(canvas: Canvas) -> PaletteAnalysis:
    """Analyze the color palette of a canvas.

    Args:
        canvas: Source canvas

    Returns:
        PaletteAnalysis with detailed color information
    """
    color_counts: Dict[Tuple[int, int, int, int], int] = {}
    total_r, total_g, total_b = 0, 0, 0
    total_pixels = 0
    min_r, max_r = 255, 0
    min_g, max_g = 255, 0
    min_b, max_b = 255, 0

    for y in range(canvas.height):
        for x in range(canvas.width):
            pixel = tuple(canvas.get_pixel(x, y))

            if pixel[3] == 0:
                continue

            total_pixels += 1
            color_counts[pixel] = color_counts.get(pixel, 0) + 1

            total_r += pixel[0]
            total_g += pixel[1]
            total_b += pixel[2]

            min_r = min(min_r, pixel[0])
            max_r = max(max_r, pixel[0])
            min_g = min(min_g, pixel[1])
            max_g = max(max_g, pixel[1])
            min_b = min(min_b, pixel[2])
            max_b = max(max_b, pixel[2])

    if total_pixels == 0:
        return PaletteAnalysis(
            colors=[],
            color_info=[],
            dominant_color=(0, 0, 0, 0),
            average_color=(0, 0, 0, 0),
            color_range={'r': (0, 0), 'g': (0, 0), 'b': (0, 0)}
        )

    # Build color info
    color_info = []
    for color, count in sorted(color_counts.items(), key=lambda x: x[1], reverse=True):
        info = ColorInfo(
            color=color,
            count=count,
            percentage=count / total_pixels * 100
        )
        color_info.append(info)

    colors = [info.color for info in color_info]
    dominant = color_info[0].color if color_info else (0, 0, 0, 0)
    average = (
        total_r // total_pixels,
        total_g // total_pixels,
        total_b // total_pixels,
        255
    )

    return PaletteAnalysis(
        colors=colors,
        color_info=color_info,
        dominant_color=dominant,
        average_color=average,
        color_range={
            'r': (min_r, max_r),
            'g': (min_g, max_g),
            'b': (min_b, max_b)
        }
    )


# ==================== Palette Remapping ====================

def remap_to_palette(canvas: Canvas, target_palette: Palette,
                    preserve_transparency: bool = True,
                    dither: bool = False) -> Canvas:
    """Remap a canvas to use only colors from target palette.

    Args:
        canvas: Source canvas
        target_palette: Target palette to map to
        preserve_transparency: Keep original alpha values
        dither: Apply dithering for smoother gradients

    Returns:
        New Canvas with remapped colors
    """
    if len(target_palette) == 0:
        return canvas.copy()

    result = Canvas(canvas.width, canvas.height)

    for y in range(canvas.height):
        for x in range(canvas.width):
            pixel = canvas.get_pixel(x, y)

            if pixel[3] == 0 and preserve_transparency:
                continue

            # Find nearest color in palette
            nearest = _find_nearest_color(pixel, target_palette)

            if preserve_transparency:
                # Keep original alpha
                new_color = (nearest[0], nearest[1], nearest[2], pixel[3])
            else:
                new_color = nearest

            if dither:
                # Simple ordered dither
                threshold = ((x % 2) + (y % 2) * 2) * 16
                # Apply error diffusion would go here for full dithering
                pass

            result.set_pixel_solid(x, y, new_color)

    return result


def remap_colors(canvas: Canvas, color_map: Dict[Tuple, Tuple],
                tolerance: int = 0) -> Canvas:
    """Remap specific colors to new colors.

    Args:
        canvas: Source canvas
        color_map: Dict mapping old colors to new colors
        tolerance: Color matching tolerance (0 = exact match)

    Returns:
        New Canvas with remapped colors
    """
    result = Canvas(canvas.width, canvas.height)

    # Normalize color map keys to tuples
    normalized_map = {}
    for old, new in color_map.items():
        old_tuple = tuple(old) if len(old) == 4 else tuple(old) + (255,)
        new_tuple = tuple(new) if len(new) == 4 else tuple(new) + (255,)
        normalized_map[old_tuple] = new_tuple

    for y in range(canvas.height):
        for x in range(canvas.width):
            pixel = tuple(canvas.get_pixel(x, y))

            if pixel in normalized_map:
                result.set_pixel_solid(x, y, normalized_map[pixel])
            elif tolerance > 0:
                # Find closest match within tolerance
                for old, new in normalized_map.items():
                    if _colors_match(pixel, old, tolerance):
                        result.set_pixel_solid(x, y, new)
                        break
                else:
                    result.set_pixel_solid(x, y, pixel)
            else:
                result.set_pixel_solid(x, y, pixel)

    return result


def reduce_colors(canvas: Canvas, max_colors: int,
                 method: str = 'popularity') -> Canvas:
    """Reduce canvas to a limited number of colors.

    Args:
        canvas: Source canvas
        max_colors: Maximum number of colors
        method: 'popularity' (keep most common) or 'kmeans' (cluster)

    Returns:
        New Canvas with reduced colors
    """
    if method == 'kmeans':
        palette = extract_palette_kmeans(canvas, max_colors)
    else:
        palette = extract_palette(canvas, max_colors)

    return remap_to_palette(canvas, palette)


# ==================== Color Matching ====================

def match_palette(source_canvas: Canvas, reference_canvas: Canvas,
                 preserve_luminance: bool = True) -> Canvas:
    """Match source canvas colors to reference canvas palette.

    Transfers the color palette from reference to source while
    preserving the source's luminance structure.

    Args:
        source_canvas: Canvas to modify
        reference_canvas: Canvas to get colors from
        preserve_luminance: Keep source luminance values

    Returns:
        New Canvas with matched colors
    """
    # Extract palettes
    source_palette = extract_palette(source_canvas, max_colors=256)
    ref_palette = extract_palette(reference_canvas, max_colors=256)

    if len(ref_palette) == 0:
        return source_canvas.copy()

    # Sort both palettes by luminance
    source_colors = sorted(
        [source_palette.get(i) for i in range(len(source_palette))],
        key=lambda c: 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]
    )
    ref_colors = sorted(
        [ref_palette.get(i) for i in range(len(ref_palette))],
        key=lambda c: 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]
    )

    # Create mapping based on luminance ranking
    color_map = {}
    for i, src_color in enumerate(source_colors):
        # Map to reference color at same relative position
        ref_idx = int(i * len(ref_colors) / len(source_colors))
        ref_idx = min(ref_idx, len(ref_colors) - 1)
        color_map[src_color] = ref_colors[ref_idx]

    return remap_colors(source_canvas, color_map, tolerance=0)


def harmonize_palettes(canvases: List[Canvas], target_size: int = 16) -> Palette:
    """Create a unified palette that works for multiple canvases.

    Args:
        canvases: List of canvases to harmonize
        target_size: Target palette size

    Returns:
        Unified Palette
    """
    # Collect all colors from all canvases
    all_colors: Dict[Tuple[int, int, int, int], int] = {}

    for canvas in canvases:
        for y in range(canvas.height):
            for x in range(canvas.width):
                pixel = tuple(canvas.get_pixel(x, y))
                if pixel[3] > 0:
                    all_colors[pixel] = all_colors.get(pixel, 0) + 1

    # Sort by frequency
    sorted_colors = sorted(all_colors.items(), key=lambda x: x[1], reverse=True)

    # Take top colors
    palette = Palette()
    for color, _ in sorted_colors[:target_size]:
        palette.add(color)

    return palette


# ==================== Utility Functions ====================

def _find_nearest_color(color: Tuple[int, int, int, int],
                       palette: Palette) -> Tuple[int, int, int, int]:
    """Find the nearest color in palette to the given color."""
    best_color = palette.get(0)
    best_dist = float('inf')

    for i in range(len(palette)):
        pal_color = palette.get(i)
        dist = color_distance_rgb(color[:3], pal_color[:3])

        if dist < best_dist:
            best_dist = dist
            best_color = pal_color

    return best_color


def _colors_match(c1: Tuple, c2: Tuple, tolerance: int) -> bool:
    """Check if two colors match within tolerance."""
    for i in range(min(len(c1), len(c2), 3)):
        if abs(c1[i] - c2[i]) > tolerance:
            return False
    return True


def create_palette_from_colors(colors: List[Tuple]) -> Palette:
    """Create a Palette from a list of colors.

    Args:
        colors: List of RGB or RGBA tuples

    Returns:
        Palette object
    """
    palette = Palette()
    for color in colors:
        if len(color) == 3:
            color = color + (255,)
        palette.add(color)
    return palette


def palette_to_image(palette: Palette, swatch_size: int = 16,
                    columns: int = 8) -> Canvas:
    """Create an image showing all colors in a palette.

    Args:
        palette: Palette to visualize
        swatch_size: Size of each color swatch
        columns: Number of columns

    Returns:
        Canvas showing the palette
    """
    count = len(palette)
    if count == 0:
        return Canvas(swatch_size, swatch_size)

    rows = (count + columns - 1) // columns
    width = columns * swatch_size
    height = rows * swatch_size

    canvas = Canvas(width, height, (40, 40, 40, 255))

    for i in range(count):
        color = palette.get(i)
        col = i % columns
        row = i // columns

        x = col * swatch_size
        y = row * swatch_size

        canvas.fill_rect(x, y, swatch_size, swatch_size, color)

    return canvas


def blend_palettes(palette1: Palette, palette2: Palette,
                  blend_factor: float = 0.5) -> Palette:
    """Blend two palettes together.

    Args:
        palette1: First palette
        palette2: Second palette
        blend_factor: 0.0 = all palette1, 1.0 = all palette2

    Returns:
        Blended Palette
    """
    result = Palette()

    max_colors = max(len(palette1), len(palette2))

    for i in range(max_colors):
        if i < len(palette1) and i < len(palette2):
            c1 = palette1.get(i)
            c2 = palette2.get(i)
            blended = (
                int(c1[0] * (1 - blend_factor) + c2[0] * blend_factor),
                int(c1[1] * (1 - blend_factor) + c2[1] * blend_factor),
                int(c1[2] * (1 - blend_factor) + c2[2] * blend_factor),
                255
            )
            result.add(blended)
        elif i < len(palette1):
            result.add(palette1.get(i))
        else:
            result.add(palette2.get(i))

    return result

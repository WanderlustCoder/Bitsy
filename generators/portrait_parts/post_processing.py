"""
Post-Processing Utilities for Anime Portraits

Provides:
- Selective anti-aliasing (silhouette only)
- Outline rendering
- Palette enforcement
"""

import math
from typing import List, Tuple, Optional, Set

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.canvas import Canvas


def apply_outline(
    canvas: Canvas,
    outline_color: Tuple[int, int, int, int] = (40, 30, 50, 255),
    thickness: int = 1
) -> None:
    """
    Apply an outline around non-transparent pixels.

    Args:
        canvas: Canvas to modify in-place
        outline_color: RGBA color for the outline
        thickness: 1 for thin, 2 for thick outline
    """
    # Collect pixels that need outline
    outline_pixels: Set[Tuple[int, int]] = set()

    # Check each transparent pixel to see if it's adjacent to opaque
    for y in range(canvas.height):
        for x in range(canvas.width):
            pixel = canvas.get_pixel(x, y)
            if pixel is None or pixel[3] < 128:
                # This is a transparent pixel - check neighbors
                has_opaque_neighbor = False
                for dy in range(-thickness, thickness + 1):
                    for dx in range(-thickness, thickness + 1):
                        if dx == 0 and dy == 0:
                            continue
                        # For thickness 1, only use 4-connectivity
                        # For thickness 2, use 8-connectivity
                        if thickness == 1 and abs(dx) + abs(dy) > 1:
                            continue
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < canvas.width and 0 <= ny < canvas.height:
                            neighbor = canvas.get_pixel(nx, ny)
                            if neighbor and neighbor[3] >= 128:
                                has_opaque_neighbor = True
                                break
                    if has_opaque_neighbor:
                        break

                if has_opaque_neighbor:
                    outline_pixels.add((x, y))

    # Apply outline
    for x, y in outline_pixels:
        canvas.set_pixel_solid(x, y, outline_color)


def apply_selective_aa(
    canvas: Canvas,
    bg_color: Tuple[int, int, int, int] = (0, 0, 0, 0)
) -> None:
    """
    Apply anti-aliasing only to silhouette edges (where sprite meets background).

    Internal edges between different colors are kept sharp for pixel art look.

    Args:
        canvas: Canvas to modify in-place
        bg_color: Background color to consider for silhouette detection
    """
    # Create copy of original pixels
    original = [[canvas.get_pixel(x, y) for x in range(canvas.width)]
                for y in range(canvas.height)]

    def is_background(pixel):
        """Check if pixel is background (transparent or matches bg_color)."""
        if pixel is None:
            return True
        if pixel[3] < 32:  # Nearly transparent
            return True
        if bg_color[3] < 32:  # If bg is transparent, only check alpha
            return False
        # Check if close to background color
        return (abs(pixel[0] - bg_color[0]) < 10 and
                abs(pixel[1] - bg_color[1]) < 10 and
                abs(pixel[2] - bg_color[2]) < 10)

    def is_silhouette_edge(x: int, y: int) -> bool:
        """Check if pixel is on the silhouette edge."""
        pixel = original[y][x]
        if is_background(pixel):
            return False

        # Check if any neighbor is background
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < canvas.width and 0 <= ny < canvas.height:
                    if is_background(original[ny][nx]):
                        return True
                else:
                    # Edge of canvas counts as silhouette
                    return True
        return False

    # Apply AA only to silhouette edges
    for y in range(canvas.height):
        for x in range(canvas.width):
            if is_silhouette_edge(x, y):
                # Blend with neighbors that are also content (not background)
                pixel = original[y][x]
                total_r, total_g, total_b, total_a = pixel
                count = 1

                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < canvas.width and 0 <= ny < canvas.height:
                            neighbor = original[ny][nx]
                            if neighbor and not is_background(neighbor):
                                # Weight diagonal neighbors less
                                weight = 0.5 if (dx != 0 and dy != 0) else 0.7
                                total_r += int(neighbor[0] * weight)
                                total_g += int(neighbor[1] * weight)
                                total_b += int(neighbor[2] * weight)
                                total_a += int(neighbor[3] * weight)
                                count += weight

                # Apply blended color
                aa_color = (
                    int(total_r / count),
                    int(total_g / count),
                    int(total_b / count),
                    int(total_a / count)
                )
                canvas.set_pixel_solid(x, y, aa_color)


def enforce_palette(
    canvas: Canvas,
    palette: List[Tuple[int, int, int, int]],
    preserve_alpha: bool = True
) -> None:
    """
    Snap all colors in canvas to nearest color in palette.

    Args:
        canvas: Canvas to modify in-place
        palette: List of allowed RGBA colors
        preserve_alpha: If True, only snap RGB, preserve original alpha
    """
    if not palette:
        return

    def find_nearest(color: Tuple[int, int, int, int]) -> Tuple[int, int, int, int]:
        """Find nearest palette color by RGB distance."""
        min_dist = float('inf')
        nearest = palette[0]

        for p_color in palette:
            dist = (
                (color[0] - p_color[0]) ** 2 +
                (color[1] - p_color[1]) ** 2 +
                (color[2] - p_color[2]) ** 2
            )
            if dist < min_dist:
                min_dist = dist
                nearest = p_color

        if preserve_alpha:
            return (nearest[0], nearest[1], nearest[2], color[3])
        return nearest

    for y in range(canvas.height):
        for x in range(canvas.width):
            pixel = canvas.get_pixel(x, y)
            if pixel and pixel[3] > 0:  # Skip fully transparent
                snapped = find_nearest(pixel)
                canvas.set_pixel_solid(x, y, snapped)


def count_colors(canvas: Canvas, min_alpha: int = 128) -> int:
    """
    Count unique colors in canvas (useful for palette verification).

    Args:
        canvas: Canvas to analyze
        min_alpha: Minimum alpha to consider a pixel

    Returns:
        Number of unique colors
    """
    colors: Set[Tuple[int, int, int, int]] = set()

    for y in range(canvas.height):
        for x in range(canvas.width):
            pixel = canvas.get_pixel(x, y)
            if pixel and pixel[3] >= min_alpha:
                colors.add(pixel)

    return len(colors)


def get_color_histogram(
    canvas: Canvas,
    min_alpha: int = 128
) -> List[Tuple[Tuple[int, int, int, int], int]]:
    """
    Get color histogram sorted by frequency.

    Args:
        canvas: Canvas to analyze
        min_alpha: Minimum alpha to consider

    Returns:
        List of (color, count) tuples sorted by count descending
    """
    from collections import Counter

    colors = []
    for y in range(canvas.height):
        for x in range(canvas.width):
            pixel = canvas.get_pixel(x, y)
            if pixel and pixel[3] >= min_alpha:
                colors.append(pixel)

    counter = Counter(colors)
    return counter.most_common()


def quantize_colors(
    canvas: Canvas,
    target_colors: int = 32,
    min_alpha: int = 128
) -> int:
    """
    Reduce canvas to target color count using median-cut quantization.

    Preserves the most used colors and merges similar rare colors.
    This maintains palette coherence while hitting color count targets.

    Args:
        canvas: Canvas to modify in-place
        target_colors: Target number of unique colors (default 32)
        min_alpha: Minimum alpha to consider for quantization

    Returns:
        Final color count after quantization
    """
    from collections import Counter

    # Get histogram - colors sorted by frequency
    histogram = get_color_histogram(canvas, min_alpha)
    if len(histogram) <= target_colors:
        return len(histogram)

    # Separate most-used colors (preserve these) from rare colors (merge these)
    # Keep top 60% of target as "protected" colors
    protected_count = int(target_colors * 0.6)
    protected_colors = set(color for color, count in histogram[:protected_count])

    # Collect rare colors to be merged
    rare_colors = [color for color, count in histogram[protected_count:]]
    remaining_slots = target_colors - protected_count

    # Use simple clustering: group rare colors by similarity
    def color_distance(c1, c2):
        return math.sqrt(
            (c1[0] - c2[0]) ** 2 +
            (c1[1] - c2[1]) ** 2 +
            (c1[2] - c2[2]) ** 2
        )

    # Build clusters using greedy approach
    clusters = []  # Each cluster: (centroid, [colors])

    for color in rare_colors:
        # Find nearest existing cluster
        best_cluster_idx = -1
        best_dist = float('inf')

        for i, (centroid, members) in enumerate(clusters):
            dist = color_distance(color, centroid)
            if dist < best_dist:
                best_dist = dist
                best_cluster_idx = i

        # Merge threshold - colors within this distance get merged
        merge_threshold = 50  # ~20% of max RGB distance

        if best_cluster_idx >= 0 and best_dist < merge_threshold:
            # Add to existing cluster
            _, members = clusters[best_cluster_idx]
            members.append(color)
            # Update centroid
            avg_r = sum(c[0] for c in members) // len(members)
            avg_g = sum(c[1] for c in members) // len(members)
            avg_b = sum(c[2] for c in members) // len(members)
            avg_a = sum(c[3] for c in members) // len(members)
            clusters[best_cluster_idx] = ((avg_r, avg_g, avg_b, avg_a), members)
        elif len(clusters) < remaining_slots:
            # Create new cluster
            clusters.append((color, [color]))
        else:
            # Force merge with nearest cluster
            if best_cluster_idx >= 0:
                _, members = clusters[best_cluster_idx]
                members.append(color)
                avg_r = sum(c[0] for c in members) // len(members)
                avg_g = sum(c[1] for c in members) // len(members)
                avg_b = sum(c[2] for c in members) // len(members)
                avg_a = sum(c[3] for c in members) // len(members)
                clusters[best_cluster_idx] = ((avg_r, avg_g, avg_b, avg_a), members)

    # Build color mapping: original color -> quantized color
    color_map = {}

    # Protected colors map to themselves
    for color in protected_colors:
        color_map[color] = color

    # Clustered colors map to their centroid
    for centroid, members in clusters:
        for color in members:
            color_map[color] = centroid

    # Apply quantization to canvas
    for y in range(canvas.height):
        for x in range(canvas.width):
            pixel = canvas.get_pixel(x, y)
            if pixel and pixel[3] >= min_alpha:
                if pixel in color_map:
                    new_color = color_map[pixel]
                    # Preserve original alpha
                    canvas.set_pixel_solid(x, y, (new_color[0], new_color[1], new_color[2], pixel[3]))

    return count_colors(canvas, min_alpha)

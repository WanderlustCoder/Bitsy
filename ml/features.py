"""
Feature extraction from pixel art sprites.

Extracts statistical features for style learning.
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from collections import Counter

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Canvas

Color = Tuple[int, int, int, int]


@dataclass
class SpriteFeatures:
    """Extracted features from a sprite."""

    # Dimensions
    width: int = 0
    height: int = 0

    # Color features
    num_colors: int = 0
    color_histogram: Dict[Color, float] = field(default_factory=dict)
    dominant_colors: List[Color] = field(default_factory=list)
    avg_brightness: float = 0.0
    avg_saturation: float = 0.0

    # Density features
    pixel_density: float = 0.0  # Non-transparent pixels / total
    quadrant_densities: List[float] = field(default_factory=list)  # 4 quadrants
    edge_density: float = 0.0  # Edge pixels / filled pixels

    # Symmetry features
    horizontal_symmetry: float = 0.0  # 0-1
    vertical_symmetry: float = 0.0  # 0-1

    # Shape features
    centroid: Tuple[float, float] = (0.0, 0.0)
    bounding_box: Tuple[int, int, int, int] = (0, 0, 0, 0)  # x, y, w, h
    aspect_ratio: float = 1.0

    def to_vector(self) -> List[float]:
        """Convert features to a flat vector for comparison."""
        vec = [
            self.num_colors / 16.0,  # Normalize
            self.avg_brightness,
            self.avg_saturation,
            self.pixel_density,
            self.edge_density,
            self.horizontal_symmetry,
            self.vertical_symmetry,
            self.aspect_ratio / 2.0,
        ]
        vec.extend(self.quadrant_densities)
        return vec


def extract_features(canvas: Canvas) -> SpriteFeatures:
    """Extract all features from a sprite canvas."""
    features = SpriteFeatures()
    features.width = canvas.width
    features.height = canvas.height

    # Collect pixel data
    pixels: List[Tuple[int, int, Color]] = []
    color_counts: Counter = Counter()

    for y in range(canvas.height):
        for x in range(canvas.width):
            color = canvas.get_pixel(x, y)
            if color and color[3] > 0:  # Non-transparent
                pixels.append((x, y, color))
                color_counts[color] += 1

    total_pixels = canvas.width * canvas.height

    if not pixels:
        return features

    # Color features
    features.num_colors = len(color_counts)
    features.color_histogram = {
        c: count / len(pixels) for c, count in color_counts.items()
    }
    features.dominant_colors = [
        c for c, _ in color_counts.most_common(5)
    ]

    # Brightness and saturation
    brightnesses = []
    saturations = []
    for _, _, color in pixels:
        r, g, b, _ = color
        brightness = (r + g + b) / (3 * 255)
        brightnesses.append(brightness)

        max_c = max(r, g, b)
        min_c = min(r, g, b)
        saturation = (max_c - min_c) / max_c if max_c > 0 else 0
        saturations.append(saturation)

    features.avg_brightness = sum(brightnesses) / len(brightnesses)
    features.avg_saturation = sum(saturations) / len(saturations)

    # Density features
    features.pixel_density = len(pixels) / total_pixels
    features.quadrant_densities = _calculate_quadrant_densities(
        pixels, canvas.width, canvas.height
    )
    features.edge_density = _calculate_edge_density(canvas, pixels)

    # Symmetry features
    features.horizontal_symmetry = _calculate_horizontal_symmetry(canvas)
    features.vertical_symmetry = _calculate_vertical_symmetry(canvas)

    # Shape features
    features.centroid = _calculate_centroid(pixels)
    features.bounding_box = _calculate_bounding_box(pixels)
    _, _, bw, bh = features.bounding_box
    features.aspect_ratio = bw / bh if bh > 0 else 1.0

    return features


def _calculate_quadrant_densities(
    pixels: List[Tuple[int, int, Color]],
    width: int,
    height: int
) -> List[float]:
    """Calculate pixel density in each quadrant."""
    mid_x = width // 2
    mid_y = height // 2

    quadrant_counts = [0, 0, 0, 0]  # TL, TR, BL, BR
    quadrant_sizes = [
        mid_x * mid_y,
        (width - mid_x) * mid_y,
        mid_x * (height - mid_y),
        (width - mid_x) * (height - mid_y)
    ]

    for x, y, _ in pixels:
        if x < mid_x:
            if y < mid_y:
                quadrant_counts[0] += 1
            else:
                quadrant_counts[2] += 1
        else:
            if y < mid_y:
                quadrant_counts[1] += 1
            else:
                quadrant_counts[3] += 1

    return [
        c / s if s > 0 else 0
        for c, s in zip(quadrant_counts, quadrant_sizes)
    ]


def _calculate_edge_density(
    canvas: Canvas,
    pixels: List[Tuple[int, int, Color]]
) -> float:
    """Calculate ratio of edge pixels to total filled pixels."""
    if not pixels:
        return 0.0

    edge_count = 0
    filled = set((x, y) for x, y, _ in pixels)

    for x, y, _ in pixels:
        # Check 4-neighbors
        is_edge = False
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if (nx, ny) not in filled:
                is_edge = True
                break
        if is_edge:
            edge_count += 1

    return edge_count / len(pixels)


def _calculate_horizontal_symmetry(canvas: Canvas) -> float:
    """Calculate horizontal symmetry score (0-1)."""
    matches = 0
    total = 0

    mid_x = canvas.width // 2

    for y in range(canvas.height):
        for x in range(mid_x):
            mirror_x = canvas.width - 1 - x
            left = canvas.get_pixel(x, y)
            right = canvas.get_pixel(mirror_x, y)

            left_filled = left and left[3] > 0
            right_filled = right and right[3] > 0

            if left_filled or right_filled:
                total += 1
                if left_filled == right_filled:
                    if not left_filled or left == right:
                        matches += 1

    return matches / total if total > 0 else 1.0


def _calculate_vertical_symmetry(canvas: Canvas) -> float:
    """Calculate vertical symmetry score (0-1)."""
    matches = 0
    total = 0

    mid_y = canvas.height // 2

    for y in range(mid_y):
        mirror_y = canvas.height - 1 - y
        for x in range(canvas.width):
            top = canvas.get_pixel(x, y)
            bottom = canvas.get_pixel(x, mirror_y)

            top_filled = top and top[3] > 0
            bottom_filled = bottom and bottom[3] > 0

            if top_filled or bottom_filled:
                total += 1
                if top_filled == bottom_filled:
                    if not top_filled or top == bottom:
                        matches += 1

    return matches / total if total > 0 else 1.0


def _calculate_centroid(
    pixels: List[Tuple[int, int, Color]]
) -> Tuple[float, float]:
    """Calculate centroid of filled pixels."""
    if not pixels:
        return (0.0, 0.0)

    sum_x = sum(x for x, _, _ in pixels)
    sum_y = sum(y for _, y, _ in pixels)
    n = len(pixels)

    return (sum_x / n, sum_y / n)


def _calculate_bounding_box(
    pixels: List[Tuple[int, int, Color]]
) -> Tuple[int, int, int, int]:
    """Calculate bounding box of filled pixels."""
    if not pixels:
        return (0, 0, 0, 0)

    xs = [x for x, _, _ in pixels]
    ys = [y for _, y, _ in pixels]

    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    return (min_x, min_y, max_x - min_x + 1, max_y - min_y + 1)


def color_distance(c1: Color, c2: Color) -> float:
    """Calculate distance between two colors (0-1)."""
    r1, g1, b1, _ = c1
    r2, g2, b2, _ = c2

    dr = (r1 - r2) / 255
    dg = (g1 - g2) / 255
    db = (b1 - b2) / 255

    return math.sqrt(dr*dr + dg*dg + db*db) / math.sqrt(3)

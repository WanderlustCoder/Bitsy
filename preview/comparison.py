"""
Comparison - Side-by-side and diff comparison tools for pixel art.

Features:
- Side-by-side comparison
- Before/after comparison
- Difference overlay visualization
- Pixel-level comparison stats
"""

import sys
import os
from typing import List, Optional, Tuple
from dataclasses import dataclass, field

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Canvas
from core.color import color_distance_weighted


@dataclass
class ComparisonResult:
    """Result of comparing two canvases."""
    identical: bool
    total_pixels: int
    different_pixels: int
    similarity_percent: float
    size_match: bool
    diff_canvas: Optional[Canvas] = None

    @property
    def difference_percent(self) -> float:
        """Percentage of pixels that differ."""
        return 100.0 - self.similarity_percent


def compare_canvases(canvas1: Canvas, canvas2: Canvas,
                     tolerance: int = 0) -> ComparisonResult:
    """
    Compare two canvases pixel-by-pixel.

    Args:
        canvas1: First canvas
        canvas2: Second canvas
        tolerance: Color difference tolerance (0 = exact match)

    Returns:
        ComparisonResult with stats and optional diff canvas
    """
    # Check size match
    size_match = (canvas1.width == canvas2.width and
                  canvas1.height == canvas2.height)

    if not size_match:
        return ComparisonResult(
            identical=False,
            total_pixels=canvas1.width * canvas1.height,
            different_pixels=canvas1.width * canvas1.height,
            similarity_percent=0.0,
            size_match=False,
            diff_canvas=None
        )

    # Compare pixels
    total_pixels = canvas1.width * canvas1.height
    different_pixels = 0

    # Create diff canvas (red = different, green = same, transparent = both transparent)
    diff_canvas = Canvas(canvas1.width, canvas1.height)

    for y in range(canvas1.height):
        for x in range(canvas1.width):
            p1 = canvas1.pixels[y][x]
            p2 = canvas2.pixels[y][x]

            # Both transparent
            if p1[3] == 0 and p2[3] == 0:
                continue

            # Check if pixels match within tolerance
            if tolerance == 0:
                match = (p1[0] == p2[0] and p1[1] == p2[1] and
                         p1[2] == p2[2] and p1[3] == p2[3])
            else:
                dist = color_distance_weighted(
                    (p1[0], p1[1], p1[2], p1[3]),
                    (p2[0], p2[1], p2[2], p2[3])
                )
                match = dist <= tolerance

            if match:
                # Same - show in green (dimmed)
                diff_canvas.pixels[y][x] = [0, 128, 0, 128]
            else:
                # Different - show in red
                different_pixels += 1
                diff_canvas.pixels[y][x] = [255, 0, 0, 255]

    similarity = ((total_pixels - different_pixels) / total_pixels * 100
                  if total_pixels > 0 else 100.0)

    return ComparisonResult(
        identical=different_pixels == 0,
        total_pixels=total_pixels,
        different_pixels=different_pixels,
        similarity_percent=similarity,
        size_match=True,
        diff_canvas=diff_canvas
    )


def create_comparison(canvas1: Canvas, canvas2: Canvas,
                      labels: Optional[Tuple[str, str]] = None,
                      padding: int = 4,
                      background: Tuple[int, int, int, int] = (40, 40, 60, 255)) -> Canvas:
    """
    Create side-by-side comparison image.

    Args:
        canvas1: First canvas (left)
        canvas2: Second canvas (right)
        labels: Optional (label1, label2) tuple
        padding: Padding between images
        background: Background color

    Returns:
        New canvas with both images side by side
    """
    # Calculate dimensions
    max_height = max(canvas1.height, canvas2.height)
    total_width = canvas1.width + padding + canvas2.width

    # Add space for labels if provided
    label_height = 10 if labels else 0
    total_height = max_height + label_height

    # Create result canvas
    result = Canvas(total_width, total_height, background)

    # Blit first canvas (vertically centered)
    y1 = label_height + (max_height - canvas1.height) // 2
    result.blit(canvas1, 0, y1)

    # Blit second canvas (vertically centered)
    x2 = canvas1.width + padding
    y2 = label_height + (max_height - canvas2.height) // 2
    result.blit(canvas2, x2, y2)

    # Add simple label indicators (colored bars) if labels provided
    if labels:
        # Label bar for first canvas
        result.fill_rect(0, 0, canvas1.width, 2, (100, 150, 255, 255))
        # Label bar for second canvas
        result.fill_rect(x2, 0, canvas2.width, 2, (255, 150, 100, 255))

    return result


def create_before_after(before: Canvas, after: Canvas,
                        padding: int = 2,
                        scale: int = 1) -> Canvas:
    """
    Create before/after comparison with visual separator.

    Args:
        before: Original canvas
        after: Modified canvas
        padding: Padding between images
        scale: Scale factor for output

    Returns:
        New canvas with before and after images
    """
    # Calculate dimensions
    max_height = max(before.height, after.height)
    separator_width = 2
    total_width = before.width + padding + separator_width + padding + after.width

    # Create result canvas with dark background
    result = Canvas(total_width, max_height, (30, 30, 40, 255))

    # Blit before (left)
    y_before = (max_height - before.height) // 2
    result.blit(before, 0, y_before)

    # Draw separator line
    separator_x = before.width + padding
    result.fill_rect(separator_x, 0, separator_width, max_height, (100, 100, 120, 255))

    # Blit after (right)
    x_after = separator_x + separator_width + padding
    y_after = (max_height - after.height) // 2
    result.blit(after, x_after, y_after)

    # Scale if requested
    if scale > 1:
        result = result.scale(scale)

    return result


def create_diff_overlay(canvas1: Canvas, canvas2: Canvas,
                        highlight_color: Tuple[int, int, int, int] = (255, 0, 0, 180),
                        tolerance: int = 0) -> Canvas:
    """
    Create an overlay showing differences between two canvases.

    Args:
        canvas1: First canvas (base)
        canvas2: Second canvas (comparison)
        highlight_color: Color to highlight differences
        tolerance: Color difference tolerance

    Returns:
        New canvas with canvas1 as base and differences highlighted
    """
    if canvas1.width != canvas2.width or canvas1.height != canvas2.height:
        raise ValueError("Canvases must have the same dimensions for diff overlay")

    # Start with copy of first canvas
    result = canvas1.copy()

    for y in range(canvas1.height):
        for x in range(canvas1.width):
            p1 = canvas1.pixels[y][x]
            p2 = canvas2.pixels[y][x]

            # Check if pixels differ
            if tolerance == 0:
                match = (p1[0] == p2[0] and p1[1] == p2[1] and
                         p1[2] == p2[2] and p1[3] == p2[3])
            else:
                dist = color_distance_weighted(
                    (p1[0], p1[1], p1[2], p1[3]),
                    (p2[0], p2[1], p2[2], p2[3])
                )
                match = dist <= tolerance

            if not match:
                # Blend highlight color over the pixel
                result.set_pixel(x, y, highlight_color)

    return result


def create_triple_comparison(original: Canvas, modified: Canvas,
                              padding: int = 4) -> Canvas:
    """
    Create a three-panel comparison: original, modified, and diff.

    Args:
        original: Original canvas
        modified: Modified canvas
        padding: Padding between panels

    Returns:
        Canvas with three panels side by side
    """
    # Generate diff
    comparison = compare_canvases(original, modified)

    # Create diff visualization if sizes match
    if comparison.size_match and comparison.diff_canvas:
        diff = comparison.diff_canvas
    else:
        # Create placeholder diff
        diff = Canvas(original.width, original.height, (128, 128, 128, 255))

    # Calculate dimensions
    max_height = max(original.height, modified.height, diff.height)
    total_width = original.width + padding + modified.width + padding + diff.width

    # Create result
    result = Canvas(total_width, max_height, (30, 30, 40, 255))

    # Blit all three
    x = 0
    for canvas in [original, modified, diff]:
        y = (max_height - canvas.height) // 2
        result.blit(canvas, x, y)
        x += canvas.width + padding

    return result


def create_grid_comparison(canvases: List[Canvas],
                           columns: int = 3,
                           padding: int = 4,
                           background: Tuple[int, int, int, int] = (40, 40, 60, 255)) -> Canvas:
    """
    Create a grid comparison of multiple canvases.

    Args:
        canvases: List of canvases to compare
        columns: Number of columns in grid
        padding: Padding between images
        background: Background color

    Returns:
        Canvas with grid layout
    """
    if not canvases:
        return Canvas(1, 1, background)

    # Find max dimensions
    max_width = max(c.width for c in canvases)
    max_height = max(c.height for c in canvases)

    # Calculate grid dimensions
    rows = (len(canvases) + columns - 1) // columns
    total_width = columns * max_width + (columns - 1) * padding
    total_height = rows * max_height + (rows - 1) * padding

    # Create result
    result = Canvas(total_width, total_height, background)

    # Place canvases in grid
    for i, canvas in enumerate(canvases):
        col = i % columns
        row = i // columns

        # Calculate position (centered in cell)
        x = col * (max_width + padding) + (max_width - canvas.width) // 2
        y = row * (max_height + padding) + (max_height - canvas.height) // 2

        result.blit(canvas, x, y)

    return result

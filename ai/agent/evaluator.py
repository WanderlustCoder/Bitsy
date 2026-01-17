"""
Quality evaluator for generated sprites.

Provides automated quality assessment based on pixel art principles
and style consistency.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Tuple
import math

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core import Canvas
from core.color import Color  # Color is a type alias for Tuple[int, int, int, int]
from ai.tools.results import QualityScore


@dataclass
class EvaluationCriteria:
    """Criteria for quality evaluation."""
    check_color_count: bool = True
    max_colors: int = 16
    check_contrast: bool = True
    min_contrast: float = 0.3
    check_coverage: bool = True
    min_coverage: float = 0.1
    max_coverage: float = 0.9
    check_symmetry: bool = False
    symmetry_threshold: float = 0.8
    check_outline: bool = True


class QualityEvaluator:
    """Evaluates the quality of generated sprites."""

    def __init__(self, criteria: Optional[EvaluationCriteria] = None):
        """Initialize evaluator.

        Args:
            criteria: Evaluation criteria to use
        """
        self.criteria = criteria or EvaluationCriteria()

    def evaluate(self, canvas: Canvas) -> QualityScore:
        """Evaluate a canvas for quality.

        Args:
            canvas: Canvas to evaluate

        Returns:
            QualityScore with component scores
        """
        scores = {}

        # Color count check
        if self.criteria.check_color_count:
            scores['color_economy'] = self._evaluate_color_count(canvas)

        # Contrast check
        if self.criteria.check_contrast:
            scores['contrast'] = self._evaluate_contrast(canvas)

        # Coverage check
        if self.criteria.check_coverage:
            scores['coverage'] = self._evaluate_coverage(canvas)

        # Symmetry check
        if self.criteria.check_symmetry:
            scores['symmetry'] = self._evaluate_symmetry(canvas)

        # Outline check
        if self.criteria.check_outline:
            scores['outline_quality'] = self._evaluate_outline(canvas)

        # Calculate overall score (weighted average)
        weights = {
            'color_economy': 0.2,
            'contrast': 0.25,
            'coverage': 0.2,
            'symmetry': 0.1,
            'outline_quality': 0.25,
        }

        total_weight = sum(weights.get(k, 0.1) for k in scores.keys())
        weighted_sum = sum(scores[k] * weights.get(k, 0.1) for k in scores.keys())
        overall = weighted_sum / total_weight if total_weight > 0 else 0.5

        return QualityScore(
            overall=overall,
            silhouette=scores.get('coverage', 0.5),
            color_harmony=scores.get('color_economy', 0.5),
            readability=scores.get('contrast', 0.5),
            detail=scores.get('outline_quality', 0.5),
        )

    def _evaluate_color_count(self, canvas: Canvas) -> float:
        """Evaluate color economy.

        Good pixel art uses limited colors efficiently.
        """
        colors = set()
        for y in range(canvas.height):
            for x in range(canvas.width):
                pixel = canvas.get_pixel(x, y)
                if pixel and pixel[3] > 0:
                    colors.add((pixel[0], pixel[1], pixel[2]))

        num_colors = len(colors)

        if num_colors == 0:
            return 0.0
        elif num_colors <= 4:
            return 1.0  # Very economical
        elif num_colors <= 8:
            return 0.9
        elif num_colors <= 16:
            return 0.8
        elif num_colors <= self.criteria.max_colors:
            return 0.6
        else:
            # Too many colors
            return max(0.1, 1.0 - (num_colors - self.criteria.max_colors) / 32)

    def _evaluate_contrast(self, canvas: Canvas) -> float:
        """Evaluate contrast between adjacent pixels."""
        contrast_samples = []

        for y in range(canvas.height):
            for x in range(canvas.width - 1):
                p1 = canvas.get_pixel(x, y)
                p2 = canvas.get_pixel(x + 1, y)
                if p1 and p2 and p1[3] > 0 and p2[3] > 0:
                    if (p1[0], p1[1], p1[2]) != (p2[0], p2[1], p2[2]):
                        contrast = self._color_contrast(p1, p2)
                        contrast_samples.append(contrast)

        if not contrast_samples:
            return 0.5

        avg_contrast = sum(contrast_samples) / len(contrast_samples)

        # Score based on whether contrast is in good range
        if avg_contrast < self.criteria.min_contrast:
            return avg_contrast / self.criteria.min_contrast
        elif avg_contrast > 0.8:
            # Too much contrast can be jarring
            return 0.8
        else:
            return min(1.0, avg_contrast + 0.2)

    def _color_contrast(self, c1: Color, c2: Color) -> float:
        """Calculate contrast between two colors."""
        # Use luminance difference
        l1 = 0.299 * c1[0] + 0.587 * c1[1] + 0.114 * c1[2]
        l2 = 0.299 * c2[0] + 0.587 * c2[1] + 0.114 * c2[2]
        return abs(l1 - l2) / 255.0

    def _evaluate_coverage(self, canvas: Canvas) -> float:
        """Evaluate how much of the canvas is used."""
        total_pixels = canvas.width * canvas.height
        filled_pixels = 0

        for y in range(canvas.height):
            for x in range(canvas.width):
                pixel = canvas.get_pixel(x, y)
                if pixel and pixel[3] > 0:
                    filled_pixels += 1

        coverage = filled_pixels / total_pixels if total_pixels > 0 else 0

        # Score based on coverage being in good range
        if coverage < self.criteria.min_coverage:
            return coverage / self.criteria.min_coverage
        elif coverage > self.criteria.max_coverage:
            return 1.0 - (coverage - self.criteria.max_coverage) / (1 - self.criteria.max_coverage)
        else:
            # Good coverage range
            return 1.0

    def _evaluate_symmetry(self, canvas: Canvas) -> float:
        """Evaluate vertical symmetry."""
        matches = 0
        total = 0
        mid_x = canvas.width // 2

        for y in range(canvas.height):
            for x in range(mid_x):
                mirror_x = canvas.width - 1 - x
                p1 = canvas.get_pixel(x, y)
                p2 = canvas.get_pixel(mirror_x, y)

                if p1 and p2:
                    total += 1
                    if self._colors_match(p1, p2):
                        matches += 1

        if total == 0:
            return 0.5

        symmetry = matches / total
        if symmetry >= self.criteria.symmetry_threshold:
            return 1.0
        else:
            return symmetry / self.criteria.symmetry_threshold

    def _colors_match(self, c1: Color, c2: Color, tolerance: int = 10) -> bool:
        """Check if two colors match within tolerance."""
        return (
            abs(c1[0] - c2[0]) <= tolerance and
            abs(c1[1] - c2[1]) <= tolerance and
            abs(c1[2] - c2[2]) <= tolerance and
            abs(c1[3] - c2[3]) <= tolerance
        )

    def _evaluate_outline(self, canvas: Canvas) -> float:
        """Evaluate outline quality."""
        # Check for consistent outline presence
        outline_pixels = 0
        edge_pixels = 0
        dark_threshold = 64

        for y in range(canvas.height):
            for x in range(canvas.width):
                pixel = canvas.get_pixel(x, y)
                if pixel and pixel[3] > 0:
                    # Check if this is an edge pixel
                    if self._is_edge_pixel(canvas, x, y):
                        edge_pixels += 1
                        # Check if it's dark (outline)
                        luminance = 0.299 * pixel[0] + 0.587 * pixel[1] + 0.114 * pixel[2]
                        if luminance < dark_threshold:
                            outline_pixels += 1

        if edge_pixels == 0:
            return 0.5

        outline_ratio = outline_pixels / edge_pixels

        # Good pixel art often has consistent outlines
        if outline_ratio > 0.7:
            return 1.0
        elif outline_ratio > 0.3:
            return 0.8
        elif outline_ratio > 0.1:
            return 0.6
        else:
            # No real outline - might be stylistic choice
            return 0.5

    def _is_edge_pixel(self, canvas: Canvas, x: int, y: int) -> bool:
        """Check if a pixel is on the edge of the sprite."""
        pixel = canvas.get_pixel(x, y)
        if not pixel or pixel[3] == 0:
            return False

        # Check 4-neighbors for transparent pixels
        neighbors = [
            (x - 1, y), (x + 1, y),
            (x, y - 1), (x, y + 1),
        ]

        for nx, ny in neighbors:
            if nx < 0 or nx >= canvas.width or ny < 0 or ny >= canvas.height:
                return True  # Canvas edge
            neighbor = canvas.get_pixel(nx, ny)
            if not neighbor or neighbor[3] == 0:
                return True

        return False


def evaluate_canvas(canvas: Canvas, criteria: Optional[EvaluationCriteria] = None) -> QualityScore:
    """Convenience function to evaluate a canvas.

    Args:
        canvas: Canvas to evaluate
        criteria: Optional evaluation criteria

    Returns:
        QualityScore
    """
    evaluator = QualityEvaluator(criteria)
    return evaluator.evaluate(canvas)


def evaluate_for_style(canvas: Canvas, reference_canvas: Canvas) -> float:
    """Evaluate how well a canvas matches a reference style.

    Args:
        canvas: Canvas to evaluate
        reference_canvas: Reference canvas for style comparison

    Returns:
        Style match score (0-1)
    """
    # Extract style features from both
    canvas_colors = _extract_color_palette(canvas)
    ref_colors = _extract_color_palette(reference_canvas)

    # Compare color palettes
    color_match = _compare_palettes(canvas_colors, ref_colors)

    # Compare coverage patterns
    canvas_coverage = _get_coverage_pattern(canvas)
    ref_coverage = _get_coverage_pattern(reference_canvas)
    coverage_match = _compare_patterns(canvas_coverage, ref_coverage)

    # Weighted combination
    return 0.6 * color_match + 0.4 * coverage_match


def _extract_color_palette(canvas: Canvas) -> List[Tuple[int, int, int]]:
    """Extract the color palette from a canvas."""
    colors = {}
    for y in range(canvas.height):
        for x in range(canvas.width):
            pixel = canvas.get_pixel(x, y)
            if pixel and pixel[3] > 0:
                key = (pixel[0], pixel[1], pixel[2])
                colors[key] = colors.get(key, 0) + 1

    # Return sorted by frequency
    sorted_colors = sorted(colors.items(), key=lambda x: -x[1])
    return [c[0] for c in sorted_colors[:16]]


def _compare_palettes(p1: List[Tuple[int, int, int]], p2: List[Tuple[int, int, int]]) -> float:
    """Compare two color palettes."""
    if not p1 or not p2:
        return 0.5

    matches = 0
    for c1 in p1[:8]:  # Compare top 8 colors
        for c2 in p2[:8]:
            if _colors_similar(c1, c2, threshold=30):
                matches += 1
                break

    return matches / min(8, len(p1))


def _colors_similar(c1: Tuple[int, int, int], c2: Tuple[int, int, int], threshold: int = 30) -> bool:
    """Check if two colors are similar."""
    return (
        abs(c1[0] - c2[0]) <= threshold and
        abs(c1[1] - c2[1]) <= threshold and
        abs(c1[2] - c2[2]) <= threshold
    )


def _get_coverage_pattern(canvas: Canvas, grid_size: int = 4) -> List[float]:
    """Get a simplified coverage pattern."""
    pattern = []
    cell_w = canvas.width // grid_size
    cell_h = canvas.height // grid_size

    for gy in range(grid_size):
        for gx in range(grid_size):
            filled = 0
            total = cell_w * cell_h
            for y in range(gy * cell_h, (gy + 1) * cell_h):
                for x in range(gx * cell_w, (gx + 1) * cell_w):
                    if x < canvas.width and y < canvas.height:
                        pixel = canvas.get_pixel(x, y)
                        if pixel and pixel[3] > 0:
                            filled += 1
            pattern.append(filled / total if total > 0 else 0)

    return pattern


def _compare_patterns(p1: List[float], p2: List[float]) -> float:
    """Compare two coverage patterns."""
    if len(p1) != len(p2):
        return 0.5

    total_diff = sum(abs(a - b) for a, b in zip(p1, p2))
    max_diff = len(p1)  # Maximum possible difference
    return 1.0 - (total_diff / max_diff) if max_diff > 0 else 0.5

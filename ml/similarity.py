"""
Style similarity comparison for sprites.

Compare sprites to determine how similar their styles are.
"""

import math
from typing import List, Optional

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Canvas
from .features import SpriteFeatures, extract_features, color_distance


def style_similarity(
    canvas1: Canvas,
    canvas2: Canvas,
    weights: Optional[List[float]] = None
) -> float:
    """Calculate style similarity between two sprites.

    Args:
        canvas1: First sprite
        canvas2: Second sprite
        weights: Optional feature weights (defaults to equal)

    Returns:
        Similarity score from 0.0 (different) to 1.0 (identical style)
    """
    f1 = extract_features(canvas1)
    f2 = extract_features(canvas2)

    return feature_similarity(f1, f2, weights)


def feature_similarity(
    f1: SpriteFeatures,
    f2: SpriteFeatures,
    weights: Optional[List[float]] = None
) -> float:
    """Calculate similarity between two feature sets."""
    v1 = f1.to_vector()
    v2 = f2.to_vector()

    if len(v1) != len(v2):
        raise ValueError("Feature vectors have different lengths")

    if weights is None:
        weights = [1.0] * len(v1)

    # Weighted Euclidean distance
    squared_diff = 0.0
    total_weight = 0.0

    for val1, val2, w in zip(v1, v2, weights):
        squared_diff += w * (val1 - val2) ** 2
        total_weight += w

    if total_weight == 0:
        return 1.0

    distance = math.sqrt(squared_diff / total_weight)

    # Convert distance to similarity (0-1)
    # Using exponential decay: similarity = e^(-distance)
    similarity = math.exp(-distance * 2)

    return similarity


def color_palette_similarity(
    canvas1: Canvas,
    canvas2: Canvas
) -> float:
    """Calculate similarity based on color palettes only."""
    f1 = extract_features(canvas1)
    f2 = extract_features(canvas2)

    if not f1.dominant_colors or not f2.dominant_colors:
        return 0.0

    # Compare dominant colors
    total_similarity = 0.0
    comparisons = 0

    for c1 in f1.dominant_colors[:3]:
        best_match = 0.0
        for c2 in f2.dominant_colors[:3]:
            dist = color_distance(c1, c2)
            match = 1.0 - dist
            best_match = max(best_match, match)
        total_similarity += best_match
        comparisons += 1

    return total_similarity / comparisons if comparisons > 0 else 0.0


def structural_similarity(
    canvas1: Canvas,
    canvas2: Canvas
) -> float:
    """Calculate structural similarity (shape, density, symmetry)."""
    f1 = extract_features(canvas1)
    f2 = extract_features(canvas2)

    # Compare structural features
    density_diff = abs(f1.pixel_density - f2.pixel_density)
    edge_diff = abs(f1.edge_density - f2.edge_density)
    h_sym_diff = abs(f1.horizontal_symmetry - f2.horizontal_symmetry)
    v_sym_diff = abs(f1.vertical_symmetry - f2.vertical_symmetry)
    aspect_diff = abs(f1.aspect_ratio - f2.aspect_ratio) / 2.0

    # Average difference
    avg_diff = (density_diff + edge_diff + h_sym_diff + v_sym_diff + aspect_diff) / 5

    return 1.0 - min(1.0, avg_diff)


def batch_similarity(
    target: Canvas,
    candidates: List[Canvas],
    top_k: int = 5
) -> List[tuple]:
    """Find most similar sprites from a list.

    Args:
        target: Target sprite to compare against
        candidates: List of candidate sprites
        top_k: Number of top matches to return

    Returns:
        List of (index, similarity) tuples, sorted by similarity
    """
    scores = []

    for i, candidate in enumerate(candidates):
        sim = style_similarity(target, candidate)
        scores.append((i, sim))

    # Sort by similarity (descending)
    scores.sort(key=lambda x: -x[1])

    return scores[:top_k]

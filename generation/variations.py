"""
Variations - Multi-generation and selection system.

Generate multiple variations of assets and select the best based on quality metrics.

Example usage:
    from generation import generate_variations, select_best
    from generators import generate_item

    # Generate 10 sword variations
    variations = generate_variations(
        lambda seed: generate_item('sword', size=32, seed=seed),
        count=10
    )

    # Select the best one
    best = select_best(variations)
    best.save('best_sword.png')
"""

import random
from typing import List, Tuple, Optional, Dict, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Canvas


class QualityCriteria(Enum):
    """Quality criteria for ranking variations."""
    DETAIL = 'detail'           # More non-transparent pixels, more colors
    CONTRAST = 'contrast'       # Good contrast between colors
    BALANCE = 'balance'         # Balanced composition
    SILHOUETTE = 'silhouette'   # Clear silhouette/shape
    COLOR_HARMONY = 'harmony'   # Colors work well together
    CLEANLINESS = 'clean'       # Few orphan pixels, clean edges
    OVERALL = 'overall'         # Combined score


@dataclass
class VariationConfig:
    """Configuration for variation generation."""
    count: int = 10             # Number of variations to generate
    seed_start: int = 0         # Starting seed
    seed_step: int = 1          # Seed increment
    parallel: bool = False      # Not used (pure Python)


@dataclass
class MutationConfig:
    """Configuration for mutation-based variations."""
    base_seed: int = 42
    mutation_rate: float = 0.2   # Probability of mutating each parameter
    mutation_amount: float = 0.3 # Amount of mutation (0-1)


@dataclass
class QualityScore:
    """Quality score for a canvas."""
    canvas: Canvas
    seed: int
    scores: Dict[str, float] = field(default_factory=dict)

    @property
    def overall(self) -> float:
        """Get overall quality score."""
        if 'overall' in self.scores:
            return self.scores['overall']
        if not self.scores:
            return 0.0
        return sum(self.scores.values()) / len(self.scores)


class QualityScorer:
    """Scores canvases based on various quality metrics."""

    def __init__(self, weights: Dict[str, float] = None):
        """Initialize scorer with optional custom weights.

        Args:
            weights: Dict mapping criteria names to weights (default equal weights)
        """
        self.weights = weights or {
            'detail': 1.0,
            'contrast': 1.0,
            'balance': 1.0,
            'silhouette': 1.0,
            'cleanliness': 1.0,
        }

    def score(self, canvas: Canvas, seed: int = 0) -> QualityScore:
        """Score a canvas on all criteria.

        Args:
            canvas: Canvas to score
            seed: Seed used to generate (for tracking)

        Returns:
            QualityScore with all metrics
        """
        scores = {}

        scores['detail'] = self._score_detail(canvas)
        scores['contrast'] = self._score_contrast(canvas)
        scores['balance'] = self._score_balance(canvas)
        scores['silhouette'] = self._score_silhouette(canvas)
        scores['cleanliness'] = self._score_cleanliness(canvas)

        # Calculate weighted overall
        total_weight = sum(self.weights.get(k, 1.0) for k in scores)
        weighted_sum = sum(
            scores[k] * self.weights.get(k, 1.0)
            for k in scores
        )
        scores['overall'] = weighted_sum / total_weight if total_weight > 0 else 0

        return QualityScore(canvas=canvas, seed=seed, scores=scores)

    def _score_detail(self, canvas: Canvas) -> float:
        """Score based on detail level (pixels and colors)."""
        opaque_count = 0
        colors = set()

        for y in range(canvas.height):
            for x in range(canvas.width):
                pixel = canvas.get_pixel(x, y)
                if pixel[3] > 0:
                    opaque_count += 1
                    colors.add(tuple(pixel))

        total = canvas.width * canvas.height

        # Coverage score (20-80% is ideal)
        coverage = opaque_count / total
        if coverage < 0.1:
            coverage_score = coverage * 5  # Penalize very sparse
        elif coverage > 0.9:
            coverage_score = 1.0 - (coverage - 0.9) * 5  # Penalize too full
        else:
            coverage_score = 0.5 + abs(coverage - 0.5)  # Prefer moderate coverage

        # Color variety score (more colors = more detail, up to a point)
        ideal_colors = min(32, canvas.width * canvas.height // 16)
        color_score = min(1.0, len(colors) / max(1, ideal_colors))

        return (coverage_score + color_score) / 2

    def _score_contrast(self, canvas: Canvas) -> float:
        """Score based on contrast between colors."""
        colors = []

        for y in range(canvas.height):
            for x in range(canvas.width):
                pixel = canvas.get_pixel(x, y)
                if pixel[3] > 128:
                    colors.append(pixel)

        if len(colors) < 2:
            return 0.5  # Can't measure contrast

        # Sample colors for efficiency
        sample_size = min(100, len(colors))
        sample = random.sample(colors, sample_size) if len(colors) > sample_size else colors

        # Calculate average contrast
        total_contrast = 0
        comparisons = 0

        for i in range(len(sample)):
            for j in range(i + 1, min(i + 10, len(sample))):  # Limit comparisons
                c1, c2 = sample[i], sample[j]
                # Luminance difference
                lum1 = 0.299 * c1[0] + 0.587 * c1[1] + 0.114 * c1[2]
                lum2 = 0.299 * c2[0] + 0.587 * c2[1] + 0.114 * c2[2]
                contrast = abs(lum1 - lum2) / 255
                total_contrast += contrast
                comparisons += 1

        if comparisons == 0:
            return 0.5

        avg_contrast = total_contrast / comparisons

        # Ideal contrast is around 0.3-0.5
        if avg_contrast < 0.1:
            return avg_contrast * 5  # Low contrast penalty
        elif avg_contrast > 0.7:
            return 1.0 - (avg_contrast - 0.7) * 2  # High contrast penalty
        else:
            return 0.7 + avg_contrast * 0.4

    def _score_balance(self, canvas: Canvas) -> float:
        """Score based on compositional balance."""
        # Calculate center of mass
        total_x, total_y, count = 0, 0, 0

        for y in range(canvas.height):
            for x in range(canvas.width):
                if canvas.get_pixel(x, y)[3] > 128:
                    total_x += x
                    total_y += y
                    count += 1

        if count == 0:
            return 0.0

        center_x = total_x / count
        center_y = total_y / count

        # Ideal center is middle of canvas
        ideal_x = canvas.width / 2
        ideal_y = canvas.height / 2

        # Distance from ideal center (normalized)
        dist_x = abs(center_x - ideal_x) / (canvas.width / 2)
        dist_y = abs(center_y - ideal_y) / (canvas.height / 2)

        # Score (closer to center = better, but slight offset is ok)
        balance = 1.0 - (dist_x + dist_y) / 2

        return max(0.0, balance)

    def _score_silhouette(self, canvas: Canvas) -> float:
        """Score based on silhouette clarity."""
        # Count edge pixels (pixels with at least one transparent neighbor)
        edge_count = 0
        interior_count = 0

        for y in range(canvas.height):
            for x in range(canvas.width):
                if canvas.get_pixel(x, y)[3] > 128:
                    # Check neighbors
                    has_transparent_neighbor = False
                    for dy in [-1, 0, 1]:
                        for dx in [-1, 0, 1]:
                            if dx == 0 and dy == 0:
                                continue
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < canvas.width and 0 <= ny < canvas.height:
                                if canvas.get_pixel(nx, ny)[3] < 128:
                                    has_transparent_neighbor = True
                                    break
                            else:
                                has_transparent_neighbor = True
                                break
                        if has_transparent_neighbor:
                            break

                    if has_transparent_neighbor:
                        edge_count += 1
                    else:
                        interior_count += 1

        total = edge_count + interior_count
        if total == 0:
            return 0.0

        # Good silhouette has clear edges relative to interior
        # Ideal ratio is around 20-40% edges
        edge_ratio = edge_count / total

        if edge_ratio < 0.1:
            return edge_ratio * 5  # Too blobby
        elif edge_ratio > 0.6:
            return 1.0 - (edge_ratio - 0.6) * 2  # Too sparse/stringy
        else:
            return 0.7 + edge_ratio

    def _score_cleanliness(self, canvas: Canvas) -> float:
        """Score based on pixel cleanliness (fewer orphans)."""
        orphan_count = 0
        total_opaque = 0

        for y in range(canvas.height):
            for x in range(canvas.width):
                if canvas.get_pixel(x, y)[3] > 128:
                    total_opaque += 1

                    # Count opaque neighbors
                    opaque_neighbors = 0
                    for dy in [-1, 0, 1]:
                        for dx in [-1, 0, 1]:
                            if dx == 0 and dy == 0:
                                continue
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < canvas.width and 0 <= ny < canvas.height:
                                if canvas.get_pixel(nx, ny)[3] > 128:
                                    opaque_neighbors += 1

                    # Orphan = pixel with 0-1 opaque neighbors
                    if opaque_neighbors <= 1:
                        orphan_count += 1

        if total_opaque == 0:
            return 0.0

        # Score based on orphan ratio (fewer = better)
        orphan_ratio = orphan_count / total_opaque

        return max(0.0, 1.0 - orphan_ratio * 2)


# ==================== Core Functions ====================

def generate_variations(generator: Callable[[int], Canvas],
                       count: int = 10,
                       seed_start: int = 0,
                       config: VariationConfig = None) -> List[Tuple[Canvas, int]]:
    """Generate multiple variations of an asset.

    Args:
        generator: Function that takes a seed and returns a Canvas
        count: Number of variations to generate
        seed_start: Starting seed value
        config: Optional VariationConfig

    Returns:
        List of (Canvas, seed) tuples
    """
    if config:
        count = config.count
        seed_start = config.seed_start
        seed_step = config.seed_step
    else:
        seed_step = 1

    variations = []

    for i in range(count):
        seed = seed_start + i * seed_step
        canvas = generator(seed)
        variations.append((canvas, seed))

    return variations


def generate_with_mutations(generator: Callable[..., Canvas],
                           base_config: Dict[str, Any],
                           mutations: Dict[str, Tuple[Any, Any]],
                           count: int = 10,
                           seed: int = 42) -> List[Tuple[Canvas, Dict[str, Any]]]:
    """Generate variations with parameter mutations.

    Args:
        generator: Generator function accepting keyword arguments
        base_config: Base configuration dict
        mutations: Dict of param -> (min_value, max_value) for mutation
        count: Number of variations
        seed: Random seed for mutation selection

    Returns:
        List of (Canvas, config_used) tuples
    """
    rng = random.Random(seed)
    variations = []

    for i in range(count):
        # Create mutated config
        config = base_config.copy()

        for param, (min_val, max_val) in mutations.items():
            if param in config:
                if isinstance(min_val, int) and isinstance(max_val, int):
                    config[param] = rng.randint(min_val, max_val)
                elif isinstance(min_val, float) or isinstance(max_val, float):
                    config[param] = rng.uniform(float(min_val), float(max_val))
                else:
                    # For non-numeric, randomly choose between options
                    config[param] = rng.choice([min_val, max_val])

        # Use different seed for each variation
        if 'seed' in config:
            config['seed'] = seed + i

        canvas = generator(**config)
        variations.append((canvas, config))

    return variations


def select_best(variations: List[Tuple[Canvas, Any]],
               criteria: Union[str, QualityCriteria] = 'overall',
               scorer: QualityScorer = None) -> Canvas:
    """Select the best variation based on quality criteria.

    Args:
        variations: List of (Canvas, metadata) tuples
        criteria: Quality criteria to use for selection
        scorer: Optional custom scorer

    Returns:
        Best Canvas
    """
    if not variations:
        raise ValueError("No variations to select from")

    if scorer is None:
        scorer = QualityScorer()

    if isinstance(criteria, QualityCriteria):
        criteria = criteria.value

    best_canvas = None
    best_score = -1

    for canvas, metadata in variations:
        seed = metadata if isinstance(metadata, int) else 0
        quality = scorer.score(canvas, seed)

        score = quality.scores.get(criteria, quality.overall)

        if score > best_score:
            best_score = score
            best_canvas = canvas

    return best_canvas


def rank_by_quality(variations: List[Tuple[Canvas, Any]],
                   criteria: Union[str, QualityCriteria] = 'overall',
                   scorer: QualityScorer = None) -> List[Tuple[Canvas, Any, float]]:
    """Rank variations by quality score.

    Args:
        variations: List of (Canvas, metadata) tuples
        criteria: Quality criteria for ranking
        scorer: Optional custom scorer

    Returns:
        List of (Canvas, metadata, score) tuples, sorted by score descending
    """
    if scorer is None:
        scorer = QualityScorer()

    if isinstance(criteria, QualityCriteria):
        criteria = criteria.value

    scored = []

    for canvas, metadata in variations:
        seed = metadata if isinstance(metadata, int) else 0
        quality = scorer.score(canvas, seed)
        score = quality.scores.get(criteria, quality.overall)
        scored.append((canvas, metadata, score))

    # Sort by score descending
    scored.sort(key=lambda x: x[2], reverse=True)

    return scored


# ==================== Batch Processing ====================

def generate_asset_set(generators: Dict[str, Callable[[int], Canvas]],
                      variations_per_asset: int = 5,
                      seed: int = 42) -> Dict[str, Canvas]:
    """Generate a complete asset set, selecting best of each.

    Args:
        generators: Dict of asset_name -> generator function
        variations_per_asset: Variations to generate per asset
        seed: Base seed

    Returns:
        Dict of asset_name -> best Canvas
    """
    result = {}
    scorer = QualityScorer()

    for i, (name, generator) in enumerate(generators.items()):
        # Generate variations with offset seed for each asset
        base_seed = seed + i * 1000
        variations = generate_variations(
            generator,
            count=variations_per_asset,
            seed_start=base_seed
        )

        # Select best
        result[name] = select_best(variations, scorer=scorer)

    return result


def batch_generate(generator: Callable[[int], Canvas],
                  count: int,
                  seed_start: int = 0,
                  output_format: str = 'list') -> Union[List[Canvas], Dict[int, Canvas]]:
    """Batch generate multiple assets.

    Args:
        generator: Generator function taking seed
        count: Number to generate
        seed_start: Starting seed
        output_format: 'list' or 'dict' (keyed by seed)

    Returns:
        List or dict of generated canvases
    """
    if output_format == 'dict':
        result = {}
        for i in range(count):
            seed = seed_start + i
            result[seed] = generator(seed)
        return result
    else:
        return [generator(seed_start + i) for i in range(count)]

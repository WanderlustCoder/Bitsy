"""
Style model for learning from example sprites.

Learns statistical patterns from examples to guide generation.
"""

import math
import random
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Set
from collections import Counter

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Canvas
from .features import SpriteFeatures, extract_features, Color


@dataclass
class StyleStatistics:
    """Statistical summary of a style."""

    # Feature means and variances
    feature_means: List[float] = field(default_factory=list)
    feature_variances: List[float] = field(default_factory=list)

    # Color palette learned from examples
    palette: List[Color] = field(default_factory=list)
    color_weights: List[float] = field(default_factory=list)

    # Target ranges
    brightness_range: Tuple[float, float] = (0.0, 1.0)
    saturation_range: Tuple[float, float] = (0.0, 1.0)
    density_range: Tuple[float, float] = (0.0, 1.0)
    symmetry_bias: float = 0.5  # 0 = asymmetric, 1 = symmetric


class StyleModel:
    """Model that learns artistic style from example sprites.

    Example:
        model = StyleModel()
        model.add_example(sprite1)
        model.add_example(sprite2)
        model.fit()

        new_sprite = model.generate(16, 16)
    """

    def __init__(self):
        """Initialize empty model."""
        self._examples: List[Canvas] = []
        self._features: List[SpriteFeatures] = []
        self._fitted = False
        self.stats = StyleStatistics()

    def add_example(self, canvas: Canvas) -> None:
        """Add an example sprite to learn from."""
        self._examples.append(canvas)
        self._features.append(extract_features(canvas))
        self._fitted = False

    def fit(self) -> None:
        """Fit the model to all added examples."""
        if not self._features:
            raise ValueError("No examples added to model")

        # Convert features to vectors
        vectors = [f.to_vector() for f in self._features]

        # Calculate means
        n_features = len(vectors[0])
        means = []
        for i in range(n_features):
            vals = [v[i] for v in vectors]
            means.append(sum(vals) / len(vals))

        # Calculate variances
        variances = []
        for i in range(n_features):
            vals = [v[i] for v in vectors]
            mean = means[i]
            var = sum((x - mean) ** 2 for x in vals) / len(vals)
            variances.append(var)

        self.stats.feature_means = means
        self.stats.feature_variances = variances

        # Build color palette from all examples
        all_colors: Counter = Counter()
        for f in self._features:
            for color, weight in f.color_histogram.items():
                all_colors[color] += weight

        # Keep top colors
        top_colors = all_colors.most_common(16)
        total = sum(w for _, w in top_colors)

        self.stats.palette = [c for c, _ in top_colors]
        self.stats.color_weights = [w / total for _, w in top_colors]

        # Calculate ranges
        brightnesses = [f.avg_brightness for f in self._features]
        saturations = [f.avg_saturation for f in self._features]
        densities = [f.pixel_density for f in self._features]
        symmetries = [
            (f.horizontal_symmetry + f.vertical_symmetry) / 2
            for f in self._features
        ]

        self.stats.brightness_range = (
            min(brightnesses) * 0.8,
            max(brightnesses) * 1.2
        )
        self.stats.saturation_range = (
            min(saturations) * 0.8,
            max(saturations) * 1.2
        )
        self.stats.density_range = (
            min(densities) * 0.8,
            min(1.0, max(densities) * 1.2)
        )
        self.stats.symmetry_bias = sum(symmetries) / len(symmetries)

        self._fitted = True

    def generate(
        self,
        width: int = 16,
        height: int = 16,
        seed: Optional[int] = None
    ) -> Canvas:
        """Generate a new sprite matching the learned style."""
        if not self._fitted:
            raise ValueError("Model not fitted. Call fit() first.")

        if seed is not None:
            random.seed(seed)

        canvas = Canvas(width, height)

        # Determine target density
        min_d, max_d = self.stats.density_range
        target_density = random.uniform(min_d, max_d)
        target_pixels = int(width * height * target_density)

        # Generate based on symmetry bias
        use_symmetry = random.random() < self.stats.symmetry_bias

        if use_symmetry:
            self._generate_symmetric(canvas, target_pixels)
        else:
            self._generate_organic(canvas, target_pixels)

        return canvas

    def _generate_symmetric(self, canvas: Canvas, target_pixels: int) -> None:
        """Generate a symmetric sprite."""
        width = canvas.width
        height = canvas.height
        half_w = (width + 1) // 2

        # Generate one half, mirror to other
        pixels_placed = 0
        attempts = 0
        max_attempts = target_pixels * 10

        while pixels_placed < target_pixels // 2 and attempts < max_attempts:
            x = random.randint(0, half_w - 1)
            y = random.randint(0, height - 1)

            if canvas.get_pixel(x, y)[3] == 0:
                color = self._pick_color()
                canvas.set_pixel(x, y, color)

                # Mirror
                mirror_x = width - 1 - x
                if mirror_x != x:
                    canvas.set_pixel(mirror_x, y, color)
                    pixels_placed += 2
                else:
                    pixels_placed += 1

            attempts += 1

    def _generate_organic(self, canvas: Canvas, target_pixels: int) -> None:
        """Generate an organic/asymmetric sprite."""
        width = canvas.width
        height = canvas.height

        # Start with some seed points
        seeds = random.randint(1, 3)
        points = []

        for _ in range(seeds):
            x = random.randint(width // 4, 3 * width // 4)
            y = random.randint(height // 4, 3 * height // 4)
            points.append((x, y))
            canvas.set_pixel(x, y, self._pick_color())

        # Grow from seeds
        pixels_placed = seeds
        attempts = 0
        max_attempts = target_pixels * 10

        while pixels_placed < target_pixels and attempts < max_attempts:
            if not points:
                break

            # Pick a random existing point
            px, py = random.choice(points)

            # Pick a neighbor
            dx = random.choice([-1, 0, 1])
            dy = random.choice([-1, 0, 1])
            nx, ny = px + dx, py + dy

            if 0 <= nx < width and 0 <= ny < height:
                if canvas.get_pixel(nx, ny)[3] == 0:
                    color = self._pick_color()
                    canvas.set_pixel(nx, ny, color)
                    points.append((nx, ny))
                    pixels_placed += 1

            attempts += 1

    def _pick_color(self) -> Color:
        """Pick a color from the learned palette."""
        if not self.stats.palette:
            return (128, 128, 128, 255)

        # Weighted random selection
        r = random.random()
        cumulative = 0.0

        for color, weight in zip(self.stats.palette, self.stats.color_weights):
            cumulative += weight
            if r <= cumulative:
                return color

        return self.stats.palette[-1]

    def is_fitted(self) -> bool:
        """Check if model has been fitted."""
        return self._fitted

    def num_examples(self) -> int:
        """Get number of examples in model."""
        return len(self._examples)

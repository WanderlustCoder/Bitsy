"""
Style-guided sprite generation.

Additional generation utilities using learned styles.
"""

import random
from typing import List, Optional, Callable

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Canvas
from .style_model import StyleModel
from .similarity import style_similarity
from .features import extract_features


def generate_variations(
    model: StyleModel,
    count: int = 5,
    width: int = 16,
    height: int = 16,
    base_seed: Optional[int] = None
) -> List[Canvas]:
    """Generate multiple variations from a style model.

    Args:
        model: Fitted StyleModel
        count: Number of variations to generate
        width: Sprite width
        height: Sprite height
        base_seed: Base seed for reproducibility

    Returns:
        List of generated sprites
    """
    variations = []

    for i in range(count):
        seed = base_seed + i if base_seed is not None else None
        sprite = model.generate(width, height, seed)
        variations.append(sprite)

    return variations


def generate_until_match(
    model: StyleModel,
    target: Canvas,
    threshold: float = 0.7,
    max_attempts: int = 100,
    width: int = 16,
    height: int = 16
) -> Optional[Canvas]:
    """Generate sprites until one matches target style.

    Args:
        model: Fitted StyleModel
        target: Target sprite to match
        threshold: Minimum similarity threshold
        max_attempts: Maximum generation attempts
        width: Sprite width
        height: Sprite height

    Returns:
        Generated sprite meeting threshold, or None
    """
    for i in range(max_attempts):
        sprite = model.generate(width, height, seed=i)
        sim = style_similarity(sprite, target)

        if sim >= threshold:
            return sprite

    return None


def generate_diverse_set(
    model: StyleModel,
    count: int = 10,
    diversity_threshold: float = 0.3,
    width: int = 16,
    height: int = 16,
    max_attempts: int = 1000
) -> List[Canvas]:
    """Generate a diverse set of sprites.

    Each sprite must be sufficiently different from existing ones.

    Args:
        model: Fitted StyleModel
        count: Number of sprites to generate
        diversity_threshold: Minimum difference required
        width: Sprite width
        height: Sprite height
        max_attempts: Maximum total attempts

    Returns:
        List of diverse sprites
    """
    sprites = []
    attempts = 0

    while len(sprites) < count and attempts < max_attempts:
        sprite = model.generate(width, height, seed=attempts)

        # Check if sufficiently different from existing
        is_diverse = True
        for existing in sprites:
            sim = style_similarity(sprite, existing)
            if sim > (1.0 - diversity_threshold):
                is_diverse = False
                break

        if is_diverse:
            sprites.append(sprite)

        attempts += 1

    return sprites


def interpolate_styles(
    model1: StyleModel,
    model2: StyleModel,
    steps: int = 5,
    width: int = 16,
    height: int = 16,
    seed: Optional[int] = None
) -> List[Canvas]:
    """Generate sprites interpolating between two styles.

    Args:
        model1: First style model
        model2: Second style model
        steps: Number of interpolation steps
        width: Sprite width
        height: Sprite height
        seed: Random seed

    Returns:
        List of sprites from model1 style to model2 style
    """
    if seed is not None:
        random.seed(seed)

    results = []

    for i in range(steps):
        # Blend factor (0 = model1, 1 = model2)
        t = i / (steps - 1) if steps > 1 else 0.5

        # Generate from both models
        s1 = model1.generate(width, height, seed=seed)
        s2 = model2.generate(width, height, seed=seed)

        # Blend the results
        blended = _blend_sprites(s1, s2, t)
        results.append(blended)

    return results


def _blend_sprites(
    sprite1: Canvas,
    sprite2: Canvas,
    t: float
) -> Canvas:
    """Blend two sprites with factor t (0-1)."""
    width = sprite1.width
    height = sprite1.height

    result = Canvas(width, height)

    for y in range(height):
        for x in range(width):
            c1 = sprite1.get_pixel(x, y)
            c2 = sprite2.get_pixel(x, y)

            # Blend based on which is filled
            a1 = c1[3] if c1 else 0
            a2 = c2[3] if c2 else 0

            if a1 > 0 and a2 > 0:
                # Both filled - blend colors
                r = int(c1[0] * (1 - t) + c2[0] * t)
                g = int(c1[1] * (1 - t) + c2[1] * t)
                b = int(c1[2] * (1 - t) + c2[2] * t)
                result.set_pixel(x, y, (r, g, b, 255))
            elif a1 > 0 and random.random() > t:
                result.set_pixel(x, y, c1)
            elif a2 > 0 and random.random() <= t:
                result.set_pixel(x, y, c2)

    return result


class StyleTransfer:
    """Transfer style from one sprite to another."""

    def __init__(self, source: Canvas):
        """Initialize with source sprite to transfer from."""
        self.source = source
        self.features = extract_features(source)
        self._model = StyleModel()
        self._model.add_example(source)
        self._model.fit()

    def transfer(
        self,
        target: Canvas,
        strength: float = 0.5
    ) -> Canvas:
        """Apply source style to target sprite.

        Args:
            target: Sprite to transform
            strength: How strongly to apply style (0-1)

        Returns:
            Transformed sprite
        """
        result = Canvas(target.width, target.height)

        # Build color mapping from target to source palette
        target_features = extract_features(target)
        color_map = self._build_color_map(
            target_features.dominant_colors,
            self.features.dominant_colors
        )

        for y in range(target.height):
            for x in range(target.width):
                color = target.get_pixel(x, y)

                if color and color[3] > 0:
                    # Map to source palette with strength
                    if color in color_map:
                        mapped = color_map[color]
                        r = int(color[0] * (1 - strength) + mapped[0] * strength)
                        g = int(color[1] * (1 - strength) + mapped[1] * strength)
                        b = int(color[2] * (1 - strength) + mapped[2] * strength)
                        result.set_pixel(x, y, (r, g, b, 255))
                    else:
                        result.set_pixel(x, y, color)

        return result

    def _build_color_map(
        self,
        from_colors: List,
        to_colors: List
    ) -> dict:
        """Build mapping from one color set to another."""
        from .features import color_distance

        mapping = {}

        for fc in from_colors:
            best_match = to_colors[0] if to_colors else fc
            best_dist = float('inf')

            for tc in to_colors:
                dist = color_distance(fc, tc)
                if dist < best_dist:
                    best_dist = dist
                    best_match = tc

            mapping[fc] = best_match

        return mapping

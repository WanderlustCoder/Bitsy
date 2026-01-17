"""
Bitsy ML - Machine learning for sprite style analysis and generation.

Learn artistic styles from example sprites and generate new sprites
matching those styles. Pure Python, no external ML libraries.

Example usage:

    # Learn from examples
    from ml import StyleModel

    model = StyleModel()
    model.add_example(sprite1)
    model.add_example(sprite2)
    model.fit()

    # Generate new sprite in learned style
    new_sprite = model.generate(width=16, height=16)

    # Compare style similarity
    from ml import style_similarity
    score = style_similarity(new_sprite, sprite1)
    print(f"Style match: {score:.2%}")

    # Extract features for analysis
    from ml import extract_features
    features = extract_features(sprite1)
    print(f"Colors: {features.num_colors}")
    print(f"Symmetry: {features.horizontal_symmetry:.2%}")
"""

from .features import (
    SpriteFeatures,
    extract_features,
    color_distance,
)

from .style_model import (
    StyleModel,
    StyleStatistics,
)

from .similarity import (
    style_similarity,
    feature_similarity,
    color_palette_similarity,
    structural_similarity,
    batch_similarity,
)

from .generator import (
    generate_variations,
    generate_until_match,
    generate_diverse_set,
    interpolate_styles,
    StyleTransfer,
)

__all__ = [
    # Features
    'SpriteFeatures',
    'extract_features',
    'color_distance',

    # Style Model
    'StyleModel',
    'StyleStatistics',

    # Similarity
    'style_similarity',
    'feature_similarity',
    'color_palette_similarity',
    'structural_similarity',
    'batch_similarity',

    # Generation
    'generate_variations',
    'generate_until_match',
    'generate_diverse_set',
    'interpolate_styles',
    'StyleTransfer',
]

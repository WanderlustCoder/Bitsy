"""
Generation - Advanced generation utilities.

Provides:
- Multi-variation generation with quality ranking
- Best asset selection based on quality metrics
- Batch generation with mutation support
"""

from .variations import (
    # Core functions
    generate_variations,
    generate_with_mutations,
    select_best,
    rank_by_quality,
    # Batch processing
    generate_asset_set,
    batch_generate,
    # Quality scoring
    QualityScorer,
    QualityCriteria,
    # Variation config
    VariationConfig,
    MutationConfig,
)

__all__ = [
    # Core functions
    'generate_variations',
    'generate_with_mutations',
    'select_best',
    'rank_by_quality',
    # Batch processing
    'generate_asset_set',
    'batch_generate',
    # Quality scoring
    'QualityScorer',
    'QualityCriteria',
    # Config
    'VariationConfig',
    'MutationConfig',
]

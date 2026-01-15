"""
Style - Style extraction and transfer system.

Provides:
- Extract style from reference art (palette, shading, outlines)
- Apply extracted styles to new sprites
- Ensure consistency across asset sets
- Style presets and templates
"""

from .transfer import (
    # Core classes
    ExtractedStyle,
    StyleEnforcer,
    # Extraction
    extract_style,
    extract_shading_style,
    extract_outline_style,
    # Application
    apply_style,
    apply_palette_style,
    apply_shading_style,
    apply_outline_style,
    # Consistency
    check_style_consistency,
    fix_style_inconsistencies,
    # Utilities
    compare_styles,
    blend_styles,
    list_style_attributes,
)

__all__ = [
    # Core classes
    'ExtractedStyle',
    'StyleEnforcer',
    # Extraction
    'extract_style',
    'extract_shading_style',
    'extract_outline_style',
    # Application
    'apply_style',
    'apply_palette_style',
    'apply_shading_style',
    'apply_outline_style',
    # Consistency
    'check_style_consistency',
    'fix_style_inconsistencies',
    # Utilities
    'compare_styles',
    'blend_styles',
    'list_style_attributes',
]

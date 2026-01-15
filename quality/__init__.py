"""
Quality - Quality assurance and validation tools for pixel art.

This module provides tools to analyze, validate, and improve pixel art quality:

- analyzer: Detect pixel issues (orphans, jaggies, banding)
- validators: Check style compliance and constraints
- color_harmony: Generate harmonious color palettes
- auto_shade: Intelligent shading and outline generation

Usage:
    from quality import (
        # Analysis
        analyze_canvas, find_orphan_pixels, find_jaggies, detect_banding,

        # Validation
        validate_style, validate_palette, check_contrast,

        # Color harmony
        generate_complementary, generate_analogous, generate_triadic,
        create_shading_ramp, suggest_accent_color,

        # Auto shading
        auto_shade, smart_outline, apply_cel_shading,
    )
"""

from .analyzer import (
    analyze_canvas,
    find_orphan_pixels,
    find_jaggies,
    detect_banding,
    check_silhouette,
    get_color_statistics,
    PixelIssue,
    QualityReport,
)

from .validators import (
    validate_style,
    validate_palette,
    check_contrast,
    check_readability,
    validate_animation,
    StyleViolation,
    ValidationReport,
)

from .color_harmony import (
    generate_complementary,
    generate_analogous,
    generate_triadic,
    generate_split_complementary,
    generate_tetradic,
    create_shading_ramp,
    optimize_palette,
    suggest_accent_color,
    HarmonyType,
)

from .auto_shade import (
    auto_shade,
    smart_outline,
    apply_cel_shading,
    detect_edges,
    add_highlights,
    add_shadows,
    EdgeMap,
)

__all__ = [
    # Analyzer
    'analyze_canvas',
    'find_orphan_pixels',
    'find_jaggies',
    'detect_banding',
    'check_silhouette',
    'get_color_statistics',
    'PixelIssue',
    'QualityReport',

    # Validators
    'validate_style',
    'validate_palette',
    'check_contrast',
    'check_readability',
    'validate_animation',
    'StyleViolation',
    'ValidationReport',

    # Color Harmony
    'generate_complementary',
    'generate_analogous',
    'generate_triadic',
    'generate_split_complementary',
    'generate_tetradic',
    'create_shading_ramp',
    'optimize_palette',
    'suggest_accent_color',
    'HarmonyType',

    # Auto Shade
    'auto_shade',
    'smart_outline',
    'apply_cel_shading',
    'detect_edges',
    'add_highlights',
    'add_shadows',
    'EdgeMap',
]

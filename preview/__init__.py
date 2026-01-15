"""
Preview Module - Visual preview and comparison tools for pixel art.

This module provides tools for:
- Generating HTML preview pages with multiple zoom levels
- Creating side-by-side comparisons
- Building contact sheets for variations
- Animation preview with playback controls

All previews are pure HTML/CSS/JS with no external dependencies,
embedding pixel art as data URIs for easy sharing.
"""

from .html_preview import (
    generate_preview_html,
    generate_preview_page,
    canvas_to_data_uri,
    PreviewOptions,
)

from .comparison import (
    create_comparison,
    create_before_after,
    create_diff_overlay,
    compare_canvases,
    ComparisonResult,
)

from .contact_sheet import (
    create_contact_sheet,
    create_labeled_sheet,
    generate_variations_preview,
    ContactSheetOptions,
)

from .animation_preview import (
    generate_animation_preview,
    create_animation_html,
    create_frame_strip,
    AnimationPreviewOptions,
)

__all__ = [
    # HTML Preview
    'generate_preview_html',
    'generate_preview_page',
    'canvas_to_data_uri',
    'PreviewOptions',
    # Comparison
    'create_comparison',
    'create_before_after',
    'create_diff_overlay',
    'compare_canvases',
    'ComparisonResult',
    # Contact Sheet
    'create_contact_sheet',
    'create_labeled_sheet',
    'generate_variations_preview',
    'ContactSheetOptions',
    # Animation Preview
    'generate_animation_preview',
    'create_animation_html',
    'create_frame_strip',
    'AnimationPreviewOptions',
]

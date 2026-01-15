"""
Bitsy Editor - Image editing and manipulation tools.

This module provides:
- PNG image loading
- Layer management with blend modes
- Color adjustments and transforms
- Batch processing utilities

Example usage:

    # Load an existing sprite
    from bitsy.editor import load_png, ImageLoader

    sprite = load_png("character.png")

    # Work with layers
    from bitsy.editor import LayerStack, BlendMode

    layers = LayerStack(32, 32)
    layers.add_layer("base", sprite)
    layers.add_layer("overlay")
    layers.set_layer_blend_mode("overlay", BlendMode.MULTIPLY)
    result = layers.flatten()

    # Apply transforms
    from bitsy.editor import adjust_hue, outline, reduce_palette

    recolored = adjust_hue(sprite, 30)  # Shift hue 30 degrees
    outlined = outline(sprite, color=(0, 0, 0, 255))
    retro = reduce_palette(sprite, max_colors=16)
"""

# Loader
from .loader import (
    # Core functions
    load_png,
    load_png_from_file,
    load_png_from_bytes,
    get_png_info,
    # High-level loader
    ImageLoader,
    # Utilities
    extract_palette,
    count_colors,
    has_transparency,
    get_bounding_box,
    trim_canvas,
    # Types
    PNGInfo,
    ColorType,
    PNGDecodeError,
)

# Layers
from .layers import (
    # Core classes
    Layer,
    LayerStack,
    LayerGroup,
    # Blend modes
    BlendMode,
    BLEND_FUNCTIONS,
    # Utilities
    create_layer_stack,
    blend_canvases,
    list_blend_modes,
)

# Palette Tools
from .palette_tools import (
    # Extraction
    extract_palette as extract_palette_advanced,
    extract_palette_kmeans,
    analyze_palette,
    # Remapping
    remap_to_palette,
    remap_colors,
    reduce_colors,
    # Matching
    match_palette,
    harmonize_palettes,
    # Utilities
    create_palette_from_colors,
    palette_to_image,
    blend_palettes,
    # Types
    ColorInfo,
    PaletteAnalysis,
)

# Transforms
from .transforms import (
    # Color adjustments
    adjust_brightness,
    adjust_contrast,
    adjust_saturation,
    adjust_hue,
    invert_colors,
    grayscale,
    sepia,
    posterize,
    # Palette operations
    extract_palette,
    reduce_palette,
    remap_palette,
    replace_color,
    # Geometric transforms
    rotate_90,
    rotate_180,
    rotate_270,
    crop,
    pad,
    tile,
    # Pixel operations
    outline,
    drop_shadow,
    glow,
    dither,
    # Batch processing
    batch_process,
    create_variations,
    create_animation_strip,
    split_animation_strip,
)

__all__ = [
    # Loader
    'load_png',
    'load_png_from_file',
    'load_png_from_bytes',
    'get_png_info',
    'ImageLoader',
    'extract_palette',
    'count_colors',
    'has_transparency',
    'get_bounding_box',
    'trim_canvas',
    'PNGInfo',
    'ColorType',
    'PNGDecodeError',

    # Layers
    'Layer',
    'LayerStack',
    'LayerGroup',
    'BlendMode',
    'BLEND_FUNCTIONS',
    'create_layer_stack',
    'blend_canvases',
    'list_blend_modes',

    # Transforms - Color
    'adjust_brightness',
    'adjust_contrast',
    'adjust_saturation',
    'adjust_hue',
    'invert_colors',
    'grayscale',
    'sepia',
    'posterize',

    # Transforms - Palette
    'reduce_palette',
    'remap_palette',
    'replace_color',

    # Transforms - Geometric
    'rotate_90',
    'rotate_180',
    'rotate_270',
    'crop',
    'pad',
    'tile',

    # Transforms - Pixel
    'outline',
    'drop_shadow',
    'glow',
    'dither',

    # Transforms - Batch
    'batch_process',
    'create_variations',
    'create_animation_strip',
    'split_animation_strip',

    # Palette Tools
    'extract_palette_advanced',
    'extract_palette_kmeans',
    'analyze_palette',
    'remap_to_palette',
    'remap_colors',
    'reduce_colors',
    'match_palette',
    'harmonize_palettes',
    'create_palette_from_colors',
    'palette_to_image',
    'blend_palettes',
    'ColorInfo',
    'PaletteAnalysis',
]

"""
Bitsy Import - Import capabilities for external assets.

This module provides:
- Aseprite file reading (.ase/.aseprite)
- Automatic sprite detection in sheets
- Reference image tracing to pixel art
- Advanced color quantization

Example usage:

    # Load an Aseprite file
    from bitsy.import_ import load_aseprite

    ase = load_aseprite("character.aseprite")
    frames = ase.get_animation("walk")

    # Detect sprites in a sheet
    from bitsy.import_ import detect_sprites

    sprites = detect_sprites(sheet_canvas)
    for sprite in sprites:
        sprite.canvas.save(f"sprite_{sprite.bounds}.png")

    # Trace a reference image
    from bitsy.import_ import trace_image

    pixel_art = trace_image(photo, width=64, colors=16)

    # Extract a palette
    from bitsy.import_ import extract_palette

    palette = extract_palette(image, colors=8)
"""

# Color quantization
from .quantize import (
    QuantizeMethod,
    QuantizeConfig,
    ColorQuantizer,
    quantize_image,
    extract_palette,
    median_cut,
    octree_quantize,
)

# Sprite detection
from .sprite_detect import (
    DetectedSprite,
    DetectionConfig,
    SpriteDetector,
    detect_sprites,
    detect_background,
    split_by_color,
    find_sprite_bounds,
)

# Image tracing
from .tracer import (
    TraceConfig,
    ImageTracer,
    trace_image,
    trace_to_palette,
    auto_pixelate,
    downsample,
)

# Aseprite reading
from .aseprite import (
    AsepriteLayer,
    AsepriteFrame,
    AsepriteCel,
    AsepriteTag,
    AsepriteFile,
    load_aseprite,
    load_aseprite_from_bytes,
)

__all__ = [
    # Quantization
    'QuantizeMethod',
    'QuantizeConfig',
    'ColorQuantizer',
    'quantize_image',
    'extract_palette',
    'median_cut',
    'octree_quantize',

    # Detection
    'DetectedSprite',
    'DetectionConfig',
    'SpriteDetector',
    'detect_sprites',
    'detect_background',
    'split_by_color',
    'find_sprite_bounds',

    # Tracing
    'TraceConfig',
    'ImageTracer',
    'trace_image',
    'trace_to_palette',
    'auto_pixelate',
    'downsample',

    # Aseprite
    'AsepriteLayer',
    'AsepriteFrame',
    'AsepriteCel',
    'AsepriteTag',
    'AsepriteFile',
    'load_aseprite',
    'load_aseprite_from_bytes',
]

"""
Bitsy Core - Foundation modules for pixel art generation.

Provides:
- PNG encoding (pure Python, no dependencies)
- Canvas with drawing primitives
- Color operations and blend modes
- Palette management with HSV operations
- Animation system with sprite sheets
- Style configurations for different art styles
- JSON spec loading for declarative generation
"""

# PNG writer (foundation)
from .png_writer import (
    create_png,
    save_png,
    create_blank_canvas,
    blend_colors,
    Color,
)

# Canvas (drawing surface)
from .canvas import (
    Canvas,
    lerp_color as canvas_lerp_color,
    hex_to_rgba as canvas_hex_to_rgba,
)

# Color operations
from .color import (
    # Type
    Color,
    # Conversion
    hex_to_rgba,
    rgba_to_hex,
    rgb_to_hsv,
    hsv_to_rgb,
    rgb_to_hsl,
    hsl_to_rgb,
    # Interpolation
    lerp_color,
    lerp_color_hsv,
    # Adjustments
    shift_hue,
    adjust_saturation,
    adjust_value,
    adjust_lightness,
    grayscale,
    invert,
    darken,
    lighten,
    with_alpha,
    premultiply_alpha,
    # Blend modes
    blend_normal,
    blend_multiply,
    blend_screen,
    blend_overlay,
    blend_soft_light,
    blend_hard_light,
    blend_color_dodge,
    blend_color_burn,
    blend_add,
    blend_subtract,
    blend_difference,
    blend,
    BLEND_MODES,
    # Dithering
    dither_threshold,
    dither_color,
    quantize_with_dither,
    BAYER_2X2,
    BAYER_4X4,
    BAYER_8X8,
    # Distance/comparison
    color_distance_rgb,
    color_distance_weighted,
    colors_similar,
    # Utilities
    color_to_float,
    float_to_color,
    # Constants
    TRANSPARENT,
    BLACK,
    WHITE,
    RED,
    GREEN,
    BLUE,
    YELLOW,
    CYAN,
    MAGENTA,
)

# Palette
from .palette import (
    Palette,
    rgba_to_hex as palette_rgba_to_hex,
)

# Animation
from .animation import (
    Animation,
    Keyframe,
)

# Style
from .style import (
    Style,
    OutlineConfig,
    ShadingConfig,
    PaletteConfig,
    get_style,
    # Presets
    CHIBI,
    RETRO_NES,
    RETRO_SNES,
    RETRO_GAMEBOY,
    MODERN_HD,
    MINIMALIST,
    SILHOUETTE,
    STYLES,
)

# Spec loader
from .spec_loader import (
    # Base
    BaseSpec,
    # Spec types
    CharacterSpec,
    AnimationSpec,
    TilesetSpec,
    EffectSpec,
    UISpec,
    ItemSpec,
    # Loading
    load_spec,
    load_specs_from_directory,
    save_spec,
    # Validation
    validate_spec,
    is_valid_spec,
)


__all__ = [
    # PNG writer
    'create_png',
    'save_png',
    'create_blank_canvas',
    'blend_colors',
    'Color',

    # Canvas
    'Canvas',

    # Color
    'hex_to_rgba',
    'rgba_to_hex',
    'rgb_to_hsv',
    'hsv_to_rgb',
    'rgb_to_hsl',
    'hsl_to_rgb',
    'lerp_color',
    'lerp_color_hsv',
    'shift_hue',
    'adjust_saturation',
    'adjust_value',
    'adjust_lightness',
    'grayscale',
    'invert',
    'darken',
    'lighten',
    'with_alpha',
    'premultiply_alpha',
    'blend_normal',
    'blend_multiply',
    'blend_screen',
    'blend_overlay',
    'blend_soft_light',
    'blend_hard_light',
    'blend_color_dodge',
    'blend_color_burn',
    'blend_add',
    'blend_subtract',
    'blend_difference',
    'blend',
    'BLEND_MODES',
    'dither_threshold',
    'dither_color',
    'quantize_with_dither',
    'BAYER_2X2',
    'BAYER_4X4',
    'BAYER_8X8',
    'color_distance_rgb',
    'color_distance_weighted',
    'colors_similar',
    'color_to_float',
    'float_to_color',
    'TRANSPARENT',
    'BLACK',
    'WHITE',
    'RED',
    'GREEN',
    'BLUE',
    'YELLOW',
    'CYAN',
    'MAGENTA',

    # Palette
    'Palette',

    # Animation
    'Animation',
    'Keyframe',

    # Style
    'Style',
    'OutlineConfig',
    'ShadingConfig',
    'PaletteConfig',
    'get_style',
    'CHIBI',
    'RETRO_NES',
    'RETRO_SNES',
    'RETRO_GAMEBOY',
    'MODERN_HD',
    'MINIMALIST',
    'SILHOUETTE',
    'STYLES',

    # Spec loader
    'BaseSpec',
    'CharacterSpec',
    'AnimationSpec',
    'TilesetSpec',
    'EffectSpec',
    'UISpec',
    'ItemSpec',
    'load_spec',
    'load_specs_from_directory',
    'save_spec',
    'validate_spec',
    'is_valid_spec',
]

__version__ = '0.2.0'

"""
Bitsy Export - Animation and sprite sheet export tools.

This module provides:
- Animated GIF export
- Animated PNG (APNG) export
- Sprite sheet and atlas packing
- Metadata export (JSON)

Example usage:

    # Export animation as GIF
    from bitsy.export import save_gif

    frames = [frame1, frame2, frame3, frame4]
    save_gif("animation.gif", frames, delays=[10, 10, 10, 10])

    # Export as APNG (better quality)
    from bitsy.export import save_apng_simple

    save_apng_simple("animation.png", frames, fps=10)

    # Create sprite atlas
    from bitsy.export import SpriteAtlas

    atlas = SpriteAtlas(max_width=256)
    atlas.add("hero", hero_sprite)
    atlas.add("enemy", enemy_sprite)
    atlas.save("sprites.png", "sprites.json")
"""

# GIF export
from .gif import (
    save_gif,
    save_gif_from_animation,
    GIFExporter,
)

# APNG export
from .apng import (
    save_apng,
    save_apng_simple,
    save_apng_from_animation,
    APNGExporter,
    frames_to_apng_bytes,
)

# Spritesheet/Atlas
from .spritesheet import (
    # Core classes
    PackedSprite,
    BinPacker,
    SpriteAtlas,
    Rect,
    # Packing functions
    pack_sprites,
    create_grid_sheet,
    create_animation_sheet,
    # Metadata
    export_atlas_json,
    load_atlas_json,
    # Utilities
    create_tileset_sheet,
    create_character_sheet,
    split_sheet,
)

__all__ = [
    # GIF
    'save_gif',
    'save_gif_from_animation',
    'GIFExporter',

    # APNG
    'save_apng',
    'save_apng_simple',
    'save_apng_from_animation',
    'APNGExporter',
    'frames_to_apng_bytes',

    # Spritesheet
    'PackedSprite',
    'BinPacker',
    'SpriteAtlas',
    'Rect',
    'pack_sprites',
    'create_grid_sheet',
    'create_animation_sheet',
    'export_atlas_json',
    'load_atlas_json',
    'create_tileset_sheet',
    'create_character_sheet',
    'split_sheet',
]

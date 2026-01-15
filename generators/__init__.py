"""
Bitsy Generators - Procedural asset generation.

Provides high-level generators for creating complete sprites
from specifications or programmatic configuration.
"""

from .character import (
    CharacterGenerator,
    CharacterConfig,
    generate_character,
)

from .item import (
    ItemGenerator,
    ItemPalette,
    generate_item,
    list_item_types,
    ITEM_GENERATORS,
)

from .creature import (
    CreatureGenerator,
    CreaturePalette,
    CreatureType,
    CreatureSize,
    generate_creature,
    generate_slime,
    generate_beast,
    generate_undead,
    generate_elemental,
    generate_insect,
    list_creature_types,
)

from .environment import (
    EnvironmentGenerator,
    SkyPalette,
    GroundPalette,
    TimeOfDay,
    WeatherType,
    TerrainType,
    generate_sky,
    generate_ground,
    generate_parallax_layers,
    generate_room_interior,
    list_terrain_types,
    list_weather_types,
)

from .prop import (
    PropGenerator,
    PropPalette,
    PropType,
    ChestState,
    generate_prop,
    generate_chest,
    generate_barrel,
    generate_crate,
    generate_furniture,
    generate_vegetation,
    list_prop_types,
)

from .structure import (
    StructureGenerator,
    StructurePalette,
    BuildingStyle,
    RoofStyle,
    DungeonTileType,
    generate_house,
    generate_castle_wall,
    generate_castle_tower,
    generate_dungeon_tile,
    generate_dungeon_tileset,
    list_building_styles,
    list_roof_styles,
    list_dungeon_tile_types,
)

__all__ = [
    # Character generation
    'CharacterGenerator',
    'CharacterConfig',
    'generate_character',
    # Item generation
    'ItemGenerator',
    'ItemPalette',
    'generate_item',
    'list_item_types',
    'ITEM_GENERATORS',
    # Creature generation
    'CreatureGenerator',
    'CreaturePalette',
    'CreatureType',
    'CreatureSize',
    'generate_creature',
    'generate_slime',
    'generate_beast',
    'generate_undead',
    'generate_elemental',
    'generate_insect',
    'list_creature_types',
    # Environment generation
    'EnvironmentGenerator',
    'SkyPalette',
    'GroundPalette',
    'TimeOfDay',
    'WeatherType',
    'TerrainType',
    'generate_sky',
    'generate_ground',
    'generate_parallax_layers',
    'generate_room_interior',
    'list_terrain_types',
    'list_weather_types',
    # Prop generation
    'PropGenerator',
    'PropPalette',
    'PropType',
    'ChestState',
    'generate_prop',
    'generate_chest',
    'generate_barrel',
    'generate_crate',
    'generate_furniture',
    'generate_vegetation',
    'list_prop_types',
    # Structure generation
    'StructureGenerator',
    'StructurePalette',
    'BuildingStyle',
    'RoofStyle',
    'DungeonTileType',
    'generate_house',
    'generate_castle_wall',
    'generate_castle_tower',
    'generate_dungeon_tile',
    'generate_dungeon_tileset',
    'list_building_styles',
    'list_roof_styles',
    'list_dungeon_tile_types',
]

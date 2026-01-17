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
    generate_creature,
    list_creature_types,
    list_slime_variants,
    CREATURE_GENERATORS,
)

from .environment import (
    EnvironmentGenerator,
    SkyPalette,
    GroundPalette,
    TimeOfDay,
    Weather,
    TerrainType,
    RoomType,
    generate_sky,
    generate_ground,
    generate_parallax,
    generate_room,
    list_time_of_day,
    list_weather,
    list_terrain_types,
    list_room_types,
)

from .prop import (
    PropGenerator,
    PropPalette,
    ChestType,
    ContainerType,
    FurnitureType,
    VegetationType,
    generate_prop,
    list_prop_types,
    list_chest_types,
    list_container_types,
    list_furniture_types,
    list_vegetation_types,
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
    generate_terrain_tileset,
    list_building_styles,
    list_roof_styles,
    list_dungeon_tile_types,
)

from .scene import (
    Scene,
    SceneLayer,
    SceneConfig,
    LightSource,
    TimeOfDay,
    WeatherType,
    create_scene,
    generate_parallax_background,
    list_times_of_day,
    list_weather_types,
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
    'generate_creature',
    'list_creature_types',
    'list_slime_variants',
    'CREATURE_GENERATORS',
    # Environment generation
    'EnvironmentGenerator',
    'SkyPalette',
    'GroundPalette',
    'TimeOfDay',
    'Weather',
    'TerrainType',
    'RoomType',
    'generate_sky',
    'generate_ground',
    'generate_parallax',
    'generate_room',
    'list_time_of_day',
    'list_weather',
    'list_terrain_types',
    'list_room_types',
    # Prop generation
    'PropGenerator',
    'PropPalette',
    'ChestType',
    'ContainerType',
    'FurnitureType',
    'VegetationType',
    'generate_prop',
    'list_prop_types',
    'list_chest_types',
    'list_container_types',
    'list_furniture_types',
    'list_vegetation_types',
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
    'generate_terrain_tileset',
    'list_building_styles',
    'list_roof_styles',
    'list_dungeon_tile_types',
    # Scene composition
    'Scene',
    'SceneLayer',
    'SceneConfig',
    'LightSource',
    'TimeOfDay',
    'WeatherType',
    'create_scene',
    'generate_parallax_background',
    'list_times_of_day',
    'list_weather_types',
]

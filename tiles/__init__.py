"""
Bitsy Tiles - Tileset and terrain generation system.

This module provides:
- AutoTile systems (16-tile simple, 47-tile blob)
- TileMap for managing tile grids
- Wang tile edge matching
- Procedural terrain generation
- Cave/dungeon generation

Example usage:

    # Create a simple autotile
    from bitsy.tiles import AutoTile16, TileConfig

    config = TileConfig(
        size=16,
        base_color=(80, 160, 80, 255),
        style='shaded'
    )
    grass = AutoTile16(config)
    grass.generate_all()
    tileset = grass.export_tileset()
    tileset.save("grass_tileset.png")

    # Create a terrain map
    from bitsy.tiles import TerrainGenerator

    terrain = TerrainGenerator(seed=42)
    terrain.add_default_biomes()
    tilemap = terrain.generate_tilemap(64, 48)
    tilemap.render().save("terrain.png")
"""

# AutoTile system
from .autotile import (
    # Constants
    NORTH, EAST, SOUTH, WEST,
    DIR_N, DIR_NE, DIR_E, DIR_SE, DIR_S, DIR_SW, DIR_W, DIR_NW,
    # Configuration
    TileConfig,
    # Base classes
    AutoTile,
    AutoTile16,
    AutoTile47,
    AutoTileRPG,
    # Utility functions
    calculate_bitmask_4,
    calculate_bitmask_8,
    bitmask_to_neighbors_4,
    bitmask_to_neighbors_8,
)

# Connections and TileMap
from .connections import (
    # Edge types
    EdgeType,
    EdgeRules,
    # Tile definitions
    TileDefinition,
    # TileMap
    TileMap,
    # Wang tiles
    WangTileSet,
    WangTileGenerator,
    WangTileMap,
)

# Terrain generation
from .terrain import (
    # Noise generators
    PerlinNoise,
    SimplexNoise,
    # Biome system
    BiomeDefinition,
    # Terrain generators
    TerrainGenerator,
    IslandGenerator,
    CaveGenerator,
)

__all__ = [
    # Autotile constants
    'NORTH', 'EAST', 'SOUTH', 'WEST',
    'DIR_N', 'DIR_NE', 'DIR_E', 'DIR_SE', 'DIR_S', 'DIR_SW', 'DIR_W', 'DIR_NW',

    # Autotile classes
    'TileConfig',
    'AutoTile',
    'AutoTile16',
    'AutoTile47',
    'AutoTileRPG',

    # Autotile utilities
    'calculate_bitmask_4',
    'calculate_bitmask_8',
    'bitmask_to_neighbors_4',
    'bitmask_to_neighbors_8',

    # Connections
    'EdgeType',
    'EdgeRules',
    'TileDefinition',
    'TileMap',

    # Wang tiles
    'WangTileSet',
    'WangTileGenerator',
    'WangTileMap',

    # Noise
    'PerlinNoise',
    'SimplexNoise',

    # Terrain
    'BiomeDefinition',
    'TerrainGenerator',
    'IslandGenerator',
    'CaveGenerator',
]

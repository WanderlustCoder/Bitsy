#!/usr/bin/env python3
"""
Tileset Demo - Demonstrates Bitsy's tileset and terrain systems.

Shows:
- 16-tile simple autotile
- 47-tile blob autotile
- TileMap with autotile rendering
- Procedural terrain generation
- Cave/dungeon generation
- Wang tile systems
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Canvas
from tiles import (
    # Autotile
    TileConfig,
    AutoTile16,
    AutoTile47,
    # TileMap
    TileMap,
    TileDefinition,
    # Terrain
    TerrainGenerator,
    IslandGenerator,
    CaveGenerator,
    PerlinNoise,
    # Wang tiles
    WangTileSet,
    WangTileGenerator,
)


def create_autotile_16_demo() -> Canvas:
    """Create a demonstration of 16-tile autotile."""
    config = TileConfig(
        size=16,
        base_color=(80, 160, 80, 255),
        highlight_color=(110, 190, 110, 255),
        shadow_color=(50, 110, 50, 255),
        edge_color=(30, 80, 30, 255),
        style='shaded'
    )

    autotile = AutoTile16(config, seed=42)
    autotile.generate_all()

    # Export as tileset (4x4 grid for 16 tiles)
    return autotile.export_tileset(columns=4)


def create_autotile_47_demo() -> Canvas:
    """Create a demonstration of 47-tile blob autotile."""
    config = TileConfig(
        size=16,
        base_color=(140, 120, 80, 255),
        highlight_color=(170, 150, 110, 255),
        shadow_color=(100, 80, 50, 255),
        edge_color=(70, 55, 35, 255),
        style='shaded'
    )

    autotile = AutoTile47(config, seed=42)
    autotile.generate_all()

    # Export as tileset (8 columns)
    return autotile.export_tileset(columns=8)


def create_tilemap_demo() -> Canvas:
    """Create a TileMap demonstration with autotiles."""
    tile_size = 16
    map_width = 20
    map_height = 15

    tilemap = TileMap(map_width, map_height, tile_size)

    # Create grass autotile
    grass_config = TileConfig(
        size=tile_size,
        base_color=(80, 160, 80, 255),
        highlight_color=(110, 190, 110, 255),
        shadow_color=(50, 110, 50, 255),
        edge_color=(30, 80, 30, 255),
        style='shaded'
    )
    grass_autotile = AutoTile47(grass_config, seed=42)
    grass_autotile.generate_all()

    # Create water autotile
    water_config = TileConfig(
        size=tile_size,
        base_color=(50, 100, 180, 255),
        highlight_color=(80, 130, 210, 255),
        shadow_color=(30, 70, 130, 255),
        edge_color=(20, 50, 100, 255),
        style='shaded'
    )
    water_autotile = AutoTile47(water_config, seed=43)
    water_autotile.generate_all()

    # Register tile types
    tilemap.register_tile(TileDefinition(
        id=1, name="grass", autotile=grass_autotile, walkable=True
    ))
    tilemap.register_tile(TileDefinition(
        id=2, name="water", autotile=water_autotile, walkable=False
    ))

    # Fill map with grass
    tilemap.fill_rect(0, 0, map_width, map_height, 1)

    # Add water features
    tilemap.fill_circle(5, 5, 3, 2)  # Pond
    tilemap.fill_rect(12, 3, 6, 2, 2)  # River segment
    tilemap.fill_rect(15, 5, 2, 8, 2)  # River continuing down

    return tilemap.render()


def create_terrain_demo() -> Canvas:
    """Create a procedural terrain demonstration."""
    terrain = TerrainGenerator(seed=12345)
    terrain.add_default_biomes()

    # Generate preview (direct pixel rendering, no autotile)
    width = 128
    height = 96

    return terrain.render_preview(width, height)


def create_island_demo() -> Canvas:
    """Create an island terrain demonstration."""
    generator = IslandGenerator(seed=42, island_size=0.6)
    generator.add_default_biomes()

    # Set island center
    width = 128
    height = 96
    generator.set_island_center(width // 2, height // 2, min(width, height) // 2)

    return generator.render_preview(width, height)


def create_cave_demo() -> Canvas:
    """Create a cave/dungeon demonstration."""
    generator = CaveGenerator(seed=42)
    generator.initial_fill = 0.45
    generator.iterations = 5

    width = 40
    height = 30
    tile_size = 8

    tilemap = generator.generate_tilemap(width, height, tile_size)
    return tilemap.render()


def create_noise_demo() -> Canvas:
    """Create a visualization of different noise settings."""
    width = 64
    height = 64
    padding = 4

    # Show 4 different noise configurations
    configs = [
        {'octaves': 1, 'label': '1 octave'},
        {'octaves': 2, 'label': '2 octaves'},
        {'octaves': 4, 'label': '4 octaves'},
        {'octaves': 6, 'label': '6 octaves'},
    ]

    cols = 2
    rows = 2

    canvas = Canvas(
        (width + padding) * cols + padding,
        (height + padding) * rows + padding,
        (30, 30, 40, 255)
    )

    noise = PerlinNoise(seed=42)

    for idx, config in enumerate(configs):
        col = idx % cols
        row = idx // cols
        x_off = padding + col * (width + padding)
        y_off = padding + row * (height + padding)

        for y in range(height):
            for x in range(width):
                value = noise.octave_noise(
                    x * 0.05, y * 0.05,
                    octaves=config['octaves']
                )
                # Normalize to grayscale
                gray = int((value + 1) * 0.5 * 255)
                gray = max(0, min(255, gray))
                canvas.set_pixel(x_off + x, y_off + y, (gray, gray, gray, 255))

    return canvas


def create_wang_tile_demo() -> Canvas:
    """Create a Wang tile demonstration."""
    tile_size = 16
    generator = WangTileGenerator(tile_size, seed=42)
    generator.set_edge_colors([
        (80, 160, 80, 255),   # Edge type 0 - grass
        (140, 120, 80, 255), # Edge type 1 - dirt
    ])

    tileset = WangTileSet(tile_size, edge_types=2)
    tileset.generate_complete_set(generator)

    # Create output canvas showing all 16 tiles
    cols = 4
    rows = 4
    padding = 2

    canvas = Canvas(
        (tile_size + padding) * cols + padding,
        (tile_size + padding) * rows + padding,
        (30, 30, 40, 255)
    )

    idx = 0
    for edges, tile in sorted(tileset.tiles.items()):
        col = idx % cols
        row = idx // cols
        x = padding + col * (tile_size + padding)
        y = padding + row * (tile_size + padding)
        canvas.blit(tile, x, y)
        idx += 1

    return canvas


def create_multi_layer_demo() -> Canvas:
    """Create a multi-layer tilemap demonstration."""
    tile_size = 16
    map_width = 16
    map_height = 12

    tilemap = TileMap(map_width, map_height, tile_size)

    # Ground layer (dirt)
    dirt_config = TileConfig(
        size=tile_size,
        base_color=(140, 120, 80, 255),
        highlight_color=(170, 150, 110, 255),
        shadow_color=(100, 80, 50, 255),
        edge_color=(70, 55, 35, 255),
    )
    dirt = AutoTile16(dirt_config, seed=1)
    dirt.generate_all()

    # Grass patches
    grass_config = TileConfig(
        size=tile_size,
        base_color=(80, 160, 80, 255),
        highlight_color=(110, 190, 110, 255),
        shadow_color=(50, 110, 50, 255),
        edge_color=(30, 80, 30, 255),
    )
    grass = AutoTile47(grass_config, seed=2)
    grass.generate_all()

    # Stone path
    stone_config = TileConfig(
        size=tile_size,
        base_color=(120, 115, 110, 255),
        highlight_color=(150, 145, 140, 255),
        shadow_color=(80, 75, 70, 255),
        edge_color=(50, 48, 45, 255),
    )
    stone = AutoTile16(stone_config, seed=3)
    stone.generate_all()

    tilemap.register_tile(TileDefinition(
        id=1, name="dirt", autotile=dirt, layer=0
    ))
    tilemap.register_tile(TileDefinition(
        id=2, name="grass", autotile=grass, layer=1
    ))
    tilemap.register_tile(TileDefinition(
        id=3, name="stone", autotile=stone, layer=2
    ))

    # Fill with dirt
    tilemap.fill_rect(0, 0, map_width, map_height, 1)

    # Add grass patches
    tilemap.fill_rect(2, 2, 5, 4, 2)
    tilemap.fill_rect(9, 6, 4, 3, 2)
    tilemap.fill_circle(12, 3, 2, 2)

    # Add stone path
    tilemap.fill_rect(0, 5, map_width, 2, 3)

    return tilemap.render()


def main():
    print("Bitsy - Tileset System Demo")
    print("=" * 40)

    # Create output directory
    output_dir = os.path.join(os.path.dirname(__file__), "..", "output")
    os.makedirs(output_dir, exist_ok=True)

    # 16-tile autotile
    print("\n1. Creating 16-tile autotile...")
    autotile_16 = create_autotile_16_demo()
    autotile_16.save(os.path.join(output_dir, "autotile_16.png"))
    autotile_16.scale(2).save(os.path.join(output_dir, "autotile_16_2x.png"))
    print("   Saved: output/autotile_16.png")

    # 47-tile blob autotile
    print("\n2. Creating 47-tile blob autotile...")
    autotile_47 = create_autotile_47_demo()
    autotile_47.save(os.path.join(output_dir, "autotile_47.png"))
    autotile_47.scale(2).save(os.path.join(output_dir, "autotile_47_2x.png"))
    print("   Saved: output/autotile_47.png")

    # TileMap demo
    print("\n3. Creating TileMap demonstration...")
    tilemap_demo = create_tilemap_demo()
    tilemap_demo.save(os.path.join(output_dir, "tilemap_demo.png"))
    tilemap_demo.scale(2).save(os.path.join(output_dir, "tilemap_demo_2x.png"))
    print("   Saved: output/tilemap_demo.png")

    # Terrain preview
    print("\n4. Creating terrain preview...")
    terrain_demo = create_terrain_demo()
    terrain_demo.save(os.path.join(output_dir, "terrain_preview.png"))
    terrain_demo.scale(2).save(os.path.join(output_dir, "terrain_preview_2x.png"))
    print("   Saved: output/terrain_preview.png")

    # Island terrain
    print("\n5. Creating island terrain...")
    island_demo = create_island_demo()
    island_demo.save(os.path.join(output_dir, "island_terrain.png"))
    island_demo.scale(2).save(os.path.join(output_dir, "island_terrain_2x.png"))
    print("   Saved: output/island_terrain.png")

    # Cave generation
    print("\n6. Creating cave dungeon...")
    cave_demo = create_cave_demo()
    cave_demo.save(os.path.join(output_dir, "cave_dungeon.png"))
    cave_demo.scale(2).save(os.path.join(output_dir, "cave_dungeon_2x.png"))
    print("   Saved: output/cave_dungeon.png")

    # Noise visualization
    print("\n7. Creating noise visualization...")
    noise_demo = create_noise_demo()
    noise_demo.save(os.path.join(output_dir, "noise_octaves.png"))
    noise_demo.scale(2).save(os.path.join(output_dir, "noise_octaves_2x.png"))
    print("   Saved: output/noise_octaves.png")

    # Wang tiles
    print("\n8. Creating Wang tile set...")
    wang_demo = create_wang_tile_demo()
    wang_demo.save(os.path.join(output_dir, "wang_tiles.png"))
    wang_demo.scale(2).save(os.path.join(output_dir, "wang_tiles_2x.png"))
    print("   Saved: output/wang_tiles.png")

    # Multi-layer tilemap
    print("\n9. Creating multi-layer tilemap...")
    multi_layer = create_multi_layer_demo()
    multi_layer.save(os.path.join(output_dir, "multi_layer_tilemap.png"))
    multi_layer.scale(2).save(os.path.join(output_dir, "multi_layer_tilemap_2x.png"))
    print("   Saved: output/multi_layer_tilemap.png")

    # Summary
    print("\n" + "=" * 40)
    print("Tileset System Summary:")
    print("  - AutoTile16: 16-tile simple autotile")
    print("  - AutoTile47: 47-tile blob autotile")
    print("  - TileMap: Grid-based tile management")
    print("  - TerrainGenerator: Noise-based terrain")
    print("  - IslandGenerator: Island landmass creation")
    print("  - CaveGenerator: Cellular automata caves")
    print("  - WangTiles: Edge-matching tilesets")

    print("\n" + "=" * 40)
    print("Done! Check the output/ directory.")


if __name__ == "__main__":
    main()

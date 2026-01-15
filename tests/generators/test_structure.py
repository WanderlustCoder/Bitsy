"""
Test Structure Generator - Tests for building and dungeon generation.

Tests:
- BuildingStyle enum
- RoofStyle enum
- DungeonTileType enum
- StructurePalette
- StructureGenerator
- generate_house
- generate_castle_wall
- generate_castle_tower
- generate_dungeon_tile
- generate_dungeon_tileset
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests.framework import TestCase, CanvasFixtures
from core import Canvas


try:
    from generators.structure import (
        BuildingStyle,
        RoofStyle,
        DungeonTileType,
        StructurePalette,
        StructureGenerator,
        generate_house,
        generate_castle_wall,
        generate_castle_tower,
        generate_dungeon_tile,
        generate_dungeon_tileset,
        list_building_styles,
        list_roof_styles,
        list_dungeon_tile_types,
    )
    STRUCTURE_AVAILABLE = True
except ImportError as e:
    STRUCTURE_AVAILABLE = False
    IMPORT_ERROR = str(e)


class TestBuildingStyle(TestCase):
    """Tests for BuildingStyle enum."""

    def test_building_styles_defined(self):
        """BuildingStyle enum has expected values."""
        self.skipUnless(STRUCTURE_AVAILABLE, "Structure module not available")

        self.assertEqual(BuildingStyle.COTTAGE.value, 'cottage')
        self.assertEqual(BuildingStyle.MEDIEVAL.value, 'medieval')
        self.assertEqual(BuildingStyle.CASTLE.value, 'castle')
        self.assertEqual(BuildingStyle.FANTASY.value, 'fantasy')
        self.assertEqual(BuildingStyle.RUSTIC.value, 'rustic')
        self.assertEqual(BuildingStyle.STONE.value, 'stone')


class TestRoofStyle(TestCase):
    """Tests for RoofStyle enum."""

    def test_roof_styles_defined(self):
        """RoofStyle enum has expected values."""
        self.skipUnless(STRUCTURE_AVAILABLE, "Structure module not available")

        self.assertEqual(RoofStyle.PEAKED.value, 'peaked')
        self.assertEqual(RoofStyle.FLAT.value, 'flat')
        self.assertEqual(RoofStyle.DOME.value, 'dome')
        self.assertEqual(RoofStyle.SLANTED.value, 'slanted')
        self.assertEqual(RoofStyle.TOWER.value, 'tower')


class TestDungeonTileType(TestCase):
    """Tests for DungeonTileType enum."""

    def test_dungeon_types_defined(self):
        """DungeonTileType enum has expected values."""
        self.skipUnless(STRUCTURE_AVAILABLE, "Structure module not available")

        self.assertEqual(DungeonTileType.FLOOR.value, 'floor')
        self.assertEqual(DungeonTileType.WALL.value, 'wall')
        self.assertEqual(DungeonTileType.CORNER.value, 'corner')
        self.assertEqual(DungeonTileType.DOOR.value, 'door')
        self.assertEqual(DungeonTileType.STAIRS.value, 'stairs')
        self.assertEqual(DungeonTileType.PIT.value, 'pit')
        self.assertEqual(DungeonTileType.PILLAR.value, 'pillar')
        self.assertEqual(DungeonTileType.TORCH.value, 'torch')


class TestStructurePalette(TestCase):
    """Tests for StructurePalette dataclass."""

    def test_palette_defaults(self):
        """StructurePalette has default colors."""
        self.skipUnless(STRUCTURE_AVAILABLE, "Structure module not available")

        palette = StructurePalette()

        self.assertEqual(len(palette.wall_base), 4)
        self.assertEqual(len(palette.roof_base), 4)
        self.assertEqual(palette.wall_base[3], 255)

    def test_palette_cottage(self):
        """StructurePalette.cottage returns warm colors."""
        self.skipUnless(STRUCTURE_AVAILABLE, "Structure module not available")

        palette = StructurePalette.cottage()

        self.assertIsInstance(palette, StructurePalette)
        # Cottage has warm tones
        self.assertGreater(palette.wall_base[0], palette.wall_base[2])

    def test_palette_stone(self):
        """StructurePalette.stone returns gray colors."""
        self.skipUnless(STRUCTURE_AVAILABLE, "Structure module not available")

        palette = StructurePalette.stone()

        self.assertIsInstance(palette, StructurePalette)
        # Stone is gray (R ~= G ~= B)
        r, g, b, _ = palette.wall_base
        self.assertLess(abs(r - g), 20)
        self.assertLess(abs(g - b), 20)

    def test_palette_castle(self):
        """StructurePalette.castle returns castle colors."""
        self.skipUnless(STRUCTURE_AVAILABLE, "Structure module not available")

        palette = StructurePalette.castle()

        self.assertIsInstance(palette, StructurePalette)

    def test_palette_dungeon(self):
        """StructurePalette.dungeon returns dark colors."""
        self.skipUnless(STRUCTURE_AVAILABLE, "Structure module not available")

        palette = StructurePalette.dungeon()

        self.assertIsInstance(palette, StructurePalette)
        # Dungeon is dark
        self.assertLess(palette.wall_base[0], 100)
        self.assertLess(palette.wall_base[1], 100)
        self.assertLess(palette.wall_base[2], 100)


class TestStructureGenerator(TestCase):
    """Tests for StructureGenerator class."""

    def test_generator_creation(self):
        """StructureGenerator can be created."""
        self.skipUnless(STRUCTURE_AVAILABLE, "Structure module not available")

        gen = StructureGenerator(seed=42)

        self.assertIsNotNone(gen)
        self.assertEqual(gen.seed, 42)

    def test_generator_deterministic(self):
        """StructureGenerator is deterministic."""
        self.skipUnless(STRUCTURE_AVAILABLE, "Structure module not available")

        gen1 = StructureGenerator(seed=42)
        gen2 = StructureGenerator(seed=42)

        house1 = gen1.generate_house(32, 32)
        house2 = gen2.generate_house(32, 32)

        self.assertCanvasEqual(house1, house2)


class TestGeneratorHouse(TestCase):
    """Tests for StructureGenerator.generate_house."""

    def test_house_basic(self):
        """generate_house creates house sprite."""
        self.skipUnless(STRUCTURE_AVAILABLE, "Structure module not available")

        gen = StructureGenerator(seed=42)
        house = gen.generate_house(48, 48)

        self.assertCanvasSize(house, 48, 48)
        self.assertCanvasNotEmpty(house)

    def test_house_cottage_style(self):
        """generate_house with cottage style."""
        self.skipUnless(STRUCTURE_AVAILABLE, "Structure module not available")

        gen = StructureGenerator(seed=42)
        house = gen.generate_house(48, 48, style='cottage')

        self.assertCanvasNotEmpty(house)

    def test_house_stone_style(self):
        """generate_house with stone style."""
        self.skipUnless(STRUCTURE_AVAILABLE, "Structure module not available")

        gen = StructureGenerator(seed=42)
        house = gen.generate_house(48, 48, style='stone')

        self.assertCanvasNotEmpty(house)

    def test_house_peaked_roof(self):
        """generate_house with peaked roof."""
        self.skipUnless(STRUCTURE_AVAILABLE, "Structure module not available")

        gen = StructureGenerator(seed=42)
        house = gen.generate_house(48, 48, roof_style='peaked')

        self.assertCanvasNotEmpty(house)

    def test_house_flat_roof(self):
        """generate_house with flat roof."""
        self.skipUnless(STRUCTURE_AVAILABLE, "Structure module not available")

        gen = StructureGenerator(seed=42)
        house = gen.generate_house(48, 48, roof_style='flat')

        self.assertCanvasNotEmpty(house)

    def test_house_slanted_roof(self):
        """generate_house with slanted roof."""
        self.skipUnless(STRUCTURE_AVAILABLE, "Structure module not available")

        gen = StructureGenerator(seed=42)
        house = gen.generate_house(48, 48, roof_style='slanted')

        self.assertCanvasNotEmpty(house)

    def test_house_no_chimney(self):
        """generate_house without chimney."""
        self.skipUnless(STRUCTURE_AVAILABLE, "Structure module not available")

        gen = StructureGenerator(seed=42)
        house = gen.generate_house(48, 48, has_chimney=False)

        self.assertCanvasNotEmpty(house)

    def test_house_multiple_windows(self):
        """generate_house with multiple windows."""
        self.skipUnless(STRUCTURE_AVAILABLE, "Structure module not available")

        gen = StructureGenerator(seed=42)
        house = gen.generate_house(64, 64, num_windows=3)

        self.assertCanvasNotEmpty(house)

    def test_house_no_windows(self):
        """generate_house without windows."""
        self.skipUnless(STRUCTURE_AVAILABLE, "Structure module not available")

        gen = StructureGenerator(seed=42)
        house = gen.generate_house(48, 48, num_windows=0)

        self.assertCanvasNotEmpty(house)

    def test_house_different_sizes(self):
        """generate_house at various sizes."""
        self.skipUnless(STRUCTURE_AVAILABLE, "Structure module not available")

        gen = StructureGenerator(seed=42)

        for size in [32, 48, 64, 96]:
            house = gen.generate_house(size, size)
            self.assertCanvasSize(house, size, size)
            self.assertCanvasNotEmpty(house)


class TestGeneratorCastleWall(TestCase):
    """Tests for StructureGenerator.generate_castle_wall."""

    def test_castle_wall_basic(self):
        """generate_castle_wall creates wall sprite."""
        self.skipUnless(STRUCTURE_AVAILABLE, "Structure module not available")

        gen = StructureGenerator(seed=42)
        wall = gen.generate_castle_wall(64, 32)

        self.assertCanvasSize(wall, 64, 32)
        self.assertCanvasNotEmpty(wall)

    def test_castle_wall_with_crenellations(self):
        """generate_castle_wall with crenellations."""
        self.skipUnless(STRUCTURE_AVAILABLE, "Structure module not available")

        gen = StructureGenerator(seed=42)
        wall = gen.generate_castle_wall(64, 32, has_crenellations=True)

        self.assertCanvasNotEmpty(wall)

    def test_castle_wall_without_crenellations(self):
        """generate_castle_wall without crenellations."""
        self.skipUnless(STRUCTURE_AVAILABLE, "Structure module not available")

        gen = StructureGenerator(seed=42)
        wall = gen.generate_castle_wall(64, 32, has_crenellations=False)

        self.assertCanvasNotEmpty(wall)

    def test_castle_wall_with_arrow_slits(self):
        """generate_castle_wall with arrow slits."""
        self.skipUnless(STRUCTURE_AVAILABLE, "Structure module not available")

        gen = StructureGenerator(seed=42)
        wall = gen.generate_castle_wall(64, 32, num_windows=3)

        self.assertCanvasNotEmpty(wall)

    def test_castle_wall_different_sizes(self):
        """generate_castle_wall at various sizes."""
        self.skipUnless(STRUCTURE_AVAILABLE, "Structure module not available")

        gen = StructureGenerator(seed=42)

        for width in [32, 64, 96]:
            wall = gen.generate_castle_wall(width, 32)
            self.assertCanvasSize(wall, width, 32)


class TestGeneratorCastleTower(TestCase):
    """Tests for StructureGenerator.generate_castle_tower."""

    def test_castle_tower_basic(self):
        """generate_castle_tower creates tower sprite."""
        self.skipUnless(STRUCTURE_AVAILABLE, "Structure module not available")

        gen = StructureGenerator(seed=42)
        tower = gen.generate_castle_tower(32, 64)

        self.assertCanvasSize(tower, 32, 64)
        self.assertCanvasNotEmpty(tower)

    def test_castle_tower_conical_roof(self):
        """generate_castle_tower with tower roof."""
        self.skipUnless(STRUCTURE_AVAILABLE, "Structure module not available")

        gen = StructureGenerator(seed=42)
        tower = gen.generate_castle_tower(32, 64, roof_style='tower')

        self.assertCanvasNotEmpty(tower)

    def test_castle_tower_flat_roof(self):
        """generate_castle_tower with flat roof."""
        self.skipUnless(STRUCTURE_AVAILABLE, "Structure module not available")

        gen = StructureGenerator(seed=42)
        tower = gen.generate_castle_tower(32, 64, roof_style='flat')

        self.assertCanvasNotEmpty(tower)

    def test_castle_tower_dome_roof(self):
        """generate_castle_tower with dome roof."""
        self.skipUnless(STRUCTURE_AVAILABLE, "Structure module not available")

        gen = StructureGenerator(seed=42)
        tower = gen.generate_castle_tower(32, 64, roof_style='dome')

        self.assertCanvasNotEmpty(tower)

    def test_castle_tower_different_sizes(self):
        """generate_castle_tower at various sizes."""
        self.skipUnless(STRUCTURE_AVAILABLE, "Structure module not available")

        gen = StructureGenerator(seed=42)

        for height in [48, 64, 80]:
            tower = gen.generate_castle_tower(32, height)
            self.assertCanvasSize(tower, 32, height)


class TestGeneratorDungeonTile(TestCase):
    """Tests for StructureGenerator.generate_dungeon_tile."""

    def test_dungeon_floor(self):
        """generate_dungeon_tile creates floor tile."""
        self.skipUnless(STRUCTURE_AVAILABLE, "Structure module not available")

        gen = StructureGenerator(seed=42)
        tile = gen.generate_dungeon_tile('floor', 16)

        self.assertCanvasSize(tile, 16, 16)
        self.assertCanvasNotEmpty(tile)

    def test_dungeon_wall(self):
        """generate_dungeon_tile creates wall tile."""
        self.skipUnless(STRUCTURE_AVAILABLE, "Structure module not available")

        gen = StructureGenerator(seed=42)
        tile = gen.generate_dungeon_tile('wall', 16)

        self.assertCanvasNotEmpty(tile)

    def test_dungeon_corner(self):
        """generate_dungeon_tile creates corner tile."""
        self.skipUnless(STRUCTURE_AVAILABLE, "Structure module not available")

        gen = StructureGenerator(seed=42)
        tile = gen.generate_dungeon_tile('corner', 16)

        self.assertCanvasNotEmpty(tile)

    def test_dungeon_door(self):
        """generate_dungeon_tile creates door tile."""
        self.skipUnless(STRUCTURE_AVAILABLE, "Structure module not available")

        gen = StructureGenerator(seed=42)
        tile = gen.generate_dungeon_tile('door', 16)

        self.assertCanvasNotEmpty(tile)

    def test_dungeon_stairs(self):
        """generate_dungeon_tile creates stairs tile."""
        self.skipUnless(STRUCTURE_AVAILABLE, "Structure module not available")

        gen = StructureGenerator(seed=42)
        tile = gen.generate_dungeon_tile('stairs', 16)

        self.assertCanvasNotEmpty(tile)

    def test_dungeon_pit(self):
        """generate_dungeon_tile creates pit tile."""
        self.skipUnless(STRUCTURE_AVAILABLE, "Structure module not available")

        gen = StructureGenerator(seed=42)
        tile = gen.generate_dungeon_tile('pit', 16)

        self.assertCanvasNotEmpty(tile)

    def test_dungeon_pillar(self):
        """generate_dungeon_tile creates pillar tile."""
        self.skipUnless(STRUCTURE_AVAILABLE, "Structure module not available")

        gen = StructureGenerator(seed=42)
        tile = gen.generate_dungeon_tile('pillar', 16)

        self.assertCanvasNotEmpty(tile)

    def test_dungeon_different_sizes(self):
        """generate_dungeon_tile at various sizes."""
        self.skipUnless(STRUCTURE_AVAILABLE, "Structure module not available")

        gen = StructureGenerator(seed=42)

        for size in [8, 16, 32]:
            tile = gen.generate_dungeon_tile('floor', size)
            self.assertCanvasSize(tile, size, size)


class TestConvenienceFunctions(TestCase):
    """Tests for convenience functions."""

    def test_generate_house_function(self):
        """generate_house convenience function works."""
        self.skipUnless(STRUCTURE_AVAILABLE, "Structure module not available")

        house = generate_house(48, 48, seed=42)

        self.assertCanvasSize(house, 48, 48)
        self.assertCanvasNotEmpty(house)

    def test_generate_house_deterministic(self):
        """generate_house is deterministic."""
        self.skipUnless(STRUCTURE_AVAILABLE, "Structure module not available")

        house1 = generate_house(48, 48, seed=42)
        house2 = generate_house(48, 48, seed=42)

        self.assertCanvasEqual(house1, house2)

    def test_generate_castle_wall_function(self):
        """generate_castle_wall convenience function works."""
        self.skipUnless(STRUCTURE_AVAILABLE, "Structure module not available")

        wall = generate_castle_wall(64, 32, seed=42)

        self.assertCanvasSize(wall, 64, 32)
        self.assertCanvasNotEmpty(wall)

    def test_generate_castle_tower_function(self):
        """generate_castle_tower convenience function works."""
        self.skipUnless(STRUCTURE_AVAILABLE, "Structure module not available")

        tower = generate_castle_tower(32, 64, seed=42)

        self.assertCanvasSize(tower, 32, 64)
        self.assertCanvasNotEmpty(tower)

    def test_generate_dungeon_tile_function(self):
        """generate_dungeon_tile convenience function works."""
        self.skipUnless(STRUCTURE_AVAILABLE, "Structure module not available")

        tile = generate_dungeon_tile('floor', 16, seed=42)

        self.assertCanvasSize(tile, 16, 16)
        self.assertCanvasNotEmpty(tile)


class TestGenerateDungeonTileset(TestCase):
    """Tests for generate_dungeon_tileset function."""

    def test_tileset_basic(self):
        """generate_dungeon_tileset creates complete set."""
        self.skipUnless(STRUCTURE_AVAILABLE, "Structure module not available")

        tileset = generate_dungeon_tileset(16, seed=42)

        self.assertIsInstance(tileset, dict)
        self.assertIn('floor', tileset)
        self.assertIn('wall', tileset)
        self.assertIn('corner', tileset)
        self.assertIn('door', tileset)
        self.assertIn('stairs', tileset)
        self.assertIn('pit', tileset)
        self.assertIn('pillar', tileset)

    def test_tileset_all_valid(self):
        """generate_dungeon_tileset all tiles are valid."""
        self.skipUnless(STRUCTURE_AVAILABLE, "Structure module not available")

        tileset = generate_dungeon_tileset(16, seed=42)

        for name, tile in tileset.items():
            self.assertIsInstance(tile, Canvas)
            self.assertCanvasSize(tile, 16, 16)
            self.assertCanvasNotEmpty(tile)

    def test_tileset_different_sizes(self):
        """generate_dungeon_tileset at various sizes."""
        self.skipUnless(STRUCTURE_AVAILABLE, "Structure module not available")

        for size in [8, 16, 32]:
            tileset = generate_dungeon_tileset(size, seed=42)
            for name, tile in tileset.items():
                self.assertCanvasSize(tile, size, size)

    def test_tileset_deterministic(self):
        """generate_dungeon_tileset is deterministic."""
        self.skipUnless(STRUCTURE_AVAILABLE, "Structure module not available")

        tileset1 = generate_dungeon_tileset(16, seed=42)
        tileset2 = generate_dungeon_tileset(16, seed=42)

        for name in tileset1:
            self.assertCanvasEqual(tileset1[name], tileset2[name])


class TestListFunctions(TestCase):
    """Tests for list_* utility functions."""

    def test_list_building_styles(self):
        """list_building_styles returns style names."""
        self.skipUnless(STRUCTURE_AVAILABLE, "Structure module not available")

        styles = list_building_styles()

        self.assertIsInstance(styles, list)
        self.assertIn('cottage', styles)
        self.assertIn('medieval', styles)
        self.assertIn('castle', styles)

    def test_list_roof_styles(self):
        """list_roof_styles returns roof names."""
        self.skipUnless(STRUCTURE_AVAILABLE, "Structure module not available")

        styles = list_roof_styles()

        self.assertIsInstance(styles, list)
        self.assertIn('peaked', styles)
        self.assertIn('flat', styles)
        self.assertIn('dome', styles)

    def test_list_dungeon_tile_types(self):
        """list_dungeon_tile_types returns tile names."""
        self.skipUnless(STRUCTURE_AVAILABLE, "Structure module not available")

        types = list_dungeon_tile_types()

        self.assertIsInstance(types, list)
        self.assertIn('floor', types)
        self.assertIn('wall', types)
        self.assertIn('door', types)
        self.assertIn('stairs', types)


class TestDifferentSeeds(TestCase):
    """Tests that different seeds produce different results."""

    def test_house_different_seeds(self):
        """Houses with different seeds differ."""
        self.skipUnless(STRUCTURE_AVAILABLE, "Structure module not available")

        house1 = generate_house(48, 48, seed=1)
        house2 = generate_house(48, 48, seed=2)

        # Check if canvases differ
        differs = False
        for y in range(house1.height):
            for x in range(house1.width):
                p1 = house1.get_pixel(x, y)
                p2 = house2.get_pixel(x, y)
                if tuple(p1) != tuple(p2):
                    differs = True
                    break
            if differs:
                break

        self.assertTrue(differs, "Different seeds should produce different results")

    def test_castle_wall_different_seeds(self):
        """Castle walls with different seeds differ."""
        self.skipUnless(STRUCTURE_AVAILABLE, "Structure module not available")

        wall1 = generate_castle_wall(64, 32, seed=1)
        wall2 = generate_castle_wall(64, 32, seed=2)

        differs = False
        for y in range(wall1.height):
            for x in range(wall1.width):
                p1 = wall1.get_pixel(x, y)
                p2 = wall2.get_pixel(x, y)
                if tuple(p1) != tuple(p2):
                    differs = True
                    break
            if differs:
                break

        self.assertTrue(differs, "Different seeds should produce different results")

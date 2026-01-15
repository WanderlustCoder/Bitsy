"""
Test Prop Generator - Tests for prop and object generation.

Tests:
- Chest generation
- Container generation
- Furniture generation
- Vegetation generation
- Decoration generation
- Palette systems
- Determinism
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests.framework import TestCase
from core import Canvas
from generators.prop import (
    PropGenerator,
    PropPalette,
    ChestType,
    ContainerType,
    FurnitureType,
    VegetationType,
    DecorationTypeEnum,
    generate_prop,
    list_prop_types,
    list_chest_types,
    list_container_types,
    list_furniture_types,
    list_vegetation_types,
    list_decoration_types,
)


class TestPropGenerator(TestCase):
    """Tests for PropGenerator class."""

    def test_constructor(self):
        """PropGenerator initializes correctly."""
        gen = PropGenerator(16, 16, seed=42)

        self.assertEqual(gen.width, 16)
        self.assertEqual(gen.height, 16)
        self.assertEqual(gen.seed, 42)

    def test_custom_dimensions(self):
        """Custom dimensions are respected."""
        gen = PropGenerator(32, 24, seed=42)

        self.assertEqual(gen.width, 32)
        self.assertEqual(gen.height, 24)

    def test_set_palette(self):
        """set_palette changes color palette."""
        gen = PropGenerator(16, 16, seed=42)
        palette = PropPalette.iron()
        result = gen.set_palette(palette)

        self.assertEqual(gen.palette, palette)
        self.assertEqual(result, gen)

    def test_set_seed(self):
        """set_seed changes random seed."""
        gen = PropGenerator(16, 16, seed=42)
        result = gen.set_seed(100)

        self.assertEqual(gen.seed, 100)
        self.assertEqual(result, gen)

    def test_generate_returns_canvas(self):
        """generate method returns Canvas."""
        gen = PropGenerator(16, 16, seed=42)
        result = gen.generate('chest')

        self.assertIsInstance(result, Canvas)

    def test_generate_unknown_defaults_to_crate(self):
        """Unknown prop type defaults to crate."""
        gen = PropGenerator(16, 16, seed=42)
        result = gen.generate('unknown_type')

        self.assertIsInstance(result, Canvas)


class TestChestGeneration(TestCase):
    """Tests for chest generation."""

    def test_wooden_chest(self):
        """Wooden chest generates."""
        gen = PropGenerator(16, 16, seed=42)
        result = gen.generate('chest', 'wooden')

        self.assertIsInstance(result, Canvas)

    def test_iron_chest(self):
        """Iron chest generates."""
        gen = PropGenerator(16, 16, seed=42)
        result = gen.generate('chest', 'iron')

        self.assertIsInstance(result, Canvas)

    def test_gold_chest(self):
        """Gold chest generates."""
        gen = PropGenerator(16, 16, seed=42)
        result = gen.generate('chest', 'gold')

        self.assertIsInstance(result, Canvas)

    def test_treasure_chest(self):
        """Treasure chest generates."""
        gen = PropGenerator(16, 16, seed=42)
        result = gen.generate('chest', 'treasure')

        self.assertIsInstance(result, Canvas)

    def test_default_chest(self):
        """Default chest generates without variant."""
        gen = PropGenerator(16, 16, seed=42)
        result = gen.generate('chest')

        self.assertIsInstance(result, Canvas)


class TestContainerGeneration(TestCase):
    """Tests for container generation."""

    def test_barrel(self):
        """Barrel generates."""
        gen = PropGenerator(16, 16, seed=42)
        result = gen.generate('barrel')

        self.assertIsInstance(result, Canvas)

    def test_crate(self):
        """Crate generates."""
        gen = PropGenerator(16, 16, seed=42)
        result = gen.generate('crate')

        self.assertIsInstance(result, Canvas)

    def test_pot(self):
        """Pot generates."""
        gen = PropGenerator(16, 16, seed=42)
        result = gen.generate('pot')

        self.assertIsInstance(result, Canvas)

    def test_vase(self):
        """Vase generates."""
        gen = PropGenerator(16, 16, seed=42)
        result = gen.generate('vase')

        self.assertIsInstance(result, Canvas)

    def test_sack(self):
        """Sack generates."""
        gen = PropGenerator(16, 16, seed=42)
        result = gen.generate('sack')

        self.assertIsInstance(result, Canvas)


class TestFurnitureGeneration(TestCase):
    """Tests for furniture generation."""

    def test_table(self):
        """Table generates."""
        gen = PropGenerator(16, 16, seed=42)
        result = gen.generate('table')

        self.assertIsInstance(result, Canvas)

    def test_chair(self):
        """Chair generates."""
        gen = PropGenerator(16, 16, seed=42)
        result = gen.generate('chair')

        self.assertIsInstance(result, Canvas)

    def test_bed(self):
        """Bed generates."""
        gen = PropGenerator(24, 16, seed=42)
        result = gen.generate('bed')

        self.assertIsInstance(result, Canvas)

    def test_bookshelf(self):
        """Bookshelf generates."""
        gen = PropGenerator(16, 24, seed=42)
        result = gen.generate('bookshelf')

        self.assertIsInstance(result, Canvas)


class TestVegetationGeneration(TestCase):
    """Tests for vegetation generation."""

    def test_tree(self):
        """Tree generates."""
        gen = PropGenerator(24, 32, seed=42)
        result = gen.generate('tree')

        self.assertIsInstance(result, Canvas)

    def test_bush(self):
        """Bush generates."""
        gen = PropGenerator(16, 16, seed=42)
        result = gen.generate('bush')

        self.assertIsInstance(result, Canvas)

    def test_flower(self):
        """Flower generates."""
        gen = PropGenerator(16, 16, seed=42)
        result = gen.generate('flower')

        self.assertIsInstance(result, Canvas)

    def test_mushroom(self):
        """Mushroom generates."""
        gen = PropGenerator(16, 16, seed=42)
        result = gen.generate('mushroom')

        self.assertIsInstance(result, Canvas)


class TestDecorationGeneration(TestCase):
    """Tests for decoration generation."""

    def test_torch(self):
        """Torch generates."""
        gen = PropGenerator(16, 16, seed=42)
        result = gen.generate('torch')

        self.assertIsInstance(result, Canvas)

    def test_candle(self):
        """Candle generates."""
        gen = PropGenerator(16, 16, seed=42)
        result = gen.generate('candle')

        self.assertIsInstance(result, Canvas)

    def test_sign(self):
        """Sign generates."""
        gen = PropGenerator(16, 16, seed=42)
        result = gen.generate('sign')

        self.assertIsInstance(result, Canvas)

    def test_gravestone(self):
        """Gravestone generates."""
        gen = PropGenerator(16, 16, seed=42)
        result = gen.generate('gravestone')

        self.assertIsInstance(result, Canvas)


class TestPropPalette(TestCase):
    """Tests for PropPalette class."""

    def test_default_palette(self):
        """Default palette has all colors."""
        palette = PropPalette()

        self.assertIsNotNone(palette.primary)
        self.assertIsNotNone(palette.secondary)
        self.assertIsNotNone(palette.highlight)
        self.assertIsNotNone(palette.shadow)
        self.assertIsNotNone(palette.accent)
        self.assertIsNotNone(palette.outline)

    def test_wood_palette(self):
        """Wood palette has brown tones."""
        palette = PropPalette.wood()

        # Brown = more red than blue
        self.assertGreater(palette.primary[0], palette.primary[2])

    def test_iron_palette(self):
        """Iron palette has gray tones."""
        palette = PropPalette.iron()

        # Gray = channels close together
        r, g, b = palette.primary[0], palette.primary[1], palette.primary[2]
        self.assertLess(abs(r - g), 20)
        self.assertLess(abs(g - b), 20)

    def test_gold_palette(self):
        """Gold palette has yellow tones."""
        palette = PropPalette.gold()

        # Yellow = high red and green
        self.assertGreater(palette.primary[0], 180)
        self.assertGreater(palette.primary[1], 140)

    def test_stone_palette(self):
        """Stone palette has gray tones."""
        palette = PropPalette.stone()

        r, g, b = palette.primary[0], palette.primary[1], palette.primary[2]
        self.assertLess(abs(r - g), 20)

    def test_plant_palette(self):
        """Plant palette has green tones."""
        palette = PropPalette.plant()

        # Green > red and blue
        self.assertGreater(palette.primary[1], palette.primary[0])
        self.assertGreater(palette.primary[1], palette.primary[2])

    def test_fabric_palette(self):
        """Fabric palette has red tones."""
        palette = PropPalette.fabric()

        # Red dominant
        self.assertGreater(palette.primary[0], palette.primary[1])
        self.assertGreater(palette.primary[0], palette.primary[2])


class TestPropEnums(TestCase):
    """Tests for prop enum types."""

    def test_chest_type_values(self):
        """ChestType enum has expected values."""
        self.assertEqual(ChestType.WOODEN.value, 'wooden')
        self.assertEqual(ChestType.IRON.value, 'iron')
        self.assertEqual(ChestType.GOLD.value, 'gold')
        self.assertEqual(ChestType.TREASURE.value, 'treasure')

    def test_container_type_values(self):
        """ContainerType enum has expected values."""
        self.assertEqual(ContainerType.BARREL.value, 'barrel')
        self.assertEqual(ContainerType.CRATE.value, 'crate')
        self.assertEqual(ContainerType.POT.value, 'pot')
        self.assertEqual(ContainerType.VASE.value, 'vase')

    def test_furniture_type_values(self):
        """FurnitureType enum has expected values."""
        self.assertEqual(FurnitureType.TABLE.value, 'table')
        self.assertEqual(FurnitureType.CHAIR.value, 'chair')
        self.assertEqual(FurnitureType.BED.value, 'bed')

    def test_vegetation_type_values(self):
        """VegetationType enum has expected values."""
        self.assertEqual(VegetationType.TREE.value, 'tree')
        self.assertEqual(VegetationType.BUSH.value, 'bush')
        self.assertEqual(VegetationType.FLOWER.value, 'flower')

    def test_decoration_type_values(self):
        """DecorationTypeEnum has expected values."""
        self.assertEqual(DecorationTypeEnum.TORCH.value, 'torch')
        self.assertEqual(DecorationTypeEnum.CANDLE.value, 'candle')
        self.assertEqual(DecorationTypeEnum.SIGN.value, 'sign')


class TestConvenienceFunctions(TestCase):
    """Tests for module-level convenience functions."""

    def test_generate_prop_function(self):
        """generate_prop convenience function works."""
        result = generate_prop('chest', 'wooden', 16, 16, 42)

        self.assertIsInstance(result, Canvas)
        self.assertEqual(result.width, 16)
        self.assertEqual(result.height, 16)

    def test_generate_prop_custom_size(self):
        """generate_prop with custom dimensions."""
        result = generate_prop('tree', None, 32, 48, 42)

        self.assertEqual(result.width, 32)
        self.assertEqual(result.height, 48)

    def test_list_prop_types(self):
        """list_prop_types returns all types."""
        types = list_prop_types()

        self.assertIn('chest', types)
        self.assertIn('barrel', types)
        self.assertIn('table', types)
        self.assertIn('tree', types)
        self.assertIn('torch', types)

    def test_list_chest_types(self):
        """list_chest_types returns all chest types."""
        types = list_chest_types()

        self.assertIn('wooden', types)
        self.assertIn('iron', types)
        self.assertIn('gold', types)

    def test_list_container_types(self):
        """list_container_types returns all container types."""
        types = list_container_types()

        self.assertIn('barrel', types)
        self.assertIn('crate', types)
        self.assertIn('pot', types)

    def test_list_furniture_types(self):
        """list_furniture_types returns all furniture types."""
        types = list_furniture_types()

        self.assertIn('table', types)
        self.assertIn('chair', types)
        self.assertIn('bed', types)

    def test_list_vegetation_types(self):
        """list_vegetation_types returns all vegetation types."""
        types = list_vegetation_types()

        self.assertIn('tree', types)
        self.assertIn('bush', types)
        self.assertIn('flower', types)

    def test_list_decoration_types(self):
        """list_decoration_types returns all decoration types."""
        types = list_decoration_types()

        self.assertIn('torch', types)
        self.assertIn('candle', types)
        self.assertIn('sign', types)


class TestDeterminism(TestCase):
    """Tests for deterministic generation."""

    def test_same_seed_same_output(self):
        """Same seed produces identical output."""
        gen1 = PropGenerator(16, 16, seed=42)
        gen2 = PropGenerator(16, 16, seed=42)

        result1 = gen1.generate('chest')
        result2 = gen2.generate('chest')

        for y in range(result1.height):
            for x in range(result1.width):
                self.assertEqual(result1.get_pixel(x, y), result2.get_pixel(x, y))

    def test_different_seeds_different_bookshelf(self):
        """Different seeds produce different bookshelves."""
        gen1 = PropGenerator(16, 24, seed=42)
        gen2 = PropGenerator(16, 24, seed=123)

        result1 = gen1.generate('bookshelf')
        result2 = gen2.generate('bookshelf')

        # Should have at least some different pixels (due to random book colors)
        different = False
        for y in range(result1.height):
            for x in range(result1.width):
                if result1.get_pixel(x, y) != result2.get_pixel(x, y):
                    different = True
                    break

        self.assertTrue(different)


class TestPropVisuals(TestCase):
    """Tests for visual properties of generated props."""

    def test_props_not_empty(self):
        """Generated props have visible content."""
        gen = PropGenerator(16, 16, seed=42)
        prop_types = ['chest', 'barrel', 'table', 'tree', 'torch']

        for prop_type in prop_types:
            result = gen.generate(prop_type)

            pixel_count = 0
            for y in range(result.height):
                for x in range(result.width):
                    if result.get_pixel(x, y)[3] > 0:
                        pixel_count += 1

            self.assertGreater(pixel_count, 0, f"{prop_type} should have visible pixels")

    def test_larger_props(self):
        """Larger canvas sizes work correctly."""
        gen = PropGenerator(32, 32, seed=42)
        result = gen.generate('chest')

        self.assertEqual(result.width, 32)
        self.assertEqual(result.height, 32)

    def test_smaller_props(self):
        """Smaller canvas sizes work correctly."""
        gen = PropGenerator(8, 8, seed=42)
        result = gen.generate('crate')

        self.assertEqual(result.width, 8)
        self.assertEqual(result.height, 8)


class TestAllPropTypes(TestCase):
    """Tests that all prop types generate without errors."""

    def test_all_prop_types_generate(self):
        """All listed prop types generate successfully."""
        gen = PropGenerator(16, 16, seed=42)
        prop_types = list_prop_types()

        for prop_type in prop_types:
            result = gen.generate(prop_type)
            self.assertIsInstance(result, Canvas,
                                  f"{prop_type} should return Canvas")


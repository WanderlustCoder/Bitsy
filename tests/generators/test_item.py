"""
Test Item Generator - Tests for procedural item generation.

Tests:
- ItemPalette creation and presets
- ItemGenerator configuration
- Item type generation
- Determinism with seeds
- Output validity
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests.framework import TestCase
from generators import (
    ItemGenerator, ItemPalette, generate_item, list_item_types, ITEM_GENERATORS
)
from core import Canvas


class TestItemPalette(TestCase):
    """Tests for ItemPalette."""

    def test_default_palette(self):
        """ItemPalette has sensible defaults."""
        palette = ItemPalette()
        self.assertEqual(len(palette.primary), 4)
        self.assertEqual(len(palette.secondary), 4)
        self.assertEqual(len(palette.accent), 4)

    def test_iron_preset(self):
        """Iron preset returns valid palette."""
        palette = ItemPalette.iron()
        self.assertIsInstance(palette, ItemPalette)
        # Iron should be grayish
        self.assertGreater(palette.primary[0], 150)

    def test_gold_preset(self):
        """Gold preset returns valid palette."""
        palette = ItemPalette.gold()
        self.assertIsInstance(palette, ItemPalette)
        # Gold should be yellowish (R > B)
        self.assertGreater(palette.primary[0], palette.primary[2])

    def test_wood_preset(self):
        """Wood preset returns valid palette."""
        palette = ItemPalette.wood()
        self.assertIsInstance(palette, ItemPalette)
        # Wood should be brownish


class TestItemGenerator(TestCase):
    """Tests for ItemGenerator class."""

    def test_create_generator(self):
        """ItemGenerator can be created."""
        gen = ItemGenerator(16, 16)
        self.assertEqual(gen.width, 16)
        self.assertEqual(gen.height, 16)

    def test_create_with_seed(self):
        """ItemGenerator accepts seed parameter."""
        gen = ItemGenerator(16, 16, seed=12345)
        self.assertEqual(gen.seed, 12345)

    def test_set_palette(self):
        """ItemGenerator accepts palette."""
        gen = ItemGenerator(16, 16)
        palette = ItemPalette.gold()
        gen.set_palette(palette)
        self.assertEqual(gen.palette, palette)

    def test_generate_sword(self):
        """generate_sword returns valid canvas."""
        gen = ItemGenerator(16, 24)
        result = gen.generate_sword()
        self.assertIsInstance(result, Canvas)
        self.assertEqual(result.width, 16)
        self.assertEqual(result.height, 24)
        self.assertCanvasNotEmpty(result)

    def test_generate_shield_round(self):
        """generate_shield round variant works."""
        gen = ItemGenerator(16, 16)
        result = gen.generate_shield('round')
        self.assertIsInstance(result, Canvas)
        self.assertCanvasNotEmpty(result)

    def test_generate_shield_kite(self):
        """generate_shield kite variant works."""
        gen = ItemGenerator(16, 16)
        result = gen.generate_shield('kite')
        self.assertIsInstance(result, Canvas)
        self.assertCanvasNotEmpty(result)

    def test_generate_potion(self):
        """generate_potion returns valid canvas."""
        gen = ItemGenerator(12, 16)
        result = gen.generate_potion('health')
        self.assertIsInstance(result, Canvas)
        self.assertCanvasNotEmpty(result)

    def test_generate_gem(self):
        """generate_gem returns valid canvas."""
        gen = ItemGenerator(12, 12)
        result = gen.generate_gem('red')
        self.assertIsInstance(result, Canvas)
        self.assertCanvasNotEmpty(result)


class TestItemGeneratorDeterminism(TestCase):
    """Tests for deterministic generation."""

    def test_same_seed_same_output(self):
        """Same seed produces identical output."""
        gen1 = ItemGenerator(16, 16, seed=42)
        gen2 = ItemGenerator(16, 16, seed=42)

        result1 = gen1.generate_sword()
        result2 = gen2.generate_sword()

        self.assertCanvasEqual(result1, result2)

    def test_different_palette_different_output(self):
        """Different palettes produce different output."""
        gen = ItemGenerator(16, 16, seed=42)

        gen.set_palette(ItemPalette.iron())
        result1 = gen.generate_sword()

        gen.set_palette(ItemPalette.gold())
        result2 = gen.generate_sword()

        # Generate hashes - should be different
        hash1 = self.getCanvasHash(result1)
        hash2 = self.getCanvasHash(result2)
        self.assertNotEqual(hash1, hash2)


class TestGenerateItemFunction(TestCase):
    """Tests for generate_item convenience function."""

    def test_generate_sword(self):
        """generate_item('sword') produces sword."""
        result = generate_item('sword')
        self.assertIsInstance(result, Canvas)
        self.assertCanvasNotEmpty(result)

    def test_generate_axe(self):
        """generate_item('axe') produces axe."""
        result = generate_item('axe')
        self.assertIsInstance(result, Canvas)
        self.assertCanvasNotEmpty(result)

    def test_generate_bow(self):
        """generate_item('bow') produces bow."""
        result = generate_item('bow')
        self.assertIsInstance(result, Canvas)
        self.assertCanvasNotEmpty(result)

    def test_generate_staff(self):
        """generate_item('staff') produces staff."""
        result = generate_item('staff')
        self.assertIsInstance(result, Canvas)
        self.assertCanvasNotEmpty(result)

    def test_generate_shield_round(self):
        """generate_item('shield_round') produces round shield."""
        result = generate_item('shield_round')
        self.assertIsInstance(result, Canvas)
        self.assertCanvasNotEmpty(result)

    def test_generate_potion_health(self):
        """generate_item('potion_health') produces health potion."""
        result = generate_item('potion_health')
        self.assertIsInstance(result, Canvas)
        self.assertCanvasNotEmpty(result)

    def test_generate_with_custom_size(self):
        """generate_item accepts custom size."""
        result = generate_item('sword', width=24, height=32)
        self.assertEqual(result.width, 24)
        self.assertEqual(result.height, 32)

    def test_generate_with_palette(self):
        """generate_item accepts palette."""
        palette = ItemPalette.gold()
        result = generate_item('sword', palette=palette)
        self.assertIsInstance(result, Canvas)
        self.assertCanvasNotEmpty(result)

    def test_generate_deterministic(self):
        """generate_item is deterministic with seed."""
        result1 = generate_item('sword', seed=123)
        result2 = generate_item('sword', seed=123)
        self.assertCanvasEqual(result1, result2)


class TestItemEdgeCases(TestCase):
    """Edge case tests for item generation."""

    def _assert_size_edge_case(self, size: int) -> None:
        """Validate size edge cases either succeed or raise ValueError."""
        try:
            result = generate_item('sword', width=size, height=size)
        except ValueError:
            return
        except Exception as exc:
            self.assertTrue(False, f"Unexpected exception for size {size}: {exc}")
            return

        self.assertIsInstance(result, Canvas)
        self.assertEqual(result.width, size)
        self.assertEqual(result.height, size)

    def test_zero_size(self):
        """Size 0 handles gracefully."""
        self._assert_size_edge_case(0)

    def test_negative_size(self):
        """Negative size handles gracefully."""
        self._assert_size_edge_case(-1)

    def test_large_size(self):
        """Large size generates successfully."""
        result = generate_item('sword', width=100, height=100)
        self.assertIsInstance(result, Canvas)
        self.assertEqual(result.width, 100)
        self.assertEqual(result.height, 100)
        self.assertCanvasNotEmpty(result)

    def test_extreme_seed_zero(self):
        """Seed 0 remains deterministic."""
        result1 = generate_item('sword', seed=0)
        result2 = generate_item('sword', seed=0)
        self.assertCanvasEqual(result1, result2)

    def test_extreme_seed_max(self):
        """Max 32-bit seed works."""
        seed_max = 2 ** 31 - 1
        result = generate_item('sword', seed=seed_max)
        self.assertIsInstance(result, Canvas)
        self.assertCanvasNotEmpty(result)

    def test_invalid_item_type(self):
        """Invalid item type raises error."""
        self.assertRaises(ValueError, generate_item, 'not_a_real_item')


class TestListItemTypes(TestCase):
    """Tests for list_item_types function."""

    def test_returns_list(self):
        """list_item_types returns a list."""
        types = list_item_types()
        self.assertIsInstance(types, list)

    def test_has_basic_types(self):
        """list_item_types includes basic item types."""
        types = list_item_types()
        self.assertIn('sword', types)
        self.assertIn('axe', types)
        self.assertIn('bow', types)

    def test_all_types_generatable(self):
        """All listed types can be generated."""
        types = list_item_types()
        for item_type in types:
            try:
                result = generate_item(item_type)
                self.assertIsInstance(result, Canvas)
            except Exception as e:
                self.fail(f"Failed to generate '{item_type}': {e}")


class TestItemGenerators(TestCase):
    """Tests for ITEM_GENERATORS registry."""

    def test_is_dict(self):
        """ITEM_GENERATORS is a dictionary."""
        self.assertIsInstance(ITEM_GENERATORS, dict)

    def test_has_entries(self):
        """ITEM_GENERATORS has entries."""
        self.assertGreater(len(ITEM_GENERATORS), 0)

    def test_entries_callable(self):
        """ITEM_GENERATORS entries are callable."""
        for name, generator in ITEM_GENERATORS.items():
            self.assertTrue(callable(generator),
                           f"Generator '{name}' is not callable")


class TestItemOutputQuality(TestCase):
    """Tests for item output quality."""

    def test_items_have_reasonable_fill(self):
        """Generated items use reasonable portion of canvas."""
        gen = ItemGenerator(16, 16)

        items_to_test = [
            ('sword', gen.generate_sword),
            ('potion', lambda: gen.generate_potion('health')),
        ]

        for name, generator in items_to_test:
            result = generator()

            # Count non-transparent pixels
            opaque_count = 0
            for y in range(result.height):
                for x in range(result.width):
                    if result.pixels[y][x][3] > 0:
                        opaque_count += 1

            # Should use at least 10% of canvas
            total = result.width * result.height
            fill_ratio = opaque_count / total
            self.assertGreater(fill_ratio, 0.10,
                              f"{name} only fills {fill_ratio:.1%} of canvas")

    def test_items_not_monochrome(self):
        """Generated items have color variation."""
        gen = ItemGenerator(16, 16)
        result = gen.generate_sword()

        colors = set()
        for y in range(result.height):
            for x in range(result.width):
                pixel = result.pixels[y][x]
                if pixel[3] > 0:
                    colors.add(tuple(pixel))

        # Should have multiple colors
        self.assertGreater(len(colors), 2,
                          f"Sword only has {len(colors)} colors")

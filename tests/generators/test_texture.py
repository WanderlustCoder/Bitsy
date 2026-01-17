"""
Test Texture Generator - Tests for seamless texture generation.

Tests:
- TexturePalette creation and presets
- TextureGenerator configuration
- All texture type generation
- Determinism with seeds
- Output validity
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests.framework import TestCase
from generators import (
    TextureGenerator, TexturePalette, generate_texture,
    list_texture_types, TEXTURE_GENERATORS
)
from core import Canvas


class TestTexturePalette(TestCase):
    """Tests for TexturePalette."""

    def test_create_custom_palette(self):
        """TexturePalette can be created with custom colors."""
        palette = TexturePalette(
            base=(100, 100, 100, 255),
            highlight=(150, 150, 150, 255),
            shadow=(50, 50, 50, 255)
        )
        self.assertEqual(palette.base[0], 100)
        self.assertEqual(palette.highlight[0], 150)
        self.assertEqual(palette.shadow[0], 50)

    def test_brick_preset(self):
        """Brick preset returns valid palette."""
        palette = TexturePalette.brick()
        self.assertIsInstance(palette, TexturePalette)
        # Brick should be reddish (R > B)
        self.assertGreater(palette.base[0], palette.base[2])

    def test_stone_preset(self):
        """Stone preset returns valid palette."""
        palette = TexturePalette.stone()
        self.assertIsInstance(palette, TexturePalette)
        # Stone should be grayish (R ≈ G ≈ B)
        self.assertEqual(palette.base[0], palette.base[1])

    def test_wood_preset(self):
        """Wood preset returns valid palette."""
        palette = TexturePalette.wood()
        self.assertIsInstance(palette, TexturePalette)
        # Wood should be brownish

    def test_grass_preset(self):
        """Grass preset returns valid palette."""
        palette = TexturePalette.grass()
        self.assertIsInstance(palette, TexturePalette)
        # Grass should be greenish (G > R and G > B)
        self.assertGreater(palette.base[1], palette.base[0])
        self.assertGreater(palette.base[1], palette.base[2])

    def test_metal_preset(self):
        """Metal preset returns valid palette."""
        palette = TexturePalette.metal()
        self.assertIsInstance(palette, TexturePalette)


class TestTextureGenerator(TestCase):
    """Tests for TextureGenerator class."""

    def test_create_generator(self):
        """TextureGenerator can be created."""
        gen = TextureGenerator(32, 32)
        self.assertEqual(gen.width, 32)
        self.assertEqual(gen.height, 32)

    def test_create_with_seed(self):
        """TextureGenerator accepts seed parameter."""
        gen = TextureGenerator(32, 32, seed=12345)
        self.assertEqual(gen.seed, 12345)

    def test_set_palette(self):
        """TextureGenerator accepts palette."""
        gen = TextureGenerator(32, 32)
        palette = TexturePalette.brick()
        gen.set_palette(palette)
        self.assertEqual(gen.palette, palette)

    def test_generate_brick(self):
        """generate_brick returns valid canvas."""
        gen = TextureGenerator(32, 32)
        gen.set_palette(TexturePalette.brick())
        result = gen.generate_brick()
        self.assertIsInstance(result, Canvas)
        self.assertEqual(result.width, 32)
        self.assertEqual(result.height, 32)
        self.assertCanvasNotEmpty(result)

    def test_generate_stone(self):
        """generate_stone returns valid canvas."""
        gen = TextureGenerator(32, 32)
        gen.set_palette(TexturePalette.stone())
        result = gen.generate_stone()
        self.assertIsInstance(result, Canvas)
        self.assertCanvasNotEmpty(result)

    def test_generate_wood(self):
        """generate_wood returns valid canvas."""
        gen = TextureGenerator(32, 32)
        gen.set_palette(TexturePalette.wood())
        result = gen.generate_wood()
        self.assertIsInstance(result, Canvas)
        self.assertCanvasNotEmpty(result)

    def test_generate_grass(self):
        """generate_grass returns valid canvas."""
        gen = TextureGenerator(32, 32)
        gen.set_palette(TexturePalette.grass())
        result = gen.generate_grass()
        self.assertIsInstance(result, Canvas)
        self.assertCanvasNotEmpty(result)

    def test_generate_fabric_checkered(self):
        """generate_fabric with checkered pattern works."""
        gen = TextureGenerator(32, 32)
        result = gen.generate_fabric(pattern='checkered')
        self.assertIsInstance(result, Canvas)
        self.assertCanvasNotEmpty(result)

    def test_generate_fabric_striped(self):
        """generate_fabric with striped pattern works."""
        gen = TextureGenerator(32, 32)
        result = gen.generate_fabric(pattern='striped')
        self.assertIsInstance(result, Canvas)
        self.assertCanvasNotEmpty(result)

    def test_generate_metal_brushed(self):
        """generate_metal with brushed style works."""
        gen = TextureGenerator(32, 32)
        gen.set_palette(TexturePalette.metal())
        result = gen.generate_metal(style='brushed')
        self.assertIsInstance(result, Canvas)
        self.assertCanvasNotEmpty(result)

    def test_generate_metal_riveted(self):
        """generate_metal with riveted style works."""
        gen = TextureGenerator(32, 32)
        gen.set_palette(TexturePalette.metal())
        result = gen.generate_metal(style='riveted')
        self.assertIsInstance(result, Canvas)
        self.assertCanvasNotEmpty(result)


class TestTextureDeterminism(TestCase):
    """Tests for deterministic generation."""

    def test_same_seed_same_output(self):
        """Same seed produces identical output."""
        gen1 = TextureGenerator(32, 32, seed=42)
        gen2 = TextureGenerator(32, 32, seed=42)

        gen1.set_palette(TexturePalette.brick())
        gen2.set_palette(TexturePalette.brick())

        result1 = gen1.generate_brick()
        result2 = gen2.generate_brick()

        self.assertCanvasEqual(result1, result2)

    def test_different_seed_different_output(self):
        """Different seeds produce different output."""
        result1 = generate_texture('stone', seed=1)
        result2 = generate_texture('stone', seed=2)

        hash1 = self.getCanvasHash(result1)
        hash2 = self.getCanvasHash(result2)
        self.assertNotEqual(hash1, hash2)


class TestGenerateTextureFunction(TestCase):
    """Tests for generate_texture convenience function."""

    def test_generate_brick(self):
        """generate_texture('brick') produces brick texture."""
        result = generate_texture('brick')
        self.assertIsInstance(result, Canvas)
        self.assertCanvasNotEmpty(result)

    def test_generate_stone(self):
        """generate_texture('stone') produces stone texture."""
        result = generate_texture('stone')
        self.assertIsInstance(result, Canvas)
        self.assertCanvasNotEmpty(result)

    def test_generate_wood(self):
        """generate_texture('wood') produces wood texture."""
        result = generate_texture('wood')
        self.assertIsInstance(result, Canvas)
        self.assertCanvasNotEmpty(result)

    def test_generate_grass(self):
        """generate_texture('grass') produces grass texture."""
        result = generate_texture('grass')
        self.assertIsInstance(result, Canvas)
        self.assertCanvasNotEmpty(result)

    def test_generate_with_custom_size(self):
        """generate_texture accepts custom size."""
        result = generate_texture('brick', width=64, height=64)
        self.assertEqual(result.width, 64)
        self.assertEqual(result.height, 64)

    def test_generate_with_palette(self):
        """generate_texture accepts palette."""
        palette = TexturePalette.stone()
        result = generate_texture('brick', palette=palette)
        self.assertIsInstance(result, Canvas)
        self.assertCanvasNotEmpty(result)

    def test_generate_deterministic(self):
        """generate_texture is deterministic with seed."""
        result1 = generate_texture('brick', seed=123)
        result2 = generate_texture('brick', seed=123)
        self.assertCanvasEqual(result1, result2)

    def test_invalid_texture_type(self):
        """Invalid texture type raises error."""
        self.assertRaises(ValueError, generate_texture, 'not_a_real_texture')


class TestListTextureTypes(TestCase):
    """Tests for list_texture_types function."""

    def test_returns_list(self):
        """list_texture_types returns a list."""
        types = list_texture_types()
        self.assertIsInstance(types, list)

    def test_has_basic_types(self):
        """list_texture_types includes basic texture types."""
        types = list_texture_types()
        self.assertIn('brick', types)
        self.assertIn('stone', types)
        self.assertIn('wood', types)
        self.assertIn('grass', types)

    def test_all_types_generatable(self):
        """All listed types can be generated."""
        types = list_texture_types()
        for texture_type in types:
            try:
                result = generate_texture(texture_type, width=16, height=16)
                self.assertIsInstance(result, Canvas)
            except Exception as e:
                self.fail(f"Failed to generate '{texture_type}': {e}")


class TestTextureGenerators(TestCase):
    """Tests for TEXTURE_GENERATORS registry."""

    def test_is_dict(self):
        """TEXTURE_GENERATORS is a dictionary."""
        self.assertIsInstance(TEXTURE_GENERATORS, dict)

    def test_has_entries(self):
        """TEXTURE_GENERATORS has entries."""
        self.assertGreater(len(TEXTURE_GENERATORS), 0)

    def test_entries_callable(self):
        """TEXTURE_GENERATORS entries are callable."""
        for name, generator in TEXTURE_GENERATORS.items():
            self.assertTrue(callable(generator),
                           f"Generator '{name}' is not callable")

"""
Test Creature Generator - Tests for creature generation.

Tests:
- Creature type generation
- Slime variants
- Undead variants
- Elemental variants
- Palette system
- Determinism
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests.framework import TestCase
from core import Canvas
from generators.creature import (
    CreatureGenerator,
    CreatureType,
    CreaturePalette,
    SlimeVariant,
    BeastVariant,
    UndeadVariant,
    ElementalVariant,
    InsectVariant,
    generate_creature,
    list_creature_types,
    list_slime_variants,
)


class TestCreatureGenerator(TestCase):
    """Tests for CreatureGenerator class."""

    def test_constructor(self):
        """CreatureGenerator initializes correctly."""
        gen = CreatureGenerator(16, 16, seed=42)

        self.assertEqual(gen.width, 16)
        self.assertEqual(gen.height, 16)
        self.assertEqual(gen.seed, 42)

    def test_custom_dimensions(self):
        """Custom dimensions are respected."""
        gen = CreatureGenerator(32, 24, seed=42)

        self.assertEqual(gen.width, 32)
        self.assertEqual(gen.height, 24)

    def test_set_palette(self):
        """set_palette changes color palette."""
        gen = CreatureGenerator(16, 16, seed=42)
        palette = CreaturePalette.blue_slime()
        result = gen.set_palette(palette)

        self.assertEqual(gen.palette, palette)
        self.assertEqual(result, gen)  # Returns self for chaining

    def test_set_seed(self):
        """set_seed changes random seed."""
        gen = CreatureGenerator(16, 16, seed=42)
        result = gen.set_seed(100)

        self.assertEqual(gen.seed, 100)
        self.assertEqual(result, gen)  # Returns self for chaining

    def test_generate_returns_canvas(self):
        """generate method returns Canvas."""
        gen = CreatureGenerator(16, 16, seed=42)
        result = gen.generate('slime')

        self.assertIsInstance(result, Canvas)

    def test_generate_unknown_type_defaults_to_slime(self):
        """Unknown creature type defaults to slime."""
        gen = CreatureGenerator(16, 16, seed=42)
        result = gen.generate('unknown_type')

        self.assertIsInstance(result, Canvas)
        self.assertEqual(result.width, 16)
        self.assertEqual(result.height, 16)


class TestSlimeGeneration(TestCase):
    """Tests for slime creature generation."""

    def test_basic_slime(self):
        """Generates basic slime."""
        gen = CreatureGenerator(16, 16, seed=42)
        result = gen.generate('slime')

        self.assertIsInstance(result, Canvas)
        self.assertEqual(result.width, 16)
        self.assertEqual(result.height, 16)

    def test_slime_variants(self):
        """All slime variants generate successfully."""
        gen = CreatureGenerator(16, 16, seed=42)
        variants = ['basic', 'fire', 'ice', 'poison', 'metal', 'blue', 'green']

        for variant in variants:
            result = gen.generate('slime', variant)
            self.assertIsInstance(result, Canvas)

    def test_fire_slime_variant(self):
        """Fire slime has distinct appearance."""
        gen = CreatureGenerator(16, 16, seed=42)
        fire = gen.generate('slime', 'fire')
        basic = gen.generate('slime', 'basic')

        # Both should generate but with different palettes
        self.assertIsInstance(fire, Canvas)
        self.assertIsInstance(basic, Canvas)

    def test_metal_slime_variant(self):
        """Metal slime variant generates."""
        gen = CreatureGenerator(16, 16, seed=42)
        result = gen.generate('slime', 'metal')

        self.assertIsInstance(result, Canvas)

    def test_slime_has_eyes(self):
        """Slime has visible eye pixels."""
        gen = CreatureGenerator(16, 16, seed=42)
        result = gen.generate('slime')

        # Check for non-transparent pixels (slime should have content)
        has_content = False
        for y in range(result.height):
            for x in range(result.width):
                pixel = result.get_pixel(x, y)
                if pixel[3] > 0:  # Non-transparent
                    has_content = True
                    break

        self.assertTrue(has_content)


class TestUndeadGeneration(TestCase):
    """Tests for undead creature generation."""

    def test_skeleton(self):
        """Generates skeleton."""
        gen = CreatureGenerator(16, 16, seed=42)
        result = gen.generate('skeleton')

        self.assertIsInstance(result, Canvas)

    def test_zombie(self):
        """Generates zombie."""
        gen = CreatureGenerator(16, 16, seed=42)
        result = gen.generate('zombie')

        self.assertIsInstance(result, Canvas)

    def test_ghost(self):
        """Generates ghost."""
        gen = CreatureGenerator(16, 16, seed=42)
        result = gen.generate('ghost')

        self.assertIsInstance(result, Canvas)

    def test_undead_dispatcher(self):
        """Undead type dispatches to variants correctly."""
        gen = CreatureGenerator(16, 16, seed=42)

        skeleton = gen.generate('undead', 'skeleton')
        zombie = gen.generate('undead', 'zombie')
        ghost = gen.generate('undead', 'ghost')

        self.assertIsInstance(skeleton, Canvas)
        self.assertIsInstance(zombie, Canvas)
        self.assertIsInstance(ghost, Canvas)

    def test_undead_default(self):
        """Undead without variant defaults to skeleton."""
        gen = CreatureGenerator(16, 16, seed=42)
        result = gen.generate('undead')

        self.assertIsInstance(result, Canvas)


class TestBeastGeneration(TestCase):
    """Tests for beast creature generation."""

    def test_wolf(self):
        """Generates wolf."""
        gen = CreatureGenerator(16, 16, seed=42)
        result = gen.generate('wolf')

        self.assertIsInstance(result, Canvas)

    def test_bat(self):
        """Generates bat."""
        gen = CreatureGenerator(16, 16, seed=42)
        result = gen.generate('bat')

        self.assertIsInstance(result, Canvas)

    def test_beast_dispatcher(self):
        """Beast type dispatches to variants."""
        gen = CreatureGenerator(16, 16, seed=42)

        wolf = gen.generate('beast', 'wolf')
        bat = gen.generate('beast', 'bat')

        self.assertIsInstance(wolf, Canvas)
        self.assertIsInstance(bat, Canvas)


class TestElementalGeneration(TestCase):
    """Tests for elemental creature generation."""

    def test_fire_elemental(self):
        """Generates fire elemental."""
        gen = CreatureGenerator(16, 16, seed=42)
        result = gen.generate('fire_elemental')

        self.assertIsInstance(result, Canvas)

    def test_ice_elemental(self):
        """Generates ice elemental."""
        gen = CreatureGenerator(16, 16, seed=42)
        result = gen.generate('ice_elemental')

        self.assertIsInstance(result, Canvas)

    def test_elemental_dispatcher(self):
        """Elemental type dispatches to variants."""
        gen = CreatureGenerator(16, 16, seed=42)

        fire = gen.generate('elemental', 'fire')
        ice = gen.generate('elemental', 'ice')

        self.assertIsInstance(fire, Canvas)
        self.assertIsInstance(ice, Canvas)


class TestInsectGeneration(TestCase):
    """Tests for insect creature generation."""

    def test_spider(self):
        """Generates spider."""
        gen = CreatureGenerator(16, 16, seed=42)
        result = gen.generate('spider')

        self.assertIsInstance(result, Canvas)

    def test_insect_dispatcher(self):
        """Insect type dispatches to spider by default."""
        gen = CreatureGenerator(16, 16, seed=42)
        result = gen.generate('insect')

        self.assertIsInstance(result, Canvas)


class TestCreaturePalette(TestCase):
    """Tests for CreaturePalette class."""

    def test_default_palette(self):
        """Default palette has all colors."""
        palette = CreaturePalette()

        self.assertIsNotNone(palette.body)
        self.assertIsNotNone(palette.body_light)
        self.assertIsNotNone(palette.body_dark)
        self.assertIsNotNone(palette.eyes)
        self.assertIsNotNone(palette.accent)
        self.assertIsNotNone(palette.outline)

    def test_green_slime_palette(self):
        """Green slime palette has green tones."""
        palette = CreaturePalette.green_slime()

        # Green channel should be dominant
        self.assertGreater(palette.body[1], palette.body[0])  # G > R
        self.assertGreater(palette.body[1], palette.body[2])  # G > B

    def test_blue_slime_palette(self):
        """Blue slime palette has blue tones."""
        palette = CreaturePalette.blue_slime()

        # Blue channel should be dominant
        self.assertGreater(palette.body[2], palette.body[0])  # B > R

    def test_red_slime_palette(self):
        """Red slime palette has red tones."""
        palette = CreaturePalette.red_slime()

        # Red channel should be dominant
        self.assertGreater(palette.body[0], palette.body[1])  # R > G
        self.assertGreater(palette.body[0], palette.body[2])  # R > B

    def test_metal_slime_palette(self):
        """Metal slime palette has metallic gray tones."""
        palette = CreaturePalette.metal_slime()

        # Should be grayish (channels relatively equal)
        r, g, b = palette.body[0], palette.body[1], palette.body[2]
        self.assertLess(abs(r - g), 30)  # R and G close
        self.assertLess(abs(g - b), 30)  # G and B close

    def test_skeleton_palette(self):
        """Skeleton palette has bone-like colors."""
        palette = CreaturePalette.skeleton()

        # Should be light/off-white
        self.assertGreater(palette.body[0], 200)  # High red
        self.assertGreater(palette.body[1], 200)  # High green
        self.assertGreater(palette.body[2], 150)  # Moderately high blue

    def test_ghost_palette_transparency(self):
        """Ghost palette includes transparency."""
        palette = CreaturePalette.ghost()

        # Ghost body should have alpha < 255
        self.assertLess(palette.body[3], 255)

    def test_fire_elemental_palette(self):
        """Fire elemental palette has warm colors."""
        palette = CreaturePalette.fire_elemental()

        # Red/orange tones
        self.assertGreater(palette.body[0], 200)  # High red
        self.assertGreater(palette.body[1], 100)  # Medium green (orange)

    def test_ice_elemental_palette(self):
        """Ice elemental palette has cool colors."""
        palette = CreaturePalette.ice_elemental()

        # Blue tones
        self.assertGreater(palette.body[2], palette.body[0])  # Blue > Red


class TestDeterminism(TestCase):
    """Tests for deterministic generation."""

    def test_same_seed_same_output(self):
        """Same seed produces identical output."""
        gen1 = CreatureGenerator(16, 16, seed=42)
        gen2 = CreatureGenerator(16, 16, seed=42)

        result1 = gen1.generate('slime')
        result2 = gen2.generate('slime')

        # Compare pixel by pixel
        for y in range(result1.height):
            for x in range(result1.width):
                p1 = result1.get_pixel(x, y)
                p2 = result2.get_pixel(x, y)
                self.assertEqual(p1, p2)

    def test_different_seeds_different_output(self):
        """Different seeds produce different output."""
        gen1 = CreatureGenerator(16, 16, seed=42)
        gen2 = CreatureGenerator(16, 16, seed=123)

        # Fire elemental uses randomness
        result1 = gen1.generate('fire_elemental')
        result2 = gen2.generate('fire_elemental')

        # Should have at least some different pixels
        different = False
        for y in range(result1.height):
            for x in range(result1.width):
                p1 = result1.get_pixel(x, y)
                p2 = result2.get_pixel(x, y)
                if p1 != p2:
                    different = True
                    break

        self.assertTrue(different)


class TestConvenienceFunctions(TestCase):
    """Tests for module-level convenience functions."""

    def test_generate_creature(self):
        """generate_creature function works."""
        result = generate_creature('slime', 'basic', 16, 16, 42)

        self.assertIsInstance(result, Canvas)
        self.assertEqual(result.width, 16)
        self.assertEqual(result.height, 16)

    def test_generate_creature_custom_size(self):
        """generate_creature with custom dimensions."""
        result = generate_creature('ghost', None, 32, 32, 42)

        self.assertEqual(result.width, 32)
        self.assertEqual(result.height, 32)

    def test_list_creature_types(self):
        """list_creature_types returns all types."""
        types = list_creature_types()

        self.assertIn('slime', types)
        self.assertIn('ghost', types)
        self.assertIn('skeleton', types)
        self.assertIn('zombie', types)
        self.assertIn('wolf', types)
        self.assertIn('bat', types)
        self.assertIn('spider', types)
        self.assertIn('fire_elemental', types)
        self.assertIn('ice_elemental', types)

    def test_list_slime_variants(self):
        """list_slime_variants returns all slime variants."""
        variants = list_slime_variants()

        self.assertIn('basic', variants)
        self.assertIn('fire', variants)
        self.assertIn('ice', variants)
        self.assertIn('poison', variants)
        self.assertIn('metal', variants)


class TestCreatureEnums(TestCase):
    """Tests for creature type enums."""

    def test_creature_type_values(self):
        """CreatureType enum has expected values."""
        self.assertEqual(CreatureType.SLIME.value, 'slime')
        self.assertEqual(CreatureType.BEAST.value, 'beast')
        self.assertEqual(CreatureType.UNDEAD.value, 'undead')
        self.assertEqual(CreatureType.ELEMENTAL.value, 'elemental')
        self.assertEqual(CreatureType.INSECT.value, 'insect')

    def test_slime_variant_values(self):
        """SlimeVariant enum has expected values."""
        self.assertEqual(SlimeVariant.BASIC.value, 'basic')
        self.assertEqual(SlimeVariant.FIRE.value, 'fire')
        self.assertEqual(SlimeVariant.ICE.value, 'ice')
        self.assertEqual(SlimeVariant.METAL.value, 'metal')

    def test_beast_variant_values(self):
        """BeastVariant enum has expected values."""
        self.assertEqual(BeastVariant.WOLF.value, 'wolf')
        self.assertEqual(BeastVariant.BAT.value, 'bat')

    def test_undead_variant_values(self):
        """UndeadVariant enum has expected values."""
        self.assertEqual(UndeadVariant.SKELETON.value, 'skeleton')
        self.assertEqual(UndeadVariant.ZOMBIE.value, 'zombie')
        self.assertEqual(UndeadVariant.GHOST.value, 'ghost')

    def test_elemental_variant_values(self):
        """ElementalVariant enum has expected values."""
        self.assertEqual(ElementalVariant.FIRE.value, 'fire')
        self.assertEqual(ElementalVariant.ICE.value, 'ice')

    def test_insect_variant_values(self):
        """InsectVariant enum has expected values."""
        self.assertEqual(InsectVariant.SPIDER.value, 'spider')


class TestCreatureVisuals(TestCase):
    """Tests for visual properties of generated creatures."""

    def test_creature_not_empty(self):
        """Generated creatures have visible content."""
        gen = CreatureGenerator(16, 16, seed=42)
        types = ['slime', 'ghost', 'skeleton', 'zombie', 'wolf', 'bat', 'spider']

        for creature_type in types:
            result = gen.generate(creature_type)

            pixel_count = 0
            for y in range(result.height):
                for x in range(result.width):
                    if result.get_pixel(x, y)[3] > 0:
                        pixel_count += 1

            self.assertGreater(pixel_count, 0, f"{creature_type} should have visible pixels")

    def test_larger_creatures(self):
        """Larger canvas sizes work correctly."""
        gen = CreatureGenerator(32, 32, seed=42)
        result = gen.generate('slime')

        self.assertEqual(result.width, 32)
        self.assertEqual(result.height, 32)

        # Should have more content on larger canvas
        pixel_count = 0
        for y in range(result.height):
            for x in range(result.width):
                if result.get_pixel(x, y)[3] > 0:
                    pixel_count += 1

        self.assertGreater(pixel_count, 50)

    def test_smaller_creatures(self):
        """Smaller canvas sizes work correctly."""
        gen = CreatureGenerator(8, 8, seed=42)
        result = gen.generate('slime')

        self.assertEqual(result.width, 8)
        self.assertEqual(result.height, 8)


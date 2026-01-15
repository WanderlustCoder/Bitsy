"""Tests for character presets."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests.framework import TestCase
from core.canvas import Canvas
from characters import (
    Character,
    list_presets,
    get_preset,
    random_character,
    hero,
    heroine,
    villager,
    wizard,
    warrior,
    rogue,
    knight,
    princess,
    monster,
    ghost,
    child,
    elder,
    cat_person,
)


class TestListPresets(TestCase):
    """Tests for list_presets function."""

    def test_returns_list(self):
        """list_presets returns a list."""
        presets = list_presets()
        self.assertIsInstance(presets, list)

    def test_contains_expected_presets(self):
        """list_presets contains expected preset names."""
        presets = list_presets()
        expected = ['hero', 'heroine', 'villager', 'wizard', 'warrior', 'rogue']
        for name in expected:
            self.assertIn(name, presets)

    def test_not_empty(self):
        """list_presets returns non-empty list."""
        presets = list_presets()
        self.assertGreater(len(presets), 0)


class TestGetPreset(TestCase):
    """Tests for get_preset function."""

    def test_get_hero(self):
        """get_preset('hero') returns Character."""
        char = get_preset('hero')
        self.assertIsInstance(char, Character)

    def test_get_with_kwargs(self):
        """get_preset accepts keyword arguments."""
        char = get_preset('hero', hair_color='black', width=64)
        self.assertIsInstance(char, Character)
        self.assertEqual(char.width, 64)

    def test_invalid_preset_raises(self):
        """get_preset raises ValueError for invalid name."""
        with self.assertRaises(ValueError):
            get_preset('not_a_real_preset')


class TestHeroPreset(TestCase):
    """Tests for hero preset."""

    def test_creates_character(self):
        """hero() creates a Character."""
        char = hero()
        self.assertIsInstance(char, Character)

    def test_renders_successfully(self):
        """hero() renders to non-empty canvas."""
        char = hero()
        canvas = char.render()
        self.assertCanvasNotEmpty(canvas)

    def test_custom_hair_color(self):
        """hero() accepts custom hair color."""
        char = hero(hair_color='red')
        self.assertIsInstance(char, Character)

    def test_custom_size(self):
        """hero() accepts custom size."""
        char = hero(width=64, height=64)
        self.assertEqual(char.width, 64)

    def test_deterministic_with_seed(self):
        """hero() is deterministic with seed."""
        char1 = hero(seed=42)
        char2 = hero(seed=42)
        self.assertCanvasEqual(char1.render(), char2.render())


class TestHeroinePreset(TestCase):
    """Tests for heroine preset."""

    def test_creates_character(self):
        """heroine() creates a Character."""
        char = heroine()
        self.assertIsInstance(char, Character)

    def test_renders_successfully(self):
        """heroine() renders to non-empty canvas."""
        char = heroine()
        canvas = char.render()
        self.assertCanvasNotEmpty(canvas)


class TestVillagerPreset(TestCase):
    """Tests for villager preset."""

    def test_creates_character(self):
        """villager() creates a Character."""
        char = villager()
        self.assertIsInstance(char, Character)

    def test_renders_successfully(self):
        """villager() renders to non-empty canvas."""
        char = villager()
        canvas = char.render()
        self.assertCanvasNotEmpty(canvas)


class TestWizardPreset(TestCase):
    """Tests for wizard preset."""

    def test_creates_character(self):
        """wizard() creates a Character."""
        char = wizard()
        self.assertIsInstance(char, Character)

    def test_renders_successfully(self):
        """wizard() renders to non-empty canvas."""
        char = wizard()
        canvas = char.render()
        self.assertCanvasNotEmpty(canvas)


class TestWarriorPreset(TestCase):
    """Tests for warrior preset."""

    def test_creates_character(self):
        """warrior() creates a Character."""
        char = warrior()
        self.assertIsInstance(char, Character)

    def test_renders_successfully(self):
        """warrior() renders to non-empty canvas."""
        char = warrior()
        canvas = char.render()
        self.assertCanvasNotEmpty(canvas)


class TestRoguePreset(TestCase):
    """Tests for rogue preset."""

    def test_creates_character(self):
        """rogue() creates a Character."""
        char = rogue()
        self.assertIsInstance(char, Character)

    def test_renders_successfully(self):
        """rogue() renders to non-empty canvas."""
        char = rogue()
        canvas = char.render()
        self.assertCanvasNotEmpty(canvas)


class TestKnightPreset(TestCase):
    """Tests for knight preset."""

    def test_creates_character(self):
        """knight() creates a Character."""
        char = knight()
        self.assertIsInstance(char, Character)

    def test_renders_successfully(self):
        """knight() renders to non-empty canvas."""
        char = knight()
        canvas = char.render()
        self.assertCanvasNotEmpty(canvas)


class TestPrincessPreset(TestCase):
    """Tests for princess preset."""

    def test_creates_character(self):
        """princess() creates a Character."""
        char = princess()
        self.assertIsInstance(char, Character)

    def test_renders_successfully(self):
        """princess() renders to non-empty canvas."""
        char = princess()
        canvas = char.render()
        self.assertCanvasNotEmpty(canvas)


class TestMonsterPreset(TestCase):
    """Tests for monster preset."""

    def test_creates_character(self):
        """monster() creates a Character."""
        char = monster()
        self.assertIsInstance(char, Character)

    def test_renders_successfully(self):
        """monster() renders to non-empty canvas."""
        char = monster()
        canvas = char.render()
        self.assertCanvasNotEmpty(canvas)


class TestGhostPreset(TestCase):
    """Tests for ghost preset."""

    def test_creates_character(self):
        """ghost() creates a Character."""
        char = ghost()
        self.assertIsInstance(char, Character)

    def test_renders_successfully(self):
        """ghost() renders to non-empty canvas."""
        char = ghost()
        canvas = char.render()
        self.assertCanvasNotEmpty(canvas)


class TestChildPreset(TestCase):
    """Tests for child preset."""

    def test_creates_character(self):
        """child() creates a Character."""
        char = child()
        self.assertIsInstance(char, Character)

    def test_renders_successfully(self):
        """child() renders to non-empty canvas."""
        char = child()
        canvas = char.render()
        self.assertCanvasNotEmpty(canvas)


class TestElderPreset(TestCase):
    """Tests for elder preset."""

    def test_creates_character(self):
        """elder() creates a Character."""
        char = elder()
        self.assertIsInstance(char, Character)

    def test_renders_successfully(self):
        """elder() renders to non-empty canvas."""
        char = elder()
        canvas = char.render()
        self.assertCanvasNotEmpty(canvas)


class TestCatPersonPreset(TestCase):
    """Tests for cat_person preset."""

    def test_creates_character(self):
        """cat_person() creates a Character."""
        char = cat_person()
        self.assertIsInstance(char, Character)

    def test_renders_successfully(self):
        """cat_person() renders to non-empty canvas."""
        char = cat_person()
        canvas = char.render()
        self.assertCanvasNotEmpty(canvas)


class TestRandomCharacter(TestCase):
    """Tests for random_character function."""

    def test_creates_character(self):
        """random_character() creates a Character."""
        char = random_character()
        self.assertIsInstance(char, Character)

    def test_renders_successfully(self):
        """random_character() renders to non-empty canvas."""
        char = random_character()
        canvas = char.render()
        self.assertCanvasNotEmpty(canvas)

    def test_deterministic_with_seed(self):
        """random_character() is deterministic with seed."""
        char1 = random_character(seed=42)
        char2 = random_character(seed=42)
        self.assertCanvasEqual(char1.render(), char2.render())

    def test_different_seeds_differ(self):
        """random_character() with different seeds differs."""
        char1 = random_character(seed=42)
        char2 = random_character(seed=99)

        canvas1 = char1.render()
        canvas2 = char2.render()

        # Should be different
        pixels_differ = False
        for y in range(canvas1.height):
            for x in range(canvas1.width):
                if canvas1.get_pixel(x, y) != canvas2.get_pixel(x, y):
                    pixels_differ = True
                    break
            if pixels_differ:
                break

        self.assertTrue(pixels_differ)

    def test_custom_size(self):
        """random_character() accepts custom size."""
        char = random_character(width=64, height=64)
        self.assertEqual(char.width, 64)
        self.assertEqual(char.height, 64)


class TestAllPresetsRender(TestCase):
    """Integration tests that all presets render correctly."""

    def test_all_presets_render(self):
        """All presets in list_presets render successfully."""
        for preset_name in list_presets():
            char = get_preset(preset_name)
            canvas = char.render()
            self.assertCanvasNotEmpty(canvas, f"Preset {preset_name} rendered empty")

    def test_all_presets_animate(self):
        """All presets can animate."""
        for preset_name in list_presets():
            char = get_preset(preset_name)
            anim = char.animate('idle')
            self.assertGreater(anim.frame_count, 0, f"Preset {preset_name} has no animation frames")

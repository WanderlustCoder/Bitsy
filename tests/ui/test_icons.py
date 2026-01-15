"""
Test Icons - Tests for icon generation.

Tests:
- create_icon function
- IconGenerator class
- Icon presets and types
- Color palettes
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests.framework import TestCase
from ui import create_icon, IconGenerator, list_icons, IconPalette
from core import Canvas


class TestCreateIcon(TestCase):
    """Tests for create_icon function."""

    def test_create_heart(self):
        """create_icon('heart') produces heart icon."""
        result = create_icon('heart')
        self.assertIsInstance(result, Canvas)
        self.assertCanvasNotEmpty(result)

    def test_create_star(self):
        """create_icon('star') produces star icon."""
        result = create_icon('star')
        self.assertIsInstance(result, Canvas)
        self.assertCanvasNotEmpty(result)

    def test_create_with_size(self):
        """create_icon respects size parameter."""
        result = create_icon('heart', size=24)
        self.assertEqual(result.width, 24)
        self.assertEqual(result.height, 24)

    def test_create_with_palette(self):
        """create_icon accepts palette parameter."""
        palette = IconPalette.red()
        result = create_icon('heart', size=16, palette=palette)
        self.assertIsInstance(result, Canvas)
        self.assertCanvasNotEmpty(result)

    def test_all_listed_icons(self):
        """All listed icons can be created."""
        icons = list_icons()
        for icon_name in icons:
            try:
                result = create_icon(icon_name)
                self.assertIsInstance(result, Canvas)
            except Exception as e:
                self.fail(f"Failed to create icon '{icon_name}': {e}")


class TestIconGenerator(TestCase):
    """Tests for IconGenerator class."""

    def test_create_generator(self):
        """IconGenerator can be created."""
        gen = IconGenerator(size=16)
        self.assertEqual(gen.size, 16)

    def test_generate_heart(self):
        """IconGenerator can generate heart."""
        gen = IconGenerator(size=16)
        result = gen.heart()
        self.assertIsInstance(result, Canvas)
        self.assertCanvasNotEmpty(result)

    def test_generate_star(self):
        """IconGenerator can generate star."""
        gen = IconGenerator(size=16)
        result = gen.star()
        self.assertIsInstance(result, Canvas)
        self.assertCanvasNotEmpty(result)

    def test_generate_checkmark(self):
        """IconGenerator can generate checkmark."""
        gen = IconGenerator(size=16)
        result = gen.checkmark()
        self.assertIsInstance(result, Canvas)
        self.assertCanvasNotEmpty(result)

    def test_generate_cross(self):
        """IconGenerator can generate cross."""
        gen = IconGenerator(size=16)
        result = gen.cross()
        self.assertIsInstance(result, Canvas)
        self.assertCanvasNotEmpty(result)

    def test_generate_arrows(self):
        """IconGenerator can generate arrow icons."""
        gen = IconGenerator(size=16)

        # Test arrow methods
        result_right = gen.arrow_right()
        result_left = gen.arrow_left()
        result_up = gen.arrow_up()
        result_down = gen.arrow_down()

        for result in [result_right, result_left, result_up, result_down]:
            self.assertIsInstance(result, Canvas)
            self.assertCanvasNotEmpty(result)

    def test_set_palette(self):
        """IconGenerator respects palette setting."""
        palette = IconPalette.red()
        gen = IconGenerator(size=16, palette=palette)
        result = gen.heart()
        self.assertCanvasNotEmpty(result)


class TestIconPalette(TestCase):
    """Tests for icon color palettes."""

    def test_default_palette(self):
        """Default icon palette exists."""
        palette = IconPalette.default()
        self.assertIsNotNone(palette)
        self.assertIsNotNone(palette.primary)
        self.assertIsNotNone(palette.secondary)

    def test_red_palette(self):
        """Red palette has red tones."""
        palette = IconPalette.red()
        # Should be reddish
        self.assertGreater(palette.primary[0], palette.primary[2])

    def test_green_palette(self):
        """Green palette has green tones."""
        palette = IconPalette.green()
        # Should be greenish
        self.assertGreater(palette.primary[1], palette.primary[2])

    def test_gold_palette(self):
        """Gold palette has yellow/gold tones."""
        palette = IconPalette.gold()
        # Should be gold-ish (R > B)
        self.assertGreater(palette.primary[0], palette.primary[2])

    def test_blue_palette(self):
        """Blue palette has blue tones."""
        palette = IconPalette.blue()
        # Should be bluish
        self.assertGreater(palette.primary[2], palette.primary[1])


class TestListIcons(TestCase):
    """Tests for list_icons function."""

    def test_returns_list(self):
        """list_icons returns a list."""
        icons = list_icons()
        self.assertIsInstance(icons, list)

    def test_has_standard_icons(self):
        """list_icons includes standard icons."""
        icons = list_icons()
        expected = ['heart', 'star', 'checkmark', 'cross', 'gear']
        for icon in expected:
            self.assertIn(icon, icons)

    def test_icons_are_strings(self):
        """All icon names are strings."""
        icons = list_icons()
        for icon in icons:
            self.assertIsInstance(icon, str)


class TestIconOutput(TestCase):
    """Tests for icon output quality."""

    def test_icons_have_content(self):
        """Icons fill reasonable portion of canvas."""
        for name in ['heart', 'star', 'gear']:
            result = create_icon(name, size=16)

            opaque = sum(
                1 for y in range(result.height)
                for x in range(result.width)
                if result.pixels[y][x][3] > 0
            )

            fill_ratio = opaque / (result.width * result.height)
            self.assertGreater(fill_ratio, 0.15,
                              f"Icon '{name}' only fills {fill_ratio:.1%}")

    def test_icons_centered(self):
        """Icons are approximately centered."""
        result = create_icon('heart', size=16)

        # Find bounding box
        min_x, max_x = 16, 0
        min_y, max_y = 16, 0

        for y in range(result.height):
            for x in range(result.width):
                if result.pixels[y][x][3] > 0:
                    min_x = min(min_x, x)
                    max_x = max(max_x, x)
                    min_y = min(min_y, y)
                    max_y = max(max_y, y)

        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2

        # Should be close to canvas center
        self.assertAlmostEqual(center_x, 7.5, delta=3)
        self.assertAlmostEqual(center_y, 7.5, delta=3)

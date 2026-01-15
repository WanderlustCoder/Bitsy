"""
Test Palette - Tests for palette management.

Tests:
- Palette creation and manipulation
- Color ramps and gradients
- Quantization
- Preset palettes
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests.framework import TestCase
from core import Palette


class TestPaletteBasics(TestCase):
    """Tests for basic palette operations."""

    def test_create_empty(self):
        """Palette can be created empty."""
        palette = Palette()
        self.assertEqual(len(palette), 0)

    def test_create_with_colors(self):
        """Palette can be created with initial colors."""
        colors = [(255, 0, 0, 255), (0, 255, 0, 255), (0, 0, 255, 255)]
        palette = Palette(colors)
        self.assertEqual(len(palette), 3)

    def test_add_color(self):
        """add() appends color to palette."""
        palette = Palette()
        palette.add((255, 0, 0, 255))
        self.assertEqual(len(palette), 1)
        self.assertEqual(palette.colors[0], (255, 0, 0, 255))

    def test_add_returns_self(self):
        """add() returns self for chaining."""
        palette = Palette()
        result = palette.add((255, 0, 0, 255))
        self.assertIs(result, palette)

    def test_add_hex(self):
        """add_hex() adds color from hex string."""
        palette = Palette()
        palette.add_hex('#ff0000')
        self.assertEqual(palette.colors[0][:3], (255, 0, 0))

    def test_method_chaining(self):
        """Methods can be chained."""
        palette = Palette().add((255, 0, 0, 255)).add_hex('#00ff00').add((0, 0, 255, 255))
        self.assertEqual(len(palette), 3)

    def test_get_valid_index(self):
        """get() returns color at index."""
        palette = Palette([(255, 0, 0, 255), (0, 255, 0, 255)])
        self.assertEqual(palette.get(0), (255, 0, 0, 255))
        self.assertEqual(palette.get(1), (0, 255, 0, 255))

    def test_get_wraps_index(self):
        """get() wraps around for out-of-bounds index."""
        palette = Palette([(255, 0, 0, 255), (0, 255, 0, 255)])
        self.assertEqual(palette.get(2), palette.get(0))
        self.assertEqual(palette.get(3), palette.get(1))

    def test_iteration(self):
        """Palette supports iteration."""
        colors = [(255, 0, 0, 255), (0, 255, 0, 255)]
        palette = Palette(colors)

        result = list(palette)
        self.assertEqual(result, colors)


class TestPaletteQuantization(TestCase):
    """Tests for palette quantization."""

    def test_find_nearest_exact_match(self):
        """find_nearest returns index of exact match."""
        palette = Palette([(255, 0, 0, 255), (0, 255, 0, 255), (0, 0, 255, 255)])
        self.assertEqual(palette.find_nearest((0, 255, 0, 255)), 1)

    def test_find_nearest_closest(self):
        """find_nearest returns index of closest color."""
        palette = Palette([(0, 0, 0, 255), (255, 255, 255, 255)])
        # Should find white as nearest to light gray
        self.assertEqual(palette.find_nearest((200, 200, 200, 255)), 1)
        # Should find black as nearest to dark gray
        self.assertEqual(palette.find_nearest((50, 50, 50, 255)), 0)

    def test_quantize(self):
        """quantize returns nearest palette color."""
        palette = Palette([(255, 0, 0, 255), (0, 0, 255, 255)])
        # Pink should quantize to red
        result = palette.quantize((200, 100, 100, 255))
        self.assertEqual(result, (255, 0, 0, 255))


class TestPaletteRamps(TestCase):
    """Tests for color ramp generation."""

    def test_create_ramp_count(self):
        """create_ramp creates correct number of colors."""
        palette = Palette()
        palette.create_ramp((0, 0, 0, 255), (255, 255, 255, 255), 5)
        self.assertEqual(len(palette), 5)

    def test_create_ramp_endpoints(self):
        """create_ramp includes start and end colors."""
        palette = Palette()
        palette.create_ramp((0, 0, 0, 255), (255, 255, 255, 255), 5)
        self.assertEqual(palette.colors[0], (0, 0, 0, 255))
        self.assertEqual(palette.colors[4], (255, 255, 255, 255))

    def test_create_ramp_gradient(self):
        """create_ramp creates smooth gradient."""
        palette = Palette()
        palette.create_ramp((0, 0, 0, 255), (100, 100, 100, 255), 3)

        # Middle color should be halfway
        mid = palette.colors[1]
        self.assertEqual(mid, (50, 50, 50, 255))

    def test_create_hue_ramp(self):
        """create_hue_ramp creates colors with hue shift."""
        palette = Palette()
        base = (255, 128, 128, 255)  # Light red/pink
        palette.create_hue_ramp(base, hue_shift=60, value_range=(1.0, 0.5), steps=3)

        self.assertEqual(len(palette), 3)

        # First color should be similar to base
        # Last color should be darker and hue-shifted


class TestPaletteShifting(TestCase):
    """Tests for palette-wide color shifting."""

    def test_shift_all_hue(self):
        """shift_all shifts hue of all colors."""
        palette = Palette([(255, 0, 0, 255)])  # Red
        shifted = palette.shift_all(hue_degrees=120)

        # Should be green-ish now
        self.assertGreater(shifted.colors[0][1], shifted.colors[0][0])

    def test_shift_all_saturation(self):
        """shift_all adjusts saturation."""
        palette = Palette([(255, 128, 128, 255)])  # Light red
        desaturated = palette.shift_all(sat_factor=0.0)

        # Should be grayscale
        c = desaturated.colors[0]
        self.assertAlmostEqual(c[0], c[1], delta=2)
        self.assertAlmostEqual(c[1], c[2], delta=2)

    def test_shift_all_value(self):
        """shift_all adjusts value/brightness."""
        palette = Palette([(100, 100, 100, 255)])
        brightened = palette.shift_all(val_factor=2.0)
        darkened = palette.shift_all(val_factor=0.5)

        self.assertGreater(brightened.colors[0][0], 100)
        self.assertLess(darkened.colors[0][0], 100)

    def test_shift_all_returns_new_palette(self):
        """shift_all returns new palette, doesn't modify original."""
        original = Palette([(255, 0, 0, 255)])
        shifted = original.shift_all(hue_degrees=180)

        self.assertIsNot(shifted, original)
        self.assertEqual(original.colors[0], (255, 0, 0, 255))


class TestPalettePresets(TestCase):
    """Tests for preset palettes."""

    def test_skin_warm_exists(self):
        """skin_warm preset exists and has colors."""
        palette = Palette.skin_warm()
        self.assertGreater(len(palette), 0)
        self.assertEqual(palette.name, "Skin Warm")

    def test_skin_cool_exists(self):
        """skin_cool preset exists and has colors."""
        palette = Palette.skin_cool()
        self.assertGreater(len(palette), 0)

    def test_hair_lavender_exists(self):
        """hair_lavender preset exists and has colors."""
        palette = Palette.hair_lavender()
        self.assertGreater(len(palette), 0)

    def test_hair_brown_exists(self):
        """hair_brown preset exists and has colors."""
        palette = Palette.hair_brown()
        self.assertGreater(len(palette), 0)

    def test_cloth_blue_exists(self):
        """cloth_blue preset exists and has colors."""
        palette = Palette.cloth_blue()
        self.assertGreater(len(palette), 0)

    def test_metal_gold_exists(self):
        """metal_gold preset exists and has colors."""
        palette = Palette.metal_gold()
        self.assertGreater(len(palette), 0)

    def test_retro_nes_exists(self):
        """retro_nes preset exists and has colors."""
        palette = Palette.retro_nes()
        self.assertGreater(len(palette), 0)

    def test_preset_colors_valid(self):
        """Preset palette colors are valid RGBA tuples."""
        palette = Palette.skin_warm()
        for color in palette:
            self.assertEqual(len(color), 4)
            for channel in color:
                self.assertGreaterEqual(channel, 0)
                self.assertLessEqual(channel, 255)

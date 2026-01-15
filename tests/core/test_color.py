"""
Test Color - Tests for color operations and blend modes.

Tests:
- Color conversion (hex, HSV, HSL)
- Color interpolation
- Color adjustments (hue, saturation, value, lightness)
- Blend modes
- Dithering
- Color distance and comparison
"""

import sys
import os
import math

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests.framework import TestCase
from core import (
    # Conversion
    hex_to_rgba, rgba_to_hex, rgb_to_hsv, hsv_to_rgb, rgb_to_hsl, hsl_to_rgb,
    # Interpolation
    lerp_color, lerp_color_hsv,
    # Adjustments
    shift_hue, adjust_saturation, adjust_value, adjust_lightness,
    grayscale, invert, darken, lighten, with_alpha, premultiply_alpha,
    # Blend modes
    blend_normal, blend_multiply, blend_screen, blend_overlay,
    blend_add, blend_subtract, blend_difference, blend, BLEND_MODES,
    # Dithering
    dither_threshold, dither_color, quantize_with_dither,
    # Distance
    color_distance_rgb, color_distance_weighted, colors_similar,
    # Utilities
    color_to_float, float_to_color,
    # Constants
    TRANSPARENT, BLACK, WHITE, RED, GREEN, BLUE
)


class TestColorConversion(TestCase):
    """Tests for color format conversion."""

    def test_hex_to_rgba_6digit(self):
        """hex_to_rgba converts 6-digit hex correctly."""
        color = hex_to_rgba('#ff0000')
        self.assertEqual(color, (255, 0, 0, 255))

    def test_hex_to_rgba_8digit(self):
        """hex_to_rgba converts 8-digit hex (with alpha) correctly."""
        color = hex_to_rgba('#ff000080')
        self.assertEqual(color, (255, 0, 0, 128))

    def test_hex_to_rgba_no_hash(self):
        """hex_to_rgba works without # prefix."""
        color = hex_to_rgba('00ff00')
        self.assertEqual(color, (0, 255, 0, 255))

    def test_hex_to_rgba_custom_alpha(self):
        """hex_to_rgba uses provided alpha."""
        color = hex_to_rgba('#ffffff', alpha=128)
        self.assertEqual(color, (255, 255, 255, 128))

    def test_rgba_to_hex_rgb_only(self):
        """rgba_to_hex produces 6-digit hex by default."""
        hex_str = rgba_to_hex((255, 128, 64, 255))
        self.assertEqual(hex_str, '#ff8040')

    def test_rgba_to_hex_with_alpha(self):
        """rgba_to_hex includes alpha when requested."""
        hex_str = rgba_to_hex((255, 128, 64, 128), include_alpha=True)
        self.assertEqual(hex_str, '#ff804080')

    def test_rgb_to_hsv_red(self):
        """rgb_to_hsv converts red correctly."""
        h, s, v = rgb_to_hsv(255, 0, 0)
        self.assertAlmostEqual(h, 0, places=1)
        self.assertAlmostEqual(s, 1.0, places=2)
        self.assertAlmostEqual(v, 1.0, places=2)

    def test_rgb_to_hsv_green(self):
        """rgb_to_hsv converts green correctly."""
        h, s, v = rgb_to_hsv(0, 255, 0)
        self.assertAlmostEqual(h, 120, places=1)

    def test_rgb_to_hsv_blue(self):
        """rgb_to_hsv converts blue correctly."""
        h, s, v = rgb_to_hsv(0, 0, 255)
        self.assertAlmostEqual(h, 240, places=1)

    def test_rgb_to_hsv_gray(self):
        """rgb_to_hsv converts gray (no saturation) correctly."""
        h, s, v = rgb_to_hsv(128, 128, 128)
        self.assertAlmostEqual(s, 0, places=2)

    def test_hsv_to_rgb_roundtrip(self):
        """hsv_to_rgb(rgb_to_hsv()) preserves color."""
        original = (200, 100, 50)
        h, s, v = rgb_to_hsv(*original)
        result = hsv_to_rgb(h, s, v)
        self.assertColorClose((result[0], result[1], result[2], 255),
                             (original[0], original[1], original[2], 255),
                             tolerance=1)

    def test_hsl_roundtrip(self):
        """hsl_to_rgb(rgb_to_hsl()) preserves color."""
        original = (150, 75, 200)
        h, s, l = rgb_to_hsl(*original)
        result = hsl_to_rgb(h, s, l)
        self.assertColorClose((result[0], result[1], result[2], 255),
                             (original[0], original[1], original[2], 255),
                             tolerance=2)


class TestColorInterpolation(TestCase):
    """Tests for color interpolation."""

    def test_lerp_color_t0(self):
        """lerp_color at t=0 returns first color."""
        result = lerp_color(RED, BLUE, 0.0)
        self.assertEqual(result, RED)

    def test_lerp_color_t1(self):
        """lerp_color at t=1 returns second color."""
        result = lerp_color(RED, BLUE, 1.0)
        self.assertEqual(result, BLUE)

    def test_lerp_color_t05(self):
        """lerp_color at t=0.5 blends colors equally."""
        result = lerp_color((0, 0, 0, 255), (100, 200, 100, 255), 0.5)
        self.assertEqual(result, (50, 100, 50, 255))

    def test_lerp_color_clamps_t(self):
        """lerp_color clamps t to [0, 1]."""
        result_neg = lerp_color(RED, BLUE, -0.5)
        result_over = lerp_color(RED, BLUE, 1.5)
        self.assertEqual(result_neg, RED)
        self.assertEqual(result_over, BLUE)

    def test_lerp_color_hsv_hue_wrap(self):
        """lerp_color_hsv takes shortest hue path."""
        # Red (0) to Blue (240) should go through magenta
        # Going backwards: 0 -> 300 -> 240
        result = lerp_color_hsv(RED, BLUE, 0.5)
        # Should be somewhere in magenta range (270-330)
        h, s, v = rgb_to_hsv(result[0], result[1], result[2])
        self.assertTrue(250 < h < 310 or h < 60)  # Account for wrap


class TestColorAdjustments(TestCase):
    """Tests for color adjustment functions."""

    def test_shift_hue(self):
        """shift_hue rotates hue correctly."""
        # Red shifted 120 degrees should be green-ish
        result = shift_hue(RED, 120)
        self.assertGreater(result[1], result[0])  # Green > Red

    def test_shift_hue_preserves_alpha(self):
        """shift_hue preserves alpha channel."""
        result = shift_hue((255, 0, 0, 128), 90)
        self.assertEqual(result[3], 128)

    def test_adjust_saturation_zero(self):
        """adjust_saturation(0) produces grayscale."""
        result = adjust_saturation(RED, 0)
        self.assertEqual(result[0], result[1])
        self.assertEqual(result[1], result[2])

    def test_adjust_saturation_preserves_gray(self):
        """adjust_saturation has no effect on gray."""
        gray = (128, 128, 128, 255)
        result = adjust_saturation(gray, 2.0)
        self.assertColorClose(result, gray, tolerance=1)

    def test_adjust_value_darken(self):
        """adjust_value < 1 darkens color."""
        result = adjust_value((200, 100, 50, 255), 0.5)
        self.assertLess(result[0], 200)
        self.assertLess(result[1], 100)

    def test_adjust_value_brighten(self):
        """adjust_value > 1 brightens color (clamped)."""
        result = adjust_value((100, 50, 25, 255), 2.0)
        self.assertGreater(result[0], 100)

    def test_adjust_lightness_lighten(self):
        """adjust_lightness positive value lightens."""
        result = adjust_lightness((100, 100, 100, 255), 0.3)
        self.assertGreater(result[0], 100)

    def test_adjust_lightness_darken(self):
        """adjust_lightness negative value darkens."""
        result = adjust_lightness((200, 200, 200, 255), -0.3)
        self.assertLess(result[0], 200)

    def test_grayscale(self):
        """grayscale converts to gray with correct luminance."""
        result = grayscale(RED)
        # All channels should be equal
        self.assertEqual(result[0], result[1])
        self.assertEqual(result[1], result[2])
        # And preserve alpha
        self.assertEqual(result[3], 255)

    def test_grayscale_luminance_weights(self):
        """grayscale uses proper luminance weights."""
        # Green contributes most to luminance
        gray_r = grayscale((255, 0, 0, 255))
        gray_g = grayscale((0, 255, 0, 255))
        gray_b = grayscale((0, 0, 255, 255))
        self.assertGreater(gray_g[0], gray_r[0])
        self.assertGreater(gray_g[0], gray_b[0])

    def test_invert(self):
        """invert produces color negative."""
        result = invert((100, 150, 200, 255))
        self.assertEqual(result, (155, 105, 55, 255))

    def test_invert_preserves_alpha(self):
        """invert preserves alpha channel."""
        result = invert((100, 100, 100, 128))
        self.assertEqual(result[3], 128)

    def test_darken(self):
        """darken reduces brightness."""
        result = darken((200, 100, 50, 255), 0.5)
        self.assertEqual(result, (100, 50, 25, 255))

    def test_darken_full(self):
        """darken(1.0) produces black."""
        result = darken(WHITE, 1.0)
        self.assertEqual(result[:3], (0, 0, 0))

    def test_lighten(self):
        """lighten increases brightness."""
        result = lighten((100, 100, 100, 255), 0.5)
        self.assertGreater(result[0], 100)

    def test_lighten_full(self):
        """lighten(1.0) produces white."""
        result = lighten(BLACK, 1.0)
        self.assertEqual(result[:3], (255, 255, 255))

    def test_with_alpha(self):
        """with_alpha creates color with new alpha."""
        result = with_alpha(RED, 128)
        self.assertEqual(result, (255, 0, 0, 128))

    def test_with_alpha_clamps(self):
        """with_alpha clamps alpha to valid range."""
        result = with_alpha(RED, 300)
        self.assertEqual(result[3], 255)

    def test_premultiply_alpha(self):
        """premultiply_alpha multiplies RGB by alpha."""
        result = premultiply_alpha((200, 100, 50, 128))
        expected_factor = 128 / 255.0
        self.assertAlmostEqual(result[0], int(200 * expected_factor), delta=1)


class TestBlendModes(TestCase):
    """Tests for blend mode functions."""

    def test_blend_normal_opaque(self):
        """blend_normal with opaque overlay replaces base."""
        result = blend_normal(WHITE, RED)
        self.assertEqual(result, RED)

    def test_blend_normal_transparent(self):
        """blend_normal with transparent overlay keeps base."""
        result = blend_normal(WHITE, TRANSPARENT)
        self.assertEqual(result, WHITE)

    def test_blend_normal_semi_transparent(self):
        """blend_normal blends semi-transparent colors."""
        result = blend_normal((0, 0, 0, 255), (255, 0, 0, 128))
        self.assertGreater(result[0], 100)
        self.assertLess(result[0], 200)

    def test_blend_multiply_darkens(self):
        """blend_multiply darkens image."""
        result = blend_multiply(WHITE, (128, 128, 128, 255))
        self.assertEqual(result[:3], (128, 128, 128))

    def test_blend_multiply_with_black(self):
        """blend_multiply with black produces black."""
        result = blend_multiply(WHITE, BLACK)
        self.assertEqual(result[:3], (0, 0, 0))

    def test_blend_screen_lightens(self):
        """blend_screen lightens image."""
        result = blend_screen((100, 100, 100, 255), (100, 100, 100, 255))
        self.assertGreater(result[0], 100)

    def test_blend_screen_with_white(self):
        """blend_screen with white produces white."""
        result = blend_screen(BLACK, WHITE)
        self.assertEqual(result[:3], (255, 255, 255))

    def test_blend_overlay_contrast(self):
        """blend_overlay increases contrast."""
        # Dark areas get darker
        dark = blend_overlay((50, 50, 50, 255), (128, 128, 128, 255))
        # Light areas get lighter
        light = blend_overlay((200, 200, 200, 255), (128, 128, 128, 255))
        self.assertLess(dark[0], 128)
        self.assertGreater(light[0], 128)

    def test_blend_add(self):
        """blend_add adds colors (clamped)."""
        result = blend_add((100, 100, 100, 255), (100, 100, 100, 255))
        self.assertEqual(result[:3], (200, 200, 200))

    def test_blend_add_clamps(self):
        """blend_add clamps at 255."""
        result = blend_add((200, 200, 200, 255), (200, 200, 200, 255))
        self.assertEqual(result[:3], (255, 255, 255))

    def test_blend_subtract(self):
        """blend_subtract subtracts colors (clamped)."""
        result = blend_subtract((200, 200, 200, 255), (50, 50, 50, 255))
        self.assertEqual(result[:3], (150, 150, 150))

    def test_blend_difference(self):
        """blend_difference shows absolute difference."""
        result = blend_difference((200, 100, 50, 255), (100, 150, 100, 255))
        self.assertAlmostEqual(result[0], 100, delta=10)
        self.assertAlmostEqual(result[1], 50, delta=10)
        self.assertAlmostEqual(result[2], 50, delta=10)

    def test_blend_function_by_name(self):
        """blend() selects correct mode by name."""
        result = blend(WHITE, (128, 128, 128, 255), 'multiply')
        expected = blend_multiply(WHITE, (128, 128, 128, 255))
        self.assertEqual(result, expected)

    def test_blend_modes_dict(self):
        """BLEND_MODES contains all standard modes."""
        expected_modes = ['normal', 'multiply', 'screen', 'overlay',
                         'add', 'subtract', 'difference']
        for mode in expected_modes:
            self.assertIn(mode, BLEND_MODES)


class TestDithering(TestCase):
    """Tests for dithering functions."""

    def test_dither_threshold_bayer4x4_range(self):
        """dither_threshold returns values in [0, 1)."""
        for y in range(4):
            for x in range(4):
                threshold = dither_threshold(x, y, 'bayer4x4')
                self.assertGreaterEqual(threshold, 0.0)
                self.assertLess(threshold, 1.0)

    def test_dither_threshold_checker_pattern(self):
        """dither_threshold checker creates alternating pattern."""
        t00 = dither_threshold(0, 0, 'checker')
        t01 = dither_threshold(0, 1, 'checker')
        t10 = dither_threshold(1, 0, 'checker')
        t11 = dither_threshold(1, 1, 'checker')
        # Alternating
        self.assertEqual(t00, t11)
        self.assertEqual(t01, t10)
        self.assertNotEqual(t00, t01)

    def test_dither_color(self):
        """dither_color chooses between two colors."""
        c1 = (0, 0, 0, 255)
        c2 = (255, 255, 255, 255)

        # With ratio=0, should always return c1
        for y in range(4):
            for x in range(4):
                result = dither_color(c1, c2, x, y, 0.0)
                self.assertEqual(result, c1)

        # With ratio=1, should always return c2
        for y in range(4):
            for x in range(4):
                result = dither_color(c1, c2, x, y, 1.0)
                self.assertEqual(result, c2)

    def test_quantize_with_dither_single_color(self):
        """quantize_with_dither with one-color palette returns that color."""
        palette = [(128, 128, 128, 255)]
        result = quantize_with_dither((200, 100, 50, 255), palette, 0, 0)
        self.assertEqual(result, palette[0])


class TestColorDistance(TestCase):
    """Tests for color distance and comparison."""

    def test_color_distance_rgb_same(self):
        """color_distance_rgb of same color is 0."""
        dist = color_distance_rgb(RED, RED)
        self.assertEqual(dist, 0)

    def test_color_distance_rgb_black_white(self):
        """color_distance_rgb black to white is maximum."""
        dist = color_distance_rgb(BLACK, WHITE)
        expected = math.sqrt(255**2 * 3)
        self.assertAlmostEqual(dist, expected, places=1)

    def test_colors_similar_identical(self):
        """colors_similar returns True for identical colors."""
        self.assertTrue(colors_similar(RED, RED))

    def test_colors_similar_different(self):
        """colors_similar returns False for very different colors."""
        self.assertFalse(colors_similar(RED, BLUE))

    def test_colors_similar_threshold(self):
        """colors_similar respects threshold."""
        similar = (250, 5, 5, 255)
        self.assertTrue(colors_similar(RED, similar, threshold=20))
        self.assertFalse(colors_similar(RED, similar, threshold=5))


class TestColorUtilities(TestCase):
    """Tests for utility functions."""

    def test_color_to_float(self):
        """color_to_float converts to 0-1 range."""
        result = color_to_float((255, 128, 0, 255))
        self.assertAlmostEqual(result[0], 1.0, places=2)
        self.assertAlmostEqual(result[1], 128/255, places=2)
        self.assertAlmostEqual(result[2], 0.0, places=2)

    def test_float_to_color(self):
        """float_to_color converts to 0-255 range."""
        result = float_to_color((1.0, 0.5, 0.0, 1.0))
        self.assertEqual(result[0], 255)
        self.assertAlmostEqual(result[1], 127, delta=1)
        self.assertEqual(result[2], 0)

    def test_color_float_roundtrip(self):
        """float_to_color(color_to_float()) preserves color."""
        original = (200, 100, 50, 128)
        result = float_to_color(color_to_float(original))
        self.assertEqual(result, original)


class TestColorConstants(TestCase):
    """Tests for color constants."""

    def test_transparent(self):
        """TRANSPARENT is fully transparent black."""
        self.assertEqual(TRANSPARENT, (0, 0, 0, 0))

    def test_black(self):
        """BLACK is opaque black."""
        self.assertEqual(BLACK, (0, 0, 0, 255))

    def test_white(self):
        """WHITE is opaque white."""
        self.assertEqual(WHITE, (255, 255, 255, 255))

    def test_primary_colors(self):
        """Primary color constants are correct."""
        self.assertEqual(RED, (255, 0, 0, 255))
        self.assertEqual(GREEN, (0, 255, 0, 255))
        self.assertEqual(BLUE, (0, 0, 255, 255))

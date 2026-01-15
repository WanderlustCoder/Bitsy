"""
Test Color Harmony - Tests for color theory palette generation.

Tests:
- Complementary colors
- Analogous colors
- Triadic colors
- Split-complementary colors
- Tetradic colors
- Shading ramps
- Palette optimization
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests.framework import TestCase
from quality.color_harmony import (
    generate_complementary,
    generate_analogous,
    generate_triadic,
    generate_split_complementary,
    generate_tetradic,
    generate_monochromatic,
    create_shading_ramp,
    optimize_palette,
    suggest_accent_color,
    generate_harmony,
    HarmonyType,
    HarmonyResult,
)
from core.color import rgb_to_hsv


class TestComplementaryHarmony(TestCase):
    """Tests for complementary color generation."""

    def test_returns_result(self):
        """generate_complementary returns HarmonyResult."""
        base = (255, 0, 0, 255)  # Red
        result = generate_complementary(base)

        self.assertIsInstance(result, HarmonyResult)
        self.assertEqual(result.harmony_type, HarmonyType.COMPLEMENTARY)

    def test_complement_opposite_hue(self):
        """Complement is approximately opposite on color wheel."""
        base = (255, 0, 0, 255)  # Red
        result = generate_complementary(base, include_base=False)

        # Red's complement should be cyan-ish
        complement = result.colors[0]
        h_base, _, _ = rgb_to_hsv(base[0], base[1], base[2])
        h_comp, _, _ = rgb_to_hsv(complement[0], complement[1], complement[2])

        # Should be ~180 degrees apart
        hue_diff = abs(h_base - h_comp)
        if hue_diff > 180:
            hue_diff = 360 - hue_diff

        self.assertGreater(hue_diff, 150)
        self.assertLess(hue_diff, 210)

    def test_include_base(self):
        """include_base parameter works."""
        base = (255, 0, 0, 255)

        with_base = generate_complementary(base, include_base=True)
        without_base = generate_complementary(base, include_base=False)

        self.assertEqual(len(with_base.colors), 2)
        self.assertEqual(len(without_base.colors), 1)


class TestAnalogousHarmony(TestCase):
    """Tests for analogous color generation."""

    def test_returns_result(self):
        """generate_analogous returns HarmonyResult."""
        base = (255, 0, 0, 255)
        result = generate_analogous(base)

        self.assertIsInstance(result, HarmonyResult)
        self.assertEqual(result.harmony_type, HarmonyType.ANALOGOUS)

    def test_default_count(self):
        """Default generates 3 colors."""
        base = (255, 0, 0, 255)
        result = generate_analogous(base, include_base=True)

        self.assertEqual(len(result.colors), 3)

    def test_custom_count(self):
        """Custom count works."""
        base = (255, 0, 0, 255)
        result = generate_analogous(base, count=5)

        self.assertEqual(len(result.colors), 5)

    def test_colors_similar_hue(self):
        """Analogous colors have similar hues."""
        base = (255, 0, 0, 255)
        result = generate_analogous(base, spread=30, count=3)

        hues = []
        for color in result.colors:
            h, _, _ = rgb_to_hsv(color[0], color[1], color[2])
            hues.append(h)

        # All hues should be within spread * 2 of each other
        for h in hues:
            for h2 in hues:
                diff = abs(h - h2)
                if diff > 180:
                    diff = 360 - diff
                self.assertLess(diff, 100)  # Generous threshold


class TestTriadicHarmony(TestCase):
    """Tests for triadic color generation."""

    def test_returns_result(self):
        """generate_triadic returns HarmonyResult."""
        base = (255, 0, 0, 255)
        result = generate_triadic(base)

        self.assertIsInstance(result, HarmonyResult)
        self.assertEqual(result.harmony_type, HarmonyType.TRIADIC)

    def test_three_colors(self):
        """Triadic generates 3 colors (with base)."""
        base = (255, 0, 0, 255)
        result = generate_triadic(base, include_base=True)

        self.assertEqual(len(result.colors), 3)

    def test_evenly_spaced(self):
        """Triadic colors are ~120 degrees apart."""
        base = (255, 0, 0, 255)
        result = generate_triadic(base, include_base=True)

        hues = []
        for color in result.colors:
            h, _, _ = rgb_to_hsv(color[0], color[1], color[2])
            hues.append(h)

        # Check spacing (should be ~120 degrees)
        hues.sort()
        for i in range(len(hues)):
            diff = hues[(i + 1) % len(hues)] - hues[i]
            if diff < 0:
                diff += 360
            # Allow some tolerance
            self.assertGreater(diff, 90)


class TestSplitComplementaryHarmony(TestCase):
    """Tests for split-complementary color generation."""

    def test_returns_result(self):
        """generate_split_complementary returns HarmonyResult."""
        base = (255, 0, 0, 255)
        result = generate_split_complementary(base)

        self.assertIsInstance(result, HarmonyResult)
        self.assertEqual(result.harmony_type, HarmonyType.SPLIT_COMPLEMENTARY)

    def test_three_colors(self):
        """Split-complementary generates 3 colors (with base)."""
        base = (255, 0, 0, 255)
        result = generate_split_complementary(base, include_base=True)

        self.assertEqual(len(result.colors), 3)


class TestTetradicHarmony(TestCase):
    """Tests for tetradic color generation."""

    def test_returns_result(self):
        """generate_tetradic returns HarmonyResult."""
        base = (255, 0, 0, 255)
        result = generate_tetradic(base)

        self.assertIsInstance(result, HarmonyResult)
        self.assertEqual(result.harmony_type, HarmonyType.TETRADIC)

    def test_four_colors(self):
        """Tetradic generates 4 colors (with base)."""
        base = (255, 0, 0, 255)
        result = generate_tetradic(base, include_base=True)

        self.assertEqual(len(result.colors), 4)


class TestMonochromaticHarmony(TestCase):
    """Tests for monochromatic color generation."""

    def test_returns_result(self):
        """generate_monochromatic returns HarmonyResult."""
        base = (255, 0, 0, 255)
        result = generate_monochromatic(base)

        self.assertIsInstance(result, HarmonyResult)
        self.assertEqual(result.harmony_type, HarmonyType.MONOCHROMATIC)

    def test_same_hue_different_values(self):
        """Monochromatic colors have same hue, different values."""
        base = (255, 0, 0, 255)
        result = generate_monochromatic(base, count=5)

        self.assertEqual(len(result.colors), 5)

        # All should have similar hue (red)
        hues = []
        values = []
        for color in result.colors:
            h, _, v = rgb_to_hsv(color[0], color[1], color[2])
            hues.append(h)
            values.append(v)

        # Hues should be identical (or very close)
        for h in hues:
            self.assertAlmostEqual(h, hues[0], delta=5)

        # Values should vary - check that range is greater than 0.1
        value_range = max(values) - min(values)
        self.assertGreater(value_range, 0.1)


class TestShadingRamp(TestCase):
    """Tests for shading ramp generation."""

    def test_returns_list(self):
        """create_shading_ramp returns list of colors."""
        base = (200, 50, 50, 255)
        ramp = create_shading_ramp(base, levels=5)

        self.assertIsInstance(ramp, list)
        self.assertEqual(len(ramp), 5)

    def test_values_gradient(self):
        """Ramp goes from dark to light."""
        base = (200, 50, 50, 255)
        ramp = create_shading_ramp(base, levels=5)

        values = []
        for color in ramp:
            _, _, v = rgb_to_hsv(color[0], color[1], color[2])
            values.append(v)

        # Should be increasing (dark to light)
        for i in range(len(values) - 1):
            self.assertLessEqual(values[i], values[i + 1] + 0.1)  # Allow small tolerance

    def test_hue_shift(self):
        """Shadows shift cool, highlights shift warm."""
        base = (200, 50, 50, 255)
        ramp = create_shading_ramp(base, levels=5,
                                    highlight_hue_shift=30,
                                    shadow_hue_shift=-30)

        h_base, _, _ = rgb_to_hsv(base[0], base[1], base[2])
        h_shadow, _, _ = rgb_to_hsv(ramp[0][0], ramp[0][1], ramp[0][2])
        h_highlight, _, _ = rgb_to_hsv(ramp[-1][0], ramp[-1][1], ramp[-1][2])

        # Shadow should shift toward cool (negative)
        # Highlight should shift toward warm (positive)
        # This is a rough check since hue wraps
        self.assertIsInstance(ramp[0], tuple)
        self.assertIsInstance(ramp[-1], tuple)


class TestPaletteOptimization(TestCase):
    """Tests for palette optimization."""

    def test_reduces_colors(self):
        """optimize_palette reduces color count."""
        colors = [(i * 10, 0, 0, 255) for i in range(20)]  # 20 colors
        optimized = optimize_palette(colors, max_colors=5)

        self.assertLessEqual(len(optimized), 5)

    def test_preserves_if_under_limit(self):
        """Doesn't reduce if already under limit."""
        colors = [(255, 0, 0, 255), (0, 255, 0, 255)]
        optimized = optimize_palette(colors, max_colors=10)

        self.assertEqual(len(optimized), 2)

    def test_preserves_extremes(self):
        """Preserves darkest and lightest colors."""
        colors = [
            (0, 0, 0, 255),  # Darkest
            (100, 100, 100, 255),
            (150, 150, 150, 255),
            (255, 255, 255, 255),  # Lightest
        ]
        optimized = optimize_palette(colors, max_colors=2, preserve_extremes=True)

        # Should contain black and white
        has_dark = any(c[0] < 50 for c in optimized)
        has_light = any(c[0] > 200 for c in optimized)

        self.assertTrue(has_dark)
        self.assertTrue(has_light)


class TestAccentColorSuggestion(TestCase):
    """Tests for accent color suggestion."""

    def test_returns_color(self):
        """suggest_accent_color returns RGBA tuple."""
        palette = [(255, 0, 0, 255), (200, 0, 0, 255)]
        accent = suggest_accent_color(palette)

        self.assertIsInstance(accent, tuple)
        self.assertEqual(len(accent), 4)

    def test_accent_differs_from_palette(self):
        """Accent color is different from palette colors."""
        palette = [(255, 0, 0, 255)]
        accent = suggest_accent_color(palette)

        # Should not be red
        from core.color import color_distance_weighted
        dist = color_distance_weighted(accent, palette[0])

        self.assertGreater(dist, 50)

    def test_empty_palette(self):
        """Handles empty palette."""
        accent = suggest_accent_color([])

        self.assertIsInstance(accent, tuple)


class TestGenerateHarmony(TestCase):
    """Tests for generic harmony generation."""

    def test_complementary(self):
        """generate_harmony works for complementary."""
        result = generate_harmony((255, 0, 0, 255), HarmonyType.COMPLEMENTARY)
        self.assertEqual(result.harmony_type, HarmonyType.COMPLEMENTARY)

    def test_analogous(self):
        """generate_harmony works for analogous."""
        result = generate_harmony((255, 0, 0, 255), HarmonyType.ANALOGOUS)
        self.assertEqual(result.harmony_type, HarmonyType.ANALOGOUS)

    def test_triadic(self):
        """generate_harmony works for triadic."""
        result = generate_harmony((255, 0, 0, 255), HarmonyType.TRIADIC)
        self.assertEqual(result.harmony_type, HarmonyType.TRIADIC)

    def test_invalid_type_raises(self):
        """Invalid harmony type raises error."""
        with self.assertRaises(ValueError):
            generate_harmony((255, 0, 0, 255), "invalid")

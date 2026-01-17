"""
Test Style Presets - Tests for style presets including professional_hd.

Tests:
- Style preset creation
- Professional HD preset configuration
- Style copying with selout fields
- Style serialization
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests.framework import TestCase
from core.style import (
    Style,
    OutlineConfig,
    ShadingConfig,
    get_style,
    STYLES,
    PROFESSIONAL_HD,
    MODERN_HD,
    CHIBI
)


class TestStylePresets(TestCase):
    """Tests for style preset availability."""

    def test_professional_hd_in_styles(self):
        """professional_hd is registered in STYLES."""
        self.assertIn('professional_hd', STYLES)

    def test_all_presets_available(self):
        """All expected presets are available."""
        expected = [
            'chibi', 'retro_nes', 'retro_snes', 'retro_gameboy',
            'modern_hd', 'professional_hd', 'minimalist', 'silhouette'
        ]
        for preset in expected:
            self.assertIn(preset, STYLES)

    def test_get_style_professional_hd(self):
        """get_style returns professional_hd preset."""
        style = get_style('professional_hd')
        self.assertEqual(style.name, 'professional_hd')


class TestProfessionalHDPreset(TestCase):
    """Tests for professional_hd preset configuration."""

    def test_professional_hd_shading_levels(self):
        """professional_hd has 6 shading levels."""
        style = Style.professional_hd()
        self.assertEqual(style.shading.levels, 6)

    def test_professional_hd_selout_enabled(self):
        """professional_hd has selout enabled."""
        style = Style.professional_hd()
        self.assertTrue(style.outline.selout_enabled)

    def test_professional_hd_anti_alias(self):
        """professional_hd has anti-aliasing enabled."""
        style = Style.professional_hd()
        self.assertTrue(style.anti_alias)

    def test_professional_hd_hue_shifts(self):
        """professional_hd has strong hue shifts."""
        style = Style.professional_hd()
        self.assertEqual(style.shading.highlight_hue_shift, 20.0)
        self.assertEqual(style.shading.shadow_hue_shift, -25.0)

    def test_professional_hd_selout_config(self):
        """professional_hd has proper selout configuration."""
        style = Style.professional_hd()
        self.assertEqual(style.outline.selout_darken, 0.30)
        self.assertEqual(style.outline.selout_saturation, 0.85)

    def test_professional_hd_outline_mode(self):
        """professional_hd uses selout outline mode."""
        style = Style.professional_hd()
        self.assertEqual(style.outline.mode, 'selout')


class TestModernHDComparison(TestCase):
    """Tests comparing modern_hd and professional_hd."""

    def test_professional_more_shading_levels(self):
        """professional_hd has more shading levels than modern_hd."""
        modern = Style.modern_hd()
        professional = Style.professional_hd()

        self.assertGreater(professional.shading.levels, modern.shading.levels)

    def test_professional_selout_vs_modern(self):
        """professional_hd has selout, modern_hd doesn't."""
        modern = Style.modern_hd()
        professional = Style.professional_hd()

        self.assertFalse(modern.outline.selout_enabled)
        self.assertTrue(professional.outline.selout_enabled)

    def test_professional_aa_vs_modern(self):
        """professional_hd has AA, modern_hd doesn't."""
        modern = Style.modern_hd()
        professional = Style.professional_hd()

        self.assertFalse(modern.anti_alias)
        self.assertTrue(professional.anti_alias)


class TestStyleCopy(TestCase):
    """Tests for style copying with selout fields."""

    def test_copy_preserves_selout_enabled(self):
        """Style copy preserves selout_enabled."""
        original = Style.professional_hd()
        copy = original.copy()
        self.assertEqual(copy.outline.selout_enabled, original.outline.selout_enabled)

    def test_copy_preserves_selout_darken(self):
        """Style copy preserves selout_darken."""
        original = Style.professional_hd()
        copy = original.copy()
        self.assertEqual(copy.outline.selout_darken, original.outline.selout_darken)

    def test_copy_preserves_selout_saturation(self):
        """Style copy preserves selout_saturation."""
        original = Style.professional_hd()
        copy = original.copy()
        self.assertEqual(copy.outline.selout_saturation, original.outline.selout_saturation)

    def test_copy_is_independent(self):
        """Style copy is independent from original."""
        original = Style.professional_hd()
        copy = original.copy()

        # Modify copy
        copy.name = 'modified'
        copy.outline.selout_enabled = False

        # Original should be unchanged
        self.assertEqual(original.name, 'professional_hd')
        self.assertTrue(original.outline.selout_enabled)


class TestStyleShadingColors(TestCase):
    """Tests for style shading color generation."""

    def test_professional_hd_shading_colors(self):
        """professional_hd generates 6 shading colors."""
        style = Style.professional_hd()
        base = (150, 100, 180, 255)

        colors = style.get_shading_colors(base)

        self.assertEqual(len(colors), 6)

    def test_shading_colors_gradient(self):
        """Shading colors form a gradient."""
        style = Style.professional_hd()
        base = (150, 100, 180, 255)

        colors = style.get_shading_colors(base)

        # First color (highlight) should be brightest
        first_brightness = sum(colors[0][:3])
        last_brightness = sum(colors[-1][:3])

        self.assertGreater(first_brightness, last_brightness)


class TestStyleOutlineColor(TestCase):
    """Tests for style outline color generation with selout."""

    def test_selout_outline_derives_from_neighbor(self):
        """With selout, outline color derives from neighbor."""
        style = Style.professional_hd()

        fill = (200, 100, 150, 255)
        neighbor = (100, 200, 100, 255)  # Very different color

        outline = style.get_outline_color(fill, neighbor)

        # Outline should be darker than neighbor
        self.assertLess(outline[1], neighbor[1])  # Green channel should be darker

    def test_non_selout_outline_derives_from_fill(self):
        """Without selout, outline color derives from fill."""
        style = Style.modern_hd()  # Selout disabled

        fill = (200, 100, 150, 255)
        neighbor = (100, 200, 100, 255)

        outline = style.get_outline_color(fill, neighbor)

        # Outline should be darker than fill, related to fill (red-ish)
        self.assertLess(outline[0], fill[0])


class TestConvenienceAliases(TestCase):
    """Tests for convenience alias instances."""

    def test_professional_hd_alias(self):
        """PROFESSIONAL_HD alias exists and is correct."""
        self.assertEqual(PROFESSIONAL_HD.name, 'professional_hd')
        self.assertTrue(PROFESSIONAL_HD.outline.selout_enabled)

    def test_aliases_are_instances(self):
        """Convenience aliases are Style instances."""
        self.assertIsInstance(PROFESSIONAL_HD, Style)
        self.assertIsInstance(MODERN_HD, Style)
        self.assertIsInstance(CHIBI, Style)

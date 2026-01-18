"""
Test Hair HD - Tests for high-detail hair styles.

Tests:
- HD hair type registration
- Bun hair rendering
- Multi-layer highlights
- Hair style creation factory
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests.framework import TestCase
from core import Canvas
from parts.hair import HAIR_TYPES, create_hair, list_hair_types
from parts.hair_hd import (
    HDHair,
    BunHairHD,
    LongHairHD,
    PonytailHairHD,
    ShortHairHD,
    HD_HAIR_TYPES
)


class TestHDHairRegistration(TestCase):
    """Tests for HD hair type registration."""

    def test_hd_types_registered(self):
        """HD hair types are registered in main HAIR_TYPES."""
        self.assertIn('bun_hd', HAIR_TYPES)
        self.assertIn('long_hd', HAIR_TYPES)
        self.assertIn('ponytail_hd', HAIR_TYPES)
        self.assertIn('short_hd', HAIR_TYPES)

    def test_hd_types_in_list(self):
        """HD hair types appear in list_hair_types."""
        types = list_hair_types()
        self.assertIn('bun_hd', types)
        self.assertIn('long_hd', types)

    def test_hd_types_count(self):
        """HD_HAIR_TYPES contains expected number of styles."""
        self.assertEqual(len(HD_HAIR_TYPES), 4)


class TestHDHairBase(TestCase):
    """Tests for HDHair base class."""

    def test_hd_hair_highlight_layers(self):
        """HDHair has multiple highlight layers."""
        hair = BunHairHD()
        self.assertEqual(hair.highlight_layers, 3)

    def test_hd_hair_detail_level(self):
        """HDHair has high detail level."""
        hair = BunHairHD()
        self.assertEqual(hair.detail_level, 'high')


class TestBunHairHD(TestCase):
    """Tests for BunHairHD style."""

    def test_bun_hair_creation(self):
        """BunHairHD can be created."""
        hair = BunHairHD()
        self.assertEqual(hair.name, 'bun_hd')

    def test_bun_hair_via_factory(self):
        """BunHairHD can be created via factory."""
        hair = create_hair('bun_hd')
        self.assertIsInstance(hair, BunHairHD)

    def test_bun_hair_draw(self):
        """BunHairHD can draw to canvas."""
        canvas = Canvas(32, 32)
        from parts.base import PartConfig
        config = PartConfig(base_color=(180, 150, 200, 255))
        hair = BunHairHD(config)

        # Should not raise
        hair.draw(canvas, 16, 16, 24, 24)

        # Canvas should have content
        self.assertCanvasNotEmpty(canvas)

    def test_bun_hair_draw_back(self):
        """BunHairHD can draw back layer."""
        canvas = Canvas(32, 32)
        from parts.base import PartConfig
        config = PartConfig(base_color=(180, 150, 200, 255))
        hair = BunHairHD(config)

        hair.draw_back(canvas, 16, 16, 24, 24)
        self.assertCanvasNotEmpty(canvas)

    def test_bun_hair_draw_front(self):
        """BunHairHD can draw front layer."""
        canvas = Canvas(32, 32)
        from parts.base import PartConfig
        config = PartConfig(base_color=(180, 150, 200, 255))
        hair = BunHairHD(config)

        hair.draw_front(canvas, 16, 16, 24, 24)
        self.assertCanvasNotEmpty(canvas)


class TestLongHairHD(TestCase):
    """Tests for LongHairHD style."""

    def test_long_hair_creation(self):
        """LongHairHD can be created."""
        hair = LongHairHD()
        self.assertEqual(hair.name, 'long_hd')

    def test_long_hair_draw(self):
        """LongHairHD can draw to canvas."""
        canvas = Canvas(32, 32)
        from parts.base import PartConfig
        config = PartConfig(base_color=(100, 80, 60, 255))
        hair = LongHairHD(config)

        hair.draw(canvas, 16, 16, 24, 24)
        self.assertCanvasNotEmpty(canvas)


class TestPonytailHairHD(TestCase):
    """Tests for PonytailHairHD style."""

    def test_ponytail_hair_creation(self):
        """PonytailHairHD can be created."""
        hair = PonytailHairHD()
        self.assertEqual(hair.name, 'ponytail_hd')

    def test_ponytail_hair_draw(self):
        """PonytailHairHD can draw to canvas."""
        canvas = Canvas(32, 32)
        from parts.base import PartConfig
        config = PartConfig(base_color=(50, 30, 20, 255))
        hair = PonytailHairHD(config)

        hair.draw(canvas, 16, 16, 24, 24)
        self.assertCanvasNotEmpty(canvas)


class TestShortHairHD(TestCase):
    """Tests for ShortHairHD style."""

    def test_short_hair_creation(self):
        """ShortHairHD can be created."""
        hair = ShortHairHD()
        self.assertEqual(hair.name, 'short_hd')

    def test_short_hair_no_back(self):
        """ShortHairHD has no back layer."""
        hair = ShortHairHD()
        self.assertFalse(hair.has_back)

    def test_short_hair_draw(self):
        """ShortHairHD can draw to canvas."""
        canvas = Canvas(32, 32)
        from parts.base import PartConfig
        config = PartConfig(base_color=(80, 70, 60, 255))
        hair = ShortHairHD(config)

        hair.draw(canvas, 16, 16, 24, 24)
        self.assertCanvasNotEmpty(canvas)


class TestHDHairHighlights(TestCase):
    """Tests for HD hair highlight system."""

    def test_multiple_highlight_colors(self):
        """HD hair generates multiple highlight colors."""
        from parts.base import PartConfig
        config = PartConfig(base_color=(150, 100, 180, 255))
        hair = BunHairHD(config)

        # Get shading colors
        colors = hair._get_colors(6)

        # Should have multiple colors
        self.assertGreaterEqual(len(colors), 3)

        # First color (highlight) should be lighter
        base = colors[2] if len(colors) > 2 else colors[-1]
        highlight = colors[0]

        # Highlight should generally be brighter
        self.assertGreater(
            highlight[0] + highlight[1] + highlight[2],
            base[0] + base[1] + base[2] - 100  # Allow some tolerance
        )

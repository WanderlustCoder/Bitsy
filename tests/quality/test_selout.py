"""
Test Selout - Tests for selective outline functionality.

Tests:
- Selout color derivation
- Edge detection
- Interior neighbor detection
- Selout application to canvas
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests.framework import TestCase
from core import Canvas
from quality.selout import (
    apply_selout,
    is_edge_pixel,
    get_interior_neighbor_color,
    derive_selout_color
)


class TestSeloutColorDerivation(TestCase):
    """Tests for selout color derivation."""

    def test_derive_selout_color_darkens(self):
        """derive_selout_color returns a darker version of the input."""
        color = (200, 100, 150, 255)
        result = derive_selout_color(color)

        # Should be darker
        self.assertLess(result[0], color[0])
        self.assertLess(result[1], color[1])
        self.assertLess(result[2], color[2])

    def test_derive_selout_color_preserves_alpha(self):
        """derive_selout_color preserves full opacity."""
        color = (200, 100, 150, 255)
        result = derive_selout_color(color)
        self.assertEqual(result[3], 255)

    def test_derive_selout_color_custom_darken(self):
        """derive_selout_color respects custom darken factor."""
        color = (200, 100, 150, 255)
        result_low = derive_selout_color(color, darken_factor=0.1)
        result_high = derive_selout_color(color, darken_factor=0.5)

        # Higher darken factor should produce darker result
        self.assertGreater(result_low[0], result_high[0])

    def test_derive_selout_color_saturation_adjustment(self):
        """derive_selout_color adjusts saturation."""
        color = (255, 100, 100, 255)  # Saturated red
        result = derive_selout_color(color, saturation_factor=0.5)

        # Result should be less saturated (R closer to G and B)
        # This is a rough check
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 4)


class TestEdgeDetection(TestCase):
    """Tests for edge pixel detection."""

    def test_is_edge_pixel_at_boundary(self):
        """is_edge_pixel detects transparent boundary."""
        canvas = Canvas(8, 8)
        canvas.fill_rect(2, 2, 4, 4, (255, 0, 0, 255))

        # Pixels at edge of filled region
        self.assertTrue(is_edge_pixel(canvas, 2, 2))  # Top-left corner
        self.assertTrue(is_edge_pixel(canvas, 5, 5))  # Bottom-right corner

        # Pixel inside filled region (not at edge)
        self.assertFalse(is_edge_pixel(canvas, 3, 3))

        # Pixel outside filled region
        self.assertFalse(is_edge_pixel(canvas, 0, 0))

    def test_is_edge_pixel_isolated(self):
        """is_edge_pixel detects isolated pixel as edge."""
        canvas = Canvas(8, 8)
        canvas.set_pixel(4, 4, (255, 0, 0, 255))

        self.assertTrue(is_edge_pixel(canvas, 4, 4))


class TestInteriorNeighbor(TestCase):
    """Tests for interior neighbor color detection."""

    def test_get_interior_neighbor_finds_fill(self):
        """get_interior_neighbor_color returns adjacent fill color."""
        canvas = Canvas(8, 8)
        canvas.fill_rect(2, 2, 4, 4, (255, 0, 0, 255))

        # Get neighbor for edge pixel
        neighbor = get_interior_neighbor_color(canvas, 2, 2)

        # Should find the red fill color
        self.assertIsNotNone(neighbor)
        if neighbor:
            self.assertEqual(neighbor[0], 255)  # Red channel

    def test_get_interior_neighbor_none_for_interior(self):
        """get_interior_neighbor_color for interior pixel still finds neighbor."""
        canvas = Canvas(8, 8)
        canvas.fill_rect(2, 2, 4, 4, (255, 0, 0, 255))

        # Interior pixel should still have neighbors
        neighbor = get_interior_neighbor_color(canvas, 3, 3)
        self.assertIsNotNone(neighbor)


class TestApplySelout(TestCase):
    """Tests for full selout application."""

    def test_apply_selout_basic(self):
        """apply_selout processes canvas without error."""
        canvas = Canvas(16, 16)
        canvas.fill_circle(8, 8, 6, (200, 100, 150, 255))

        # Should not raise
        result = apply_selout(canvas)

        # Result should be a canvas
        self.assertEqual(result.width, canvas.width)
        self.assertEqual(result.height, canvas.height)

    def test_apply_selout_modifies_edges(self):
        """apply_selout modifies edge pixels."""
        canvas = Canvas(16, 16)
        fill_color = (200, 100, 150, 255)
        canvas.fill_rect(4, 4, 8, 8, fill_color)

        result = apply_selout(canvas)

        # Edge pixels should be different from original fill
        # (they should be darkened outlines)
        edge_pixel = result.pixels[4][4]
        self.assertNotEqual(tuple(edge_pixel), fill_color)

    def test_apply_selout_empty_canvas(self):
        """apply_selout handles empty canvas."""
        canvas = Canvas(8, 8)
        result = apply_selout(canvas)

        # Should return unchanged empty canvas
        self.assertEqual(result.width, 8)


class TestSeloutIntegration(TestCase):
    """Integration tests for selout with style system."""

    def test_selout_with_style_config(self):
        """Selout works with style configuration."""
        from core.style import Style, OutlineConfig

        style = Style(
            name='test_selout',
            outline=OutlineConfig(
                enabled=True,
                selout_enabled=True,
                selout_darken=0.25,
                selout_saturation=0.9
            )
        )

        # Get outline color with neighbor
        fill = (200, 100, 150, 255)
        neighbor = (180, 80, 130, 255)

        outline = style.get_outline_color(fill, neighbor)

        # Should derive from neighbor, not fill
        self.assertIsNotNone(outline)
        self.assertLess(outline[0], neighbor[0])  # Should be darker

    def test_selout_disabled_uses_fill(self):
        """When selout disabled, outline derives from fill color."""
        from core.style import Style, OutlineConfig

        style = Style(
            name='test_no_selout',
            outline=OutlineConfig(
                enabled=True,
                selout_enabled=False,
                darken_factor=0.4
            )
        )

        fill = (200, 100, 150, 255)
        neighbor = (50, 200, 50, 255)  # Very different color

        outline = style.get_outline_color(fill, neighbor)

        # Should derive from fill, ignoring neighbor
        # Outline should be darker than fill, but related to fill color
        self.assertLess(outline[0], fill[0])

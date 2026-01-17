"""
Test HDCanvas - Tests for the HDCanvas drawing wrapper.

Tests:
- HDCanvas creation and initialization
- Circle fill routing
- Line drawing
- Finalize behavior
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests.framework import TestCase
from core.hd_canvas import HDCanvas
from core.style import Style
from quality.selout import derive_selout_color


class TestHDCanvasCreation(TestCase):
    """Tests for HDCanvas creation and initialization."""

    def test_hd_canvas_init_default_style_transparent(self):
        """Default init uses transparent background and professional HD style."""
        canvas = HDCanvas(6, 4)
        self.assertEqual(canvas.width, 6)
        self.assertEqual(canvas.height, 4)
        self.assertPixelColor(canvas.canvas, 0, 0, (0, 0, 0, 0))
        self.assertEqual(canvas.style.name, 'professional_hd')
        self.assertTrue(canvas.style.anti_alias)

    def test_hd_canvas_init_custom_background_and_style(self):
        """Custom background and style are used as provided."""
        style = Style()
        style.anti_alias = False
        canvas = HDCanvas(3, 3, background=(10, 20, 30, 255), style=style)
        self.assertIs(canvas.style, style)
        self.assertPixelColor(canvas.canvas, 2, 2, (10, 20, 30, 255))


class TestHDCanvasShapes(TestCase):
    """Tests for HDCanvas shape primitives."""

    def test_hd_canvas_fill_circle(self):
        """fill_circle fills the circle area on the underlying canvas."""
        style = Style()
        style.anti_alias = False
        canvas = HDCanvas(10, 10, style=style)
        canvas.fill_circle(5, 5, 3, (255, 0, 0, 255))
        self.assertPixelColor(canvas.canvas, 5, 5, (255, 0, 0, 255))
        self.assertPixelColor(canvas.canvas, 0, 0, (0, 0, 0, 0))


class TestHDCanvasLines(TestCase):
    """Tests for HDCanvas line drawing."""

    def test_hd_canvas_draw_line(self):
        """draw_line draws a simple horizontal line."""
        style = Style()
        style.anti_alias = False
        canvas = HDCanvas(8, 4, style=style)
        canvas.draw_line(1, 2, 6, 2, (0, 255, 0, 255))
        self.assertPixelColor(canvas.canvas, 1, 2, (0, 255, 0, 255))
        self.assertPixelColor(canvas.canvas, 4, 2, (0, 255, 0, 255))
        self.assertPixelColor(canvas.canvas, 0, 0, (0, 0, 0, 0))


class TestHDCanvasFinalize(TestCase):
    """Tests for HDCanvas finalize behavior."""

    def test_hd_canvas_finalize_applies_selout(self):
        """finalize applies selout when enabled."""
        style = Style()
        style.outline.selout_enabled = True
        style.outline.selout_darken = 0.30
        style.outline.selout_saturation = 0.85
        canvas = HDCanvas(7, 7, style=style)
        fill = (120, 160, 200, 255)
        canvas.fill_rect(2, 2, 3, 3, fill)
        final = canvas.finalize()
        expected = derive_selout_color(fill, 0.30, 0.85)
        self.assertPixelColor(final, 2, 2, expected)
        self.assertPixelColor(final, 3, 3, fill)

    def test_hd_canvas_finalize_without_selout_returns_copy(self):
        """finalize returns a copy when selout is disabled."""
        style = Style()
        style.outline.selout_enabled = False
        canvas = HDCanvas(4, 4, style=style)
        canvas.fill_rect(1, 1, 2, 2, (50, 100, 150, 255))
        final = canvas.finalize()
        self.assertIsNot(final, canvas.canvas)
        self.assertCanvasEqual(final, canvas.canvas)

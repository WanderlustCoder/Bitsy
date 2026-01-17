"""Tests for selection and masking tools."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests.framework import TestCase
from core import Canvas
from editor.selection import (
    Selection,
    Mask,
    SelectionMode,
    select_rect,
    select_ellipse,
    select_polygon,
    select_by_color,
    select_all,
    create_mask_from_selection,
    create_mask_from_alpha,
    apply_mask,
    copy_selection,
    fill_selection,
    clear_selection,
)


class TestSelection(TestCase):
    """Tests for Selection class."""

    def test_selection_create_empty(self):
        """Selection starts empty."""
        sel = Selection(16, 16)
        self.assertEqual(len(sel), 0)
        self.assertFalse(sel)

    def test_selection_add_pixel(self):
        """Can add pixels to selection."""
        sel = Selection(16, 16)
        sel.add(5, 5)
        self.assertEqual(len(sel), 1)
        self.assertIn((5, 5), sel)

    def test_selection_remove_pixel(self):
        """Can remove pixels from selection."""
        sel = Selection(16, 16)
        sel.add(5, 5)
        sel.remove(5, 5)
        self.assertEqual(len(sel), 0)

    def test_selection_bounds_check(self):
        """Pixels outside bounds are not added."""
        sel = Selection(16, 16)
        sel.add(-1, 5)
        sel.add(20, 5)
        self.assertEqual(len(sel), 0)

    def test_selection_invert(self):
        """Invert creates complement selection."""
        sel = Selection(4, 4)
        sel.add(0, 0)
        inverted = sel.invert()
        self.assertEqual(len(inverted), 15)
        self.assertNotIn((0, 0), inverted)

    def test_selection_union(self):
        """Union combines selections."""
        sel1 = Selection(8, 8)
        sel1.add(0, 0)
        sel2 = Selection(8, 8)
        sel2.add(1, 1)
        combined = sel1.union(sel2)
        self.assertEqual(len(combined), 2)

    def test_selection_subtract(self):
        """Subtract removes from selection."""
        sel1 = Selection(8, 8)
        sel1.add(0, 0)
        sel1.add(1, 1)
        sel2 = Selection(8, 8)
        sel2.add(1, 1)
        result = sel1.subtract(sel2)
        self.assertEqual(len(result), 1)
        self.assertIn((0, 0), result)

    def test_selection_intersect(self):
        """Intersect finds common pixels."""
        sel1 = Selection(8, 8)
        sel1.add(0, 0)
        sel1.add(1, 1)
        sel2 = Selection(8, 8)
        sel2.add(1, 1)
        sel2.add(2, 2)
        result = sel1.intersect(sel2)
        self.assertEqual(len(result), 1)
        self.assertIn((1, 1), result)

    def test_selection_bounds(self):
        """Get bounds returns bounding box."""
        sel = Selection(16, 16)
        sel.add(2, 3)
        sel.add(5, 7)
        bounds = sel.get_bounds()
        self.assertEqual(bounds, (2, 3, 4, 5))

    def test_selection_expand(self):
        """Expand grows selection."""
        sel = Selection(16, 16)
        sel.add(8, 8)
        expanded = sel.expand(1)
        self.assertGreater(len(expanded), 1)
        self.assertIn((8, 8), expanded)
        self.assertIn((8, 9), expanded)


class TestMask(TestCase):
    """Tests for Mask class."""

    def test_mask_create(self):
        """Mask initializes to zeros."""
        mask = Mask(8, 8)
        self.assertEqual(mask.get(0, 0), 0.0)

    def test_mask_set_get(self):
        """Can set and get mask values."""
        mask = Mask(8, 8)
        mask.set(2, 2, 0.5)
        self.assertEqual(mask.get(2, 2), 0.5)

    def test_mask_clamp(self):
        """Mask values are clamped to 0-1."""
        mask = Mask(8, 8)
        mask.set(0, 0, 1.5)
        self.assertEqual(mask.get(0, 0), 1.0)
        mask.set(0, 0, -0.5)
        self.assertEqual(mask.get(0, 0), 0.0)

    def test_mask_invert(self):
        """Invert creates complement mask."""
        mask = Mask(8, 8)
        mask.set(0, 0, 0.3)
        inverted = mask.invert()
        self.assertAlmostEqual(inverted.get(0, 0), 0.7, places=5)

    def test_mask_to_selection(self):
        """Convert mask to selection with threshold."""
        mask = Mask(8, 8)
        mask.set(0, 0, 0.6)
        mask.set(1, 1, 0.4)
        sel = mask.to_selection(threshold=0.5)
        self.assertIn((0, 0), sel)
        self.assertNotIn((1, 1), sel)


class TestSelectRect(TestCase):
    """Tests for rectangular selection."""

    def test_select_rect_basic(self):
        """Create rectangular selection."""
        sel = select_rect(16, 16, 2, 2, 4, 4)
        self.assertEqual(len(sel), 16)
        self.assertIn((2, 2), sel)
        self.assertIn((5, 5), sel)

    def test_select_rect_clipped(self):
        """Rectangle clipped to bounds."""
        sel = select_rect(8, 8, 6, 6, 10, 10)
        self.assertGreater(len(sel), 0)
        for x, y in sel.pixels:
            self.assertLess(x, 8)
            self.assertLess(y, 8)


class TestSelectEllipse(TestCase):
    """Tests for elliptical selection."""

    def test_select_ellipse_basic(self):
        """Create elliptical selection."""
        sel = select_ellipse(16, 16, 8, 8, 4, 4)
        self.assertGreater(len(sel), 0)
        self.assertIn((8, 8), sel)

    def test_select_ellipse_circle(self):
        """Ellipse with equal radii is circle."""
        sel = select_ellipse(32, 32, 16, 16, 5, 5)
        self.assertIn((16, 16), sel)
        self.assertIn((16, 11), sel)
        self.assertIn((21, 16), sel)


class TestSelectPolygon(TestCase):
    """Tests for polygon selection."""

    def test_select_polygon_triangle(self):
        """Create triangular selection."""
        points = [(4, 0), (8, 8), (0, 8)]
        sel = select_polygon(16, 16, points)
        self.assertGreater(len(sel), 0)

    def test_select_polygon_square(self):
        """Create square selection."""
        points = [(2, 2), (6, 2), (6, 6), (2, 6)]
        sel = select_polygon(16, 16, points)
        self.assertIn((4, 4), sel)


class TestSelectByColor(TestCase):
    """Tests for magic wand selection."""

    def test_select_by_color_exact(self):
        """Select exact color match."""
        canvas = Canvas(8, 8, (0, 0, 0, 0))
        canvas.fill_rect(2, 2, 4, 4, (255, 0, 0, 255))
        sel = select_by_color(canvas, 3, 3, tolerance=0.0)
        self.assertEqual(len(sel), 16)

    def test_select_by_color_non_contiguous(self):
        """Select non-contiguous matching pixels."""
        canvas = Canvas(8, 8, (0, 0, 0, 0))
        canvas.set_pixel_solid(0, 0, (255, 0, 0, 255))
        canvas.set_pixel_solid(7, 7, (255, 0, 0, 255))
        sel = select_by_color(canvas, 0, 0, contiguous=False)
        self.assertEqual(len(sel), 2)


class TestSelectAll(TestCase):
    """Tests for select all."""

    def test_select_all_opaque(self):
        """Select all opaque pixels."""
        canvas = Canvas(8, 8, (0, 0, 0, 0))
        canvas.fill_rect(0, 0, 4, 4, (255, 0, 0, 255))
        sel = select_all(canvas)
        self.assertEqual(len(sel), 16)


class TestMaskOperations(TestCase):
    """Tests for mask operations."""

    def test_create_mask_from_selection(self):
        """Create mask from selection."""
        sel = Selection(8, 8)
        sel.add(2, 2)
        mask = create_mask_from_selection(sel)
        self.assertEqual(mask.get(2, 2), 1.0)
        self.assertEqual(mask.get(0, 0), 0.0)

    def test_create_mask_from_alpha(self):
        """Create mask from canvas alpha."""
        canvas = Canvas(8, 8, (0, 0, 0, 0))
        canvas.set_pixel_solid(2, 2, (255, 0, 0, 128))
        mask = create_mask_from_alpha(canvas)
        self.assertAlmostEqual(mask.get(2, 2), 128/255, places=2)

    def test_apply_mask(self):
        """Apply mask modifies alpha."""
        canvas = Canvas(8, 8, (255, 0, 0, 255))
        mask = Mask(8, 8)
        mask.set(0, 0, 0.5)
        result = apply_mask(canvas, mask)
        pixel = result.get_pixel(0, 0)
        self.assertEqual(pixel[3], 127)


class TestCopyFillClear(TestCase):
    """Tests for copy, fill, clear operations."""

    def test_copy_selection(self):
        """Copy selected pixels to new canvas."""
        canvas = Canvas(8, 8, (255, 0, 0, 255))
        sel = Selection(8, 8)
        sel.add(2, 2)
        result = copy_selection(canvas, sel)
        self.assertIsNotNone(result.get_pixel(2, 2))
        self.assertEqual(result.get_pixel(0, 0)[3], 0)

    def test_fill_selection(self):
        """Fill selection with color."""
        canvas = Canvas(8, 8, (0, 0, 0, 0))
        sel = Selection(8, 8)
        sel.add(2, 2)
        result = fill_selection(canvas, sel, (0, 255, 0, 255))
        self.assertEqual(result.get_pixel(2, 2), (0, 255, 0, 255))

    def test_clear_selection(self):
        """Clear selection makes transparent."""
        canvas = Canvas(8, 8, (255, 0, 0, 255))
        sel = Selection(8, 8)
        sel.add(2, 2)
        result = clear_selection(canvas, sel)
        self.assertEqual(result.get_pixel(2, 2)[3], 0)

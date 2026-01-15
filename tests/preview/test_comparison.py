"""
Test Comparison - Tests for comparison tools.

Tests:
- Canvas comparison
- Side-by-side comparison
- Before/after comparison
- Diff overlay
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests.framework import TestCase
from core import Canvas
from preview.comparison import (
    compare_canvases,
    create_comparison,
    create_before_after,
    create_diff_overlay,
    create_triple_comparison,
    create_grid_comparison,
    ComparisonResult,
)


class TestCompareCanvases(TestCase):
    """Tests for canvas comparison."""

    def test_identical_canvases(self):
        """Identical canvases compare as identical."""
        canvas1 = Canvas(8, 8, (255, 0, 0, 255))
        canvas2 = Canvas(8, 8, (255, 0, 0, 255))

        result = compare_canvases(canvas1, canvas2)

        self.assertTrue(result.identical)
        self.assertEqual(result.different_pixels, 0)
        self.assertEqual(result.similarity_percent, 100.0)

    def test_different_canvases(self):
        """Different canvases are detected."""
        canvas1 = Canvas(8, 8, (255, 0, 0, 255))
        canvas2 = Canvas(8, 8, (0, 255, 0, 255))

        result = compare_canvases(canvas1, canvas2)

        self.assertFalse(result.identical)
        self.assertGreater(result.different_pixels, 0)
        self.assertLess(result.similarity_percent, 100.0)

    def test_size_mismatch(self):
        """Different sized canvases detected."""
        canvas1 = Canvas(8, 8, (255, 0, 0, 255))
        canvas2 = Canvas(16, 16, (255, 0, 0, 255))

        result = compare_canvases(canvas1, canvas2)

        self.assertFalse(result.size_match)
        self.assertFalse(result.identical)

    def test_tolerance_zero(self):
        """Zero tolerance requires exact match."""
        canvas1 = Canvas(8, 8, (255, 0, 0, 255))
        canvas2 = Canvas(8, 8, (254, 0, 0, 255))  # Slightly different

        result = compare_canvases(canvas1, canvas2, tolerance=0)

        self.assertFalse(result.identical)

    def test_tolerance_allows_near_match(self):
        """Non-zero tolerance allows near matches."""
        canvas1 = Canvas(8, 8, (255, 0, 0, 255))
        canvas2 = Canvas(8, 8, (254, 0, 0, 255))  # Slightly different

        result = compare_canvases(canvas1, canvas2, tolerance=10)

        self.assertTrue(result.identical)

    def test_returns_diff_canvas(self):
        """Comparison returns diff canvas."""
        canvas1 = Canvas(8, 8, (255, 0, 0, 255))
        canvas2 = Canvas(8, 8, (0, 255, 0, 255))

        result = compare_canvases(canvas1, canvas2)

        self.assertIsNotNone(result.diff_canvas)
        self.assertIsInstance(result.diff_canvas, Canvas)

    def test_transparent_pixels_handling(self):
        """Transparent pixels handled correctly."""
        canvas1 = Canvas(8, 8)  # All transparent
        canvas2 = Canvas(8, 8)  # All transparent

        result = compare_canvases(canvas1, canvas2)

        self.assertTrue(result.identical)


class TestComparisonResult(TestCase):
    """Tests for ComparisonResult dataclass."""

    def test_difference_percent(self):
        """difference_percent property works."""
        result = ComparisonResult(
            identical=False,
            total_pixels=100,
            different_pixels=25,
            similarity_percent=75.0,
            size_match=True
        )

        self.assertEqual(result.difference_percent, 25.0)


class TestCreateComparison(TestCase):
    """Tests for side-by-side comparison."""

    def test_returns_canvas(self):
        """create_comparison returns Canvas."""
        canvas1 = Canvas(8, 8, (255, 0, 0, 255))
        canvas2 = Canvas(8, 8, (0, 255, 0, 255))

        result = create_comparison(canvas1, canvas2)

        self.assertIsInstance(result, Canvas)

    def test_combined_width(self):
        """Result width includes both canvases and padding."""
        canvas1 = Canvas(10, 8, (255, 0, 0, 255))
        canvas2 = Canvas(12, 8, (0, 255, 0, 255))

        result = create_comparison(canvas1, canvas2, padding=4)

        expected_width = 10 + 4 + 12  # canvas1 + padding + canvas2
        self.assertEqual(result.width, expected_width)

    def test_max_height(self):
        """Result height is max of both canvases."""
        canvas1 = Canvas(8, 10, (255, 0, 0, 255))
        canvas2 = Canvas(8, 16, (0, 255, 0, 255))

        result = create_comparison(canvas1, canvas2)

        self.assertGreaterEqual(result.height, 16)

    def test_custom_padding(self):
        """Custom padding is applied."""
        canvas1 = Canvas(8, 8, (255, 0, 0, 255))
        canvas2 = Canvas(8, 8, (0, 255, 0, 255))

        result_small = create_comparison(canvas1, canvas2, padding=2)
        result_large = create_comparison(canvas1, canvas2, padding=10)

        self.assertGreater(result_large.width, result_small.width)


class TestCreateBeforeAfter(TestCase):
    """Tests for before/after comparison."""

    def test_returns_canvas(self):
        """create_before_after returns Canvas."""
        before = Canvas(8, 8, (100, 100, 100, 255))
        after = Canvas(8, 8, (200, 200, 200, 255))

        result = create_before_after(before, after)

        self.assertIsInstance(result, Canvas)

    def test_includes_separator(self):
        """Result includes separator between images."""
        before = Canvas(8, 8, (100, 100, 100, 255))
        after = Canvas(8, 8, (200, 200, 200, 255))

        result = create_before_after(before, after, padding=2)

        # Width should be: before + padding + separator + padding + after
        expected_min_width = 8 + 2 + 2 + 2 + 8
        self.assertGreaterEqual(result.width, expected_min_width)

    def test_scale_parameter(self):
        """Scale parameter increases output size."""
        before = Canvas(8, 8, (100, 100, 100, 255))
        after = Canvas(8, 8, (200, 200, 200, 255))

        result_1x = create_before_after(before, after, scale=1)
        result_2x = create_before_after(before, after, scale=2)

        self.assertEqual(result_2x.width, result_1x.width * 2)
        self.assertEqual(result_2x.height, result_1x.height * 2)


class TestCreateDiffOverlay(TestCase):
    """Tests for diff overlay creation."""

    def test_returns_canvas(self):
        """create_diff_overlay returns Canvas."""
        canvas1 = Canvas(8, 8, (255, 0, 0, 255))
        canvas2 = Canvas(8, 8, (0, 255, 0, 255))

        result = create_diff_overlay(canvas1, canvas2)

        self.assertIsInstance(result, Canvas)

    def test_same_size_as_input(self):
        """Result has same size as input canvases."""
        canvas1 = Canvas(16, 12, (255, 0, 0, 255))
        canvas2 = Canvas(16, 12, (0, 255, 0, 255))

        result = create_diff_overlay(canvas1, canvas2)

        self.assertEqual(result.width, 16)
        self.assertEqual(result.height, 12)

    def test_raises_on_size_mismatch(self):
        """Raises ValueError for different sized canvases."""
        canvas1 = Canvas(8, 8)
        canvas2 = Canvas(16, 16)

        with self.assertRaises(ValueError):
            create_diff_overlay(canvas1, canvas2)

    def test_custom_highlight_color(self):
        """Custom highlight color is applied."""
        canvas1 = Canvas(8, 8, (255, 0, 0, 255))
        canvas2 = Canvas(8, 8, (0, 255, 0, 255))

        highlight = (0, 0, 255, 255)  # Blue
        result = create_diff_overlay(canvas1, canvas2, highlight_color=highlight)

        # At least some pixels should be highlighted
        self.assertIsInstance(result, Canvas)


class TestCreateTripleComparison(TestCase):
    """Tests for triple comparison (original, modified, diff)."""

    def test_returns_canvas(self):
        """create_triple_comparison returns Canvas."""
        original = Canvas(8, 8, (255, 0, 0, 255))
        modified = Canvas(8, 8, (0, 255, 0, 255))

        result = create_triple_comparison(original, modified)

        self.assertIsInstance(result, Canvas)

    def test_three_panels_width(self):
        """Result has width for three panels."""
        original = Canvas(8, 8, (255, 0, 0, 255))
        modified = Canvas(8, 8, (0, 255, 0, 255))

        result = create_triple_comparison(original, modified, padding=4)

        # Width: original + padding + modified + padding + diff
        min_width = 8 + 4 + 8 + 4 + 8
        self.assertGreaterEqual(result.width, min_width)


class TestCreateGridComparison(TestCase):
    """Tests for grid comparison."""

    def test_returns_canvas(self):
        """create_grid_comparison returns Canvas."""
        canvases = [
            Canvas(8, 8, (255, 0, 0, 255)),
            Canvas(8, 8, (0, 255, 0, 255)),
            Canvas(8, 8, (0, 0, 255, 255)),
        ]

        result = create_grid_comparison(canvases, columns=2)

        self.assertIsInstance(result, Canvas)

    def test_respects_columns(self):
        """Grid respects column count."""
        canvases = [Canvas(8, 8, (i * 50, 0, 0, 255)) for i in range(6)]

        result_2col = create_grid_comparison(canvases, columns=2)
        result_3col = create_grid_comparison(canvases, columns=3)

        # 2 columns should be narrower than 3 columns
        self.assertLess(result_2col.width, result_3col.width)

    def test_empty_list(self):
        """Handles empty canvas list."""
        result = create_grid_comparison([])

        self.assertIsInstance(result, Canvas)
        self.assertEqual(result.width, 1)
        self.assertEqual(result.height, 1)

    def test_custom_padding(self):
        """Custom padding affects result size."""
        canvases = [Canvas(8, 8, (255, 0, 0, 255)) for _ in range(4)]

        result_small = create_grid_comparison(canvases, padding=2)
        result_large = create_grid_comparison(canvases, padding=10)

        self.assertGreater(result_large.width, result_small.width)

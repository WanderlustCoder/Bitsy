"""
Test Contact Sheet - Tests for contact sheet generation.

Tests:
- Contact sheet creation
- Labeled sheets
- Variation preview
- Layout options
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests.framework import TestCase
from core import Canvas
from preview.contact_sheet import (
    create_contact_sheet,
    create_labeled_sheet,
    generate_variations_preview,
    create_comparison_strip,
    ContactSheetOptions,
)


class TestCreateContactSheet(TestCase):
    """Tests for contact sheet creation."""

    def test_returns_canvas(self):
        """create_contact_sheet returns Canvas."""
        canvases = [
            Canvas(8, 8, (255, 0, 0, 255)),
            Canvas(8, 8, (0, 255, 0, 255)),
        ]
        result = create_contact_sheet(canvases)

        self.assertIsInstance(result, Canvas)

    def test_empty_list(self):
        """Handles empty canvas list."""
        result = create_contact_sheet([])

        self.assertIsInstance(result, Canvas)

    def test_single_canvas(self):
        """Single canvas creates valid sheet."""
        canvases = [Canvas(16, 16, (255, 0, 0, 255))]
        result = create_contact_sheet(canvases)

        self.assertIsInstance(result, Canvas)
        self.assertGreaterEqual(result.width, 16)
        self.assertGreaterEqual(result.height, 16)

    def test_respects_columns(self):
        """Column count affects layout."""
        canvases = [Canvas(8, 8, (i * 30, 0, 0, 255)) for i in range(8)]

        result_2col = create_contact_sheet(canvases, ContactSheetOptions(columns=2))
        result_4col = create_contact_sheet(canvases, ContactSheetOptions(columns=4))

        # 2 columns = more rows = taller
        # 4 columns = fewer rows = wider
        self.assertGreater(result_4col.width, result_2col.width)
        self.assertGreater(result_2col.height, result_4col.height)

    def test_with_scale(self):
        """Scale option increases output size."""
        canvases = [Canvas(8, 8, (255, 0, 0, 255)) for _ in range(4)]

        result_1x = create_contact_sheet(canvases, ContactSheetOptions(scale=1))
        result_2x = create_contact_sheet(canvases, ContactSheetOptions(scale=2))

        self.assertGreater(result_2x.width, result_1x.width)
        self.assertGreater(result_2x.height, result_1x.height)

    def test_different_sized_canvases(self):
        """Handles canvases of different sizes."""
        canvases = [
            Canvas(8, 8, (255, 0, 0, 255)),
            Canvas(16, 16, (0, 255, 0, 255)),
            Canvas(12, 10, (0, 0, 255, 255)),
        ]
        result = create_contact_sheet(canvases)

        # Should accommodate largest canvas
        self.assertGreaterEqual(result.width, 16)


class TestCreateLabeledSheet(TestCase):
    """Tests for labeled contact sheets."""

    def test_returns_canvas(self):
        """create_labeled_sheet returns Canvas."""
        items = [
            ("Red", Canvas(8, 8, (255, 0, 0, 255))),
            ("Green", Canvas(8, 8, (0, 255, 0, 255))),
        ]
        result = create_labeled_sheet(items)

        self.assertIsInstance(result, Canvas)

    def test_empty_list(self):
        """Handles empty item list."""
        result = create_labeled_sheet([])

        self.assertIsInstance(result, Canvas)

    def test_adds_label_space(self):
        """Labels add extra height."""
        # Labeled version should be taller than unlabeled
        canvases = [Canvas(8, 8, (255, 0, 0, 255)) for _ in range(4)]
        items = [(f"Item {i}", c) for i, c in enumerate(canvases)]

        labeled = create_labeled_sheet(items, ContactSheetOptions(columns=4))
        unlabeled = create_contact_sheet(canvases, ContactSheetOptions(columns=4))

        # Labeled should have some extra height for labels
        self.assertGreaterEqual(labeled.height, unlabeled.height)


class TestContactSheetOptions(TestCase):
    """Tests for ContactSheetOptions dataclass."""

    def test_default_values(self):
        """Options have sensible defaults."""
        options = ContactSheetOptions()

        self.assertEqual(options.columns, 4)
        self.assertEqual(options.padding, 4)
        self.assertEqual(options.scale, 1)
        self.assertFalse(options.show_index)

    def test_custom_values(self):
        """Custom values are accepted."""
        options = ContactSheetOptions(
            columns=3,
            padding=8,
            scale=2,
            show_index=True
        )

        self.assertEqual(options.columns, 3)
        self.assertEqual(options.padding, 8)
        self.assertEqual(options.scale, 2)
        self.assertTrue(options.show_index)

    def test_show_index_option(self):
        """show_index affects output."""
        canvases = [Canvas(8, 8, (i * 30, 0, 0, 255)) for i in range(6)]

        with_index = create_contact_sheet(canvases, ContactSheetOptions(show_index=True))
        without_index = create_contact_sheet(canvases, ContactSheetOptions(show_index=False))

        # With index should have extra space at top of cells
        self.assertGreaterEqual(with_index.height, without_index.height)


class TestGenerateVariationsPreview(TestCase):
    """Tests for variation preview generation."""

    def test_generates_multiple_variations(self):
        """Generates requested number of variations."""
        def simple_generator(seed=0, **kwargs):
            return Canvas(8, 8, (seed * 25 % 256, 0, 0, 255))

        result = generate_variations_preview(simple_generator, count=4, columns=2)

        self.assertIsInstance(result, Canvas)

    def test_uses_different_seeds(self):
        """Different seeds produce different results."""
        generated_colors = []

        def tracking_generator(seed=0, **kwargs):
            color = (seed * 25 % 256, 0, 0, 255)
            generated_colors.append(color)
            return Canvas(8, 8, color)

        generate_variations_preview(tracking_generator, count=4, seed_start=0)

        # Should have 4 different colors
        self.assertEqual(len(generated_colors), 4)
        self.assertEqual(len(set(generated_colors)), 4)

    def test_custom_seed_start(self):
        """seed_start parameter works."""
        generated_seeds = []

        def tracking_generator(seed=0, **kwargs):
            generated_seeds.append(seed)
            return Canvas(8, 8, (255, 0, 0, 255))

        generate_variations_preview(tracking_generator, count=3, seed_start=100)

        self.assertEqual(generated_seeds, [100, 101, 102])


class TestCreateComparisonStrip(TestCase):
    """Tests for comparison strip creation."""

    def test_horizontal_strip(self):
        """Creates horizontal strip."""
        canvases = [Canvas(8, 8, (i * 50, 0, 0, 255)) for i in range(4)]
        result = create_comparison_strip(canvases, horizontal=True)

        self.assertIsInstance(result, Canvas)
        # Horizontal should be wider than tall
        self.assertGreater(result.width, result.height)

    def test_vertical_strip(self):
        """Creates vertical strip."""
        canvases = [Canvas(8, 8, (i * 50, 0, 0, 255)) for i in range(4)]
        result = create_comparison_strip(canvases, horizontal=False)

        self.assertIsInstance(result, Canvas)
        # Vertical should be taller than wide
        self.assertGreater(result.height, result.width)

    def test_empty_list(self):
        """Handles empty canvas list."""
        result = create_comparison_strip([])

        self.assertIsInstance(result, Canvas)

    def test_padding_affects_size(self):
        """Padding affects strip size."""
        canvases = [Canvas(8, 8, (255, 0, 0, 255)) for _ in range(4)]

        small_pad = create_comparison_strip(canvases, padding=2)
        large_pad = create_comparison_strip(canvases, padding=10)

        self.assertGreater(large_pad.width, small_pad.width)

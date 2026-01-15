"""
Test Palette Tools - Tests for palette extraction and remapping.

Tests:
- extract_palette
- extract_palette_kmeans
- analyze_palette
- remap_to_palette
- remap_colors
- match_palette
- palette utilities
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests.framework import TestCase, CanvasFixtures
from core import Canvas, Palette


try:
    from editor.palette_tools import (
        ColorInfo,
        PaletteAnalysis,
        extract_palette,
        extract_palette_kmeans,
        analyze_palette,
        remap_to_palette,
        remap_colors,
        reduce_colors,
        match_palette,
        harmonize_palettes,
        create_palette_from_colors,
        palette_to_image,
        blend_palettes,
    )
    PALETTE_TOOLS_AVAILABLE = True
except ImportError as e:
    PALETTE_TOOLS_AVAILABLE = False
    IMPORT_ERROR = str(e)


class TestExtractPalette(TestCase):
    """Tests for extract_palette function."""

    def test_extract_palette_basic(self):
        """extract_palette extracts colors from canvas."""
        self.skipUnless(PALETTE_TOOLS_AVAILABLE, "Palette tools not available")

        canvas = CanvasFixtures.solid((255, 100, 50, 255), width=16, height=16)
        palette = extract_palette(canvas)

        self.assertGreater(len(palette), 0)

    def test_extract_palette_max_colors(self):
        """extract_palette respects max_colors."""
        self.skipUnless(PALETTE_TOOLS_AVAILABLE, "Palette tools not available")

        # Create canvas with many colors
        canvas = CanvasFixtures.gradient_h(
            (255, 0, 0, 255), (0, 0, 255, 255), width=32, height=16
        )

        palette = extract_palette(canvas, max_colors=8)

        self.assertLessEqual(len(palette), 8)

    def test_extract_palette_empty_canvas(self):
        """extract_palette handles empty canvas."""
        self.skipUnless(PALETTE_TOOLS_AVAILABLE, "Palette tools not available")

        canvas = Canvas(16, 16)
        palette = extract_palette(canvas)

        self.assertEqual(len(palette), 0)

    def test_extract_palette_excludes_transparent(self):
        """extract_palette excludes transparent by default."""
        self.skipUnless(PALETTE_TOOLS_AVAILABLE, "Palette tools not available")

        canvas = Canvas(16, 16)
        canvas.fill_rect(4, 4, 8, 8, (255, 0, 0, 255))

        palette = extract_palette(canvas, include_transparent=False)

        # Should not include fully transparent
        for i in range(len(palette)):
            self.assertGreater(palette.get(i)[3], 0)


class TestExtractPaletteKmeans(TestCase):
    """Tests for extract_palette_kmeans function."""

    def test_kmeans_basic(self):
        """extract_palette_kmeans clusters colors."""
        self.skipUnless(PALETTE_TOOLS_AVAILABLE, "Palette tools not available")

        canvas = CanvasFixtures.gradient_h(
            (255, 0, 0, 255), (0, 0, 255, 255), width=32, height=16
        )

        palette = extract_palette_kmeans(canvas, num_colors=4)

        self.assertLessEqual(len(palette), 4)

    def test_kmeans_empty_canvas(self):
        """extract_palette_kmeans handles empty canvas."""
        self.skipUnless(PALETTE_TOOLS_AVAILABLE, "Palette tools not available")

        canvas = Canvas(16, 16)
        palette = extract_palette_kmeans(canvas, num_colors=4)

        self.assertEqual(len(palette), 0)


class TestAnalyzePalette(TestCase):
    """Tests for analyze_palette function."""

    def test_analyze_palette_basic(self):
        """analyze_palette returns analysis."""
        self.skipUnless(PALETTE_TOOLS_AVAILABLE, "Palette tools not available")

        canvas = CanvasFixtures.solid((200, 100, 50, 255), width=16, height=16)
        analysis = analyze_palette(canvas)

        self.assertIsInstance(analysis, PaletteAnalysis)
        self.assertGreater(len(analysis.colors), 0)
        self.assertIsNotNone(analysis.dominant_color)
        self.assertIsNotNone(analysis.average_color)

    def test_analyze_palette_color_info(self):
        """analyze_palette provides color info."""
        self.skipUnless(PALETTE_TOOLS_AVAILABLE, "Palette tools not available")

        canvas = CanvasFixtures.solid((100, 150, 200, 255), width=16, height=16)
        analysis = analyze_palette(canvas)

        self.assertGreater(len(analysis.color_info), 0)
        self.assertIsInstance(analysis.color_info[0], ColorInfo)

    def test_analyze_palette_color_range(self):
        """analyze_palette calculates color range."""
        self.skipUnless(PALETTE_TOOLS_AVAILABLE, "Palette tools not available")

        canvas = CanvasFixtures.gradient_h(
            (50, 100, 150, 255), (200, 150, 100, 255), width=16, height=16
        )
        analysis = analyze_palette(canvas)

        self.assertIn('r', analysis.color_range)
        self.assertIn('g', analysis.color_range)
        self.assertIn('b', analysis.color_range)

    def test_analyze_palette_empty(self):
        """analyze_palette handles empty canvas."""
        self.skipUnless(PALETTE_TOOLS_AVAILABLE, "Palette tools not available")

        canvas = Canvas(16, 16)
        analysis = analyze_palette(canvas)

        self.assertEqual(len(analysis.colors), 0)


class TestRemapToPalette(TestCase):
    """Tests for remap_to_palette function."""

    def test_remap_basic(self):
        """remap_to_palette remaps colors."""
        self.skipUnless(PALETTE_TOOLS_AVAILABLE, "Palette tools not available")

        canvas = CanvasFixtures.solid((200, 100, 50, 255), width=16, height=16)

        palette = Palette()
        palette.add((255, 0, 0, 255))
        palette.add((0, 255, 0, 255))
        palette.add((0, 0, 255, 255))

        result = remap_to_palette(canvas, palette)

        self.assertCanvasSize(result, 16, 16)
        self.assertCanvasNotEmpty(result)

    def test_remap_preserves_transparency(self):
        """remap_to_palette preserves transparency."""
        self.skipUnless(PALETTE_TOOLS_AVAILABLE, "Palette tools not available")

        canvas = Canvas(16, 16)
        canvas.fill_rect(4, 4, 8, 8, (200, 100, 50, 255))

        palette = Palette()
        palette.add((255, 0, 0, 255))

        result = remap_to_palette(canvas, palette, preserve_transparency=True)

        # Transparent areas should remain transparent
        self.assertEqual(result.get_pixel(0, 0)[3], 0)

    def test_remap_empty_palette(self):
        """remap_to_palette handles empty palette."""
        self.skipUnless(PALETTE_TOOLS_AVAILABLE, "Palette tools not available")

        canvas = CanvasFixtures.solid((200, 100, 50, 255), width=16, height=16)
        palette = Palette()

        result = remap_to_palette(canvas, palette)

        # Should return copy of original
        self.assertCanvasEqual(result, canvas)


class TestRemapColors(TestCase):
    """Tests for remap_colors function."""

    def test_remap_colors_exact(self):
        """remap_colors with exact matches."""
        self.skipUnless(PALETTE_TOOLS_AVAILABLE, "Palette tools not available")

        canvas = CanvasFixtures.solid((255, 0, 0, 255), width=16, height=16)

        color_map = {
            (255, 0, 0, 255): (0, 255, 0, 255)
        }

        result = remap_colors(canvas, color_map)

        # Should have remapped red to green
        pixel = result.get_pixel(8, 8)
        self.assertEqual(tuple(pixel), (0, 255, 0, 255))

    def test_remap_colors_with_tolerance(self):
        """remap_colors with tolerance."""
        self.skipUnless(PALETTE_TOOLS_AVAILABLE, "Palette tools not available")

        canvas = CanvasFixtures.solid((250, 5, 5, 255), width=16, height=16)

        color_map = {
            (255, 0, 0, 255): (0, 255, 0, 255)
        }

        result = remap_colors(canvas, color_map, tolerance=10)

        # Should match within tolerance
        pixel = result.get_pixel(8, 8)
        self.assertEqual(tuple(pixel), (0, 255, 0, 255))


class TestReduceColors(TestCase):
    """Tests for reduce_colors function."""

    def test_reduce_colors_basic(self):
        """reduce_colors limits colors."""
        self.skipUnless(PALETTE_TOOLS_AVAILABLE, "Palette tools not available")

        canvas = CanvasFixtures.gradient_h(
            (255, 0, 0, 255), (0, 0, 255, 255), width=32, height=16
        )

        result = reduce_colors(canvas, max_colors=4)

        # Count unique colors in result
        colors = set()
        for y in range(result.height):
            for x in range(result.width):
                pixel = tuple(result.get_pixel(x, y))
                if pixel[3] > 0:
                    colors.add(pixel)

        self.assertLessEqual(len(colors), 4)


class TestMatchPalette(TestCase):
    """Tests for match_palette function."""

    def test_match_palette_basic(self):
        """match_palette transfers colors."""
        self.skipUnless(PALETTE_TOOLS_AVAILABLE, "Palette tools not available")

        source = CanvasFixtures.solid((100, 100, 100, 255), width=16, height=16)
        reference = CanvasFixtures.solid((255, 100, 50, 255), width=16, height=16)

        result = match_palette(source, reference)

        self.assertCanvasSize(result, 16, 16)
        self.assertCanvasNotEmpty(result)


class TestHarmonizePalettes(TestCase):
    """Tests for harmonize_palettes function."""

    def test_harmonize_basic(self):
        """harmonize_palettes creates unified palette."""
        self.skipUnless(PALETTE_TOOLS_AVAILABLE, "Palette tools not available")

        canvas1 = CanvasFixtures.solid((255, 0, 0, 255), width=16, height=16)
        canvas2 = CanvasFixtures.solid((0, 255, 0, 255), width=16, height=16)

        palette = harmonize_palettes([canvas1, canvas2], target_size=8)

        self.assertLessEqual(len(palette), 8)
        self.assertGreater(len(palette), 0)


class TestPaletteUtilities(TestCase):
    """Tests for palette utility functions."""

    def test_create_palette_from_colors(self):
        """create_palette_from_colors creates palette."""
        self.skipUnless(PALETTE_TOOLS_AVAILABLE, "Palette tools not available")

        colors = [
            (255, 0, 0),
            (0, 255, 0),
            (0, 0, 255, 255),
        ]

        palette = create_palette_from_colors(colors)

        self.assertEqual(len(palette), 3)

    def test_palette_to_image(self):
        """palette_to_image creates visualization."""
        self.skipUnless(PALETTE_TOOLS_AVAILABLE, "Palette tools not available")

        palette = Palette()
        palette.add((255, 0, 0, 255))
        palette.add((0, 255, 0, 255))
        palette.add((0, 0, 255, 255))

        image = palette_to_image(palette, swatch_size=8, columns=3)

        self.assertCanvasNotEmpty(image)
        self.assertEqual(image.width, 24)  # 3 * 8

    def test_blend_palettes(self):
        """blend_palettes blends two palettes."""
        self.skipUnless(PALETTE_TOOLS_AVAILABLE, "Palette tools not available")

        p1 = Palette()
        p1.add((255, 0, 0, 255))
        p1.add((0, 0, 0, 255))

        p2 = Palette()
        p2.add((0, 0, 255, 255))
        p2.add((255, 255, 255, 255))

        blended = blend_palettes(p1, p2, blend_factor=0.5)

        self.assertEqual(len(blended), 2)
        # First color should be blend of red and blue
        first = blended.get(0)
        self.assertGreater(first[0], 100)  # Some red
        self.assertGreater(first[2], 100)  # Some blue

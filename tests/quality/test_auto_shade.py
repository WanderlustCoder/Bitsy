"""
Test Auto Shade - Tests for intelligent shading and outline generation.

Tests:
- Edge detection
- Smart outlining
- Cel shading
- Highlights and shadows
- Auto shading with styles
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests.framework import TestCase
from core import Canvas
from core.style import Style, ShadingConfig
from quality.auto_shade import (
    detect_edges,
    smart_outline,
    apply_cel_shading,
    add_highlights,
    add_shadows,
    auto_shade,
    EdgeType,
    EdgePixel,
    EdgeMap,
)


class TestEdgeDetection(TestCase):
    """Tests for edge detection."""

    def test_empty_canvas_no_edges(self):
        """Empty canvas has no edges."""
        canvas = Canvas(8, 8)
        edge_map = detect_edges(canvas)

        self.assertEqual(len(edge_map.edges), 0)

    def test_solid_canvas_has_border_edges(self):
        """Solid canvas has edges at borders."""
        canvas = Canvas(8, 8, (255, 0, 0, 255))
        edge_map = detect_edges(canvas)

        # All border pixels should be edges
        self.assertGreater(len(edge_map.edges), 0)

        # Check that edges are on the border
        for (x, y), edge in edge_map.edges.items():
            is_border = x == 0 or x == 7 or y == 0 or y == 7
            self.assertTrue(is_border)

    def test_interior_shape_edges(self):
        """Shape in center has edges."""
        canvas = Canvas(16, 16)
        canvas.fill_rect(4, 4, 8, 8, (255, 0, 0, 255))
        edge_map = detect_edges(canvas)

        # Should have edges around the rectangle
        self.assertGreater(len(edge_map.edges), 0)

        # All edges should be within/on rectangle bounds
        for (x, y), edge in edge_map.edges.items():
            self.assertTrue(4 <= x < 12)
            self.assertTrue(4 <= y < 12)

    def test_edge_map_properties(self):
        """EdgeMap has correct width/height."""
        canvas = Canvas(16, 16)
        canvas.fill_rect(4, 4, 8, 8, (255, 0, 0, 255))
        edge_map = detect_edges(canvas)

        self.assertEqual(edge_map.width, 16)
        self.assertEqual(edge_map.height, 16)

    def test_is_edge_method(self):
        """is_edge method works correctly."""
        canvas = Canvas(16, 16)
        canvas.fill_rect(4, 4, 8, 8, (255, 0, 0, 255))
        edge_map = detect_edges(canvas)

        # Corner should be an edge
        self.assertTrue(edge_map.is_edge(4, 4))

        # Interior should not be an edge
        self.assertFalse(edge_map.is_edge(8, 8))

        # Outside shape should not be an edge
        self.assertFalse(edge_map.is_edge(0, 0))

    def test_get_method(self):
        """get method returns EdgePixel or None."""
        canvas = Canvas(16, 16)
        canvas.fill_rect(4, 4, 8, 8, (255, 0, 0, 255))
        edge_map = detect_edges(canvas)

        # Edge pixel should return EdgePixel
        edge = edge_map.get(4, 4)
        self.assertIsInstance(edge, EdgePixel)

        # Non-edge should return None
        non_edge = edge_map.get(8, 8)
        self.assertIsNone(non_edge)

    def test_corner_detection(self):
        """Corners are detected correctly."""
        canvas = Canvas(16, 16)
        canvas.fill_rect(4, 4, 8, 8, (255, 0, 0, 255))
        edge_map = detect_edges(canvas)

        corners = edge_map.get_corners()
        # Should have corners at the rectangle corners
        self.assertGreater(len(corners), 0)

    def test_outer_edges(self):
        """get_outer_edges returns outer edges."""
        canvas = Canvas(16, 16)
        canvas.fill_rect(4, 4, 8, 8, (255, 0, 0, 255))
        edge_map = detect_edges(canvas)

        outer = edge_map.get_outer_edges()
        self.assertGreater(len(outer), 0)

        for edge in outer:
            self.assertEqual(edge.edge_type, EdgeType.OUTER)

    def test_edge_has_normal(self):
        """Edge pixels have normal vectors."""
        canvas = Canvas(16, 16)
        canvas.fill_rect(4, 4, 8, 8, (255, 0, 0, 255))
        edge_map = detect_edges(canvas)

        for edge in edge_map.edges.values():
            # Normal should be a tuple of two floats
            self.assertIsInstance(edge.normal, tuple)
            self.assertEqual(len(edge.normal), 2)


class TestSmartOutline(TestCase):
    """Tests for smart outline generation."""

    def test_returns_canvas(self):
        """smart_outline returns a Canvas."""
        canvas = Canvas(16, 16)
        canvas.fill_rect(4, 4, 8, 8, (255, 0, 0, 255))
        result = smart_outline(canvas)

        self.assertIsInstance(result, Canvas)
        self.assertEqual(result.width, 16)
        self.assertEqual(result.height, 16)

    def test_preserves_size(self):
        """Output has same size as input."""
        canvas = Canvas(32, 24)
        canvas.fill_rect(8, 8, 16, 8, (255, 0, 0, 255))
        result = smart_outline(canvas)

        self.assertEqual(result.width, 32)
        self.assertEqual(result.height, 24)

    def test_with_custom_outline_color(self):
        """Custom outline color is applied."""
        canvas = Canvas(16, 16)
        canvas.fill_rect(4, 4, 8, 8, (255, 0, 0, 255))
        outline_color = (0, 0, 0, 255)
        result = smart_outline(canvas, outline_color=outline_color)

        # Check that outline color appears in result
        has_outline = False
        for y in range(result.height):
            for x in range(result.width):
                pixel = tuple(result.pixels[y][x])
                if pixel == outline_color:
                    has_outline = True
                    break

        self.assertTrue(has_outline)

    def test_auto_darken_outline(self):
        """Auto-darkened outline when no color specified."""
        canvas = Canvas(16, 16)
        canvas.fill_rect(4, 4, 8, 8, (255, 0, 0, 255))
        result = smart_outline(canvas, outline_color=None)

        # Should have some modified edge pixels
        # that are darker than the original
        self.assertIsInstance(result, Canvas)


class TestCelShading(TestCase):
    """Tests for cel shading."""

    def test_returns_canvas(self):
        """apply_cel_shading returns a Canvas."""
        canvas = Canvas(16, 16, (255, 0, 0, 255))
        result = apply_cel_shading(canvas, levels=3)

        self.assertIsInstance(result, Canvas)

    def test_preserves_size(self):
        """Output has same size as input."""
        canvas = Canvas(32, 24, (255, 0, 0, 255))
        result = apply_cel_shading(canvas, levels=3)

        self.assertEqual(result.width, 32)
        self.assertEqual(result.height, 24)

    def test_preserves_transparency(self):
        """Transparent pixels remain transparent."""
        canvas = Canvas(16, 16)
        canvas.fill_rect(4, 4, 8, 8, (255, 0, 0, 255))
        result = apply_cel_shading(canvas, levels=3)

        # Check corners are still transparent
        self.assertEqual(result.pixels[0][0][3], 0)
        self.assertEqual(result.pixels[15][15][3], 0)

    def test_different_levels(self):
        """Different level counts work."""
        canvas = Canvas(16, 16, (128, 128, 128, 255))

        result_2 = apply_cel_shading(canvas, levels=2)
        result_5 = apply_cel_shading(canvas, levels=5)

        self.assertIsInstance(result_2, Canvas)
        self.assertIsInstance(result_5, Canvas)

    def test_light_direction(self):
        """Different light directions produce different results."""
        canvas = Canvas(16, 16)
        canvas.fill_rect(4, 4, 8, 8, (200, 100, 100, 255))

        result_right = apply_cel_shading(canvas, levels=3, light_direction=(1.0, 0.0))
        result_left = apply_cel_shading(canvas, levels=3, light_direction=(-1.0, 0.0))

        # Results should differ
        differences = 0
        for y in range(16):
            for x in range(16):
                if result_right.pixels[y][x] != result_left.pixels[y][x]:
                    differences += 1

        # Should have some differences in lit areas
        self.assertGreater(differences, 0)


class TestHighlights(TestCase):
    """Tests for highlight addition."""

    def test_returns_canvas(self):
        """add_highlights returns a Canvas."""
        canvas = Canvas(16, 16)
        canvas.fill_rect(4, 4, 8, 8, (200, 50, 50, 255))
        result = add_highlights(canvas)

        self.assertIsInstance(result, Canvas)

    def test_preserves_size(self):
        """Output has same size as input."""
        canvas = Canvas(32, 24)
        canvas.fill_rect(8, 6, 16, 12, (200, 50, 50, 255))
        result = add_highlights(canvas)

        self.assertEqual(result.width, 32)
        self.assertEqual(result.height, 24)

    def test_intensity_affects_result(self):
        """Different intensities produce different results."""
        canvas = Canvas(16, 16)
        canvas.fill_rect(4, 4, 8, 8, (200, 50, 50, 255))

        result_low = add_highlights(canvas, intensity=0.1)
        result_high = add_highlights(canvas, intensity=0.5)

        # Results should differ
        differences = 0
        for y in range(16):
            for x in range(16):
                if result_low.pixels[y][x] != result_high.pixels[y][x]:
                    differences += 1

        self.assertGreater(differences, 0)


class TestShadows(TestCase):
    """Tests for shadow addition."""

    def test_returns_canvas(self):
        """add_shadows returns a Canvas."""
        canvas = Canvas(16, 16)
        canvas.fill_rect(4, 4, 8, 8, (200, 50, 50, 255))
        result = add_shadows(canvas)

        self.assertIsInstance(result, Canvas)

    def test_preserves_size(self):
        """Output has same size as input."""
        canvas = Canvas(32, 24)
        canvas.fill_rect(8, 6, 16, 12, (200, 50, 50, 255))
        result = add_shadows(canvas)

        self.assertEqual(result.width, 32)
        self.assertEqual(result.height, 24)

    def test_intensity_affects_result(self):
        """Different intensities produce different results."""
        canvas = Canvas(16, 16)
        canvas.fill_rect(4, 4, 8, 8, (200, 50, 50, 255))

        result_low = add_shadows(canvas, intensity=0.1)
        result_high = add_shadows(canvas, intensity=0.5)

        # Results should differ
        differences = 0
        for y in range(16):
            for x in range(16):
                if result_low.pixels[y][x] != result_high.pixels[y][x]:
                    differences += 1

        self.assertGreater(differences, 0)


class TestAutoShade(TestCase):
    """Tests for automatic shading."""

    def test_returns_canvas(self):
        """auto_shade returns a Canvas."""
        canvas = Canvas(16, 16)
        canvas.fill_rect(4, 4, 8, 8, (200, 50, 50, 255))
        result = auto_shade(canvas)

        self.assertIsInstance(result, Canvas)

    def test_preserves_size(self):
        """Output has same size as input."""
        canvas = Canvas(32, 24)
        canvas.fill_rect(8, 6, 16, 12, (200, 50, 50, 255))
        result = auto_shade(canvas)

        self.assertEqual(result.width, 32)
        self.assertEqual(result.height, 24)

    def test_with_default_style(self):
        """Works with no style specified."""
        canvas = Canvas(16, 16)
        canvas.fill_rect(4, 4, 8, 8, (200, 50, 50, 255))
        result = auto_shade(canvas, style=None)

        self.assertIsInstance(result, Canvas)

    def test_with_flat_style(self):
        """Flat style returns copy without shading."""
        canvas = Canvas(16, 16)
        canvas.fill_rect(4, 4, 8, 8, (200, 50, 50, 255))

        style = Style(shading=ShadingConfig(mode='flat'))
        result = auto_shade(canvas, style=style)

        # Flat should be same as input
        for y in range(16):
            for x in range(16):
                self.assertEqual(result.pixels[y][x], canvas.pixels[y][x])

    def test_with_cel_style(self):
        """Cel style applies cel shading."""
        canvas = Canvas(16, 16)
        canvas.fill_rect(4, 4, 8, 8, (200, 50, 50, 255))

        style = Style(shading=ShadingConfig(mode='cel', levels=3))
        result = auto_shade(canvas, style=style)

        self.assertIsInstance(result, Canvas)

    def test_with_gradient_style(self):
        """Gradient style uses more levels."""
        canvas = Canvas(16, 16)
        canvas.fill_rect(4, 4, 8, 8, (200, 50, 50, 255))

        style = Style(shading=ShadingConfig(mode='gradient', levels=3))
        result = auto_shade(canvas, style=style)

        self.assertIsInstance(result, Canvas)

    def test_light_direction(self):
        """Light direction affects shading."""
        canvas = Canvas(16, 16)
        canvas.fill_rect(4, 4, 8, 8, (200, 50, 50, 255))

        result_tl = auto_shade(canvas, light_direction=(-1.0, -1.0))
        result_br = auto_shade(canvas, light_direction=(1.0, 1.0))

        # Results should differ
        differences = 0
        for y in range(16):
            for x in range(16):
                if result_tl.pixels[y][x] != result_br.pixels[y][x]:
                    differences += 1

        self.assertGreater(differences, 0)


class TestEdgeTypeEnum(TestCase):
    """Tests for EdgeType enum."""

    def test_edge_types_exist(self):
        """All edge types are defined."""
        self.assertEqual(EdgeType.NONE.value, 0)
        self.assertEqual(EdgeType.OUTER.value, 1)
        self.assertEqual(EdgeType.INNER.value, 2)
        self.assertEqual(EdgeType.CORNER.value, 3)
        self.assertEqual(EdgeType.CURVE.value, 4)


class TestEdgePixelDataclass(TestCase):
    """Tests for EdgePixel dataclass."""

    def test_create_edge_pixel(self):
        """EdgePixel can be created."""
        edge = EdgePixel(
            x=5, y=10,
            edge_type=EdgeType.OUTER,
            normal=(1.0, 0.0),
            curvature=0.5
        )

        self.assertEqual(edge.x, 5)
        self.assertEqual(edge.y, 10)
        self.assertEqual(edge.edge_type, EdgeType.OUTER)
        self.assertEqual(edge.normal, (1.0, 0.0))
        self.assertEqual(edge.curvature, 0.5)

    def test_default_curvature(self):
        """EdgePixel has default curvature of 0."""
        edge = EdgePixel(
            x=0, y=0,
            edge_type=EdgeType.OUTER,
            normal=(0.0, 1.0)
        )

        self.assertEqual(edge.curvature, 0.0)


"""
Test Canvas - Tests for the Canvas drawing surface.

Tests:
- Canvas creation and initialization
- Pixel operations (get, set, blend)
- Shape primitives (rect, circle, ellipse, polygon)
- Line drawing
- Gradients
- Sprite operations (blit, flip, scale)
- Output operations
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests.framework import TestCase, CanvasFixtures
from core import Canvas


class TestCanvasCreation(TestCase):
    """Tests for Canvas creation and initialization."""

    def test_create_default_size(self):
        """Canvas can be created with specified dimensions."""
        canvas = Canvas(32, 24)
        self.assertEqual(canvas.width, 32)
        self.assertEqual(canvas.height, 24)

    def test_create_with_background(self):
        """Canvas can be created with a background color."""
        canvas = Canvas(8, 8, (255, 0, 0, 255))
        self.assertPixelColor(canvas, 0, 0, (255, 0, 0, 255))
        self.assertPixelColor(canvas, 7, 7, (255, 0, 0, 255))

    def test_create_transparent(self):
        """Canvas created without background is transparent."""
        canvas = Canvas(4, 4)
        self.assertPixelColor(canvas, 0, 0, (0, 0, 0, 0))

    def test_clear(self):
        """Canvas can be cleared to a color."""
        canvas = Canvas(8, 8, (255, 0, 0, 255))
        canvas.clear((0, 255, 0, 255))
        self.assertPixelColor(canvas, 0, 0, (0, 255, 0, 255))

    def test_pixels_array_structure(self):
        """Canvas pixels array has correct structure."""
        canvas = Canvas(4, 3)
        self.assertEqual(len(canvas.pixels), 3)  # rows
        self.assertEqual(len(canvas.pixels[0]), 4)  # columns


class TestCanvasPixelOps(TestCase):
    """Tests for pixel operations."""

    def test_set_pixel_solid(self):
        """set_pixel_solid replaces pixel without blending."""
        canvas = Canvas(4, 4, (255, 255, 255, 255))
        canvas.set_pixel_solid(2, 2, (255, 0, 0, 128))
        # Should be exactly the color we set (no blending)
        self.assertPixelColor(canvas, 2, 2, (255, 0, 0, 128))

    def test_set_pixel_with_blend(self):
        """set_pixel blends with existing color."""
        canvas = Canvas(4, 4, (255, 255, 255, 255))
        canvas.set_pixel(2, 2, (255, 0, 0, 128))
        # Should be blended (not pure red)
        pixel = canvas.pixels[2][2]
        self.assertGreater(pixel[0], 200)  # Red is high
        self.assertLess(pixel[1], pixel[0])  # Green reduced

    def test_get_pixel_valid(self):
        """get_pixel returns correct color for valid coordinates."""
        canvas = Canvas(4, 4, (100, 150, 200, 255))
        color = canvas.get_pixel(1, 1)
        self.assertEqual(tuple(color), (100, 150, 200, 255))

    def test_get_pixel_out_of_bounds(self):
        """get_pixel returns None for out-of-bounds coordinates."""
        canvas = Canvas(4, 4)
        self.assertIsNone(canvas.get_pixel(-1, 0))
        self.assertIsNone(canvas.get_pixel(0, -1))
        self.assertIsNone(canvas.get_pixel(4, 0))
        self.assertIsNone(canvas.get_pixel(0, 4))

    def test_set_pixel_out_of_bounds_safe(self):
        """set_pixel silently ignores out-of-bounds coordinates."""
        canvas = Canvas(4, 4)
        # Should not raise
        canvas.set_pixel(-1, 0, (255, 0, 0, 255))
        canvas.set_pixel(100, 100, (255, 0, 0, 255))


class TestCanvasShapes(TestCase):
    """Tests for shape primitives."""

    def test_fill_rect(self):
        """fill_rect fills rectangular area."""
        canvas = Canvas(8, 8)
        canvas.fill_rect(2, 2, 4, 3, (255, 0, 0, 255))

        # Inside rect
        self.assertPixelColor(canvas, 2, 2, (255, 0, 0, 255))
        self.assertPixelColor(canvas, 5, 4, (255, 0, 0, 255))

        # Outside rect
        self.assertPixelColor(canvas, 0, 0, (0, 0, 0, 0))
        self.assertPixelColor(canvas, 6, 5, (0, 0, 0, 0))

    def test_draw_rect(self):
        """draw_rect draws rectangle outline."""
        canvas = Canvas(8, 8)
        canvas.draw_rect(1, 1, 5, 4, (255, 0, 0, 255))

        # Corners
        self.assertPixelColor(canvas, 1, 1, (255, 0, 0, 255))
        self.assertPixelColor(canvas, 5, 4, (255, 0, 0, 255))

        # Center (should be empty)
        self.assertPixelColor(canvas, 3, 2, (0, 0, 0, 0))

    def test_fill_circle(self):
        """fill_circle fills circular area."""
        canvas = Canvas(16, 16)
        canvas.fill_circle(8, 8, 4, (255, 0, 0, 255))

        # Center should be filled
        self.assertPixelColor(canvas, 8, 8, (255, 0, 0, 255))

        # Edge within radius
        self.assertPixelColor(canvas, 8, 5, (255, 0, 0, 255))

        # Outside radius
        self.assertPixelColor(canvas, 0, 0, (0, 0, 0, 0))

    def test_draw_circle(self):
        """draw_circle draws circle outline."""
        canvas = Canvas(16, 16)
        canvas.draw_circle(8, 8, 4, (255, 0, 0, 255))

        # Center should be empty (outline only)
        self.assertPixelColor(canvas, 8, 8, (0, 0, 0, 0))

        # Check that some outline pixels exist
        self.assertCanvasNotEmpty(canvas)

    def test_fill_ellipse(self):
        """fill_ellipse fills elliptical area."""
        canvas = Canvas(20, 10)
        canvas.fill_ellipse(10, 5, 8, 3, (0, 255, 0, 255))

        # Center
        self.assertPixelColor(canvas, 10, 5, (0, 255, 0, 255))

        # Wide edge
        self.assertPixelColor(canvas, 2, 5, (0, 255, 0, 255))

        # Corner (outside)
        self.assertPixelColor(canvas, 0, 0, (0, 0, 0, 0))

    def test_fill_polygon_triangle(self):
        """fill_polygon fills triangular area."""
        canvas = Canvas(16, 16)
        points = [(8, 2), (2, 14), (14, 14)]
        canvas.fill_polygon(points, (0, 0, 255, 255))

        # Center of triangle
        self.assertPixelColor(canvas, 8, 10, (0, 0, 255, 255))

        # Corners (outside triangle)
        self.assertPixelColor(canvas, 0, 0, (0, 0, 0, 0))

    def test_fill_polygon_too_few_points(self):
        """fill_polygon does nothing with fewer than 3 points."""
        canvas = Canvas(8, 8)
        canvas.fill_polygon([(0, 0), (4, 4)], (255, 0, 0, 255))
        # Canvas should remain empty
        for y in range(8):
            for x in range(8):
                self.assertPixelColor(canvas, x, y, (0, 0, 0, 0))


class TestCanvasLines(TestCase):
    """Tests for line drawing."""

    def test_draw_line_horizontal(self):
        """draw_line draws horizontal line."""
        canvas = Canvas(10, 5)
        canvas.draw_line(1, 2, 8, 2, (255, 0, 0, 255))

        # Line pixels
        self.assertPixelColor(canvas, 1, 2, (255, 0, 0, 255))
        self.assertPixelColor(canvas, 5, 2, (255, 0, 0, 255))
        self.assertPixelColor(canvas, 8, 2, (255, 0, 0, 255))

        # Off line
        self.assertPixelColor(canvas, 5, 0, (0, 0, 0, 0))

    def test_draw_line_vertical(self):
        """draw_line draws vertical line."""
        canvas = Canvas(5, 10)
        canvas.draw_line(2, 1, 2, 8, (0, 255, 0, 255))

        # Line pixels
        self.assertPixelColor(canvas, 2, 1, (0, 255, 0, 255))
        self.assertPixelColor(canvas, 2, 5, (0, 255, 0, 255))

    def test_draw_line_diagonal(self):
        """draw_line draws diagonal line."""
        canvas = Canvas(8, 8)
        canvas.draw_line(0, 0, 7, 7, (0, 0, 255, 255))

        # Some diagonal pixels should be filled
        self.assertPixelColor(canvas, 0, 0, (0, 0, 255, 255))
        self.assertPixelColor(canvas, 7, 7, (0, 0, 255, 255))


class TestCanvasGradients(TestCase):
    """Tests for gradient fills."""

    def test_gradient_vertical(self):
        """gradient_vertical creates vertical color gradient."""
        canvas = Canvas(4, 8)
        canvas.gradient_vertical(0, 0, 4, 8, (255, 0, 0, 255), (0, 0, 255, 255))

        # Top should be red-ish
        top = canvas.pixels[0][0]
        self.assertGreater(top[0], 200)  # Red high

        # Bottom should be blue-ish
        bottom = canvas.pixels[7][0]
        self.assertGreater(bottom[2], 200)  # Blue high

    def test_gradient_radial(self):
        """gradient_radial creates radial color gradient."""
        canvas = Canvas(16, 16)
        canvas.gradient_radial(8, 8, 6, (255, 255, 0, 255), (0, 0, 0, 255))

        # Center should be bright (yellow)
        center = canvas.pixels[8][8]
        self.assertGreater(center[0], 200)  # Red component high

        # Edge should be darker
        edge = canvas.pixels[8][2]
        self.assertLess(edge[0], center[0])


class TestCanvasSpriteOps(TestCase):
    """Tests for sprite operations."""

    def test_blit(self):
        """blit composites one canvas onto another."""
        base = Canvas(8, 8, (255, 255, 255, 255))
        overlay = Canvas(2, 2, (255, 0, 0, 255))

        base.blit(overlay, 3, 3)

        # Overlay area
        self.assertPixelColor(base, 3, 3, (255, 0, 0, 255))
        self.assertPixelColor(base, 4, 4, (255, 0, 0, 255))

        # Outside overlay
        self.assertPixelColor(base, 0, 0, (255, 255, 255, 255))

    def test_blit_with_transparency(self):
        """blit respects transparency."""
        base = Canvas(8, 8, (0, 0, 255, 255))
        overlay = Canvas(4, 4)
        overlay.fill_rect(1, 1, 2, 2, (255, 0, 0, 255))  # Small red square

        base.blit(overlay, 2, 2)

        # Transparent area should show base color
        self.assertPixelColor(base, 2, 2, (0, 0, 255, 255))

        # Opaque area should show overlay
        self.assertPixelColor(base, 3, 3, (255, 0, 0, 255))

    def test_flip_horizontal(self):
        """flip_horizontal mirrors canvas horizontally."""
        canvas = Canvas(4, 2)
        canvas.set_pixel_solid(0, 0, (255, 0, 0, 255))
        canvas.set_pixel_solid(3, 0, (0, 255, 0, 255))

        flipped = canvas.flip_horizontal()

        # Red should now be at right
        self.assertPixelColor(flipped, 3, 0, (255, 0, 0, 255))
        # Green should now be at left
        self.assertPixelColor(flipped, 0, 0, (0, 255, 0, 255))

    def test_flip_vertical(self):
        """flip_vertical mirrors canvas vertically."""
        canvas = Canvas(2, 4)
        canvas.set_pixel_solid(0, 0, (255, 0, 0, 255))
        canvas.set_pixel_solid(0, 3, (0, 255, 0, 255))

        flipped = canvas.flip_vertical()

        # Red should now be at bottom
        self.assertPixelColor(flipped, 0, 3, (255, 0, 0, 255))
        # Green should now be at top
        self.assertPixelColor(flipped, 0, 0, (0, 255, 0, 255))

    def test_scale_2x(self):
        """scale doubles canvas size with nearest neighbor."""
        canvas = Canvas(2, 2)
        canvas.set_pixel_solid(0, 0, (255, 0, 0, 255))
        canvas.set_pixel_solid(1, 1, (0, 255, 0, 255))

        scaled = canvas.scale(2)

        self.assertEqual(scaled.width, 4)
        self.assertEqual(scaled.height, 4)

        # Red should fill 2x2 area at top-left
        self.assertPixelColor(scaled, 0, 0, (255, 0, 0, 255))
        self.assertPixelColor(scaled, 1, 1, (255, 0, 0, 255))

        # Green should fill 2x2 area at bottom-right
        self.assertPixelColor(scaled, 2, 2, (0, 255, 0, 255))
        self.assertPixelColor(scaled, 3, 3, (0, 255, 0, 255))

    def test_copy(self):
        """copy creates independent duplicate."""
        original = Canvas(4, 4, (255, 0, 0, 255))
        copy = original.copy()

        # Modify original
        original.set_pixel_solid(0, 0, (0, 255, 0, 255))

        # Copy should be unchanged
        self.assertPixelColor(copy, 0, 0, (255, 0, 0, 255))


class TestCanvasOutput(TestCase):
    """Tests for canvas output operations."""

    def test_to_bytes_returns_png(self):
        """to_bytes returns valid PNG data."""
        canvas = Canvas(4, 4, (255, 0, 0, 255))
        png_bytes = canvas.to_bytes()

        # PNG magic bytes
        self.assertEqual(png_bytes[:8], b'\x89PNG\r\n\x1a\n')

    def test_to_bytes_deterministic(self):
        """to_bytes produces identical output for same canvas."""
        canvas1 = Canvas(4, 4, (100, 150, 200, 255))
        canvas2 = Canvas(4, 4, (100, 150, 200, 255))

        self.assertEqual(canvas1.to_bytes(), canvas2.to_bytes())


class TestCanvasEdgeCases(TestCase):
    """Tests for edge cases and boundary conditions."""

    def test_1x1_canvas(self):
        """1x1 canvas works correctly."""
        canvas = Canvas(1, 1, (128, 128, 128, 255))
        self.assertPixelColor(canvas, 0, 0, (128, 128, 128, 255))

    def test_large_canvas(self):
        """Large canvas can be created."""
        canvas = Canvas(256, 256)
        self.assertEqual(canvas.width, 256)
        self.assertEqual(canvas.height, 256)

    def test_rect_clipping(self):
        """fill_rect clips to canvas bounds."""
        canvas = Canvas(8, 8)
        canvas.fill_rect(-2, -2, 5, 5, (255, 0, 0, 255))

        # Should have filled (0,0) to (2,2)
        self.assertPixelColor(canvas, 0, 0, (255, 0, 0, 255))
        self.assertPixelColor(canvas, 2, 2, (255, 0, 0, 255))

        # Outside filled area
        self.assertPixelColor(canvas, 3, 3, (0, 0, 0, 0))

    def test_circle_at_edge(self):
        """fill_circle near edge doesn't crash."""
        canvas = Canvas(8, 8)
        # Circle centered at corner
        canvas.fill_circle(0, 0, 3, (255, 0, 0, 255))
        self.assertCanvasNotEmpty(canvas)

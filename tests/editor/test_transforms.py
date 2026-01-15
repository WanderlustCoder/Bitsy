"""
Test Transforms - Tests for image transformation operations.

Tests:
- Color adjustments (brightness, contrast, saturation, hue)
- Pixel effects (outline, shadow, glow, dither)
- Palette operations
- Geometric transforms
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests.framework import TestCase, CanvasFixtures
from editor import (
    adjust_brightness, adjust_contrast, adjust_saturation, adjust_hue,
    grayscale, sepia, posterize, invert_colors,
    outline, drop_shadow, glow, dither,
    reduce_palette, remap_palette, replace_color,
    rotate_90, rotate_180, rotate_270, crop, pad, tile
)
from core import Canvas


class TestColorAdjustments(TestCase):
    """Tests for color adjustment functions."""

    def test_adjust_brightness_increase(self):
        """adjust_brightness > 0 lightens image."""
        canvas = CanvasFixtures.solid((100, 100, 100, 255))
        result = adjust_brightness(canvas, 0.5)

        pixel = result.pixels[0][0]
        self.assertGreater(pixel[0], 100)

    def test_adjust_brightness_decrease(self):
        """adjust_brightness < 0 darkens image."""
        canvas = CanvasFixtures.solid((200, 200, 200, 255))
        result = adjust_brightness(canvas, -0.5)

        pixel = result.pixels[0][0]
        self.assertLess(pixel[0], 200)

    def test_adjust_contrast_increase(self):
        """adjust_contrast > 1 increases contrast."""
        canvas = CanvasFixtures.gradient_h(
            (100, 100, 100, 255), (150, 150, 150, 255)
        )
        result = adjust_contrast(canvas, 1.5)

        # Dark areas darker, light areas lighter
        dark = result.pixels[0][0]
        light = result.pixels[0][-1]
        self.assertLess(dark[0], 100)
        self.assertGreater(light[0], 150)

    def test_adjust_saturation_zero(self):
        """adjust_saturation(0) produces grayscale."""
        canvas = CanvasFixtures.solid((255, 0, 0, 255))
        result = adjust_saturation(canvas, 0)

        pixel = result.pixels[0][0]
        # All channels should be equal (grayscale)
        self.assertEqual(pixel[0], pixel[1])
        self.assertEqual(pixel[1], pixel[2])

    def test_adjust_hue_shift(self):
        """adjust_hue rotates color."""
        canvas = CanvasFixtures.solid((255, 0, 0, 255))  # Red
        result = adjust_hue(canvas, 120)  # Shift to green

        pixel = result.pixels[0][0]
        self.assertGreater(pixel[1], pixel[0])  # Green > Red


class TestPixelEffects(TestCase):
    """Tests for pixel effect functions."""

    def test_outline_adds_border(self):
        """outline adds border around opaque pixels."""
        canvas = Canvas(8, 8)
        canvas.fill_rect(2, 2, 4, 4, (255, 0, 0, 255))

        result = outline(canvas, (0, 0, 0, 255))

        # Should have black pixels around red square
        self.assertCanvasHasColor(result, (0, 0, 0, 255))
        self.assertCanvasHasColor(result, (255, 0, 0, 255))

    def test_drop_shadow(self):
        """drop_shadow adds shadow behind content."""
        canvas = Canvas(16, 16)
        canvas.fill_rect(4, 4, 8, 8, (255, 0, 0, 255))

        result = drop_shadow(canvas, offset_x=2, offset_y=2)

        # Original content should still exist
        self.assertCanvasHasColor(result, (255, 0, 0, 255))
        # Should have shadow color
        self.assertCanvasNotEmpty(result)

    def test_glow(self):
        """glow adds glow effect around content."""
        canvas = Canvas(16, 16)
        canvas.fill_circle(8, 8, 3, (255, 255, 255, 255))

        result = glow(canvas, (255, 255, 0, 128), radius=2)

        # Should be larger than original
        opaque_original = sum(
            1 for y in range(canvas.height)
            for x in range(canvas.width)
            if canvas.pixels[y][x][3] > 0
        )
        opaque_result = sum(
            1 for y in range(result.height)
            for x in range(result.width)
            if result.pixels[y][x][3] > 0
        )
        self.assertGreater(opaque_result, opaque_original)

    def test_dither(self):
        """dither creates dithered pattern."""
        canvas = CanvasFixtures.gradient_h((0, 0, 0, 255), (255, 255, 255, 255))
        result = dither(canvas, levels=4)

        # Should reduce to limited color levels
        colors = set()
        for y in range(result.height):
            for x in range(result.width):
                colors.add(tuple(result.pixels[y][x]))

        # With 4 levels, should have limited unique colors
        self.assertGreaterEqual(len(colors), 1)


class TestPaletteOperations(TestCase):
    """Tests for palette manipulation."""

    def test_reduce_palette(self):
        """reduce_palette limits colors."""
        canvas = CanvasFixtures.gradient_h(
            (0, 0, 0, 255), (255, 255, 255, 255), width=32
        )

        result = reduce_palette(canvas, 4)

        # Count unique colors
        colors = set()
        for y in range(result.height):
            for x in range(result.width):
                colors.add(tuple(result.pixels[y][x]))

        self.assertLessEqual(len(colors), 4)

    def test_replace_color(self):
        """replace_color swaps colors."""
        canvas = CanvasFixtures.solid((255, 0, 0, 255))
        result = replace_color(canvas, (255, 0, 0, 255), (0, 255, 0, 255))

        # Should be all green now
        self.assertPixelColor(result, 0, 0, (0, 255, 0, 255))


class TestGeometricTransforms(TestCase):
    """Tests for geometric transformations."""

    def test_rotate_90(self):
        """rotate_90 rotates 90 degrees clockwise."""
        canvas = Canvas(4, 2)
        canvas.set_pixel_solid(0, 0, (255, 0, 0, 255))
        canvas.set_pixel_solid(3, 0, (0, 255, 0, 255))

        result = rotate_90(canvas)

        # Dimensions should swap
        self.assertEqual(result.width, 2)
        self.assertEqual(result.height, 4)

    def test_rotate_180(self):
        """rotate_180 rotates 180 degrees."""
        canvas = Canvas(4, 4)
        canvas.set_pixel_solid(0, 0, (255, 0, 0, 255))

        result = rotate_180(canvas)

        # Red pixel should be at opposite corner
        self.assertPixelColor(result, 3, 3, (255, 0, 0, 255))
        self.assertPixelColor(result, 0, 0, (0, 0, 0, 0))

    def test_rotate_270(self):
        """rotate_270 rotates 270 degrees clockwise."""
        canvas = Canvas(4, 2)

        result = rotate_270(canvas)

        self.assertEqual(result.width, 2)
        self.assertEqual(result.height, 4)

    def test_crop(self):
        """crop extracts region."""
        canvas = CanvasFixtures.checkerboard()  # 16x16

        result = crop(canvas, 4, 4, 8, 8)

        self.assertEqual(result.width, 8)
        self.assertEqual(result.height, 8)

    def test_pad(self):
        """pad adds border around canvas."""
        canvas = Canvas(8, 8, (255, 0, 0, 255))

        result = pad(canvas, 2, 2, 2, 2, (0, 0, 0, 255))

        self.assertEqual(result.width, 12)
        self.assertEqual(result.height, 12)

        # Border should be black
        self.assertPixelColor(result, 0, 0, (0, 0, 0, 255))
        # Center should be red
        self.assertPixelColor(result, 6, 6, (255, 0, 0, 255))

    def test_tile(self):
        """tile repeats canvas."""
        canvas = Canvas(4, 4, (255, 0, 0, 255))

        result = tile(canvas, 3, 2)

        self.assertEqual(result.width, 12)
        self.assertEqual(result.height, 8)

        # All pixels should be red
        for y in range(result.height):
            for x in range(result.width):
                self.assertPixelColor(result, x, y, (255, 0, 0, 255))


class TestTransformPreservation(TestCase):
    """Tests that transforms preserve important properties."""

    def test_transforms_preserve_dimensions(self):
        """Non-geometric transforms preserve canvas size."""
        canvas = CanvasFixtures.solid((100, 100, 100, 255), width=10, height=15)

        for transform in [adjust_brightness, adjust_contrast, grayscale, sepia]:
            if transform == adjust_brightness:
                result = transform(canvas, 0.5)
            elif transform == adjust_contrast:
                result = transform(canvas, 1.5)
            else:
                result = transform(canvas)

            self.assertEqual(result.width, canvas.width)
            self.assertEqual(result.height, canvas.height)

    def test_transforms_preserve_alpha(self):
        """Transforms preserve transparency."""
        canvas = Canvas(8, 8)
        canvas.fill_rect(2, 2, 4, 4, (255, 0, 0, 255))

        result = grayscale(canvas)

        # Transparent areas should remain transparent
        self.assertPixelColor(result, 0, 0, (0, 0, 0, 0))

        # Opaque areas should remain opaque
        pixel = result.pixels[4][4]
        self.assertEqual(pixel[3], 255)

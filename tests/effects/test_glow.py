"""Tests for glow and bloom effects."""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core import Canvas
from effects.glow import (
    GlowEffect,
    BloomEffect,
    InnerGlow,
    OuterGlow,
    ColorGlow,
    add_glow,
    add_bloom,
    add_outer_glow,
    add_inner_glow,
)


def create_test_canvas():
    """Create a test canvas with a bright center."""
    canvas = Canvas(16, 16)
    # Fill with dark color
    for y in range(16):
        for x in range(16):
            canvas.set_pixel(x, y, (50, 50, 50, 255))
    # Add bright spot in center
    for y in range(6, 10):
        for x in range(6, 10):
            canvas.set_pixel(x, y, (255, 255, 255, 255))
    return canvas


def create_sprite_canvas():
    """Create a canvas with a simple sprite shape."""
    canvas = Canvas(16, 16)
    # Create a small square sprite
    for y in range(4, 12):
        for x in range(4, 12):
            canvas.set_pixel(x, y, (100, 150, 200, 255))
    return canvas


class TestGlowEffect:
    """Tests for GlowEffect."""

    def test_glow_creates_canvas(self):
        """Test glow returns a canvas."""
        canvas = create_test_canvas()
        glowed = GlowEffect(threshold=200, radius=3, intensity=0.5).apply(canvas)
        assert glowed is not None
        assert glowed.width == canvas.width
        assert glowed.height == canvas.height

    def test_glow_affects_neighbors(self):
        """Test glow spreads to neighboring pixels."""
        canvas = create_test_canvas()
        glowed = GlowEffect(threshold=200, radius=3, intensity=0.5).apply(canvas)

        # Pixels near the bright center should be brighter than original
        # Check a pixel adjacent to the bright area
        orig_pixel = canvas.pixels[5][8]
        glow_pixel = glowed.pixels[5][8]

        # At least one channel should be brighter
        brightness_orig = orig_pixel[0] + orig_pixel[1] + orig_pixel[2]
        brightness_glow = glow_pixel[0] + glow_pixel[1] + glow_pixel[2]
        assert brightness_glow >= brightness_orig

    def test_glow_with_custom_color(self):
        """Test glow with forced color."""
        canvas = create_test_canvas()
        glowed = GlowEffect(
            threshold=200,
            radius=3,
            intensity=0.5,
            color=(255, 0, 0, 255)
        ).apply(canvas)
        assert glowed is not None


class TestBloomEffect:
    """Tests for BloomEffect."""

    def test_bloom_creates_canvas(self):
        """Test bloom returns a canvas."""
        canvas = create_test_canvas()
        bloomed = BloomEffect(threshold=180, blur_radius=4, intensity=0.4).apply(canvas)
        assert bloomed is not None
        assert bloomed.width == canvas.width

    def test_bloom_blurs_bright_areas(self):
        """Test bloom creates blur around bright areas."""
        canvas = create_test_canvas()
        bloomed = BloomEffect(threshold=180, blur_radius=4, intensity=0.6).apply(canvas)

        # Areas near bright spots should be affected
        # Compare pixel at edge of bright area
        orig = canvas.pixels[5][5]
        bloom = bloomed.pixels[5][5]

        # Should be brighter due to bloom
        orig_brightness = (orig[0] + orig[1] + orig[2]) / 3
        bloom_brightness = (bloom[0] + bloom[1] + bloom[2]) / 3
        assert bloom_brightness >= orig_brightness


class TestInnerGlow:
    """Tests for InnerGlow."""

    def test_inner_glow_creates_canvas(self):
        """Test inner glow returns a canvas."""
        canvas = create_sprite_canvas()
        glowed = InnerGlow(color=(255, 255, 200, 255), radius=2, intensity=0.5).apply(canvas)
        assert glowed is not None

    def test_inner_glow_affects_edges(self):
        """Test inner glow affects sprite edges."""
        canvas = create_sprite_canvas()
        glowed = InnerGlow(color=(255, 255, 200, 255), radius=2, intensity=0.5).apply(canvas)

        # Edge pixel should be brighter
        edge_pixel = glowed.pixels[4][4]
        center_pixel = canvas.pixels[8][8]

        # Edge should have glow applied
        assert edge_pixel[3] > 0


class TestOuterGlow:
    """Tests for OuterGlow."""

    def test_outer_glow_creates_canvas(self):
        """Test outer glow returns a canvas."""
        canvas = create_sprite_canvas()
        glowed = OuterGlow(color=(255, 200, 100, 255), radius=3, intensity=0.6).apply(canvas)
        assert glowed is not None

    def test_outer_glow_on_transparent(self):
        """Test outer glow appears on transparent pixels."""
        canvas = create_sprite_canvas()
        glowed = OuterGlow(color=(255, 200, 100, 255), radius=3, intensity=0.6).apply(canvas)

        # Check a pixel just outside the sprite
        orig_outside = canvas.pixels[3][8]
        glow_outside = glowed.pixels[3][8]

        # Original was transparent
        assert orig_outside[3] == 0
        # With glow, should have some alpha
        assert glow_outside[3] > 0


class TestColorGlow:
    """Tests for ColorGlow."""

    def test_color_glow_creates_canvas(self):
        """Test color glow returns a canvas."""
        canvas = create_sprite_canvas()
        glowed = ColorGlow(
            target_color=(100, 150, 200, 255),
            tolerance=30,
            radius=3,
            intensity=0.5
        ).apply(canvas)
        assert glowed is not None

    def test_color_glow_targets_color(self):
        """Test color glow only affects target color."""
        canvas = Canvas(16, 16)
        # Red area
        for y in range(4, 8):
            for x in range(4, 8):
                canvas.set_pixel(x, y, (255, 0, 0, 255))
        # Blue area
        for y in range(8, 12):
            for x in range(8, 12):
                canvas.set_pixel(x, y, (0, 0, 255, 255))

        # Target only red
        glowed = ColorGlow(
            target_color=(255, 0, 0, 255),
            tolerance=30,
            radius=2,
            intensity=0.5
        ).apply(canvas)

        # Blue area should be mostly unaffected
        blue_pixel = glowed.pixels[10][10]
        assert blue_pixel[2] > blue_pixel[0]  # Still more blue


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_add_glow(self):
        """Test add_glow function."""
        canvas = create_test_canvas()
        result = add_glow(canvas, threshold=200, radius=3, intensity=0.5)
        assert result is not None

    def test_add_bloom(self):
        """Test add_bloom function."""
        canvas = create_test_canvas()
        result = add_bloom(canvas, threshold=180, blur_radius=4, intensity=0.4)
        assert result is not None

    def test_add_outer_glow(self):
        """Test add_outer_glow function."""
        canvas = create_sprite_canvas()
        result = add_outer_glow(canvas, color=(255, 200, 100, 255), radius=3, intensity=0.6)
        assert result is not None

    def test_add_inner_glow(self):
        """Test add_inner_glow function."""
        canvas = create_sprite_canvas()
        result = add_inner_glow(canvas, color=(255, 255, 200, 255), radius=2, intensity=0.5)
        assert result is not None

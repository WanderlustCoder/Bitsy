"""Tests for image tracing."""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core import Canvas
from core.palette import Palette
from import_.tracer import (
    TraceConfig,
    ImageTracer,
    trace_image,
    trace_to_palette,
    auto_pixelate,
    downsample,
)


def create_high_res_image():
    """Create a high-resolution test image."""
    canvas = Canvas(128, 128)

    # Create a gradient pattern
    for y in range(128):
        for x in range(128):
            r = int(x * 255 / 127)
            g = int(y * 255 / 127)
            b = int((x + y) * 127 / 254)
            canvas.set_pixel(x, y, (r, g, b, 255))

    return canvas


def create_image_with_edges():
    """Create an image with distinct edges."""
    canvas = Canvas(64, 64)

    # White background
    canvas.clear((255, 255, 255, 255))

    # Black square in center
    for y in range(20, 44):
        for x in range(20, 44):
            canvas.set_pixel(x, y, (0, 0, 0, 255))

    return canvas


def create_colorful_image():
    """Create an image with multiple colors."""
    canvas = Canvas(64, 64)

    # Quadrants with different colors
    for y in range(64):
        for x in range(64):
            if x < 32 and y < 32:
                color = (255, 0, 0, 255)  # Red
            elif x >= 32 and y < 32:
                color = (0, 255, 0, 255)  # Green
            elif x < 32 and y >= 32:
                color = (0, 0, 255, 255)  # Blue
            else:
                color = (255, 255, 0, 255)  # Yellow
            canvas.set_pixel(x, y, color)

    return canvas


class TestTraceConfig:
    """Tests for TraceConfig."""

    def test_default_config(self):
        """Test default configuration values."""
        config = TraceConfig()
        assert config.target_width == 32
        assert config.target_height is None
        assert config.color_count == 16
        assert config.outline is True

    def test_custom_config(self):
        """Test custom configuration."""
        config = TraceConfig(
            target_width=64,
            target_height=48,
            color_count=8,
            outline=False
        )
        assert config.target_width == 64
        assert config.target_height == 48
        assert config.color_count == 8
        assert config.outline is False


class TestImageTracer:
    """Tests for ImageTracer."""

    def test_trace_basic(self):
        """Test basic image tracing."""
        source = create_high_res_image()
        tracer = ImageTracer(TraceConfig(target_width=16))
        result = tracer.trace(source)

        assert result.width == 16
        # Height should be auto-calculated
        assert result.height > 0

    def test_trace_with_target_height(self):
        """Test tracing with specific target height."""
        source = create_high_res_image()
        tracer = ImageTracer(TraceConfig(target_width=32, target_height=24))
        result = tracer.trace(source)

        assert result.width == 32
        assert result.height == 24

    def test_trace_color_reduction(self):
        """Test that tracing reduces colors."""
        source = create_high_res_image()
        tracer = ImageTracer(TraceConfig(target_width=32, color_count=8))
        result = tracer.trace(source)

        # Count unique colors
        colors = set()
        for y in range(result.height):
            for x in range(result.width):
                colors.add(result.get_pixel(x, y))

        # Should have at most 8 colors (plus possibly transparent)
        assert len(colors) <= 9

    def test_trace_with_outline(self):
        """Test tracing with outlines."""
        source = create_image_with_edges()
        tracer = ImageTracer(TraceConfig(
            target_width=16,
            outline=True,
            outline_threshold=0.3
        ))
        result = tracer.trace(source)

        assert result is not None

    def test_trace_without_outline(self):
        """Test tracing without outlines."""
        source = create_image_with_edges()
        tracer = ImageTracer(TraceConfig(target_width=16, outline=False))
        result = tracer.trace(source)

        assert result is not None

    def test_trace_with_palette(self):
        """Test tracing with specific palette."""
        source = create_colorful_image()
        palette = Palette([
            (255, 0, 0, 255),
            (0, 255, 0, 255),
            (0, 0, 255, 255),
            (255, 255, 0, 255),
        ], "RGBY")

        tracer = ImageTracer(TraceConfig(target_width=16))
        result = tracer.trace_with_palette(source, palette)

        # All pixels should be from palette
        for y in range(result.height):
            for x in range(result.width):
                color = result.get_pixel(x, y)
                if color[3] > 0:  # Not transparent
                    assert color in palette.colors or color == (0, 0, 0, 255)  # outline

    def test_downsample_smooth(self):
        """Test smooth downsampling."""
        source = create_high_res_image()
        tracer = ImageTracer(TraceConfig(target_width=16, smooth=True))
        result = tracer._downsample(source, 16, 16)

        assert result.width == 16
        assert result.height == 16

    def test_downsample_nearest(self):
        """Test nearest neighbor downsampling."""
        source = create_high_res_image()
        tracer = ImageTracer(TraceConfig(target_width=16, smooth=False))
        result = tracer._downsample(source, 16, 16)

        assert result.width == 16
        assert result.height == 16

    def test_edge_detection(self):
        """Test edge detection."""
        source = create_image_with_edges()
        tracer = ImageTracer()
        edges = tracer._detect_edges(source)

        assert edges.width == source.width
        assert edges.height == source.height

        # Edge pixels should have higher values
        # Check center area (inside black square) vs edge
        center = edges.get_pixel(32, 32)[0]
        edge = edges.get_pixel(20, 32)[0]
        assert edge >= center  # Edge should be brighter or equal

    def test_contrast_adjustment(self):
        """Test contrast adjustment."""
        source = create_high_res_image()
        tracer = ImageTracer()

        # Increase contrast
        high = tracer._adjust_contrast(source, 1.5)
        assert high is not None

        # Decrease contrast
        low = tracer._adjust_contrast(source, 0.5)
        assert low is not None

    def test_saturation_adjustment(self):
        """Test saturation adjustment."""
        source = create_colorful_image()
        tracer = ImageTracer()

        # Increase saturation
        high = tracer._adjust_saturation(source, 1.5)
        assert high is not None

        # Decrease saturation (toward grayscale)
        low = tracer._adjust_saturation(source, 0.5)
        assert low is not None


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_trace_image(self):
        """Test trace_image function."""
        source = create_high_res_image()
        result = trace_image(source, width=32, colors=16)

        assert result.width == 32

    def test_trace_image_options(self):
        """Test trace_image with options."""
        source = create_high_res_image()
        result = trace_image(source, width=24, colors=8, outline=False)

        assert result.width == 24

    def test_trace_to_palette(self):
        """Test trace_to_palette function."""
        source = create_colorful_image()
        palette = Palette([
            (255, 0, 0, 255),
            (0, 128, 0, 255),
        ], "Test")

        result = trace_to_palette(source, palette, width=16)
        assert result.width == 16

    def test_auto_pixelate(self):
        """Test auto_pixelate function."""
        source = create_high_res_image()
        result = auto_pixelate(source, target_size=32)

        assert result.width == 32
        # Should preserve more colors (no quantization)

    def test_downsample_function(self):
        """Test downsample function."""
        source = create_high_res_image()
        result = downsample(source, width=32)

        assert result.width == 32
        # Height should be auto-calculated
        assert result.height == 32  # Square source

    def test_downsample_with_height(self):
        """Test downsample with specific height."""
        source = create_high_res_image()
        result = downsample(source, width=32, height=16)

        assert result.width == 32
        assert result.height == 16


class TestEdgeCases:
    """Tests for edge cases."""

    def test_small_source(self):
        """Test tracing a small source image."""
        source = Canvas(8, 8)
        source.clear((255, 0, 0, 255))

        result = trace_image(source, width=16, colors=4)
        assert result.width == 16

    def test_single_color(self):
        """Test tracing single color image."""
        source = Canvas(64, 64)
        source.clear((100, 150, 200, 255))

        result = trace_image(source, width=16, colors=4)
        assert result.width == 16

    def test_transparent_image(self):
        """Test tracing image with transparency."""
        source = Canvas(64, 64)
        source.clear((0, 0, 0, 0))

        # Add some content
        for y in range(20, 44):
            for x in range(20, 44):
                source.set_pixel(x, y, (255, 0, 0, 255))

        result = trace_image(source, width=16, colors=4)
        assert result is not None

    def test_very_small_target(self):
        """Test tracing to very small target."""
        source = create_high_res_image()
        result = trace_image(source, width=4, colors=4)

        assert result.width == 4
        assert result.height == 4

    def test_non_square_aspect_ratio(self):
        """Test tracing non-square image."""
        source = Canvas(128, 64)
        for y in range(64):
            for x in range(128):
                r = int(x * 255 / 127)
                g = int(y * 255 / 63)
                source.set_pixel(x, y, (r, g, 128, 255))

        result = trace_image(source, width=32, colors=8)
        assert result.width == 32
        assert result.height == 16  # Half of width (2:1 ratio)

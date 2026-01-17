"""Tests for color quantization."""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core import Canvas
from core.palette import Palette
from import_.quantize import (
    QuantizeMethod,
    QuantizeConfig,
    ColorQuantizer,
    ColorBox,
    Octree,
    quantize_image,
    extract_palette,
    median_cut,
    octree_quantize,
)


def create_gradient_canvas():
    """Create a canvas with color gradient."""
    canvas = Canvas(16, 16)
    for y in range(16):
        for x in range(16):
            r = int(x * 255 / 15)
            g = int(y * 255 / 15)
            b = 128
            canvas.set_pixel(x, y, (r, g, b, 255))
    return canvas


def create_simple_canvas():
    """Create a canvas with a few distinct colors."""
    canvas = Canvas(8, 8)
    colors = [
        (255, 0, 0, 255),    # Red
        (0, 255, 0, 255),    # Green
        (0, 0, 255, 255),    # Blue
        (255, 255, 0, 255),  # Yellow
    ]
    for y in range(8):
        for x in range(8):
            color_idx = (y // 4) * 2 + (x // 4)
            canvas.set_pixel(x, y, colors[color_idx])
    return canvas


class TestColorBox:
    """Tests for ColorBox."""

    def test_color_box_init(self):
        """Test ColorBox initialization."""
        colors = [
            ((100, 50, 25, 255), 10),
            ((200, 150, 125, 255), 20),
        ]
        box = ColorBox(colors)
        assert box.min_r == 100
        assert box.max_r == 200
        assert box.pixel_count == 30

    def test_longest_axis(self):
        """Test finding longest axis."""
        colors = [
            ((0, 0, 0, 255), 1),
            ((255, 100, 50, 255), 1),
        ]
        box = ColorBox(colors)
        assert box.longest_axis == 0  # Red has widest range

    def test_average_color(self):
        """Test average color calculation."""
        colors = [
            ((100, 100, 100, 255), 1),
            ((200, 200, 200, 255), 1),
        ]
        box = ColorBox(colors)
        avg = box.average_color()
        assert avg[0] == 150
        assert avg[1] == 150
        assert avg[2] == 150

    def test_split(self):
        """Test box splitting."""
        colors = [
            ((0, 0, 0, 255), 1),
            ((100, 0, 0, 255), 1),
            ((200, 0, 0, 255), 1),
            ((255, 0, 0, 255), 1),
        ]
        box = ColorBox(colors)
        box1, box2 = box.split()
        assert len(box1.colors) > 0
        assert len(box2.colors) > 0


class TestOctree:
    """Tests for Octree quantization."""

    def test_octree_add_color(self):
        """Test adding colors to octree."""
        tree = Octree(max_colors=4)
        tree.add_color((255, 0, 0, 255))
        tree.add_color((0, 255, 0, 255))
        tree.add_color((0, 0, 255, 255))

        leaves = tree.root.get_leaves()
        assert len(leaves) == 3

    def test_octree_reduce(self):
        """Test octree reduction."""
        tree = Octree(max_colors=2)

        for i in range(256):
            tree.add_color((i, 0, 0, 255))

        tree.reduce()
        palette = tree.get_palette()
        assert len(palette) <= 2


class TestColorQuantizer:
    """Tests for ColorQuantizer."""

    def test_quantizer_median_cut(self):
        """Test median cut quantization."""
        canvas = create_gradient_canvas()
        config = QuantizeConfig(
            method=QuantizeMethod.MEDIAN_CUT,
            color_count=8
        )
        quantizer = ColorQuantizer(config)
        result, palette = quantizer.quantize(canvas)

        assert result.width == canvas.width
        assert result.height == canvas.height
        assert len(palette.colors) <= 8

    def test_quantizer_octree(self):
        """Test octree quantization."""
        canvas = create_gradient_canvas()
        config = QuantizeConfig(
            method=QuantizeMethod.OCTREE,
            color_count=8
        )
        quantizer = ColorQuantizer(config)
        result, palette = quantizer.quantize(canvas)

        assert result is not None
        assert palette is not None

    def test_quantizer_kmeans(self):
        """Test k-means quantization."""
        canvas = create_simple_canvas()
        config = QuantizeConfig(
            method=QuantizeMethod.KMEANS,
            color_count=4
        )
        quantizer = ColorQuantizer(config)
        result, palette = quantizer.quantize(canvas)

        assert result is not None
        assert len(palette.colors) <= 4

    def test_quantizer_popularity(self):
        """Test popularity-based quantization."""
        canvas = create_simple_canvas()
        config = QuantizeConfig(
            method=QuantizeMethod.POPULARITY,
            color_count=4
        )
        quantizer = ColorQuantizer(config)
        result, palette = quantizer.quantize(canvas)

        assert result is not None
        # Should get exactly the 4 colors used
        assert len(palette.colors) == 4

    def test_preserve_exact_colors(self):
        """Test preserving specific colors."""
        canvas = create_gradient_canvas()
        preserve = [(255, 0, 0, 255), (0, 255, 0, 255)]
        config = QuantizeConfig(
            method=QuantizeMethod.MEDIAN_CUT,
            color_count=8,
            preserve_exact=preserve
        )
        quantizer = ColorQuantizer(config)
        _, palette = quantizer.quantize(canvas)

        # Preserved colors should be in palette
        for color in preserve:
            assert color in palette.colors

    def test_transparent_handling(self):
        """Test handling of transparent pixels."""
        canvas = Canvas(8, 8)
        for y in range(8):
            for x in range(8):
                if x < 4:
                    canvas.set_pixel(x, y, (255, 0, 0, 255))
                else:
                    canvas.set_pixel(x, y, (0, 0, 0, 0))  # Transparent

        config = QuantizeConfig(color_count=4)
        quantizer = ColorQuantizer(config)
        result, _ = quantizer.quantize(canvas)

        # Transparent pixels should remain transparent
        assert result.get_pixel(6, 0)[3] == 0


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_quantize_image(self):
        """Test quantize_image function."""
        canvas = create_gradient_canvas()
        result, palette = quantize_image(canvas, colors=8, method="median_cut")

        assert result is not None
        assert len(palette.colors) <= 8

    def test_quantize_image_methods(self):
        """Test all quantization methods via convenience function."""
        canvas = create_simple_canvas()

        for method in ["median_cut", "octree", "kmeans", "popularity"]:
            result, palette = quantize_image(canvas, colors=4, method=method)
            assert result is not None
            assert palette is not None

    def test_extract_palette(self):
        """Test extract_palette function."""
        canvas = create_simple_canvas()
        palette = extract_palette(canvas, colors=4)

        assert palette is not None
        assert len(palette.colors) <= 4

    def test_median_cut_function(self):
        """Test median_cut convenience function."""
        colors = [
            (255, 0, 0, 255),
            (0, 255, 0, 255),
            (0, 0, 255, 255),
            (128, 128, 128, 255),
        ]
        result = median_cut(colors, 2)
        assert len(result) <= 2

    def test_octree_quantize_function(self):
        """Test octree_quantize convenience function."""
        colors = [
            (255, 0, 0, 255),
            (0, 255, 0, 255),
            (0, 0, 255, 255),
            (128, 128, 128, 255),
        ]
        result = octree_quantize(colors, 2)
        assert len(result) <= 2


class TestEdgeCases:
    """Tests for edge cases."""

    def test_empty_canvas(self):
        """Test quantization of empty canvas."""
        canvas = Canvas(4, 4)
        result, palette = quantize_image(canvas, colors=4)
        assert result is not None

    def test_single_color(self):
        """Test quantization with single color."""
        canvas = Canvas(4, 4)
        canvas.clear((128, 64, 32, 255))
        result, palette = quantize_image(canvas, colors=4)

        assert len(palette.colors) >= 1

    def test_more_colors_than_pixels(self):
        """Test requesting more colors than unique pixels."""
        canvas = Canvas(2, 2)
        canvas.set_pixel(0, 0, (255, 0, 0, 255))
        canvas.set_pixel(1, 0, (0, 255, 0, 255))
        canvas.set_pixel(0, 1, (0, 0, 255, 255))
        canvas.set_pixel(1, 1, (255, 255, 0, 255))

        result, palette = quantize_image(canvas, colors=16)
        # Should get at most 4 colors (the unique colors)
        assert len(palette.colors) <= 4

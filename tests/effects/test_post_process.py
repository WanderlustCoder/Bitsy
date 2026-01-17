"""Tests for post-processing effects."""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core import Canvas
from effects.post_process import (
    GaussianBlur,
    BoxBlur,
    Sharpen,
    Emboss,
    EdgeDetect,
    Pixelate,
    Posterize,
    Dither,
    DitherMethod,
    Invert,
    Grayscale,
    Sepia,
    PostProcessor,
    ConvolutionKernel,
    blur,
    sharpen,
    pixelate,
    posterize,
    grayscale,
    sepia,
    invert,
    emboss,
    detect_edges,
)


def create_test_canvas(fill_color=(100, 150, 200, 255)):
    """Create a test canvas with solid color."""
    canvas = Canvas(16, 16)
    for y in range(16):
        for x in range(16):
            canvas.set_pixel(x, y, fill_color)
    return canvas


def create_gradient_canvas():
    """Create a canvas with gradient."""
    canvas = Canvas(16, 16)
    for y in range(16):
        for x in range(16):
            v = int(x * 255 / 15)
            canvas.set_pixel(x, y, (v, v, v, 255))
    return canvas


class TestConvolutionKernel:
    """Tests for ConvolutionKernel."""

    def test_identity_kernel(self):
        """Test identity kernel produces unchanged output."""
        kernel = ConvolutionKernel([[0, 0, 0], [0, 1, 0], [0, 0, 0]], normalize=False)
        canvas = create_test_canvas()
        result = kernel.apply(canvas)

        # Check center pixels are unchanged
        orig = canvas.pixels[8][8]
        new = result.pixels[8][8]
        assert orig[0] == new[0]
        assert orig[1] == new[1]
        assert orig[2] == new[2]

    def test_kernel_normalization(self):
        """Test kernel normalization."""
        kernel = ConvolutionKernel([[1, 1, 1], [1, 1, 1], [1, 1, 1]], normalize=True)
        total = sum(sum(row) for row in kernel.matrix)
        assert abs(total - 1.0) < 0.001


class TestGaussianBlur:
    """Tests for Gaussian blur."""

    def test_blur_creates_canvas(self):
        """Test blur returns a canvas."""
        canvas = create_test_canvas()
        blurred = GaussianBlur(radius=2).process(canvas)
        assert blurred is not None
        assert blurred.width == canvas.width
        assert blurred.height == canvas.height

    def test_blur_smooths_gradient(self):
        """Test blur smooths a gradient."""
        canvas = create_gradient_canvas()
        blurred = GaussianBlur(radius=2).process(canvas)

        # Blurred gradient should have less extreme values at edges
        assert blurred.pixels[8][0][0] > canvas.pixels[8][0][0]
        assert blurred.pixels[8][15][0] < canvas.pixels[8][15][0]

    def test_convenience_blur(self):
        """Test convenience blur function."""
        canvas = create_test_canvas()
        result = blur(canvas, radius=2)
        assert result is not None


class TestBoxBlur:
    """Tests for box blur."""

    def test_box_blur_creates_canvas(self):
        """Test box blur returns a canvas."""
        canvas = create_test_canvas()
        blurred = BoxBlur(radius=2).process(canvas)
        assert blurred is not None

    def test_box_blur_uniform_color(self):
        """Test box blur on uniform color stays similar."""
        canvas = create_test_canvas((100, 100, 100, 255))
        blurred = BoxBlur(radius=1).process(canvas)

        # Center should be nearly unchanged
        pixel = blurred.pixels[8][8]
        assert abs(pixel[0] - 100) < 5


class TestSharpen:
    """Tests for sharpening."""

    def test_sharpen_creates_canvas(self):
        """Test sharpen returns a canvas."""
        canvas = create_test_canvas()
        sharpened = Sharpen(amount=1.0).process(canvas)
        assert sharpened is not None

    def test_convenience_sharpen(self):
        """Test convenience sharpen function."""
        canvas = create_test_canvas()
        result = sharpen(canvas, amount=1.0)
        assert result is not None


class TestEmboss:
    """Tests for emboss effect."""

    def test_emboss_creates_canvas(self):
        """Test emboss returns a canvas."""
        canvas = create_test_canvas()
        embossed = Emboss(direction="top-left").process(canvas)
        assert embossed is not None

    def test_emboss_directions(self):
        """Test different emboss directions."""
        canvas = create_gradient_canvas()
        for direction in ["top-left", "top", "top-right", "left", "right", "bottom-left", "bottom", "bottom-right"]:
            result = Emboss(direction=direction).process(canvas)
            assert result is not None

    def test_convenience_emboss(self):
        """Test convenience emboss function."""
        canvas = create_test_canvas()
        result = emboss(canvas)
        assert result is not None


class TestEdgeDetect:
    """Tests for edge detection."""

    def test_edge_detect_creates_canvas(self):
        """Test edge detection returns a canvas."""
        canvas = create_gradient_canvas()
        edges = EdgeDetect(method="sobel").process(canvas)
        assert edges is not None

    def test_edge_detect_methods(self):
        """Test different edge detection methods."""
        canvas = create_gradient_canvas()
        for method in ["sobel", "prewitt", "laplacian"]:
            result = EdgeDetect(method=method).process(canvas)
            assert result is not None

    def test_convenience_detect_edges(self):
        """Test convenience detect_edges function."""
        canvas = create_gradient_canvas()
        result = detect_edges(canvas)
        assert result is not None


class TestPixelate:
    """Tests for pixelation."""

    def test_pixelate_creates_canvas(self):
        """Test pixelate returns a canvas."""
        canvas = create_gradient_canvas()
        pixelated = Pixelate(block_size=4).process(canvas)
        assert pixelated is not None

    def test_pixelate_block_size(self):
        """Test pixelation creates blocks."""
        canvas = create_gradient_canvas()
        pixelated = Pixelate(block_size=4).process(canvas)

        # Pixels within same block should be equal
        assert pixelated.pixels[0][0] == pixelated.pixels[0][1]
        assert pixelated.pixels[0][0] == pixelated.pixels[1][0]

    def test_convenience_pixelate(self):
        """Test convenience pixelate function."""
        canvas = create_gradient_canvas()
        result = pixelate(canvas, block_size=4)
        assert result is not None


class TestPosterize:
    """Tests for posterization."""

    def test_posterize_creates_canvas(self):
        """Test posterize returns a canvas."""
        canvas = create_gradient_canvas()
        posterized = Posterize(levels=4).process(canvas)
        assert posterized is not None

    def test_posterize_reduces_colors(self):
        """Test posterize reduces color levels."""
        canvas = create_gradient_canvas()
        posterized = Posterize(levels=4).process(canvas)

        # Count unique colors
        colors = set()
        for y in range(canvas.height):
            for x in range(canvas.width):
                pixel = posterized.pixels[y][x]
                if pixel[3] > 0:
                    colors.add((pixel[0], pixel[1], pixel[2]))

        # Should have fewer colors
        assert len(colors) <= 16  # At most 4 levels per channel

    def test_convenience_posterize(self):
        """Test convenience posterize function."""
        canvas = create_gradient_canvas()
        result = posterize(canvas, levels=4)
        assert result is not None


class TestDither:
    """Tests for dithering."""

    def test_ordered_dither(self):
        """Test ordered dithering."""
        canvas = create_gradient_canvas()
        palette = [(0, 0, 0, 255), (128, 128, 128, 255), (255, 255, 255, 255)]
        dithered = Dither(palette, DitherMethod.ORDERED).process(canvas)
        assert dithered is not None

    def test_floyd_steinberg_dither(self):
        """Test Floyd-Steinberg dithering."""
        canvas = create_gradient_canvas()
        palette = [(0, 0, 0, 255), (128, 128, 128, 255), (255, 255, 255, 255)]
        dithered = Dither(palette, DitherMethod.FLOYD_STEINBERG).process(canvas)
        assert dithered is not None


class TestInvert:
    """Tests for color inversion."""

    def test_invert_creates_canvas(self):
        """Test invert returns a canvas."""
        canvas = create_test_canvas()
        inverted = Invert().process(canvas)
        assert inverted is not None

    def test_invert_values(self):
        """Test invert produces correct values."""
        canvas = create_test_canvas((100, 150, 200, 255))
        inverted = Invert().process(canvas)

        pixel = inverted.pixels[8][8]
        assert pixel[0] == 155  # 255 - 100
        assert pixel[1] == 105  # 255 - 150
        assert pixel[2] == 55   # 255 - 200

    def test_convenience_invert(self):
        """Test convenience invert function."""
        canvas = create_test_canvas()
        result = invert(canvas)
        assert result is not None


class TestGrayscale:
    """Tests for grayscale conversion."""

    def test_grayscale_creates_canvas(self):
        """Test grayscale returns a canvas."""
        canvas = create_test_canvas()
        gray = Grayscale().process(canvas)
        assert gray is not None

    def test_grayscale_produces_gray(self):
        """Test grayscale produces gray values."""
        canvas = create_test_canvas()
        gray = Grayscale().process(canvas)

        pixel = gray.pixels[8][8]
        # All channels should be equal in grayscale
        assert pixel[0] == pixel[1] == pixel[2]

    def test_grayscale_methods(self):
        """Test different grayscale methods."""
        canvas = create_test_canvas()
        for method in ["luminosity", "average", "lightness"]:
            result = Grayscale(method=method).process(canvas)
            assert result is not None

    def test_convenience_grayscale(self):
        """Test convenience grayscale function."""
        canvas = create_test_canvas()
        result = grayscale(canvas)
        assert result is not None


class TestSepia:
    """Tests for sepia effect."""

    def test_sepia_creates_canvas(self):
        """Test sepia returns a canvas."""
        canvas = create_test_canvas()
        sep = Sepia().process(canvas)
        assert sep is not None

    def test_sepia_warmth(self):
        """Test sepia adds warmth."""
        canvas = create_test_canvas((100, 100, 100, 255))
        sep = Sepia(intensity=1.0).process(canvas)

        pixel = sep.pixels[8][8]
        # Red should be higher than blue in sepia
        assert pixel[0] > pixel[2]

    def test_convenience_sepia(self):
        """Test convenience sepia function."""
        canvas = create_test_canvas()
        result = sepia(canvas)
        assert result is not None


class TestPostProcessor:
    """Tests for PostProcessor manager."""

    def test_empty_processor(self):
        """Test empty processor returns unchanged canvas."""
        processor = PostProcessor()
        canvas = create_test_canvas()
        result = processor.process(canvas)

        # Should be same as input
        assert result.pixels[8][8][0] == canvas.pixels[8][8][0]

    def test_chained_effects(self):
        """Test chaining multiple effects."""
        processor = PostProcessor()
        processor.add(Grayscale()).add(Posterize(levels=4))

        canvas = create_gradient_canvas()
        result = processor.process(canvas)

        # Should be grayscale and posterized
        pixel = result.pixels[8][8]
        assert pixel[0] == pixel[1] == pixel[2]

    def test_clear_effects(self):
        """Test clearing effects."""
        processor = PostProcessor()
        processor.add(Grayscale())
        processor.clear()

        assert len(processor.effects) == 0

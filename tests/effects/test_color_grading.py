"""Tests for color grading and LUTs."""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core import Canvas
from effects.color_grading import (
    LUT,
    ColorGrader,
    create_warm_grade,
    create_cool_grade,
    create_vintage_grade,
    create_cyberpunk_grade,
    create_noir_grade,
    create_golden_hour_grade,
    apply_color_grade,
    adjust_levels,
    adjust_temperature,
    list_color_grades,
)


def create_test_canvas():
    """Create a test canvas with varied colors."""
    canvas = Canvas(16, 16)
    for y in range(16):
        for x in range(16):
            r = int(x * 255 / 15)
            g = int(y * 255 / 15)
            b = int((x + y) * 127 / 15)
            canvas.set_pixel(x, y, (r, g, b, 255))
    return canvas


def create_gray_canvas():
    """Create a grayscale gradient canvas."""
    canvas = Canvas(16, 16)
    for y in range(16):
        for x in range(16):
            v = int(x * 255 / 15)
            canvas.set_pixel(x, y, (v, v, v, 255))
    return canvas


class TestLUT:
    """Tests for LUT (Lookup Table)."""

    def test_identity_lut(self):
        """Test identity LUT produces unchanged colors."""
        lut = LUT.identity(size=16)
        color = (100, 150, 200, 255)
        result = lut.lookup(color)

        # Should be very close to original
        assert abs(result[0] - color[0]) <= 2
        assert abs(result[1] - color[1]) <= 2
        assert abs(result[2] - color[2]) <= 2

    def test_lut_from_function(self):
        """Test creating LUT from function."""
        def invert(color):
            return (255 - color[0], 255 - color[1], 255 - color[2], color[3])

        lut = LUT.from_function(invert, size=16)

        # Check inversion works
        result = lut.lookup((0, 0, 0, 255))
        assert result[0] > 200
        assert result[1] > 200
        assert result[2] > 200

    def test_lut_interpolation(self):
        """Test LUT interpolation."""
        lut = LUT.identity(size=16)
        color = (100, 150, 200, 255)

        # Interpolated should be smoother
        result = lut.lookup_interpolated(color)
        assert result is not None
        assert result[3] == color[3]

    def test_lut_size(self):
        """Test different LUT sizes."""
        for size in [8, 16, 32]:
            lut = LUT.identity(size=size)
            assert lut.size == size
            assert len(lut.data) == size


class TestColorGrader:
    """Tests for ColorGrader."""

    def test_apply_lut(self):
        """Test applying LUT to canvas."""
        grader = ColorGrader()
        canvas = create_test_canvas()
        lut = LUT.identity()

        result = grader.apply_lut(canvas, lut)
        assert result is not None
        assert result.width == canvas.width

    def test_adjust_levels(self):
        """Test levels adjustment."""
        grader = ColorGrader()
        canvas = create_gray_canvas()

        # Lift shadows
        result = grader.adjust_levels(canvas, shadows=0.1, midtones=1.0, highlights=1.0)
        assert result is not None

        # Check black level is lifted
        black_pixel = result.pixels[0][0]
        assert black_pixel[0] > 0

    def test_adjust_curves(self):
        """Test curves adjustment."""
        grader = ColorGrader()
        canvas = create_gray_canvas()

        # S-curve for contrast
        curve = [(0, 0), (0.25, 0.15), (0.75, 0.85), (1, 1)]
        result = grader.adjust_curves(canvas, master_curve=curve)
        assert result is not None

    def test_color_balance(self):
        """Test color balance adjustment."""
        grader = ColorGrader()
        canvas = create_test_canvas()

        # Shift shadows toward blue
        result = grader.color_balance(
            canvas,
            shadows_shift=(0, 0, 30),
            midtones_shift=(0, 0, 0),
            highlights_shift=(0, 0, 0)
        )
        assert result is not None

    def test_hue_saturation(self):
        """Test hue/saturation adjustment."""
        grader = ColorGrader()
        canvas = create_test_canvas()

        # Rotate hue
        result = grader.hue_saturation(canvas, hue_shift=90, saturation=1.0)
        assert result is not None

    def test_temperature_tint(self):
        """Test temperature/tint adjustment."""
        grader = ColorGrader()
        canvas = create_test_canvas()

        # Warm up the image
        result = grader.temperature_tint(canvas, temperature=50, tint=0)
        assert result is not None


class TestPresetGrades:
    """Tests for preset color grades."""

    def test_warm_grade(self):
        """Test warm color grade."""
        lut = create_warm_grade()
        assert lut is not None
        assert lut.size == 16

    def test_cool_grade(self):
        """Test cool color grade."""
        lut = create_cool_grade()
        assert lut is not None

    def test_vintage_grade(self):
        """Test vintage color grade."""
        lut = create_vintage_grade()
        assert lut is not None

    def test_cyberpunk_grade(self):
        """Test cyberpunk color grade."""
        lut = create_cyberpunk_grade()
        assert lut is not None

    def test_noir_grade(self):
        """Test noir color grade."""
        lut = create_noir_grade()
        assert lut is not None

        # Noir should convert to grayscale
        color = (100, 150, 200, 255)
        result = lut.lookup(color)
        # Should be grayscale (all channels similar)
        assert abs(result[0] - result[1]) < 5
        assert abs(result[1] - result[2]) < 5

    def test_golden_hour_grade(self):
        """Test golden hour color grade."""
        lut = create_golden_hour_grade()
        assert lut is not None


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_apply_color_grade(self):
        """Test apply_color_grade function."""
        canvas = create_test_canvas()

        for preset in list_color_grades():
            result = apply_color_grade(canvas, preset)
            assert result is not None
            assert result.width == canvas.width

    def test_adjust_levels_function(self):
        """Test adjust_levels function."""
        canvas = create_gray_canvas()
        result = adjust_levels(canvas, shadows=0.1, midtones=1.2)
        assert result is not None

    def test_adjust_temperature_function(self):
        """Test adjust_temperature function."""
        canvas = create_test_canvas()
        result = adjust_temperature(canvas, temperature=50)
        assert result is not None

    def test_list_color_grades(self):
        """Test list_color_grades function."""
        grades = list_color_grades()
        assert len(grades) > 0
        assert "warm" in grades
        assert "cool" in grades
        assert "vintage" in grades

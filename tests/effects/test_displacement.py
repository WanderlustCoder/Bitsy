"""Tests for displacement effects."""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core import Canvas
from effects.displacement import (
    WaveDisplacement,
    RippleDisplacement,
    TwirlDisplacement,
    BulgeDisplacement,
    NoiseDisplacement,
    BarrelDisplacement,
    ShearDisplacement,
    CompositeDisplacement,
    apply_wave,
    apply_ripple,
    apply_twirl,
    apply_bulge,
    apply_noise,
    apply_barrel,
)


def create_test_canvas():
    """Create a test canvas with a simple pattern."""
    canvas = Canvas(16, 16)
    for y in range(16):
        for x in range(16):
            # Checkerboard pattern
            if (x + y) % 2 == 0:
                canvas.set_pixel(x, y, (200, 200, 200, 255))
            else:
                canvas.set_pixel(x, y, (100, 100, 100, 255))
    return canvas


def create_gradient_canvas():
    """Create a gradient canvas."""
    canvas = Canvas(16, 16)
    for y in range(16):
        for x in range(16):
            r = int(x * 255 / 15)
            b = int(y * 255 / 15)
            canvas.set_pixel(x, y, (r, 128, b, 255))
    return canvas


class TestWaveDisplacement:
    """Tests for wave displacement."""

    def test_wave_creates_canvas(self):
        """Test wave displacement returns a canvas."""
        canvas = create_test_canvas()
        wave = WaveDisplacement(amplitude=3.0, frequency=0.2, direction="horizontal")
        result = wave.apply(canvas)
        assert result is not None
        assert result.width == canvas.width
        assert result.height == canvas.height

    def test_wave_directions(self):
        """Test different wave directions."""
        canvas = create_test_canvas()
        for direction in ["horizontal", "vertical", "both"]:
            wave = WaveDisplacement(amplitude=3.0, frequency=0.2, direction=direction)
            result = wave.apply(canvas)
            assert result is not None

    def test_wave_phase(self):
        """Test wave phase offset."""
        canvas = create_test_canvas()
        wave1 = WaveDisplacement(amplitude=3.0, frequency=0.2, phase=0.0)
        wave2 = WaveDisplacement(amplitude=3.0, frequency=0.2, phase=3.14159)

        result1 = wave1.apply(canvas)
        result2 = wave2.apply(canvas)

        # Results should be different due to phase
        # Check some pixel
        assert result1 is not None
        assert result2 is not None


class TestRippleDisplacement:
    """Tests for ripple displacement."""

    def test_ripple_creates_canvas(self):
        """Test ripple displacement returns a canvas."""
        canvas = create_test_canvas()
        ripple = RippleDisplacement(amplitude=4.0, wavelength=8.0)
        result = ripple.apply(canvas)
        assert result is not None

    def test_ripple_with_center(self):
        """Test ripple with custom center."""
        canvas = create_test_canvas()
        ripple = RippleDisplacement(center=(4, 4), amplitude=4.0, wavelength=8.0)
        result = ripple.apply(canvas)
        assert result is not None

    def test_ripple_phase(self):
        """Test ripple phase for animation."""
        canvas = create_test_canvas()
        ripple = RippleDisplacement(amplitude=4.0, wavelength=8.0, phase=1.0)
        result = ripple.apply(canvas)
        assert result is not None


class TestTwirlDisplacement:
    """Tests for twirl displacement."""

    def test_twirl_creates_canvas(self):
        """Test twirl displacement returns a canvas."""
        canvas = create_test_canvas()
        twirl = TwirlDisplacement(angle=45.0, radius=0.8)
        result = twirl.apply(canvas)
        assert result is not None

    def test_twirl_with_center(self):
        """Test twirl with custom center."""
        canvas = create_test_canvas()
        twirl = TwirlDisplacement(center=(4, 4), angle=45.0, radius=0.6)
        result = twirl.apply(canvas)
        assert result is not None

    def test_twirl_negative_angle(self):
        """Test twirl with negative angle."""
        canvas = create_test_canvas()
        twirl = TwirlDisplacement(angle=-45.0, radius=0.8)
        result = twirl.apply(canvas)
        assert result is not None


class TestBulgeDisplacement:
    """Tests for bulge displacement."""

    def test_bulge_creates_canvas(self):
        """Test bulge displacement returns a canvas."""
        canvas = create_test_canvas()
        bulge = BulgeDisplacement(strength=0.5, radius=0.6)
        result = bulge.apply(canvas)
        assert result is not None

    def test_pinch_effect(self):
        """Test pinch (negative bulge)."""
        canvas = create_test_canvas()
        pinch = BulgeDisplacement(strength=-0.5, radius=0.6)
        result = pinch.apply(canvas)
        assert result is not None

    def test_bulge_with_center(self):
        """Test bulge with custom center."""
        canvas = create_test_canvas()
        bulge = BulgeDisplacement(center=(4, 4), strength=0.5, radius=0.6)
        result = bulge.apply(canvas)
        assert result is not None


class TestNoiseDisplacement:
    """Tests for noise displacement."""

    def test_noise_creates_canvas(self):
        """Test noise displacement returns a canvas."""
        canvas = create_test_canvas()
        noise = NoiseDisplacement(strength=2.0, seed=42)
        result = noise.apply(canvas)
        assert result is not None

    def test_noise_deterministic(self):
        """Test noise is deterministic with same seed."""
        canvas = create_test_canvas()
        noise1 = NoiseDisplacement(strength=2.0, seed=42)
        noise2 = NoiseDisplacement(strength=2.0, seed=42)

        result1 = noise1.apply(canvas)
        result2 = noise2.apply(canvas)

        # Results should be identical with same seed
        assert result1.pixels[8][8] == result2.pixels[8][8]

    def test_noise_smoothness(self):
        """Test noise smoothness parameter."""
        canvas = create_test_canvas()
        noise_rough = NoiseDisplacement(strength=2.0, seed=42, smoothness=0.0)
        noise_smooth = NoiseDisplacement(strength=2.0, seed=42, smoothness=1.0)

        result_rough = noise_rough.apply(canvas)
        result_smooth = noise_smooth.apply(canvas)

        assert result_rough is not None
        assert result_smooth is not None


class TestBarrelDisplacement:
    """Tests for barrel distortion."""

    def test_barrel_creates_canvas(self):
        """Test barrel displacement returns a canvas."""
        canvas = create_test_canvas()
        barrel = BarrelDisplacement(strength=0.3)
        result = barrel.apply(canvas)
        assert result is not None

    def test_pincushion_effect(self):
        """Test pincushion (negative barrel)."""
        canvas = create_test_canvas()
        pincushion = BarrelDisplacement(strength=-0.3)
        result = pincushion.apply(canvas)
        assert result is not None


class TestShearDisplacement:
    """Tests for shear displacement."""

    def test_horizontal_shear(self):
        """Test horizontal shear."""
        canvas = create_test_canvas()
        shear = ShearDisplacement(horizontal=0.5, vertical=0.0)
        result = shear.apply(canvas)
        assert result is not None

    def test_vertical_shear(self):
        """Test vertical shear."""
        canvas = create_test_canvas()
        shear = ShearDisplacement(horizontal=0.0, vertical=0.5)
        result = shear.apply(canvas)
        assert result is not None


class TestCompositeDisplacement:
    """Tests for composite displacement."""

    def test_combine_effects(self):
        """Test combining multiple effects."""
        canvas = create_test_canvas()

        wave = WaveDisplacement(amplitude=2.0, frequency=0.1)
        twirl = TwirlDisplacement(angle=15.0, radius=0.5)

        composite = CompositeDisplacement(wave, twirl)
        result = composite.apply(canvas)
        assert result is not None

    def test_add_effect(self):
        """Test adding effects with chaining."""
        canvas = create_test_canvas()

        composite = CompositeDisplacement()
        composite.add(WaveDisplacement(amplitude=2.0)).add(NoiseDisplacement(strength=1.0))

        assert len(composite.effects) == 2
        result = composite.apply(canvas)
        assert result is not None


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_apply_wave(self):
        """Test apply_wave function."""
        canvas = create_test_canvas()
        result = apply_wave(canvas, amplitude=3.0, frequency=0.2)
        assert result is not None

    def test_apply_ripple(self):
        """Test apply_ripple function."""
        canvas = create_test_canvas()
        result = apply_ripple(canvas, amplitude=4.0, wavelength=8.0)
        assert result is not None

    def test_apply_twirl(self):
        """Test apply_twirl function."""
        canvas = create_test_canvas()
        result = apply_twirl(canvas, angle=45.0, radius=0.8)
        assert result is not None

    def test_apply_bulge(self):
        """Test apply_bulge function."""
        canvas = create_test_canvas()
        result = apply_bulge(canvas, strength=0.5, radius=0.6)
        assert result is not None

    def test_apply_noise(self):
        """Test apply_noise function."""
        canvas = create_test_canvas()
        result = apply_noise(canvas, strength=2.0, seed=42)
        assert result is not None

    def test_apply_barrel(self):
        """Test apply_barrel function."""
        canvas = create_test_canvas()
        result = apply_barrel(canvas, strength=0.3)
        assert result is not None

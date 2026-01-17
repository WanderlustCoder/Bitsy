"""Tests for palette cycling animations."""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core import Canvas
from core.palette import Palette, hex_to_rgba
from effects.palette_cycle import (
    CycleRange,
    PaletteCycler,
    ColorShifter,
    PaletteCycleAnimation,
    create_water_palette,
    create_fire_palette,
    create_rainbow_palette,
    create_lava_palette,
    create_water_cycle,
    create_fire_cycle,
    create_rainbow_cycle,
    create_shimmer_cycle,
    create_lava_cycle,
    create_cycle,
    list_cycle_presets,
)


def create_test_palette():
    """Create a test palette."""
    return Palette([
        (50, 50, 50, 255),
        (100, 100, 100, 255),
        (150, 150, 150, 255),
        (200, 200, 200, 255),
    ], "Test")


def create_canvas_with_palette(palette):
    """Create a canvas using palette colors."""
    canvas = Canvas(8, 8)
    colors = palette.colors

    for y in range(8):
        for x in range(8):
            color_idx = (x + y) % len(colors)
            color = colors[color_idx]
            canvas.set_pixel(x, y, color)

    return canvas


class TestCycleRange:
    """Tests for CycleRange."""

    def test_cycle_range_init(self):
        """Test CycleRange initialization."""
        cycle_range = CycleRange(start_index=0, end_index=3, speed=2.0)
        assert cycle_range.start_index == 0
        assert cycle_range.end_index == 3
        assert cycle_range.speed == 2.0

    def test_cycle_range_update(self):
        """Test CycleRange update."""
        cycle_range = CycleRange(start_index=0, end_index=3, speed=1.0)
        cycle_range.update(0.5)  # Half a step
        assert cycle_range._offset > 0

    def test_cycle_range_wrapping(self):
        """Test cycle range wraps around."""
        cycle_range = CycleRange(start_index=0, end_index=3, speed=1.0)

        # Update beyond range
        for _ in range(10):
            cycle_range.update(1.0)

        # Offset should be wrapped
        assert 0 <= cycle_range._offset < 4

    def test_cycle_range_bounce(self):
        """Test bounce mode."""
        cycle_range = CycleRange(start_index=0, end_index=3, speed=1.0, bounce=True)

        # Update to trigger bounce
        for _ in range(10):
            cycle_range.update(1.0)

        # Offset should be within bounds
        assert 0 <= cycle_range._offset <= 3

    def test_get_mapped_index(self):
        """Test index mapping."""
        cycle_range = CycleRange(start_index=0, end_index=3, speed=1.0)
        cycle_range._offset = 1.0

        # Index 0 should map to 1 (offset by 1)
        mapped = cycle_range.get_mapped_index(0, 4)
        assert mapped == 1

        # Index outside range should be unchanged
        mapped = cycle_range.get_mapped_index(5, 8)
        assert mapped == 5


class TestPaletteCycler:
    """Tests for PaletteCycler."""

    def test_cycler_init(self):
        """Test PaletteCycler initialization."""
        palette = create_test_palette()
        cycler = PaletteCycler(palette)
        assert cycler.base_palette == palette
        assert len(cycler.ranges) == 0

    def test_add_range(self):
        """Test adding cycle ranges."""
        palette = create_test_palette()
        cycler = PaletteCycler(palette)

        cycler.add_range(0, 3, speed=2.0)
        assert len(cycler.ranges) == 1

    def test_add_range_chaining(self):
        """Test add_range returns self for chaining."""
        palette = create_test_palette()
        cycler = PaletteCycler(palette)

        result = cycler.add_range(0, 3)
        assert result is cycler

    def test_update(self):
        """Test cycler update."""
        palette = create_test_palette()
        cycler = PaletteCycler(palette)
        cycler.add_range(0, 3, speed=1.0)

        cycler.update(0.5)
        assert cycler.elapsed == 0.5

    def test_get_current_palette(self):
        """Test getting cycled palette."""
        palette = create_test_palette()
        cycler = PaletteCycler(palette)
        cycler.add_range(0, 3, speed=1.0)

        # Initial palette should match base
        current = cycler.get_current_palette()
        assert len(current.colors) == len(palette.colors)

        # After update, colors should be shifted
        cycler.update(1.0)
        shifted = cycler.get_current_palette()
        assert shifted is not None

    def test_apply(self):
        """Test applying cycle to canvas."""
        palette = create_test_palette()
        canvas = create_canvas_with_palette(palette)
        cycler = PaletteCycler(palette)
        cycler.add_range(0, 3, speed=1.0)

        cycler.update(1.0)
        result = cycler.apply(canvas)
        assert result is not None
        assert result.width == canvas.width


class TestColorShifter:
    """Tests for ColorShifter."""

    def test_hue_rotation(self):
        """Test hue rotation effect."""
        shifter = ColorShifter()
        shifter.set_hue_rotation(90.0)  # 90 degrees per second

        palette = create_test_palette()
        canvas = create_canvas_with_palette(palette)

        shifter.update(1.0)
        result = shifter.apply(canvas)
        assert result is not None

    def test_saturation_wave(self):
        """Test saturation wave effect."""
        shifter = ColorShifter()
        shifter.set_saturation_wave(amplitude=0.3, frequency=1.0)

        palette = create_test_palette()
        canvas = create_canvas_with_palette(palette)

        shifter.update(0.5)
        result = shifter.apply(canvas)
        assert result is not None

    def test_brightness_wave(self):
        """Test brightness wave effect."""
        shifter = ColorShifter()
        shifter.set_brightness_wave(amplitude=0.2, frequency=2.0)

        palette = create_test_palette()
        canvas = create_canvas_with_palette(palette)

        shifter.update(0.25)
        result = shifter.apply(canvas)
        assert result is not None

    def test_target_color(self):
        """Test targeting specific colors."""
        shifter = ColorShifter()
        shifter.set_hue_rotation(90.0)
        shifter.target_color((100, 100, 100, 255), tolerance=20)

        palette = create_test_palette()
        canvas = create_canvas_with_palette(palette)

        shifter.update(1.0)
        result = shifter.apply(canvas)
        assert result is not None


class TestPresetPalettes:
    """Tests for preset palettes."""

    def test_water_palette(self):
        """Test water palette creation."""
        palette = create_water_palette()
        assert len(palette.colors) > 0
        assert palette.name == "Water"

    def test_fire_palette(self):
        """Test fire palette creation."""
        palette = create_fire_palette()
        assert len(palette.colors) > 0
        assert palette.name == "Fire"

    def test_rainbow_palette(self):
        """Test rainbow palette creation."""
        palette = create_rainbow_palette()
        assert len(palette.colors) > 0

    def test_rainbow_palette_steps(self):
        """Test rainbow palette with custom steps."""
        palette = create_rainbow_palette(steps=8)
        assert len(palette.colors) == 8

    def test_lava_palette(self):
        """Test lava palette creation."""
        palette = create_lava_palette()
        assert len(palette.colors) > 0


class TestPresetCycles:
    """Tests for preset cycle creators."""

    def test_water_cycle(self):
        """Test water cycle creation."""
        cycler = create_water_cycle()
        assert len(cycler.ranges) > 0

    def test_fire_cycle(self):
        """Test fire cycle creation."""
        cycler = create_fire_cycle()
        assert len(cycler.ranges) > 0

    def test_rainbow_cycle(self):
        """Test rainbow cycle creation."""
        cycler = create_rainbow_cycle()
        assert len(cycler.ranges) > 0

    def test_shimmer_cycle(self):
        """Test shimmer cycle creation."""
        palette = create_test_palette()
        cycler = create_shimmer_cycle(palette)
        assert cycler.base_palette == palette

    def test_lava_cycle(self):
        """Test lava cycle creation."""
        cycler = create_lava_cycle()
        assert len(cycler.ranges) > 0

    def test_cycles_with_custom_palette(self):
        """Test cycles with custom palette."""
        palette = create_test_palette()
        cycler = create_water_cycle(palette)
        assert cycler.base_palette == palette


class TestPaletteCycleAnimation:
    """Tests for PaletteCycleAnimation."""

    def test_generate_frames(self):
        """Test frame generation."""
        palette = create_water_palette()
        canvas = create_canvas_with_palette(palette)
        cycler = create_water_cycle(palette)

        animation = PaletteCycleAnimation(cycler, frame_time=1/30)
        frames = animation.generate_frames(canvas, duration=0.5)

        assert len(frames) > 0
        assert all(f.width == canvas.width for f in frames)

    def test_get_frame(self):
        """Test getting frame at specific time."""
        palette = create_water_palette()
        canvas = create_canvas_with_palette(palette)
        cycler = create_water_cycle(palette)

        animation = PaletteCycleAnimation(cycler)
        frame = animation.get_frame(canvas, time=0.5)

        assert frame is not None
        assert frame.width == canvas.width


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_create_cycle(self):
        """Test create_cycle function."""
        palette = create_test_palette()

        for preset in list_cycle_presets():
            cycler = create_cycle(palette, preset)
            assert cycler is not None

    def test_create_cycle_speed(self):
        """Test create_cycle with speed multiplier."""
        palette = create_test_palette()
        cycler = create_cycle(palette, "shimmer", speed=2.0)
        assert cycler is not None

    def test_list_cycle_presets(self):
        """Test list_cycle_presets function."""
        presets = list_cycle_presets()
        assert len(presets) > 0
        assert "water" in presets
        assert "fire" in presets
        assert "shimmer" in presets

"""
Palette Cycling Animations - Classic color cycling effects.

Provides palette cycling for water shimmer, fire flicker,
rainbow effects, and other animated color effects.
"""

import math
from typing import List, Tuple, Optional, Dict, Callable
from dataclasses import dataclass, field
from enum import Enum

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Canvas
from core.color import Color
from core.palette import Palette, rgb_to_hsv, hsv_to_rgb


@dataclass
class CycleRange:
    """A range of palette colors to cycle."""
    start_index: int
    end_index: int
    speed: float = 1.0       # Steps per second
    reverse: bool = False    # Cycle direction
    bounce: bool = False     # Ping-pong mode

    # Internal state
    _offset: float = 0.0
    _direction: int = 1

    def update(self, dt: float) -> None:
        """Update cycle state.

        Args:
            dt: Delta time in seconds
        """
        step = self.speed * dt * self._direction

        if self.reverse:
            step = -step

        self._offset += step

        # Handle wrapping/bouncing
        range_size = self.end_index - self.start_index + 1

        if self.bounce:
            if self._offset >= range_size:
                self._offset = range_size - 1
                self._direction = -1
            elif self._offset < 0:
                self._offset = 0
                self._direction = 1
        else:
            self._offset = self._offset % range_size

    def get_mapped_index(self, original_index: int, palette_size: int) -> int:
        """Get the cycled index for an original palette index.

        Args:
            original_index: Original palette index
            palette_size: Total palette size

        Returns:
            Cycled palette index
        """
        if original_index < self.start_index or original_index > self.end_index:
            return original_index

        range_size = self.end_index - self.start_index + 1
        relative_index = original_index - self.start_index

        # Apply cycle offset
        new_relative = (relative_index + int(self._offset)) % range_size
        return self.start_index + new_relative


class PaletteCycler:
    """Manages palette cycling animations."""

    def __init__(self, base_palette: Palette):
        """Initialize cycler.

        Args:
            base_palette: Base palette to cycle
        """
        self.base_palette = base_palette
        self.ranges: List[CycleRange] = []
        self.elapsed = 0.0

    def add_range(
        self,
        start: int,
        end: int,
        speed: float = 1.0,
        reverse: bool = False,
        bounce: bool = False
    ) -> 'PaletteCycler':
        """Add a cycling range.

        Args:
            start: Start index in palette
            end: End index in palette
            speed: Cycle speed
            reverse: Reverse direction
            bounce: Ping-pong mode

        Returns:
            Self for chaining
        """
        self.ranges.append(CycleRange(
            start_index=start,
            end_index=end,
            speed=speed,
            reverse=reverse,
            bounce=bounce
        ))
        return self

    def update(self, dt: float) -> None:
        """Update all cycle states.

        Args:
            dt: Delta time in seconds
        """
        self.elapsed += dt
        for cycle_range in self.ranges:
            cycle_range.update(dt)

    def get_current_palette(self) -> Palette:
        """Get palette with current cycle state.

        Returns:
            Cycled palette
        """
        new_colors = list(self.base_palette.colors)
        palette_size = len(new_colors)

        for cycle_range in self.ranges:
            # Create mapping of old to new indices
            index_map = {}
            for i in range(cycle_range.start_index, cycle_range.end_index + 1):
                if i < palette_size:
                    mapped = cycle_range.get_mapped_index(i, palette_size)
                    index_map[i] = mapped

            # Apply mapping
            original = list(new_colors)
            for old_idx, new_idx in index_map.items():
                if new_idx < palette_size:
                    new_colors[old_idx] = original[new_idx]

        return Palette(new_colors, f"{self.base_palette.name}_cycled")

    def apply(self, canvas: Canvas) -> Canvas:
        """Remap canvas colors to cycled palette.

        Args:
            canvas: Source canvas

        Returns:
            Canvas with cycled colors
        """
        cycled_palette = self.get_current_palette()
        result = Canvas(canvas.width, canvas.height)

        # Build color mapping from base to cycled
        color_map = {}
        for i, base_color in enumerate(self.base_palette.colors):
            key = (base_color[0], base_color[1], base_color[2])
            cycled = cycled_palette.colors[i]
            color_map[key] = cycled

        for y in range(canvas.height):
            for x in range(canvas.width):
                pixel = canvas.pixels[y][x]
                if pixel[3] == 0:
                    continue

                key = (pixel[0], pixel[1], pixel[2])
                if key in color_map:
                    cycled = color_map[key]
                    result.pixels[y][x] = [cycled[0], cycled[1], cycled[2], pixel[3]]
                else:
                    # Find nearest palette color
                    nearest_idx = self.base_palette.find_nearest(pixel)
                    cycled = cycled_palette.colors[nearest_idx]
                    result.pixels[y][x] = [cycled[0], cycled[1], cycled[2], pixel[3]]

        return result


class ColorShifter:
    """Shift colors over time without strict palette mapping."""

    def __init__(self):
        """Initialize color shifter."""
        self.elapsed = 0.0
        self.hue_speed = 0.0
        self.saturation_wave = 0.0
        self.brightness_wave = 0.0
        self.target_colors: List[Color] = []
        self.target_tolerance = 30

    def set_hue_rotation(self, speed: float) -> 'ColorShifter':
        """Set continuous hue rotation.

        Args:
            speed: Degrees per second

        Returns:
            Self for chaining
        """
        self.hue_speed = speed
        return self

    def set_saturation_wave(self, amplitude: float, frequency: float) -> 'ColorShifter':
        """Set saturation oscillation.

        Args:
            amplitude: Wave amplitude (0-1)
            frequency: Wave frequency in Hz

        Returns:
            Self for chaining
        """
        self.saturation_wave = amplitude
        self._sat_freq = frequency
        return self

    def set_brightness_wave(self, amplitude: float, frequency: float) -> 'ColorShifter':
        """Set brightness oscillation.

        Args:
            amplitude: Wave amplitude (0-1)
            frequency: Wave frequency in Hz

        Returns:
            Self for chaining
        """
        self.brightness_wave = amplitude
        self._bright_freq = frequency
        return self

    def target_color(self, color: Color, tolerance: int = 30) -> 'ColorShifter':
        """Add a color to target for shifting.

        Args:
            color: Color to target
            tolerance: Color matching tolerance

        Returns:
            Self for chaining
        """
        self.target_colors.append(color)
        self.target_tolerance = tolerance
        return self

    def update(self, dt: float) -> None:
        """Update shift state.

        Args:
            dt: Delta time in seconds
        """
        self.elapsed += dt

    def apply(self, canvas: Canvas) -> Canvas:
        """Apply color shifting.

        Args:
            canvas: Source canvas

        Returns:
            Shifted canvas
        """
        result = Canvas(canvas.width, canvas.height)

        for y in range(canvas.height):
            for x in range(canvas.width):
                pixel = canvas.pixels[y][x]
                if pixel[3] == 0:
                    continue

                # Check if this pixel should be affected
                should_shift = len(self.target_colors) == 0
                if not should_shift:
                    for target in self.target_colors:
                        if (abs(pixel[0] - target[0]) <= self.target_tolerance and
                            abs(pixel[1] - target[1]) <= self.target_tolerance and
                            abs(pixel[2] - target[2]) <= self.target_tolerance):
                            should_shift = True
                            break

                if should_shift:
                    shifted = self._shift_pixel(pixel)
                    result.pixels[y][x] = list(shifted)
                else:
                    result.pixels[y][x] = list(pixel)

        return result

    def _shift_pixel(self, pixel: Color) -> Color:
        """Apply shift to a single pixel."""
        h, s, v = rgb_to_hsv(pixel[0], pixel[1], pixel[2])

        # Apply hue rotation
        if self.hue_speed != 0:
            h = (h + self.hue_speed * self.elapsed) % 360

        # Apply saturation wave
        if self.saturation_wave > 0:
            wave = math.sin(self.elapsed * self._sat_freq * 2 * math.pi)
            s = max(0, min(1, s + wave * self.saturation_wave))

        # Apply brightness wave
        if self.brightness_wave > 0:
            wave = math.sin(self.elapsed * self._bright_freq * 2 * math.pi)
            v = max(0, min(1, v + wave * self.brightness_wave))

        r, g, b = hsv_to_rgb(h, s, v)
        return (r, g, b, pixel[3])


# =============================================================================
# Preset Palette Cycles
# =============================================================================

def create_water_palette() -> Palette:
    """Create a water-appropriate palette."""
    return Palette([
        (20, 60, 100, 255),    # Deep blue
        (30, 80, 130, 255),
        (40, 100, 160, 255),
        (60, 130, 190, 255),   # Mid blue
        (80, 160, 210, 255),
        (120, 190, 230, 255),
        (160, 210, 240, 255),
        (200, 230, 250, 255),  # Light highlight
    ], "Water")


def create_water_cycle(palette: Optional[Palette] = None) -> PaletteCycler:
    """Create water shimmer cycle.

    Args:
        palette: Water palette (None = use default)

    Returns:
        Configured palette cycler
    """
    if palette is None:
        palette = create_water_palette()

    cycler = PaletteCycler(palette)
    # Cycle through water blues slowly
    cycler.add_range(0, len(palette) - 1, speed=2.0, bounce=True)
    return cycler


def create_fire_palette() -> Palette:
    """Create a fire-appropriate palette."""
    return Palette([
        (40, 10, 0, 255),      # Dark red/brown
        (80, 20, 0, 255),
        (140, 40, 0, 255),     # Deep orange
        (200, 80, 0, 255),
        (255, 120, 20, 255),   # Orange
        (255, 180, 60, 255),   # Yellow-orange
        (255, 220, 120, 255),
        (255, 255, 200, 255),  # Bright yellow/white
    ], "Fire")


def create_fire_cycle(palette: Optional[Palette] = None) -> PaletteCycler:
    """Create fire flicker cycle.

    Args:
        palette: Fire palette (None = use default)

    Returns:
        Configured palette cycler
    """
    if palette is None:
        palette = create_fire_palette()

    cycler = PaletteCycler(palette)
    # Fast flickering cycle
    cycler.add_range(0, len(palette) - 1, speed=8.0, reverse=False)
    return cycler


def create_rainbow_palette(steps: int = 12) -> Palette:
    """Create a rainbow palette.

    Args:
        steps: Number of hue steps

    Returns:
        Rainbow palette
    """
    colors = []
    for i in range(steps):
        hue = (i * 360) / steps
        r, g, b = hsv_to_rgb(hue, 1.0, 1.0)
        colors.append((r, g, b, 255))
    return Palette(colors, "Rainbow")


def create_rainbow_cycle(palette: Optional[Palette] = None) -> PaletteCycler:
    """Create rainbow rotation cycle.

    Args:
        palette: Rainbow palette (None = use default)

    Returns:
        Configured palette cycler
    """
    if palette is None:
        palette = create_rainbow_palette()

    cycler = PaletteCycler(palette)
    # Continuous rainbow rotation
    cycler.add_range(0, len(palette) - 1, speed=3.0)
    return cycler


def create_shimmer_cycle(palette: Palette) -> PaletteCycler:
    """Create subtle shimmer effect.

    Args:
        palette: Base palette

    Returns:
        Configured palette cycler
    """
    cycler = PaletteCycler(palette)
    # Shimmer only affects brighter colors (higher indices typically)
    mid = len(palette) // 2
    if mid > 0:
        cycler.add_range(mid, len(palette) - 1, speed=1.5, bounce=True)
    return cycler


def create_lava_palette() -> Palette:
    """Create a lava-appropriate palette."""
    return Palette([
        (20, 0, 0, 255),       # Dark
        (60, 0, 0, 255),
        (100, 20, 0, 255),
        (160, 40, 0, 255),
        (200, 60, 0, 255),
        (255, 100, 0, 255),
        (255, 160, 20, 255),
        (255, 200, 100, 255),
        (255, 220, 160, 255),
        (255, 240, 200, 255),  # Hot white
    ], "Lava")


def create_lava_cycle(palette: Optional[Palette] = None) -> PaletteCycler:
    """Create lava flow cycle.

    Args:
        palette: Lava palette (None = use default)

    Returns:
        Configured palette cycler
    """
    if palette is None:
        palette = create_lava_palette()

    cycler = PaletteCycler(palette)
    # Slow flowing effect
    cycler.add_range(0, len(palette) - 1, speed=1.5)
    return cycler


# =============================================================================
# Animation Integration
# =============================================================================

@dataclass
class PaletteCycleAnimation:
    """Animates palette cycling over multiple frames."""
    cycler: PaletteCycler
    frame_time: float = 1/30  # Time per frame

    def generate_frames(
        self,
        canvas: Canvas,
        duration: float
    ) -> List[Canvas]:
        """Generate animation frames.

        Args:
            canvas: Source canvas
            duration: Animation duration in seconds

        Returns:
            List of animated frames
        """
        frames = []
        time = 0.0

        while time < duration:
            self.cycler.update(self.frame_time)
            frame = self.cycler.apply(canvas)
            frames.append(frame)
            time += self.frame_time

        return frames

    def get_frame(self, canvas: Canvas, time: float) -> Canvas:
        """Get frame at specific time.

        Args:
            canvas: Source canvas
            time: Time in seconds

        Returns:
            Animated frame
        """
        # Update to target time
        dt = time - self.cycler.elapsed
        if dt > 0:
            self.cycler.update(dt)

        return self.cycler.apply(canvas)


# =============================================================================
# Convenience Functions
# =============================================================================

def create_cycle(
    palette: Palette,
    preset: str = "shimmer",
    speed: float = 1.0
) -> PaletteCycler:
    """Create a palette cycler with preset.

    Args:
        palette: Base palette
        preset: Preset name (shimmer, water, fire, rainbow, lava)
        speed: Speed multiplier

    Returns:
        Configured palette cycler
    """
    if preset == "water":
        cycler = create_water_cycle(palette)
    elif preset == "fire":
        cycler = create_fire_cycle(palette)
    elif preset == "rainbow":
        cycler = create_rainbow_cycle(palette)
    elif preset == "lava":
        cycler = create_lava_cycle(palette)
    else:  # shimmer
        cycler = create_shimmer_cycle(palette)

    # Apply speed multiplier
    for cycle_range in cycler.ranges:
        cycle_range.speed *= speed

    return cycler


def list_cycle_presets() -> List[str]:
    """List available cycle presets.

    Returns:
        List of preset names
    """
    return ["shimmer", "water", "fire", "rainbow", "lava"]

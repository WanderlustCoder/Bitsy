"""
Color Grading and LUTs - Cinematic color manipulation.

Provides lookup tables (LUTs), levels adjustment, curves, and
color balance for cinematic post-processing.
"""

import math
from typing import List, Tuple, Optional, Dict, Callable
from dataclasses import dataclass, field

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Canvas
from core.color import Color
from core.palette import rgb_to_hsv, hsv_to_rgb


@dataclass
class LUT:
    """3D Color Lookup Table for color grading.

    A LUT maps input RGB values to output RGB values, allowing
    complex color transformations to be applied efficiently.
    """
    size: int = 16  # Usually 16, 32, or 64
    data: List[List[List[Color]]] = field(default_factory=list)

    def __post_init__(self):
        if not self.data:
            # Initialize with identity mapping
            self.data = self._create_identity()

    def _create_identity(self) -> List[List[List[Color]]]:
        """Create identity LUT (no transformation)."""
        data = []
        for r in range(self.size):
            r_plane = []
            for g in range(self.size):
                g_row = []
                for b in range(self.size):
                    # Map indices to full 0-255 range
                    out_r = int(r * 255 / (self.size - 1))
                    out_g = int(g * 255 / (self.size - 1))
                    out_b = int(b * 255 / (self.size - 1))
                    g_row.append((out_r, out_g, out_b, 255))
                r_plane.append(g_row)
            data.append(r_plane)
        return data

    def lookup(self, color: Color) -> Color:
        """Look up transformed color.

        Args:
            color: Input color

        Returns:
            Transformed color from LUT
        """
        # Map 0-255 to LUT indices
        r_idx = int(color[0] * (self.size - 1) / 255)
        g_idx = int(color[1] * (self.size - 1) / 255)
        b_idx = int(color[2] * (self.size - 1) / 255)

        # Clamp indices
        r_idx = max(0, min(self.size - 1, r_idx))
        g_idx = max(0, min(self.size - 1, g_idx))
        b_idx = max(0, min(self.size - 1, b_idx))

        result = self.data[r_idx][g_idx][b_idx]
        return (result[0], result[1], result[2], color[3])

    def lookup_interpolated(self, color: Color) -> Color:
        """Look up with trilinear interpolation for smoother results.

        Args:
            color: Input color

        Returns:
            Interpolated transformed color
        """
        # Calculate fractional indices
        r_f = color[0] * (self.size - 1) / 255
        g_f = color[1] * (self.size - 1) / 255
        b_f = color[2] * (self.size - 1) / 255

        # Get integer and fractional parts
        r0, g0, b0 = int(r_f), int(g_f), int(b_f)
        r1 = min(self.size - 1, r0 + 1)
        g1 = min(self.size - 1, g0 + 1)
        b1 = min(self.size - 1, b0 + 1)

        rf, gf, bf = r_f - r0, g_f - g0, b_f - b0

        # Trilinear interpolation
        def lerp(a, b, t):
            return a + (b - a) * t

        def lerp_color(c1, c2, t):
            return tuple(lerp(c1[i], c2[i], t) for i in range(3))

        # Interpolate along B axis
        c000 = self.data[r0][g0][b0]
        c001 = self.data[r0][g0][b1]
        c00 = lerp_color(c000, c001, bf)

        c010 = self.data[r0][g1][b0]
        c011 = self.data[r0][g1][b1]
        c01 = lerp_color(c010, c011, bf)

        c100 = self.data[r1][g0][b0]
        c101 = self.data[r1][g0][b1]
        c10 = lerp_color(c100, c101, bf)

        c110 = self.data[r1][g1][b0]
        c111 = self.data[r1][g1][b1]
        c11 = lerp_color(c110, c111, bf)

        # Interpolate along G axis
        c0 = lerp_color(c00, c01, gf)
        c1 = lerp_color(c10, c11, gf)

        # Interpolate along R axis
        result = lerp_color(c0, c1, rf)

        return (int(result[0]), int(result[1]), int(result[2]), color[3])

    @classmethod
    def identity(cls, size: int = 16) -> 'LUT':
        """Create identity (no-op) LUT.

        Args:
            size: LUT size

        Returns:
            Identity LUT
        """
        return cls(size=size)

    @classmethod
    def from_function(cls, func: Callable[[Color], Color], size: int = 16) -> 'LUT':
        """Create LUT from a color transformation function.

        Args:
            func: Function that takes and returns Color
            size: LUT size

        Returns:
            LUT with function baked in
        """
        lut = cls(size=size)

        for r in range(size):
            for g in range(size):
                for b in range(size):
                    # Map indices to colors
                    in_r = int(r * 255 / (size - 1))
                    in_g = int(g * 255 / (size - 1))
                    in_b = int(b * 255 / (size - 1))

                    result = func((in_r, in_g, in_b, 255))
                    lut.data[r][g][b] = result

        return lut


class ColorGrader:
    """Apply color grading transformations to canvases."""

    def apply_lut(self, canvas: Canvas, lut: LUT, interpolate: bool = True) -> Canvas:
        """Apply LUT color transformation.

        Args:
            canvas: Source canvas
            lut: LUT to apply
            interpolate: Use trilinear interpolation

        Returns:
            Graded canvas
        """
        result = Canvas(canvas.width, canvas.height)
        lookup = lut.lookup_interpolated if interpolate else lut.lookup

        for y in range(canvas.height):
            for x in range(canvas.width):
                pixel = canvas.pixels[y][x]
                if pixel[3] > 0:
                    graded = lookup(pixel)
                    result.pixels[y][x] = list(graded)

        return result

    def adjust_levels(
        self,
        canvas: Canvas,
        shadows: float = 0.0,
        midtones: float = 1.0,
        highlights: float = 1.0,
        output_min: int = 0,
        output_max: int = 255
    ) -> Canvas:
        """Adjust tonal levels.

        Args:
            canvas: Source canvas
            shadows: Shadow point (0-1, lifts blacks)
            midtones: Gamma adjustment (>1 = darker mids)
            highlights: Highlight point (0-1, clips whites)
            output_min: Minimum output value
            output_max: Maximum output value

        Returns:
            Adjusted canvas
        """
        result = Canvas(canvas.width, canvas.height)

        # Build lookup table for efficiency
        lookup = []
        for i in range(256):
            # Input mapping
            v = i / 255.0

            # Apply input levels
            v = max(0, (v - shadows) / (highlights - shadows))

            # Apply gamma (midtones)
            if midtones != 1.0:
                v = pow(max(0, v), 1.0 / midtones)

            # Apply output levels
            v = output_min + v * (output_max - output_min)
            v = max(0, min(255, int(v)))

            lookup.append(v)

        for y in range(canvas.height):
            for x in range(canvas.width):
                pixel = canvas.pixels[y][x]
                if pixel[3] > 0:
                    r = lookup[pixel[0]]
                    g = lookup[pixel[1]]
                    b = lookup[pixel[2]]
                    result.pixels[y][x] = [r, g, b, pixel[3]]

        return result

    def adjust_curves(
        self,
        canvas: Canvas,
        red_curve: Optional[List[Tuple[float, float]]] = None,
        green_curve: Optional[List[Tuple[float, float]]] = None,
        blue_curve: Optional[List[Tuple[float, float]]] = None,
        master_curve: Optional[List[Tuple[float, float]]] = None
    ) -> Canvas:
        """Apply RGB curves adjustment.

        Curves are lists of (input, output) control points where values
        are 0-1. Points are linearly interpolated.

        Args:
            canvas: Source canvas
            red_curve: Red channel curve
            green_curve: Green channel curve
            blue_curve: Blue channel curve
            master_curve: Applied to all channels

        Returns:
            Adjusted canvas
        """
        # Build lookup tables from curves
        def build_lut(curve: Optional[List[Tuple[float, float]]]) -> List[int]:
            if not curve:
                return list(range(256))

            # Sort by input value
            sorted_curve = sorted(curve, key=lambda p: p[0])

            # Ensure we have endpoints
            if sorted_curve[0][0] > 0:
                sorted_curve.insert(0, (0.0, sorted_curve[0][1]))
            if sorted_curve[-1][0] < 1:
                sorted_curve.append((1.0, sorted_curve[-1][1]))

            lut = []
            for i in range(256):
                x = i / 255.0

                # Find surrounding control points
                for j in range(len(sorted_curve) - 1):
                    if sorted_curve[j][0] <= x <= sorted_curve[j + 1][0]:
                        # Linear interpolation
                        x1, y1 = sorted_curve[j]
                        x2, y2 = sorted_curve[j + 1]
                        t = (x - x1) / (x2 - x1) if x2 != x1 else 0
                        y = y1 + t * (y2 - y1)
                        lut.append(max(0, min(255, int(y * 255))))
                        break
                else:
                    lut.append(i)

            return lut

        r_lut = build_lut(red_curve)
        g_lut = build_lut(green_curve)
        b_lut = build_lut(blue_curve)
        m_lut = build_lut(master_curve)

        result = Canvas(canvas.width, canvas.height)

        for y in range(canvas.height):
            for x in range(canvas.width):
                pixel = canvas.pixels[y][x]
                if pixel[3] > 0:
                    r = m_lut[r_lut[pixel[0]]]
                    g = m_lut[g_lut[pixel[1]]]
                    b = m_lut[b_lut[pixel[2]]]
                    result.pixels[y][x] = [r, g, b, pixel[3]]

        return result

    def color_balance(
        self,
        canvas: Canvas,
        shadows_shift: Tuple[int, int, int] = (0, 0, 0),
        midtones_shift: Tuple[int, int, int] = (0, 0, 0),
        highlights_shift: Tuple[int, int, int] = (0, 0, 0)
    ) -> Canvas:
        """Shift colors in different tonal ranges.

        Args:
            canvas: Source canvas
            shadows_shift: RGB shift for shadows (-255 to 255)
            midtones_shift: RGB shift for midtones
            highlights_shift: RGB shift for highlights

        Returns:
            Balanced canvas
        """
        result = Canvas(canvas.width, canvas.height)

        for y in range(canvas.height):
            for x in range(canvas.width):
                pixel = canvas.pixels[y][x]
                if pixel[3] == 0:
                    continue

                # Calculate luminance to determine tonal region
                lum = (pixel[0] + pixel[1] + pixel[2]) / 3 / 255

                # Weight shifts based on luminance
                # Shadows: 0-0.33, Midtones: 0.33-0.66, Highlights: 0.66-1.0
                if lum < 0.33:
                    shadow_weight = 1.0 - (lum / 0.33)
                    mid_weight = lum / 0.33
                    high_weight = 0.0
                elif lum < 0.66:
                    shadow_weight = 0.0
                    mid_weight = 1.0 - abs(lum - 0.5) / 0.16
                    high_weight = (lum - 0.33) / 0.33
                else:
                    shadow_weight = 0.0
                    mid_weight = (1.0 - lum) / 0.34
                    high_weight = (lum - 0.66) / 0.34

                # Apply weighted shifts
                r_shift = (
                    shadows_shift[0] * shadow_weight +
                    midtones_shift[0] * mid_weight +
                    highlights_shift[0] * high_weight
                )
                g_shift = (
                    shadows_shift[1] * shadow_weight +
                    midtones_shift[1] * mid_weight +
                    highlights_shift[1] * high_weight
                )
                b_shift = (
                    shadows_shift[2] * shadow_weight +
                    midtones_shift[2] * mid_weight +
                    highlights_shift[2] * high_weight
                )

                r = max(0, min(255, pixel[0] + int(r_shift)))
                g = max(0, min(255, pixel[1] + int(g_shift)))
                b = max(0, min(255, pixel[2] + int(b_shift)))

                result.pixels[y][x] = [r, g, b, pixel[3]]

        return result

    def hue_saturation(
        self,
        canvas: Canvas,
        hue_shift: float = 0.0,
        saturation: float = 1.0,
        lightness: float = 0.0
    ) -> Canvas:
        """Adjust hue, saturation, and lightness.

        Args:
            canvas: Source canvas
            hue_shift: Hue rotation in degrees
            saturation: Saturation multiplier (0 = grayscale)
            lightness: Lightness adjustment (-1 to 1)

        Returns:
            Adjusted canvas
        """
        result = Canvas(canvas.width, canvas.height)

        for y in range(canvas.height):
            for x in range(canvas.width):
                pixel = canvas.pixels[y][x]
                if pixel[3] == 0:
                    continue

                h, s, v = rgb_to_hsv(pixel[0], pixel[1], pixel[2])

                # Apply adjustments
                h = (h + hue_shift) % 360
                s = max(0, min(1, s * saturation))
                v = max(0, min(1, v + lightness))

                r, g, b = hsv_to_rgb(h, s, v)
                result.pixels[y][x] = [r, g, b, pixel[3]]

        return result

    def temperature_tint(
        self,
        canvas: Canvas,
        temperature: float = 0.0,
        tint: float = 0.0
    ) -> Canvas:
        """Adjust white balance.

        Args:
            canvas: Source canvas
            temperature: Yellow-Blue shift (-100 to 100)
            tint: Green-Magenta shift (-100 to 100)

        Returns:
            Adjusted canvas
        """
        result = Canvas(canvas.width, canvas.height)

        for y in range(canvas.height):
            for x in range(canvas.width):
                pixel = canvas.pixels[y][x]
                if pixel[3] == 0:
                    continue

                r, g, b = pixel[0], pixel[1], pixel[2]

                # Temperature: shift yellow/blue
                if temperature > 0:
                    # Warmer: add yellow (red+green), reduce blue
                    r = min(255, r + int(temperature * 0.5))
                    g = min(255, g + int(temperature * 0.25))
                    b = max(0, b - int(temperature * 0.5))
                else:
                    # Cooler: add blue, reduce red/green
                    r = max(0, r + int(temperature * 0.5))
                    g = max(0, g + int(temperature * 0.25))
                    b = min(255, b - int(temperature * 0.5))

                # Tint: shift green/magenta
                if tint > 0:
                    # More magenta: add red+blue, reduce green
                    r = min(255, r + int(tint * 0.3))
                    g = max(0, g - int(tint * 0.3))
                    b = min(255, b + int(tint * 0.3))
                else:
                    # More green: add green, reduce red+blue
                    r = max(0, r + int(tint * 0.3))
                    g = min(255, g - int(tint * 0.3))
                    b = max(0, b + int(tint * 0.3))

                result.pixels[y][x] = [r, g, b, pixel[3]]

        return result


# =============================================================================
# Preset Color Grades
# =============================================================================

def create_warm_grade() -> LUT:
    """Create warm/sunset color grade."""
    def warm_transform(color: Color) -> Color:
        r = min(255, int(color[0] * 1.1))
        g = int(color[1] * 0.95)
        b = int(color[2] * 0.85)
        return (r, g, b, color[3])

    return LUT.from_function(warm_transform)


def create_cool_grade() -> LUT:
    """Create cool/blue color grade."""
    def cool_transform(color: Color) -> Color:
        r = int(color[0] * 0.9)
        g = int(color[1] * 0.95)
        b = min(255, int(color[2] * 1.1))
        return (r, g, b, color[3])

    return LUT.from_function(cool_transform)


def create_vintage_grade() -> LUT:
    """Create vintage/faded film look."""
    def vintage_transform(color: Color) -> Color:
        # Lift blacks, fade contrast
        r = min(255, int(20 + color[0] * 0.85))
        g = min(255, int(15 + color[1] * 0.88))
        b = min(255, int(25 + color[2] * 0.82))

        # Add slight sepia
        avg = (r + g + b) // 3
        r = min(255, r + (avg - r) // 4 + 10)
        g = min(255, g + (avg - g) // 4)
        b = max(0, b + (avg - b) // 4 - 10)

        return (r, g, b, color[3])

    return LUT.from_function(vintage_transform)


def create_cyberpunk_grade() -> LUT:
    """Create cyberpunk/neon color grade."""
    def cyberpunk_transform(color: Color) -> Color:
        h, s, v = rgb_to_hsv(color[0], color[1], color[2])

        # Boost saturation
        s = min(1.0, s * 1.3)

        # Shift toward cyan/magenta
        if h < 60 or h > 300:
            # Reds -> Magenta
            h = (h + 30) % 360
        elif 60 <= h < 180:
            # Yellows/Greens -> Cyan
            h = (h + 40) % 360

        r, g, b = hsv_to_rgb(h, s, v)

        # Add slight teal shadow/orange highlight split
        lum = (r + g + b) / 3
        if lum < 128:
            b = min(255, b + 15)
            g = min(255, g + 5)
        else:
            r = min(255, r + 10)

        return (r, g, b, color[3])

    return LUT.from_function(cyberpunk_transform)


def create_noir_grade() -> LUT:
    """Create noir/high contrast B&W grade."""
    def noir_transform(color: Color) -> Color:
        # Convert to grayscale with high contrast
        gray = int(0.299 * color[0] + 0.587 * color[1] + 0.114 * color[2])

        # Apply S-curve for contrast
        normalized = gray / 255.0
        if normalized < 0.5:
            normalized = 2 * normalized * normalized
        else:
            normalized = 1 - 2 * (1 - normalized) * (1 - normalized)

        gray = int(normalized * 255)
        return (gray, gray, gray, color[3])

    return LUT.from_function(noir_transform)


def create_golden_hour_grade() -> LUT:
    """Create golden hour/sunset lighting grade."""
    def golden_transform(color: Color) -> Color:
        # Warm shadows, golden highlights
        lum = (color[0] + color[1] + color[2]) / 3 / 255

        r = color[0]
        g = color[1]
        b = color[2]

        # Add orange to highlights
        if lum > 0.5:
            highlight_factor = (lum - 0.5) * 2
            r = min(255, r + int(30 * highlight_factor))
            g = min(255, g + int(15 * highlight_factor))
            b = max(0, b - int(20 * highlight_factor))

        # Add magenta to shadows
        if lum < 0.5:
            shadow_factor = (0.5 - lum) * 2
            r = min(255, r + int(10 * shadow_factor))
            b = min(255, b + int(15 * shadow_factor))

        return (r, g, b, color[3])

    return LUT.from_function(golden_transform)


# =============================================================================
# Convenience Functions
# =============================================================================

def apply_color_grade(canvas: Canvas, preset: str = "warm") -> Canvas:
    """Apply a preset color grade.

    Args:
        canvas: Source canvas
        preset: Grade name (warm, cool, vintage, cyberpunk, noir, golden_hour)

    Returns:
        Graded canvas
    """
    presets = {
        "warm": create_warm_grade,
        "cool": create_cool_grade,
        "vintage": create_vintage_grade,
        "cyberpunk": create_cyberpunk_grade,
        "noir": create_noir_grade,
        "golden_hour": create_golden_hour_grade,
    }

    grade_func = presets.get(preset, create_warm_grade)
    lut = grade_func()

    grader = ColorGrader()
    return grader.apply_lut(canvas, lut)


def adjust_levels(
    canvas: Canvas,
    shadows: float = 0.0,
    midtones: float = 1.0,
    highlights: float = 1.0
) -> Canvas:
    """Adjust tonal levels.

    Args:
        canvas: Source canvas
        shadows: Shadow lift (0-1)
        midtones: Gamma (>1 = darker)
        highlights: Highlight clip (0-1)

    Returns:
        Adjusted canvas
    """
    grader = ColorGrader()
    return grader.adjust_levels(canvas, shadows, midtones, highlights)


def adjust_temperature(canvas: Canvas, temperature: float = 0.0) -> Canvas:
    """Adjust color temperature.

    Args:
        canvas: Source canvas
        temperature: Warm/cool shift (-100 to 100)

    Returns:
        Adjusted canvas
    """
    grader = ColorGrader()
    return grader.temperature_tint(canvas, temperature, 0)


def list_color_grades() -> List[str]:
    """List available color grade presets.

    Returns:
        List of preset names
    """
    return ["warm", "cool", "vintage", "cyberpunk", "noir", "golden_hour"]

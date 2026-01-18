"""
Color Harmony - Color theory tools for generating harmonious palettes.

Implements color harmony rules:
- Complementary: Opposite colors on the wheel
- Analogous: Adjacent colors
- Triadic: Three evenly spaced colors
- Split-complementary: Base + two adjacent to complement
- Tetradic: Four colors forming a rectangle

Also provides:
- Shading ramp generation with hue shifting
- Palette optimization
- Accent color suggestion
"""

import sys
import os
from typing import List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import math

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.color import (
    Color, rgb_to_hsv, hsv_to_rgb, rgb_to_hsl, hsl_to_rgb,
    shift_hue, adjust_saturation, lighten, darken,
    color_distance_weighted
)
from core.palette import Palette


class HarmonyType(Enum):
    """Types of color harmony."""
    COMPLEMENTARY = "complementary"
    ANALOGOUS = "analogous"
    TRIADIC = "triadic"
    SPLIT_COMPLEMENTARY = "split_complementary"
    TETRADIC = "tetradic"
    MONOCHROMATIC = "monochromatic"


@dataclass
class HarmonyResult:
    """Result of harmony generation."""
    harmony_type: HarmonyType
    base_color: Color
    colors: List[Color]
    palette: Palette

    def __str__(self) -> str:
        return f"{self.harmony_type.value} harmony from RGB{self.base_color[:3]}: {len(self.colors)} colors"


class ColorHarmony:
    """Convenience wrappers for harmony generation."""

    @staticmethod
    def complementary(base_color: Color, include_base: bool = True) -> HarmonyResult:
        return generate_complementary(base_color, include_base=include_base)

    @staticmethod
    def analogous(base_color: Color, spread: float = 30,
                  count: int = 3, include_base: bool = True) -> HarmonyResult:
        return generate_analogous(base_color, spread=spread, count=count, include_base=include_base)

    @staticmethod
    def triadic(base_color: Color, include_base: bool = True) -> HarmonyResult:
        return generate_triadic(base_color, include_base=include_base)

    @staticmethod
    def split_complementary(base_color: Color, split_angle: float = 30,
                            include_base: bool = True) -> HarmonyResult:
        return generate_split_complementary(base_color, split_angle=split_angle, include_base=include_base)

    @staticmethod
    def tetradic(base_color: Color, angle: float = 60,
                 include_base: bool = True) -> HarmonyResult:
        return generate_tetradic(base_color, angle=angle, include_base=include_base)

    @staticmethod
    def monochromatic(base_color: Color, count: int = 5,
                      value_range: Tuple[float, float] = (0.2, 1.0)) -> HarmonyResult:
        return generate_monochromatic(base_color, count=count, value_range=value_range)

    @staticmethod
    def harmony(base_color: Color, harmony_type: HarmonyType,
                **kwargs) -> HarmonyResult:
        return generate_harmony(base_color, harmony_type, **kwargs)


def _normalize_hue(hue: float) -> float:
    """Normalize hue to 0-360 range."""
    while hue < 0:
        hue += 360
    while hue >= 360:
        hue -= 360
    return hue


def _hsv_to_rgba(h: float, s: float, v: float, a: int = 255) -> Color:
    """Convert HSV to RGBA color."""
    r, g, b = hsv_to_rgb(h, s, v)
    return (r, g, b, a)


def generate_complementary(base_color: Color, include_base: bool = True) -> HarmonyResult:
    """
    Generate complementary color palette (opposite on color wheel).

    Args:
        base_color: Starting color (RGBA)
        include_base: Include base color in result

    Returns:
        HarmonyResult with complementary colors
    """
    h, s, v = rgb_to_hsv(base_color[0], base_color[1], base_color[2])

    colors = []
    if include_base:
        colors.append(base_color)

    # Complement is 180 degrees opposite
    comp_h = _normalize_hue(h + 180)
    complement = _hsv_to_rgba(comp_h, s, v, base_color[3] if len(base_color) > 3 else 255)
    colors.append(complement)

    return HarmonyResult(
        harmony_type=HarmonyType.COMPLEMENTARY,
        base_color=base_color,
        colors=colors,
        palette=Palette(colors)
    )


def generate_analogous(base_color: Color, spread: float = 30,
                       count: int = 3, include_base: bool = True) -> HarmonyResult:
    """
    Generate analogous color palette (adjacent colors on wheel).

    Args:
        base_color: Starting color (RGBA)
        spread: Degrees between adjacent colors
        count: Total number of colors (including base if included)
        include_base: Include base color in result

    Returns:
        HarmonyResult with analogous colors
    """
    h, s, v = rgb_to_hsv(base_color[0], base_color[1], base_color[2])
    alpha = base_color[3] if len(base_color) > 3 else 255

    colors = []

    # Calculate starting hue
    if include_base:
        total_spread = spread * (count - 1)
        start_h = h - total_spread / 2
    else:
        total_spread = spread * count
        start_h = h - total_spread / 2

    for i in range(count):
        new_h = _normalize_hue(start_h + spread * i)
        if include_base and abs(_normalize_hue(new_h - h)) < 1:
            colors.append(base_color)
        else:
            colors.append(_hsv_to_rgba(new_h, s, v, alpha))

    return HarmonyResult(
        harmony_type=HarmonyType.ANALOGOUS,
        base_color=base_color,
        colors=colors,
        palette=Palette(colors)
    )


def generate_triadic(base_color: Color, include_base: bool = True) -> HarmonyResult:
    """
    Generate triadic color palette (three evenly spaced colors).

    Args:
        base_color: Starting color (RGBA)
        include_base: Include base color in result

    Returns:
        HarmonyResult with triadic colors
    """
    h, s, v = rgb_to_hsv(base_color[0], base_color[1], base_color[2])
    alpha = base_color[3] if len(base_color) > 3 else 255

    colors = []
    if include_base:
        colors.append(base_color)

    # Two other colors at 120 and 240 degrees
    colors.append(_hsv_to_rgba(_normalize_hue(h + 120), s, v, alpha))
    colors.append(_hsv_to_rgba(_normalize_hue(h + 240), s, v, alpha))

    return HarmonyResult(
        harmony_type=HarmonyType.TRIADIC,
        base_color=base_color,
        colors=colors,
        palette=Palette(colors)
    )


def generate_split_complementary(base_color: Color, split_angle: float = 30,
                                  include_base: bool = True) -> HarmonyResult:
    """
    Generate split-complementary palette (base + two colors adjacent to complement).

    Args:
        base_color: Starting color (RGBA)
        split_angle: Degrees from complement for split colors
        include_base: Include base color in result

    Returns:
        HarmonyResult with split-complementary colors
    """
    h, s, v = rgb_to_hsv(base_color[0], base_color[1], base_color[2])
    alpha = base_color[3] if len(base_color) > 3 else 255

    colors = []
    if include_base:
        colors.append(base_color)

    # Two colors adjacent to complement
    comp_h = h + 180
    colors.append(_hsv_to_rgba(_normalize_hue(comp_h - split_angle), s, v, alpha))
    colors.append(_hsv_to_rgba(_normalize_hue(comp_h + split_angle), s, v, alpha))

    return HarmonyResult(
        harmony_type=HarmonyType.SPLIT_COMPLEMENTARY,
        base_color=base_color,
        colors=colors,
        palette=Palette(colors)
    )


def generate_tetradic(base_color: Color, angle: float = 60,
                      include_base: bool = True) -> HarmonyResult:
    """
    Generate tetradic (rectangular) color palette.

    Args:
        base_color: Starting color (RGBA)
        angle: Angle offset for the rectangle
        include_base: Include base color in result

    Returns:
        HarmonyResult with tetradic colors
    """
    h, s, v = rgb_to_hsv(base_color[0], base_color[1], base_color[2])
    alpha = base_color[3] if len(base_color) > 3 else 255

    colors = []
    if include_base:
        colors.append(base_color)

    # Three other colors forming a rectangle
    colors.append(_hsv_to_rgba(_normalize_hue(h + angle), s, v, alpha))
    colors.append(_hsv_to_rgba(_normalize_hue(h + 180), s, v, alpha))
    colors.append(_hsv_to_rgba(_normalize_hue(h + 180 + angle), s, v, alpha))

    return HarmonyResult(
        harmony_type=HarmonyType.TETRADIC,
        base_color=base_color,
        colors=colors,
        palette=Palette(colors)
    )


def generate_monochromatic(base_color: Color, count: int = 5,
                           value_range: Tuple[float, float] = (0.2, 1.0)) -> HarmonyResult:
    """
    Generate monochromatic palette (same hue, varying brightness).

    Args:
        base_color: Starting color (RGBA)
        count: Number of colors to generate
        value_range: Range of brightness values (0-1)

    Returns:
        HarmonyResult with monochromatic colors
    """
    h, s, v = rgb_to_hsv(base_color[0], base_color[1], base_color[2])
    alpha = base_color[3] if len(base_color) > 3 else 255

    colors = []
    min_v, max_v = value_range

    for i in range(count):
        t = i / (count - 1) if count > 1 else 0.5
        new_v = min_v + t * (max_v - min_v)
        colors.append(_hsv_to_rgba(h, s, new_v, alpha))

    return HarmonyResult(
        harmony_type=HarmonyType.MONOCHROMATIC,
        base_color=base_color,
        colors=colors,
        palette=Palette(colors)
    )


def create_shading_ramp(base_color: Color, levels: int = 5,
                        highlight_hue_shift: float = 15,
                        shadow_hue_shift: float = -20,
                        highlight_sat_adjust: float = 0.9,
                        shadow_sat_adjust: float = 0.85) -> List[Color]:
    """
    Create a shading ramp with professional hue shifting.

    Follows pixel art best practices:
    - Highlights shift toward warm (yellow/orange)
    - Shadows shift toward cool (blue/purple)
    - Saturation adjusts for natural look

    Args:
        base_color: Middle color of the ramp
        levels: Number of colors in ramp (odd numbers work best)
        highlight_hue_shift: Degrees to shift highlights toward warm
        shadow_hue_shift: Degrees to shift shadows toward cool
        highlight_sat_adjust: Saturation multiplier for highlights
        shadow_sat_adjust: Saturation multiplier for shadows

    Returns:
        List of colors from darkest to lightest
    """
    h, s, v = rgb_to_hsv(base_color[0], base_color[1], base_color[2])
    alpha = base_color[3] if len(base_color) > 3 else 255

    colors = []
    mid = levels // 2

    for i in range(levels):
        # Calculate position relative to middle (-1 to 1)
        t = (i - mid) / mid if mid > 0 else 0

        # Hue shift (negative t = shadow, positive t = highlight)
        if t < 0:
            hue_shift = shadow_hue_shift * abs(t)
            sat_mult = 1.0 + (shadow_sat_adjust - 1.0) * abs(t)
        else:
            hue_shift = highlight_hue_shift * t
            sat_mult = 1.0 + (highlight_sat_adjust - 1.0) * t

        new_h = _normalize_hue(h + hue_shift)
        new_s = max(0, min(1, s * sat_mult))

        # Value adjustment (darker for shadows, lighter for highlights)
        if t < 0:
            new_v = v * (0.4 + 0.6 * (1 + t))  # Range: 0.4v to v
        else:
            new_v = v + (1 - v) * t * 0.6  # Range: v to v + 0.6*(1-v)

        new_v = max(0, min(1, new_v))

        colors.append(_hsv_to_rgba(new_h, new_s, new_v, alpha))

    return colors


def optimize_palette(colors: List[Color], max_colors: int,
                     preserve_extremes: bool = True) -> List[Color]:
    """
    Reduce a palette to specified number of colors.

    Uses median cut algorithm to find representative colors.

    Args:
        colors: List of colors to reduce
        max_colors: Maximum colors in output
        preserve_extremes: Keep darkest and lightest colors

    Returns:
        Optimized palette with max_colors or fewer
    """
    if len(colors) <= max_colors:
        return colors

    # Remove duplicates first
    unique = list(set(colors))
    if len(unique) <= max_colors:
        return unique

    # Find extremes if preserving
    preserved = []
    remaining = list(unique)

    if preserve_extremes:
        # Find darkest
        darkest = min(remaining, key=lambda c: c[0] + c[1] + c[2])
        preserved.append(darkest)
        remaining.remove(darkest)

        # Find lightest
        if remaining:
            lightest = max(remaining, key=lambda c: c[0] + c[1] + c[2])
            preserved.append(lightest)
            remaining.remove(lightest)

    # Simple k-means-like reduction for remaining colors
    target_count = max_colors - len(preserved)

    if target_count <= 0:
        return preserved

    # Start with evenly distributed colors
    step = len(remaining) // target_count if target_count > 0 else 1
    selected = remaining[::max(1, step)][:target_count]

    # Refine by moving toward cluster centers
    for _ in range(5):  # Iterations
        # Assign each color to nearest selected
        clusters = {tuple(c): [] for c in selected}
        for color in remaining:
            nearest = min(selected, key=lambda s: color_distance_weighted(color, s))
            clusters[tuple(nearest)].append(color)

        # Move selected to cluster centers
        new_selected = []
        for center, members in clusters.items():
            if members:
                avg_r = sum(c[0] for c in members) // len(members)
                avg_g = sum(c[1] for c in members) // len(members)
                avg_b = sum(c[2] for c in members) // len(members)
                avg_a = sum(c[3] for c in members) // len(members)
                new_selected.append((avg_r, avg_g, avg_b, avg_a))
            else:
                new_selected.append(center)
        selected = new_selected

    return preserved + selected


def suggest_accent_color(palette: List[Color], min_distance: float = 100) -> Color:
    """
    Suggest an accent color that stands out from the palette.

    Args:
        palette: Existing palette colors
        min_distance: Minimum color distance from existing colors

    Returns:
        Suggested accent color
    """
    if not palette:
        return (255, 200, 0, 255)  # Default gold accent

    # Calculate average hue of palette
    hues = []
    for color in palette:
        h, s, v = rgb_to_hsv(color[0], color[1], color[2])
        if s > 0.1:  # Only consider saturated colors
            hues.append(h)

    if not hues:
        # Palette is mostly grayscale - suggest saturated color
        return (255, 100, 100, 255)

    avg_hue = sum(hues) / len(hues)

    # Try complementary first
    accent_hue = _normalize_hue(avg_hue + 180)
    accent = _hsv_to_rgba(accent_hue, 0.8, 0.9, 255)

    # Check if it's far enough from all palette colors
    min_dist = min(color_distance_weighted(accent, c) for c in palette)
    if min_dist >= min_distance:
        return accent

    # Try split complementary
    for offset in [150, 210, 120, 240]:
        accent_hue = _normalize_hue(avg_hue + offset)
        accent = _hsv_to_rgba(accent_hue, 0.8, 0.9, 255)
        min_dist = min(color_distance_weighted(accent, c) for c in palette)
        if min_dist >= min_distance:
            return accent

    # Fall back to high-saturation version of complement
    return _hsv_to_rgba(_normalize_hue(avg_hue + 180), 1.0, 1.0, 255)


def generate_harmony(base_color: Color, harmony_type: HarmonyType,
                     **kwargs) -> HarmonyResult:
    """
    Generate color harmony of specified type.

    Args:
        base_color: Starting color
        harmony_type: Type of harmony to generate
        **kwargs: Additional arguments for specific harmony type

    Returns:
        HarmonyResult
    """
    generators = {
        HarmonyType.COMPLEMENTARY: generate_complementary,
        HarmonyType.ANALOGOUS: generate_analogous,
        HarmonyType.TRIADIC: generate_triadic,
        HarmonyType.SPLIT_COMPLEMENTARY: generate_split_complementary,
        HarmonyType.TETRADIC: generate_tetradic,
        HarmonyType.MONOCHROMATIC: generate_monochromatic,
    }

    generator = generators.get(harmony_type)
    if generator is None:
        raise ValueError(f"Unknown harmony type: {harmony_type}")

    return generator(base_color, **kwargs)


def generate_harmonious_palette(base_color: Color,
                                harmony_type: HarmonyType = HarmonyType.ANALOGOUS,
                                count: int = 3,
                                include_base: bool = False,
                                **kwargs) -> Palette:
    """
    Generate a harmonious palette around a base color.

    Args:
        base_color: Starting color
        harmony_type: Harmony rule to apply
        count: Maximum number of colors to return
        include_base: Include base color in palette
        **kwargs: Additional arguments for the harmony generator

    Returns:
        Palette with harmonious colors
    """
    if harmony_type == HarmonyType.ANALOGOUS:
        result = generate_analogous(
            base_color,
            count=count + (1 if include_base else 0),
            include_base=include_base,
            **kwargs
        )
        colors = result.colors
    elif harmony_type == HarmonyType.MONOCHROMATIC:
        result = generate_monochromatic(base_color, count=count, **kwargs)
        colors = result.colors
    else:
        result = generate_harmony(base_color, harmony_type, include_base=include_base, **kwargs)
        colors = result.colors

    if not include_base:
        colors = [color for color in colors if color != base_color]

    if count is not None:
        colors = colors[:count]

    return Palette(colors, f"{harmony_type.value} harmony")


def palette_from_image_colors(colors: List[Color], harmony_type: HarmonyType,
                               key_color_index: int = 0) -> HarmonyResult:
    """
    Generate a harmonious palette based on colors from an image.

    Args:
        colors: Colors extracted from image (sorted by frequency)
        harmony_type: Type of harmony to generate
        key_color_index: Which color to use as base (0 = most common)

    Returns:
        HarmonyResult based on image colors
    """
    if not colors:
        raise ValueError("No colors provided")

    base_color = colors[min(key_color_index, len(colors) - 1)]
    return generate_harmony(base_color, harmony_type)

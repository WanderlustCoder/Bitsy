"""
Color Utilities for Anime-Style Rendering

Provides hue-shifting color palettes where shadows shift toward cool colors
and highlights shift toward warm, creating the characteristic anime look.
"""

import math
from typing import List, Tuple, Optional
from dataclasses import dataclass

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.color import Color
from core.palette import rgb_to_hsv, hsv_to_rgb


@dataclass
class HueShiftPalette:
    """
    Anime-style color palette where shadows shift hue, not just darken.

    Creates palettes where:
    - Shadows shift toward cool (blue/purple) and boost saturation
    - Highlights shift toward warm (yellow/orange) with slight desat

    This creates the characteristic anime color blocking look.
    """
    base_color: Tuple[int, int, int]  # RGB base color
    shadow_hue_shift: float = -15.0   # Degrees to shift shadows (negative = cool)
    highlight_hue_shift: float = 10.0  # Degrees to shift highlights (positive = warm)
    shadow_sat_boost: float = 0.15     # Saturation boost for shadows
    highlight_sat_reduce: float = 0.1  # Saturation reduction for highlights

    def generate(self, levels: int = 6) -> List[Tuple[int, int, int, int]]:
        """
        Generate a hue-shifted color ramp.

        Args:
            levels: Number of colors (6 recommended for anime style)

        Returns:
            List of RGBA colors from darkest (shadow) to lightest (highlight)
        """
        r, g, b = self.base_color
        h, s, v = rgb_to_hsv(r, g, b)

        colors = []
        mid = (levels - 1) / 2.0

        for i in range(levels):
            # Position: -1.0 (shadow) to +1.0 (highlight)
            t = (i - mid) / mid if mid > 0 else 0

            # Hue shift: interpolate between shadow and highlight shifts
            if t < 0:
                hue_shift = self.shadow_hue_shift * abs(t)
            else:
                hue_shift = self.highlight_hue_shift * t

            new_h = (h + hue_shift) % 360

            # Saturation: boost in shadows, reduce in highlights
            if t < 0:
                new_s = min(1.0, s + self.shadow_sat_boost * abs(t))
            else:
                new_s = max(0.0, s - self.highlight_sat_reduce * t)

            # Value: darken shadows, lighten highlights
            if t < 0:
                # Shadows: compress toward dark
                new_v = v * (1.0 + t * 0.5)  # t is negative, so this darkens
            else:
                # Highlights: expand toward white
                new_v = v + (1.0 - v) * t * 0.6

            new_v = max(0.05, min(1.0, new_v))

            # Convert back to RGB
            nr, ng, nb = hsv_to_rgb(new_h, new_s, new_v)
            colors.append((int(nr), int(ng), int(nb), 255))

        return colors

    def get_shadow(self, depth: int = 1) -> Tuple[int, int, int, int]:
        """Get a shadow color at specified depth (1 = light shadow, 2 = deep)."""
        ramp = self.generate(6)
        idx = max(0, 2 - depth)  # 2=base shadow, 1=mid shadow, 0=deep shadow
        return ramp[idx]

    def get_highlight(self, intensity: int = 1) -> Tuple[int, int, int, int]:
        """Get a highlight color at specified intensity (1 = subtle, 2 = bright)."""
        ramp = self.generate(6)
        idx = min(5, 3 + intensity)  # 4=highlight, 5=peak
        return ramp[idx]


class PaletteManager:
    """
    Manages limited color palettes for anime-style rendering.

    Ensures each element (skin, hair, eyes, etc.) uses a limited
    set of colors, creating the characteristic flat-shaded anime look.
    """

    def __init__(self, max_colors_per_element: int = 6):
        self.max_colors = max_colors_per_element
        self.palettes: dict[str, List[Tuple[int, int, int, int]]] = {}

    def register_palette(self, name: str, colors: List[Tuple[int, int, int, int]]) -> None:
        """
        Register an element palette.

        Args:
            name: Palette identifier (e.g., "skin", "hair", "eyes")
            colors: List of RGBA colors in the palette
        """
        # Limit to max colors
        self.palettes[name] = colors[:self.max_colors]

    def get_nearest(self, color: Tuple[int, int, int], palette_name: str) -> Tuple[int, int, int, int]:
        """
        Snap a color to the nearest color in the specified palette.

        Args:
            color: RGB color to snap
            palette_name: Name of registered palette

        Returns:
            Nearest RGBA color from palette
        """
        if palette_name not in self.palettes:
            return (color[0], color[1], color[2], 255)

        palette = self.palettes[palette_name]
        if not palette:
            return (color[0], color[1], color[2], 255)

        # Find nearest by RGB distance
        min_dist = float('inf')
        nearest = palette[0]

        for p_color in palette:
            dist = (
                (color[0] - p_color[0]) ** 2 +
                (color[1] - p_color[1]) ** 2 +
                (color[2] - p_color[2]) ** 2
            )
            if dist < min_dist:
                min_dist = dist
                nearest = p_color

        return nearest

    def get_palette(self, name: str) -> List[Tuple[int, int, int, int]]:
        """Get a registered palette by name."""
        return self.palettes.get(name, [])


# Pre-defined anime-style color ramps

# Anime skin ramp (6 colors: deep shadow -> peak highlight)
# Uses warm base with cool shadows for that anime warmth
ANIME_SKIN_RAMP = [
    (139, 90, 74, 255),    # Deep shadow (cool undertone)
    (166, 117, 99, 255),   # Shadow
    (212, 160, 136, 255),  # Base shadow
    (232, 196, 168, 255),  # Base
    (245, 220, 200, 255),  # Highlight
    (255, 240, 224, 255),  # Peak highlight
]

# Anime purple hair ramp (for reference image matching)
ANIME_PURPLE_HAIR_RAMP = [
    (60, 40, 80, 255),     # Deep shadow
    (90, 60, 110, 255),    # Shadow
    (130, 90, 150, 255),   # Base shadow
    (160, 120, 180, 255),  # Base
    (190, 150, 210, 255),  # Highlight
    (220, 190, 235, 255),  # Peak/rim light
]

# Generic anime hair palettes by color
ANIME_HAIR_PALETTES = {
    "black": [
        (20, 20, 30, 255),
        (35, 35, 50, 255),
        (55, 50, 70, 255),
        (75, 70, 90, 255),
        (100, 95, 115, 255),
        (130, 125, 145, 255),
    ],
    "brown": [
        (50, 35, 30, 255),
        (80, 55, 45, 255),
        (110, 75, 55, 255),
        (140, 100, 75, 255),
        (170, 130, 100, 255),
        (200, 165, 135, 255),
    ],
    "blonde": [
        (150, 120, 70, 255),
        (180, 150, 90, 255),
        (210, 180, 120, 255),
        (230, 205, 150, 255),
        (245, 225, 180, 255),
        (255, 245, 215, 255),
    ],
    "red": [
        (90, 30, 30, 255),
        (130, 45, 40, 255),
        (170, 65, 55, 255),
        (200, 90, 70, 255),
        (225, 120, 95, 255),
        (245, 160, 130, 255),
    ],
    "purple": ANIME_PURPLE_HAIR_RAMP,
    "blue": [
        (30, 50, 90, 255),
        (50, 75, 130, 255),
        (75, 105, 165, 255),
        (100, 135, 195, 255),
        (135, 170, 220, 255),
        (175, 205, 240, 255),
    ],
    "pink": [
        (130, 70, 90, 255),
        (170, 95, 120, 255),
        (200, 125, 150, 255),
        (225, 155, 180, 255),
        (240, 190, 210, 255),
        (255, 220, 235, 255),
    ],
    "green": [
        (35, 70, 50, 255),
        (55, 100, 70, 255),
        (80, 135, 95, 255),
        (110, 165, 125, 255),
        (145, 195, 155, 255),
        (185, 225, 190, 255),
    ],
    "white": [
        (170, 170, 180, 255),
        (190, 190, 200, 255),
        (210, 210, 220, 255),
        (225, 225, 235, 255),
        (240, 240, 248, 255),
        (252, 252, 255, 255),
    ],
    "gray": [
        (80, 80, 90, 255),
        (110, 110, 120, 255),
        (140, 140, 150, 255),
        (170, 170, 180, 255),
        (200, 200, 210, 255),
        (225, 225, 235, 255),
    ],
}

# Anime eye palettes (iris colors)
ANIME_EYE_PALETTES = {
    "brown": [
        (60, 35, 25, 255),
        (100, 60, 40, 255),
        (140, 90, 60, 255),
        (170, 120, 85, 255),
        (200, 155, 115, 255),
    ],
    "blue": [
        (40, 70, 130, 255),
        (60, 100, 170, 255),
        (90, 140, 200, 255),
        (130, 175, 225, 255),
        (180, 210, 245, 255),
    ],
    "green": [
        (40, 80, 50, 255),
        (60, 120, 70, 255),
        (90, 160, 100, 255),
        (130, 195, 140, 255),
        (175, 225, 180, 255),
    ],
    "purple": [
        (70, 40, 100, 255),
        (100, 60, 140, 255),
        (140, 90, 180, 255),
        (180, 130, 210, 255),
        (215, 175, 235, 255),
    ],
    "amber": [
        (140, 80, 30, 255),
        (180, 110, 45, 255),
        (210, 145, 60, 255),
        (235, 180, 90, 255),
        (250, 215, 130, 255),
    ],
    "red": [
        (120, 30, 30, 255),
        (160, 45, 45, 255),
        (200, 70, 70, 255),
        (230, 110, 110, 255),
        (250, 160, 160, 255),
    ],
}


def create_hue_shifted_ramp(base_color: Tuple[int, int, int],
                            levels: int = 6,
                            shadow_shift: float = -15.0,
                            highlight_shift: float = 10.0) -> List[Tuple[int, int, int, int]]:
    """
    Convenience function to create a hue-shifted color ramp.

    Args:
        base_color: RGB base color (middle of ramp)
        levels: Number of colors in ramp
        shadow_shift: Hue shift for shadows (negative = cool)
        highlight_shift: Hue shift for highlights (positive = warm)

    Returns:
        List of RGBA colors from darkest to lightest
    """
    palette = HueShiftPalette(
        base_color=base_color,
        shadow_hue_shift=shadow_shift,
        highlight_hue_shift=highlight_shift
    )
    return palette.generate(levels)


def get_anime_hair_ramp(color_name: str) -> List[Tuple[int, int, int, int]]:
    """
    Get a pre-defined anime hair color ramp.

    Args:
        color_name: Hair color name (black, brown, blonde, red, purple, blue, pink, green, white, gray)

    Returns:
        6-color RGBA ramp for hair rendering
    """
    return ANIME_HAIR_PALETTES.get(color_name.lower(), ANIME_HAIR_PALETTES["brown"])


def get_anime_eye_ramp(color_name: str) -> List[Tuple[int, int, int, int]]:
    """
    Get a pre-defined anime eye color ramp.

    Args:
        color_name: Eye color name (brown, blue, green, purple, amber, red)

    Returns:
        5-color RGBA ramp for iris rendering
    """
    return ANIME_EYE_PALETTES.get(color_name.lower(), ANIME_EYE_PALETTES["brown"])


def apply_rim_light(color: Tuple[int, int, int, int],
                    rim_color: Tuple[int, int, int],
                    intensity: float,
                    edge_factor: float) -> Tuple[int, int, int, int]:
    """
    Apply rim lighting to a color based on edge proximity.

    Args:
        color: Base RGBA color
        rim_color: RGB rim light color
        intensity: Overall rim light intensity (0.0-1.0)
        edge_factor: How close to edge (0.0 = interior, 1.0 = edge)

    Returns:
        RGBA color with rim lighting applied
    """
    # Rim light only applies at edges
    if edge_factor < 0.7:
        return color

    # Blend toward rim color at edges
    blend = (edge_factor - 0.7) / 0.3 * intensity
    blend = min(1.0, blend)

    r = int(color[0] * (1 - blend) + rim_color[0] * blend)
    g = int(color[1] * (1 - blend) + rim_color[1] * blend)
    b = int(color[2] * (1 - blend) + rim_color[2] * blend)

    return (r, g, b, color[3])

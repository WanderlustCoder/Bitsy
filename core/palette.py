"""
Palette - Color management for pixel art.

Provides palette creation, hue shifting, and color quantization.
"""

import math
from functools import lru_cache
from typing import List, Tuple, Optional
from .png_writer import Color


@lru_cache(maxsize=256)
def hex_to_rgba(hex_color: str, alpha: int = 255) -> Color:
    """Convert hex color string to RGBA tuple."""
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return (r, g, b, alpha)


def rgba_to_hex(color: Color) -> str:
    """Convert RGBA tuple to hex string."""
    return f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"


def lerp_color(c1: Color, c2: Color, t: float) -> Color:
    """Linear interpolation between two colors."""
    t = max(0.0, min(1.0, t))
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t),
        int(c1[3] + (c2[3] - c1[3]) * t)
    )


@lru_cache(maxsize=1024)
def rgb_to_hsv(r: int, g: int, b: int) -> Tuple[float, float, float]:
    """Convert RGB to HSV."""
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    mx, mn = max(r, g, b), min(r, g, b)
    v = mx
    d = mx - mn
    s = 0 if mx == 0 else d / mx

    if mx == mn:
        h = 0
    elif mx == r:
        h = (60 * ((g - b) / d) + 360) % 360
    elif mx == g:
        h = (60 * ((b - r) / d) + 120) % 360
    else:
        h = (60 * ((r - g) / d) + 240) % 360

    return (h, s, v)


def hsv_to_rgb(h: float, s: float, v: float) -> Tuple[int, int, int]:
    """Convert HSV to RGB."""
    if s == 0:
        r = g = b = int(v * 255)
        return (r, g, b)

    h = h / 60
    i = int(h)
    f = h - i
    p = v * (1 - s)
    q = v * (1 - s * f)
    t = v * (1 - s * (1 - f))

    if i == 0:
        r, g, b = v, t, p
    elif i == 1:
        r, g, b = q, v, p
    elif i == 2:
        r, g, b = p, v, t
    elif i == 3:
        r, g, b = p, q, v
    elif i == 4:
        r, g, b = t, p, v
    else:
        r, g, b = v, p, q

    return (int(r * 255), int(g * 255), int(b * 255))


def shift_hue(color: Color, degrees: float) -> Color:
    """Shift the hue of a color by degrees."""
    h, s, v = rgb_to_hsv(color[0], color[1], color[2])
    h = (h + degrees) % 360
    r, g, b = hsv_to_rgb(h, s, v)
    return (r, g, b, color[3])


def adjust_saturation(color: Color, factor: float) -> Color:
    """Adjust saturation (factor: 0=grayscale, 1=unchanged, 2=double)."""
    h, s, v = rgb_to_hsv(color[0], color[1], color[2])
    s = max(0.0, min(1.0, s * factor))
    r, g, b = hsv_to_rgb(h, s, v)
    return (r, g, b, color[3])


def adjust_value(color: Color, factor: float) -> Color:
    """Adjust value/brightness."""
    h, s, v = rgb_to_hsv(color[0], color[1], color[2])
    v = max(0.0, min(1.0, v * factor))
    r, g, b = hsv_to_rgb(h, s, v)
    return (r, g, b, color[3])


class Palette:
    """A color palette for pixel art."""

    def __init__(self, colors: List[Color] = None, name: str = "Custom"):
        self.name = name
        self.colors = colors or []

    def add(self, color: Color) -> 'Palette':
        """Add a color to the palette."""
        self.colors.append(color)
        return self

    def add_hex(self, hex_color: str) -> 'Palette':
        """Add a color from hex string."""
        self.colors.append(hex_to_rgba(hex_color))
        return self

    def get(self, index: int) -> Color:
        """Get color at index."""
        return self.colors[index % len(self.colors)]

    def find_nearest(self, color: Color) -> int:
        """Find the index of the nearest color in the palette."""
        min_dist = float('inf')
        nearest_idx = 0

        for i, pal_color in enumerate(self.colors):
            dist = (
                (color[0] - pal_color[0]) ** 2 +
                (color[1] - pal_color[1]) ** 2 +
                (color[2] - pal_color[2]) ** 2
            )
            if dist < min_dist:
                min_dist = dist
                nearest_idx = i

        return nearest_idx

    def quantize(self, color: Color) -> Color:
        """Return the nearest palette color."""
        return self.colors[self.find_nearest(color)]

    def create_ramp(self, start: Color, end: Color, steps: int) -> 'Palette':
        """Create a color ramp between two colors."""
        for i in range(steps):
            t = i / (steps - 1) if steps > 1 else 0
            self.colors.append(lerp_color(start, end, t))
        return self

    def create_hue_ramp(self, base: Color, hue_shift: float, value_range: Tuple[float, float], steps: int) -> 'Palette':
        """Create a ramp with hue shifting (e.g., for hair: pink highlights → purple shadows)."""
        h, s, v = rgb_to_hsv(base[0], base[1], base[2])

        for i in range(steps):
            t = i / (steps - 1) if steps > 1 else 0

            # Shift hue as we go darker
            new_h = (h + hue_shift * t) % 360

            # Interpolate value
            new_v = value_range[0] + (value_range[1] - value_range[0]) * t

            r, g, b = hsv_to_rgb(new_h, s, new_v)
            self.colors.append((r, g, b, 255))

        return self

    def shift_all(self, hue_degrees: float = 0, sat_factor: float = 1.0, val_factor: float = 1.0) -> 'Palette':
        """Return a new palette with all colors shifted."""
        new_colors = []
        for color in self.colors:
            c = color
            if hue_degrees != 0:
                c = shift_hue(c, hue_degrees)
            if sat_factor != 1.0:
                c = adjust_saturation(c, sat_factor)
            if val_factor != 1.0:
                c = adjust_value(c, val_factor)
            new_colors.append(c)
        return Palette(new_colors, f"{self.name}_shifted")

    def __len__(self) -> int:
        return len(self.colors)

    def __iter__(self):
        return iter(self.colors)

    # === Preset Palettes ===

    @classmethod
    def skin_warm(cls) -> 'Palette':
        """Warm skin tones (peach/orange)."""
        return cls([
            hex_to_rgba('#fff0e0'),
            hex_to_rgba('#ffd8b8'),
            hex_to_rgba('#f0c090'),
            hex_to_rgba('#e0a070'),
            hex_to_rgba('#d08050'),
            hex_to_rgba('#b06038'),
        ], "Skin Warm")

    @classmethod
    def skin_cool(cls) -> 'Palette':
        """Cool skin tones (pink/beige)."""
        return cls([
            hex_to_rgba('#fff8f0'),
            hex_to_rgba('#f8e0d8'),
            hex_to_rgba('#e8c8c0'),
            hex_to_rgba('#d8a8a0'),
            hex_to_rgba('#c08880'),
            hex_to_rgba('#986860'),
        ], "Skin Cool")

    @classmethod
    def hair_lavender(cls) -> 'Palette':
        """Lavender/purple hair with hue shift."""
        return cls([
            hex_to_rgba('#fff0f8'),
            hex_to_rgba('#f8e0f0'),
            hex_to_rgba('#e8d0e8'),
            hex_to_rgba('#d8c0e0'),
            hex_to_rgba('#c8a8d8'),
            hex_to_rgba('#b090c8'),
            hex_to_rgba('#9878b8'),
            hex_to_rgba('#8060a8'),
            hex_to_rgba('#685098'),
            hex_to_rgba('#504080'),
            hex_to_rgba('#403068'),
            hex_to_rgba('#302050'),
        ], "Hair Lavender")

    @classmethod
    def hair_brown(cls) -> 'Palette':
        """Brown hair tones."""
        return cls([
            hex_to_rgba('#f0d8c0'),
            hex_to_rgba('#d8b890'),
            hex_to_rgba('#c09868'),
            hex_to_rgba('#987848'),
            hex_to_rgba('#705830'),
            hex_to_rgba('#504020'),
        ], "Hair Brown")

    @classmethod
    def cloth_blue(cls) -> 'Palette':
        """Blue cloth/robe tones."""
        return cls([
            hex_to_rgba('#8090a8'),
            hex_to_rgba('#607898'),
            hex_to_rgba('#506080'),
            hex_to_rgba('#405068'),
            hex_to_rgba('#304058'),
            hex_to_rgba('#203040'),
        ], "Cloth Blue")

    @classmethod
    def metal_gold(cls) -> 'Palette':
        """Gold/brass metal."""
        return cls([
            hex_to_rgba('#f8e8a0'),
            hex_to_rgba('#d8c070'),
            hex_to_rgba('#b89850'),
            hex_to_rgba('#907030'),
            hex_to_rgba('#685020'),
        ], "Metal Gold")

    @classmethod
    def retro_nes(cls) -> 'Palette':
        """NES-inspired limited palette."""
        return cls([
            hex_to_rgba('#000000'),
            hex_to_rgba('#fcfcfc'),
            hex_to_rgba('#f8f8f8'),
            hex_to_rgba('#bcbcbc'),
            hex_to_rgba('#7c7c7c'),
            hex_to_rgba('#a4e4fc'),
            hex_to_rgba('#3cbcfc'),
            hex_to_rgba('#0078f8'),
            hex_to_rgba('#0000fc'),
            hex_to_rgba('#b8f8b8'),
            hex_to_rgba('#58d854'),
            hex_to_rgba('#008200'),
            hex_to_rgba('#f8d8f8'),
            hex_to_rgba('#f878f8'),
            hex_to_rgba('#9878f8'),
            hex_to_rgba('#6844fc'),
        ], "Retro NES")

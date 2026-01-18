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


# === CIE Lab Color Space ===
# Lab provides perceptually uniform color distance

# D65 illuminant reference values
_LAB_REF_X = 95.047
_LAB_REF_Y = 100.0
_LAB_REF_Z = 108.883


def _linear_rgb(c: int) -> float:
    """Convert sRGB component to linear RGB."""
    c_normalized = c / 255.0
    if c_normalized <= 0.04045:
        return c_normalized / 12.92
    return ((c_normalized + 0.055) / 1.055) ** 2.4


def _lab_f(t: float) -> float:
    """Lab conversion helper function."""
    delta = 6 / 29
    if t > delta ** 3:
        return t ** (1 / 3)
    return t / (3 * delta ** 2) + 4 / 29


@lru_cache(maxsize=4096)
def rgb_to_lab(r: int, g: int, b: int) -> Tuple[float, float, float]:
    """Convert RGB to CIE Lab color space.

    Args:
        r, g, b: RGB values (0-255)

    Returns:
        Tuple of (L, a, b) where:
        - L: lightness (0-100)
        - a: green-red axis (-128 to +128)
        - b: blue-yellow axis (-128 to +128)
    """
    # RGB to linear RGB
    lr = _linear_rgb(r)
    lg = _linear_rgb(g)
    lb = _linear_rgb(b)

    # Linear RGB to XYZ (sRGB D65)
    x = (lr * 0.4124564 + lg * 0.3575761 + lb * 0.1804375) * 100
    y = (lr * 0.2126729 + lg * 0.7151522 + lb * 0.0721750) * 100
    z = (lr * 0.0193339 + lg * 0.1191920 + lb * 0.9503041) * 100

    # XYZ to Lab
    fx = _lab_f(x / _LAB_REF_X)
    fy = _lab_f(y / _LAB_REF_Y)
    fz = _lab_f(z / _LAB_REF_Z)

    L = 116 * fy - 16
    a = 500 * (fx - fy)
    b_val = 200 * (fy - fz)

    return (L, a, b_val)


def lab_to_rgb(L: float, a: float, b_val: float) -> Tuple[int, int, int]:
    """Convert CIE Lab to RGB color space.

    Args:
        L: lightness (0-100)
        a: green-red axis
        b_val: blue-yellow axis

    Returns:
        Tuple of (r, g, b) values (0-255)
    """
    # Lab to XYZ
    fy = (L + 16) / 116
    fx = a / 500 + fy
    fz = fy - b_val / 200

    delta = 6 / 29
    delta3 = delta ** 3

    x = _LAB_REF_X * (fx ** 3 if fx ** 3 > delta3 else 3 * delta ** 2 * (fx - 4 / 29))
    y = _LAB_REF_Y * (fy ** 3 if fy ** 3 > delta3 else 3 * delta ** 2 * (fy - 4 / 29))
    z = _LAB_REF_Z * (fz ** 3 if fz ** 3 > delta3 else 3 * delta ** 2 * (fz - 4 / 29))

    # XYZ to linear RGB
    x, y, z = x / 100, y / 100, z / 100
    lr = x * 3.2404542 + y * -1.5371385 + z * -0.4985314
    lg = x * -0.9692660 + y * 1.8760108 + z * 0.0415560
    lb = x * 0.0556434 + y * -0.2040259 + z * 1.0572252

    def to_srgb(c: float) -> int:
        if c <= 0.0031308:
            c = 12.92 * c
        else:
            c = 1.055 * (c ** (1 / 2.4)) - 0.055
        return max(0, min(255, int(c * 255 + 0.5)))

    return (to_srgb(lr), to_srgb(lg), to_srgb(lb))


def rgb_to_lch(r: int, g: int, b: int) -> Tuple[float, float, float]:
    """Convert RGB to CIE LCh color space.

    LCh is Lab in cylindrical coordinates, similar to HSV but perceptually uniform.

    Returns:
        Tuple of (L, C, h) where:
        - L: lightness (0-100)
        - C: chroma (saturation, 0-~180)
        - h: hue angle (0-360)
    """
    L, a, b_val = rgb_to_lab(r, g, b)
    C = math.sqrt(a * a + b_val * b_val)
    h = math.degrees(math.atan2(b_val, a)) % 360
    return (L, C, h)


def lch_to_rgb(L: float, C: float, h: float) -> Tuple[int, int, int]:
    """Convert CIE LCh to RGB."""
    a = C * math.cos(math.radians(h))
    b_val = C * math.sin(math.radians(h))
    return lab_to_rgb(L, a, b_val)


def color_distance_lab(c1: Color, c2: Color) -> float:
    """Calculate perceptually uniform color distance using CIE Lab.

    This distance metric matches human perception better than RGB Euclidean.

    Args:
        c1, c2: RGBA colors to compare

    Returns:
        Delta E distance (0 = identical, ~2.3 = JND, 100+ = very different)
    """
    L1, a1, b1 = rgb_to_lab(c1[0], c1[1], c1[2])
    L2, a2, b2 = rgb_to_lab(c2[0], c2[1], c2[2])

    dL = L1 - L2
    da = a1 - a2
    db = b1 - b2

    return math.sqrt(dL * dL + da * da + db * db)


def color_distance_rgb(c1: Color, c2: Color) -> float:
    """Calculate RGB Euclidean color distance (fast but not perceptually accurate)."""
    dr = c1[0] - c2[0]
    dg = c1[1] - c2[1]
    db = c1[2] - c2[2]
    return math.sqrt(dr * dr + dg * dg + db * db)


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

    def find_nearest_lab(self, color: Color) -> int:
        """Find the index of the nearest color using perceptually uniform Lab distance."""
        min_dist = float('inf')
        nearest_idx = 0

        for i, pal_color in enumerate(self.colors):
            dist = color_distance_lab(color, pal_color)
            if dist < min_dist:
                min_dist = dist
                nearest_idx = i

        return nearest_idx

    def quantize_lab(self, color: Color) -> Color:
        """Return the nearest palette color using perceptually uniform Lab distance."""
        return self.colors[self.find_nearest_lab(color)]

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

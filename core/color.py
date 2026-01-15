"""
Color - Color operations and blend modes for pixel art.

Provides blend modes, color manipulation, and dithering utilities.
All operations work with RGBA tuples (r, g, b, a) where values are 0-255.
"""

from typing import Tuple, List, Optional
import math

# Type alias for RGBA color
Color = Tuple[int, int, int, int]


# =============================================================================
# Color Conversion
# =============================================================================

def hex_to_rgba(hex_color: str, alpha: int = 255) -> Color:
    """Convert hex color string to RGBA tuple.

    Args:
        hex_color: Hex string like '#ff0000' or 'ff0000'
        alpha: Alpha value 0-255

    Returns:
        RGBA tuple
    """
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 8:
        # Has alpha
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        a = int(hex_color[6:8], 16)
        return (r, g, b, a)
    else:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return (r, g, b, alpha)


def rgba_to_hex(color: Color, include_alpha: bool = False) -> str:
    """Convert RGBA tuple to hex string.

    Args:
        color: RGBA tuple
        include_alpha: Whether to include alpha in output

    Returns:
        Hex string like '#ff0000' or '#ff0000ff'
    """
    if include_alpha:
        return f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}{color[3]:02x}"
    return f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"


def rgb_to_hsv(r: int, g: int, b: int) -> Tuple[float, float, float]:
    """Convert RGB to HSV.

    Args:
        r, g, b: RGB values 0-255

    Returns:
        (hue 0-360, saturation 0-1, value 0-1)
    """
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
    """Convert HSV to RGB.

    Args:
        h: Hue 0-360
        s: Saturation 0-1
        v: Value 0-1

    Returns:
        RGB tuple (0-255, 0-255, 0-255)
    """
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


def rgb_to_hsl(r: int, g: int, b: int) -> Tuple[float, float, float]:
    """Convert RGB to HSL.

    Args:
        r, g, b: RGB values 0-255

    Returns:
        (hue 0-360, saturation 0-1, lightness 0-1)
    """
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    mx, mn = max(r, g, b), min(r, g, b)
    l = (mx + mn) / 2.0

    if mx == mn:
        h = s = 0.0
    else:
        d = mx - mn
        s = d / (2.0 - mx - mn) if l > 0.5 else d / (mx + mn)

        if mx == r:
            h = (g - b) / d + (6.0 if g < b else 0.0)
        elif mx == g:
            h = (b - r) / d + 2.0
        else:
            h = (r - g) / d + 4.0
        h *= 60.0

    return (h, s, l)


def hsl_to_rgb(h: float, s: float, l: float) -> Tuple[int, int, int]:
    """Convert HSL to RGB.

    Args:
        h: Hue 0-360
        s: Saturation 0-1
        l: Lightness 0-1

    Returns:
        RGB tuple (0-255, 0-255, 0-255)
    """
    if s == 0:
        v = int(l * 255)
        return (v, v, v)

    def hue_to_rgb(p: float, q: float, t: float) -> float:
        if t < 0:
            t += 1
        if t > 1:
            t -= 1
        if t < 1/6:
            return p + (q - p) * 6 * t
        if t < 1/2:
            return q
        if t < 2/3:
            return p + (q - p) * (2/3 - t) * 6
        return p

    q = l * (1 + s) if l < 0.5 else l + s - l * s
    p = 2 * l - q
    h_norm = h / 360.0

    r = hue_to_rgb(p, q, h_norm + 1/3)
    g = hue_to_rgb(p, q, h_norm)
    b = hue_to_rgb(p, q, h_norm - 1/3)

    return (int(r * 255), int(g * 255), int(b * 255))


# =============================================================================
# Color Interpolation
# =============================================================================

def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation between two values."""
    return a + (b - a) * t


def lerp_color(c1: Color, c2: Color, t: float) -> Color:
    """Linear interpolation between two colors.

    Args:
        c1: First color
        c2: Second color
        t: Interpolation factor 0-1 (clamped)

    Returns:
        Interpolated color
    """
    t = max(0.0, min(1.0, t))
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t),
        int(c1[3] + (c2[3] - c1[3]) * t)
    )


def lerp_color_hsv(c1: Color, c2: Color, t: float) -> Color:
    """Interpolate colors in HSV space (better for hue transitions).

    Args:
        c1: First color
        c2: Second color
        t: Interpolation factor 0-1

    Returns:
        Interpolated color
    """
    t = max(0.0, min(1.0, t))

    h1, s1, v1 = rgb_to_hsv(c1[0], c1[1], c1[2])
    h2, s2, v2 = rgb_to_hsv(c2[0], c2[1], c2[2])

    # Handle hue wrapping (take shortest path)
    h_diff = h2 - h1
    if abs(h_diff) > 180:
        if h_diff > 0:
            h1 += 360
        else:
            h2 += 360

    h = lerp(h1, h2, t) % 360
    s = lerp(s1, s2, t)
    v = lerp(v1, v2, t)
    a = int(lerp(c1[3], c2[3], t))

    r, g, b = hsv_to_rgb(h, s, v)
    return (r, g, b, a)


# =============================================================================
# Color Adjustments
# =============================================================================

def shift_hue(color: Color, degrees: float) -> Color:
    """Shift the hue of a color.

    Args:
        color: Input color
        degrees: Degrees to shift (-360 to 360)

    Returns:
        Color with shifted hue
    """
    h, s, v = rgb_to_hsv(color[0], color[1], color[2])
    h = (h + degrees) % 360
    r, g, b = hsv_to_rgb(h, s, v)
    return (r, g, b, color[3])


def adjust_saturation(color: Color, factor: float) -> Color:
    """Adjust saturation.

    Args:
        color: Input color
        factor: Multiplier (0=grayscale, 1=unchanged, >1=more saturated)

    Returns:
        Adjusted color
    """
    h, s, v = rgb_to_hsv(color[0], color[1], color[2])
    s = max(0.0, min(1.0, s * factor))
    r, g, b = hsv_to_rgb(h, s, v)
    return (r, g, b, color[3])


def adjust_value(color: Color, factor: float) -> Color:
    """Adjust brightness/value.

    Args:
        color: Input color
        factor: Multiplier (0=black, 1=unchanged, >1=brighter)

    Returns:
        Adjusted color
    """
    h, s, v = rgb_to_hsv(color[0], color[1], color[2])
    v = max(0.0, min(1.0, v * factor))
    r, g, b = hsv_to_rgb(h, s, v)
    return (r, g, b, color[3])


def adjust_lightness(color: Color, delta: float) -> Color:
    """Adjust lightness additively.

    Args:
        color: Input color
        delta: Amount to add (-1 to 1)

    Returns:
        Adjusted color
    """
    h, s, l = rgb_to_hsl(color[0], color[1], color[2])
    l = max(0.0, min(1.0, l + delta))
    r, g, b = hsl_to_rgb(h, s, l)
    return (r, g, b, color[3])


def grayscale(color: Color) -> Color:
    """Convert color to grayscale using luminance weights.

    Args:
        color: Input color

    Returns:
        Grayscale color
    """
    # Using perceptual luminance weights
    gray = int(0.299 * color[0] + 0.587 * color[1] + 0.114 * color[2])
    return (gray, gray, gray, color[3])


def invert(color: Color) -> Color:
    """Invert a color.

    Args:
        color: Input color

    Returns:
        Inverted color (alpha unchanged)
    """
    return (255 - color[0], 255 - color[1], 255 - color[2], color[3])


def darken(color: Color, amount: float) -> Color:
    """Darken a color.

    Args:
        color: Input color
        amount: Darkening amount 0-1 (0=unchanged, 1=black)

    Returns:
        Darkened color
    """
    amount = max(0.0, min(1.0, amount))
    return (
        int(color[0] * (1 - amount)),
        int(color[1] * (1 - amount)),
        int(color[2] * (1 - amount)),
        color[3]
    )


def lighten(color: Color, amount: float) -> Color:
    """Lighten a color.

    Args:
        color: Input color
        amount: Lightening amount 0-1 (0=unchanged, 1=white)

    Returns:
        Lightened color
    """
    amount = max(0.0, min(1.0, amount))
    return (
        int(color[0] + (255 - color[0]) * amount),
        int(color[1] + (255 - color[1]) * amount),
        int(color[2] + (255 - color[2]) * amount),
        color[3]
    )


def with_alpha(color: Color, alpha: int) -> Color:
    """Return color with new alpha value.

    Args:
        color: Input color
        alpha: New alpha 0-255

    Returns:
        Color with new alpha
    """
    return (color[0], color[1], color[2], max(0, min(255, alpha)))


def premultiply_alpha(color: Color) -> Color:
    """Premultiply RGB by alpha.

    Args:
        color: Input color

    Returns:
        Premultiplied color
    """
    a = color[3] / 255.0
    return (
        int(color[0] * a),
        int(color[1] * a),
        int(color[2] * a),
        color[3]
    )


# =============================================================================
# Blend Modes
# =============================================================================

def _clamp(v: int) -> int:
    """Clamp value to 0-255."""
    return max(0, min(255, v))


def blend_normal(base: Color, blend: Color) -> Color:
    """Normal alpha blending (Porter-Duff over).

    Args:
        base: Background color
        blend: Foreground color

    Returns:
        Blended color
    """
    if blend[3] == 0:
        return base
    if blend[3] == 255:
        return blend

    alpha = blend[3] / 255.0
    inv_alpha = 1.0 - alpha

    return (
        _clamp(int(blend[0] * alpha + base[0] * inv_alpha)),
        _clamp(int(blend[1] * alpha + base[1] * inv_alpha)),
        _clamp(int(blend[2] * alpha + base[2] * inv_alpha)),
        _clamp(int(blend[3] + base[3] * inv_alpha))
    )


def blend_multiply(base: Color, blend: Color) -> Color:
    """Multiply blend mode - darkens image.

    Args:
        base: Background color
        blend: Foreground color

    Returns:
        Blended color
    """
    alpha = blend[3] / 255.0
    result = (
        _clamp(int((base[0] * blend[0]) / 255)),
        _clamp(int((base[1] * blend[1]) / 255)),
        _clamp(int((base[2] * blend[2]) / 255)),
        base[3]
    )
    return lerp_color(base, result, alpha)


def blend_screen(base: Color, blend: Color) -> Color:
    """Screen blend mode - lightens image.

    Args:
        base: Background color
        blend: Foreground color

    Returns:
        Blended color
    """
    alpha = blend[3] / 255.0
    result = (
        _clamp(255 - ((255 - base[0]) * (255 - blend[0])) // 255),
        _clamp(255 - ((255 - base[1]) * (255 - blend[1])) // 255),
        _clamp(255 - ((255 - base[2]) * (255 - blend[2])) // 255),
        base[3]
    )
    return lerp_color(base, result, alpha)


def blend_overlay(base: Color, blend: Color) -> Color:
    """Overlay blend mode - combines multiply and screen.

    Args:
        base: Background color
        blend: Foreground color

    Returns:
        Blended color
    """
    def overlay_channel(b: int, l: int) -> int:
        if b < 128:
            return _clamp((2 * b * l) // 255)
        else:
            return _clamp(255 - (2 * (255 - b) * (255 - l)) // 255)

    alpha = blend[3] / 255.0
    result = (
        overlay_channel(base[0], blend[0]),
        overlay_channel(base[1], blend[1]),
        overlay_channel(base[2], blend[2]),
        base[3]
    )
    return lerp_color(base, result, alpha)


def blend_soft_light(base: Color, blend: Color) -> Color:
    """Soft light blend mode - gentler than overlay.

    Args:
        base: Background color
        blend: Foreground color

    Returns:
        Blended color
    """
    def soft_light_channel(b: int, l: int) -> int:
        b_n, l_n = b / 255.0, l / 255.0
        if l_n < 0.5:
            result = b_n - (1 - 2 * l_n) * b_n * (1 - b_n)
        else:
            if b_n < 0.25:
                d = ((16 * b_n - 12) * b_n + 4) * b_n
            else:
                d = math.sqrt(b_n)
            result = b_n + (2 * l_n - 1) * (d - b_n)
        return _clamp(int(result * 255))

    alpha = blend[3] / 255.0
    result = (
        soft_light_channel(base[0], blend[0]),
        soft_light_channel(base[1], blend[1]),
        soft_light_channel(base[2], blend[2]),
        base[3]
    )
    return lerp_color(base, result, alpha)


def blend_hard_light(base: Color, blend: Color) -> Color:
    """Hard light blend mode - like overlay but inverted.

    Args:
        base: Background color
        blend: Foreground color

    Returns:
        Blended color
    """
    def hard_light_channel(b: int, l: int) -> int:
        if l < 128:
            return _clamp((2 * b * l) // 255)
        else:
            return _clamp(255 - (2 * (255 - b) * (255 - l)) // 255)

    alpha = blend[3] / 255.0
    result = (
        hard_light_channel(base[0], blend[0]),
        hard_light_channel(base[1], blend[1]),
        hard_light_channel(base[2], blend[2]),
        base[3]
    )
    return lerp_color(base, result, alpha)


def blend_color_dodge(base: Color, blend: Color) -> Color:
    """Color dodge blend mode - brightens and increases contrast.

    Args:
        base: Background color
        blend: Foreground color

    Returns:
        Blended color
    """
    def dodge_channel(b: int, l: int) -> int:
        if l == 255:
            return 255
        return _clamp((b * 255) // (255 - l))

    alpha = blend[3] / 255.0
    result = (
        dodge_channel(base[0], blend[0]),
        dodge_channel(base[1], blend[1]),
        dodge_channel(base[2], blend[2]),
        base[3]
    )
    return lerp_color(base, result, alpha)


def blend_color_burn(base: Color, blend: Color) -> Color:
    """Color burn blend mode - darkens and increases contrast.

    Args:
        base: Background color
        blend: Foreground color

    Returns:
        Blended color
    """
    def burn_channel(b: int, l: int) -> int:
        if l == 0:
            return 0
        return _clamp(255 - ((255 - b) * 255) // l)

    alpha = blend[3] / 255.0
    result = (
        burn_channel(base[0], blend[0]),
        burn_channel(base[1], blend[1]),
        burn_channel(base[2], blend[2]),
        base[3]
    )
    return lerp_color(base, result, alpha)


def blend_add(base: Color, blend: Color) -> Color:
    """Additive blend mode - used for glows and highlights.

    Args:
        base: Background color
        blend: Foreground color

    Returns:
        Blended color
    """
    alpha = blend[3] / 255.0
    result = (
        _clamp(int(base[0] + blend[0] * alpha)),
        _clamp(int(base[1] + blend[1] * alpha)),
        _clamp(int(base[2] + blend[2] * alpha)),
        base[3]
    )
    return result


def blend_subtract(base: Color, blend: Color) -> Color:
    """Subtractive blend mode.

    Args:
        base: Background color
        blend: Foreground color

    Returns:
        Blended color
    """
    alpha = blend[3] / 255.0
    result = (
        _clamp(int(base[0] - blend[0] * alpha)),
        _clamp(int(base[1] - blend[1] * alpha)),
        _clamp(int(base[2] - blend[2] * alpha)),
        base[3]
    )
    return result


def blend_difference(base: Color, blend: Color) -> Color:
    """Difference blend mode - shows difference between colors.

    Args:
        base: Background color
        blend: Foreground color

    Returns:
        Blended color
    """
    alpha = blend[3] / 255.0
    result = (
        abs(base[0] - blend[0]),
        abs(base[1] - blend[1]),
        abs(base[2] - blend[2]),
        base[3]
    )
    return lerp_color(base, result, alpha)


# Blend mode lookup for string-based access
BLEND_MODES = {
    'normal': blend_normal,
    'multiply': blend_multiply,
    'screen': blend_screen,
    'overlay': blend_overlay,
    'soft_light': blend_soft_light,
    'hard_light': blend_hard_light,
    'color_dodge': blend_color_dodge,
    'color_burn': blend_color_burn,
    'add': blend_add,
    'subtract': blend_subtract,
    'difference': blend_difference,
}


def blend(base: Color, blend_color: Color, mode: str = 'normal') -> Color:
    """Blend two colors using specified mode.

    Args:
        base: Background color
        blend_color: Foreground color
        mode: Blend mode name

    Returns:
        Blended color
    """
    blend_func = BLEND_MODES.get(mode, blend_normal)
    return blend_func(base, blend_color)


# =============================================================================
# Dithering
# =============================================================================

# Bayer 2x2 dither matrix (values 0-3)
BAYER_2X2 = [
    [0, 2],
    [3, 1]
]

# Bayer 4x4 dither matrix (values 0-15)
BAYER_4X4 = [
    [0,  8,  2, 10],
    [12, 4, 14,  6],
    [3, 11,  1,  9],
    [15, 7, 13,  5]
]

# Bayer 8x8 dither matrix (values 0-63)
BAYER_8X8 = [
    [0,  32,  8, 40,  2, 34, 10, 42],
    [48, 16, 56, 24, 50, 18, 58, 26],
    [12, 44,  4, 36, 14, 46,  6, 38],
    [60, 28, 52, 20, 62, 30, 54, 22],
    [3,  35, 11, 43,  1, 33,  9, 41],
    [51, 19, 59, 27, 49, 17, 57, 25],
    [15, 47,  7, 39, 13, 45,  5, 37],
    [63, 31, 55, 23, 61, 29, 53, 21]
]


def dither_threshold(x: int, y: int, pattern: str = 'bayer4x4') -> float:
    """Get dither threshold for a pixel position.

    Args:
        x, y: Pixel coordinates
        pattern: 'bayer2x2', 'bayer4x4', 'bayer8x8', or 'checker'

    Returns:
        Threshold value 0-1
    """
    if pattern == 'checker':
        return 0.5 if (x + y) % 2 == 0 else 0.0
    elif pattern == 'bayer2x2':
        matrix = BAYER_2X2
        return matrix[y % 2][x % 2] / 4.0
    elif pattern == 'bayer8x8':
        matrix = BAYER_8X8
        return matrix[y % 8][x % 8] / 64.0
    else:  # bayer4x4
        matrix = BAYER_4X4
        return matrix[y % 4][x % 4] / 16.0


def dither_color(c1: Color, c2: Color, x: int, y: int,
                 ratio: float, pattern: str = 'bayer4x4') -> Color:
    """Choose between two colors using dithering.

    Args:
        c1: First color
        c2: Second color
        x, y: Pixel coordinates
        ratio: Blend ratio 0-1 (0=c1, 1=c2)
        pattern: Dither pattern name

    Returns:
        One of the two colors based on dither threshold
    """
    threshold = dither_threshold(x, y, pattern)
    return c2 if ratio > threshold else c1


def quantize_with_dither(color: Color, palette: List[Color],
                         x: int, y: int, pattern: str = 'bayer4x4') -> Color:
    """Quantize color to palette with dithering.

    Finds the two nearest palette colors and dithers between them.

    Args:
        color: Input color
        palette: List of palette colors
        x, y: Pixel coordinates (for dither pattern)
        pattern: Dither pattern name

    Returns:
        Quantized color from palette
    """
    if len(palette) == 0:
        return color
    if len(palette) == 1:
        return palette[0]

    # Find two nearest colors
    distances = []
    for i, pal_color in enumerate(palette):
        dist = (
            (color[0] - pal_color[0]) ** 2 +
            (color[1] - pal_color[1]) ** 2 +
            (color[2] - pal_color[2]) ** 2
        )
        distances.append((dist, i))

    distances.sort(key=lambda x: x[0])

    c1_idx = distances[0][1]
    c2_idx = distances[1][1] if len(distances) > 1 else c1_idx

    c1 = palette[c1_idx]
    c2 = palette[c2_idx]

    d1 = math.sqrt(distances[0][0])
    d2 = math.sqrt(distances[1][0]) if len(distances) > 1 else d1

    total = d1 + d2
    if total == 0:
        return c1

    ratio = d1 / total  # How much of c2 to use

    return dither_color(c1, c2, x, y, ratio, pattern)


# =============================================================================
# Color Distance and Comparison
# =============================================================================

def color_distance_rgb(c1: Color, c2: Color) -> float:
    """Euclidean distance between two colors in RGB space.

    Args:
        c1: First color
        c2: Second color

    Returns:
        Distance (0 to ~441.67)
    """
    return math.sqrt(
        (c1[0] - c2[0]) ** 2 +
        (c1[1] - c2[1]) ** 2 +
        (c1[2] - c2[2]) ** 2
    )


def color_distance_weighted(c1: Color, c2: Color) -> float:
    """Perceptually weighted color distance.

    Uses weights based on human color perception.

    Args:
        c1: First color
        c2: Second color

    Returns:
        Weighted distance
    """
    # Weights based on human perception (red-green more sensitive)
    rmean = (c1[0] + c2[0]) / 2.0
    dr = c1[0] - c2[0]
    dg = c1[1] - c2[1]
    db = c1[2] - c2[2]

    return math.sqrt(
        (2 + rmean/256) * dr*dr +
        4 * dg*dg +
        (2 + (255-rmean)/256) * db*db
    )


def colors_similar(c1: Color, c2: Color, threshold: float = 30.0) -> bool:
    """Check if two colors are similar.

    Args:
        c1: First color
        c2: Second color
        threshold: Maximum distance to be considered similar

    Returns:
        True if colors are similar
    """
    return color_distance_rgb(c1, c2) < threshold


# =============================================================================
# Utility Functions
# =============================================================================

def color_to_float(color: Color) -> Tuple[float, float, float, float]:
    """Convert 0-255 color to 0-1 floats.

    Args:
        color: RGBA tuple 0-255

    Returns:
        RGBA tuple 0-1
    """
    return (color[0]/255.0, color[1]/255.0, color[2]/255.0, color[3]/255.0)


def float_to_color(color: Tuple[float, float, float, float]) -> Color:
    """Convert 0-1 floats to 0-255 color.

    Args:
        color: RGBA tuple 0-1

    Returns:
        RGBA tuple 0-255
    """
    return (
        _clamp(int(color[0] * 255)),
        _clamp(int(color[1] * 255)),
        _clamp(int(color[2] * 255)),
        _clamp(int(color[3] * 255))
    )


# Common color constants
TRANSPARENT = (0, 0, 0, 0)
BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 255)
RED = (255, 0, 0, 255)
GREEN = (0, 255, 0, 255)
BLUE = (0, 0, 255, 255)
YELLOW = (255, 255, 0, 255)
CYAN = (0, 255, 255, 255)
MAGENTA = (255, 0, 255, 255)

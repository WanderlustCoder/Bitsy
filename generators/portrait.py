"""
Portrait Generator - Creates detailed portrait sprites.

Produces high-quality pixel art portraits with:
- Detailed hair clusters (bezier-based strands)
- Multi-layer eyes with catchlights
- Nuanced facial features (nose, lips)
- Hue-shifted shading ramps
- Accessories support (glasses, jewelry)

Target quality: Professional pixel art comparable to UserExamples/HighRes.png
"""

import random
import math
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.canvas import Canvas
from core.color import Color
from core.palette import Palette, rgb_to_lch, lch_to_rgb, rgb_to_hsv, hsv_to_rgb


class HairStyle(Enum):
    """Available hair styles."""
    WAVY = "wavy"
    STRAIGHT = "straight"
    CURLY = "curly"
    SHORT = "short"
    PONYTAIL = "ponytail"
    BRAIDED = "braided"
    LONG = "long"
    BUN = "bun"


class EyeShape(Enum):
    """Eye shape variants."""
    ROUND = "round"
    ALMOND = "almond"
    DROOPY = "droopy"
    SHARP = "sharp"


class NoseType(Enum):
    """Nose shape variants."""
    SMALL = "small"
    BUTTON = "button"
    POINTED = "pointed"
    WIDE = "wide"


class LipShape(Enum):
    """Lip shape variants."""
    THIN = "thin"
    FULL = "full"
    HEART = "heart"
    NEUTRAL = "neutral"


@dataclass
class PortraitConfig:
    """Configuration for portrait generation."""

    # Canvas size
    width: int = 128
    height: int = 160

    # Random seed
    seed: Optional[int] = None

    # Skin
    skin_tone: str = "light"  # light, medium, tan, dark, pale

    # Hair
    hair_style: HairStyle = HairStyle.WAVY
    hair_color: str = "brown"  # brown, black, blonde, red, gray, etc.
    hair_length: float = 1.0  # 0.5 = short, 1.0 = medium, 1.5 = long

    # Face
    face_shape: str = "oval"  # oval, round, heart, square
    eye_shape: EyeShape = EyeShape.ROUND
    eye_color: str = "brown"
    nose_type: NoseType = NoseType.SMALL
    lip_shape: LipShape = LipShape.NEUTRAL
    lip_color: str = "natural"

    # Expression
    expression: str = "neutral"  # neutral, happy, sad, surprised, etc.
    eye_openness: float = 1.0  # 0.0 = closed, 1.0 = fully open
    gaze_direction: Tuple[float, float] = (0.0, 0.0)  # pupil offset

    # Eyebrows
    eyebrow_arch: float = 0.3  # 0.0 to 1.0, controls arch height
    eyebrow_angle: float = 0.0  # -0.5 to 0.5, negative=sad, positive=angry

    # Accessories
    has_glasses: bool = False
    glasses_style: str = "round"
    has_earrings: bool = False
    earring_style: str = "stud"
    has_facial_hair: bool = False
    facial_hair_style: str = "none"
    facial_hair_color: Optional[str] = None  # None = use hair color

    # Clothing
    clothing_style: str = "casual"
    clothing_color: str = "blue"

    # Lighting
    light_direction: Tuple[float, float] = (1.0, -1.0)  # (x, y) normalized

    # Quality
    shading_levels: int = 7  # Number of colors in shading ramps

    # Background
    background_color: Optional[Tuple] = None  # None=transparent, RGB tuple, or (top, bottom) for gradient
    vignette_strength: float = 0.0  # 0.0-1.0, darkens edges/corners

    # Framing
    show_shoulders: bool = True  # Show shoulders extending from clothing

    # Color
    color_vibrancy: float = 1.0  # 0.5-1.5, affects color saturation


# Skin tone palettes (base colors for ramp generation)
SKIN_TONES = {
    "pale": (255, 230, 220),
    "light": (255, 220, 200),
    "medium": (230, 185, 150),
    "tan": (210, 160, 120),
    "olive": (195, 165, 130),
    "brown": (165, 120, 85),
    "dark": (120, 80, 55),
}

# Hair color base values
HAIR_COLORS = {
    "black": (30, 25, 25),
    "dark_brown": (60, 45, 35),
    "brown": (100, 70, 50),
    "light_brown": (140, 100, 70),
    "auburn": (130, 60, 40),
    "red": (160, 60, 45),
    "ginger": (190, 100, 60),
    "blonde": (210, 180, 130),
    "platinum": (230, 220, 200),
    "gray": (150, 150, 155),
    "white": (240, 240, 245),
    "blue": (60, 80, 140),
    "purple": (100, 60, 120),
    "pink": (200, 120, 150),
    "green": (70, 120, 80),
}

# Eye color base values
EYE_COLORS = {
    "brown": (100, 60, 40),
    "dark_brown": (60, 35, 25),
    "hazel": (140, 100, 60),
    "green": (80, 130, 80),
    "blue": (70, 120, 170),
    "gray": (130, 140, 150),
    "amber": (180, 130, 60),
    "violet": (120, 80, 150),
}


def create_portrait_ramp(base_color: Color, levels: int = 7,
                         highlight_hue_shift: float = 18.0,
                         shadow_hue_shift: float = -25.0) -> List[Color]:
    """
    Generate a hue-shifted color ramp for portrait shading.

    Creates perceptually uniform ramp using LCh color space with:
    - Highlights shifted toward warm (yellow/orange)
    - Shadows shifted toward cool (blue/purple)
    - Saturation peaks in midtones, decreases at extremes

    Args:
        base_color: Middle color of the ramp (RGB tuple or RGBA)
        levels: Number of colors in ramp (odd numbers recommended)
        highlight_hue_shift: Degrees to shift highlights (+ve = warm)
        shadow_hue_shift: Degrees to shift shadows (-ve = cool)

    Returns:
        List of colors from darkest to lightest
    """
    r, g, b = base_color[0], base_color[1], base_color[2]
    alpha = base_color[3] if len(base_color) > 3 else 255

    # Convert to LCh for perceptually uniform manipulation
    L, C, h = rgb_to_lch(r, g, b)

    colors = []
    mid = levels // 2

    for i in range(levels):
        # Position in ramp: -1.0 (darkest) to +1.0 (lightest)
        t = (i - mid) / mid if mid > 0 else 0

        # Lightness: smooth curve from dark to light
        # Use a slight S-curve for more natural look
        if t < 0:
            # Shadows: compress more
            new_L = L + t * L * 0.7
        else:
            # Highlights: expand toward white
            new_L = L + t * (100 - L) * 0.6

        new_L = max(5, min(98, new_L))

        # Hue shift: interpolate between shadow and highlight shifts
        if t < 0:
            hue_shift = shadow_hue_shift * abs(t)
        else:
            hue_shift = highlight_hue_shift * t

        new_h = (h + hue_shift) % 360

        # Saturation: peak in midtones, reduce at extremes
        # This prevents oversaturated highlights and muddy shadows
        sat_factor = 1.0 - 0.3 * (t ** 2)
        new_C = C * sat_factor

        # Desaturate shadows slightly more
        if t < -0.5:
            new_C *= 0.85

        # Convert back to RGB
        try:
            nr, ng, nb = lch_to_rgb(new_L, new_C, new_h)
            colors.append((nr, ng, nb, alpha))
        except ValueError:
            # Fallback if out of gamut
            colors.append((r, g, b, alpha))

    return colors


def create_hair_ramp(base_color: Color, levels: int = 6) -> List[Color]:
    """
    Generate a specialized ramp for hair rendering.

    Hair needs:
    - More contrast between highlight and shadow
    - Subtle warm shift in highlights (simulates subsurface scattering)
    - Cooler, less saturated shadows

    Args:
        base_color: Base hair color
        levels: Number of colors (6 recommended for hair)

    Returns:
        List of colors from darkest to lightest
    """
    return create_portrait_ramp(
        base_color,
        levels=levels,
        highlight_hue_shift=12.0,  # Less shift for natural look
        shadow_hue_shift=-15.0,
    )


def create_skin_ramp(base_color: Color, levels: int = 7) -> List[Color]:
    """
    Generate a specialized ramp for skin rendering.

    Skin needs:
    - Warm highlights (subsurface scattering)
    - Cooler shadows with slight desaturation
    - Extra red in midtones for lifelike appearance

    Args:
        base_color: Base skin tone
        levels: Number of colors

    Returns:
        List of colors from darkest to lightest
    """
    r, g, b = base_color[0], base_color[1], base_color[2]
    alpha = base_color[3] if len(base_color) > 3 else 255

    L, C, h = rgb_to_lch(r, g, b)

    colors = []
    mid = levels // 2

    for i in range(levels):
        t = (i - mid) / mid if mid > 0 else 0

        # Lightness curve
        if t < 0:
            new_L = L + t * L * 0.6
        else:
            new_L = L + t * (100 - L) * 0.5

        new_L = max(15, min(95, new_L))

        # Hue shift: warm highlights, cool shadows
        if t < 0:
            hue_shift = -20 * abs(t)  # Blue shift in shadows
        else:
            hue_shift = 15 * t  # Yellow/orange shift in highlights

        new_h = (h + hue_shift) % 360

        # Saturation: boost slightly in midtones for healthy look
        if abs(t) < 0.5:
            sat_factor = 1.1
        else:
            sat_factor = 1.0 - 0.2 * abs(t)

        new_C = C * sat_factor

        try:
            nr, ng, nb = lch_to_rgb(new_L, new_C, new_h)
            colors.append((nr, ng, nb, alpha))
        except ValueError:
            colors.append((r, g, b, alpha))

    return colors


def create_eye_ramp(base_color: Color, levels: int = 5) -> List[Color]:
    """
    Generate a ramp for iris rendering.

    Eyes need:
    - Dark outer edge
    - Lighter center with subtle radial gradient
    - Slight color variation for depth

    Args:
        base_color: Iris base color
        levels: Number of colors

    Returns:
        List of colors from outer (dark) to inner (light)
    """
    return create_portrait_ramp(
        base_color,
        levels=levels,
        highlight_hue_shift=10.0,
        shadow_hue_shift=-10.0,
    )


class PortraitGenerator:
    """
    Generates detailed portrait sprites.

    Usage:
        gen = PortraitGenerator(width=128, height=160, seed=42)
        gen.set_skin("light")
        gen.set_hair(HairStyle.WAVY, "brown")
        gen.set_eyes(EyeShape.ROUND, "blue")

        portrait = gen.render()
        portrait.save("portrait.png")
    """

    def __init__(self, width: int = 128, height: int = 160,
                 seed: Optional[int] = None):
        """
        Initialize portrait generator.

        Args:
            width: Canvas width (default 128)
            height: Canvas height (default 160)
            seed: Random seed for reproducible generation
        """
        self.config = PortraitConfig(width=width, height=height, seed=seed)
        self.rng = random.Random(seed)

        # Pre-computed color ramps (populated during render)
        self._skin_ramp: List[Color] = []
        self._hair_ramp: List[Color] = []
        self._eye_ramp: List[Color] = []
        self._lip_ramp: List[Color] = []

    def set_skin(self, tone: str) -> 'PortraitGenerator':
        """Set skin tone."""
        self.config.skin_tone = tone
        return self

    def set_hair(self, style: HairStyle, color: str,
                 length: float = 1.0) -> 'PortraitGenerator':
        """Set hair style and color."""
        self.config.hair_style = style
        self.config.hair_color = color
        self.config.hair_length = length
        return self

    def set_eyes(self, shape: EyeShape, color: str,
                 openness: float = 1.0) -> 'PortraitGenerator':
        """Set eye shape and color."""
        self.config.eye_shape = shape
        self.config.eye_color = color
        self.config.eye_openness = openness
        return self

    def set_nose(self, nose_type: NoseType) -> 'PortraitGenerator':
        """Set nose type."""
        self.config.nose_type = nose_type
        return self

    def set_lips(self, shape: LipShape, color: str = "natural") -> 'PortraitGenerator':
        """Set lip shape and color."""
        self.config.lip_shape = shape
        self.config.lip_color = color
        return self

    def set_expression(self, expression: str,
                       gaze: Optional[Tuple[float, float]] = None) -> 'PortraitGenerator':
        """Set facial expression with automatic eye/gaze adjustments.

        Expression presets:
        - neutral: Normal eyes, centered gaze
        - happy: Slightly squinted, upward gaze hint
        - sad: Droopy, downward gaze
        - surprised: Wide eyes, centered gaze
        - angry: Narrowed eyes, direct gaze
        - sleepy: Half-closed eyes, downward gaze
        - wink: One eye closed (left)
        """
        self.config.expression = expression

        # Expression presets: (eye_openness, gaze, eyebrow_arch, eyebrow_angle)
        presets = {
            "neutral": (1.0, (0.0, 0.0), 0.3, 0.0),
            "happy": (0.85, (0.0, -0.1), 0.4, 0.1),  # Raised, slight angle up
            "sad": (0.9, (0.0, 0.2), 0.5, -0.25),  # High arch, sad angle
            "surprised": (1.2, (0.0, 0.0), 0.6, 0.0),  # Raised eyebrows
            "angry": (0.75, (0.0, 0.0), 0.15, 0.35),  # Low, angry angle
            "sleepy": (0.5, (0.0, 0.15), 0.2, -0.1),  # Relaxed
            "wink": (0.9, (0.1, 0.0), 0.35, 0.1),
        }

        if expression.lower() in presets:
            openness, default_gaze, arch, angle = presets[expression.lower()]
            self.config.eye_openness = openness
            self.config.gaze_direction = gaze if gaze is not None else default_gaze
            self.config.eyebrow_arch = arch
            self.config.eyebrow_angle = angle
        else:
            self.config.gaze_direction = gaze if gaze is not None else (0.0, 0.0)

        return self

    def set_eyebrows(self, arch: float = 0.3, angle: float = 0.0) -> 'PortraitGenerator':
        """Set eyebrow shape.

        Args:
            arch: Arch height (0.0-1.0, default 0.3)
            angle: Angle tilt (-0.5 to 0.5, negative=sad, positive=angry)
        """
        self.config.eyebrow_arch = max(0.0, min(1.0, arch))
        self.config.eyebrow_angle = max(-0.5, min(0.5, angle))
        return self

    def set_glasses(self, style: str = "round") -> 'PortraitGenerator':
        """Add glasses."""
        self.config.has_glasses = True
        self.config.glasses_style = style
        return self

    def set_earrings(self, style: str = "stud") -> 'PortraitGenerator':
        """Add earrings."""
        self.config.has_earrings = True
        self.config.earring_style = style
        return self

    def set_facial_hair(self, style: str = "stubble",
                        color: Optional[str] = None) -> 'PortraitGenerator':
        """
        Add facial hair.

        Args:
            style: One of 'stubble', 'mustache', 'goatee', 'short_beard', 'full_beard'
            color: Hair color (defaults to hair color if not specified)
        """
        self.config.has_facial_hair = True
        self.config.facial_hair_style = style
        self.config.facial_hair_color = color
        return self

    def set_clothing(self, style: str, color: str) -> 'PortraitGenerator':
        """Set clothing style and color."""
        self.config.clothing_style = style
        self.config.clothing_color = color
        return self

    def set_lighting(self, direction: Tuple[float, float]) -> 'PortraitGenerator':
        """Set light direction (x, y) - normalized."""
        # Normalize
        mag = math.sqrt(direction[0]**2 + direction[1]**2)
        if mag > 0:
            self.config.light_direction = (direction[0]/mag, direction[1]/mag)
        return self

    def set_background(self, color: Optional[Tuple] = None,
                       gradient: Optional[Tuple[Tuple, Tuple]] = None) -> 'PortraitGenerator':
        """
        Set background color or gradient.

        Args:
            color: RGB tuple for solid color, or None for transparent
            gradient: Tuple of (top_color, bottom_color) for vertical gradient

        Examples:
            set_background(color=(30, 30, 50))  # Dark blue solid
            set_background(gradient=((20, 20, 40), (40, 40, 80)))  # Dark gradient
        """
        if gradient:
            self.config.background_color = gradient
        else:
            self.config.background_color = color
        return self

    def set_framing(self, show_shoulders: bool = True) -> 'PortraitGenerator':
        """Set framing options."""
        self.config.show_shoulders = show_shoulders
        return self

    def set_vignette(self, strength: float = 0.5) -> 'PortraitGenerator':
        """Set vignette strength (0.0-1.0)."""
        self.config.vignette_strength = max(0.0, min(1.0, strength))
        return self

    def set_vibrancy(self, factor: float = 1.0) -> 'PortraitGenerator':
        """Set color vibrancy/saturation (0.5-1.5)."""
        self.config.color_vibrancy = max(0.5, min(1.5, factor))
        return self

    def _prepare_ramps(self) -> None:
        """Pre-compute color ramps based on configuration."""
        # Skin ramp
        skin_base = SKIN_TONES.get(self.config.skin_tone, SKIN_TONES["light"])
        self._skin_ramp = create_skin_ramp(
            (*skin_base, 255),
            levels=self.config.shading_levels
        )

        # Hair ramp
        hair_base = HAIR_COLORS.get(self.config.hair_color, HAIR_COLORS["brown"])
        self._hair_ramp = create_hair_ramp(
            (*hair_base, 255),
            levels=6
        )

        # Eye ramp
        eye_base = EYE_COLORS.get(self.config.eye_color, EYE_COLORS["brown"])
        self._eye_ramp = create_eye_ramp(
            (*eye_base, 255),
            levels=5
        )

        # Lip ramp - derived from skin with slight red shift
        if self.config.lip_color == "natural":
            lip_base = skin_base
            # Shift toward red/pink
            lip_base = (
                min(255, lip_base[0] + 30),
                max(0, lip_base[1] - 20),
                max(0, lip_base[2] - 10)
            )
        else:
            lip_base = skin_base  # Could add custom lip colors later

        self._lip_ramp = create_portrait_ramp(
            (*lip_base, 255),
            levels=5
        )

        # Apply vibrancy adjustment if not default
        vibrancy = getattr(self.config, 'color_vibrancy', 1.0)
        if vibrancy != 1.0:
            self._skin_ramp = self._adjust_ramp_vibrancy(self._skin_ramp, vibrancy)
            self._hair_ramp = self._adjust_ramp_vibrancy(self._hair_ramp, vibrancy)
            self._eye_ramp = self._adjust_ramp_vibrancy(self._eye_ramp, vibrancy)
            self._lip_ramp = self._adjust_ramp_vibrancy(self._lip_ramp, vibrancy)

    def _adjust_ramp_vibrancy(self, ramp: List[Color], factor: float) -> List[Color]:
        """Adjust saturation of all colors in a ramp."""
        result = []
        for color in ramp:
            r, g, b = color[0], color[1], color[2]
            alpha = color[3] if len(color) > 3 else 255

            # Convert RGB to HSV
            max_c = max(r, g, b)
            min_c = min(r, g, b)
            diff = max_c - min_c

            # Value
            v = max_c

            # Saturation
            s = 0 if max_c == 0 else (diff / max_c) * 255

            # Apply vibrancy to saturation
            s = min(255, int(s * factor))

            # Convert back to RGB
            if s == 0:
                nr, ng, nb = v, v, v
            else:
                # Hue calculation
                if max_c == r:
                    h = 60 * ((g - b) / diff % 6) if diff > 0 else 0
                elif max_c == g:
                    h = 60 * ((b - r) / diff + 2) if diff > 0 else 0
                else:
                    h = 60 * ((r - g) / diff + 4) if diff > 0 else 0

                # HSV to RGB
                s_norm = s / 255
                c = v * s_norm
                x = c * (1 - abs((h / 60) % 2 - 1))
                m = v - c

                if h < 60:
                    nr, ng, nb = c + m, x + m, m
                elif h < 120:
                    nr, ng, nb = x + m, c + m, m
                elif h < 180:
                    nr, ng, nb = m, c + m, x + m
                elif h < 240:
                    nr, ng, nb = m, x + m, c + m
                elif h < 300:
                    nr, ng, nb = x + m, m, c + m
                else:
                    nr, ng, nb = c + m, m, x + m

                nr, ng, nb = int(nr), int(ng), int(nb)

            result.append((max(0, min(255, nr)), max(0, min(255, ng)),
                          max(0, min(255, nb)), alpha))
        return result

    def _get_face_center(self) -> Tuple[int, int]:
        """Calculate face center position."""
        cx = self.config.width // 2
        cy = int(self.config.height * 0.45)  # Face slightly above center
        return cx, cy

    def _get_face_dimensions(self) -> Tuple[int, int]:
        """Calculate face width and height."""
        # Face takes about 60% of width, 50% of height
        fw = int(self.config.width * 0.6)
        fh = int(self.config.height * 0.5)
        return fw, fh

    def _render_face_base(self, canvas: Canvas) -> None:
        """Render the base face shape with gradient shading."""
        cx, cy = self._get_face_center()
        fw, fh = self._get_face_dimensions()
        rx, ry = fw // 2, fh // 2

        # Light direction
        lx, ly = self.config.light_direction
        light_len = (lx * lx + ly * ly) ** 0.5
        if light_len > 0:
            lx, ly = lx / light_len, ly / light_len

        # Skin ramp indices
        ramp_len = len(self._skin_ramp)
        mid_idx = ramp_len // 2

        # Per-pixel gradient shading
        for y in range(cy - ry - 1, cy + ry + 2):
            for x in range(cx - rx - 1, cx + rx + 2):
                # Check if inside ellipse
                dx = (x - cx) / rx if rx > 0 else 0
                dy = (y - cy) / ry if ry > 0 else 0
                dist_sq = dx * dx + dy * dy

                if dist_sq > 1.0:
                    continue

                # Calculate shading based on surface normal approximation
                # Normal points outward from ellipse center
                nx = dx
                ny = dy
                nlen = (nx * nx + ny * ny) ** 0.5
                if nlen > 0:
                    nx, ny = nx / nlen, ny / nlen
                else:
                    nx, ny = 0, -1  # Top faces light

                # Dot product with light direction (inverted for surface facing)
                # Light comes FROM lx,ly direction, surface faces -normal
                dot = -(nx * lx + ny * ly)

                # Map dot product to ramp index
                # dot ranges from -1 (facing away) to 1 (facing light)
                # Add vertical bias (top is lighter)
                vertical_bias = -dy * 0.3
                shading = (dot + vertical_bias + 1.0) / 2.0  # Map to 0-1
                shading = max(0.0, min(1.0, shading))

                # Select color from ramp
                ramp_idx = int(shading * (ramp_len - 1))
                ramp_idx = max(0, min(ramp_len - 1, ramp_idx))
                color = self._skin_ramp[ramp_idx]

                # Apply warm/cool temperature shift
                r, g, b = color[0], color[1], color[2]
                if shading > 0.6:
                    # Highlights: warm shift (more orange/yellow)
                    warmth = (shading - 0.6) / 0.4
                    r = min(255, int(r + warmth * 8))
                    g = min(255, int(g + warmth * 4))
                elif shading < 0.4:
                    # Shadows: cool shift (more blue/purple)
                    coolness = (0.4 - shading) / 0.4
                    r = max(0, int(r - coolness * 5))
                    b = min(255, int(b + coolness * 8))

                # Anti-aliasing at edges
                alpha = 255
                if dist_sq > 0.85:
                    edge_factor = (1.0 - dist_sq) / 0.15
                    alpha = int(255 * max(0, min(1, edge_factor)))

                if alpha > 0:
                    final_color = (r, g, b, alpha)
                    canvas.set_pixel(x, y, final_color)

        # Add subtle nose shadow
        self._render_nose_shadow(canvas)

        # Add optional cheek blush
        self._render_cheek_blush(canvas)

    def _render_nose_shadow(self, canvas: Canvas) -> None:
        """Render subtle nose shadow for depth."""
        cx, cy = self._get_face_center()
        fw, fh = self._get_face_dimensions()

        # Nose position
        nose_y = cy + fh // 10
        lx, _ = self.config.light_direction

        # Shadow on opposite side of light
        shadow_x = cx + (3 if lx < 0 else -3)
        shadow_color = self._skin_ramp[1]  # Dark shade

        # Small shadow stroke
        for dy in range(-2, 4):
            alpha = 60 - abs(dy) * 10
            if alpha > 0:
                canvas.set_pixel(shadow_x, nose_y + dy, (*shadow_color[:3], alpha))

    def _render_cheek_blush(self, canvas: Canvas) -> None:
        """Render subtle cheek blush for liveliness."""
        cx, cy = self._get_face_center()
        fw, fh = self._get_face_dimensions()

        # Blush positions on both cheeks
        cheek_y = cy + fh // 8
        cheek_offset = fw // 4

        # Subtle pink/peach blush color
        base_skin = self._skin_ramp[len(self._skin_ramp) // 2]
        blush_color = (
            min(255, base_skin[0] + 15),
            max(0, base_skin[1] - 10),
            max(0, base_skin[2] - 5),
        )

        blush_radius = fw // 8
        for side in [-1, 1]:
            blush_cx = cx + side * cheek_offset
            for dy in range(-blush_radius, blush_radius + 1):
                for dx in range(-blush_radius, blush_radius + 1):
                    dist = (dx * dx + dy * dy) ** 0.5
                    if dist < blush_radius:
                        # Fade out toward edges
                        alpha = int(25 * (1 - dist / blush_radius))
                        if alpha > 0:
                            px, py = blush_cx + dx, cheek_y + dy
                            canvas.set_pixel(px, py, (*blush_color, alpha))

    def _render_eyes(self, canvas: Canvas) -> None:
        """Render detailed eyes with multiple layers."""
        cx, cy = self._get_face_center()
        fw, fh = self._get_face_dimensions()

        # Eye positioning
        eye_y = cy - fh // 8
        eye_spacing = fw // 4
        eye_width = fw // 6
        eye_height = int(eye_width * 0.6 * self.config.eye_openness)

        for side in [-1, 1]:  # Left and right eye
            ex = cx + side * eye_spacing

            # Layer 1: Eye white (slight off-white)
            white_color = (245, 242, 238, 255)
            canvas.fill_ellipse_aa(ex, eye_y, eye_width, eye_height, white_color)

            # Layer 2: Iris
            iris_radius = int(eye_width * 0.6)
            # Apply gaze offset
            gaze_x = int(self.config.gaze_direction[0] * eye_width * 0.2)
            gaze_y = int(self.config.gaze_direction[1] * eye_height * 0.2)
            iris_x = ex + gaze_x
            iris_y = eye_y + gaze_y

            # Iris gradient: darker at edge
            iris_outer = self._eye_ramp[0]  # Darkest
            iris_mid = self._eye_ramp[2]    # Middle
            canvas.fill_circle_aa(iris_x, iris_y, iris_radius, iris_outer)
            canvas.fill_circle_aa(iris_x, iris_y, int(iris_radius * 0.7), iris_mid)

            # Layer 3: Pupil
            pupil_radius = int(iris_radius * 0.4)
            pupil_color = (10, 10, 15, 255)  # Near black with slight blue
            canvas.fill_circle_aa(iris_x, iris_y, pupil_radius, pupil_color)

            # Layer 4: Catchlight (2 small white dots)
            catchlight_color = (255, 255, 255, 255)
            cl_offset_x = int(iris_radius * 0.3)
            cl_offset_y = int(iris_radius * 0.3)
            # Primary catchlight
            canvas.set_pixel(iris_x - cl_offset_x, iris_y - cl_offset_y, catchlight_color)
            canvas.set_pixel(iris_x - cl_offset_x + 1, iris_y - cl_offset_y, catchlight_color)
            # Secondary smaller catchlight
            canvas.set_pixel(iris_x + cl_offset_x - 1, iris_y + cl_offset_y, (255, 255, 255, 180))

            # Layer 5: Eyelid shadow (1px darker at top of eye)
            eyelid_shadow = (0, 0, 0, 40)
            for dx in range(-eye_width + 2, eye_width - 1):
                px = ex + dx
                py = eye_y - eye_height + 1
                if canvas.get_pixel(px, py) and canvas.get_pixel(px, py)[3] > 100:
                    canvas.set_pixel(px, py, eyelid_shadow)

    def _render_nose(self, canvas: Canvas) -> None:
        """Render nose with subtle shading."""
        cx, cy = self._get_face_center()
        fw, fh = self._get_face_dimensions()

        nose_y = cy + fh // 10
        nose_width = fw // 12
        nose_height = fh // 8

        # Nose shadow on one side (based on lighting)
        lx, _ = self.config.light_direction
        shadow_side = -1 if lx > 0 else 1

        mid_idx = len(self._skin_ramp) // 2
        shadow_color = (*self._skin_ramp[mid_idx - 1][:3], 60)
        highlight_color = (*self._skin_ramp[mid_idx + 1][:3], 50)

        # Subtle shadow line on one side
        for dy in range(nose_height):
            py = nose_y + dy
            px = cx + shadow_side * 2
            canvas.set_pixel(px, py, shadow_color)

        # Nose tip highlight
        canvas.set_pixel(cx, nose_y + nose_height - 2, highlight_color)
        canvas.set_pixel(cx, nose_y + nose_height - 1, highlight_color)

    def _render_lips(self, canvas: Canvas) -> None:
        """Render lips with gradient and highlight."""
        cx, cy = self._get_face_center()
        fw, fh = self._get_face_dimensions()

        lip_y = cy + fh // 4
        lip_width = fw // 5
        lip_height = fh // 20

        # Upper lip (slightly darker)
        upper_lip_color = self._lip_ramp[1]
        for dx in range(-lip_width, lip_width + 1):
            # Curved shape
            curve = int((1 - (dx / lip_width) ** 2) * lip_height * 0.5)
            for dy in range(curve):
                canvas.set_pixel(cx + dx, lip_y - dy, upper_lip_color)

        # Lip line (darker)
        lip_line_color = self._lip_ramp[0]
        for dx in range(-lip_width + 2, lip_width - 1):
            canvas.set_pixel(cx + dx, lip_y, lip_line_color)

        # Lower lip (lighter with highlight)
        lower_lip_color = self._lip_ramp[2]
        highlight_color = self._lip_ramp[3]

        for dx in range(-lip_width + 1, lip_width):
            curve = int((1 - (dx / lip_width) ** 2) * lip_height * 0.8)
            for dy in range(1, curve + 1):
                color = highlight_color if dy == 1 else lower_lip_color
                canvas.set_pixel(cx + dx, lip_y + dy, color)

    def _render_facial_hair(self, canvas: Canvas) -> None:
        """Render facial hair if configured."""
        if not self.config.has_facial_hair:
            return

        from generators.portrait_parts.face import (
            render_facial_hair, FacialHairStyle
        )

        cx, cy = self._get_face_center()
        fw, fh = self._get_face_dimensions()

        # Map style string to enum
        style_map = {
            "none": FacialHairStyle.NONE,
            "stubble": FacialHairStyle.STUBBLE,
            "mustache": FacialHairStyle.MUSTACHE,
            "goatee": FacialHairStyle.GOATEE,
            "short_beard": FacialHairStyle.SHORT_BEARD,
            "full_beard": FacialHairStyle.FULL_BEARD,
        }
        style = style_map.get(
            self.config.facial_hair_style.lower(),
            FacialHairStyle.STUBBLE
        )

        # Use facial hair color if specified, otherwise use hair color
        if self.config.facial_hair_color:
            facial_hair_ramp = self._generate_hair_ramp(self.config.facial_hair_color)
        else:
            facial_hair_ramp = self._hair_ramp

        render_facial_hair(
            canvas, cx, cy, fw, fh,
            style, facial_hair_ramp,
            self.config.light_direction
        )

    def _render_eyebrows(self, canvas: Canvas) -> None:
        """Render eyebrows with configurable arch and angle."""
        cx, cy = self._get_face_center()
        fw, fh = self._get_face_dimensions()

        brow_y = cy - fh // 5
        eye_spacing = fw // 4
        brow_width = fw // 6
        half_width = brow_width // 2

        # Eyebrow color (darker than hair)
        brow_color = self._hair_ramp[0]  # Darkest hair color

        # Get config values
        arch_amount = self.config.eyebrow_arch
        angle = self.config.eyebrow_angle

        for side in [-1, 1]:
            brow_x = cx + side * eye_spacing

            # Angle is mirrored for left/right eyebrows
            effective_angle = angle * side

            for dx in range(-half_width, half_width + 1):
                # Normalized position (-1 to 1)
                t = dx / half_width if half_width > 0 else 0

                # Arch curve (higher arch_amount = more curved)
                arch = int(arch_amount * (1 - t ** 2) * 4)

                # Angle offset (tilts the eyebrow)
                angle_offset = int(effective_angle * t * 4)

                px = brow_x + dx
                py = brow_y - arch + angle_offset

                canvas.set_pixel(px, py, brow_color)
                canvas.set_pixel(px, py + 1, brow_color)  # 2px thick

    def _render_hair(self, canvas: Canvas) -> None:
        """Render back hair using bezier-based cluster system."""
        from generators.portrait_parts.hair import (
            generate_hair_clusters, render_hair_clusters,
            generate_stray_strands,
            HairStyle as HairStyleParts
        )

        cx, cy = self._get_face_center()
        fw, fh = self._get_face_dimensions()

        # Hair parameters
        hair_top = cy - fh // 2 - fh // 4
        hair_width = int(fw * 0.85)
        hair_length = int(fh * 0.85 * self.config.hair_length)

        # Map HairStyle enum to parts module enum
        style_map = {
            HairStyle.WAVY: HairStyleParts.WAVY,
            HairStyle.STRAIGHT: HairStyleParts.STRAIGHT,
            HairStyle.CURLY: HairStyleParts.CURLY,
            HairStyle.SHORT: HairStyleParts.SHORT,
            HairStyle.PONYTAIL: HairStyleParts.PONYTAIL,
            HairStyle.BRAIDED: HairStyleParts.STRAIGHT,
        }
        hair_style = style_map.get(self.config.hair_style, HairStyleParts.WAVY)

        # Increased cluster count for fuller hair
        cluster_count = max(15, self.config.width // 4)

        # Generate main hair clusters
        clusters = generate_hair_clusters(
            style=hair_style,
            center_x=float(cx),
            top_y=float(hair_top),
            width=float(hair_width),
            length=float(hair_length),
            count=cluster_count,
            seed=self.config.seed
        )

        # Add stray strands for detail
        stray_count = max(3, self.config.width // 20)
        stray_rng = self.rng if self.config.seed else None
        strays = generate_stray_strands(
            center_x=float(cx),
            top_y=float(hair_top),
            width=float(hair_width),
            length=float(hair_length),
            count=stray_count,
            rng=stray_rng
        )
        clusters.extend(strays)

        # Sort all clusters by z_depth
        clusters.sort(key=lambda c: c.z_depth)

        # Render clusters
        render_hair_clusters(
            canvas=canvas,
            clusters=clusters,
            color_ramp=self._hair_ramp,
            light_direction=self.config.light_direction
        )

    def _render_bangs(self, canvas: Canvas) -> None:
        """Render front bangs/fringe over the forehead."""
        from generators.portrait_parts.hair import (
            generate_bangs_clusters, render_hair_clusters,
            HairStyle as HairStyleParts
        )

        # Skip bangs for short hair
        if self.config.hair_style == HairStyle.SHORT:
            return

        cx, cy = self._get_face_center()
        fw, fh = self._get_face_dimensions()

        # Bangs start at top of forehead
        forehead_y = cy - fh // 3
        bangs_width = int(fw * 0.6)
        bangs_length = int(fh * 0.25)  # Bangs extend down over forehead

        # Map style
        style_map = {
            HairStyle.WAVY: HairStyleParts.WAVY,
            HairStyle.STRAIGHT: HairStyleParts.STRAIGHT,
            HairStyle.CURLY: HairStyleParts.CURLY,
            HairStyle.SHORT: HairStyleParts.SHORT,
            HairStyle.PONYTAIL: HairStyleParts.WAVY,
            HairStyle.BRAIDED: HairStyleParts.STRAIGHT,
        }
        hair_style = style_map.get(self.config.hair_style, HairStyleParts.WAVY)

        # Bangs cluster count based on size
        bangs_count = max(5, self.config.width // 12)

        # Use different seed for bangs variation
        bangs_seed = (self.config.seed + 1000) if self.config.seed else None
        bangs_rng = random.Random(bangs_seed)

        bangs = generate_bangs_clusters(
            center_x=float(cx),
            forehead_y=float(forehead_y),
            width=float(bangs_width),
            length=float(bangs_length),
            count=bangs_count,
            style=hair_style,
            rng=bangs_rng
        )

        # Render bangs
        render_hair_clusters(
            canvas=canvas,
            clusters=bangs,
            color_ramp=self._hair_ramp,
            light_direction=self.config.light_direction
        )

    def _render_earrings(self, canvas: Canvas) -> None:
        """Render earrings if configured."""
        if not self.config.has_earrings:
            return

        from generators.portrait_parts.accessories import (
            render_earring, EarringStyle
        )

        cx, cy = self._get_face_center()
        fw, fh = self._get_face_dimensions()

        # Ear position - on the sides of the face, slightly below eye level
        ear_y = cy + fh // 12  # Slightly below center
        ear_offset = fw // 2 + 2  # Just outside face edge

        # Map style string to enum
        style_map = {
            "stud": EarringStyle.STUD,
            "hoop": EarringStyle.HOOP,
            "drop": EarringStyle.DROP,
            "dangle": EarringStyle.DANGLE,
        }
        earring_style = style_map.get(
            self.config.earring_style.lower(),
            EarringStyle.STUD
        )

        # Earring colors based on style
        earring_colors = {
            "stud": (255, 215, 0, 255),     # Gold
            "hoop": (200, 200, 210, 255),    # Silver
            "drop": (70, 130, 180, 255),     # Blue gem
            "dangle": (255, 215, 0, 255),    # Gold
        }
        color = earring_colors.get(
            self.config.earring_style.lower(),
            (255, 215, 0, 255)
        )

        # Size scales with face
        size = max(2, fw // 20)

        # Render on both ears
        render_earring(canvas, cx - ear_offset, ear_y, earring_style, color, size)
        render_earring(canvas, cx + ear_offset, ear_y, earring_style, color, size)

    def _render_glasses(self, canvas: Canvas) -> None:
        """Render glasses if configured."""
        if not self.config.has_glasses:
            return

        from generators.portrait_parts.accessories import (
            render_glasses, GlassesParams, GlassesStyle
        )

        cx, cy = self._get_face_center()
        fw, fh = self._get_face_dimensions()

        # Eye positions (matching _render_eyes)
        eye_y = cy - fh // 8
        eye_spacing = fw // 4
        eye_width = fw // 6

        # Map style string to enum
        style_map = {
            "round": GlassesStyle.ROUND,
            "rectangular": GlassesStyle.RECTANGULAR,
            "cat_eye": GlassesStyle.CAT_EYE,
            "aviator": GlassesStyle.AVIATOR,
            "rimless": GlassesStyle.RIMLESS,
        }
        glasses_style = style_map.get(
            self.config.glasses_style.lower(),
            GlassesStyle.ROUND
        )

        # Lens dimensions slightly larger than eyes
        lens_width = int(eye_width * 1.4)
        lens_height = int(eye_width * 0.9)

        # Frame color - dark brown/black
        frame_color = (45, 35, 30, 255)

        params = GlassesParams(
            left_eye_x=cx - eye_spacing,
            left_eye_y=eye_y,
            right_eye_x=cx + eye_spacing,
            right_eye_y=eye_y,
            lens_width=lens_width,
            lens_height=lens_height,
            style=glasses_style,
            frame_color=frame_color,
            lens_tint=None,  # Clear lenses
            has_reflection=True,
        )

        render_glasses(canvas, params, self.config.light_direction)

    def _render_clothing(self, canvas: Canvas) -> None:
        """Render clothing neckline at bottom of portrait."""
        from generators.portrait_parts.clothing import (
            render_neckline, ClothingParams, ClothingStyle,
            create_clothing_ramp
        )

        cx, cy = self._get_face_center()
        fw, fh = self._get_face_dimensions()

        # Clothing starts below the chin
        neckline_y = cy + fh // 2 + fh // 8
        shoulder_width = int(fw * 0.9)

        # Map style
        style_map = {
            "casual": ClothingStyle.CREW_NECK,
            "formal": ClothingStyle.COLLARED,
            "v_neck": ClothingStyle.V_NECK,
            "turtleneck": ClothingStyle.TURTLENECK,
        }
        clothing_style = style_map.get(
            self.config.clothing_style.lower(),
            ClothingStyle.CREW_NECK
        )

        # Get clothing color
        clothing_colors = {
            "blue": (70, 90, 140),
            "red": (140, 60, 60),
            "green": (60, 120, 80),
            "white": (230, 230, 235),
            "black": (35, 35, 40),
            "gray": (120, 120, 125),
            "purple": (100, 70, 130),
            "brown": (100, 75, 55),
        }
        base_color = clothing_colors.get(
            self.config.clothing_color.lower(),
            (70, 90, 140)  # Default blue
        )
        color_ramp = create_clothing_ramp((*base_color, 255), levels=5)

        params = ClothingParams(
            neckline_y=neckline_y,
            shoulder_left_x=cx - shoulder_width // 2,
            shoulder_right_x=cx + shoulder_width // 2,
            center_x=cx,
            canvas_bottom=self.config.height,
            style=clothing_style,
            color_ramp=color_ramp,
        )

        render_neckline(canvas, params, self.config.light_direction)

    def _render_shoulders(self, canvas: Canvas) -> None:
        """Render shoulders extending from clothing area."""
        cx, cy = self._get_face_center()
        fw, fh = self._get_face_dimensions()

        # Shoulder parameters
        neckline_y = cy + fh // 2 + fh // 8
        shoulder_width = int(self.config.width * 0.45)  # Wider shoulders
        shoulder_drop = int(self.config.height * 0.12)  # How much shoulders slope down

        # Get clothing color for shoulder fill
        clothing_colors = {
            "blue": (70, 90, 140),
            "red": (140, 60, 60),
            "green": (60, 120, 80),
            "white": (230, 230, 235),
            "black": (35, 35, 40),
            "gray": (120, 120, 125),
            "purple": (100, 70, 130),
            "brown": (100, 75, 55),
        }
        base_color = clothing_colors.get(
            self.config.clothing_color.lower(),
            (70, 90, 140)
        )

        # Create shading colors
        dark_color = (
            max(0, base_color[0] - 30),
            max(0, base_color[1] - 30),
            max(0, base_color[2] - 30),
            255
        )
        light_color = (
            min(255, base_color[0] + 20),
            min(255, base_color[1] + 20),
            min(255, base_color[2] + 20),
            255
        )
        base_color = (*base_color, 255)

        lx, _ = self.config.light_direction

        # Render left shoulder
        for x in range(0, cx - fw // 3):
            # Curved shoulder line
            dist_from_body = (cx - fw // 3) - x
            progress = dist_from_body / shoulder_width if shoulder_width > 0 else 0
            progress = min(1.0, progress)

            # Shoulder drops as it goes outward
            shoulder_top = neckline_y + int(progress * shoulder_drop)

            # Fill from shoulder top to canvas bottom
            for y in range(shoulder_top, self.config.height):
                # Gradient shading
                vert_progress = (y - shoulder_top) / max(1, self.config.height - shoulder_top)

                if progress > 0.6:
                    # Outer shoulder is darker
                    color = dark_color
                elif lx < 0:
                    # Light from left, this shoulder is lit
                    color = light_color if vert_progress < 0.3 else base_color
                else:
                    color = dark_color if vert_progress > 0.5 else base_color

                canvas.set_pixel(x, y, color)

        # Render right shoulder
        for x in range(cx + fw // 3, self.config.width):
            dist_from_body = x - (cx + fw // 3)
            progress = dist_from_body / shoulder_width if shoulder_width > 0 else 0
            progress = min(1.0, progress)

            shoulder_top = neckline_y + int(progress * shoulder_drop)

            for y in range(shoulder_top, self.config.height):
                vert_progress = (y - shoulder_top) / max(1, self.config.height - shoulder_top)

                if progress > 0.6:
                    color = dark_color
                elif lx > 0:
                    # Light from right, this shoulder is lit
                    color = light_color if vert_progress < 0.3 else base_color
                else:
                    color = dark_color if vert_progress > 0.5 else base_color

                canvas.set_pixel(x, y, color)

    def _render_background(self, canvas: Canvas) -> None:
        """Render background with optional gradient and vignette."""
        if not hasattr(self.config, 'background_color') or self.config.background_color is None:
            return  # Transparent background

        bg = self.config.background_color
        cx, cy = self.config.width / 2, self.config.height / 2
        max_dist = math.sqrt(cx * cx + cy * cy)
        vignette = getattr(self.config, 'vignette_strength', 0.0)

        for y in range(self.config.height):
            for x in range(self.config.width):
                # Get base color
                if isinstance(bg, tuple) and len(bg) == 2 and isinstance(bg[0], (tuple, list)):
                    # Gradient
                    t = y / max(1, self.config.height - 1)
                    r = int(bg[0][0] + (bg[1][0] - bg[0][0]) * t)
                    g = int(bg[0][1] + (bg[1][1] - bg[0][1]) * t)
                    b = int(bg[0][2] + (bg[1][2] - bg[0][2]) * t)
                else:
                    # Solid
                    r, g, b = bg[0], bg[1], bg[2]

                # Apply vignette
                if vignette > 0:
                    dx, dy = x - cx, y - cy
                    dist = math.sqrt(dx * dx + dy * dy) / max_dist
                    # Smooth falloff from center
                    darken = dist * dist * vignette
                    r = int(r * (1 - darken * 0.7))
                    g = int(g * (1 - darken * 0.7))
                    b = int(b * (1 - darken * 0.7))
                    r, g, b = max(0, r), max(0, g), max(0, b)

                canvas.set_pixel(x, y, (r, g, b, 255))

    def render(self) -> Canvas:
        """
        Render the complete portrait.

        Returns:
            Canvas with the rendered portrait
        """
        # Prepare color ramps
        self._prepare_ramps()

        # Create canvas
        canvas = Canvas(self.config.width, self.config.height)

        # Render layers from back to front
        self._render_background(canvas)  # Background first
        if self.config.show_shoulders:
            self._render_shoulders(canvas)  # Shoulders behind clothing center
        self._render_clothing(canvas)  # Clothing center area
        self._render_hair(canvas)  # Back hair with cluster system
        self._render_face_base(canvas)
        self._render_nose(canvas)
        self._render_lips(canvas)
        self._render_facial_hair(canvas)  # Facial hair below face
        self._render_eyes(canvas)
        self._render_earrings(canvas)  # Earrings on side of face
        self._render_glasses(canvas)  # Glasses over eyes
        self._render_eyebrows(canvas)
        self._render_bangs(canvas)  # Front hair over forehead

        return canvas


def generate_portrait(config: Optional[PortraitConfig] = None,
                      **kwargs) -> Canvas:
    """
    Convenience function to generate a portrait.

    Args:
        config: PortraitConfig object, or None to use defaults
        **kwargs: Override config parameters

    Returns:
        Canvas with rendered portrait
    """
    if config is None:
        config = PortraitConfig(**kwargs)
    else:
        # Apply any overrides
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)

    gen = PortraitGenerator(
        width=config.width,
        height=config.height,
        seed=config.seed
    )

    # Apply configuration
    gen.config = config

    return gen.render()


# Quick test when run directly
if __name__ == "__main__":
    print("Testing PortraitGenerator...")

    gen = PortraitGenerator(width=128, height=160, seed=42)
    gen.set_skin("light")
    gen.set_hair(HairStyle.WAVY, "brown")
    gen.set_eyes(EyeShape.ROUND, "blue")

    portrait = gen.render()
    portrait.save("test_portrait.png")
    print(f"Saved test_portrait.png ({portrait.width}x{portrait.height})")

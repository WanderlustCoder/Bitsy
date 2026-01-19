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
    hair_parting: str = "none"  # none, left, right, center
    has_hair_highlights: bool = False
    highlight_color: str = "blonde"  # color for highlights/streaks
    highlight_intensity: float = 0.3  # 0.0-1.0, proportion of hair highlighted

    # Face
    face_shape: str = "oval"  # oval, round, heart, square
    face_width: float = 1.0  # 0.8-1.2, multiplier for face width
    chin_type: str = "normal"  # normal, pointed, square, round, cleft
    forehead_size: str = "normal"  # normal, large, small
    ear_type: str = "normal"  # normal, pointed, round, large, small
    eye_shape: EyeShape = EyeShape.ROUND
    eye_color: str = "brown"
    eye_size: float = 1.0  # 0.7-1.3, multiplier for eye size
    right_eye_color: Optional[str] = None  # None = same as left, set for heterochromia
    nose_type: NoseType = NoseType.SMALL
    nose_size: float = 1.0  # 0.7-1.3, multiplier for nose size
    lip_shape: LipShape = LipShape.NEUTRAL
    lip_color: str = "natural"
    has_lipstick: bool = False
    lipstick_color: str = "red"  # red, pink, nude, berry, coral, plum
    lipstick_intensity: float = 0.7  # 0.0 to 1.0
    lip_thickness: float = 1.0  # 0.5-1.5, multiplier for lip height

    # Teeth
    show_teeth: bool = False
    teeth_whiteness: float = 0.9  # 0.0-1.0, how white the teeth are

    # Expression
    expression: str = "neutral"  # neutral, happy, sad, surprised, etc.
    eye_openness: float = 1.0  # 0.0 = closed, 1.0 = fully open
    gaze_direction: Tuple[float, float] = (0.0, 0.0)  # pupil offset

    # Eyeliner
    has_eyeliner: bool = False
    eyeliner_style: str = "thin"  # thin, thick, winged, smoky
    eyeliner_color: str = "black"  # black, brown, blue, purple

    # Eyebrows
    eyebrow_arch: float = 0.3  # 0.0 to 1.0, controls arch height
    eyebrow_angle: float = 0.0  # -0.5 to 0.5, negative=sad, positive=angry
    eyebrow_thickness: int = 2  # 1-4 pixels thick

    # Eyebags
    has_eyebags: bool = False
    eyebag_intensity: float = 0.5  # 0.0 to 1.0

    # Blush
    has_blush: bool = False
    blush_color: str = "pink"  # pink, peach, coral, rose
    blush_intensity: float = 0.5  # 0.0 to 1.0

    # Dimples
    has_dimples: bool = False
    dimple_depth: float = 0.5  # 0.0 to 1.0

    # Wrinkles/aging
    has_wrinkles: bool = False
    wrinkle_intensity: float = 0.5  # 0.0 to 1.0, controls visibility
    wrinkle_areas: str = "all"  # all, forehead, eyes, mouth

    # Accessories
    has_glasses: bool = False
    glasses_style: str = "round"
    has_earrings: bool = False
    earring_style: str = "stud"
    has_facial_hair: bool = False
    facial_hair_style: str = "none"
    facial_hair_color: Optional[str] = None  # None = use hair color
    has_necklace: bool = False
    necklace_style: str = "chain"
    has_hair_accessory: bool = False
    hair_accessory_style: str = "headband"
    hair_accessory_color: Optional[str] = None  # None = use default pink
    has_nose_piercing: bool = False
    nose_piercing_type: str = "stud"  # stud, ring, septum
    has_eyebrow_piercing: bool = False
    has_lip_piercing: bool = False
    lip_piercing_type: str = "stud"  # stud, ring, labret
    piercing_color: str = "silver"  # silver, gold, black

    # Freckles and beauty marks
    has_freckles: bool = False
    freckle_density: float = 0.5  # 0.0 to 1.0
    has_moles: bool = False
    mole_count: int = 3  # 1-5 moles
    mole_positions: str = "random"  # random, cheeks, forehead
    has_beauty_mark: bool = False
    beauty_mark_position: str = "cheek"  # cheek, lip, chin
    has_scar: bool = False
    scar_type: str = "cheek"  # cheek, eyebrow, lip, forehead
    scar_intensity: float = 0.5  # 0.0 to 1.0

    # Face tattoos
    has_face_tattoo: bool = False
    face_tattoo_type: str = "tear"  # tear, star, tribal, dots
    face_tattoo_position: str = "cheek"  # cheek, forehead, temple
    face_tattoo_color: str = "black"  # black, blue, red

    # Cheekbone prominence
    cheekbone_prominence: str = "normal"  # low, normal, high, sculpted

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

EYELINER_COLORS = {
    "black": (20, 20, 25),
    "brown": (70, 50, 40),
    "blue": (40, 60, 120),
    "purple": (85, 55, 125),
}

LIPSTICK_COLORS = {
    "red": (190, 45, 60),
    "pink": (210, 90, 130),
    "nude": (195, 130, 110),
    "berry": (135, 45, 80),
    "coral": (220, 95, 75),
    "plum": (115, 50, 90),
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

    def set_face_shape(self, shape: str = "oval") -> 'PortraitGenerator':
        """
        Set face shape.

        Args:
            shape: One of 'oval', 'round', 'heart', 'square'
        """
        self.config.face_shape = shape
        return self

    def set_face_width(self, width: float = 1.0) -> 'PortraitGenerator':
        """
        Set face width multiplier.

        Args:
            width: Multiplier for face width (0.8-1.2, default 1.0)
        """
        self.config.face_width = max(0.8, min(1.2, width))
        return self

    def set_chin(self, chin_type: str = "normal") -> 'PortraitGenerator':
        """
        Set chin type.

        Args:
            chin_type: One of 'normal', 'pointed', 'square', 'round', 'cleft'
        """
        self.config.chin_type = chin_type
        return self

    def set_forehead(self, size: str = "normal") -> 'PortraitGenerator':
        """
        Set forehead size.

        Args:
            size: One of 'normal', 'large', 'small'
        """
        self.config.forehead_size = size
        return self

    def set_ears(self, ear_type: str = "normal") -> 'PortraitGenerator':
        """
        Set ear type.

        Args:
            ear_type: One of 'normal', 'pointed', 'round', 'large', 'small'
        """
        self.config.ear_type = ear_type
        return self

    def set_hair(self, style: HairStyle, color: str,
                 length: float = 1.0) -> 'PortraitGenerator':
        """Set hair style and color."""
        self.config.hair_style = style
        self.config.hair_color = color
        self.config.hair_length = length
        return self

    def set_hair_parting(self, side: str = "center") -> 'PortraitGenerator':
        """Set hair parting side (none, left, right, center)."""
        self.config.hair_parting = (side or "none").lower()
        return self

    def set_hair_highlights(self, color: str = "blonde",
                            intensity: float = 0.3) -> 'PortraitGenerator':
        """
        Add highlights/streaks to hair.

        Args:
            color: Highlight color (blonde, red, gray, white, etc.)
            intensity: Proportion of hair that's highlighted (0.0-1.0)
        """
        self.config.has_hair_highlights = True
        self.config.highlight_color = color
        self.config.highlight_intensity = max(0.0, min(1.0, intensity))
        return self

    def set_eyes(self, shape: EyeShape, color: str,
                 openness: float = 1.0,
                 right_color: Optional[str] = None,
                 size: float = 1.0) -> 'PortraitGenerator':
        """
        Set eye shape and color.

        Args:
            shape: Eye shape
            color: Left eye color (and right if right_color not set)
            openness: How open the eyes are (0.0-1.0)
            right_color: Right eye color for heterochromia (None = same as left)
            size: Eye size multiplier (0.7-1.3, default 1.0)
        """
        self.config.eye_shape = shape
        self.config.eye_color = color
        self.config.right_eye_color = right_color
        self.config.eye_openness = openness
        self.config.eye_size = max(0.7, min(1.3, size))
        return self

    def set_eyeliner(self, style: str = "thin",
                     color: str = "black") -> 'PortraitGenerator':
        """Add eyeliner with style and color."""
        self.config.has_eyeliner = True
        self.config.eyeliner_style = style
        self.config.eyeliner_color = color
        return self

    def set_nose(self, nose_type: NoseType, size: float = 1.0) -> 'PortraitGenerator':
        """
        Set nose type and size.

        Args:
            nose_type: Nose shape type
            size: Size multiplier (0.7-1.3, default 1.0)
        """
        self.config.nose_type = nose_type
        self.config.nose_size = max(0.7, min(1.3, size))
        return self

    def set_lips(self, shape: LipShape, color: str = "natural") -> 'PortraitGenerator':
        """Set lip shape and color."""
        self.config.lip_shape = shape
        self.config.lip_color = color
        return self

    def set_nose_piercing(self, piercing_type: str = "stud",
                          color: str = "silver") -> 'PortraitGenerator':
        """Add a nose piercing with type and color."""
        self.config.has_nose_piercing = True
        self.config.nose_piercing_type = piercing_type
        self.config.piercing_color = color
        return self

    def set_eyebrow_piercing(self, color: str = "silver") -> 'PortraitGenerator':
        """Add an eyebrow piercing with color."""
        self.config.has_eyebrow_piercing = True
        self.config.piercing_color = color
        return self

    def set_lip_piercing(self, piercing_type: str = "stud",
                         color: str = "silver") -> 'PortraitGenerator':
        """Add a lip piercing with type and color."""
        self.config.has_lip_piercing = True
        self.config.lip_piercing_type = piercing_type
        self.config.piercing_color = color
        return self

    def set_lipstick(self, color: str = "red",
                     intensity: float = 0.7) -> 'PortraitGenerator':
        """Add lipstick with configurable color and intensity (0.0-1.0)."""
        self.config.has_lipstick = True
        self.config.lipstick_color = color
        self.config.lipstick_intensity = max(0.0, min(1.0, intensity))
        return self

    def set_lip_thickness(self, thickness: float = 1.0) -> 'PortraitGenerator':
        """
        Set lip thickness multiplier.

        Args:
            thickness: Multiplier for lip height (0.5-1.5, default 1.0)
        """
        self.config.lip_thickness = max(0.5, min(1.5, thickness))
        return self

    def set_teeth(self, whiteness: float = 0.9) -> 'PortraitGenerator':
        """
        Show teeth (visible when smiling/happy expression).

        Args:
            whiteness: How white the teeth are (0.0-1.0)
        """
        self.config.show_teeth = True
        self.config.teeth_whiteness = max(0.0, min(1.0, whiteness))
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
        - suspicious: Narrowed eyes, slightly angled brows
        - loving: Soft eyes, gentle upward gaze
        - confused: Normal eyes, mixed brow angle
        - determined: Focused eyes, strong brow angle
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
            "sleepy": (0.45, (0.0, 0.15), 0.2, -0.1),  # Relaxed droop
            "suspicious": (0.6, (0.1, 0.0), 0.35, 0.2),  # Narrow eyes, side glance
            "loving": (1.3, (0.0, -0.05), 0.45, 0.05),  # Soft, slightly upturned
            "confused": (1.0, (0.0, 0.0), 0.35, -0.15),  # Mixed brow angle
            "determined": (0.85, (0.0, 0.0), 0.2, 0.3),  # Focused, strong angle
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

    def set_eyebrows(self, arch: float = 0.3, angle: float = 0.0,
                      thickness: int = 2) -> 'PortraitGenerator':
        """Set eyebrow shape.

        Args:
            arch: Arch height (0.0-1.0, default 0.3)
            angle: Angle tilt (-0.5 to 0.5, negative=sad, positive=angry)
            thickness: Thickness in pixels (1-4, default 2)
        """
        self.config.eyebrow_arch = max(0.0, min(1.0, arch))
        self.config.eyebrow_angle = max(-0.5, min(0.5, angle))
        self.config.eyebrow_thickness = max(1, min(4, thickness))
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

    def set_necklace(self, style: str = "chain") -> 'PortraitGenerator':
        """
        Add a necklace.

        Args:
            style: One of 'chain', 'choker', 'pendant', 'pearl'
        """
        self.config.has_necklace = True
        self.config.necklace_style = style
        return self

    def set_hair_accessory(self, style: str = "headband",
                           color: Optional[str] = None) -> 'PortraitGenerator':
        """
        Add a hair accessory.

        Args:
            style: One of 'headband', 'bow', 'clip', 'scrunchie'
            color: Color name (None for default pink)
        """
        self.config.has_hair_accessory = True
        self.config.hair_accessory_style = style
        self.config.hair_accessory_color = color
        return self

    def set_freckles(self, density: float = 0.5) -> 'PortraitGenerator':
        """Add freckles with a density from 0.0 to 1.0."""
        self.config.has_freckles = True
        self.config.freckle_density = max(0.0, min(1.0, density))
        return self

    def set_moles(self, count: int = 3, positions: str = "random") -> 'PortraitGenerator':
        """Add facial moles with count and positions."""
        self.config.has_moles = True
        self.config.mole_count = max(1, min(5, count))
        self.config.mole_positions = positions
        return self

    def set_dimples(self, depth: float = 0.5) -> 'PortraitGenerator':
        """Add cheek dimples with depth from 0.0 to 1.0."""
        self.config.has_dimples = True
        self.config.dimple_depth = max(0.0, min(1.0, depth))
        return self

    def set_eyebags(self, intensity: float = 0.5) -> 'PortraitGenerator':
        """Add eyebags with intensity from 0.0 to 1.0."""
        self.config.has_eyebags = True
        self.config.eyebag_intensity = max(0.0, min(1.0, intensity))
        return self

    def set_blush(self, color: str = "pink",
                  intensity: float = 0.5) -> 'PortraitGenerator':
        """Add blush with configurable color and intensity (0.0-1.0)."""
        self.config.has_blush = True
        self.config.blush_color = color
        self.config.blush_intensity = max(0.0, min(1.0, intensity))
        return self

    def set_wrinkles(self, intensity: float = 0.5,
                     areas: str = "all") -> 'PortraitGenerator':
        """
        Add wrinkles/aging lines.

        Args:
            intensity: How visible the wrinkles are (0.0-1.0)
            areas: Which areas to affect - "all", "forehead", "eyes", "mouth"
        """
        self.config.has_wrinkles = True
        self.config.wrinkle_intensity = max(0.0, min(1.0, intensity))
        self.config.wrinkle_areas = areas
        return self

    def set_beauty_mark(self, position: str = "cheek") -> 'PortraitGenerator':
        """Add a beauty mark at the specified position."""
        self.config.has_beauty_mark = True
        self.config.beauty_mark_position = position
        return self

    def set_scar(self, scar_type: str = "cheek",
                 intensity: float = 0.5) -> 'PortraitGenerator':
        """Add a facial scar with a specified type and intensity (0.0-1.0)."""
        self.config.has_scar = True
        self.config.scar_type = scar_type
        self.config.scar_intensity = max(0.0, min(1.0, intensity))
        return self

    def set_face_tattoo(self, tattoo_type: str = "tear",
                        position: str = "cheek",
                        color: str = "black") -> 'PortraitGenerator':
        """Add a facial tattoo with type, position, and color."""
        self.config.has_face_tattoo = True
        self.config.face_tattoo_type = tattoo_type
        self.config.face_tattoo_position = position
        self.config.face_tattoo_color = color
        return self

    def set_cheekbones(self, prominence: str = "normal") -> 'PortraitGenerator':
        """
        Set cheekbone prominence level.

        Args:
            prominence: One of 'low', 'normal', 'high', 'sculpted'
        """
        self.config.cheekbone_prominence = prominence
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

        # Hair highlight ramp (for streaks/highlights)
        if self.config.has_hair_highlights:
            highlight_base = HAIR_COLORS.get(self.config.highlight_color, HAIR_COLORS["blonde"])
            self._highlight_ramp = create_hair_ramp(
                (*highlight_base, 255),
                levels=6
            )
        else:
            self._highlight_ramp = self._hair_ramp

        # Eye ramp (left eye / both if no heterochromia)
        eye_base = EYE_COLORS.get(self.config.eye_color, EYE_COLORS["brown"])
        self._eye_ramp = create_eye_ramp(
            (*eye_base, 255),
            levels=5
        )

        # Right eye ramp for heterochromia
        if self.config.right_eye_color:
            right_eye_base = EYE_COLORS.get(self.config.right_eye_color, EYE_COLORS["brown"])
            self._right_eye_ramp = create_eye_ramp(
                (*right_eye_base, 255),
                levels=5
            )
        else:
            self._right_eye_ramp = self._eye_ramp

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
            self._right_eye_ramp = self._adjust_ramp_vibrancy(self._right_eye_ramp, vibrancy)
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
        _, fh = self._get_face_dimensions()
        center_shift, _, _ = self._get_forehead_tuning(fh)
        cy = int(self.config.height * 0.45) + center_shift  # Face slightly above center
        return cx, cy

    def _get_face_dimensions(self) -> Tuple[int, int]:
        """Calculate face width and height."""
        # Face takes about 60% of width, 50% of height
        width_mult = getattr(self.config, 'face_width', 1.0)
        fw = int(self.config.width * 0.6 * width_mult)
        fh = int(self.config.height * 0.5)
        return fw, fh

    def _get_hair_parting_segments(self, center_x: float,
                                   width: float) -> List[Tuple[float, float]]:
        """Compute hair segment centers/widths based on parting."""
        parting = (self.config.hair_parting or "none").lower()
        if parting not in ("none", "left", "right", "center"):
            parting = "none"
        if parting == "none":
            return [(center_x, width)]

        shift = {"left": -0.14, "right": 0.14, "center": 0.0}[parting]
        gap = max(2.0, width * 0.07)
        gap = min(gap, width * 0.3)

        left_edge = center_x - width / 2
        right_edge = center_x + width / 2
        parting_x = center_x + shift * width
        parting_x = max(left_edge + gap, min(right_edge - gap, parting_x))

        left_end = parting_x - gap / 2
        right_start = parting_x + gap / 2

        left_width = max(1.0, left_end - left_edge)
        right_width = max(1.0, right_edge - right_start)

        left_center = left_edge + left_width / 2
        right_center = right_start + right_width / 2

        return [(left_center, left_width), (right_center, right_width)]

    def _get_forehead_tuning(self, fh: int) -> Tuple[int, int, float]:
        """Return center shift, eye shift, and upper scale for forehead sizing."""
        size = (self.config.forehead_size or "normal").lower()
        if size == "large":
            return int(fh * 0.02), int(fh * 0.06), 0.88
        if size == "small":
            return -int(fh * 0.02), -int(fh * 0.05), 1.12
        return 0, 0, 1.0

    def _get_eye_y(self, cy: int, fh: int) -> int:
        """Calculate eye baseline position with forehead sizing."""
        _, eye_shift, _ = self._get_forehead_tuning(fh)
        return cy - fh // 8 + eye_shift

    def _render_face_base(self, canvas: Canvas) -> None:
        """Render the base face shape with gradient shading."""
        cx, cy = self._get_face_center()
        fw, fh = self._get_face_dimensions()
        rx, ry = fw // 2, fh // 2
        _, _, forehead_scale = self._get_forehead_tuning(fh)

        # Light direction
        lx, ly = self.config.light_direction
        light_len = (lx * lx + ly * ly) ** 0.5
        if light_len > 0:
            lx, ly = lx / light_len, ly / light_len

        # Skin ramp indices
        ramp_len = len(self._skin_ramp)
        mid_idx = ramp_len // 2

        # Face shape parameters
        face_shape = self.config.face_shape.lower()
        chin_type = self.config.chin_type.lower()

        # Per-pixel gradient shading
        for y in range(cy - ry - 1, cy + ry + 2):
            for x in range(cx - rx - 1, cx + rx + 2):
                # Calculate base normalized coordinates
                dx = (x - cx) / rx if rx > 0 else 0
                dy = (y - cy) / ry if ry > 0 else 0

                # Apply face shape transformation
                if face_shape == "round":
                    # Round face: more circular proportions
                    # Reduce the y-elongation effect
                    adj_rx = rx * 0.95
                    adj_ry = ry * 0.85
                    dx = (x - cx) / adj_rx if adj_rx > 0 else 0
                    dy = (y - cy) / adj_ry if adj_ry > 0 else 0

                elif face_shape == "heart":
                    # Heart face: wider forehead, narrower chin
                    # Apply progressive narrowing toward bottom
                    if dy > 0:  # Below center
                        chin_narrow = 1.0 + dy * 0.25  # Narrow chin by up to 25%
                        dx = dx * chin_narrow
                    else:  # Above center (forehead)
                        forehead_wide = 1.0 + dy * 0.08  # Slightly wider forehead
                        dx = dx * forehead_wide

                elif face_shape == "square":
                    # Square face: defined jawline, straighter edges
                    # Blend between ellipse and rectangle
                    abs_dx = abs(dx)
                    abs_dy = abs(dy)
                    # Use superellipse approximation (squircle effect)
                    # Higher power = more rectangular
                    power = 2.8
                    dx = dx * (1.0 - 0.15 * (1.0 - abs_dx ** power))
                    dy = dy * (1.0 - 0.1 * (1.0 - abs_dy ** power))

                # else: oval (default) - no transformation needed

                if dy < 0:
                    dy = dy * forehead_scale

                chin_adjust = 0.0
                if dy > 0:
                    chin_weight = dy
                    if chin_type == "pointed":
                        # Narrower, more angular chin
                        taper = 1.0 + chin_weight * 0.6
                        dx = dx * taper
                        dy = dy * (1.0 + chin_weight * 0.12)
                    elif chin_type == "square":
                        # Wider, flatter bottom
                        widen = max(0.7, 1.0 - chin_weight * 0.25)
                        dx = dx * widen
                        if chin_weight > 0.65:
                            dy = 0.65 + (dy - 0.65) * 0.5
                    elif chin_type == "round":
                        # Softer, curved chin
                        soften = max(0.8, 1.0 - chin_weight * 0.15)
                        dx = dx * soften
                        dy = dy * (1.0 - chin_weight * 0.08)
                    elif chin_type == "cleft":
                        # Slight central indent
                        if chin_weight > 0.4:
                            cleft_width = 0.22
                            indent = (cleft_width - abs(dx)) / cleft_width
                            if indent > 0:
                                chin_adjust = indent * 0.08 * (chin_weight ** 2)

                dist_sq = dx * dx + dy * dy + chin_adjust

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

    def _render_ears(self, canvas: Canvas) -> None:
        """Render ears on the sides of the face with shape variations."""
        ear_type = (self.config.ear_type or "normal").lower()
        cx, cy = self._get_face_center()
        fw, fh = self._get_face_dimensions()
        rx, ry = fw // 2, fh // 2

        base_w = max(3, fw // 8)
        base_h = max(6, fh // 4)

        scale = 1.0
        if ear_type == "large":
            scale = 1.25
        elif ear_type == "small":
            scale = 0.75

        ear_w = max(3, int(base_w * scale))
        ear_h = max(5, int(base_h * scale))

        if ear_type == "round":
            ear_w = int(ear_w * 1.15)
            ear_h = int(ear_h * 0.9)
        elif ear_type == "pointed":
            ear_h = int(ear_h * 1.1)

        ear_center_y = cy - fh // 10

        lx, ly = self.config.light_direction
        light_len = (lx * lx + ly * ly) ** 0.5
        if light_len > 0:
            lx, ly = lx / light_len, ly / light_len

        ramp_len = len(self._skin_ramp)
        mid_idx = ramp_len // 2
        inner_color = self._skin_ramp[max(0, mid_idx - 2)]

        tip_height = max(2, ear_h // 4)
        tip_width = max(2, ear_w // 2)

        for side in (-1, 1):
            ear_center_x = cx + side * (rx + ear_w // 3)
            ear_top = ear_center_y - ear_h // 2
            ear_bottom = ear_center_y + ear_h // 2

            min_x = ear_center_x - ear_w // 2 - 1
            max_x = ear_center_x + ear_w // 2 + 1
            min_y = ear_top - (tip_height if ear_type == "pointed" else 0) - 1
            max_y = ear_bottom + 1

            for y in range(min_y, max_y + 1):
                for x in range(min_x, max_x + 1):
                    dx = (x - ear_center_x) / (ear_w / 2) if ear_w > 0 else 0
                    dy = (y - ear_center_y) / (ear_h / 2) if ear_h > 0 else 0

                    in_ellipse = dx * dx + dy * dy <= 1.0
                    in_tip = False
                    if ear_type == "pointed" and y < ear_top:
                        if y >= ear_top - tip_height:
                            t = (ear_top - y) / max(1, tip_height)
                            half_w = max(1, int(tip_width * (1.0 - t)))
                            in_tip = abs(x - ear_center_x) <= half_w

                    if not (in_ellipse or in_tip):
                        continue

                    face_dx = (x - cx) / rx if rx > 0 else 0
                    face_dy = (y - cy) / ry if ry > 0 else 0
                    if face_dx * face_dx + face_dy * face_dy <= 1.0:
                        continue

                    nx = dx
                    ny = dy
                    nlen = (nx * nx + ny * ny) ** 0.5
                    if nlen > 0:
                        nx, ny = nx / nlen, ny / nlen
                    else:
                        nx, ny = 0, -1

                    dot = -(nx * lx + ny * ly)
                    vertical_bias = -dy * 0.15
                    shading = (dot + vertical_bias + 1.0) / 2.0
                    shading = max(0.0, min(1.0, shading))

                    ramp_idx = int(shading * (ramp_len - 1))
                    ramp_idx = max(0, min(ramp_len - 1, ramp_idx))
                    color = self._skin_ramp[ramp_idx]
                    canvas.set_pixel(x, y, color)

                    if abs(dx) < 0.4 and abs(dy) < 0.4:
                        if side * dx < 0:
                            canvas.set_pixel(x, y, inner_color)

    def _render_blush(self, canvas: Canvas) -> None:
        """Render subtle cheek blush with a feathered gradient."""
        if not self.config.has_blush:
            return

        intensity = max(0.0, min(1.0, self.config.blush_intensity))
        if intensity <= 0.0:
            return

        cx, cy = self._get_face_center()
        fw, fh = self._get_face_dimensions()

        # Eye positioning (matching _render_eyes)
        eye_y = self._get_eye_y(cy, fh)
        eye_spacing = fw // 4
        eye_width = fw // 6
        eye_height = int(eye_width * 0.6 * self.config.eye_openness)

        # Blush position: upper cheeks, below eyes
        cheek_y = eye_y + eye_height + max(2, fh // 10)
        cheek_offset = eye_spacing

        base_skin = self._skin_ramp[len(self._skin_ramp) // 2]
        blush_palette = {
            "pink": (230, 150, 170),
            "peach": (240, 170, 140),
            "coral": (235, 120, 110),
            "rose": (210, 110, 140),
        }
        target = blush_palette.get(self.config.blush_color.lower(), blush_palette["pink"])

        # Blend blush toward skin tone for a natural mix
        blend_factor = 0.6
        blush_color = (
            int(base_skin[0] + (target[0] - base_skin[0]) * blend_factor),
            int(base_skin[1] + (target[1] - base_skin[1]) * blend_factor),
            int(base_skin[2] + (target[2] - base_skin[2]) * blend_factor),
        )

        rx = max(3, fw // 7)
        ry = max(2, fh // 12)
        max_alpha = int(80 * intensity)

        for side in (-1, 1):
            blush_cx = cx + side * cheek_offset
            for dy in range(-ry - 1, ry + 2):
                for dx in range(-rx - 1, rx + 2):
                    nx = dx / rx if rx > 0 else 0
                    ny = dy / ry if ry > 0 else 0
                    dist = nx * nx + ny * ny
                    if dist <= 1.0:
                        # Feathered falloff for a soft gradient
                        falloff = (1.0 - dist) ** 2
                        alpha = int(max_alpha * falloff)
                        if alpha > 0:
                            px, py = blush_cx + dx, cheek_y + dy
                            canvas.set_pixel(px, py, (*blush_color, alpha))

    def _render_freckles(self, canvas: Canvas) -> None:
        """Render freckles across nose and cheeks."""
        if not self.config.has_freckles:
            return

        density = max(0.0, min(1.0, self.config.freckle_density))
        if density <= 0.0:
            return

        cx, cy = self._get_face_center()
        fw, fh = self._get_face_dimensions()
        rx, ry = fw // 2, fh // 2

        seed = self.config.seed
        rng = random.Random(seed + 2000) if seed is not None else random.Random()

        base_count = int(fw * fh * 0.0035)
        freckle_count = max(1, int(base_count * density))

        mid_idx = len(self._skin_ramp) // 2
        freckle_color = self._skin_ramp[max(0, mid_idx - 2)]
        freckle_color = (freckle_color[0], freckle_color[1], freckle_color[2], 210)

        regions = [
            (cx, cy + fh // 10, fw // 10, fh // 10, 0.4),  # nose bridge/tip
            (cx - fw // 4, cy + fh // 8, fw // 8, fh // 10, 0.3),  # left cheek
            (cx + fw // 4, cy + fh // 8, fw // 8, fh // 10, 0.3),  # right cheek
        ]
        region_weights = [r[4] for r in regions]

        for _ in range(freckle_count):
            for _ in range(6):
                region_idx = rng.choices(range(len(regions)), weights=region_weights, k=1)[0]
                rcx, rcy, rw, rh, _ = regions[region_idx]
                angle = rng.random() * math.tau
                radius = (rng.random() ** 0.5)
                px = int(rcx + math.cos(angle) * rw * radius)
                py = int(rcy + math.sin(angle) * rh * radius)

                dx = (px - cx) / rx if rx > 0 else 0
                dy = (py - cy) / ry if ry > 0 else 0
                if dx * dx + dy * dy <= 1.0:
                    canvas.set_pixel(px, py, freckle_color)
                    if rng.random() < 0.2:
                        canvas.set_pixel(px + 1, py, freckle_color)
                    break

    def _render_moles(self, canvas: Canvas) -> None:
        """Render small moles on the face."""
        if not self.config.has_moles:
            return

        count = max(1, min(5, self.config.mole_count))
        positions = (self.config.mole_positions or "random").lower()

        cx, cy = self._get_face_center()
        fw, fh = self._get_face_dimensions()
        rx, ry = fw // 2, fh // 2

        seed = self.config.seed
        rng = random.Random(seed + 2400) if seed is not None else random.Random()

        eye_y = self._get_eye_y(cy, fh)
        eye_spacing = fw // 4
        eye_width = max(1, fw // 6)
        eye_height = max(1, int(eye_width * 0.6 * max(0.3, self.config.eye_openness)))

        nose_y = cy + fh // 10
        if self.config.nose_type == NoseType.SMALL:
            nose_height = fh // 10
        elif self.config.nose_type == NoseType.BUTTON:
            nose_height = fh // 9
        elif self.config.nose_type == NoseType.POINTED:
            nose_height = fh // 7
        else:
            nose_height = fh // 8

        lip_y = cy + fh // 4
        lip_width = fw // 5
        lip_height = max(1, fh // 20)

        def in_face(px: int, py: int) -> bool:
            dx = (px - cx) / rx if rx > 0 else 0
            dy = (py - cy) / ry if ry > 0 else 0
            return dx * dx + dy * dy <= 1.0

        def in_exclusion(px: int, py: int) -> bool:
            for side in (-1, 1):
                ex = cx + side * eye_spacing
                if (ex - eye_width - 2) <= px <= (ex + eye_width + 2) and \
                        (eye_y - eye_height - 2) <= py <= (eye_y + eye_height + 2):
                    return True

            if (cx - fw // 12) <= px <= (cx + fw // 12) and \
                    (nose_y - 1) <= py <= (nose_y + nose_height + 2):
                return True

            if (cx - lip_width - 2) <= px <= (cx + lip_width + 2) and \
                    (lip_y - lip_height - 2) <= py <= (lip_y + lip_height + 2):
                return True

            return False

        cheek_offset = fw // 4
        cheek_y = cy + fh // 10
        cheek_rw = max(3, fw // 6)
        cheek_rh = max(3, fh // 7)

        forehead_y = cy - fh // 4
        forehead_rw = max(3, fw // 5)
        forehead_rh = max(3, fh // 8)

        regions = []
        if positions == "cheeks":
            regions = [
                (cx - cheek_offset, cheek_y, cheek_rw, cheek_rh),
                (cx + cheek_offset, cheek_y, cheek_rw, cheek_rh),
            ]
        elif positions == "forehead":
            regions = [(cx, forehead_y, forehead_rw, forehead_rh)]
        else:
            regions = [(cx, cy, rx, ry)]

        placed: List[Tuple[int, int]] = []
        attempts = 0
        max_attempts = max(30, count * 15)

        while len(placed) < count and attempts < max_attempts:
            attempts += 1
            rcx, rcy, rw, rh = rng.choice(regions)
            angle = rng.random() * math.tau
            radius = math.sqrt(rng.random())
            px = int(rcx + math.cos(angle) * rw * radius)
            py = int(rcy + math.sin(angle) * rh * radius)

            if not in_face(px, py):
                continue
            if in_exclusion(px, py):
                continue
            if any(abs(px - mx) <= 1 and abs(py - my) <= 1 for mx, my in placed):
                continue

            base = (28, 20, 18)
            shade = rng.randint(-8, 8)
            r = max(0, min(255, base[0] + shade))
            g = max(0, min(255, base[1] + shade))
            b = max(0, min(255, base[2] + shade))
            alpha = rng.randint(200, 245)
            canvas.set_pixel(px, py, (r, g, b, alpha))

            if rng.random() < 0.35:
                dx, dy = rng.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
                sx, sy = px + dx, py + dy
                if in_face(sx, sy) and not in_exclusion(sx, sy):
                    canvas.set_pixel(sx, sy, (r, g, b, max(180, alpha - 20)))

            placed.append((px, py))

    def _render_dimples(self, canvas: Canvas) -> None:
        """Render subtle cheek dimples for smiling expressions."""
        if not self.config.has_dimples:
            return

        expression = (self.config.expression or "").lower()
        if "happy" not in expression and "smile" not in expression and expression != "loving":
            return

        depth = max(0.0, min(1.0, self.config.dimple_depth))
        if depth <= 0.0:
            return

        cx, cy = self._get_face_center()
        fw, fh = self._get_face_dimensions()

        lip_y = cy + fh // 4
        cheek_y = lip_y + max(1, fh // 20)
        cheek_offset = max(3, fw // 6)

        mid_idx = len(self._skin_ramp) // 2
        shade_idx = max(0, mid_idx - 2)
        base_color = self._skin_ramp[shade_idx]

        radius = max(1, int(fw * (0.02 + 0.015 * depth)))
        alpha = int(40 + 60 * depth)
        dimple_color = (base_color[0], base_color[1], base_color[2], alpha)

        for side in [-1, 1]:
            dimple_x = cx + side * cheek_offset
            canvas.fill_circle_aa(dimple_x, cheek_y, radius, dimple_color)

    def _render_beauty_mark(self, canvas: Canvas) -> None:
        """Render a small beauty mark at a specified position."""
        if not self.config.has_beauty_mark:
            return

        cx, cy = self._get_face_center()
        fw, fh = self._get_face_dimensions()
        lip_y = cy + fh // 4

        position = (self.config.beauty_mark_position or "cheek").lower()
        if position == "lip":
            bx, by = cx + fw // 8, lip_y - 2
        elif position == "chin":
            bx, by = cx + fw // 12, cy + fh // 3
        else:
            bx, by = cx + fw // 6, cy - fh // 12

        mark_color = (30, 20, 20, 230)
        canvas.set_pixel(bx, by, mark_color)
        if fw > 80:
            canvas.set_pixel(bx + 1, by, mark_color)

    def _render_face_tattoo(self, canvas: Canvas) -> None:
        """Render a small facial tattoo design."""
        if not self.config.has_face_tattoo:
            return

        cx, cy = self._get_face_center()
        fw, fh = self._get_face_dimensions()
        rx, ry = fw // 2, fh // 2

        position = (self.config.face_tattoo_position or "cheek").lower()
        tattoo_type = (self.config.face_tattoo_type or "tear").lower()
        color_key = (self.config.face_tattoo_color or "black").lower()

        color_map = {
            "black": (20, 20, 25),
            "blue": (35, 60, 120),
            "red": (140, 40, 50),
        }
        base_color = color_map.get(color_key, color_map["black"])
        ink_color = (*base_color, 220)

        eye_y = self._get_eye_y(cy, fh)
        eye_spacing = fw // 4

        if position == "forehead":
            anchor_x = cx
            anchor_y = cy - fh // 4
        elif position == "temple":
            anchor_x = cx + eye_spacing + fw // 12
            anchor_y = eye_y - fh // 12
        else:
            anchor_x = cx + eye_spacing - fw // 18
            anchor_y = eye_y + fh // 10

        def in_face(px: int, py: int) -> bool:
            dx = (px - cx) / rx if rx > 0 else 0
            dy = (py - cy) / ry if ry > 0 else 0
            return dx * dx + dy * dy <= 1.0

        def draw_pixels(points: List[Tuple[int, int]]) -> None:
            for dx, dy in points:
                px, py = anchor_x + dx, anchor_y + dy
                if in_face(px, py):
                    canvas.set_pixel(px, py, ink_color)

        if tattoo_type == "star":
            draw_pixels([
                (0, 0), (-1, 0), (1, 0), (0, -1), (0, 1),
                (-1, -1), (1, -1)
            ])
        elif tattoo_type == "tribal":
            draw_pixels([
                (-2, 0), (-1, 0), (0, 1), (1, 1), (2, 2), (3, 2)
            ])
            draw_pixels([
                (-1, -1), (0, -1), (1, -2), (2, -2)
            ])
        elif tattoo_type == "dots":
            draw_pixels([(0, 0), (2, 1), (4, 2)])
        else:
            draw_pixels([(0, 0), (0, 1), (-1, 2), (0, 2), (1, 2), (0, 3)])

    def _render_cheekbones(self, canvas: Canvas) -> None:
        """Render cheekbone prominence with highlight and shadow shading."""
        prominence = self.config.cheekbone_prominence.lower()
        if prominence == "normal":
            return

        cx, cy = self._get_face_center()
        fw, fh = self._get_face_dimensions()

        # Eye positioning reference
        eye_y = cy - fh // 8
        eye_spacing = fw // 4

        # Cheekbone position: below outer eye area
        cheek_y = eye_y + fh // 6
        cheek_offset = eye_spacing + fw // 12

        # Get skin colors for blending
        light_skin = self._skin_ramp[-1]
        dark_skin = self._skin_ramp[1]

        # Prominence settings
        if prominence == "low":
            highlight_alpha = 15
            shadow_alpha = 10
            rx, ry = max(2, fw // 10), max(1, fh // 20)
        elif prominence == "high":
            highlight_alpha = 40
            shadow_alpha = 30
            rx, ry = max(4, fw // 7), max(2, fh // 14)
        elif prominence == "sculpted":
            highlight_alpha = 55
            shadow_alpha = 45
            rx, ry = max(5, fw // 6), max(3, fh // 12)
        else:
            return

        for side in (-1, 1):
            bone_cx = cx + side * cheek_offset

            # Highlight on top of cheekbone
            highlight_y = cheek_y - ry // 2
            for dy in range(-ry, ry + 1):
                for dx in range(-rx, rx + 1):
                    nx = dx / rx if rx > 0 else 0
                    ny = dy / ry if ry > 0 else 0
                    dist = nx * nx + ny * ny
                    if dist <= 1.0:
                        falloff = (1.0 - dist) ** 1.5
                        alpha = int(highlight_alpha * falloff)
                        if alpha > 0:
                            px, py = bone_cx + dx, highlight_y + dy
                            canvas.set_pixel(px, py, (*light_skin[:3], alpha))

            # Shadow below cheekbone
            shadow_y = cheek_y + ry
            shadow_ry = max(1, ry // 2)
            for dy in range(-shadow_ry, shadow_ry + 1):
                for dx in range(-rx, rx + 1):
                    nx = dx / rx if rx > 0 else 0
                    ny = dy / shadow_ry if shadow_ry > 0 else 0
                    dist = nx * nx + ny * ny
                    if dist <= 1.0:
                        falloff = (1.0 - dist) ** 1.5
                        alpha = int(shadow_alpha * falloff)
                        if alpha > 0:
                            px, py = bone_cx + dx, shadow_y + dy
                            canvas.set_pixel(px, py, (*dark_skin[:3], alpha))

    def _render_scar(self, canvas: Canvas) -> None:
        """Render a subtle facial scar line."""
        if not self.config.has_scar:
            return

        intensity = max(0.0, min(1.0, self.config.scar_intensity))
        if intensity <= 0.0:
            return

        cx, cy = self._get_face_center()
        fw, fh = self._get_face_dimensions()

        seed = self.config.seed
        rng = random.Random(seed + 3000) if seed is not None else random.Random()

        mid_idx = len(self._skin_ramp) // 2
        base_idx = min(len(self._skin_ramp) - 1, mid_idx + 1)
        base_color = self._skin_ramp[base_idx]
        scar_color = (
            min(255, base_color[0] + 12 + int(8 * intensity)),
            min(255, base_color[1] + 4),
            max(0, base_color[2] - 8),
        )

        base_alpha = int(40 + 120 * intensity)
        thickness = 2 if intensity > 0.7 and fw >= 90 else 1
        scar_type = (self.config.scar_type or "cheek").lower()
        side = rng.choice([-1, 1])

        def draw_line(x0: int, y0: int, x1: int, y1: int) -> None:
            steps = max(abs(x1 - x0), abs(y1 - y0))
            if steps == 0:
                canvas.set_pixel(x0, y0, (*scar_color, base_alpha))
                return

            skip_prob = 0.15 * (1.0 - intensity)
            for i in range(steps + 1):
                t = i / steps
                if skip_prob > 0 and rng.random() < skip_prob:
                    continue
                x = int(round(x0 + (x1 - x0) * t))
                y = int(round(y0 + (y1 - y0) * t))
                fade = math.sin(t * math.pi)
                alpha = int(base_alpha * (0.45 + 0.55 * fade))
                color = (*scar_color, alpha)
                for ox in range(-thickness + 1, thickness):
                    for oy in range(-thickness + 1, thickness):
                        if abs(ox) + abs(oy) <= thickness - 1:
                            canvas.set_pixel(x + ox, y + oy, color)

        if scar_type == "eyebrow":
            brow_y = cy - fh // 5
            eye_spacing = fw // 4
            brow_x = cx + side * eye_spacing
            start = (brow_x - side * 2, brow_y - 2)
            end = (brow_x + side * 3, brow_y + 6)
        elif scar_type == "lip":
            lip_y = cy + fh // 4
            offset_x = side * max(3, fw // 10)
            start = (cx + offset_x - side * 2, lip_y - 1)
            end = (cx + offset_x + side * 1, lip_y + max(2, fh // 24))
        elif scar_type == "forehead":
            forehead_y = cy - fh // 3
            length = max(6, int(fw * 0.22))
            center_x = cx + side * fw // 10
            start = (center_x - length // 2, forehead_y - 1)
            end = (center_x + length // 2, forehead_y + max(1, fh // 32))
        else:
            cheek_y = cy + fh // 10
            cheek_x = cx + side * fw // 5
            dx = max(4, int(fw * 0.08))
            dy = max(3, int(fh * 0.06))
            start = (cheek_x - side * dx, cheek_y - dy)
            end = (cheek_x + side * dx, cheek_y + dy)

        draw_line(start[0], start[1], end[0], end[1])

    def _render_eyebags(self, canvas: Canvas) -> None:
        """Render subtle dark semicircles under each eye."""
        if not self.config.has_eyebags:
            return

        intensity = max(0.0, min(1.0, self.config.eyebag_intensity))
        if intensity <= 0.0:
            return

        cx, cy = self._get_face_center()
        fw, fh = self._get_face_dimensions()

        # Eye positioning (matching _render_eyes)
        eye_y = self._get_eye_y(cy, fh)
        eye_spacing = fw // 4
        eye_width = fw // 6
        eye_height = int(eye_width * 0.6 * self.config.eye_openness)

        bag_width = max(2, int(eye_width * (0.45 + 0.25 * intensity)))
        bag_height = max(1, int(eye_height * (0.25 + 0.25 * intensity)))
        bag_offset_y = max(1, int(eye_height * 0.55))
        base_alpha = int(30 + 70 * intensity)

        mid_idx = len(self._skin_ramp) // 2
        shade_idx = max(0, mid_idx - 2)
        base_color = self._skin_ramp[shade_idx]

        for side in [-1, 1]:
            ex = cx + side * eye_spacing
            center_y = eye_y + bag_offset_y + bag_height // 2

            x_start = ex - bag_width - 1
            x_end = ex + bag_width + 2
            y_start = center_y - bag_height - 1
            y_end = center_y + bag_height + 2

            for py in range(y_start, y_end):
                if py < center_y:
                    continue
                for px in range(x_start, x_end):
                    if bag_width == 0 or bag_height == 0:
                        continue
                    nx = (px - ex) / bag_width
                    ny = (py - center_y) / bag_height
                    dist = nx * nx + ny * ny
                    if dist <= 1.0:
                        fade = max(0.0, 1.0 - dist)
                        alpha = int(base_alpha * (0.4 + 0.6 * fade))
                        if alpha > 0:
                            canvas.set_pixel(px, py, (*base_color[:3], alpha))

    def _render_wrinkles(self, canvas: Canvas) -> None:
        """Render wrinkle lines for an aged appearance."""
        if not self.config.has_wrinkles:
            return

        intensity = max(0.0, min(1.0, self.config.wrinkle_intensity))
        if intensity <= 0.0:
            return

        cx, cy = self._get_face_center()
        fw, fh = self._get_face_dimensions()
        areas = (self.config.wrinkle_areas or "all").lower()

        # Wrinkle color - slightly darker than skin
        mid_idx = len(self._skin_ramp) // 2
        shade_idx = max(0, mid_idx - 2)
        base_color = self._skin_ramp[shade_idx]
        base_alpha = int(40 + 80 * intensity)

        # Forehead wrinkles (horizontal lines)
        if areas in ("all", "forehead"):
            forehead_y = cy - fh // 3
            forehead_w = int(fw * 0.6)

            # 2-3 horizontal forehead lines
            num_lines = 2 if intensity < 0.7 else 3
            for i in range(num_lines):
                ly = forehead_y + i * int(fh * 0.05)
                line_w = int(forehead_w * (0.7 + 0.3 * (1 - i / num_lines)))

                for px in range(cx - line_w // 2, cx + line_w // 2):
                    # Slight wave in the line
                    wave = int(math.sin(px * 0.1) * 1.5)
                    py = ly + wave

                    if 0 <= px < canvas.width and 0 <= py < canvas.height:
                        # Fade at edges
                        dist_from_center = abs(px - cx) / (line_w / 2)
                        fade = 1.0 - dist_from_center ** 2
                        alpha = int(base_alpha * fade * 0.7)
                        if alpha > 0:
                            canvas.set_pixel(px, py, (*base_color[:3], alpha))

        # Crow's feet (lines at outer corners of eyes)
        if areas in ("all", "eyes"):
            eye_y = self._get_eye_y(cy, fh)
            eye_spacing = fw // 4
            eye_width = fw // 6

            for side in [-1, 1]:
                corner_x = cx + side * (eye_spacing + eye_width // 2)
                corner_y = eye_y

                # 2-4 radiating lines
                num_lines = 2 + int(intensity * 2)
                for i in range(num_lines):
                    angle = side * (0.3 + i * 0.15)  # Spread out from corner
                    line_len = int(fw * 0.06 * (1 + 0.5 * intensity))

                    for t in range(line_len):
                        px = int(corner_x + side * t * math.cos(angle))
                        py = int(corner_y + t * math.sin(angle) - t * 0.3)

                        if 0 <= px < canvas.width and 0 <= py < canvas.height:
                            fade = 1.0 - (t / line_len)
                            alpha = int(base_alpha * fade * 0.6)
                            if alpha > 0:
                                canvas.set_pixel(px, py, (*base_color[:3], alpha))

        # Nasolabial folds (lines from nose to mouth corners)
        if areas in ("all", "mouth"):
            nose_y = cy + fh // 16
            mouth_corner_y = cy + fh // 4
            nose_x_offset = fw // 12
            mouth_x_offset = fw // 6

            for side in [-1, 1]:
                start_x = cx + side * nose_x_offset
                start_y = nose_y
                end_x = cx + side * mouth_x_offset
                end_y = mouth_corner_y

                # Draw curved line
                steps = int(abs(end_y - start_y) * 1.5)
                for i in range(steps):
                    t = i / max(1, steps - 1)
                    # Curve outward then inward
                    curve = math.sin(t * math.pi) * fw * 0.02 * side
                    px = int(start_x + (end_x - start_x) * t + curve)
                    py = int(start_y + (end_y - start_y) * t)

                    if 0 <= px < canvas.width and 0 <= py < canvas.height:
                        # Stronger in middle, fade at ends
                        fade = math.sin(t * math.pi)
                        alpha = int(base_alpha * fade * 0.8)
                        if alpha > 0:
                            canvas.set_pixel(px, py, (*base_color[:3], alpha))

    def _render_eyes(self, canvas: Canvas) -> None:
        """Render detailed eyes with multiple layers."""
        cx, cy = self._get_face_center()
        fw, fh = self._get_face_dimensions()

        # Eye positioning
        eye_y = self._get_eye_y(cy, fh)
        eye_spacing = fw // 4
        size_mult = getattr(self.config, 'eye_size', 1.0)
        eye_width = int(fw // 6 * size_mult)
        eye_height = int(eye_width * 0.6 * self.config.eye_openness)

        for side in [-1, 1]:  # Left (-1) and right (1) eye
            ex = cx + side * eye_spacing

            # Select eye color ramp (heterochromia support)
            eye_ramp = self._right_eye_ramp if side == 1 else self._eye_ramp

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
            iris_outer = eye_ramp[0]  # Darkest
            iris_mid = eye_ramp[2]    # Middle
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

    def _render_eyeliner(self, canvas: Canvas) -> None:
        """Render eyeliner that follows the eye shape."""
        if not self.config.has_eyeliner:
            return

        cx, cy = self._get_face_center()
        fw, fh = self._get_face_dimensions()

        eye_y = self._get_eye_y(cy, fh)
        eye_spacing = fw // 4
        eye_width = max(1, fw // 6)
        eye_height = max(1, int(eye_width * 0.6 * self.config.eye_openness))

        style = self.config.eyeliner_style.lower()
        if style not in ("thin", "thick", "winged", "smoky"):
            style = "thin"

        base_color = EYELINER_COLORS.get(
            self.config.eyeliner_color.lower(),
            EYELINER_COLORS["black"],
        )

        thickness = 1 if style == "thin" else 2
        if style == "smoky":
            thickness = 3

        alpha = 200
        if style in ("thick", "winged"):
            alpha = 230
        elif style == "smoky":
            alpha = 170

        for side in (-1, 1):
            ex = cx + side * eye_spacing

            for dx in range(-eye_width, eye_width + 1):
                nx = dx / eye_width if eye_width else 0
                if nx * nx > 1.0:
                    continue
                top_y = -math.sqrt(1.0 - nx * nx) * eye_height
                py = eye_y + int(round(top_y))

                for t in range(thickness):
                    canvas.set_pixel(ex + dx, py + t, (*base_color, alpha))

                if style == "smoky":
                    for s in range(1, 3):
                        smoke_alpha = int(alpha * (0.4 / s))
                        if smoke_alpha > 0:
                            canvas.set_pixel(ex + dx, py - s, (*base_color, smoke_alpha))

            if style == "smoky":
                lower_alpha = int(alpha * 0.45)
                for dx in range(-eye_width + 1, eye_width):
                    nx = dx / eye_width if eye_width else 0
                    if nx * nx > 1.0:
                        continue
                    bottom_y = math.sqrt(1.0 - nx * nx) * eye_height
                    py = eye_y + int(round(bottom_y))
                    canvas.set_pixel(ex + dx, py, (*base_color, lower_alpha))

            if style == "winged":
                wing_len = max(2, int(eye_width * 0.45))
                wing_start_x = ex + side * eye_width
                wing_start_y = eye_y - max(1, int(eye_height * 0.3))
                for i in range(wing_len):
                    px = wing_start_x + side * i
                    py = wing_start_y - int(i * 0.5)
                    for t in range(thickness):
                        canvas.set_pixel(px, py + t, (*base_color, alpha))

    def _render_nose(self, canvas: Canvas) -> None:
        """Render nose with subtle shading based on nose type."""
        cx, cy = self._get_face_center()
        fw, fh = self._get_face_dimensions()

        # Apply nose size multiplier
        nose_size_mult = getattr(self.config, 'nose_size', 1.0)
        nose_y = cy + fh // 10

        # Nose shadow on one side (based on lighting)
        lx, _ = self.config.light_direction
        shadow_side = -1 if lx > 0 else 1

        mid_idx = len(self._skin_ramp) // 2
        shadow_color = (*self._skin_ramp[mid_idx - 1][:3], 60)
        highlight_color = (*self._skin_ramp[mid_idx + 1][:3], 50)
        dark_shadow = (*self._skin_ramp[mid_idx - 2][:3], 45)

        nose_type = self.config.nose_type

        if nose_type == NoseType.SMALL:
            # Small nose: minimal shadow, small highlight
            nose_height = int(fh // 10 * nose_size_mult)
            # Very subtle shadow line
            for dy in range(nose_height):
                py = nose_y + dy
                px = cx + shadow_side * 1
                canvas.set_pixel(px, py, (*shadow_color[:3], 40))
            # Small tip highlight
            canvas.set_pixel(cx, nose_y + nose_height - 1, highlight_color)

        elif nose_type == NoseType.BUTTON:
            # Button nose: round, prominent tip
            nose_height = int(fh // 9 * nose_size_mult)
            nose_width = fw // 14
            # Rounded shadow
            for dy in range(nose_height):
                t = dy / nose_height
                shadow_width = int(1 + t * 1.5)  # Widens toward tip
                py = nose_y + dy
                for sw in range(shadow_width):
                    canvas.set_pixel(cx + shadow_side * (1 + sw), py, shadow_color)
            # Round tip highlight (larger)
            tip_y = nose_y + nose_height - 1
            canvas.set_pixel(cx - 1, tip_y, highlight_color)
            canvas.set_pixel(cx, tip_y, highlight_color)
            canvas.set_pixel(cx + 1, tip_y, highlight_color)
            canvas.set_pixel(cx, tip_y - 1, highlight_color)

        elif nose_type == NoseType.POINTED:
            # Pointed nose: sharper, narrower shadow
            nose_height = int(fh // 7 * nose_size_mult)
            # Sharp, narrow shadow line
            for dy in range(nose_height):
                py = nose_y + dy
                px = cx + shadow_side * 2
                # Sharper contrast
                canvas.set_pixel(px, py, (*shadow_color[:3], 70))
            # Sharper bridge shadow
            for dy in range(nose_height // 2):
                canvas.set_pixel(cx + shadow_side, nose_y + dy, (*shadow_color[:3], 35))
            # Pointed tip highlight
            tip_y = nose_y + nose_height - 1
            canvas.set_pixel(cx, tip_y, highlight_color)
            canvas.set_pixel(cx, tip_y - 1, (*highlight_color[:3], 70))

        elif nose_type == NoseType.WIDE:
            # Wide nose: broader shadow area, larger nostrils hint
            nose_height = int(fh // 8 * nose_size_mult)
            nose_width = fw // 10
            # Wider shadow area
            for dy in range(nose_height):
                t = dy / nose_height
                shadow_width = int(1 + t * 2)  # Wider at bottom
                py = nose_y + dy
                for sw in range(shadow_width):
                    alpha = 60 - sw * 15
                    if alpha > 0:
                        canvas.set_pixel(cx + shadow_side * (2 + sw), py, (*shadow_color[:3], alpha))
            # Nostril hints
            nostril_y = nose_y + nose_height
            nostril_offset = nose_width // 2 + 1
            canvas.set_pixel(cx - nostril_offset, nostril_y, dark_shadow)
            canvas.set_pixel(cx + nostril_offset, nostril_y, dark_shadow)
            # Tip highlight
            canvas.set_pixel(cx - 1, nose_y + nose_height - 1, highlight_color)
            canvas.set_pixel(cx, nose_y + nose_height - 1, highlight_color)
            canvas.set_pixel(cx + 1, nose_y + nose_height - 1, highlight_color)

        else:
            # Default: basic small nose rendering
            nose_height = int(fh // 8 * nose_size_mult)
            for dy in range(nose_height):
                py = nose_y + dy
                px = cx + shadow_side * 2
                canvas.set_pixel(px, py, shadow_color)
            canvas.set_pixel(cx, nose_y + nose_height - 2, highlight_color)
            canvas.set_pixel(cx, nose_y + nose_height - 1, highlight_color)

    def _render_lips(self, canvas: Canvas) -> None:
        """Render lips with gradient and highlight."""
        cx, cy = self._get_face_center()
        fw, fh = self._get_face_dimensions()

        lip_y = cy + fh // 4
        lip_width = fw // 5
        base_lip_height = fh // 20
        thickness = getattr(self.config, 'lip_thickness', 1.0)
        lip_height = int(base_lip_height * thickness)
        shape = self.config.lip_shape
        lip_ramp = self._lip_ramp

        if self.config.has_lipstick:
            intensity = max(0.0, min(1.0, self.config.lipstick_intensity))
            if intensity > 0.0:
                lipstick_base = LIPSTICK_COLORS.get(
                    self.config.lipstick_color.lower(),
                    LIPSTICK_COLORS["red"]
                )
                lipstick_ramp = create_portrait_ramp(
                    (*lipstick_base, 255),
                    levels=len(self._lip_ramp)
                )
                vibrancy = getattr(self.config, 'color_vibrancy', 1.0)
                if vibrancy != 1.0:
                    lipstick_ramp = self._adjust_ramp_vibrancy(lipstick_ramp, vibrancy)
                blended = []
                for natural, lipstick in zip(self._lip_ramp, lipstick_ramp):
                    nr, ng, nb = natural[:3]
                    lr, lg, lb = lipstick[:3]
                    alpha = natural[3] if len(natural) > 3 else 255
                    blended.append((
                        int(nr + (lr - nr) * intensity),
                        int(ng + (lg - ng) * intensity),
                        int(nb + (lb - nb) * intensity),
                        alpha
                    ))
                lip_ramp = blended

        if shape == LipShape.NEUTRAL:
            # Keep the default rendering for neutral lips.
            upper_lip_color = lip_ramp[1]
            for dx in range(-lip_width, lip_width + 1):
                curve = int((1 - (dx / lip_width) ** 2) * lip_height * 0.5)
                for dy in range(curve):
                    canvas.set_pixel(cx + dx, lip_y - dy, upper_lip_color)

            lip_line_color = lip_ramp[0]
            for dx in range(-lip_width + 2, lip_width - 1):
                canvas.set_pixel(cx + dx, lip_y, lip_line_color)

            lower_lip_color = lip_ramp[2]
            highlight_color = lip_ramp[3]
            for dx in range(-lip_width + 1, lip_width):
                curve = int((1 - (dx / lip_width) ** 2) * lip_height * 0.8)
                for dy in range(1, curve + 1):
                    color = highlight_color if dy == 1 else lower_lip_color
                    canvas.set_pixel(cx + dx, lip_y + dy, color)
            return

        upper_scale = 0.5
        lower_scale = 0.8
        highlight_rows = 1
        highlight_span = lip_width - 1
        line_inset = 2
        cupid_width = 0
        cupid_depth = 0

        if shape == LipShape.THIN:
            lip_height = max(1, int(lip_height * 0.6))
            upper_scale = 0.35
            lower_scale = 0.5
            highlight_rows = 1
            highlight_span = max(1, lip_width // 2)
            line_inset = 3
        elif shape == LipShape.FULL:
            lip_height = max(2, int(lip_height * 1.4))
            upper_scale = 0.7
            lower_scale = 1.05
            highlight_rows = 2
            highlight_span = lip_width
            line_inset = 1
        elif shape == LipShape.HEART:
            lip_height = max(2, int(lip_height * 1.1))
            upper_scale = 0.6
            lower_scale = 0.85
            highlight_rows = 1
            highlight_span = max(1, lip_width - 2)
            line_inset = 2
            cupid_width = max(1, lip_width // 4)
            cupid_depth = max(1, int(lip_height * 0.35))

        upper_lip_color = lip_ramp[1]
        for dx in range(-lip_width, lip_width + 1):
            curve = int((1 - (dx / lip_width) ** 2) * lip_height * upper_scale)
            if shape == LipShape.HEART and abs(dx) <= cupid_width:
                dip = int((1 - (abs(dx) / cupid_width)) * cupid_depth)
                curve = max(0, curve - dip)
            for dy in range(curve):
                canvas.set_pixel(cx + dx, lip_y - dy, upper_lip_color)

        lip_line_color = lip_ramp[0]
        for dx in range(-lip_width + line_inset, lip_width - line_inset + 1):
            canvas.set_pixel(cx + dx, lip_y, lip_line_color)

        lower_lip_color = lip_ramp[2]
        highlight_color = lip_ramp[3]
        for dx in range(-lip_width + 1, lip_width):
            curve = int((1 - (dx / lip_width) ** 2) * lip_height * lower_scale)
            for dy in range(1, curve + 1):
                if dy <= highlight_rows and abs(dx) <= highlight_span:
                    color = highlight_color
                else:
                    color = lower_lip_color
                canvas.set_pixel(cx + dx, lip_y + dy, color)

    def _render_teeth(self, canvas: Canvas) -> None:
        """Render teeth visible through smile gap."""
        if not self.config.show_teeth:
            return

        # Only show teeth for certain expressions
        expression = (self.config.expression or "neutral").lower()
        if expression not in ("happy", "surprised", "loving"):
            return

        cx, cy = self._get_face_center()
        fw, fh = self._get_face_dimensions()

        lip_y = cy + fh // 4
        lip_width = fw // 5
        teeth_height = max(2, fh // 25)

        # Teeth color based on whiteness
        whiteness = self.config.teeth_whiteness
        base_white = int(200 + 55 * whiteness)
        teeth_color = (base_white, base_white, int(base_white * 0.95), 255)
        gum_color = (180, 120, 120, 200)

        # Draw teeth in the gap where mouth opens
        teeth_width = int(lip_width * 0.7)
        gap_start = lip_y + 1

        # Upper teeth row
        for dx in range(-teeth_width, teeth_width + 1):
            # Slight curve for teeth row
            curve = int((1 - (dx / teeth_width) ** 2) * teeth_height * 0.4)
            for dy in range(teeth_height - curve):
                px = cx + dx
                py = gap_start + dy

                # Draw individual teeth with gaps
                tooth_width = max(2, teeth_width // 3)
                within_tooth = (dx + teeth_width) % tooth_width != 0

                if within_tooth:
                    canvas.set_pixel(px, py, teeth_color)
                else:
                    # Slight gap between teeth
                    canvas.set_pixel(px, py, gum_color)

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

                # Draw eyebrow with configurable thickness
                thickness = getattr(self.config, 'eyebrow_thickness', 2)
                for ty in range(thickness):
                    canvas.set_pixel(px, py + ty, brow_color)

    def _render_piercings(self, canvas: Canvas) -> None:
        """Render facial piercings if configured."""
        if not (self.config.has_nose_piercing or self.config.has_eyebrow_piercing or self.config.has_lip_piercing):
            return

        color_key = (self.config.piercing_color or "silver").lower()
        base_color = {
            "silver": (200, 200, 210, 255),
            "gold": (255, 215, 0, 255),
            "black": (40, 40, 45, 255),
        }.get(color_key, (200, 200, 210, 255))

        highlight = (
            min(255, base_color[0] + 40),
            min(255, base_color[1] + 40),
            min(255, base_color[2] + 40),
            255,
        )
        shadow = (
            max(0, base_color[0] - 30),
            max(0, base_color[1] - 30),
            max(0, base_color[2] - 30),
            255,
        )

        cx, cy = self._get_face_center()
        fw, fh = self._get_face_dimensions()

        if self.config.has_nose_piercing:
            nose_y = cy + fh // 10
            nose_height = max(4, fh // 9)
            nostril_offset = max(2, fw // 12)
            pierce_type = (self.config.nose_piercing_type or "stud").lower()
            px = cx - nostril_offset
            py = nose_y + nose_height - 1

            if pierce_type == "septum":
                ring_y = nose_y + nose_height
                canvas.set_pixel(cx - 1, ring_y, shadow)
                canvas.set_pixel(cx + 1, ring_y, shadow)
                canvas.set_pixel(cx, ring_y + 1, base_color)
                canvas.set_pixel(cx, ring_y, highlight)
            elif pierce_type == "ring":
                canvas.set_pixel(px, py - 1, base_color)
                canvas.set_pixel(px, py, base_color)
                canvas.set_pixel(px, py + 1, base_color)
                canvas.set_pixel(px + 1, py, highlight)
            else:
                canvas.set_pixel(px, py, base_color)
                canvas.set_pixel(px + 1, py, highlight)

        if self.config.has_eyebrow_piercing:
            brow_y = cy - fh // 5
            eye_spacing = fw // 4
            brow_width = fw // 6
            half_width = brow_width // 2
            side = 1
            brow_x = cx + side * eye_spacing
            px = brow_x + side * (half_width - 1)
            py = brow_y + int(self.config.eyebrow_angle * 4) - 1

            canvas.set_pixel(px, py, base_color)
            canvas.set_pixel(px + side * 2, py + 1, base_color)
            canvas.set_pixel(px + side, py, highlight)

        if self.config.has_lip_piercing:
            lip_y = cy + fh // 4
            lip_width = fw // 5
            pierce_type = (self.config.lip_piercing_type or "stud").lower()

            if pierce_type == "labret":
                px = cx
                py = lip_y + max(2, fh // 18)
                canvas.set_pixel(px, py, base_color)
                canvas.set_pixel(px + 1, py, highlight)
            elif pierce_type == "ring":
                px = cx + max(2, lip_width // 2)
                py = lip_y + 1
                canvas.set_pixel(px, py - 1, base_color)
                canvas.set_pixel(px, py, base_color)
                canvas.set_pixel(px, py + 1, base_color)
                canvas.set_pixel(px + 1, py, highlight)
            else:
                px = cx + max(2, lip_width // 2)
                py = lip_y + 1
                canvas.set_pixel(px, py, base_color)
                canvas.set_pixel(px + 1, py, highlight)

    def _render_hair(self, canvas: Canvas) -> None:
        """Render back hair using bezier-based cluster system."""
        from generators.portrait_parts.hair import (
            render_hair,
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

        # Determine highlight parameters
        highlight_ramp = None
        highlight_intensity = 0.0
        if self.config.has_hair_highlights:
            highlight_ramp = self._highlight_ramp
            highlight_intensity = self.config.highlight_intensity

        segments = self._get_hair_parting_segments(float(cx), float(hair_width))
        if len(segments) == 1:
            render_hair(
                canvas=canvas,
                style=hair_style,
                center_x=float(cx),
                top_y=float(hair_top),
                width=float(hair_width),
                length=float(hair_length),
                color_ramp=self._hair_ramp,
                light_direction=self.config.light_direction,
                count=cluster_count,
                seed=self.config.seed,
                include_strays=True,
                highlight_ramp=highlight_ramp,
                highlight_intensity=highlight_intensity,
            )
            return

        total_width = sum(segment_width for _, segment_width in segments)
        for index, (segment_center, segment_width) in enumerate(segments):
            ratio = segment_width / total_width if total_width > 0 else 0.5
            segment_count = max(3, int(round(cluster_count * ratio)))
            segment_seed = None
            if self.config.seed is not None:
                segment_seed = self.config.seed + 2000 + index * 137

            render_hair(
                canvas=canvas,
                style=hair_style,
                center_x=float(segment_center),
                top_y=float(hair_top),
                width=float(segment_width),
                length=float(hair_length),
                color_ramp=self._hair_ramp,
                light_direction=self.config.light_direction,
                count=segment_count,
                seed=segment_seed,
                include_strays=True,
                highlight_ramp=highlight_ramp,
                highlight_intensity=highlight_intensity,
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
        segments = self._get_hair_parting_segments(float(cx), float(bangs_width))
        if len(segments) == 1:
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
        else:
            bangs = []
            total_width = sum(segment_width for _, segment_width in segments)
            for index, (segment_center, segment_width) in enumerate(segments):
                ratio = segment_width / total_width if total_width > 0 else 0.5
                segment_count = max(2, int(round(bangs_count * ratio)))
                segment_seed = None
                if bangs_seed is not None:
                    segment_seed = bangs_seed + index * 113
                segment_rng = random.Random(segment_seed)

                bangs.extend(generate_bangs_clusters(
                    center_x=float(segment_center),
                    forehead_y=float(forehead_y),
                    width=float(segment_width),
                    length=float(bangs_length),
                    count=segment_count,
                    style=hair_style,
                    rng=segment_rng
                ))

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
        eye_y = self._get_eye_y(cy, fh)
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

    def _render_necklace(self, canvas: Canvas) -> None:
        """Render necklace if configured."""
        if not self.config.has_necklace:
            return

        from generators.portrait_parts.accessories import (
            render_necklace, NecklaceStyle
        )

        cx, cy = self._get_face_center()
        fw, fh = self._get_face_dimensions()

        # Necklace position - at the neckline
        neck_y = cy + fh // 2
        neck_width = fw // 2

        # Map style string to enum
        style_map = {
            "chain": NecklaceStyle.CHAIN,
            "choker": NecklaceStyle.CHOKER,
            "pendant": NecklaceStyle.PENDANT,
            "pearl": NecklaceStyle.PEARL,
        }
        necklace_style = style_map.get(
            self.config.necklace_style.lower(),
            NecklaceStyle.CHAIN
        )

        # Necklace colors based on style
        necklace_colors = {
            "chain": (255, 215, 0, 255),      # Gold
            "choker": (30, 30, 35, 255),       # Black
            "pendant": (200, 200, 210, 255),   # Silver
            "pearl": (250, 245, 235, 255),     # Pearl white
        }
        color = necklace_colors.get(
            self.config.necklace_style.lower(),
            (255, 215, 0, 255)
        )

        # Size scales with face
        size = max(2, fw // 30)

        render_necklace(canvas, cx, neck_y, neck_width, necklace_style, color, size)

    def _render_hair_accessory(self, canvas: Canvas) -> None:
        """Render hair accessory if configured."""
        if not self.config.has_hair_accessory:
            return

        from generators.portrait_parts.accessories import (
            render_hair_accessory, HairAccessoryStyle
        )

        cx, cy = self._get_face_center()
        fw, fh = self._get_face_dimensions()

        # Hair accessory position - at top of hair
        hair_top_y = cy - fh // 2 - fh // 4
        hair_width = fw

        # Map style string to enum
        style_map = {
            "headband": HairAccessoryStyle.HEADBAND,
            "bow": HairAccessoryStyle.BOW,
            "clip": HairAccessoryStyle.CLIP,
            "scrunchie": HairAccessoryStyle.SCRUNCHIE,
        }
        accessory_style = style_map.get(
            self.config.hair_accessory_style.lower(),
            HairAccessoryStyle.HEADBAND
        )

        # Color - use configured color or default
        if self.config.hair_accessory_color:
            color_map = {
                "pink": (255, 150, 180, 255),
                "red": (220, 60, 80, 255),
                "blue": (100, 150, 255, 255),
                "purple": (180, 100, 220, 255),
                "white": (250, 250, 255, 255),
                "black": (40, 35, 40, 255),
                "gold": (255, 215, 0, 255),
                "green": (100, 200, 120, 255),
            }
            color = color_map.get(
                self.config.hair_accessory_color.lower(),
                (255, 150, 180, 255)
            )
        else:
            color = (255, 150, 180, 255)  # Default pink

        # Size scales with face
        size = max(2, fw // 25)

        render_hair_accessory(canvas, cx, hair_top_y, hair_width, accessory_style, color, size)

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
        self._render_necklace(canvas)  # Necklace on top of clothing
        self._render_hair(canvas)  # Back hair with cluster system
        self._render_face_base(canvas)
        self._render_cheekbones(canvas)  # Cheekbone shading
        self._render_ears(canvas)
        self._render_blush(canvas)
        self._render_dimples(canvas)
        self._render_wrinkles(canvas)  # Age lines on face
        self._render_eyebags(canvas)
        self._render_freckles(canvas)
        self._render_moles(canvas)
        self._render_beauty_mark(canvas)
        self._render_nose(canvas)
        self._render_teeth(canvas)  # Teeth behind lips (visible when smiling)
        self._render_lips(canvas)
        self._render_facial_hair(canvas)  # Facial hair below face
        self._render_eyes(canvas)
        self._render_eyeliner(canvas)
        self._render_eyebrows(canvas)
        self._render_scar(canvas)
        self._render_piercings(canvas)
        self._render_earrings(canvas)  # Earrings on side of face
        self._render_face_tattoo(canvas)
        self._render_glasses(canvas)  # Glasses over eyes
        self._render_bangs(canvas)  # Front hair over forehead
        self._render_hair_accessory(canvas)  # Hair accessories on top

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

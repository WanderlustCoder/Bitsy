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

    # Accessories
    has_glasses: bool = False
    glasses_style: str = "round"
    has_earrings: bool = False
    earring_style: str = "stud"

    # Clothing
    clothing_style: str = "casual"
    clothing_color: str = "blue"

    # Lighting
    light_direction: Tuple[float, float] = (1.0, -1.0)  # (x, y) normalized

    # Quality
    shading_levels: int = 7  # Number of colors in shading ramps


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
                       gaze: Tuple[float, float] = (0.0, 0.0)) -> 'PortraitGenerator':
        """Set facial expression and gaze direction."""
        self.config.expression = expression
        self.config.gaze_direction = gaze
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
        """Render the base face shape with shading."""
        cx, cy = self._get_face_center()
        fw, fh = self._get_face_dimensions()

        # Base skin color (middle of ramp)
        mid_idx = len(self._skin_ramp) // 2
        base_color = self._skin_ramp[mid_idx]

        # Draw oval face shape
        canvas.fill_ellipse_aa(cx, cy, fw // 2, fh // 2, base_color)

        # Apply basic shading based on light direction
        lx, ly = self.config.light_direction

        # Shadow side
        shadow_color = self._skin_ramp[mid_idx - 2]
        if lx > 0:
            # Light from right, shadow on left
            shadow_cx = cx - fw // 6
        else:
            shadow_cx = cx + fw // 6

        # Subtle shadow on opposite side of light
        shadow_rx = fw // 4
        shadow_ry = fh // 3
        # Draw with reduced alpha for subtle effect
        shadow_with_alpha = (*shadow_color[:3], 80)
        canvas.fill_ellipse_aa(shadow_cx, cy, shadow_rx, shadow_ry, shadow_with_alpha)

        # Highlight on light side
        highlight_color = self._skin_ramp[mid_idx + 2]
        if lx > 0:
            highlight_cx = cx + fw // 5
        else:
            highlight_cx = cx - fw // 5
        highlight_cy = cy - fh // 6

        highlight_with_alpha = (*highlight_color[:3], 60)
        canvas.fill_ellipse_aa(highlight_cx, highlight_cy, fw // 6, fh // 6, highlight_with_alpha)

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

    def _render_eyebrows(self, canvas: Canvas) -> None:
        """Render eyebrows."""
        cx, cy = self._get_face_center()
        fw, fh = self._get_face_dimensions()

        brow_y = cy - fh // 5
        eye_spacing = fw // 4
        brow_width = fw // 6

        # Eyebrow color (darker than hair)
        brow_color = self._hair_ramp[0]  # Darkest hair color

        for side in [-1, 1]:
            brow_x = cx + side * eye_spacing

            # Simple arch shape
            for dx in range(-brow_width // 2, brow_width // 2 + 1):
                # Arch curve
                arch = int(abs(dx) * 0.3)
                px = brow_x + dx
                py = brow_y + arch

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
            HairStyle.PONYTAIL: HairStyleParts.WAVY,
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
        self._render_clothing(canvas)  # Clothing behind everything
        self._render_hair(canvas)  # Back hair with cluster system
        self._render_face_base(canvas)
        self._render_nose(canvas)
        self._render_lips(canvas)
        self._render_eyes(canvas)
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

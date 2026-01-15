"""
Style - Art style configurations for pixel art generation.

Defines rendering styles including outlines, shading, and color constraints.
Styles can be used by generators to produce consistent art across assets.
"""

from typing import Optional, Tuple, List, Dict, Any
from dataclasses import dataclass, field
from .color import Color, darken, lighten, shift_hue, adjust_saturation


@dataclass
class OutlineConfig:
    """Configuration for sprite outlines."""

    enabled: bool = True
    color: Optional[Color] = None  # None = derive from fill color
    mode: str = 'external'  # 'all', 'external', 'internal', 'none'
    thickness: int = 1
    darken_factor: float = 0.4  # How much to darken fill for auto-outline


@dataclass
class ShadingConfig:
    """Configuration for shading and lighting."""

    mode: str = 'cel'  # 'flat', 'cel', 'gradient', 'dither'
    levels: int = 3  # Number of shading levels (for cel shading)
    light_direction: Tuple[float, float] = (1.0, -1.0)  # Light source direction

    # Hue shifting
    highlight_hue_shift: float = 15.0  # Degrees toward warm (yellow/orange)
    shadow_hue_shift: float = -20.0  # Degrees toward cool (blue/purple)

    # Saturation
    highlight_saturation: float = 0.9  # Slightly less saturated highlights
    shadow_saturation: float = 0.85  # Desaturate shadows

    # Value/brightness
    highlight_value: float = 1.3  # Brighten highlights
    shadow_value: float = 0.6  # Darken shadows

    # Dithering (when mode='dither')
    dither_pattern: str = 'bayer4x4'  # 'checker', 'bayer2x2', 'bayer4x4', 'bayer8x8'


@dataclass
class PaletteConfig:
    """Configuration for palette constraints."""

    max_colors: Optional[int] = None  # None = unlimited
    global_palette: Optional[List[Color]] = None  # Force quantization to palette
    per_sprite_colors: Optional[int] = None  # Max colors per individual sprite

    # Retro constraints
    enforce_hardware_palette: bool = False
    hardware_palette_name: Optional[str] = None  # 'nes', 'gameboy', 'snes', etc.


@dataclass
class Style:
    """Complete art style configuration."""

    name: str = 'custom'

    # Component configurations
    outline: OutlineConfig = field(default_factory=OutlineConfig)
    shading: ShadingConfig = field(default_factory=ShadingConfig)
    palette: PaletteConfig = field(default_factory=PaletteConfig)

    # General style properties
    pixel_perfect: bool = True  # Enforce integer coordinates
    anti_alias: bool = False  # Allow anti-aliasing
    subpixel: bool = False  # Allow sub-pixel positioning

    # Proportions (for character generation)
    head_ratio: float = 0.3  # Head size relative to body
    eye_size: str = 'medium'  # 'tiny', 'small', 'medium', 'large', 'huge'
    limb_style: str = 'normal'  # 'stub', 'simple', 'normal', 'detailed'

    # Animation hints
    squash_stretch: float = 0.0  # Amount of squash/stretch (0-1)
    follow_through: float = 0.0  # Secondary motion amount (0-1)

    def get_highlight_color(self, base: Color) -> Color:
        """Generate highlight color from base color using style settings.

        Args:
            base: Base color to derive highlight from

        Returns:
            Highlight color
        """
        color = base
        if self.shading.highlight_hue_shift != 0:
            color = shift_hue(color, self.shading.highlight_hue_shift)
        if self.shading.highlight_saturation != 1.0:
            color = adjust_saturation(color, self.shading.highlight_saturation)
        color = lighten(color, 1.0 - (1.0 / self.shading.highlight_value))
        return color

    def get_shadow_color(self, base: Color) -> Color:
        """Generate shadow color from base color using style settings.

        Args:
            base: Base color to derive shadow from

        Returns:
            Shadow color
        """
        color = base
        if self.shading.shadow_hue_shift != 0:
            color = shift_hue(color, self.shading.shadow_hue_shift)
        if self.shading.shadow_saturation != 1.0:
            color = adjust_saturation(color, self.shading.shadow_saturation)
        color = darken(color, 1.0 - self.shading.shadow_value)
        return color

    def get_outline_color(self, fill_color: Color) -> Color:
        """Get outline color for a given fill color.

        Args:
            fill_color: The fill color to outline

        Returns:
            Outline color
        """
        if not self.outline.enabled:
            return (0, 0, 0, 0)
        if self.outline.color is not None:
            return self.outline.color
        return darken(fill_color, self.outline.darken_factor)

    def get_shading_colors(self, base: Color, num_levels: Optional[int] = None) -> List[Color]:
        """Generate a ramp of shading colors from highlight to shadow.

        Args:
            base: Base/mid-tone color
            num_levels: Number of levels (default: self.shading.levels)

        Returns:
            List of colors from highlight to shadow
        """
        levels = num_levels or self.shading.levels
        if levels < 2:
            return [base]

        highlight = self.get_highlight_color(base)
        shadow = self.get_shadow_color(base)

        colors = []
        for i in range(levels):
            t = i / (levels - 1)
            # Interpolate from highlight through base to shadow
            if t < 0.5:
                # Highlight to base
                t2 = t * 2
                from .color import lerp_color
                colors.append(lerp_color(highlight, base, t2))
            else:
                # Base to shadow
                t2 = (t - 0.5) * 2
                from .color import lerp_color
                colors.append(lerp_color(base, shadow, t2))

        return colors

    def copy(self) -> 'Style':
        """Create a copy of this style."""
        return Style(
            name=self.name,
            outline=OutlineConfig(
                enabled=self.outline.enabled,
                color=self.outline.color,
                mode=self.outline.mode,
                thickness=self.outline.thickness,
                darken_factor=self.outline.darken_factor
            ),
            shading=ShadingConfig(
                mode=self.shading.mode,
                levels=self.shading.levels,
                light_direction=self.shading.light_direction,
                highlight_hue_shift=self.shading.highlight_hue_shift,
                shadow_hue_shift=self.shading.shadow_hue_shift,
                highlight_saturation=self.shading.highlight_saturation,
                shadow_saturation=self.shading.shadow_saturation,
                highlight_value=self.shading.highlight_value,
                shadow_value=self.shading.shadow_value,
                dither_pattern=self.shading.dither_pattern
            ),
            palette=PaletteConfig(
                max_colors=self.palette.max_colors,
                global_palette=self.palette.global_palette,
                per_sprite_colors=self.palette.per_sprite_colors,
                enforce_hardware_palette=self.palette.enforce_hardware_palette,
                hardware_palette_name=self.palette.hardware_palette_name
            ),
            pixel_perfect=self.pixel_perfect,
            anti_alias=self.anti_alias,
            subpixel=self.subpixel,
            head_ratio=self.head_ratio,
            eye_size=self.eye_size,
            limb_style=self.limb_style,
            squash_stretch=self.squash_stretch,
            follow_through=self.follow_through
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize style to dictionary."""
        return {
            'name': self.name,
            'outline': {
                'enabled': self.outline.enabled,
                'color': self.outline.color,
                'mode': self.outline.mode,
                'thickness': self.outline.thickness,
                'darken_factor': self.outline.darken_factor
            },
            'shading': {
                'mode': self.shading.mode,
                'levels': self.shading.levels,
                'light_direction': self.shading.light_direction,
                'highlight_hue_shift': self.shading.highlight_hue_shift,
                'shadow_hue_shift': self.shading.shadow_hue_shift,
                'highlight_saturation': self.shading.highlight_saturation,
                'shadow_saturation': self.shading.shadow_saturation,
                'highlight_value': self.shading.highlight_value,
                'shadow_value': self.shading.shadow_value,
                'dither_pattern': self.shading.dither_pattern
            },
            'palette': {
                'max_colors': self.palette.max_colors,
                'per_sprite_colors': self.palette.per_sprite_colors,
                'hardware_palette_name': self.palette.hardware_palette_name
            },
            'pixel_perfect': self.pixel_perfect,
            'anti_alias': self.anti_alias,
            'head_ratio': self.head_ratio,
            'eye_size': self.eye_size,
            'limb_style': self.limb_style
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Style':
        """Create style from dictionary."""
        style = cls(name=data.get('name', 'custom'))

        if 'outline' in data:
            o = data['outline']
            style.outline = OutlineConfig(
                enabled=o.get('enabled', True),
                color=tuple(o['color']) if o.get('color') else None,
                mode=o.get('mode', 'external'),
                thickness=o.get('thickness', 1),
                darken_factor=o.get('darken_factor', 0.4)
            )

        if 'shading' in data:
            s = data['shading']
            style.shading = ShadingConfig(
                mode=s.get('mode', 'cel'),
                levels=s.get('levels', 3),
                light_direction=tuple(s.get('light_direction', (1.0, -1.0))),
                highlight_hue_shift=s.get('highlight_hue_shift', 15.0),
                shadow_hue_shift=s.get('shadow_hue_shift', -20.0),
                highlight_saturation=s.get('highlight_saturation', 0.9),
                shadow_saturation=s.get('shadow_saturation', 0.85),
                highlight_value=s.get('highlight_value', 1.3),
                shadow_value=s.get('shadow_value', 0.6),
                dither_pattern=s.get('dither_pattern', 'bayer4x4')
            )

        if 'palette' in data:
            p = data['palette']
            style.palette = PaletteConfig(
                max_colors=p.get('max_colors'),
                per_sprite_colors=p.get('per_sprite_colors'),
                hardware_palette_name=p.get('hardware_palette_name')
            )

        style.pixel_perfect = data.get('pixel_perfect', True)
        style.anti_alias = data.get('anti_alias', False)
        style.subpixel = data.get('subpixel', False)
        style.head_ratio = data.get('head_ratio', 0.3)
        style.eye_size = data.get('eye_size', 'medium')
        style.limb_style = data.get('limb_style', 'normal')
        style.squash_stretch = data.get('squash_stretch', 0.0)
        style.follow_through = data.get('follow_through', 0.0)

        return style

    # =========================================================================
    # Style Presets
    # =========================================================================

    @classmethod
    def chibi(cls) -> 'Style':
        """Cute chibi/anime style with big heads and simple limbs.

        Characteristics:
        - Large head (40-50% of height)
        - Big expressive eyes
        - Simple tube/stub limbs
        - Soft outlines (not black)
        - Cel shading with 2-3 tones
        - Warm highlights, cool shadows
        """
        return cls(
            name='chibi',
            outline=OutlineConfig(
                enabled=True,
                color=None,  # Derive from fill
                mode='external',
                thickness=1,
                darken_factor=0.35  # Soft outline
            ),
            shading=ShadingConfig(
                mode='cel',
                levels=3,
                light_direction=(1.0, -1.0),
                highlight_hue_shift=12.0,  # Slightly warm
                shadow_hue_shift=-15.0,  # Slightly cool
                highlight_saturation=0.95,
                shadow_saturation=0.9,
                highlight_value=1.25,
                shadow_value=0.65
            ),
            palette=PaletteConfig(
                max_colors=None,
                per_sprite_colors=None
            ),
            pixel_perfect=True,
            anti_alias=False,
            head_ratio=0.45,  # Big head
            eye_size='large',
            limb_style='simple',
            squash_stretch=0.15,
            follow_through=0.1
        )

    @classmethod
    def retro_nes(cls) -> 'Style':
        """NES-era 8-bit style with strict limitations.

        Characteristics:
        - 4 colors per sprite (including transparent)
        - Hard black outlines
        - Flat or simple 2-tone shading
        - Dithering for gradients
        - 8x8 or 8x16 tiles
        - Limited 52-54 color master palette
        """
        from .color import hex_to_rgba

        # NES palette subset (common colors)
        nes_palette = [
            hex_to_rgba('#000000'),  # Black
            hex_to_rgba('#fcfcfc'),  # White
            hex_to_rgba('#f8f8f8'),  # Light gray
            hex_to_rgba('#bcbcbc'),  # Mid gray
            hex_to_rgba('#7c7c7c'),  # Dark gray
            hex_to_rgba('#a4e4fc'),  # Light blue
            hex_to_rgba('#3cbcfc'),  # Blue
            hex_to_rgba('#0078f8'),  # Dark blue
            hex_to_rgba('#0000fc'),  # Pure blue
            hex_to_rgba('#b8f8b8'),  # Light green
            hex_to_rgba('#58d854'),  # Green
            hex_to_rgba('#008200'),  # Dark green
            hex_to_rgba('#f8d8f8'),  # Light pink
            hex_to_rgba('#f878f8'),  # Pink
            hex_to_rgba('#9878f8'),  # Purple
            hex_to_rgba('#6844fc'),  # Dark purple
            hex_to_rgba('#f8b8f8'),  # Light magenta
            hex_to_rgba('#f85898'),  # Red
            hex_to_rgba('#e40058'),  # Dark red
            hex_to_rgba('#f8d878'),  # Yellow
            hex_to_rgba('#f8a100'),  # Orange
            hex_to_rgba('#c84c0c'),  # Brown
        ]

        return cls(
            name='retro_nes',
            outline=OutlineConfig(
                enabled=True,
                color=(0, 0, 0, 255),  # Black outlines
                mode='all',
                thickness=1,
                darken_factor=1.0
            ),
            shading=ShadingConfig(
                mode='flat',  # Flat shading, maybe 2 tones
                levels=2,
                light_direction=(1.0, -1.0),
                highlight_hue_shift=0.0,  # No hue shift
                shadow_hue_shift=0.0,
                highlight_saturation=1.0,
                shadow_saturation=1.0,
                highlight_value=1.0,
                shadow_value=0.7,
                dither_pattern='checker'
            ),
            palette=PaletteConfig(
                max_colors=54,
                global_palette=nes_palette,
                per_sprite_colors=4,  # 3 colors + transparent
                enforce_hardware_palette=True,
                hardware_palette_name='nes'
            ),
            pixel_perfect=True,
            anti_alias=False,
            head_ratio=0.35,
            eye_size='small',
            limb_style='stub',
            squash_stretch=0.0,
            follow_through=0.0
        )

    @classmethod
    def retro_snes(cls) -> 'Style':
        """SNES-era 16-bit style with more colors.

        Characteristics:
        - 16 colors per sprite
        - More detailed shading (3-4 levels)
        - Optional anti-aliased outlines
        - Richer color gradients
        - Some hue shifting allowed
        """
        return cls(
            name='retro_snes',
            outline=OutlineConfig(
                enabled=True,
                color=None,
                mode='external',
                thickness=1,
                darken_factor=0.5
            ),
            shading=ShadingConfig(
                mode='cel',
                levels=4,
                light_direction=(1.0, -1.0),
                highlight_hue_shift=8.0,  # Subtle warm
                shadow_hue_shift=-10.0,  # Subtle cool
                highlight_saturation=0.95,
                shadow_saturation=0.9,
                highlight_value=1.2,
                shadow_value=0.55,
                dither_pattern='bayer2x2'
            ),
            palette=PaletteConfig(
                max_colors=256,
                per_sprite_colors=16,
                enforce_hardware_palette=True,
                hardware_palette_name='snes'
            ),
            pixel_perfect=True,
            anti_alias=False,
            head_ratio=0.32,
            eye_size='medium',
            limb_style='simple',
            squash_stretch=0.05,
            follow_through=0.05
        )

    @classmethod
    def retro_gameboy(cls) -> 'Style':
        """Game Boy style with 4 shades of green.

        Characteristics:
        - Exactly 4 colors (green palette)
        - High contrast
        - Very simple shapes
        - Dithering essential for gradients
        """
        from .color import hex_to_rgba

        gb_palette = [
            hex_to_rgba('#0f380f'),  # Darkest green
            hex_to_rgba('#306230'),  # Dark green
            hex_to_rgba('#8bac0f'),  # Light green
            hex_to_rgba('#9bbc0f'),  # Lightest green
        ]

        return cls(
            name='retro_gameboy',
            outline=OutlineConfig(
                enabled=True,
                color=hex_to_rgba('#0f380f'),  # Darkest green
                mode='external',
                thickness=1,
                darken_factor=1.0
            ),
            shading=ShadingConfig(
                mode='dither',
                levels=4,
                light_direction=(1.0, -1.0),
                highlight_hue_shift=0.0,
                shadow_hue_shift=0.0,
                highlight_saturation=1.0,
                shadow_saturation=1.0,
                highlight_value=1.0,
                shadow_value=1.0,
                dither_pattern='bayer2x2'
            ),
            palette=PaletteConfig(
                max_colors=4,
                global_palette=gb_palette,
                per_sprite_colors=4,
                enforce_hardware_palette=True,
                hardware_palette_name='gameboy'
            ),
            pixel_perfect=True,
            anti_alias=False,
            head_ratio=0.4,
            eye_size='tiny',
            limb_style='stub',
            squash_stretch=0.0,
            follow_through=0.0
        )

    @classmethod
    def modern_hd(cls) -> 'Style':
        """Modern high-resolution pixel art style.

        Characteristics:
        - Unlimited colors
        - Detailed shading with hue shifts
        - Selective/soft outlines
        - Sub-pixel detail allowed
        - High resolution (64x64+)
        - Smooth gradients
        """
        return cls(
            name='modern_hd',
            outline=OutlineConfig(
                enabled=True,
                color=None,
                mode='external',  # Selective outline
                thickness=1,
                darken_factor=0.25  # Very soft
            ),
            shading=ShadingConfig(
                mode='gradient',
                levels=5,
                light_direction=(1.0, -1.0),
                highlight_hue_shift=18.0,  # Warm highlights
                shadow_hue_shift=-25.0,  # Cool shadows
                highlight_saturation=0.85,  # Slightly desaturated
                shadow_saturation=0.8,
                highlight_value=1.35,
                shadow_value=0.5,
                dither_pattern='bayer4x4'
            ),
            palette=PaletteConfig(
                max_colors=None,  # Unlimited
                per_sprite_colors=None
            ),
            pixel_perfect=True,
            anti_alias=False,  # Still pixel art
            subpixel=False,
            head_ratio=0.28,  # More realistic proportions
            eye_size='medium',
            limb_style='detailed',
            squash_stretch=0.2,
            follow_through=0.15
        )

    @classmethod
    def minimalist(cls) -> 'Style':
        """Clean minimalist style with limited colors.

        Characteristics:
        - 2-4 colors typically
        - No outlines or very subtle
        - Flat shading
        - Simple geometric shapes
        - High contrast
        """
        return cls(
            name='minimalist',
            outline=OutlineConfig(
                enabled=False,
                mode='none',
                thickness=0
            ),
            shading=ShadingConfig(
                mode='flat',
                levels=2,
                light_direction=(1.0, -1.0),
                highlight_hue_shift=0.0,
                shadow_hue_shift=0.0,
                highlight_saturation=1.0,
                shadow_saturation=1.0,
                highlight_value=1.0,
                shadow_value=0.7
            ),
            palette=PaletteConfig(
                max_colors=8,
                per_sprite_colors=4
            ),
            pixel_perfect=True,
            anti_alias=False,
            head_ratio=0.35,
            eye_size='small',
            limb_style='stub',
            squash_stretch=0.0,
            follow_through=0.0
        )

    @classmethod
    def silhouette(cls) -> 'Style':
        """Silhouette/shadow style with single color.

        Characteristics:
        - Single color (usually black)
        - No internal detail
        - Strong recognizable shapes
        - No shading
        """
        return cls(
            name='silhouette',
            outline=OutlineConfig(
                enabled=False,
                mode='none'
            ),
            shading=ShadingConfig(
                mode='flat',
                levels=1,
                highlight_hue_shift=0.0,
                shadow_hue_shift=0.0
            ),
            palette=PaletteConfig(
                max_colors=2,  # Foreground + transparent
                per_sprite_colors=2
            ),
            pixel_perfect=True,
            anti_alias=False,
            head_ratio=0.35,
            eye_size='tiny',  # Eyes as simple shapes
            limb_style='simple'
        )


# Convenience aliases for quick access
CHIBI = Style.chibi()
RETRO_NES = Style.retro_nes()
RETRO_SNES = Style.retro_snes()
RETRO_GAMEBOY = Style.retro_gameboy()
MODERN_HD = Style.modern_hd()
MINIMALIST = Style.minimalist()
SILHOUETTE = Style.silhouette()

# Style lookup by name
STYLES = {
    'chibi': Style.chibi,
    'retro_nes': Style.retro_nes,
    'retro_snes': Style.retro_snes,
    'retro_gameboy': Style.retro_gameboy,
    'modern_hd': Style.modern_hd,
    'minimalist': Style.minimalist,
    'silhouette': Style.silhouette,
}


def get_style(name: str) -> Style:
    """Get a style by name.

    Args:
        name: Style name (e.g., 'chibi', 'retro_nes')

    Returns:
        Style instance

    Raises:
        KeyError: If style name not found
    """
    if name not in STYLES:
        available = ', '.join(STYLES.keys())
        raise KeyError(f"Unknown style '{name}'. Available: {available}")
    return STYLES[name]()

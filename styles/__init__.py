"""Bitsy Styles - Art style presets."""

from dataclasses import dataclass
from typing import Dict, Tuple

from style.transfer import OutlineType, ShadingType


@dataclass(frozen=True)
class OutlinePreset:
    """Preset outline settings."""
    type: OutlineType
    thickness: int
    color_method: str  # 'solid', 'darker_shade', 'selective'


@dataclass(frozen=True)
class ShadingPreset:
    """Preset shading settings."""
    type: ShadingType
    intensity: float
    direction: Tuple[float, float]


@dataclass(frozen=True)
class PaletteConstraints:
    """Preset palette constraints."""
    color_count: int
    saturation_range: Tuple[float, float]
    hue_shift: float


@dataclass(frozen=True)
class ProportionModifiers:
    """Preset proportion modifiers for character generators."""
    head_scale: float
    body_scale: float
    limb_scale: float


@dataclass(frozen=True)
class StylePreset:
    """Complete art style preset."""
    name: str
    outline_style: OutlinePreset
    shading_style: ShadingPreset
    palette_constraints: PaletteConstraints
    proportion_modifiers: ProportionModifiers


CHIBI = StylePreset(
    name='chibi',
    outline_style=OutlinePreset(
        type=OutlineType.FULL,
        thickness=2,
        color_method='solid'
    ),
    shading_style=ShadingPreset(
        type=ShadingType.CEL,
        intensity=0.6,
        direction=(1.0, -1.0)
    ),
    palette_constraints=PaletteConstraints(
        color_count=24,
        saturation_range=(0.7, 1.0),
        hue_shift=5.0
    ),
    proportion_modifiers=ProportionModifiers(
        head_scale=1.6,
        body_scale=0.7,
        limb_scale=0.7
    )
)

RETRO = StylePreset(
    name='retro',
    outline_style=OutlinePreset(
        type=OutlineType.FULL,
        thickness=1,
        color_method='solid'
    ),
    shading_style=ShadingPreset(
        type=ShadingType.DITHER,
        intensity=0.35,
        direction=(1.0, -1.0)
    ),
    palette_constraints=PaletteConstraints(
        color_count=12,
        saturation_range=(0.3, 0.8),
        hue_shift=0.0
    ),
    proportion_modifiers=ProportionModifiers(
        head_scale=1.1,
        body_scale=1.0,
        limb_scale=0.9
    )
)

MODERN = StylePreset(
    name='modern',
    outline_style=OutlinePreset(
        type=OutlineType.SELECTIVE,
        thickness=1,
        color_method='selective'
    ),
    shading_style=ShadingPreset(
        type=ShadingType.SOFT,
        intensity=0.75,
        direction=(1.0, -1.0)
    ),
    palette_constraints=PaletteConstraints(
        color_count=48,
        saturation_range=(0.4, 0.9),
        hue_shift=10.0
    ),
    proportion_modifiers=ProportionModifiers(
        head_scale=1.0,
        body_scale=1.0,
        limb_scale=1.0
    )
)

STYLE_PRESETS: Dict[str, StylePreset] = {
    'chibi': CHIBI,
    'retro': RETRO,
    'modern': MODERN,
}


def get_preset(name: str) -> StylePreset:
    """Fetch a style preset by name."""
    if name not in STYLE_PRESETS:
        available = ', '.join(sorted(STYLE_PRESETS.keys()))
        raise KeyError(f"Unknown style preset '{name}'. Available: {available}")
    return STYLE_PRESETS[name]


__all__ = [
    'OutlinePreset',
    'ShadingPreset',
    'PaletteConstraints',
    'ProportionModifiers',
    'StylePreset',
    'CHIBI',
    'RETRO',
    'MODERN',
    'STYLE_PRESETS',
    'get_preset',
]

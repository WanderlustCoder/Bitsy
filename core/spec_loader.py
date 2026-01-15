"""
Spec Loader - JSON specification parsing for Bitsy assets.

Provides loading, validation, and parsing of JSON specifications
for characters, animations, tilesets, effects, and UI elements.
"""

import json
import os
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass, field
from .style import Style, get_style
from .color import Color, hex_to_rgba


# =============================================================================
# Spec Types
# =============================================================================

@dataclass
class BaseSpec:
    """Base class for all specifications."""

    type: str
    seed: Optional[int] = None
    style: Optional[str] = None
    size: tuple = (32, 32)
    raw_data: Dict[str, Any] = field(default_factory=dict)

    def get_style(self) -> Style:
        """Get the Style object for this spec."""
        if self.style:
            return get_style(self.style)
        return Style()  # Default style


@dataclass
class CharacterSpec(BaseSpec):
    """Specification for character generation."""

    type: str = 'character'

    # Body
    body_proportions: str = 'chibi_standard'
    skin_palette: str = 'warm'
    build: str = 'average'

    # Head
    head_shape: str = 'round'
    face_style: str = 'cute'

    # Hair
    hair_style: str = 'fluffy_medium'
    hair_palette: str = 'lavender'
    has_bangs: bool = True

    # Eyes
    eye_style: str = 'large_sparkle'
    eye_color: str = 'blue'
    expression: str = 'neutral'

    # Outfit
    outfit_top: Optional[str] = None
    outfit_bottom: Optional[str] = None
    outfit_palette: str = 'cloth_blue'

    # Accessories
    accessories: List[str] = field(default_factory=list)

    # Animations to generate
    animations: List[str] = field(default_factory=list)


@dataclass
class AnimationSpec(BaseSpec):
    """Specification for animation generation."""

    type: str = 'animation'
    name: str = 'unnamed'
    fps: int = 8
    loop: bool = True

    # Frame data
    frames: List[Dict[str, Any]] = field(default_factory=list)

    # Procedural animation
    procedural_type: Optional[str] = None  # 'idle', 'walk', 'breathing', etc.
    frame_count: int = 4


@dataclass
class TilesetSpec(BaseSpec):
    """Specification for tileset generation."""

    type: str = 'tileset'
    tile_size: int = 16
    autotile_mode: str = 'blob_47'  # 'simple_16', 'blob_47', 'none'

    # Terrain colors
    base_color: str = '#4a7c4e'
    highlight_color: Optional[str] = None
    shadow_color: Optional[str] = None
    edge_style: str = 'rounded'  # 'rounded', 'sharp', 'smooth'

    # Decorations
    grass_tufts: bool = False
    flowers: List[str] = field(default_factory=list)
    rocks: bool = False

    # Variations
    variation_count: int = 1


@dataclass
class EffectSpec(BaseSpec):
    """Specification for visual effect generation."""

    type: str = 'effect'
    name: str = 'unnamed'
    duration: float = 0.5

    # Particle settings
    particle_count: int = 8
    particle_shape: str = 'circle'  # 'circle', 'square', 'diamond', 'star'
    particle_colors: List[str] = field(default_factory=lambda: ['#ffffff'])
    particle_size_range: tuple = (2, 6)
    velocity: float = 50.0
    spread: float = 360.0
    gravity: float = 0.0
    fade: bool = True


@dataclass
class UISpec(BaseSpec):
    """Specification for UI element generation."""

    type: str = 'ui_panel'
    ui_style: str = 'fantasy_wood'

    # 9-patch settings
    corner_size: int = 8
    edge_style: str = 'simple'  # 'simple', 'ornate', 'rounded'

    # Colors
    bg_color: str = '#3a2a1a'
    border_color: str = '#5a4a3a'
    highlight_color: str = '#7a6a5a'

    # Title
    title_text: Optional[str] = None
    title_font: str = 'pixel_8'
    title_color: str = '#ffffff'


@dataclass
class ItemSpec(BaseSpec):
    """Specification for item generation."""

    type: str = 'item'
    item_type: str = 'weapon'  # 'weapon', 'armor', 'potion', 'key', 'misc'
    item_subtype: str = 'sword'  # e.g., 'sword', 'staff', 'shield', 'helmet'

    # Colors
    primary_color: str = '#c0c0c0'  # Main material color
    secondary_color: Optional[str] = None  # Accent color
    glow_color: Optional[str] = None  # Optional glow

    # Properties
    rarity: str = 'common'  # 'common', 'uncommon', 'rare', 'epic', 'legendary'
    enchanted: bool = False


# =============================================================================
# Spec Loading
# =============================================================================

def _parse_color(value: Union[str, List[int], tuple]) -> Color:
    """Parse a color from various formats."""
    if isinstance(value, str):
        return hex_to_rgba(value)
    elif isinstance(value, (list, tuple)):
        if len(value) == 3:
            return (value[0], value[1], value[2], 255)
        elif len(value) == 4:
            return tuple(value)
    return (255, 255, 255, 255)


def _parse_size(value: Union[List[int], tuple, int]) -> tuple:
    """Parse size from various formats."""
    if isinstance(value, int):
        return (value, value)
    elif isinstance(value, (list, tuple)) and len(value) >= 2:
        return (value[0], value[1])
    return (32, 32)


def load_character_spec(data: Dict[str, Any]) -> CharacterSpec:
    """Parse character specification from dict."""
    spec = CharacterSpec(
        seed=data.get('seed'),
        style=data.get('style', 'chibi'),
        size=_parse_size(data.get('size', [32, 32])),
        raw_data=data
    )

    # Body
    body = data.get('body', {})
    spec.body_proportions = body.get('proportions', 'chibi_standard')
    spec.skin_palette = body.get('skin_palette', 'warm')
    spec.build = body.get('build', 'average')

    # Head
    head = data.get('head', {})
    spec.head_shape = head.get('shape', 'round')
    spec.face_style = head.get('face_style', 'cute')

    # Hair
    hair = data.get('hair', {})
    spec.hair_style = hair.get('style', 'fluffy_medium')
    spec.hair_palette = hair.get('palette', 'lavender')
    spec.has_bangs = hair.get('has_bangs', True)

    # Eyes
    eyes = data.get('eyes', {})
    spec.eye_style = eyes.get('style', 'large_sparkle')
    spec.eye_color = eyes.get('color', 'blue')
    spec.expression = eyes.get('expression', 'neutral')

    # Outfit
    outfit = data.get('outfit', {})
    spec.outfit_top = outfit.get('top')
    spec.outfit_bottom = outfit.get('bottom')
    spec.outfit_palette = outfit.get('palette', 'cloth_blue')

    # Accessories
    spec.accessories = data.get('accessories', [])

    # Animations
    spec.animations = data.get('animations', [])

    return spec


def load_animation_spec(data: Dict[str, Any]) -> AnimationSpec:
    """Parse animation specification from dict."""
    spec = AnimationSpec(
        seed=data.get('seed'),
        style=data.get('style'),
        size=_parse_size(data.get('size', [32, 32])),
        raw_data=data,
        name=data.get('name', 'unnamed'),
        fps=data.get('fps', 8),
        loop=data.get('loop', True),
        frames=data.get('frames', []),
        procedural_type=data.get('procedural_type'),
        frame_count=data.get('frame_count', 4)
    )
    return spec


def load_tileset_spec(data: Dict[str, Any]) -> TilesetSpec:
    """Parse tileset specification from dict."""
    terrain = data.get('terrain', {})
    decorations = data.get('decorations', {})

    spec = TilesetSpec(
        seed=data.get('seed'),
        style=data.get('style', 'retro_snes'),
        size=_parse_size(data.get('size', [16, 16])),
        raw_data=data,
        tile_size=data.get('tile_size', 16),
        autotile_mode=data.get('autotile_mode', 'blob_47'),
        base_color=terrain.get('base_color', '#4a7c4e'),
        highlight_color=terrain.get('highlight_color'),
        shadow_color=terrain.get('shadow_color'),
        edge_style=terrain.get('edge_style', 'rounded'),
        grass_tufts=decorations.get('grass_tufts', False),
        flowers=decorations.get('flowers', []),
        rocks=decorations.get('rocks', False),
        variation_count=data.get('variation_count', 1)
    )
    return spec


def load_effect_spec(data: Dict[str, Any]) -> EffectSpec:
    """Parse effect specification from dict."""
    particles = data.get('particles', {})

    spec = EffectSpec(
        seed=data.get('seed'),
        style=data.get('style'),
        size=_parse_size(data.get('size', [32, 32])),
        raw_data=data,
        name=data.get('name', 'unnamed'),
        duration=data.get('duration', 0.5),
        particle_count=particles.get('count', 8),
        particle_shape=particles.get('shape', 'circle'),
        particle_colors=particles.get('colors', ['#ffffff']),
        particle_size_range=tuple(particles.get('size_range', [2, 6])),
        velocity=particles.get('velocity', 50.0),
        spread=particles.get('spread', 360.0),
        gravity=particles.get('gravity', 0.0),
        fade=particles.get('fade', True)
    )
    return spec


def load_ui_spec(data: Dict[str, Any]) -> UISpec:
    """Parse UI specification from dict."""
    nine_patch = data.get('nine_patch', {})
    title = data.get('title', {})

    spec = UISpec(
        seed=data.get('seed'),
        style=data.get('style'),
        size=_parse_size(data.get('size', [200, 150])),
        raw_data=data,
        ui_style=data.get('ui_style', 'fantasy_wood'),
        corner_size=nine_patch.get('corner_size', 8),
        edge_style=nine_patch.get('edge_style', 'simple'),
        bg_color=data.get('bg_color', '#3a2a1a'),
        border_color=data.get('border_color', '#5a4a3a'),
        highlight_color=data.get('highlight_color', '#7a6a5a'),
        title_text=title.get('text'),
        title_font=title.get('font', 'pixel_8'),
        title_color=title.get('color', '#ffffff')
    )
    return spec


def load_item_spec(data: Dict[str, Any]) -> ItemSpec:
    """Parse item specification from dict."""
    spec = ItemSpec(
        seed=data.get('seed'),
        style=data.get('style'),
        size=_parse_size(data.get('size', [16, 16])),
        raw_data=data,
        item_type=data.get('item_type', 'weapon'),
        item_subtype=data.get('item_subtype', 'sword'),
        primary_color=data.get('primary_color', '#c0c0c0'),
        secondary_color=data.get('secondary_color'),
        glow_color=data.get('glow_color'),
        rarity=data.get('rarity', 'common'),
        enchanted=data.get('enchanted', False)
    )
    return spec


# Spec type registry
SPEC_LOADERS = {
    'character': load_character_spec,
    'animation': load_animation_spec,
    'tileset': load_tileset_spec,
    'effect': load_effect_spec,
    'ui_panel': load_ui_spec,
    'ui': load_ui_spec,
    'item': load_item_spec,
}


def load_spec(source: Union[str, Dict[str, Any]]) -> BaseSpec:
    """Load a specification from file path or dict.

    Args:
        source: Path to JSON file or dict with spec data

    Returns:
        Appropriate spec object based on type

    Raises:
        ValueError: If spec type is unknown
        FileNotFoundError: If file doesn't exist
    """
    if isinstance(source, str):
        # Load from file
        if not os.path.exists(source):
            raise FileNotFoundError(f"Spec file not found: {source}")

        with open(source, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = source

    spec_type = data.get('type', 'character')

    if spec_type not in SPEC_LOADERS:
        available = ', '.join(SPEC_LOADERS.keys())
        raise ValueError(f"Unknown spec type '{spec_type}'. Available: {available}")

    return SPEC_LOADERS[spec_type](data)


def load_specs_from_directory(directory: str) -> List[BaseSpec]:
    """Load all JSON specs from a directory.

    Args:
        directory: Path to directory containing .json files

    Returns:
        List of loaded specs
    """
    specs = []

    if not os.path.isdir(directory):
        raise NotADirectoryError(f"Not a directory: {directory}")

    for filename in sorted(os.listdir(directory)):
        if filename.endswith('.json'):
            filepath = os.path.join(directory, filename)
            try:
                spec = load_spec(filepath)
                specs.append(spec)
            except (ValueError, json.JSONDecodeError) as e:
                print(f"Warning: Failed to load {filename}: {e}")

    return specs


def save_spec(spec: BaseSpec, filepath: str, indent: int = 2) -> None:
    """Save a specification to JSON file.

    Args:
        spec: Spec object to save
        filepath: Output file path
        indent: JSON indentation
    """
    # Use raw_data if available, otherwise build from spec fields
    if spec.raw_data:
        data = spec.raw_data.copy()
    else:
        data = {'type': spec.type}
        if spec.seed is not None:
            data['seed'] = spec.seed
        if spec.style:
            data['style'] = spec.style
        data['size'] = list(spec.size)

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent)


# =============================================================================
# Spec Validation
# =============================================================================

def validate_spec(spec: BaseSpec) -> List[str]:
    """Validate a specification and return list of warnings/errors.

    Args:
        spec: Spec to validate

    Returns:
        List of validation messages (empty if valid)
    """
    issues = []

    # Common validations
    if spec.size[0] <= 0 or spec.size[1] <= 0:
        issues.append(f"Invalid size: {spec.size}")

    if spec.seed is not None and spec.seed < 0:
        issues.append(f"Seed should be non-negative: {spec.seed}")

    if spec.style:
        try:
            get_style(spec.style)
        except KeyError as e:
            issues.append(str(e))

    # Type-specific validations
    if isinstance(spec, CharacterSpec):
        valid_builds = ['slim', 'average', 'stocky', 'muscular']
        if spec.build not in valid_builds:
            issues.append(f"Unknown build '{spec.build}'. Valid: {valid_builds}")

    elif isinstance(spec, TilesetSpec):
        valid_modes = ['none', 'simple_16', 'blob_47']
        if spec.autotile_mode not in valid_modes:
            issues.append(f"Unknown autotile mode '{spec.autotile_mode}'. Valid: {valid_modes}")

    elif isinstance(spec, EffectSpec):
        valid_shapes = ['circle', 'square', 'diamond', 'star']
        if spec.particle_shape not in valid_shapes:
            issues.append(f"Unknown particle shape '{spec.particle_shape}'. Valid: {valid_shapes}")

    return issues


def is_valid_spec(spec: BaseSpec) -> bool:
    """Check if a spec is valid.

    Args:
        spec: Spec to validate

    Returns:
        True if valid, False otherwise
    """
    return len(validate_spec(spec)) == 0

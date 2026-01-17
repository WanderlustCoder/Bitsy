"""URL routing and parameter parsing for the preview server."""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Tuple
from urllib.parse import urlparse, parse_qs
import re


@dataclass
class Route:
    """Parsed route information."""
    type: str  # 'index', 'generate', 'animate', 'gallery', 'static', 'error'
    generator: Optional[str] = None
    params: Dict[str, Any] = field(default_factory=dict)
    options: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


# Valid generators and their parameter specs
GENERATORS = {
    'character': {
        'params': ['style', 'palette', 'seed', 'body_type', 'hair', 'equipment'],
        'styles': ['chibi', 'tiny', 'standard'],
        'description': 'Generate a character sprite',
    },
    'creature': {
        'params': ['style', 'palette', 'seed', 'creature_type', 'size'],
        'styles': ['chibi', 'tiny', 'standard'],
        'description': 'Generate a creature sprite',
    },
    'item': {
        'params': ['style', 'palette', 'seed', 'item_type', 'rarity'],
        'styles': ['chibi', 'tiny', 'standard'],
        'description': 'Generate an item sprite',
    },
    'prop': {
        'params': ['style', 'palette', 'seed', 'prop_type'],
        'styles': ['chibi', 'tiny', 'standard'],
        'description': 'Generate a prop sprite',
    },
    'structure': {
        'params': ['style', 'palette', 'seed', 'structure_type', 'size'],
        'styles': ['default'],
        'types': ['castle', 'house', 'tower', 'wall', 'ruins', 'temple', 'windmill', 'lighthouse', 'barn', 'well'],
        'description': 'Generate a structure sprite',
    },
}

EFFECTS = {
    'particle': {
        'params': ['effect_type', 'seed'],
        'types': ['spark', 'explosion', 'magic', 'fire', 'smoke', 'rain', 'snow', 'dust', 'heal', 'lightning'],
        'description': 'Generate particle effect frames',
    },
    'weather': {
        'params': ['weather_type', 'intensity', 'seed'],
        'types': ['rain', 'snow', 'fog'],
        'intensities': ['light', 'medium', 'heavy'],
        'description': 'Generate weather overlay',
    },
}

ANIMATIONS = {
    'walk': {
        'params': ['style', 'palette', 'seed', 'direction', 'frames'],
        'description': 'Generate walk cycle animation',
    },
    'idle': {
        'params': ['style', 'palette', 'seed', 'frames'],
        'description': 'Generate idle animation',
    },
}

# Common display options
DISPLAY_OPTIONS = {
    'zoom': {'type': int, 'default': 4, 'values': [1, 2, 4, 8]},
    'grid': {'type': bool, 'default': False},
    'dark': {'type': bool, 'default': True},
}


def parse_route(path: str) -> Route:
    """Parse a URL path into a Route object.

    Args:
        path: URL path with optional query string

    Returns:
        Route object with parsed information
    """
    parsed = urlparse(path)
    url_path = parsed.path.rstrip('/')
    query = parse_qs(parsed.query)

    # Flatten query values (parse_qs returns lists)
    params = {k: v[0] if len(v) == 1 else v for k, v in query.items()}

    # Extract display options
    options = {}
    for opt, spec in DISPLAY_OPTIONS.items():
        if opt in params:
            try:
                if spec['type'] == bool:
                    options[opt] = params.pop(opt).lower() in ('true', '1', 'yes')
                elif spec['type'] == int:
                    options[opt] = int(params.pop(opt))
            except (ValueError, KeyError):
                options[opt] = spec['default']
        else:
            options[opt] = spec['default']

    # Route matching
    if url_path == '' or url_path == '/':
        return Route(type='index', options=options)

    if url_path == '/gallery':
        return Route(type='gallery', options=options)

    if url_path == '/favicon.ico':
        return Route(type='static', params={'file': 'favicon.ico'})

    # Generate route: /generate/<type>
    match = re.match(r'^/generate/(\w+)$', url_path)
    if match:
        gen_type = match.group(1)
        if gen_type in GENERATORS:
            validated = validate_generator_params(gen_type, params)
            return Route(
                type='generate',
                generator=gen_type,
                params=validated,
                options=options
            )
        elif gen_type in EFFECTS:
            validated = validate_effect_params(gen_type, params)
            return Route(
                type='generate',
                generator=gen_type,
                params=validated,
                options=options
            )
        else:
            return Route(
                type='error',
                error=f"Unknown generator: {gen_type}. Valid: {', '.join(list(GENERATORS.keys()) + list(EFFECTS.keys()))}"
            )

    # Animate route: /animate/<type>
    match = re.match(r'^/animate/(\w+)$', url_path)
    if match:
        anim_type = match.group(1)
        if anim_type in ANIMATIONS:
            validated = validate_animation_params(anim_type, params)
            return Route(
                type='animate',
                generator=anim_type,
                params=validated,
                options=options
            )
        else:
            return Route(
                type='error',
                error=f"Unknown animation: {anim_type}. Valid: {', '.join(ANIMATIONS.keys())}"
            )

    return Route(type='error', error=f"Unknown path: {url_path}")


def validate_generator_params(gen_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and convert generator parameters."""
    spec = GENERATORS[gen_type]
    validated = {}

    # Seed (common to all)
    if 'seed' in params:
        try:
            validated['seed'] = int(params['seed'])
        except ValueError:
            pass

    # Style
    if 'style' in params:
        if params['style'] in spec.get('styles', []):
            validated['style'] = params['style']

    # Palette
    if 'palette' in params:
        validated['palette'] = params['palette']

    # Structure-specific: type
    if gen_type == 'structure' and 'type' in params:
        if params['type'] in spec.get('types', []):
            validated['structure_type'] = params['type']

    return validated


def validate_effect_params(effect_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and convert effect parameters."""
    spec = EFFECTS[effect_type]
    validated = {}

    if 'seed' in params:
        try:
            validated['seed'] = int(params['seed'])
        except ValueError:
            pass

    if effect_type == 'particle' and 'type' in params:
        if params['type'] in spec.get('types', []):
            validated['effect_type'] = params['type']

    if effect_type == 'weather':
        if 'type' in params and params['type'] in spec.get('types', []):
            validated['weather_type'] = params['type']
        if 'intensity' in params and params['intensity'] in spec.get('intensities', []):
            validated['intensity'] = params['intensity']

    return validated


def validate_animation_params(anim_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and convert animation parameters."""
    validated = {}

    if 'seed' in params:
        try:
            validated['seed'] = int(params['seed'])
        except ValueError:
            pass

    if 'style' in params:
        validated['style'] = params['style']

    if 'frames' in params:
        try:
            validated['frames'] = int(params['frames'])
        except ValueError:
            pass

    return validated


def get_generator_info() -> List[Dict[str, Any]]:
    """Get information about all available generators."""
    info = []

    for name, spec in GENERATORS.items():
        info.append({
            'name': name,
            'type': 'generator',
            'description': spec['description'],
            'params': spec['params'],
            'styles': spec.get('styles', []),
            'types': spec.get('types', []),
        })

    for name, spec in EFFECTS.items():
        info.append({
            'name': name,
            'type': 'effect',
            'description': spec['description'],
            'params': spec['params'],
            'types': spec.get('types', []),
        })

    for name, spec in ANIMATIONS.items():
        info.append({
            'name': name,
            'type': 'animation',
            'description': spec['description'],
            'params': spec['params'],
        })

    return info

"""
Composition Renderer - Render parsed scenes into pixel art.

Takes a Scene structure from composition.py and renders:
- Backgrounds/environments
- Objects
- Characters
- Proper layer ordering
"""

from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass

# Import core canvas
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.canvas import Canvas

# Import parsers
from recipes.composition import (
    Scene, Element, Character, Object, Environment,
    Relationship, Position, parse_scene, parse_full_description
)
from recipes.natural_language import parse_description as parse_character


# =============================================================================
# COLOR PALETTES (simplified from recipe files)
# =============================================================================

SKY_PALETTES = {
    'day': [(100, 160, 220), (140, 190, 235), (180, 215, 245)],
    'sunset': [(60, 80, 140), (180, 120, 100), (255, 180, 100)],
    'night': [(15, 20, 40), (25, 35, 60), (40, 50, 80)],
}

GROUND_PALETTES = {
    'grass': [(45, 80, 35), (70, 120, 50), (100, 160, 70)],
    'stone': [(80, 80, 90), (120, 120, 130), (160, 160, 170)],
    'wood': [(60, 45, 35), (100, 80, 60), (145, 120, 95)],
}

INDOOR_PALETTES = {
    'cozy': {
        'wall': [(90, 75, 65), (110, 95, 80), (130, 115, 100)],
        'floor': [(70, 55, 45), (90, 75, 60), (110, 95, 80)],
    },
    'library': {
        'wall': [(60, 50, 55), (80, 70, 75), (100, 90, 95)],
        'floor': [(50, 40, 35), (70, 60, 50), (90, 80, 70)],
    },
    'castle': {
        'wall': [(80, 80, 90), (100, 100, 110), (120, 120, 130)],
        'floor': [(60, 60, 70), (80, 80, 90), (100, 100, 110)],
    },
    'tavern': {
        'wall': [(70, 55, 45), (100, 80, 65), (130, 110, 90)],
        'floor': [(50, 40, 30), (80, 65, 50), (110, 95, 75)],
    },
    'cafe': {
        'wall': [(100, 90, 80), (130, 120, 105), (160, 150, 135)],
        'floor': [(80, 70, 60), (110, 100, 85), (140, 130, 115)],
    },
}

OBJECT_COLORS = {
    'book': {
        'cover': [(60, 40, 30), (100, 70, 50), (140, 100, 75)],
        'pages': [(235, 225, 205)],
    },
    'potion': {
        'glass': [(80, 90, 100), (200, 220, 240)],
        'health': (180, 40, 50),
        'mana': (50, 90, 180),
        'poison': (50, 140, 50),
    },
    'sword': {
        'blade': [(100, 110, 125), (150, 160, 175), (200, 210, 225)],
        'handle': (80, 60, 45),
    },
    'teacup': {
        'cup': [(240, 235, 230), (220, 215, 210)],
        'tea': (160, 120, 80),
    },
    'staff': {
        'wood': [(60, 45, 35), (100, 80, 60)],
        'gem': (180, 120, 255),
    },
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def lerp_color(c1: Tuple, c2: Tuple, t: float) -> Tuple[int, int, int, int]:
    """Linear interpolate between two colors, return RGBA."""
    rgb = tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(min(len(c1), len(c2), 3)))
    return (*rgb, 255)


def rgba(color: Tuple) -> Tuple[int, int, int, int]:
    """Convert RGB or RGBA color to RGBA."""
    if len(color) == 4:
        return color
    return (*color, 255)


def get_position_coords(position: Position, canvas_width: int, canvas_height: int,
                        element_width: int, element_height: int) -> Tuple[int, int]:
    """Convert Position enum to x, y coordinates."""
    margin = 10

    positions = {
        Position.CENTER: (canvas_width // 2 - element_width // 2,
                         canvas_height // 2 - element_height // 2),
        Position.LEFT: (margin, canvas_height // 2 - element_height // 2),
        Position.RIGHT: (canvas_width - element_width - margin,
                        canvas_height // 2 - element_height // 2),
        Position.TOP: (canvas_width // 2 - element_width // 2, margin),
        Position.BOTTOM: (canvas_width // 2 - element_width // 2,
                         canvas_height - element_height - margin),
    }

    return positions.get(position, positions[Position.CENTER])


# =============================================================================
# ENVIRONMENT RENDERERS
# =============================================================================

def render_environment(canvas: Canvas, env_name: str, atmosphere: Dict = None):
    """Render a background environment."""
    width, height = canvas.width, canvas.height

    # Determine palette based on environment category
    indoor_envs = {'library', 'study', 'room', 'tavern', 'inn', 'cafe',
                   'castle', 'throne_room', 'bedroom', 'kitchen'}
    outdoor_envs = {'forest', 'beach', 'mountain', 'meadow', 'field', 'garden'}

    # Get time modifier
    time = 'day'
    if atmosphere:
        time_mods = atmosphere.get('time', [])
        if 'night' in time_mods or 'midnight' in time_mods:
            time = 'night'
        elif 'sunset' in time_mods or 'evening' in time_mods:
            time = 'sunset'

    if env_name in indoor_envs or env_name.endswith('_room'):
        _render_indoor(canvas, env_name, time)
    elif env_name in outdoor_envs:
        _render_outdoor(canvas, env_name, time)
    else:
        # Default simple gradient
        _render_simple_bg(canvas, env_name)


def _render_indoor(canvas: Canvas, env_name: str, time: str):
    """Render indoor environment."""
    width, height = canvas.width, canvas.height

    # Select palette
    if 'library' in env_name or 'study' in env_name:
        palette = INDOOR_PALETTES['library']
    elif 'tavern' in env_name or 'inn' in env_name:
        palette = INDOOR_PALETTES['tavern']
    elif 'castle' in env_name or 'throne' in env_name:
        palette = INDOOR_PALETTES['castle']
    elif 'cafe' in env_name:
        palette = INDOOR_PALETTES['cafe']
    else:
        palette = INDOOR_PALETTES['cozy']

    floor_y = height * 2 // 3

    # Wall
    for y in range(floor_y):
        t = y / floor_y
        idx = min(2, int((1 - t) * 3))
        color = rgba(palette['wall'][idx])
        canvas.draw_line(0, y, width - 1, y, color)

    # Floor
    for y in range(floor_y, height):
        t = (y - floor_y) / (height - floor_y)
        idx = min(2, int(t * 3))
        color = rgba(palette['floor'][idx])
        canvas.draw_line(0, y, width - 1, y, color)

    # Wall-floor line
    canvas.draw_line(0, floor_y, width - 1, floor_y, rgba(palette['floor'][0]))

    # Add simple window for indoor scenes
    if width >= 64:
        win_width = width // 5
        win_height = floor_y // 2
        win_x = width // 2 - win_width // 2
        win_y = floor_y // 4

        # Window
        if time == 'night':
            glass_color = rgba((40, 50, 80))
        elif time == 'sunset':
            glass_color = rgba((255, 200, 150))
        else:
            glass_color = rgba((180, 210, 240))

        canvas.fill_rect(win_x, win_y, win_width, win_height, glass_color)
        # Frame
        frame_color = rgba(GROUND_PALETTES['wood'][1])
        canvas.draw_rect(win_x - 1, win_y - 1, win_width + 2, win_height + 2, frame_color)

    # Night overlay
    if time == 'night':
        # Darken everything slightly (simplified - just draw over)
        pass


def _render_outdoor(canvas: Canvas, env_name: str, time: str):
    """Render outdoor environment."""
    width, height = canvas.width, canvas.height

    sky = SKY_PALETTES.get(time, SKY_PALETTES['day'])
    ground = GROUND_PALETTES['grass']

    sky_height = height // 2

    # Sky gradient
    for y in range(sky_height):
        t = y / sky_height
        idx = min(2, int(t * 3))
        canvas.draw_line(0, y, width - 1, y, rgba(sky[idx]))

    # Ground gradient
    for y in range(sky_height, height):
        t = (y - sky_height) / (height - sky_height)
        idx = 2 - min(2, int(t * 3))
        canvas.draw_line(0, y, width - 1, y, rgba(ground[idx]))

    # Add simple trees for forest
    if 'forest' in env_name:
        import random
        random.seed(42)
        for i in range(3):
            tx = random.randint(width // 6, width * 5 // 6)
            _draw_simple_tree(canvas, tx, sky_height + 10, 30)


def _render_simple_bg(canvas: Canvas, env_name: str):
    """Render simple gradient background."""
    width, height = canvas.width, canvas.height

    # Default purple-gray gradient
    top = (45, 40, 55)
    bottom = (65, 55, 70)

    for y in range(height):
        t = y / height
        color = lerp_color(top, bottom, t)
        canvas.draw_line(0, y, width - 1, y, color)


def _draw_simple_tree(canvas: Canvas, x: int, base_y: int, height: int):
    """Draw a simple tree silhouette."""
    trunk_h = height // 4
    trunk_color = rgba(GROUND_PALETTES['wood'][0])
    leaf_color = rgba(GROUND_PALETTES['grass'][0])

    # Trunk
    canvas.fill_rect(x - 1, base_y, 3, trunk_h, trunk_color)

    # Foliage (triangle)
    foliage_h = height - trunk_h
    for fy in range(foliage_h):
        t = fy / foliage_h
        row_w = int((1 - t) * foliage_h // 2) * 2 + 1
        row_x = x - row_w // 2
        row_y = base_y - foliage_h + fy
        canvas.draw_line(row_x, row_y, row_x + row_w - 1, row_y, leaf_color)


# =============================================================================
# OBJECT RENDERERS
# =============================================================================

def render_object(canvas: Canvas, obj_name: str, x: int, y: int,
                  width: int, height: int, attributes: Dict = None):
    """Render an object at position."""

    if obj_name in ('book', 'tome', 'spellbook', 'grimoire'):
        _draw_book(canvas, x, y, width, height)
    elif obj_name in ('potion', 'vial', 'flask', 'elixir', 'health_potion', 'mana_potion'):
        liquid = 'health' if 'health' in obj_name else 'mana' if 'mana' in obj_name else 'health'
        _draw_potion(canvas, x, y, width, height, liquid)
    elif obj_name in ('sword', 'blade', 'dagger', 'knife'):
        _draw_sword(canvas, x, y, height)
    elif obj_name in ('staff', 'wand', 'rod'):
        _draw_staff(canvas, x, y, height)
    elif obj_name in ('teacup', 'cup', 'mug', 'goblet'):
        _draw_cup(canvas, x, y, width, height)
    elif obj_name == 'throne':
        _draw_throne(canvas, x, y, width, height)
    else:
        # Generic object placeholder
        _draw_generic_object(canvas, x, y, width, height, obj_name)


def _draw_book(canvas: Canvas, x: int, y: int, width: int, height: int):
    """Draw a closed book."""
    colors = OBJECT_COLORS['book']

    spine_w = max(2, width // 6)
    page_h = max(1, height // 8)

    # Cover back
    canvas.fill_rect(x + 1, y + 1, width - 1, height - 1, rgba(colors['cover'][0]))

    # Spine
    canvas.fill_rect(x, y, spine_w, height, rgba(colors['cover'][1]))
    canvas.draw_line(x, y, x, y + height - 1, rgba(colors['cover'][2]))

    # Cover front
    canvas.fill_rect(x + spine_w, y, width - spine_w, height - page_h, rgba(colors['cover'][1]))

    # Pages edge
    canvas.fill_rect(x + spine_w, y + height - page_h, width - spine_w, page_h, rgba(colors['pages'][0]))

    # Cover highlight
    canvas.draw_line(x + spine_w, y, x + width - 1, y, rgba(colors['cover'][2]))


def _draw_potion(canvas: Canvas, x: int, y: int, width: int, height: int, liquid: str):
    """Draw a potion bottle."""
    colors = OBJECT_COLORS['potion']
    liquid_color = rgba(colors.get(liquid, colors['health']))

    neck_h = height // 4
    neck_w = width // 3
    body_h = height - neck_h
    cork_h = 2

    # Body
    body_cx = x + width // 2
    body_cy = y + neck_h + body_h // 2
    body_rx = width // 2
    body_ry = body_h // 2

    # Liquid fill
    for py in range(body_cy - body_ry // 2, body_cy + body_ry):
        # Approximate ellipse width
        rel_y = (py - body_cy) / body_ry if body_ry > 0 else 0
        if abs(rel_y) <= 1:
            import math
            half_w = int(body_rx * math.sqrt(max(0, 1 - rel_y * rel_y)))
            if half_w > 0:
                canvas.draw_line(body_cx - half_w + 1, py, body_cx + half_w - 1, py, liquid_color)

    # Glass outline (use circle approximation)
    canvas.draw_circle(body_cx, body_cy, min(body_rx, body_ry), rgba(colors['glass'][0]))

    # Neck
    neck_x = x + (width - neck_w) // 2
    canvas.fill_rect(neck_x, y + cork_h, neck_w, neck_h - cork_h, rgba(colors['glass'][0]))

    # Cork
    cork_color = rgba((150, 110, 80))
    canvas.fill_rect(neck_x - 1, y, neck_w + 2, cork_h, cork_color)

    # Glass highlight
    canvas.set_pixel(body_cx - body_rx // 2, body_cy - body_ry // 2, rgba(colors['glass'][1]))


def _draw_sword(canvas: Canvas, x: int, y: int, length: int):
    """Draw a vertical sword."""
    colors = OBJECT_COLORS['sword']

    handle_len = length // 5
    guard_w = 5
    blade_len = length - handle_len - 1

    # Handle
    for i in range(handle_len):
        canvas.set_pixel(x, y + length - i, rgba(colors['handle']))

    # Guard
    guard_y = y + blade_len + 1
    canvas.draw_line(x - guard_w // 2, guard_y, x + guard_w // 2, guard_y, rgba(colors['blade'][1]))

    # Blade
    for i in range(blade_len):
        by = y + i + 1
        canvas.set_pixel(x - 1, by, rgba(colors['blade'][0]))
        canvas.set_pixel(x, by, rgba(colors['blade'][2]))
        canvas.set_pixel(x + 1, by, rgba(colors['blade'][1]))

    # Tip
    canvas.set_pixel(x, y, rgba(colors['blade'][2]))


def _draw_staff(canvas: Canvas, x: int, y: int, length: int):
    """Draw a magic staff."""
    colors = OBJECT_COLORS['staff']

    # Shaft
    for i in range(length):
        canvas.set_pixel(x, y + i, rgba(colors['wood'][1]))
        canvas.set_pixel(x - 1, y + i, rgba(colors['wood'][0]))

    # Gem at top
    gem_size = 3
    canvas.fill_ellipse(x, y - gem_size, gem_size, gem_size, rgba(colors['gem']))
    canvas.set_pixel(x - 1, y - gem_size - 1, rgba((255, 255, 255)))  # Highlight


def _draw_cup(canvas: Canvas, x: int, y: int, width: int, height: int):
    """Draw a teacup/mug."""
    colors = OBJECT_COLORS['teacup']

    # Cup body
    canvas.fill_rect(x, y, width, height, rgba(colors['cup'][0]))
    canvas.draw_rect(x, y, width, height, rgba(colors['cup'][1]))

    # Tea inside
    tea_h = height - 3
    canvas.fill_rect(x + 1, y + 2, width - 2, tea_h, rgba(colors['tea']))

    # Handle
    handle_h = height // 2
    canvas.draw_line(x + width, y + 2, x + width + 2, y + 2, rgba(colors['cup'][1]))
    canvas.draw_line(x + width + 2, y + 2, x + width + 2, y + 2 + handle_h, rgba(colors['cup'][1]))
    canvas.draw_line(x + width, y + 2 + handle_h, x + width + 2, y + 2 + handle_h, rgba(colors['cup'][1]))


def _draw_throne(canvas: Canvas, x: int, y: int, width: int, height: int):
    """Draw a throne."""
    wood = GROUND_PALETTES['wood']
    gold = rgba((200, 170, 80))

    # Back (tall)
    back_h = height * 2 // 3
    canvas.fill_rect(x, y, width, back_h, rgba(wood[1]))
    canvas.draw_rect(x, y, width, back_h, rgba(wood[0]))

    # Seat
    seat_y = y + back_h
    seat_h = height - back_h
    canvas.fill_rect(x - 2, seat_y, width + 4, seat_h // 2, rgba(wood[1]))

    # Armrests
    canvas.fill_rect(x - 4, seat_y - seat_h // 2, 3, seat_h, rgba(wood[1]))
    canvas.fill_rect(x + width + 1, seat_y - seat_h // 2, 3, seat_h, rgba(wood[1]))

    # Gold accents
    canvas.set_pixel(x + width // 2, y + 2, gold)
    canvas.set_pixel(x + 2, y + 2, gold)
    canvas.set_pixel(x + width - 3, y + 2, gold)


def _draw_generic_object(canvas: Canvas, x: int, y: int, width: int, height: int, name: str):
    """Draw a placeholder for unknown objects."""
    # Simple colored rectangle with label
    color = rgba((100, 100, 120))
    canvas.fill_rect(x, y, width, height, color)
    canvas.draw_rect(x, y, width, height, rgba((80, 80, 100)))


# =============================================================================
# CHARACTER RENDERER
# =============================================================================

def render_character(canvas: Canvas, char_spec: Dict, x: int, y: int,
                     width: int, height: int):
    """
    Render a character using the recipe-based approach.

    This integrates with the existing loader.py for character rendering.
    """
    try:
        from recipes.loader import render_character as recipe_render

        # Create a sub-canvas for the character
        char_canvas = Canvas(width, height)

        # Build spec for loader
        spec = {
            'size': min(width, height),
            'character': char_spec.get('character', {}),
            'background': None,  # Transparent
        }

        # Render character
        recipe_render(char_canvas, spec)

        # Composite onto main canvas
        for cy in range(height):
            for cx in range(width):
                pixel = char_canvas.get_pixel(cx, cy)
                if pixel and pixel[3] > 0:  # Has alpha
                    canvas.set_pixel(x + cx, y + cy, pixel[:3])

    except Exception as e:
        # Fallback: simple character silhouette
        _draw_character_silhouette(canvas, x, y, width, height)


def _draw_character_silhouette(canvas: Canvas, x: int, y: int, width: int, height: int):
    """Draw a simple character placeholder."""
    # Head
    head_size = min(width, height) // 3
    head_x = x + width // 2
    head_y = y + head_size

    canvas.fill_ellipse(head_x, head_y, head_size, head_size, rgba((235, 200, 175)))

    # Body
    body_top = head_y + head_size
    body_height = height - head_size * 2
    body_width = width // 2

    canvas.fill_rect(x + width // 4, body_top, body_width, body_height, rgba((100, 80, 120)))


# =============================================================================
# MAIN COMPOSITION RENDERER
# =============================================================================

@dataclass
class RenderConfig:
    """Configuration for rendering."""
    width: int = 128
    height: int = 128
    character_scale: float = 0.6  # Character takes 60% of height
    object_scale: float = 0.15   # Held objects are 15% of character
    margin: int = 10


def render_scene(description: str, config: RenderConfig = None) -> Canvas:
    """
    Main entry point: render a natural language description.

    Args:
        description: Natural language scene description
        config: Render configuration

    Returns:
        Canvas with rendered scene
    """
    if config is None:
        config = RenderConfig()

    canvas = Canvas(config.width, config.height)

    # Parse the description
    result = parse_full_description(description)
    scene = result['scene']

    # 1. Render environment (background)
    if scene.environment:
        render_environment(canvas, scene.environment.name, scene.atmosphere)
    else:
        # Default background
        _render_simple_bg(canvas, 'default')

    # 2. Determine layout
    char_height = int(config.height * config.character_scale)
    char_width = int(char_height * 0.7)

    # Center character
    char_x = (config.width - char_width) // 2
    char_y = config.height - char_height - config.margin

    # 3. Render background objects (furniture, etc.)
    for instr in result['render_instructions']:
        if instr['type'] == 'object' and not instr.get('held'):
            obj_name = instr['element']
            cat = instr['attributes'].get('category', '')

            # Position furniture in background
            if cat in ('furniture', 'containers'):
                obj_w = config.width // 4
                obj_h = config.height // 4
                obj_x = config.margin
                obj_y = config.height - obj_h - config.margin

                render_object(canvas, obj_name, obj_x, obj_y, obj_w, obj_h)

    # 4. Render character
    if scene.subjects and result.get('character_spec'):
        render_character(canvas, result['character_spec'],
                        char_x, char_y, char_width, char_height)

    # 5. Render held objects
    for instr in result['render_instructions']:
        if instr['type'] == 'object' and instr.get('held'):
            obj_name = instr['element']

            # Position held object near character's hand area
            obj_w = int(char_width * 0.4)
            obj_h = int(char_height * 0.25)
            obj_x = char_x + char_width - obj_w // 2
            obj_y = char_y + int(char_height * 0.5)

            render_object(canvas, obj_name, obj_x, obj_y, obj_w, obj_h)

    return canvas


def render_object_only(description: str, config: RenderConfig = None) -> Canvas:
    """Render just an object (no character/scene)."""
    if config is None:
        config = RenderConfig(width=64, height=64)

    canvas = Canvas(config.width, config.height)

    # Simple gradient background
    for y in range(config.height):
        t = y / config.height
        color = lerp_color((45, 40, 55), (55, 50, 65), t)
        canvas.draw_line(0, y, config.width - 1, y, color)

    # Parse to find object
    scene = parse_scene(description)

    if scene.objects:
        obj = scene.objects[0]
        obj_w = config.width // 2
        obj_h = config.height // 2
        obj_x = (config.width - obj_w) // 2
        obj_y = (config.height - obj_h) // 2

        render_object(canvas, obj.name, obj_x, obj_y, obj_w, obj_h)

    return canvas


def render_character_only(description: str, config: RenderConfig = None) -> Canvas:
    """Render just a character (no scene)."""
    if config is None:
        config = RenderConfig()

    canvas = Canvas(config.width, config.height)

    # Background
    for y in range(config.height):
        t = y / config.height
        color = lerp_color((45, 40, 55), (55, 50, 65), t)
        canvas.draw_line(0, y, config.width - 1, y, color)

    # Parse character
    char_spec = parse_character(description)

    char_height = int(config.height * 0.8)
    char_width = int(char_height * 0.7)
    char_x = (config.width - char_width) // 2
    char_y = config.height - char_height - 10

    render_character(canvas, char_spec, char_x, char_y, char_width, char_height)

    return canvas


# =============================================================================
# UNIFIED GENERATE FUNCTION
# =============================================================================

def generate(description: str, output_path: str = None,
             width: int = 128, height: int = 128) -> Canvas:
    """
    Generate pixel art from natural language description.

    Automatically determines if it's a character, object, or scene.

    Args:
        description: What to generate
        output_path: Optional path to save PNG
        width, height: Canvas size

    Returns:
        Canvas with rendered result
    """
    config = RenderConfig(width=width, height=height)

    # Parse to determine type
    scene = parse_scene(description)

    if scene.type == 'object' and not scene.subjects:
        canvas = render_object_only(description, config)
    elif scene.type == 'character' or (scene.subjects and not scene.environment):
        canvas = render_character_only(description, config)
    else:
        canvas = render_scene(description, config)

    # Save if path provided
    if output_path:
        canvas.save(output_path)

    return canvas

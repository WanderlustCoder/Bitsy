"""
Texture Generator - Seamless tileable textures for pixel art.

Provides generators for common texture types used in games:
- Brick, stone, wood patterns
- Grass and organic textures
- Fabric patterns (checkered, striped)
- Metal textures (brushed, riveted)
"""

import random
from typing import Optional, List, Tuple, Dict, Callable
from enum import Enum

from core import Canvas
from core.png_writer import Color


class TextureType(Enum):
    """Types of textures that can be generated."""
    BRICK = "brick"
    STONE = "stone"
    WOOD = "wood"
    GRASS = "grass"
    FABRIC = "fabric"
    METAL = "metal"


class TexturePalette:
    """Color palette for textures."""

    def __init__(self, base: Color, highlight: Color, shadow: Color,
                 accent: Optional[Color] = None):
        self.base = base
        self.highlight = highlight
        self.shadow = shadow
        self.accent = accent or shadow

    @classmethod
    def brick(cls) -> 'TexturePalette':
        """Red/brown brick colors."""
        return cls(
            base=(178, 102, 76, 255),
            highlight=(204, 128, 102, 255),
            shadow=(140, 76, 56, 255),
            accent=(64, 56, 52, 255)  # mortar
        )

    @classmethod
    def stone(cls) -> 'TexturePalette':
        """Gray stone colors."""
        return cls(
            base=(128, 128, 128, 255),
            highlight=(160, 160, 160, 255),
            shadow=(96, 96, 96, 255),
            accent=(80, 80, 80, 255)
        )

    @classmethod
    def wood(cls) -> 'TexturePalette':
        """Brown wood grain colors."""
        return cls(
            base=(139, 90, 43, 255),
            highlight=(181, 137, 77, 255),
            shadow=(101, 67, 33, 255),
            accent=(79, 52, 26, 255)
        )

    @classmethod
    def grass(cls) -> 'TexturePalette':
        """Green grass colors."""
        return cls(
            base=(76, 153, 76, 255),
            highlight=(102, 178, 102, 255),
            shadow=(51, 128, 51, 255),
            accent=(38, 102, 38, 255)
        )

    @classmethod
    def metal(cls) -> 'TexturePalette':
        """Silver/steel colors."""
        return cls(
            base=(160, 160, 170, 255),
            highlight=(200, 200, 210, 255),
            shadow=(120, 120, 130, 255),
            accent=(80, 80, 90, 255)
        )

    @classmethod
    def fabric_red(cls) -> 'TexturePalette':
        """Red fabric colors."""
        return cls(
            base=(180, 60, 60, 255),
            highlight=(220, 100, 100, 255),
            shadow=(140, 40, 40, 255),
            accent=(240, 240, 240, 255)  # white accent
        )


class TextureGenerator:
    """Generator for seamless tileable textures."""

    def __init__(self, width: int, height: int, seed: int = 42):
        self.width = width
        self.height = height
        self.seed = seed
        self.rng = random.Random(seed)
        self.palette = TexturePalette.stone()

    def set_palette(self, palette: TexturePalette) -> None:
        """Set the color palette."""
        self.palette = palette

    def _wrap_x(self, x: int) -> int:
        """Wrap x coordinate for seamless tiling."""
        return x % self.width

    def _wrap_y(self, y: int) -> int:
        """Wrap y coordinate for seamless tiling."""
        return y % self.height

    def generate_brick(self, brick_width: int = 8, brick_height: int = 4,
                       mortar_width: int = 1) -> Canvas:
        """Generate a brick wall texture.

        Args:
            brick_width: Width of each brick
            brick_height: Height of each brick
            mortar_width: Width of mortar lines

        Returns:
            Canvas with seamless brick texture
        """
        canvas = Canvas(self.width, self.height, self.palette.accent)
        self.rng = random.Random(self.seed)

        # Draw bricks in rows
        y = 0
        row = 0
        while y < self.height:
            # Offset every other row
            x_offset = (brick_width // 2) if row % 2 else 0
            x = -x_offset

            while x < self.width:
                # Draw brick with slight color variation
                variation = self.rng.randint(-15, 15)
                brick_color = (
                    max(0, min(255, self.palette.base[0] + variation)),
                    max(0, min(255, self.palette.base[1] + variation)),
                    max(0, min(255, self.palette.base[2] + variation)),
                    255
                )

                # Draw brick rectangle (accounting for mortar)
                for by in range(brick_height - mortar_width):
                    for bx in range(brick_width - mortar_width):
                        px = self._wrap_x(x + bx)
                        py = self._wrap_y(y + by)
                        canvas.set_pixel_solid(px, py, brick_color)

                        # Add highlight on top-left edge
                        if by == 0 or bx == 0:
                            canvas.set_pixel_solid(px, py, self.palette.highlight)
                        # Add shadow on bottom-right edge
                        elif by == brick_height - mortar_width - 1 or bx == brick_width - mortar_width - 1:
                            canvas.set_pixel_solid(px, py, self.palette.shadow)

                x += brick_width
            y += brick_height
            row += 1

        return canvas

    def generate_stone(self, min_size: int = 4, max_size: int = 8) -> Canvas:
        """Generate a cobblestone/flagstone texture.

        Args:
            min_size: Minimum stone size
            max_size: Maximum stone size

        Returns:
            Canvas with seamless stone texture
        """
        canvas = Canvas(self.width, self.height, self.palette.accent)
        self.rng = random.Random(self.seed)

        # Place stones randomly but try to fill space
        stones = []
        attempts = 0
        max_attempts = 200

        while attempts < max_attempts:
            x = self.rng.randint(0, self.width - 1)
            y = self.rng.randint(0, self.height - 1)
            w = self.rng.randint(min_size, max_size)
            h = self.rng.randint(min_size, max_size)

            # Check overlap with existing stones
            overlap = False
            for sx, sy, sw, sh in stones:
                if (x < sx + sw + 1 and x + w + 1 > sx and
                    y < sy + sh + 1 and y + h + 1 > sy):
                    overlap = True
                    break

            if not overlap or attempts > max_attempts // 2:
                stones.append((x, y, w, h))
                attempts = 0
            else:
                attempts += 1

            if len(stones) > (self.width * self.height) // (min_size * min_size):
                break

        # Draw stones
        for sx, sy, sw, sh in stones:
            variation = self.rng.randint(-20, 20)
            stone_color = (
                max(0, min(255, self.palette.base[0] + variation)),
                max(0, min(255, self.palette.base[1] + variation)),
                max(0, min(255, self.palette.base[2] + variation)),
                255
            )

            for dy in range(sh):
                for dx in range(sw):
                    px = self._wrap_x(sx + dx)
                    py = self._wrap_y(sy + dy)
                    canvas.set_pixel_solid(px, py, stone_color)

                    # Highlight top-left
                    if dy == 0 or dx == 0:
                        canvas.set_pixel_solid(px, py, self.palette.highlight)
                    # Shadow bottom-right
                    elif dy == sh - 1 or dx == sw - 1:
                        canvas.set_pixel_solid(px, py, self.palette.shadow)

        return canvas

    def generate_wood(self, grain_spacing: int = 3,
                      grain_direction: str = 'horizontal') -> Canvas:
        """Generate a wood grain texture.

        Args:
            grain_spacing: Average spacing between grain lines
            grain_direction: 'horizontal' or 'vertical'

        Returns:
            Canvas with seamless wood texture
        """
        canvas = Canvas(self.width, self.height, self.palette.base)
        self.rng = random.Random(self.seed)

        vertical = grain_direction == 'vertical'
        primary_size = self.height if vertical else self.width
        secondary_size = self.width if vertical else self.height

        # Draw grain lines
        pos = 0
        while pos < secondary_size:
            # Grain line with some waviness
            wave_offset = 0
            for i in range(primary_size):
                # Add some wave to the grain
                if self.rng.random() < 0.1:
                    wave_offset += self.rng.choice([-1, 0, 1])
                    wave_offset = max(-2, min(2, wave_offset))

                line_pos = self._wrap_x(pos + wave_offset) if vertical else self._wrap_y(pos + wave_offset)

                if vertical:
                    px, py = line_pos, i
                else:
                    px, py = i, line_pos

                # Alternate between shadow and highlight for grain effect
                if self.rng.random() < 0.5:
                    canvas.set_pixel_solid(px, py, self.palette.shadow)
                else:
                    canvas.set_pixel_solid(px, py, self.palette.accent)

            pos += grain_spacing + self.rng.randint(-1, 1)

        # Add some knots
        num_knots = max(1, (self.width * self.height) // 256)
        for _ in range(num_knots):
            kx = self.rng.randint(0, self.width - 1)
            ky = self.rng.randint(0, self.height - 1)
            kr = self.rng.randint(1, 3)

            for dy in range(-kr, kr + 1):
                for dx in range(-kr, kr + 1):
                    if dx * dx + dy * dy <= kr * kr:
                        px = self._wrap_x(kx + dx)
                        py = self._wrap_y(ky + dy)
                        dist = (dx * dx + dy * dy) / (kr * kr + 0.1)
                        if dist < 0.5:
                            canvas.set_pixel_solid(px, py, self.palette.accent)
                        else:
                            canvas.set_pixel_solid(px, py, self.palette.shadow)

        return canvas

    def generate_grass(self, density: float = 0.3,
                       blade_height: int = 3) -> Canvas:
        """Generate a grass texture.

        Args:
            density: How densely packed grass blades are (0-1)
            blade_height: Maximum height of grass blades

        Returns:
            Canvas with seamless grass texture
        """
        canvas = Canvas(self.width, self.height, self.palette.base)
        self.rng = random.Random(self.seed)

        # Add base color variation
        for y in range(self.height):
            for x in range(self.width):
                if self.rng.random() < 0.3:
                    variation = self.rng.choice([self.palette.shadow, self.palette.highlight])
                    canvas.set_pixel_solid(x, y, variation)

        # Draw grass blades
        num_blades = int(self.width * self.height * density)
        for _ in range(num_blades):
            bx = self.rng.randint(0, self.width - 1)
            by = self.rng.randint(0, self.height - 1)
            bh = self.rng.randint(1, blade_height)

            # Choose blade color
            blade_color = self.rng.choice([
                self.palette.highlight,
                self.palette.base,
                self.palette.shadow
            ])

            # Draw blade going up
            for i in range(bh):
                py = self._wrap_y(by - i)
                # Slight horizontal sway
                sway = 0 if i < bh // 2 else self.rng.choice([-1, 0, 0, 1])
                px = self._wrap_x(bx + sway)
                canvas.set_pixel_solid(px, py, blade_color)

        return canvas

    def generate_fabric(self, pattern: str = 'checkered',
                        pattern_size: int = 4) -> Canvas:
        """Generate a fabric pattern texture.

        Args:
            pattern: Pattern type ('checkered', 'striped', 'dotted')
            pattern_size: Size of pattern elements

        Returns:
            Canvas with seamless fabric texture
        """
        canvas = Canvas(self.width, self.height, self.palette.base)
        self.rng = random.Random(self.seed)

        if pattern == 'checkered':
            for y in range(self.height):
                for x in range(self.width):
                    cell_x = x // pattern_size
                    cell_y = y // pattern_size
                    if (cell_x + cell_y) % 2 == 0:
                        canvas.set_pixel_solid(x, y, self.palette.accent)

        elif pattern == 'striped':
            for y in range(self.height):
                stripe = y // pattern_size
                if stripe % 2 == 0:
                    for x in range(self.width):
                        canvas.set_pixel_solid(x, y, self.palette.accent)

        elif pattern == 'dotted':
            for y in range(0, self.height, pattern_size):
                for x in range(0, self.width, pattern_size):
                    # Place dot at center of cell
                    cx = x + pattern_size // 2
                    cy = y + pattern_size // 2
                    px = self._wrap_x(cx)
                    py = self._wrap_y(cy)
                    canvas.set_pixel_solid(px, py, self.palette.accent)

        # Add subtle texture variation
        for y in range(self.height):
            for x in range(self.width):
                if self.rng.random() < 0.1:
                    current = canvas.get_pixel(x, y)
                    if current:
                        variation = self.rng.randint(-10, 10)
                        new_color = (
                            max(0, min(255, current[0] + variation)),
                            max(0, min(255, current[1] + variation)),
                            max(0, min(255, current[2] + variation)),
                            255
                        )
                        canvas.set_pixel_solid(x, y, new_color)

        return canvas

    def generate_metal(self, style: str = 'brushed') -> Canvas:
        """Generate a metal texture.

        Args:
            style: Style of metal ('brushed', 'riveted', 'plated')

        Returns:
            Canvas with seamless metal texture
        """
        canvas = Canvas(self.width, self.height, self.palette.base)
        self.rng = random.Random(self.seed)

        if style == 'brushed':
            # Horizontal brush strokes
            for y in range(self.height):
                for x in range(self.width):
                    variation = self.rng.randint(-15, 15)
                    streak = self.rng.choice([0, 0, 0, -20, 20])
                    color = (
                        max(0, min(255, self.palette.base[0] + variation + streak)),
                        max(0, min(255, self.palette.base[1] + variation + streak)),
                        max(0, min(255, self.palette.base[2] + variation + streak)),
                        255
                    )
                    canvas.set_pixel_solid(x, y, color)

        elif style == 'riveted':
            # Base metal with rivet pattern
            rivet_spacing = max(4, self.width // 4)
            for y in range(0, self.height, rivet_spacing):
                for x in range(0, self.width, rivet_spacing):
                    # Draw rivet (small circle)
                    rx = self._wrap_x(x + rivet_spacing // 2)
                    ry = self._wrap_y(y + rivet_spacing // 2)

                    # Rivet center
                    canvas.set_pixel_solid(rx, ry, self.palette.highlight)

                    # Rivet shadow
                    canvas.set_pixel_solid(self._wrap_x(rx + 1), ry, self.palette.shadow)
                    canvas.set_pixel_solid(rx, self._wrap_y(ry + 1), self.palette.shadow)

        elif style == 'plated':
            # Metal plates with seams
            plate_size = max(8, self.width // 2)
            for py in range(0, self.height, plate_size):
                for px in range(0, self.width, plate_size):
                    # Draw plate edges (seams)
                    for i in range(plate_size):
                        # Horizontal seam
                        x = self._wrap_x(px + i)
                        y = self._wrap_y(py)
                        canvas.set_pixel_solid(x, y, self.palette.shadow)
                        canvas.set_pixel_solid(x, self._wrap_y(y + 1), self.palette.accent)

                        # Vertical seam
                        x = self._wrap_x(px)
                        y = self._wrap_y(py + i)
                        canvas.set_pixel_solid(x, y, self.palette.shadow)
                        canvas.set_pixel_solid(self._wrap_x(x + 1), y, self.palette.accent)

        return canvas


# Registry of texture generators
TEXTURE_GENERATORS: Dict[str, Callable] = {}


def _register_generators():
    """Register all texture type generators."""
    global TEXTURE_GENERATORS
    TEXTURE_GENERATORS = {
        'brick': lambda gen, **kw: gen.generate_brick(**kw),
        'stone': lambda gen, **kw: gen.generate_stone(**kw),
        'wood': lambda gen, **kw: gen.generate_wood(**kw),
        'grass': lambda gen, **kw: gen.generate_grass(**kw),
        'fabric': lambda gen, **kw: gen.generate_fabric(**kw),
        'fabric_checkered': lambda gen, **kw: gen.generate_fabric(pattern='checkered', **kw),
        'fabric_striped': lambda gen, **kw: gen.generate_fabric(pattern='striped', **kw),
        'fabric_dotted': lambda gen, **kw: gen.generate_fabric(pattern='dotted', **kw),
        'metal': lambda gen, **kw: gen.generate_metal(**kw),
        'metal_brushed': lambda gen, **kw: gen.generate_metal(style='brushed', **kw),
        'metal_riveted': lambda gen, **kw: gen.generate_metal(style='riveted', **kw),
        'metal_plated': lambda gen, **kw: gen.generate_metal(style='plated', **kw),
    }


_register_generators()


def list_texture_types() -> List[str]:
    """List all available texture types."""
    return sorted(TEXTURE_GENERATORS.keys())


def generate_texture(texture_type: str,
                     width: int = 32,
                     height: int = 32,
                     seed: int = 42,
                     palette: Optional[TexturePalette] = None,
                     **kwargs) -> Canvas:
    """Generate a texture of the specified type.

    Args:
        texture_type: Type of texture to generate
        width: Texture width in pixels
        height: Texture height in pixels
        seed: Random seed for deterministic generation
        palette: Optional color palette
        **kwargs: Additional arguments for specific texture types

    Returns:
        Canvas with seamless texture

    Raises:
        ValueError: If texture_type is not recognized
    """
    if texture_type not in TEXTURE_GENERATORS:
        available = ', '.join(sorted(TEXTURE_GENERATORS.keys()))
        raise ValueError(f"Unknown texture type '{texture_type}'. Available: {available}")

    gen = TextureGenerator(width, height, seed)

    # Set palette based on texture type if not provided
    if palette:
        gen.set_palette(palette)
    else:
        palette_map = {
            'brick': TexturePalette.brick,
            'stone': TexturePalette.stone,
            'wood': TexturePalette.wood,
            'grass': TexturePalette.grass,
            'metal': TexturePalette.metal,
            'metal_brushed': TexturePalette.metal,
            'metal_riveted': TexturePalette.metal,
            'metal_plated': TexturePalette.metal,
            'fabric': TexturePalette.fabric_red,
            'fabric_checkered': TexturePalette.fabric_red,
            'fabric_striped': TexturePalette.fabric_red,
            'fabric_dotted': TexturePalette.fabric_red,
        }
        if texture_type in palette_map:
            gen.set_palette(palette_map[texture_type]())

    return TEXTURE_GENERATORS[texture_type](gen, **kwargs)


__all__ = [
    'TextureType',
    'TexturePalette',
    'TextureGenerator',
    'generate_texture',
    'list_texture_types',
    'TEXTURE_GENERATORS',
]

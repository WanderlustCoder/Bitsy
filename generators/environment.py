"""
Environment Generator - Procedural generation of backgrounds and scenes.

Generates pixel art for:
- Skies (day, night, sunset, storm)
- Grounds (grass, stone, sand, snow)
- Parallax background layers
- Room interiors (dungeon, house, castle)
- Natural elements (mountains, forests, water)
"""

import math
import random
from typing import Dict, List, Tuple, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Canvas
from core.color import darken, lighten, blend_normal


class TimeOfDay(Enum):
    """Time of day presets."""
    DAWN = 'dawn'
    DAY = 'day'
    DUSK = 'dusk'
    NIGHT = 'night'
    MIDNIGHT = 'midnight'


class Weather(Enum):
    """Weather conditions."""
    CLEAR = 'clear'
    CLOUDY = 'cloudy'
    OVERCAST = 'overcast'
    RAIN = 'rain'
    STORM = 'storm'
    SNOW = 'snow'
    FOG = 'fog'


class TerrainType(Enum):
    """Ground terrain types."""
    GRASS = 'grass'
    STONE = 'stone'
    SAND = 'sand'
    SNOW = 'snow'
    DIRT = 'dirt'
    WATER = 'water'
    LAVA = 'lava'


class RoomType(Enum):
    """Interior room types."""
    DUNGEON = 'dungeon'
    HOUSE = 'house'
    CASTLE = 'castle'
    CAVE = 'cave'
    FOREST = 'forest'
    TEMPLE = 'temple'


@dataclass
class SkyPalette:
    """Color palette for sky generation."""
    top: Tuple[int, int, int, int] = (100, 150, 255, 255)
    middle: Tuple[int, int, int, int] = (150, 200, 255, 255)
    horizon: Tuple[int, int, int, int] = (200, 220, 255, 255)
    sun: Tuple[int, int, int, int] = (255, 255, 200, 255)
    cloud: Tuple[int, int, int, int] = (255, 255, 255, 255)
    cloud_shadow: Tuple[int, int, int, int] = (200, 200, 220, 255)
    star: Tuple[int, int, int, int] = (255, 255, 255, 255)

    @classmethod
    def day(cls) -> 'SkyPalette':
        return cls(
            top=(100, 150, 255, 255),
            middle=(150, 200, 255, 255),
            horizon=(200, 220, 255, 255),
            sun=(255, 255, 200, 255),
            cloud=(255, 255, 255, 255),
            cloud_shadow=(200, 200, 220, 255)
        )

    @classmethod
    def dawn(cls) -> 'SkyPalette':
        return cls(
            top=(50, 80, 150, 255),
            middle=(200, 150, 100, 255),
            horizon=(255, 180, 120, 255),
            sun=(255, 200, 150, 255),
            cloud=(255, 200, 180, 255),
            cloud_shadow=(180, 130, 100, 255)
        )

    @classmethod
    def dusk(cls) -> 'SkyPalette':
        return cls(
            top=(40, 50, 100, 255),
            middle=(150, 80, 100, 255),
            horizon=(255, 150, 100, 255),
            sun=(255, 100, 50, 255),
            cloud=(255, 180, 150, 255),
            cloud_shadow=(150, 80, 80, 255)
        )

    @classmethod
    def night(cls) -> 'SkyPalette':
        return cls(
            top=(10, 15, 40, 255),
            middle=(20, 30, 60, 255),
            horizon=(40, 50, 80, 255),
            sun=(200, 200, 220, 255),  # Moon
            cloud=(80, 90, 120, 255),
            cloud_shadow=(50, 60, 90, 255),
            star=(255, 255, 255, 255)
        )

    @classmethod
    def storm(cls) -> 'SkyPalette':
        return cls(
            top=(40, 50, 60, 255),
            middle=(60, 70, 80, 255),
            horizon=(80, 90, 100, 255),
            sun=(100, 100, 110, 255),
            cloud=(70, 75, 85, 255),
            cloud_shadow=(50, 55, 65, 255)
        )


@dataclass
class GroundPalette:
    """Color palette for ground/terrain generation."""
    base: Tuple[int, int, int, int] = (100, 150, 80, 255)
    light: Tuple[int, int, int, int] = (130, 180, 100, 255)
    dark: Tuple[int, int, int, int] = (70, 110, 60, 255)
    detail: Tuple[int, int, int, int] = (80, 130, 70, 255)
    accent: Tuple[int, int, int, int] = (120, 100, 80, 255)

    @classmethod
    def grass(cls) -> 'GroundPalette':
        return cls(
            base=(100, 150, 80, 255),
            light=(130, 180, 100, 255),
            dark=(70, 110, 60, 255),
            detail=(80, 130, 70, 255),
            accent=(120, 100, 60, 255)
        )

    @classmethod
    def stone(cls) -> 'GroundPalette':
        return cls(
            base=(120, 120, 130, 255),
            light=(150, 150, 160, 255),
            dark=(80, 80, 90, 255),
            detail=(100, 100, 110, 255),
            accent=(90, 90, 100, 255)
        )

    @classmethod
    def sand(cls) -> 'GroundPalette':
        return cls(
            base=(220, 200, 150, 255),
            light=(240, 220, 170, 255),
            dark=(180, 160, 120, 255),
            detail=(200, 180, 140, 255),
            accent=(190, 170, 130, 255)
        )

    @classmethod
    def snow(cls) -> 'GroundPalette':
        return cls(
            base=(240, 245, 255, 255),
            light=(255, 255, 255, 255),
            dark=(200, 210, 230, 255),
            detail=(220, 230, 245, 255),
            accent=(180, 200, 230, 255)
        )

    @classmethod
    def dirt(cls) -> 'GroundPalette':
        return cls(
            base=(120, 90, 60, 255),
            light=(150, 120, 80, 255),
            dark=(80, 60, 40, 255),
            detail=(100, 75, 50, 255),
            accent=(110, 85, 55, 255)
        )

    @classmethod
    def water(cls) -> 'GroundPalette':
        return cls(
            base=(60, 120, 180, 255),
            light=(100, 160, 220, 255),
            dark=(40, 80, 140, 255),
            detail=(70, 130, 190, 255),
            accent=(80, 140, 200, 200)  # Semi-transparent
        )

    @classmethod
    def lava(cls) -> 'GroundPalette':
        return cls(
            base=(255, 100, 50, 255),
            light=(255, 200, 100, 255),
            dark=(200, 50, 30, 255),
            detail=(255, 150, 70, 255),
            accent=(180, 40, 20, 255)
        )


class EnvironmentGenerator:
    """Generates pixel art environments and backgrounds."""

    def __init__(self, width: int = 64, height: int = 64, seed: int = 42):
        """Initialize environment generator.

        Args:
            width: Canvas width in pixels
            height: Canvas height in pixels
            seed: Random seed for reproducibility
        """
        self.width = width
        self.height = height
        self.seed = seed
        self.rng = random.Random(seed)

    def set_seed(self, seed: int) -> 'EnvironmentGenerator':
        """Set random seed."""
        self.seed = seed
        self.rng = random.Random(seed)
        return self

    def generate_sky(self, time_of_day: str = 'day',
                     weather: str = 'clear',
                     include_sun: bool = True,
                     include_stars: bool = False,
                     cloud_density: float = 0.3) -> Canvas:
        """Generate a sky background.

        Args:
            time_of_day: Time preset (dawn, day, dusk, night, midnight)
            weather: Weather condition (clear, cloudy, storm)
            include_sun: Whether to draw sun/moon
            include_stars: Whether to draw stars (for night)
            cloud_density: Cloud coverage 0.0 to 1.0

        Returns:
            Canvas with generated sky
        """
        canvas = Canvas(self.width, self.height)

        # Get palette for time of day
        time_palettes = {
            'dawn': SkyPalette.dawn(),
            'day': SkyPalette.day(),
            'dusk': SkyPalette.dusk(),
            'night': SkyPalette.night(),
            'midnight': SkyPalette.night(),
        }
        palette = time_palettes.get(time_of_day, SkyPalette.day())

        # Adjust for weather
        if weather in ('storm', 'overcast'):
            palette = SkyPalette.storm()
        elif weather == 'cloudy':
            cloud_density = max(cloud_density, 0.5)

        # Draw gradient sky
        for y in range(self.height):
            progress = y / self.height

            # Interpolate between top and horizon
            if progress < 0.5:
                t = progress * 2
                color = self._lerp_color(palette.top, palette.middle, t)
            else:
                t = (progress - 0.5) * 2
                color = self._lerp_color(palette.middle, palette.horizon, t)

            for x in range(self.width):
                canvas.set_pixel_solid(x, y, color)

        # Draw stars for night sky
        if include_stars and time_of_day in ('night', 'midnight'):
            star_count = int(self.width * self.height * 0.01)
            for _ in range(star_count):
                x = self.rng.randint(0, self.width - 1)
                y = self.rng.randint(0, int(self.height * 0.7))
                brightness = self.rng.randint(150, 255)
                star_color = (brightness, brightness, brightness, 255)
                canvas.set_pixel_solid(x, y, star_color)

        # Draw sun/moon
        if include_sun:
            sun_x = int(self.width * 0.7)
            sun_y = int(self.height * 0.2)
            sun_radius = max(3, self.width // 16)

            # Draw glow
            for dy in range(-sun_radius * 2, sun_radius * 2 + 1):
                for dx in range(-sun_radius * 2, sun_radius * 2 + 1):
                    dist = math.sqrt(dx * dx + dy * dy)
                    if dist < sun_radius * 2:
                        px, py = sun_x + dx, sun_y + dy
                        if 0 <= px < self.width and 0 <= py < self.height:
                            alpha = int(255 * (1 - dist / (sun_radius * 2)) * 0.3)
                            glow = (palette.sun[0], palette.sun[1], palette.sun[2], alpha)
                            current = canvas.get_pixel(px, py)
                            blended = blend_normal(current, glow)
                            canvas.set_pixel_solid(px, py, blended)

            # Draw sun/moon core
            canvas.fill_circle(sun_x, sun_y, sun_radius, palette.sun)

        # Draw clouds
        if cloud_density > 0 and weather != 'clear':
            self._draw_clouds(canvas, palette, cloud_density)

        return canvas

    def _draw_clouds(self, canvas: Canvas, palette: SkyPalette, density: float):
        """Draw clouds on sky canvas."""
        cloud_count = int(density * 10)

        for _ in range(cloud_count):
            cloud_x = self.rng.randint(0, self.width)
            cloud_y = self.rng.randint(0, int(self.height * 0.6))
            cloud_width = self.rng.randint(10, 30)
            cloud_height = self.rng.randint(4, 10)

            # Draw cloud as multiple overlapping circles
            for i in range(5):
                cx = cloud_x + self.rng.randint(-cloud_width // 2, cloud_width // 2)
                cy = cloud_y + self.rng.randint(-cloud_height // 3, cloud_height // 3)
                radius = self.rng.randint(3, 8)

                # Draw shadow first (offset down)
                canvas.fill_circle(cx, cy + 2, radius, palette.cloud_shadow)
                # Draw main cloud
                canvas.fill_circle(cx, cy, radius, palette.cloud)

    def generate_ground(self, terrain: str = 'grass',
                        height_variance: float = 0.2,
                        include_details: bool = True) -> Canvas:
        """Generate ground/terrain.

        Args:
            terrain: Terrain type (grass, stone, sand, snow, dirt)
            height_variance: How much the ground varies in height
            include_details: Add small details like rocks, plants

        Returns:
            Canvas with generated ground
        """
        canvas = Canvas(self.width, self.height)

        # Get palette
        terrain_palettes = {
            'grass': GroundPalette.grass(),
            'stone': GroundPalette.stone(),
            'sand': GroundPalette.sand(),
            'snow': GroundPalette.snow(),
            'dirt': GroundPalette.dirt(),
            'water': GroundPalette.water(),
            'lava': GroundPalette.lava(),
        }
        palette = terrain_palettes.get(terrain, GroundPalette.grass())

        # Generate height map for ground surface
        heights = []
        base_height = self.height // 3
        for x in range(self.width):
            # Simple noise-like height variation
            noise = math.sin(x * 0.1) * 0.3 + math.sin(x * 0.3) * 0.2
            noise += self.rng.random() * 0.1 - 0.05
            h = base_height + int(noise * height_variance * self.height)
            heights.append(h)

        # Draw ground
        for x in range(self.width):
            surface_y = self.height - heights[x]

            for y in range(self.height):
                if y >= surface_y:
                    depth = y - surface_y

                    # Surface layer
                    if depth < 2:
                        canvas.set_pixel_solid(x, y, palette.light)
                    # Main layer
                    elif depth < 6:
                        if (x + y) % 3 == 0:
                            canvas.set_pixel_solid(x, y, palette.base)
                        else:
                            canvas.set_pixel_solid(x, y, palette.detail)
                    # Deep layer
                    else:
                        canvas.set_pixel_solid(x, y, palette.dark)

        # Add details
        if include_details:
            self._add_terrain_details(canvas, terrain, heights, palette)

        return canvas

    def _add_terrain_details(self, canvas: Canvas, terrain: str,
                             heights: List[int], palette: GroundPalette):
        """Add small details to terrain."""
        detail_count = self.width // 8

        if terrain == 'grass':
            # Add grass blades
            for _ in range(detail_count * 2):
                x = self.rng.randint(0, self.width - 1)
                surface_y = self.height - heights[x]

                for i in range(3):
                    if surface_y - i >= 0:
                        canvas.set_pixel_solid(x, surface_y - i, palette.light)

            # Add flowers
            for _ in range(detail_count // 2):
                x = self.rng.randint(0, self.width - 1)
                surface_y = self.height - heights[x]
                if surface_y - 2 >= 0:
                    flower_colors = [(255, 100, 100, 255), (255, 255, 100, 255),
                                     (200, 100, 255, 255), (100, 200, 255, 255)]
                    color = self.rng.choice(flower_colors)
                    canvas.set_pixel_solid(x, surface_y - 2, color)

        elif terrain == 'stone':
            # Add rocks
            for _ in range(detail_count):
                x = self.rng.randint(0, self.width - 1)
                surface_y = self.height - heights[x]

                rock_size = self.rng.randint(1, 3)
                rock_color = darken(palette.base, self.rng.random() * 0.3)
                canvas.fill_circle(x, surface_y - rock_size, rock_size, rock_color)

        elif terrain in ('sand', 'snow'):
            # Add dunes/drifts
            for _ in range(detail_count):
                x = self.rng.randint(0, self.width - 1)
                surface_y = self.height - heights[x]
                if surface_y - 1 >= 0:
                    highlight = lighten(palette.light, 0.1)
                    canvas.set_pixel_solid(x, surface_y - 1, highlight)

    def generate_parallax_layers(self, theme: str = 'forest',
                                 num_layers: int = 3) -> List[Canvas]:
        """Generate parallax background layers.

        Args:
            theme: Visual theme (forest, mountains, city, cave)
            num_layers: Number of layers to generate

        Returns:
            List of Canvas objects, from back to front
        """
        layers = []

        generators = {
            'forest': self._generate_forest_layers,
            'mountains': self._generate_mountain_layers,
            'city': self._generate_city_layers,
            'cave': self._generate_cave_layers,
        }

        generator = generators.get(theme, self._generate_forest_layers)

        for i in range(num_layers):
            depth = i / num_layers  # 0 = far, 1 = near
            layer = generator(depth)
            layers.append(layer)

        return layers

    def _generate_forest_layers(self, depth: float) -> Canvas:
        """Generate forest parallax layer."""
        canvas = Canvas(self.width, self.height)

        # Deeper = more faded blue tint
        fade = 1 - depth
        base_green = int(80 + fade * 50)
        dark_green = int(40 + fade * 30)

        tree_color = (dark_green, base_green, dark_green, 255)
        trunk_color = (60 + int(fade * 40), 40 + int(fade * 20), 30, 255)

        # Draw trees
        tree_count = int(3 + depth * 5)
        tree_size = int(self.height * (0.3 + depth * 0.3))

        for _ in range(tree_count):
            x = self.rng.randint(0, self.width - 1)
            base_y = self.height

            # Tree trunk
            trunk_height = tree_size // 3
            trunk_width = max(2, tree_size // 8)
            for ty in range(trunk_height):
                for tx in range(-trunk_width // 2, trunk_width // 2 + 1):
                    px = x + tx
                    py = base_y - ty
                    if 0 <= px < self.width and 0 <= py < self.height:
                        canvas.set_pixel_solid(px, py, trunk_color)

            # Tree foliage (triangle)
            foliage_height = tree_size - trunk_height
            foliage_y = base_y - trunk_height

            for fy in range(foliage_height):
                row_width = int((foliage_height - fy) * 0.8)
                for fx in range(-row_width, row_width + 1):
                    px = x + fx
                    py = foliage_y - fy
                    if 0 <= px < self.width and 0 <= py < self.height:
                        # Vary color slightly
                        color_var = (
                            tree_color[0] + self.rng.randint(-10, 10),
                            tree_color[1] + self.rng.randint(-10, 10),
                            tree_color[2] + self.rng.randint(-10, 10),
                            255
                        )
                        canvas.set_pixel_solid(px, py, color_var)

        return canvas

    def _generate_mountain_layers(self, depth: float) -> Canvas:
        """Generate mountain parallax layer."""
        canvas = Canvas(self.width, self.height)

        # Color based on depth (atmospheric perspective)
        fade = 1 - depth
        gray = int(100 + fade * 100)
        blue_tint = int(fade * 50)
        mountain_color = (gray - 20, gray, gray + blue_tint, 255)
        snow_color = (230 + int(fade * 25), 235 + int(fade * 20), 255, 255)

        # Generate mountain peaks
        peak_count = int(2 + depth * 3)
        peaks = []

        for _ in range(peak_count):
            peak_x = self.rng.randint(0, self.width - 1)
            peak_y = int(self.height * (0.2 + depth * 0.3))
            peak_width = self.rng.randint(
                self.width // 4,
                self.width // 2
            )
            peaks.append((peak_x, peak_y, peak_width))

        # Draw mountains
        for peak_x, peak_y, peak_width in peaks:
            for x in range(self.width):
                dx = abs(x - peak_x)
                if dx < peak_width:
                    height = peak_y + int((dx / peak_width) ** 2 * (self.height - peak_y))

                    for y in range(height, self.height):
                        if canvas.get_pixel(x, y)[3] == 0:  # Not already drawn
                            # Snow cap on top portion
                            if y < peak_y + (self.height - peak_y) * 0.2:
                                canvas.set_pixel_solid(x, y, snow_color)
                            else:
                                canvas.set_pixel_solid(x, y, mountain_color)

        return canvas

    def _generate_city_layers(self, depth: float) -> Canvas:
        """Generate city skyline parallax layer."""
        canvas = Canvas(self.width, self.height)

        # Buildings get darker/bluer in distance
        fade = 1 - depth
        gray = int(60 + fade * 40)
        building_color = (gray, gray, gray + 20, 255)
        window_color = (200 + int(fade * 55), 200, 100, 255)

        # Generate buildings
        x = 0
        while x < self.width:
            building_width = self.rng.randint(5, 15)
            building_height = self.rng.randint(
                int(self.height * (0.3 + depth * 0.2)),
                int(self.height * (0.5 + depth * 0.3))
            )

            base_y = self.height

            # Draw building
            for bx in range(building_width):
                for by in range(building_height):
                    px = x + bx
                    py = base_y - by
                    if 0 <= px < self.width and 0 <= py < self.height:
                        canvas.set_pixel_solid(px, py, building_color)

            # Add windows
            if depth > 0.3:  # Only near buildings have visible windows
                for wy in range(2, building_height - 2, 4):
                    for wx in range(2, building_width - 2, 3):
                        px = x + wx
                        py = base_y - wy
                        if 0 <= px < self.width and 0 <= py < self.height:
                            if self.rng.random() > 0.3:  # Some windows lit
                                canvas.set_pixel_solid(px, py, window_color)

            x += building_width + self.rng.randint(1, 5)

        return canvas

    def _generate_cave_layers(self, depth: float) -> Canvas:
        """Generate cave parallax layer."""
        canvas = Canvas(self.width, self.height)

        # Dark colors for cave
        fade = depth  # Closer = darker in caves
        gray = int(30 + (1 - fade) * 40)
        rock_color = (gray, gray - 5, gray - 10, 255)

        # Stalactites from top
        for x in range(0, self.width, 3):
            stalactite_length = self.rng.randint(5, 15 + int(depth * 10))
            for y in range(stalactite_length):
                width = max(1, 3 - y // 4)
                for dx in range(-width, width + 1):
                    px = x + dx
                    if 0 <= px < self.width:
                        canvas.set_pixel_solid(px, y, rock_color)

        # Stalagmites from bottom
        for x in range(2, self.width, 4):
            stalagmite_length = self.rng.randint(3, 10 + int(depth * 8))
            for y in range(stalagmite_length):
                width = max(1, 2 - y // 5)
                for dx in range(-width, width + 1):
                    px = x + dx
                    py = self.height - 1 - y
                    if 0 <= px < self.width and py >= 0:
                        canvas.set_pixel_solid(px, py, rock_color)

        return canvas

    def generate_room_interior(self, room_type: str = 'dungeon',
                               style: str = 'simple') -> Canvas:
        """Generate an interior room background.

        Args:
            room_type: Type of room (dungeon, house, castle, cave)
            style: Art style (simple, detailed)

        Returns:
            Canvas with generated room
        """
        canvas = Canvas(self.width, self.height)

        generators = {
            'dungeon': self._generate_dungeon_room,
            'house': self._generate_house_room,
            'castle': self._generate_castle_room,
            'cave': self._generate_cave_room,
        }

        generator = generators.get(room_type, self._generate_dungeon_room)
        return generator(style)

    def _generate_dungeon_room(self, style: str) -> Canvas:
        """Generate dungeon interior."""
        canvas = Canvas(self.width, self.height)

        # Stone wall colors
        wall_color = (80, 80, 90, 255)
        wall_light = (100, 100, 110, 255)
        wall_dark = (50, 50, 60, 255)
        floor_color = (60, 60, 70, 255)

        # Fill with wall
        canvas.fill_rect(0, 0, self.width, self.height, wall_color)

        # Add floor
        floor_y = int(self.height * 0.7)
        canvas.fill_rect(0, floor_y, self.width, self.height - floor_y, floor_color)

        # Add brick pattern to walls
        brick_height = 4
        brick_width = 8

        for y in range(0, floor_y, brick_height):
            offset = (y // brick_height) % 2 * (brick_width // 2)
            for x in range(offset, self.width, brick_width):
                # Brick outline
                color = wall_light if (x + y) % 2 == 0 else wall_dark
                # Top edge
                if y > 0:
                    for bx in range(brick_width - 1):
                        if x + bx < self.width:
                            canvas.set_pixel_solid(x + bx, y, wall_dark)
                # Left edge
                for by in range(brick_height):
                    if y + by < floor_y:
                        canvas.set_pixel_solid(x, y + by, wall_dark)

        # Add torch
        torch_x = self.width // 4
        torch_y = self.height // 3

        # Torch holder
        canvas.fill_rect(torch_x - 1, torch_y, 3, 4, (100, 80, 60, 255))

        # Flame
        flame_colors = [(255, 200, 50, 255), (255, 150, 50, 255), (255, 100, 50, 255)]
        canvas.fill_circle(torch_x, torch_y - 2, 2, flame_colors[0])
        canvas.set_pixel_solid(torch_x, torch_y - 4, flame_colors[1])

        return canvas

    def _generate_house_room(self, style: str) -> Canvas:
        """Generate house interior."""
        canvas = Canvas(self.width, self.height)

        # Warm wood colors
        wall_color = (180, 160, 140, 255)
        floor_color = (120, 90, 60, 255)
        floor_light = (140, 110, 80, 255)
        trim_color = (100, 80, 60, 255)

        # Fill wall
        canvas.fill_rect(0, 0, self.width, self.height, wall_color)

        # Floor
        floor_y = int(self.height * 0.7)
        canvas.fill_rect(0, floor_y, self.width, self.height - floor_y, floor_color)

        # Wood plank pattern on floor
        plank_width = 6
        for x in range(0, self.width, plank_width):
            for y in range(floor_y, self.height):
                if x + plank_width < self.width:
                    canvas.set_pixel_solid(x + plank_width - 1, y, trim_color)
                if (x // plank_width + y) % 4 == 0:
                    canvas.set_pixel_solid(x + 2, y, floor_light)

        # Baseboard
        canvas.fill_rect(0, floor_y - 2, self.width, 2, trim_color)

        # Window
        window_x = self.width // 3
        window_y = self.height // 4
        window_w = self.width // 4
        window_h = self.height // 3

        # Window frame
        canvas.fill_rect(window_x - 2, window_y - 2, window_w + 4, window_h + 4, trim_color)
        # Window glass (sky blue)
        canvas.fill_rect(window_x, window_y, window_w, window_h, (150, 200, 255, 255))
        # Cross frame
        canvas.fill_rect(window_x + window_w // 2 - 1, window_y, 2, window_h, trim_color)
        canvas.fill_rect(window_x, window_y + window_h // 2 - 1, window_w, 2, trim_color)

        return canvas

    def _generate_castle_room(self, style: str) -> Canvas:
        """Generate castle interior."""
        canvas = Canvas(self.width, self.height)

        # Gray stone with regal accents
        wall_color = (100, 100, 110, 255)
        floor_color = (80, 80, 90, 255)
        banner_red = (180, 50, 50, 255)
        gold = (200, 170, 80, 255)

        # Fill wall
        canvas.fill_rect(0, 0, self.width, self.height, wall_color)

        # Floor
        floor_y = int(self.height * 0.75)
        canvas.fill_rect(0, floor_y, self.width, self.height - floor_y, floor_color)

        # Tile pattern
        tile_size = 8
        for tx in range(0, self.width, tile_size):
            for ty in range(floor_y, self.height, tile_size):
                if (tx // tile_size + ty // tile_size) % 2 == 0:
                    canvas.fill_rect(tx, ty, tile_size - 1, tile_size - 1,
                                     (90, 90, 100, 255))

        # Banner
        banner_x = self.width // 2 - 4
        banner_y = 4
        banner_w = 8
        banner_h = self.height // 3

        canvas.fill_rect(banner_x, banner_y, banner_w, banner_h, banner_red)
        # Gold trim
        canvas.fill_rect(banner_x, banner_y, banner_w, 2, gold)
        canvas.fill_rect(banner_x, banner_y + banner_h - 2, banner_w, 2, gold)
        # Banner points at bottom
        for i in range(4):
            canvas.set_pixel_solid(banner_x + i, banner_y + banner_h + i, banner_red)
            canvas.set_pixel_solid(banner_x + banner_w - 1 - i, banner_y + banner_h + i,
                                   banner_red)

        return canvas

    def _generate_cave_room(self, style: str) -> Canvas:
        """Generate cave interior."""
        canvas = Canvas(self.width, self.height)

        # Dark rocky colors
        wall_color = (50, 45, 40, 255)
        floor_color = (40, 35, 30, 255)
        highlight = (70, 65, 60, 255)

        # Fill with dark
        canvas.fill_rect(0, 0, self.width, self.height, wall_color)

        # Rough, organic edges
        for y in range(self.height):
            left_edge = int(math.sin(y * 0.2) * 5 + self.rng.random() * 3)
            right_edge = self.width - int(math.sin(y * 0.15) * 4 + self.rng.random() * 3)

            for x in range(left_edge):
                canvas.set_pixel_solid(x, y, (0, 0, 0, 255))
            for x in range(right_edge, self.width):
                canvas.set_pixel_solid(x, y, (0, 0, 0, 255))

        # Floor
        floor_y = int(self.height * 0.7)
        for x in range(self.width):
            floor_height = floor_y + int(math.sin(x * 0.3) * 3 + self.rng.random() * 2)
            for y in range(floor_height, self.height):
                canvas.set_pixel_solid(x, y, floor_color)

        # Add rock details
        for _ in range(10):
            x = self.rng.randint(5, self.width - 5)
            y = self.rng.randint(5, self.height - 5)
            canvas.set_pixel_solid(x, y, highlight)

        return canvas

    def _lerp_color(self, c1: Tuple[int, int, int, int],
                    c2: Tuple[int, int, int, int],
                    t: float) -> Tuple[int, int, int, int]:
        """Linear interpolation between two colors."""
        return (
            int(c1[0] + (c2[0] - c1[0]) * t),
            int(c1[1] + (c2[1] - c1[1]) * t),
            int(c1[2] + (c2[2] - c1[2]) * t),
            int(c1[3] + (c2[3] - c1[3]) * t)
        )


# Convenience functions
def generate_sky(width: int = 64, height: int = 64, time_of_day: str = 'day',
                 weather: str = 'clear', seed: int = 42) -> Canvas:
    """Generate a sky background.

    Args:
        width: Canvas width
        height: Canvas height
        time_of_day: Time preset
        weather: Weather condition
        seed: Random seed

    Returns:
        Canvas with generated sky
    """
    gen = EnvironmentGenerator(width, height, seed)
    return gen.generate_sky(time_of_day, weather)


def generate_ground(width: int = 64, height: int = 64, terrain: str = 'grass',
                    seed: int = 42) -> Canvas:
    """Generate ground/terrain.

    Args:
        width: Canvas width
        height: Canvas height
        terrain: Terrain type
        seed: Random seed

    Returns:
        Canvas with generated ground
    """
    gen = EnvironmentGenerator(width, height, seed)
    return gen.generate_ground(terrain)


def generate_parallax(width: int = 64, height: int = 64, theme: str = 'forest',
                      num_layers: int = 3, seed: int = 42) -> List[Canvas]:
    """Generate parallax background layers.

    Args:
        width: Canvas width
        height: Canvas height
        theme: Visual theme
        num_layers: Number of layers
        seed: Random seed

    Returns:
        List of Canvas layers
    """
    gen = EnvironmentGenerator(width, height, seed)
    return gen.generate_parallax_layers(theme, num_layers)


def generate_room(width: int = 64, height: int = 64, room_type: str = 'dungeon',
                  seed: int = 42) -> Canvas:
    """Generate interior room.

    Args:
        width: Canvas width
        height: Canvas height
        room_type: Type of room
        seed: Random seed

    Returns:
        Canvas with generated room
    """
    gen = EnvironmentGenerator(width, height, seed)
    return gen.generate_room_interior(room_type)


def list_time_of_day() -> List[str]:
    """List available time of day presets."""
    return [t.value for t in TimeOfDay]


def list_weather() -> List[str]:
    """List available weather conditions."""
    return [w.value for w in Weather]


def list_terrain_types() -> List[str]:
    """List available terrain types."""
    return [t.value for t in TerrainType]


def list_room_types() -> List[str]:
    """List available room types."""
    return [r.value for r in RoomType]

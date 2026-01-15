"""
Terrain - Procedural terrain and biome generation.

Provides noise-based terrain generation for creating:
- Height maps
- Biome maps
- Natural-looking terrain distributions
"""

import math
import random
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass, field

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Canvas
from .autotile import AutoTile, AutoTile16, AutoTile47, TileConfig
from .connections import TileMap, TileDefinition


# =============================================================================
# Noise Functions
# =============================================================================

class PerlinNoise:
    """Simple Perlin-like noise generator.

    Produces smooth, continuous noise suitable for terrain generation.
    Uses value noise with cubic interpolation for simplicity.
    """

    def __init__(self, seed: int = 42):
        """Initialize noise generator.

        Args:
            seed: Random seed for reproducibility
        """
        self.seed = seed
        self.rng = random.Random(seed)

        # Generate permutation table
        self.perm = list(range(256))
        self.rng.shuffle(self.perm)
        self.perm = self.perm + self.perm  # Duplicate for wrapping

        # Generate gradient table
        self.gradients = [
            (self.rng.uniform(-1, 1), self.rng.uniform(-1, 1))
            for _ in range(256)
        ]
        # Normalize gradients
        self.gradients = [
            (g[0] / math.sqrt(g[0]*g[0] + g[1]*g[1] + 0.0001),
             g[1] / math.sqrt(g[0]*g[0] + g[1]*g[1] + 0.0001))
            for g in self.gradients
        ]

    def noise(self, x: float, y: float) -> float:
        """Get noise value at position.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            Noise value in range [-1, 1]
        """
        # Grid cell coordinates
        x0 = int(math.floor(x)) & 255
        y0 = int(math.floor(y)) & 255
        x1 = (x0 + 1) & 255
        y1 = (y0 + 1) & 255

        # Local coordinates within cell
        dx = x - math.floor(x)
        dy = y - math.floor(y)

        # Fade curves
        u = self._fade(dx)
        v = self._fade(dy)

        # Hash coordinates
        aa = self.perm[self.perm[x0] + y0]
        ab = self.perm[self.perm[x0] + y1]
        ba = self.perm[self.perm[x1] + y0]
        bb = self.perm[self.perm[x1] + y1]

        # Gradient dot products
        g_aa = self._grad(aa, dx, dy)
        g_ab = self._grad(ab, dx, dy - 1)
        g_ba = self._grad(ba, dx - 1, dy)
        g_bb = self._grad(bb, dx - 1, dy - 1)

        # Interpolate
        x1_interp = self._lerp(g_aa, g_ba, u)
        x2_interp = self._lerp(g_ab, g_bb, u)
        return self._lerp(x1_interp, x2_interp, v)

    def _fade(self, t: float) -> float:
        """Fade function for smooth interpolation."""
        return t * t * t * (t * (t * 6 - 15) + 10)

    def _lerp(self, a: float, b: float, t: float) -> float:
        """Linear interpolation."""
        return a + t * (b - a)

    def _grad(self, hash_val: int, x: float, y: float) -> float:
        """Gradient dot product."""
        g = self.gradients[hash_val & 255]
        return g[0] * x + g[1] * y

    def octave_noise(self, x: float, y: float, octaves: int = 4,
                     persistence: float = 0.5, lacunarity: float = 2.0) -> float:
        """Get multi-octave noise (fractal noise).

        Args:
            x: X coordinate
            y: Y coordinate
            octaves: Number of noise layers
            persistence: Amplitude reduction per octave
            lacunarity: Frequency increase per octave

        Returns:
            Combined noise value, normalized to approximately [-1, 1]
        """
        total = 0.0
        amplitude = 1.0
        frequency = 1.0
        max_value = 0.0

        for _ in range(octaves):
            total += self.noise(x * frequency, y * frequency) * amplitude
            max_value += amplitude
            amplitude *= persistence
            frequency *= lacunarity

        return total / max_value if max_value > 0 else 0.0


class SimplexNoise:
    """Simplex noise generator (2D).

    More efficient and produces better gradients than Perlin noise.
    """

    # Skew factors for 2D
    F2 = 0.5 * (math.sqrt(3.0) - 1.0)
    G2 = (3.0 - math.sqrt(3.0)) / 6.0

    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = random.Random(seed)

        # Permutation table
        self.perm = list(range(256))
        self.rng.shuffle(self.perm)
        self.perm = self.perm + self.perm

        # Gradients for 2D
        self.grad2 = [
            (1, 1), (-1, 1), (1, -1), (-1, -1),
            (1, 0), (-1, 0), (0, 1), (0, -1),
        ]

    def noise(self, x: float, y: float) -> float:
        """Get simplex noise value at position."""
        # Skew input space
        s = (x + y) * self.F2
        i = int(math.floor(x + s))
        j = int(math.floor(y + s))

        # Unskew back
        t = (i + j) * self.G2
        x0 = x - (i - t)
        y0 = y - (j - t)

        # Determine simplex
        if x0 > y0:
            i1, j1 = 1, 0
        else:
            i1, j1 = 0, 1

        x1 = x0 - i1 + self.G2
        y1 = y0 - j1 + self.G2
        x2 = x0 - 1.0 + 2.0 * self.G2
        y2 = y0 - 1.0 + 2.0 * self.G2

        # Hash coordinates
        ii = i & 255
        jj = j & 255

        # Calculate contributions
        n0 = self._contribution(x0, y0, ii, jj)
        n1 = self._contribution(x1, y1, ii + i1, jj + j1)
        n2 = self._contribution(x2, y2, ii + 1, jj + 1)

        # Scale to [-1, 1]
        return 70.0 * (n0 + n1 + n2)

    def _contribution(self, x: float, y: float, i: int, j: int) -> float:
        """Calculate contribution from one corner."""
        t = 0.5 - x * x - y * y
        if t < 0:
            return 0.0

        gi = self.perm[(i + self.perm[j & 255]) & 255] % 8
        g = self.grad2[gi]
        t *= t
        return t * t * (g[0] * x + g[1] * y)

    def octave_noise(self, x: float, y: float, octaves: int = 4,
                     persistence: float = 0.5, lacunarity: float = 2.0) -> float:
        """Get multi-octave simplex noise."""
        total = 0.0
        amplitude = 1.0
        frequency = 1.0
        max_value = 0.0

        for _ in range(octaves):
            total += self.noise(x * frequency, y * frequency) * amplitude
            max_value += amplitude
            amplitude *= persistence
            frequency *= lacunarity

        return total / max_value if max_value > 0 else 0.0


# =============================================================================
# Terrain Generation
# =============================================================================

@dataclass
class BiomeDefinition:
    """Definition of a terrain biome.

    Attributes:
        id: Unique biome identifier
        name: Human-readable name
        tile_id: Associated tile type ID for tilemap
        height_range: (min, max) height values for this biome
        moisture_range: (min, max) moisture values
        temperature_range: (min, max) temperature values
        color: Preview color for visualization
    """

    id: int
    name: str
    tile_id: int
    height_range: Tuple[float, float] = (0.0, 1.0)
    moisture_range: Tuple[float, float] = (0.0, 1.0)
    temperature_range: Tuple[float, float] = (0.0, 1.0)
    color: Tuple[int, int, int, int] = (100, 100, 100, 255)

    def matches(self, height: float, moisture: float = 0.5,
                temperature: float = 0.5) -> bool:
        """Check if given values fall within this biome's ranges."""
        h_min, h_max = self.height_range
        m_min, m_max = self.moisture_range
        t_min, t_max = self.temperature_range

        return (h_min <= height <= h_max and
                m_min <= moisture <= m_max and
                t_min <= temperature <= t_max)


class TerrainGenerator:
    """Procedural terrain generator.

    Uses noise functions to create natural-looking terrain with
    multiple biomes based on height, moisture, and temperature.
    """

    def __init__(self, seed: int = 42):
        """Initialize terrain generator.

        Args:
            seed: Random seed for reproducibility
        """
        self.seed = seed
        self.rng = random.Random(seed)

        # Noise generators for different terrain aspects
        self.height_noise = PerlinNoise(seed)
        self.moisture_noise = PerlinNoise(seed + 1000)
        self.temperature_noise = PerlinNoise(seed + 2000)

        # Biome definitions
        self.biomes: List[BiomeDefinition] = []

        # Generation parameters
        self.height_scale = 0.05
        self.height_octaves = 4
        self.moisture_scale = 0.03
        self.moisture_octaves = 3
        self.temperature_scale = 0.02
        self.temperature_octaves = 2

    def add_biome(self, biome: BiomeDefinition) -> None:
        """Add a biome definition."""
        self.biomes.append(biome)
        # Sort by height range (lower first)
        self.biomes.sort(key=lambda b: b.height_range[0])

    def add_default_biomes(self) -> None:
        """Add a default set of biomes."""
        self.biomes = [
            BiomeDefinition(
                id=1, name="deep_water", tile_id=1,
                height_range=(0.0, 0.3),
                color=(30, 60, 120, 255)
            ),
            BiomeDefinition(
                id=2, name="shallow_water", tile_id=2,
                height_range=(0.3, 0.4),
                color=(50, 100, 180, 255)
            ),
            BiomeDefinition(
                id=3, name="sand", tile_id=3,
                height_range=(0.4, 0.45),
                color=(210, 200, 140, 255)
            ),
            BiomeDefinition(
                id=4, name="grass", tile_id=4,
                height_range=(0.45, 0.65),
                color=(80, 160, 80, 255)
            ),
            BiomeDefinition(
                id=5, name="forest", tile_id=5,
                height_range=(0.65, 0.75),
                color=(40, 100, 40, 255)
            ),
            BiomeDefinition(
                id=6, name="mountain", tile_id=6,
                height_range=(0.75, 0.85),
                color=(120, 110, 100, 255)
            ),
            BiomeDefinition(
                id=7, name="snow", tile_id=7,
                height_range=(0.85, 1.0),
                color=(240, 240, 250, 255)
            ),
        ]

    def get_height(self, x: float, y: float) -> float:
        """Get height value at world position.

        Returns:
            Height value normalized to [0, 1]
        """
        value = self.height_noise.octave_noise(
            x * self.height_scale,
            y * self.height_scale,
            self.height_octaves
        )
        # Normalize from [-1, 1] to [0, 1]
        return (value + 1.0) * 0.5

    def get_moisture(self, x: float, y: float) -> float:
        """Get moisture value at world position."""
        value = self.moisture_noise.octave_noise(
            x * self.moisture_scale,
            y * self.moisture_scale,
            self.moisture_octaves
        )
        return (value + 1.0) * 0.5

    def get_temperature(self, x: float, y: float) -> float:
        """Get temperature value at world position."""
        value = self.temperature_noise.octave_noise(
            x * self.temperature_scale,
            y * self.temperature_scale,
            self.temperature_octaves
        )
        return (value + 1.0) * 0.5

    def get_biome(self, x: float, y: float) -> Optional[BiomeDefinition]:
        """Get the biome at a world position."""
        height = self.get_height(x, y)
        moisture = self.get_moisture(x, y)
        temperature = self.get_temperature(x, y)

        for biome in self.biomes:
            if biome.matches(height, moisture, temperature):
                return biome

        return None

    def generate_height_map(self, width: int, height: int,
                            offset_x: float = 0, offset_y: float = 0) -> List[List[float]]:
        """Generate a 2D height map.

        Args:
            width: Map width
            height: Map height
            offset_x: World X offset
            offset_y: World Y offset

        Returns:
            2D array of height values [0, 1]
        """
        return [
            [self.get_height(x + offset_x, y + offset_y) for x in range(width)]
            for y in range(height)
        ]

    def generate_biome_map(self, width: int, height: int,
                           offset_x: float = 0, offset_y: float = 0) -> List[List[int]]:
        """Generate a 2D biome map.

        Args:
            width: Map width
            height: Map height
            offset_x: World X offset
            offset_y: World Y offset

        Returns:
            2D array of biome IDs
        """
        result = []
        for y in range(height):
            row = []
            for x in range(width):
                biome = self.get_biome(x + offset_x, y + offset_y)
                row.append(biome.id if biome else 0)
            result.append(row)
        return result

    def generate_tilemap(self, width: int, height: int, tile_size: int = 16,
                         offset_x: float = 0, offset_y: float = 0) -> TileMap:
        """Generate a TileMap with terrain.

        Args:
            width: Map width in tiles
            height: Map height in tiles
            tile_size: Tile size in pixels
            offset_x: World X offset
            offset_y: World Y offset

        Returns:
            TileMap with terrain data
        """
        tilemap = TileMap(width, height, tile_size)

        # Register biome tiles
        for biome in self.biomes:
            config = TileConfig(
                size=tile_size,
                base_color=biome.color,
                highlight_color=self._lighten(biome.color),
                shadow_color=self._darken(biome.color),
                edge_color=self._darken(biome.color, 0.5),
                style='shaded'
            )
            autotile = AutoTile47(config, self.seed + biome.id)
            autotile.generate_all()

            tile_def = TileDefinition(
                id=biome.tile_id,
                name=biome.name,
                autotile=autotile,
                walkable=biome.name not in ('deep_water', 'shallow_water'),
            )
            tilemap.register_tile(tile_def)

        # Fill tilemap with biome data
        for y in range(height):
            for x in range(width):
                biome = self.get_biome(x + offset_x, y + offset_y)
                if biome:
                    tilemap.set_tile(x, y, biome.tile_id)

        return tilemap

    def render_preview(self, width: int, height: int,
                       offset_x: float = 0, offset_y: float = 0) -> Canvas:
        """Render a preview image of the terrain.

        Args:
            width: Image width in pixels
            height: Image height in pixels
            offset_x: World X offset
            offset_y: World Y offset

        Returns:
            Canvas with terrain preview
        """
        canvas = Canvas(width, height, (0, 0, 0, 255))

        for y in range(height):
            for x in range(width):
                biome = self.get_biome(x + offset_x, y + offset_y)
                if biome:
                    canvas.set_pixel(x, y, biome.color)
                else:
                    # Use height-based grayscale if no biome matches
                    h = self.get_height(x + offset_x, y + offset_y)
                    gray = int(h * 255)
                    canvas.set_pixel(x, y, (gray, gray, gray, 255))

        return canvas

    def _lighten(self, color: Tuple[int, int, int, int],
                 factor: float = 0.3) -> Tuple[int, int, int, int]:
        """Lighten a color."""
        return (
            min(255, int(color[0] + (255 - color[0]) * factor)),
            min(255, int(color[1] + (255 - color[1]) * factor)),
            min(255, int(color[2] + (255 - color[2]) * factor)),
            color[3]
        )

    def _darken(self, color: Tuple[int, int, int, int],
                factor: float = 0.3) -> Tuple[int, int, int, int]:
        """Darken a color."""
        return (
            int(color[0] * (1 - factor)),
            int(color[1] * (1 - factor)),
            int(color[2] * (1 - factor)),
            color[3]
        )


class IslandGenerator(TerrainGenerator):
    """Terrain generator that creates island-like landmasses.

    Applies a radial falloff to create islands surrounded by water.
    """

    def __init__(self, seed: int = 42, island_size: float = 0.8):
        """Initialize island generator.

        Args:
            seed: Random seed
            island_size: Island size factor (0-1, larger = bigger island)
        """
        super().__init__(seed)
        self.island_size = island_size
        self.center_x = 0.0
        self.center_y = 0.0
        self.radius = 50.0

    def set_island_center(self, x: float, y: float, radius: float) -> None:
        """Set the island center and radius."""
        self.center_x = x
        self.center_y = y
        self.radius = radius

    def get_height(self, x: float, y: float) -> float:
        """Get height with island falloff applied."""
        # Base noise height
        base_height = super().get_height(x, y)

        # Calculate distance from island center
        dx = x - self.center_x
        dy = y - self.center_y
        dist = math.sqrt(dx * dx + dy * dy)

        # Radial falloff
        if self.radius > 0:
            normalized_dist = dist / self.radius
            # Smooth falloff using smoothstep
            if normalized_dist >= 1.0:
                falloff = 0.0
            elif normalized_dist <= self.island_size:
                falloff = 1.0
            else:
                t = (normalized_dist - self.island_size) / (1.0 - self.island_size)
                falloff = 1.0 - (t * t * (3 - 2 * t))
        else:
            falloff = 1.0

        return base_height * falloff


class CaveGenerator:
    """Generator for cave/dungeon-like terrain.

    Uses cellular automata to create organic cave shapes.
    """

    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = random.Random(seed)

        # Cellular automata parameters
        self.initial_fill = 0.45  # Initial random fill percentage
        self.birth_limit = 4     # Neighbors needed to birth a wall
        self.death_limit = 3     # Neighbors needed to keep a wall alive
        self.iterations = 5      # Number of smoothing iterations

    def generate(self, width: int, height: int) -> List[List[int]]:
        """Generate a cave map.

        Args:
            width: Map width
            height: Map height

        Returns:
            2D array where 1 = wall, 0 = floor
        """
        # Initialize with random noise
        grid = [
            [1 if self.rng.random() < self.initial_fill else 0
             for _ in range(width)]
            for _ in range(height)
        ]

        # Ensure borders are walls
        for x in range(width):
            grid[0][x] = 1
            grid[height - 1][x] = 1
        for y in range(height):
            grid[y][0] = 1
            grid[y][width - 1] = 1

        # Apply cellular automata
        for _ in range(self.iterations):
            grid = self._iterate(grid, width, height)

        return grid

    def _iterate(self, grid: List[List[int]], width: int,
                 height: int) -> List[List[int]]:
        """Perform one iteration of cellular automata."""
        new_grid = [[0 for _ in range(width)] for _ in range(height)]

        for y in range(height):
            for x in range(width):
                neighbors = self._count_neighbors(grid, x, y, width, height)

                if grid[y][x] == 1:
                    # Wall cell
                    new_grid[y][x] = 1 if neighbors >= self.death_limit else 0
                else:
                    # Floor cell
                    new_grid[y][x] = 1 if neighbors > self.birth_limit else 0

        return new_grid

    def _count_neighbors(self, grid: List[List[int]], x: int, y: int,
                         width: int, height: int) -> int:
        """Count wall neighbors (including diagonals)."""
        count = 0
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < width and 0 <= ny < height:
                    count += grid[ny][nx]
                else:
                    count += 1  # Out of bounds counts as wall
        return count

    def generate_tilemap(self, width: int, height: int,
                         tile_size: int = 16) -> TileMap:
        """Generate a TileMap from cave data."""
        cave_data = self.generate(width, height)
        tilemap = TileMap(width, height, tile_size)

        # Register floor and wall tiles
        floor_config = TileConfig(
            size=tile_size,
            base_color=(60, 50, 40, 255),
            highlight_color=(80, 70, 60, 255),
            shadow_color=(40, 30, 25, 255),
            edge_color=(30, 25, 20, 255),
        )
        floor_autotile = AutoTile16(floor_config, self.seed)
        floor_autotile.generate_all()

        wall_config = TileConfig(
            size=tile_size,
            base_color=(80, 75, 70, 255),
            highlight_color=(100, 95, 90, 255),
            shadow_color=(50, 45, 40, 255),
            edge_color=(40, 35, 30, 255),
        )
        wall_autotile = AutoTile47(wall_config, self.seed + 1)
        wall_autotile.generate_all()

        tilemap.register_tile(TileDefinition(
            id=1, name="floor", autotile=floor_autotile, walkable=True
        ))
        tilemap.register_tile(TileDefinition(
            id=2, name="wall", autotile=wall_autotile, walkable=False
        ))

        # Fill tilemap
        for y in range(height):
            for x in range(width):
                tile_id = 2 if cave_data[y][x] == 1 else 1
                tilemap.set_tile(x, y, tile_id)

        return tilemap

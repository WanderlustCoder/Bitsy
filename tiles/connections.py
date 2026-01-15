"""
Connections - Edge matching and tile connection rules.

Provides systems for:
- Wang tile edge matching
- Tile connection rules between different tile types
- TileMap for managing and rendering tile grids
"""

import random
from typing import Dict, List, Tuple, Optional, Set, Any
from dataclasses import dataclass, field
from enum import IntEnum

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Canvas
from .autotile import (
    AutoTile, AutoTile16, AutoTile47,
    TileConfig,
    DIR_N, DIR_NE, DIR_E, DIR_SE, DIR_S, DIR_SW, DIR_W, DIR_NW,
    NORTH, EAST, SOUTH, WEST,
)


class EdgeType(IntEnum):
    """Edge types for Wang tile matching."""
    EMPTY = 0
    SOLID = 1
    # Extendable for more edge varieties
    GRASS = 2
    WATER = 3
    STONE = 4
    SAND = 5


@dataclass
class TileDefinition:
    """Definition of a tile type for the tilemap.

    Attributes:
        id: Unique tile type identifier
        name: Human-readable name
        autotile: Optional autotile system for this tile type
        connects_to: Set of tile IDs this tile connects to
        layer: Rendering layer (higher = on top)
        walkable: Whether entities can traverse this tile
        properties: Custom properties dictionary
    """

    id: int
    name: str
    autotile: Optional[AutoTile] = None
    connects_to: Set[int] = field(default_factory=set)
    layer: int = 0
    walkable: bool = True
    properties: Dict[str, Any] = field(default_factory=dict)

    def connects_with(self, other_id: int) -> bool:
        """Check if this tile connects with another tile type."""
        # Self always connects
        if other_id == self.id:
            return True
        # Check explicit connections
        return other_id in self.connects_to


@dataclass
class EdgeRules:
    """Edge matching rules for Wang tiles.

    Defines what edge types can connect to each other.
    """

    # Map of (edge_type_a, edge_type_b) -> can_connect
    _connections: Dict[Tuple[EdgeType, EdgeType], bool] = field(default_factory=dict)

    def __post_init__(self):
        # Default: same edges connect
        for edge in EdgeType:
            self._connections[(edge, edge)] = True

    def set_connection(self, edge_a: EdgeType, edge_b: EdgeType,
                       can_connect: bool, bidirectional: bool = True) -> None:
        """Set whether two edge types can connect.

        Args:
            edge_a: First edge type
            edge_b: Second edge type
            can_connect: Whether they can connect
            bidirectional: Apply rule in both directions
        """
        self._connections[(edge_a, edge_b)] = can_connect
        if bidirectional:
            self._connections[(edge_b, edge_a)] = can_connect

    def can_connect(self, edge_a: EdgeType, edge_b: EdgeType) -> bool:
        """Check if two edges can connect."""
        return self._connections.get((edge_a, edge_b), False)


class TileMap:
    """A grid-based tilemap with autotile support.

    Manages a 2D grid of tiles and handles:
    - Tile placement and removal
    - Automatic neighbor-based tile selection
    - Multi-layer rendering
    - Tile queries
    """

    def __init__(self, width: int, height: int, tile_size: int = 16):
        """Initialize tilemap.

        Args:
            width: Grid width in tiles
            height: Grid height in tiles
            tile_size: Size of each tile in pixels
        """
        self.width = width
        self.height = height
        self.tile_size = tile_size

        # Grid stores tile type IDs (0 = empty)
        self._grid: List[List[int]] = [
            [0 for _ in range(width)] for _ in range(height)
        ]

        # Tile definitions
        self._tile_defs: Dict[int, TileDefinition] = {
            0: TileDefinition(0, "empty", walkable=True)
        }

        # Cached tile renders
        self._cache: Dict[Tuple[int, int], Canvas] = {}
        self._cache_valid = False

    def register_tile(self, tile_def: TileDefinition) -> None:
        """Register a tile type definition.

        Args:
            tile_def: Tile definition to register
        """
        self._tile_defs[tile_def.id] = tile_def
        self._cache_valid = False

    def get_tile_def(self, tile_id: int) -> Optional[TileDefinition]:
        """Get tile definition by ID."""
        return self._tile_defs.get(tile_id)

    def set_tile(self, x: int, y: int, tile_id: int) -> None:
        """Set a tile at position.

        Args:
            x: X coordinate
            y: Y coordinate
            tile_id: Tile type ID
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            self._grid[y][x] = tile_id
            self._cache_valid = False

    def get_tile(self, x: int, y: int) -> int:
        """Get tile ID at position.

        Returns 0 (empty) for out-of-bounds.
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            return self._grid[y][x]
        return 0

    def fill_rect(self, x: int, y: int, w: int, h: int, tile_id: int) -> None:
        """Fill a rectangular area with a tile type."""
        for dy in range(h):
            for dx in range(w):
                self.set_tile(x + dx, y + dy, tile_id)

    def fill_circle(self, cx: int, cy: int, radius: int, tile_id: int) -> None:
        """Fill a circular area with a tile type."""
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                if dx * dx + dy * dy <= radius * radius:
                    self.set_tile(cx + dx, cy + dy, tile_id)

    def clear(self, tile_id: int = 0) -> None:
        """Clear the entire map to a single tile type."""
        for y in range(self.height):
            for x in range(self.width):
                self._grid[y][x] = tile_id
        self._cache_valid = False

    def get_neighbors_4(self, x: int, y: int, tile_id: int) -> int:
        """Get 4-direction neighbor bitmask for autotiling.

        Checks which neighbors match or connect with the given tile_id.
        """
        tile_def = self._tile_defs.get(tile_id)
        mask = 0

        # North
        if self._tiles_connect(tile_id, self.get_tile(x, y - 1)):
            mask |= NORTH
        # East
        if self._tiles_connect(tile_id, self.get_tile(x + 1, y)):
            mask |= EAST
        # South
        if self._tiles_connect(tile_id, self.get_tile(x, y + 1)):
            mask |= SOUTH
        # West
        if self._tiles_connect(tile_id, self.get_tile(x - 1, y)):
            mask |= WEST

        return mask

    def get_neighbors_8(self, x: int, y: int, tile_id: int) -> int:
        """Get 8-direction neighbor bitmask for autotiling."""
        mask = 0

        # Cardinals
        if self._tiles_connect(tile_id, self.get_tile(x, y - 1)):
            mask |= DIR_N
        if self._tiles_connect(tile_id, self.get_tile(x + 1, y)):
            mask |= DIR_E
        if self._tiles_connect(tile_id, self.get_tile(x, y + 1)):
            mask |= DIR_S
        if self._tiles_connect(tile_id, self.get_tile(x - 1, y)):
            mask |= DIR_W

        # Diagonals (only if adjacent cardinals connect)
        if self._tiles_connect(tile_id, self.get_tile(x + 1, y - 1)):
            mask |= DIR_NE
        if self._tiles_connect(tile_id, self.get_tile(x + 1, y + 1)):
            mask |= DIR_SE
        if self._tiles_connect(tile_id, self.get_tile(x - 1, y + 1)):
            mask |= DIR_SW
        if self._tiles_connect(tile_id, self.get_tile(x - 1, y - 1)):
            mask |= DIR_NW

        return mask

    def _tiles_connect(self, tile_a: int, tile_b: int) -> bool:
        """Check if two tile types connect."""
        if tile_a == tile_b:
            return True
        tile_def = self._tile_defs.get(tile_a)
        if tile_def:
            return tile_def.connects_with(tile_b)
        return False

    def render(self) -> Canvas:
        """Render the entire tilemap to a canvas.

        Returns:
            Canvas with rendered tilemap
        """
        canvas = Canvas(
            self.width * self.tile_size,
            self.height * self.tile_size,
            (0, 0, 0, 0)
        )

        # Sort tile definitions by layer
        sorted_defs = sorted(self._tile_defs.values(), key=lambda d: d.layer)

        # Render each layer
        for tile_def in sorted_defs:
            if tile_def.id == 0:  # Skip empty
                continue

            for y in range(self.height):
                for x in range(self.width):
                    if self._grid[y][x] == tile_def.id:
                        tile_canvas = self._get_tile_render(x, y, tile_def)
                        if tile_canvas:
                            canvas.blit(
                                tile_canvas,
                                x * self.tile_size,
                                y * self.tile_size
                            )

        return canvas

    def _get_tile_render(self, x: int, y: int,
                         tile_def: TileDefinition) -> Optional[Canvas]:
        """Get the rendered tile for a position."""
        if tile_def.autotile:
            # Use autotile system
            if isinstance(tile_def.autotile, AutoTile47):
                mask = self.get_neighbors_8(x, y, tile_def.id)
            else:
                mask = self.get_neighbors_4(x, y, tile_def.id)
            return tile_def.autotile.get_tile(mask)
        else:
            # No autotile - return a solid color tile
            return self._create_solid_tile(tile_def)

    def _create_solid_tile(self, tile_def: TileDefinition) -> Canvas:
        """Create a simple solid color tile."""
        color = tile_def.properties.get('color', (100, 100, 100, 255))
        canvas = Canvas(self.tile_size, self.tile_size, color)
        return canvas

    def is_walkable(self, x: int, y: int) -> bool:
        """Check if a tile position is walkable."""
        tile_id = self.get_tile(x, y)
        tile_def = self._tile_defs.get(tile_id)
        if tile_def:
            return tile_def.walkable
        return True

    def get_walkable_mask(self) -> List[List[bool]]:
        """Get a 2D array of walkable states."""
        return [
            [self.is_walkable(x, y) for x in range(self.width)]
            for y in range(self.height)
        ]


class WangTileSet:
    """Wang tile set for seamless tiling.

    Wang tiles use edge colors to ensure seamless connections.
    Each tile has edges (N, E, S, W) with specific colors/types
    that must match adjacent tiles.
    """

    def __init__(self, tile_size: int = 16, edge_types: int = 2):
        """Initialize Wang tileset.

        Args:
            tile_size: Tile size in pixels
            edge_types: Number of edge type variations (usually 2)
        """
        self.tile_size = tile_size
        self.edge_types = edge_types
        self.tiles: Dict[Tuple[int, int, int, int], Canvas] = {}

    def add_tile(self, edges: Tuple[int, int, int, int], canvas: Canvas) -> None:
        """Add a tile with specific edge configuration.

        Args:
            edges: (north, east, south, west) edge types
            canvas: The tile image
        """
        self.tiles[edges] = canvas

    def get_tile(self, edges: Tuple[int, int, int, int]) -> Optional[Canvas]:
        """Get tile for specific edge configuration."""
        return self.tiles.get(edges)

    def generate_complete_set(self, generator: 'WangTileGenerator') -> None:
        """Generate a complete Wang tile set.

        For 2 edge types, this creates 16 tiles (2^4 combinations).
        """
        for n in range(self.edge_types):
            for e in range(self.edge_types):
                for s in range(self.edge_types):
                    for w in range(self.edge_types):
                        edges = (n, e, s, w)
                        self.tiles[edges] = generator.generate(edges)

    def find_matching_tiles(self, constraints: Dict[str, int]) -> List[Tuple[int, int, int, int]]:
        """Find all tiles matching edge constraints.

        Args:
            constraints: Dict with 'north', 'east', 'south', 'west' keys
                        (missing keys = any value allowed)

        Returns:
            List of matching edge configurations
        """
        matches = []
        for edges in self.tiles.keys():
            n, e, s, w = edges
            if 'north' in constraints and constraints['north'] != n:
                continue
            if 'east' in constraints and constraints['east'] != e:
                continue
            if 'south' in constraints and constraints['south'] != s:
                continue
            if 'west' in constraints and constraints['west'] != w:
                continue
            matches.append(edges)
        return matches


class WangTileGenerator:
    """Generates Wang tiles procedurally."""

    def __init__(self, tile_size: int = 16, seed: int = 42):
        self.tile_size = tile_size
        self.seed = seed
        self.rng = random.Random(seed)

        # Edge colors
        self.edge_colors = [
            (80, 140, 80, 255),   # Type 0 - e.g., grass
            (140, 120, 80, 255), # Type 1 - e.g., dirt
        ]

    def set_edge_colors(self, colors: List[Tuple[int, int, int, int]]) -> None:
        """Set colors for edge types."""
        self.edge_colors = colors

    def generate(self, edges: Tuple[int, int, int, int]) -> Canvas:
        """Generate a Wang tile for the given edge configuration."""
        n, e, s, w = edges
        size = self.tile_size
        canvas = Canvas(size, size, (0, 0, 0, 0))

        # Determine corner colors based on adjacent edges
        nw_color = self._blend_colors(self.edge_colors[n], self.edge_colors[w])
        ne_color = self._blend_colors(self.edge_colors[n], self.edge_colors[e])
        sw_color = self._blend_colors(self.edge_colors[s], self.edge_colors[w])
        se_color = self._blend_colors(self.edge_colors[s], self.edge_colors[e])

        # Fill with bilinear interpolation
        for y in range(size):
            for x in range(size):
                tx = x / (size - 1) if size > 1 else 0.5
                ty = y / (size - 1) if size > 1 else 0.5

                # Bilinear interpolation
                top = self._lerp_color(nw_color, ne_color, tx)
                bottom = self._lerp_color(sw_color, se_color, tx)
                color = self._lerp_color(top, bottom, ty)

                canvas.set_pixel(x, y, color)

        return canvas

    def _blend_colors(self, c1: Tuple[int, int, int, int],
                      c2: Tuple[int, int, int, int]) -> Tuple[int, int, int, int]:
        """Blend two colors equally."""
        return self._lerp_color(c1, c2, 0.5)

    def _lerp_color(self, c1: Tuple[int, int, int, int],
                    c2: Tuple[int, int, int, int],
                    t: float) -> Tuple[int, int, int, int]:
        """Linear interpolate between two colors."""
        return (
            int(c1[0] + (c2[0] - c1[0]) * t),
            int(c1[1] + (c2[1] - c1[1]) * t),
            int(c1[2] + (c2[2] - c1[2]) * t),
            int(c1[3] + (c2[3] - c1[3]) * t),
        )


class WangTileMap:
    """A tilemap using Wang tiles for seamless rendering."""

    def __init__(self, width: int, height: int, tileset: WangTileSet):
        """Initialize Wang tilemap.

        Args:
            width: Grid width in tiles
            height: Grid height in tiles
            tileset: Wang tileset to use
        """
        self.width = width
        self.height = height
        self.tileset = tileset

        # Store edge types at each position
        # Each cell stores which edge type it "wants" on each side
        self._grid: List[List[Optional[Tuple[int, int, int, int]]]] = [
            [None for _ in range(width)] for _ in range(height)
        ]

    def set_tile(self, x: int, y: int, edges: Tuple[int, int, int, int]) -> None:
        """Set tile edges at position."""
        if 0 <= x < self.width and 0 <= y < self.height:
            self._grid[y][x] = edges

    def get_tile(self, x: int, y: int) -> Optional[Tuple[int, int, int, int]]:
        """Get tile edges at position."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self._grid[y][x]
        return None

    def auto_fill(self, rng: Optional[random.Random] = None) -> None:
        """Automatically fill the grid with valid Wang tiles.

        Uses constraint propagation to ensure all edges match.
        """
        if rng is None:
            rng = random.Random(42)

        # Simple greedy fill - for each cell, find a tile that matches neighbors
        for y in range(self.height):
            for x in range(self.width):
                constraints = {}

                # Check north neighbor's south edge
                if y > 0 and self._grid[y-1][x]:
                    constraints['north'] = self._grid[y-1][x][2]  # South edge of north neighbor

                # Check west neighbor's east edge
                if x > 0 and self._grid[y][x-1]:
                    constraints['west'] = self._grid[y][x-1][1]  # East edge of west neighbor

                # Find matching tiles
                matches = self.tileset.find_matching_tiles(constraints)
                if matches:
                    self._grid[y][x] = rng.choice(matches)

    def render(self) -> Canvas:
        """Render the tilemap."""
        tile_size = self.tileset.tile_size
        canvas = Canvas(self.width * tile_size, self.height * tile_size, (0, 0, 0, 0))

        for y in range(self.height):
            for x in range(self.width):
                edges = self._grid[y][x]
                if edges:
                    tile = self.tileset.get_tile(edges)
                    if tile:
                        canvas.blit(tile, x * tile_size, y * tile_size)

        return canvas

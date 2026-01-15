"""
AutoTile - Automatic tile selection based on neighbors.

Provides two main autotile systems:
- Simple 16-tile: Basic cardinal direction matching
- Blob 47-tile: Full 8-direction matching for smooth terrain

Bitmask conventions:
- Simple 16-tile uses 4 bits (N, E, S, W)
- Blob 47-tile uses 8 bits (N, NE, E, SE, S, SW, W, NW)
"""

import random
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Canvas


# =============================================================================
# Bitmask Constants
# =============================================================================

# Simple 4-direction bitmask (16 combinations)
NORTH = 1
EAST = 2
SOUTH = 4
WEST = 8

# 8-direction bitmask for blob autotile (47 unique visual combinations)
DIR_N = 1
DIR_NE = 2
DIR_E = 4
DIR_SE = 8
DIR_S = 16
DIR_SW = 32
DIR_W = 64
DIR_NW = 128


@dataclass
class TileConfig:
    """Configuration for tile generation.

    Attributes:
        size: Tile size in pixels (square)
        base_color: Primary fill color
        highlight_color: Lighter shade for highlights
        shadow_color: Darker shade for shadows
        edge_color: Color for tile edges/outlines
        style: Rendering style ('flat', 'shaded', 'outline')
    """

    size: int = 16
    base_color: Tuple[int, int, int, int] = (100, 180, 100, 255)
    highlight_color: Tuple[int, int, int, int] = (130, 210, 130, 255)
    shadow_color: Tuple[int, int, int, int] = (70, 130, 70, 255)
    edge_color: Tuple[int, int, int, int] = (50, 100, 50, 255)
    style: str = 'shaded'


class AutoTile:
    """Base class for autotile systems.

    Generates tiles that automatically connect based on neighboring tiles.
    """

    def __init__(self, config: Optional[TileConfig] = None, seed: int = 42):
        """Initialize autotile.

        Args:
            config: Tile configuration
            seed: Random seed for deterministic generation
        """
        self.config = config or TileConfig()
        self.seed = seed
        self.rng = random.Random(seed)
        self.tiles: Dict[int, Canvas] = {}

    def get_tile(self, bitmask: int) -> Canvas:
        """Get tile for given neighbor bitmask.

        Args:
            bitmask: Neighbor bitmask value

        Returns:
            Canvas with the appropriate tile
        """
        if bitmask not in self.tiles:
            self.tiles[bitmask] = self._generate_tile(bitmask)
        return self.tiles[bitmask]

    def _generate_tile(self, bitmask: int) -> Canvas:
        """Generate a tile for the given bitmask.

        Override in subclasses for specific autotile logic.
        """
        canvas = Canvas(self.config.size, self.config.size, self.config.base_color)
        return canvas

    def generate_all(self) -> None:
        """Pre-generate all tile variants."""
        raise NotImplementedError("Subclasses must implement generate_all")

    def export_tileset(self, columns: int = 0) -> Canvas:
        """Export all tiles as a tileset image.

        Args:
            columns: Number of columns (0 = auto)

        Returns:
            Canvas containing all tiles
        """
        if not self.tiles:
            self.generate_all()

        tile_count = len(self.tiles)
        if columns <= 0:
            columns = 8  # Default to 8 columns

        rows = (tile_count + columns - 1) // columns
        size = self.config.size

        tileset = Canvas(columns * size, rows * size)

        for i, (bitmask, tile) in enumerate(sorted(self.tiles.items())):
            col = i % columns
            row = i // columns
            tileset.blit(tile, col * size, row * size)

        return tileset


class AutoTile16(AutoTile):
    """Simple 16-tile autotile system.

    Uses 4-direction neighbor matching (N, E, S, W).
    Produces 16 unique tile combinations.

    Bitmask layout:
        N = 1, E = 2, S = 4, W = 8
    """

    def generate_all(self) -> None:
        """Generate all 16 tile variants."""
        for bitmask in range(16):
            self.tiles[bitmask] = self._generate_tile(bitmask)

    def _generate_tile(self, bitmask: int) -> Canvas:
        """Generate a tile based on 4-direction neighbors."""
        size = self.config.size
        canvas = Canvas(size, size, (0, 0, 0, 0))

        has_north = bool(bitmask & NORTH)
        has_east = bool(bitmask & EAST)
        has_south = bool(bitmask & SOUTH)
        has_west = bool(bitmask & WEST)

        # Fill base
        self._fill_base(canvas, has_north, has_east, has_south, has_west)

        # Add edges
        if self.config.style in ('shaded', 'outline'):
            self._draw_edges(canvas, has_north, has_east, has_south, has_west)

        # Add shading
        if self.config.style == 'shaded':
            self._add_shading(canvas, has_north, has_east, has_south, has_west)

        return canvas

    def _fill_base(self, canvas: Canvas, n: bool, e: bool, s: bool, w: bool) -> None:
        """Fill the base tile shape."""
        size = self.config.size
        corner_size = size // 4

        for y in range(size):
            for x in range(size):
                # Determine if this pixel should be filled
                fill = True

                # Check corners (only filled if both adjacent sides connect)
                in_nw = x < corner_size and y < corner_size
                in_ne = x >= size - corner_size and y < corner_size
                in_sw = x < corner_size and y >= size - corner_size
                in_se = x >= size - corner_size and y >= size - corner_size

                if in_nw and not (n and w):
                    fill = False
                elif in_ne and not (n and e):
                    fill = False
                elif in_sw and not (s and w):
                    fill = False
                elif in_se and not (s and e):
                    fill = False

                if fill:
                    canvas.set_pixel(x, y, self.config.base_color)

    def _draw_edges(self, canvas: Canvas, n: bool, e: bool, s: bool, w: bool) -> None:
        """Draw edge outlines where there's no neighbor."""
        size = self.config.size
        edge = self.config.edge_color

        # Top edge
        if not n:
            for x in range(size):
                if canvas.pixels[0][x][3] > 0:
                    canvas.set_pixel(x, 0, edge)

        # Bottom edge
        if not s:
            for x in range(size):
                if canvas.pixels[size-1][x][3] > 0:
                    canvas.set_pixel(x, size - 1, edge)

        # Left edge
        if not w:
            for y in range(size):
                if canvas.pixels[y][0][3] > 0:
                    canvas.set_pixel(0, y, edge)

        # Right edge
        if not e:
            for y in range(size):
                if canvas.pixels[y][size-1][3] > 0:
                    canvas.set_pixel(size - 1, y, edge)

    def _add_shading(self, canvas: Canvas, n: bool, e: bool, s: bool, w: bool) -> None:
        """Add highlights and shadows."""
        size = self.config.size

        # Top highlight (if no north neighbor)
        if not n:
            for x in range(1, size - 1):
                if canvas.pixels[1][x][3] > 0:
                    canvas.set_pixel(x, 1, self.config.highlight_color)

        # Left highlight (if no west neighbor)
        if not w:
            for y in range(1, size - 1):
                if canvas.pixels[y][1][3] > 0:
                    canvas.set_pixel(1, y, self.config.highlight_color)

        # Bottom shadow (if no south neighbor)
        if not s:
            for x in range(1, size - 1):
                if canvas.pixels[size-2][x][3] > 0:
                    canvas.set_pixel(x, size - 2, self.config.shadow_color)

        # Right shadow (if no east neighbor)
        if not e:
            for y in range(1, size - 1):
                if canvas.pixels[y][size-2][3] > 0:
                    canvas.set_pixel(size - 2, y, self.config.shadow_color)


class AutoTile47(AutoTile):
    """47-tile blob autotile system.

    Uses 8-direction neighbor matching for smooth terrain.
    Although 8 bits give 256 combinations, only 47 are visually unique.

    This is the standard "blob" tileset used in many games like RPG Maker.

    Bitmask layout (clockwise from north):
        N=1, NE=2, E=4, SE=8, S=16, SW=32, W=64, NW=128
    """

    # The 47 unique blob tile indices
    # Maps from simplified visual state to full bitmask
    BLOB_47_INDICES = None  # Computed on first use

    def __init__(self, config: Optional[TileConfig] = None, seed: int = 42):
        super().__init__(config, seed)
        self._compute_blob_indices()

    def _compute_blob_indices(self) -> None:
        """Compute the 47 unique blob tile configurations."""
        if AutoTile47.BLOB_47_INDICES is not None:
            return

        # For blob autotile, diagonal neighbors only matter if both
        # adjacent cardinal neighbors are present
        unique_masks = set()

        for mask in range(256):
            # Normalize the mask - diagonals only count if cardinals present
            normalized = self._normalize_bitmask(mask)
            unique_masks.add(normalized)

        AutoTile47.BLOB_47_INDICES = sorted(unique_masks)

    def _normalize_bitmask(self, mask: int) -> int:
        """Normalize a bitmask by removing invalid diagonal connections.

        A diagonal only counts if both adjacent cardinals are present.
        """
        result = mask & (DIR_N | DIR_E | DIR_S | DIR_W)  # Keep cardinals

        # NE only if N and E
        if (mask & DIR_NE) and (mask & DIR_N) and (mask & DIR_E):
            result |= DIR_NE

        # SE only if S and E
        if (mask & DIR_SE) and (mask & DIR_S) and (mask & DIR_E):
            result |= DIR_SE

        # SW only if S and W
        if (mask & DIR_SW) and (mask & DIR_S) and (mask & DIR_W):
            result |= DIR_SW

        # NW only if N and W
        if (mask & DIR_NW) and (mask & DIR_N) and (mask & DIR_W):
            result |= DIR_NW

        return result

    def generate_all(self) -> None:
        """Generate all 47 unique tile variants."""
        self._compute_blob_indices()
        for bitmask in AutoTile47.BLOB_47_INDICES:
            self.tiles[bitmask] = self._generate_tile(bitmask)

    def get_tile(self, bitmask: int) -> Canvas:
        """Get tile for given neighbor bitmask (auto-normalizes)."""
        normalized = self._normalize_bitmask(bitmask)
        if normalized not in self.tiles:
            self.tiles[normalized] = self._generate_tile(normalized)
        return self.tiles[normalized]

    def _generate_tile(self, bitmask: int) -> Canvas:
        """Generate a tile based on 8-direction neighbors."""
        size = self.config.size
        canvas = Canvas(size, size, (0, 0, 0, 0))

        # Parse directions
        has_n = bool(bitmask & DIR_N)
        has_ne = bool(bitmask & DIR_NE)
        has_e = bool(bitmask & DIR_E)
        has_se = bool(bitmask & DIR_SE)
        has_s = bool(bitmask & DIR_S)
        has_sw = bool(bitmask & DIR_SW)
        has_w = bool(bitmask & DIR_W)
        has_nw = bool(bitmask & DIR_NW)

        # Generate using quarter-tile approach
        self._draw_quarter(canvas, 0, 0, has_nw, has_n, has_w)  # NW quarter
        self._draw_quarter(canvas, 1, 0, has_ne, has_n, has_e)  # NE quarter
        self._draw_quarter(canvas, 0, 1, has_sw, has_s, has_w)  # SW quarter
        self._draw_quarter(canvas, 1, 1, has_se, has_s, has_e)  # SE quarter

        # Add edge details
        if self.config.style in ('shaded', 'outline'):
            self._add_edge_details(canvas, bitmask)

        return canvas

    def _draw_quarter(self, canvas: Canvas, qx: int, qy: int,
                      has_diag: bool, has_vert: bool, has_horiz: bool) -> None:
        """Draw one quarter of the tile.

        Args:
            canvas: Target canvas
            qx: Quarter x (0 or 1)
            qy: Quarter y (0 or 1)
            has_diag: Has diagonal neighbor
            has_vert: Has vertical neighbor (N for top, S for bottom)
            has_horiz: Has horizontal neighbor (W for left, E for right)
        """
        size = self.config.size
        half = size // 2
        quarter = size // 4

        x_start = qx * half
        y_start = qy * half
        x_end = x_start + half
        y_end = y_start + half

        base = self.config.base_color

        for y in range(y_start, y_end):
            for x in range(x_start, x_end):
                # Local coordinates within quarter
                lx = x - x_start
                ly = y - y_start

                fill = False

                # Inner area always filled
                inner_margin = quarter // 2 if quarter > 1 else 1
                is_inner = (inner_margin <= lx < half - inner_margin and
                           inner_margin <= ly < half - inner_margin)

                if is_inner:
                    fill = True
                else:
                    # Edge areas - check neighbors
                    at_outer_edge_x = (lx < inner_margin) if qx == 0 else (lx >= half - inner_margin)
                    at_outer_edge_y = (ly < inner_margin) if qy == 0 else (ly >= half - inner_margin)

                    if at_outer_edge_x and at_outer_edge_y:
                        # Corner pixel - need diagonal
                        fill = has_diag
                    elif at_outer_edge_x:
                        # Horizontal edge
                        fill = has_horiz
                    elif at_outer_edge_y:
                        # Vertical edge
                        fill = has_vert
                    else:
                        fill = True

                if fill:
                    canvas.set_pixel(x, y, base)

    def _add_edge_details(self, canvas: Canvas, bitmask: int) -> None:
        """Add edge highlights, shadows, and outlines."""
        size = self.config.size

        has_n = bool(bitmask & DIR_N)
        has_e = bool(bitmask & DIR_E)
        has_s = bool(bitmask & DIR_S)
        has_w = bool(bitmask & DIR_W)

        edge = self.config.edge_color
        highlight = self.config.highlight_color
        shadow = self.config.shadow_color

        # Scan for edges and apply effects
        for y in range(size):
            for x in range(size):
                if canvas.pixels[y][x][3] == 0:
                    continue

                # Check if on edge
                on_top = y == 0 or canvas.pixels[y-1][x][3] == 0
                on_bottom = y == size - 1 or canvas.pixels[y+1][x][3] == 0
                on_left = x == 0 or canvas.pixels[y][x-1][3] == 0
                on_right = x == size - 1 or canvas.pixels[y][x+1][3] == 0

                # Apply outline
                if self.config.style == 'outline':
                    if on_top or on_bottom or on_left or on_right:
                        canvas.set_pixel(x, y, edge)
                elif self.config.style == 'shaded':
                    # Subtle edge darkening
                    if on_top or on_left:
                        if on_top and not has_n:
                            canvas.set_pixel(x, y, highlight)
                        elif on_left and not has_w:
                            canvas.set_pixel(x, y, highlight)
                    if on_bottom or on_right:
                        if on_bottom and not has_s:
                            canvas.set_pixel(x, y, shadow)
                        elif on_right and not has_e:
                            canvas.set_pixel(x, y, shadow)


class AutoTileRPG(AutoTile):
    """RPG Maker-style autotile with 48 tiles (A2 format).

    Uses a 2x3 mini-tile system where each tile is composed of
    four 8x8 (for 16px tiles) or similar quarter-pieces.
    """

    def __init__(self, config: Optional[TileConfig] = None, seed: int = 42):
        super().__init__(config, seed)
        self._mini_tiles: Dict[int, Canvas] = {}

    def generate_all(self) -> None:
        """Generate all tiles using mini-tile composition."""
        # First generate the 6 mini-tiles
        self._generate_mini_tiles()

        # Then compose all 47 combinations
        for bitmask in range(256):
            normalized = self._normalize_bitmask(bitmask)
            if normalized not in self.tiles:
                self.tiles[normalized] = self._compose_tile(normalized)

    def _normalize_bitmask(self, mask: int) -> int:
        """Same normalization as AutoTile47."""
        result = mask & (DIR_N | DIR_E | DIR_S | DIR_W)

        if (mask & DIR_NE) and (mask & DIR_N) and (mask & DIR_E):
            result |= DIR_NE
        if (mask & DIR_SE) and (mask & DIR_S) and (mask & DIR_E):
            result |= DIR_SE
        if (mask & DIR_SW) and (mask & DIR_S) and (mask & DIR_W):
            result |= DIR_SW
        if (mask & DIR_NW) and (mask & DIR_N) and (mask & DIR_W):
            result |= DIR_NW

        return result

    def _generate_mini_tiles(self) -> None:
        """Generate the 6 base mini-tiles for composition."""
        size = self.config.size
        mini_size = size // 2

        # Mini-tile types:
        # 0: Full (center of large area)
        # 1: Top edge
        # 2: Bottom edge
        # 3: Left edge
        # 4: Right edge
        # 5: Outer corner
        # 6: Inner corner

        for mt_type in range(7):
            mini = Canvas(mini_size, mini_size, (0, 0, 0, 0))
            self._draw_mini_tile(mini, mt_type)
            self._mini_tiles[mt_type] = mini

    def _draw_mini_tile(self, canvas: Canvas, tile_type: int) -> None:
        """Draw a specific mini-tile type."""
        size = canvas.width
        base = self.config.base_color
        edge = self.config.edge_color

        if tile_type == 0:  # Full
            for y in range(size):
                for x in range(size):
                    canvas.set_pixel(x, y, base)

        elif tile_type == 1:  # Top edge
            for y in range(size):
                for x in range(size):
                    if y > 0:
                        canvas.set_pixel(x, y, base)
                    else:
                        canvas.set_pixel(x, y, edge)

        elif tile_type == 2:  # Bottom edge
            for y in range(size):
                for x in range(size):
                    if y < size - 1:
                        canvas.set_pixel(x, y, base)
                    else:
                        canvas.set_pixel(x, y, edge)

        elif tile_type == 3:  # Left edge
            for y in range(size):
                for x in range(size):
                    if x > 0:
                        canvas.set_pixel(x, y, base)
                    else:
                        canvas.set_pixel(x, y, edge)

        elif tile_type == 4:  # Right edge
            for y in range(size):
                for x in range(size):
                    if x < size - 1:
                        canvas.set_pixel(x, y, base)
                    else:
                        canvas.set_pixel(x, y, edge)

        elif tile_type == 5:  # Outer corner (empty)
            pass  # Leave transparent

        elif tile_type == 6:  # Inner corner
            for y in range(size):
                for x in range(size):
                    canvas.set_pixel(x, y, base)
            # Add corner detail
            canvas.set_pixel(0, 0, edge)

    def _compose_tile(self, bitmask: int) -> Canvas:
        """Compose a full tile from mini-tiles based on bitmask."""
        size = self.config.size
        mini_size = size // 2
        canvas = Canvas(size, size, (0, 0, 0, 0))

        # Determine mini-tile for each quarter
        nw_mini = self._get_mini_tile_type(bitmask, 'nw')
        ne_mini = self._get_mini_tile_type(bitmask, 'ne')
        sw_mini = self._get_mini_tile_type(bitmask, 'sw')
        se_mini = self._get_mini_tile_type(bitmask, 'se')

        # Blit mini-tiles
        if nw_mini in self._mini_tiles:
            canvas.blit(self._mini_tiles[nw_mini], 0, 0)
        if ne_mini in self._mini_tiles:
            canvas.blit(self._mini_tiles[ne_mini], mini_size, 0)
        if sw_mini in self._mini_tiles:
            canvas.blit(self._mini_tiles[sw_mini], 0, mini_size)
        if se_mini in self._mini_tiles:
            canvas.blit(self._mini_tiles[se_mini], mini_size, mini_size)

        return canvas

    def _get_mini_tile_type(self, bitmask: int, corner: str) -> int:
        """Determine which mini-tile type to use for a corner."""
        has_n = bool(bitmask & DIR_N)
        has_e = bool(bitmask & DIR_E)
        has_s = bool(bitmask & DIR_S)
        has_w = bool(bitmask & DIR_W)
        has_ne = bool(bitmask & DIR_NE)
        has_se = bool(bitmask & DIR_SE)
        has_sw = bool(bitmask & DIR_SW)
        has_nw = bool(bitmask & DIR_NW)

        if corner == 'nw':
            if has_n and has_w:
                return 0 if has_nw else 6
            elif has_n:
                return 3
            elif has_w:
                return 1
            else:
                return 5
        elif corner == 'ne':
            if has_n and has_e:
                return 0 if has_ne else 6
            elif has_n:
                return 4
            elif has_e:
                return 1
            else:
                return 5
        elif corner == 'sw':
            if has_s and has_w:
                return 0 if has_sw else 6
            elif has_s:
                return 3
            elif has_w:
                return 2
            else:
                return 5
        elif corner == 'se':
            if has_s and has_e:
                return 0 if has_se else 6
            elif has_s:
                return 4
            elif has_e:
                return 2
            else:
                return 5

        return 0


# =============================================================================
# Utility Functions
# =============================================================================

def calculate_bitmask_4(neighbors: Dict[str, bool]) -> int:
    """Calculate 4-direction bitmask from neighbor dictionary.

    Args:
        neighbors: Dict with keys 'north', 'east', 'south', 'west'

    Returns:
        4-bit bitmask
    """
    mask = 0
    if neighbors.get('north', False):
        mask |= NORTH
    if neighbors.get('east', False):
        mask |= EAST
    if neighbors.get('south', False):
        mask |= SOUTH
    if neighbors.get('west', False):
        mask |= WEST
    return mask


def calculate_bitmask_8(neighbors: Dict[str, bool]) -> int:
    """Calculate 8-direction bitmask from neighbor dictionary.

    Args:
        neighbors: Dict with keys 'n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw'

    Returns:
        8-bit bitmask
    """
    mask = 0
    if neighbors.get('n', False):
        mask |= DIR_N
    if neighbors.get('ne', False):
        mask |= DIR_NE
    if neighbors.get('e', False):
        mask |= DIR_E
    if neighbors.get('se', False):
        mask |= DIR_SE
    if neighbors.get('s', False):
        mask |= DIR_S
    if neighbors.get('sw', False):
        mask |= DIR_SW
    if neighbors.get('w', False):
        mask |= DIR_W
    if neighbors.get('nw', False):
        mask |= DIR_NW
    return mask


def bitmask_to_neighbors_4(mask: int) -> Dict[str, bool]:
    """Convert 4-bit bitmask to neighbor dictionary."""
    return {
        'north': bool(mask & NORTH),
        'east': bool(mask & EAST),
        'south': bool(mask & SOUTH),
        'west': bool(mask & WEST),
    }


def bitmask_to_neighbors_8(mask: int) -> Dict[str, bool]:
    """Convert 8-bit bitmask to neighbor dictionary."""
    return {
        'n': bool(mask & DIR_N),
        'ne': bool(mask & DIR_NE),
        'e': bool(mask & DIR_E),
        'se': bool(mask & DIR_SE),
        's': bool(mask & DIR_S),
        'sw': bool(mask & DIR_SW),
        'w': bool(mask & DIR_W),
        'nw': bool(mask & DIR_NW),
    }

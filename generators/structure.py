"""
Structure Generator - Procedural building and dungeon generation.

Generates:
- Houses and buildings (various styles)
- Castles and fortifications
- Dungeon tiles and rooms
- Doors, windows, and architectural details

Example usage:
    from generators.structure import StructureGenerator

    gen = StructureGenerator(seed=42)

    # Generate a house
    house = gen.generate_house(width=48, height=48, style='cottage')

    # Generate castle wall
    wall = gen.generate_castle_wall(width=64, height=32)

    # Generate dungeon tile
    dungeon = gen.generate_dungeon_tile(tile_type='floor', size=16)
"""

import random
import math
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Canvas, Palette
from core.color import darken, lighten


class BuildingStyle(Enum):
    """Building architectural styles."""
    COTTAGE = 'cottage'       # Small cozy house
    MEDIEVAL = 'medieval'     # Medieval town building
    CASTLE = 'castle'         # Castle/fortress
    FANTASY = 'fantasy'       # Fantasy style
    RUSTIC = 'rustic'         # Rural/wooden
    STONE = 'stone'           # Stone construction


class RoofStyle(Enum):
    """Roof styles for buildings."""
    PEAKED = 'peaked'         # Traditional peaked roof
    FLAT = 'flat'             # Flat roof
    DOME = 'dome'             # Domed roof
    SLANTED = 'slanted'       # Single slant
    TOWER = 'tower'           # Conical tower roof


class DungeonTileType(Enum):
    """Types of dungeon tiles."""
    FLOOR = 'floor'
    WALL = 'wall'
    CORNER = 'corner'
    DOOR = 'door'
    STAIRS = 'stairs'
    PIT = 'pit'
    PILLAR = 'pillar'
    TORCH = 'torch'


@dataclass
class StructurePalette:
    """Color palette for structure generation."""
    wall_base: Tuple[int, int, int, int] = (160, 140, 120, 255)
    wall_highlight: Tuple[int, int, int, int] = (180, 160, 140, 255)
    wall_shadow: Tuple[int, int, int, int] = (120, 100, 80, 255)
    roof_base: Tuple[int, int, int, int] = (140, 80, 60, 255)
    roof_highlight: Tuple[int, int, int, int] = (170, 100, 80, 255)
    roof_shadow: Tuple[int, int, int, int] = (100, 60, 40, 255)
    wood_base: Tuple[int, int, int, int] = (120, 80, 50, 255)
    wood_dark: Tuple[int, int, int, int] = (80, 50, 30, 255)
    window_base: Tuple[int, int, int, int] = (100, 150, 200, 255)
    window_frame: Tuple[int, int, int, int] = (60, 40, 30, 255)
    door_base: Tuple[int, int, int, int] = (100, 70, 45, 255)

    @classmethod
    def cottage(cls) -> 'StructurePalette':
        """Warm cottage colors."""
        return cls(
            wall_base=(200, 180, 150, 255),
            wall_highlight=(220, 200, 170, 255),
            wall_shadow=(160, 140, 110, 255),
            roof_base=(140, 100, 70, 255),
            roof_highlight=(170, 120, 90, 255),
            roof_shadow=(100, 70, 50, 255),
        )

    @classmethod
    def stone(cls) -> 'StructurePalette':
        """Gray stone colors."""
        return cls(
            wall_base=(140, 140, 140, 255),
            wall_highlight=(170, 170, 170, 255),
            wall_shadow=(100, 100, 100, 255),
            roof_base=(80, 80, 90, 255),
            roof_highlight=(100, 100, 110, 255),
            roof_shadow=(60, 60, 70, 255),
        )

    @classmethod
    def castle(cls) -> 'StructurePalette':
        """Castle stone colors."""
        return cls(
            wall_base=(150, 145, 140, 255),
            wall_highlight=(180, 175, 170, 255),
            wall_shadow=(110, 105, 100, 255),
            roof_base=(70, 70, 80, 255),
            roof_highlight=(90, 90, 100, 255),
            roof_shadow=(50, 50, 60, 255),
        )

    @classmethod
    def dungeon(cls) -> 'StructurePalette':
        """Dark dungeon colors."""
        return cls(
            wall_base=(80, 75, 70, 255),
            wall_highlight=(100, 95, 90, 255),
            wall_shadow=(50, 45, 40, 255),
            roof_base=(60, 55, 50, 255),
            roof_highlight=(80, 75, 70, 255),
            roof_shadow=(40, 35, 30, 255),
        )


class StructureGenerator:
    """Generator for buildings, castles, and dungeon tiles."""

    def __init__(self, seed: int = 42):
        """Initialize structure generator.

        Args:
            seed: Random seed for deterministic generation
        """
        self.seed = seed
        self.rng = random.Random(seed)

    def _reset_seed(self, offset: int = 0):
        """Reset RNG with offset for variation."""
        self.rng = random.Random(self.seed + offset)

    # ==================== House Generation ====================

    def generate_house(self, width: int = 48, height: int = 48,
                      style: str = 'cottage',
                      roof_style: str = 'peaked',
                      has_chimney: bool = True,
                      num_windows: int = 2) -> Canvas:
        """Generate a house sprite.

        Args:
            width: Canvas width
            height: Canvas height
            style: Building style ('cottage', 'medieval', 'stone')
            roof_style: Roof style ('peaked', 'flat', 'slanted')
            has_chimney: Whether to add a chimney
            num_windows: Number of windows

        Returns:
            Canvas with generated house
        """
        self._reset_seed()

        canvas = Canvas(width, height)

        # Get palette
        if style == 'cottage':
            palette = StructurePalette.cottage()
        elif style == 'stone':
            palette = StructurePalette.stone()
        elif style == 'castle':
            palette = StructurePalette.castle()
        else:
            palette = StructurePalette()

        # Calculate proportions
        roof_height = height // 3
        body_height = height - roof_height - 2
        body_width = int(width * 0.8)
        body_x = (width - body_width) // 2
        body_y = roof_height + 2

        # Draw building body
        self._draw_building_body(canvas, body_x, body_y, body_width, body_height, palette)

        # Draw roof
        if roof_style == 'peaked':
            self._draw_peaked_roof(canvas, body_x - 2, roof_height, body_width + 4, roof_height, palette)
        elif roof_style == 'flat':
            self._draw_flat_roof(canvas, body_x - 2, roof_height, body_width + 4, 4, palette)
        else:
            self._draw_slanted_roof(canvas, body_x - 2, roof_height, body_width + 4, roof_height, palette)

        # Draw door
        door_width = body_width // 4
        door_height = body_height // 2
        door_x = body_x + (body_width - door_width) // 2
        door_y = body_y + body_height - door_height
        self._draw_door(canvas, door_x, door_y, door_width, door_height, palette)

        # Draw windows
        if num_windows > 0:
            window_width = body_width // 5
            window_height = body_height // 3
            window_y = body_y + body_height // 4

            for i in range(num_windows):
                if num_windows == 1:
                    window_x = body_x + body_width // 4
                else:
                    spacing = (body_width - window_width * num_windows) // (num_windows + 1)
                    window_x = body_x + spacing + i * (window_width + spacing)

                # Don't overlap with door
                if not (window_x < door_x + door_width and window_x + window_width > door_x):
                    self._draw_window(canvas, window_x, window_y, window_width, window_height, palette)

        # Draw chimney
        if has_chimney:
            chimney_width = body_width // 6
            chimney_height = roof_height // 2
            chimney_x = body_x + body_width - chimney_width - 4
            chimney_y = 2
            self._draw_chimney(canvas, chimney_x, chimney_y, chimney_width, chimney_height, palette)

        return canvas

    def _draw_building_body(self, canvas: Canvas, x: int, y: int,
                           width: int, height: int, palette: StructurePalette):
        """Draw the main building body."""
        # Main wall
        canvas.fill_rect(x, y, width, height, palette.wall_base)

        # Highlight on left
        for py in range(y, y + height):
            canvas.set_pixel_solid(x, py, palette.wall_highlight)
            canvas.set_pixel_solid(x + 1, py, palette.wall_highlight)

        # Shadow on right
        for py in range(y, y + height):
            canvas.set_pixel_solid(x + width - 1, py, palette.wall_shadow)
            canvas.set_pixel_solid(x + width - 2, py, palette.wall_shadow)

        # Add some texture
        for _ in range(width * height // 30):
            px = x + self.rng.randint(2, width - 3)
            py = y + self.rng.randint(0, height - 1)
            if self.rng.random() > 0.5:
                canvas.set_pixel_solid(px, py, palette.wall_highlight)
            else:
                canvas.set_pixel_solid(px, py, palette.wall_shadow)

    def _draw_peaked_roof(self, canvas: Canvas, x: int, y: int,
                         width: int, height: int, palette: StructurePalette):
        """Draw a peaked/triangular roof."""
        peak_x = x + width // 2
        peak_y = y - height // 2

        # Draw roof triangles
        for row in range(height):
            row_width = width - (row * width // height)
            row_x = x + (width - row_width) // 2
            actual_y = y + height - row - 1

            # Left side (highlight)
            for px in range(row_x, peak_x):
                if actual_y >= 0:
                    if px < peak_x - 2:
                        canvas.set_pixel_solid(px, actual_y, palette.roof_highlight)
                    else:
                        canvas.set_pixel_solid(px, actual_y, palette.roof_base)

            # Right side (shadow)
            for px in range(peak_x, row_x + row_width):
                if actual_y >= 0:
                    if px > peak_x + 2:
                        canvas.set_pixel_solid(px, actual_y, palette.roof_shadow)
                    else:
                        canvas.set_pixel_solid(px, actual_y, palette.roof_base)

    def _draw_flat_roof(self, canvas: Canvas, x: int, y: int,
                       width: int, height: int, palette: StructurePalette):
        """Draw a flat roof."""
        canvas.fill_rect(x, y, width, height, palette.roof_base)
        # Top highlight
        canvas.fill_rect(x, y, width, 1, palette.roof_highlight)
        # Bottom shadow
        canvas.fill_rect(x, y + height - 1, width, 1, palette.roof_shadow)

    def _draw_slanted_roof(self, canvas: Canvas, x: int, y: int,
                          width: int, height: int, palette: StructurePalette):
        """Draw a slanted roof."""
        for row in range(height):
            row_width = width - row
            actual_y = y + height - row - 1
            if actual_y >= 0:
                canvas.fill_rect(x, actual_y, row_width, 1, palette.roof_base)
                # Highlight on top edge
                if row > 0:
                    canvas.set_pixel_solid(x + row_width - 1, actual_y, palette.roof_highlight)

    def _draw_door(self, canvas: Canvas, x: int, y: int,
                  width: int, height: int, palette: StructurePalette):
        """Draw a door."""
        # Door frame
        canvas.fill_rect(x, y, width, height, palette.wood_dark)
        # Door body
        canvas.fill_rect(x + 1, y + 1, width - 2, height - 1, palette.door_base)
        # Highlight
        canvas.fill_rect(x + 1, y + 1, 1, height - 1, lighten(palette.door_base, 0.2))
        # Handle
        handle_y = y + height // 2
        canvas.set_pixel_solid(x + width - 3, handle_y, (200, 180, 50, 255))

    def _draw_window(self, canvas: Canvas, x: int, y: int,
                    width: int, height: int, palette: StructurePalette):
        """Draw a window."""
        # Frame
        canvas.fill_rect(x, y, width, height, palette.window_frame)
        # Glass
        canvas.fill_rect(x + 1, y + 1, width - 2, height - 2, palette.window_base)
        # Cross frame
        mid_x = x + width // 2
        mid_y = y + height // 2
        canvas.fill_rect(mid_x, y, 1, height, palette.window_frame)
        canvas.fill_rect(x, mid_y, width, 1, palette.window_frame)
        # Highlight
        canvas.set_pixel_solid(x + 2, y + 2, lighten(palette.window_base, 0.3))

    def _draw_chimney(self, canvas: Canvas, x: int, y: int,
                     width: int, height: int, palette: StructurePalette):
        """Draw a chimney."""
        # Body
        canvas.fill_rect(x, y, width, height, palette.wall_shadow)
        # Highlight
        canvas.fill_rect(x, y, 1, height, palette.wall_base)
        # Top rim
        canvas.fill_rect(x - 1, y, width + 2, 2, palette.wall_shadow)

    # ==================== Castle Generation ====================

    def generate_castle_wall(self, width: int = 64, height: int = 32,
                            has_crenellations: bool = True,
                            num_windows: int = 2) -> Canvas:
        """Generate a castle wall segment.

        Args:
            width: Canvas width
            height: Canvas height
            has_crenellations: Add crenellations (battlements)
            num_windows: Number of arrow slits

        Returns:
            Canvas with castle wall
        """
        self._reset_seed(100)

        canvas = Canvas(width, height)
        palette = StructurePalette.castle()

        wall_height = height - 6 if has_crenellations else height
        wall_y = height - wall_height

        # Main wall
        canvas.fill_rect(0, wall_y, width, wall_height, palette.wall_base)

        # Stone texture
        self._add_stone_texture(canvas, 0, wall_y, width, wall_height, palette)

        # Crenellations
        if has_crenellations:
            crenel_width = 6
            crenel_height = 6
            for x in range(0, width, crenel_width * 2):
                canvas.fill_rect(x, 0, crenel_width, crenel_height, palette.wall_base)
                self._add_stone_texture(canvas, x, 0, crenel_width, crenel_height, palette)

        # Arrow slits
        if num_windows > 0:
            slit_width = 2
            slit_height = 8
            slit_y = wall_y + (wall_height - slit_height) // 2
            spacing = width // (num_windows + 1)

            for i in range(num_windows):
                slit_x = spacing * (i + 1) - slit_width // 2
                canvas.fill_rect(slit_x, slit_y, slit_width, slit_height, (20, 20, 30, 255))

        return canvas

    def generate_castle_tower(self, width: int = 32, height: int = 64,
                             roof_style: str = 'tower') -> Canvas:
        """Generate a castle tower.

        Args:
            width: Canvas width
            height: Canvas height
            roof_style: Roof style ('tower', 'flat', 'dome')

        Returns:
            Canvas with castle tower
        """
        self._reset_seed(200)

        canvas = Canvas(width, height)
        palette = StructurePalette.castle()

        # Tower proportions
        roof_height = height // 4
        body_height = height - roof_height
        body_y = roof_height

        # Tower body
        canvas.fill_rect(2, body_y, width - 4, body_height, palette.wall_base)
        self._add_stone_texture(canvas, 2, body_y, width - 4, body_height, palette)

        # Crenellations at top of body
        crenel_width = 4
        crenel_height = 4
        crenel_y = body_y
        for x in range(2, width - 4, crenel_width * 2):
            canvas.fill_rect(x, crenel_y, crenel_width, crenel_height, palette.wall_base)

        # Roof
        if roof_style == 'tower':
            self._draw_conical_roof(canvas, 0, 0, width, roof_height, palette)
        elif roof_style == 'dome':
            self._draw_dome_roof(canvas, 2, 0, width - 4, roof_height, palette)
        else:
            self._draw_flat_roof(canvas, 0, body_y - 4, width, 4, palette)

        # Windows
        window_y = body_y + body_height // 3
        self._draw_window(canvas, width // 2 - 3, window_y, 6, 8, palette)

        return canvas

    def _draw_conical_roof(self, canvas: Canvas, x: int, y: int,
                          width: int, height: int, palette: StructurePalette):
        """Draw a conical tower roof."""
        center_x = x + width // 2

        for row in range(height):
            t = row / height
            row_width = int(width * (1 - t * 0.8))
            row_x = center_x - row_width // 2
            actual_y = y + height - row - 1

            for px in range(row_x, row_x + row_width):
                if px < center_x:
                    canvas.set_pixel_solid(px, actual_y, palette.roof_highlight)
                else:
                    canvas.set_pixel_solid(px, actual_y, palette.roof_shadow)

        # Peak
        canvas.set_pixel_solid(center_x, y, palette.roof_base)

    def _draw_dome_roof(self, canvas: Canvas, x: int, y: int,
                       width: int, height: int, palette: StructurePalette):
        """Draw a dome roof."""
        center_x = x + width // 2
        center_y = y + height

        for py in range(y, y + height):
            # Calculate dome width at this height
            t = (y + height - py) / height
            dome_width = int(width * math.sin(t * math.pi / 2))
            dome_x = center_x - dome_width // 2

            for px in range(dome_x, dome_x + dome_width):
                if px < center_x:
                    canvas.set_pixel_solid(px, py, palette.roof_highlight)
                else:
                    canvas.set_pixel_solid(px, py, palette.roof_shadow)

    def _add_stone_texture(self, canvas: Canvas, x: int, y: int,
                          width: int, height: int, palette: StructurePalette):
        """Add stone block texture to a wall."""
        block_width = 8
        block_height = 4

        for row in range(0, height, block_height):
            offset = (row // block_height % 2) * (block_width // 2)

            for col in range(-block_width, width + block_width, block_width):
                bx = x + col + offset
                by = y + row

                # Horizontal mortar line
                if by >= y and by < y + height:
                    for px in range(max(x, bx), min(x + width, bx + block_width)):
                        if self.rng.random() > 0.3:
                            canvas.set_pixel_solid(px, by, palette.wall_shadow)

                # Vertical mortar line
                if bx >= x and bx < x + width:
                    for py in range(max(y, by), min(y + height, by + block_height)):
                        if self.rng.random() > 0.3:
                            canvas.set_pixel_solid(bx, py, palette.wall_shadow)

    # ==================== Dungeon Tile Generation ====================

    def generate_dungeon_tile(self, tile_type: str = 'floor',
                             size: int = 16) -> Canvas:
        """Generate a dungeon tile.

        Args:
            tile_type: Type of tile ('floor', 'wall', 'corner', 'door', 'stairs')
            size: Tile size (square)

        Returns:
            Canvas with dungeon tile
        """
        self._reset_seed(300)

        canvas = Canvas(size, size)
        palette = StructurePalette.dungeon()

        if tile_type == 'floor':
            self._draw_dungeon_floor(canvas, size, palette)
        elif tile_type == 'wall':
            self._draw_dungeon_wall(canvas, size, palette)
        elif tile_type == 'corner':
            self._draw_dungeon_corner(canvas, size, palette)
        elif tile_type == 'door':
            self._draw_dungeon_door(canvas, size, palette)
        elif tile_type == 'stairs':
            self._draw_dungeon_stairs(canvas, size, palette)
        elif tile_type == 'pit':
            self._draw_dungeon_pit(canvas, size, palette)
        elif tile_type == 'pillar':
            self._draw_dungeon_pillar(canvas, size, palette)
        else:
            self._draw_dungeon_floor(canvas, size, palette)

        return canvas

    def _draw_dungeon_floor(self, canvas: Canvas, size: int, palette: StructurePalette):
        """Draw dungeon floor tile."""
        # Base floor
        canvas.fill_rect(0, 0, size, size, palette.wall_base)

        # Stone pattern
        for _ in range(size * size // 8):
            px = self.rng.randint(0, size - 1)
            py = self.rng.randint(0, size - 1)
            if self.rng.random() > 0.5:
                canvas.set_pixel_solid(px, py, palette.wall_highlight)
            else:
                canvas.set_pixel_solid(px, py, palette.wall_shadow)

        # Cracks
        if self.rng.random() > 0.5:
            crack_x = self.rng.randint(2, size - 3)
            for cy in range(self.rng.randint(0, size // 2), self.rng.randint(size // 2, size)):
                canvas.set_pixel_solid(crack_x + self.rng.randint(-1, 1), cy, (30, 25, 20, 255))

    def _draw_dungeon_wall(self, canvas: Canvas, size: int, palette: StructurePalette):
        """Draw dungeon wall tile."""
        # Base wall
        canvas.fill_rect(0, 0, size, size, palette.wall_shadow)

        # Top highlight
        canvas.fill_rect(0, 0, size, 2, palette.wall_base)

        # Stone blocks
        block_size = 4
        for row in range(0, size, block_size):
            offset = (row // block_size % 2) * (block_size // 2)
            for col in range(0, size + block_size, block_size):
                bx = col + offset
                if 0 <= bx < size:
                    canvas.set_pixel_solid(bx, row, (20, 15, 10, 255))
                if 0 <= bx < size and row > 0:
                    for px in range(max(0, bx), min(size, bx + block_size)):
                        canvas.set_pixel_solid(px, row, (20, 15, 10, 255))

    def _draw_dungeon_corner(self, canvas: Canvas, size: int, palette: StructurePalette):
        """Draw dungeon corner tile."""
        # Floor base
        self._draw_dungeon_floor(canvas, size, palette)

        # Corner walls
        wall_thickness = size // 3

        # Top wall
        canvas.fill_rect(0, 0, size, wall_thickness, palette.wall_shadow)
        canvas.fill_rect(0, wall_thickness - 1, size, 1, palette.wall_base)

        # Left wall
        canvas.fill_rect(0, 0, wall_thickness, size, palette.wall_shadow)
        canvas.fill_rect(wall_thickness - 1, 0, 1, size, palette.wall_base)

    def _draw_dungeon_door(self, canvas: Canvas, size: int, palette: StructurePalette):
        """Draw dungeon door tile."""
        # Floor
        self._draw_dungeon_floor(canvas, size, palette)

        # Door frame
        frame_width = size // 6
        canvas.fill_rect(0, 0, frame_width, size, palette.wall_shadow)
        canvas.fill_rect(size - frame_width, 0, frame_width, size, palette.wall_shadow)

        # Door
        door_width = size - frame_width * 2
        canvas.fill_rect(frame_width, 2, door_width, size - 2, palette.wood_base)

        # Door planks
        plank_width = door_width // 3
        for i in range(3):
            px = frame_width + i * plank_width
            canvas.fill_rect(px, 2, 1, size - 2, palette.wood_dark)

        # Handle
        canvas.set_pixel_solid(size - frame_width - 3, size // 2, (180, 160, 50, 255))

    def _draw_dungeon_stairs(self, canvas: Canvas, size: int, palette: StructurePalette):
        """Draw dungeon stairs tile."""
        step_count = 4
        step_height = size // step_count

        for i in range(step_count):
            y = i * step_height
            step_depth = size - i * (size // step_count)

            # Step top
            canvas.fill_rect(0, y, step_depth, 1, palette.wall_highlight)
            # Step face
            canvas.fill_rect(0, y + 1, step_depth, step_height - 1, palette.wall_base)
            # Step shadow
            if i < step_count - 1:
                canvas.fill_rect(step_depth - 2, y, 2, step_height, palette.wall_shadow)

    def _draw_dungeon_pit(self, canvas: Canvas, size: int, palette: StructurePalette):
        """Draw dungeon pit tile."""
        # Floor around pit
        self._draw_dungeon_floor(canvas, size, palette)

        # Pit
        pit_margin = 2
        pit_size = size - pit_margin * 2
        canvas.fill_rect(pit_margin, pit_margin, pit_size, pit_size, (10, 10, 15, 255))

        # Pit edges
        canvas.fill_rect(pit_margin, pit_margin, pit_size, 1, palette.wall_shadow)
        canvas.fill_rect(pit_margin, pit_margin, 1, pit_size, palette.wall_shadow)
        canvas.fill_rect(pit_margin + pit_size - 1, pit_margin, 1, pit_size, palette.wall_highlight)
        canvas.fill_rect(pit_margin, pit_margin + pit_size - 1, pit_size, 1, palette.wall_highlight)

    def _draw_dungeon_pillar(self, canvas: Canvas, size: int, palette: StructurePalette):
        """Draw dungeon pillar tile."""
        # Floor
        self._draw_dungeon_floor(canvas, size, palette)

        # Pillar
        pillar_width = size // 2
        pillar_x = (size - pillar_width) // 2

        # Base
        canvas.fill_rect(pillar_x - 1, size - 3, pillar_width + 2, 3, palette.wall_shadow)

        # Shaft
        canvas.fill_rect(pillar_x, 3, pillar_width, size - 6, palette.wall_base)
        canvas.fill_rect(pillar_x, 3, 2, size - 6, palette.wall_highlight)
        canvas.fill_rect(pillar_x + pillar_width - 2, 3, 2, size - 6, palette.wall_shadow)

        # Capital
        canvas.fill_rect(pillar_x - 1, 0, pillar_width + 2, 3, palette.wall_shadow)


# ==================== Convenience Functions ====================

def generate_house(width: int = 48, height: int = 48, style: str = 'cottage',
                  seed: int = 42) -> Canvas:
    """Generate a house sprite."""
    gen = StructureGenerator(seed)
    return gen.generate_house(width, height, style=style)


def generate_castle_wall(width: int = 64, height: int = 32, seed: int = 42) -> Canvas:
    """Generate a castle wall segment."""
    gen = StructureGenerator(seed)
    return gen.generate_castle_wall(width, height)


def generate_castle_tower(width: int = 32, height: int = 64, seed: int = 42) -> Canvas:
    """Generate a castle tower."""
    gen = StructureGenerator(seed)
    return gen.generate_castle_tower(width, height)


def generate_dungeon_tile(tile_type: str = 'floor', size: int = 16, seed: int = 42) -> Canvas:
    """Generate a dungeon tile."""
    gen = StructureGenerator(seed)
    return gen.generate_dungeon_tile(tile_type, size)


def generate_dungeon_tileset(size: int = 16, seed: int = 42) -> Dict[str, Canvas]:
    """Generate a complete dungeon tileset."""
    gen = StructureGenerator(seed)
    return {
        'floor': gen.generate_dungeon_tile('floor', size),
        'wall': gen.generate_dungeon_tile('wall', size),
        'corner': gen.generate_dungeon_tile('corner', size),
        'door': gen.generate_dungeon_tile('door', size),
        'stairs': gen.generate_dungeon_tile('stairs', size),
        'pit': gen.generate_dungeon_tile('pit', size),
        'pillar': gen.generate_dungeon_tile('pillar', size),
    }


def list_building_styles() -> List[str]:
    """List available building styles."""
    return [s.value for s in BuildingStyle]


def list_roof_styles() -> List[str]:
    """List available roof styles."""
    return [s.value for s in RoofStyle]


def list_dungeon_tile_types() -> List[str]:
    """List available dungeon tile types."""
    return [t.value for t in DungeonTileType]

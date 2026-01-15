"""
Spritesheet - Atlas packing and sprite sheet generation.

Provides:
- Automatic bin packing for sprites
- Grid-based sprite sheets
- JSON metadata export
- Animation strip creation
"""

import json
from typing import List, Tuple, Optional, Dict, Any, NamedTuple
from dataclasses import dataclass, field

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Canvas


class Rect(NamedTuple):
    """Rectangle for packing."""
    x: int
    y: int
    width: int
    height: int


@dataclass
class PackedSprite:
    """A sprite packed into an atlas."""
    name: str
    canvas: Canvas
    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0
    rotated: bool = False

    def __post_init__(self):
        if self.width == 0:
            self.width = self.canvas.width
        if self.height == 0:
            self.height = self.canvas.height


class BinPacker:
    """Binary tree bin packing algorithm.

    Uses the Guillotine algorithm for efficient 2D bin packing.
    """

    def __init__(self, width: int, height: int, padding: int = 0):
        """Initialize packer.

        Args:
            width: Atlas width
            height: Atlas height
            padding: Padding between sprites
        """
        self.width = width
        self.height = height
        self.padding = padding
        self.free_rects: List[Rect] = [Rect(0, 0, width, height)]
        self.used_rects: List[Rect] = []

    def insert(self, width: int, height: int) -> Optional[Rect]:
        """Insert a rectangle into the bin.

        Args:
            width: Rectangle width
            height: Rectangle height

        Returns:
            Packed rectangle or None if it doesn't fit
        """
        width += self.padding
        height += self.padding

        # Find best fit
        best_rect = None
        best_idx = -1
        best_score = float('inf')

        for idx, free in enumerate(self.free_rects):
            if width <= free.width and height <= free.height:
                # Best short side fit
                score = min(free.width - width, free.height - height)
                if score < best_score:
                    best_score = score
                    best_idx = idx
                    best_rect = Rect(free.x, free.y, width - self.padding, height - self.padding)

        if best_rect is None:
            return None

        # Split the free rectangle
        self._split_free_rect(best_idx, width, height)
        self.used_rects.append(best_rect)

        return best_rect

    def _split_free_rect(self, idx: int, width: int, height: int) -> None:
        """Split a free rectangle after placing a sprite."""
        free = self.free_rects.pop(idx)

        # Create new free rectangles
        # Right remainder
        if free.width - width > 0:
            self.free_rects.append(Rect(
                free.x + width,
                free.y,
                free.width - width,
                height
            ))

        # Bottom remainder
        if free.height - height > 0:
            self.free_rects.append(Rect(
                free.x,
                free.y + height,
                free.width,
                free.height - height
            ))

        # Merge free rectangles where possible
        self._merge_free_rects()

    def _merge_free_rects(self) -> None:
        """Merge adjacent free rectangles."""
        # Simple implementation - just remove fully contained rects
        i = 0
        while i < len(self.free_rects):
            j = i + 1
            while j < len(self.free_rects):
                ri = self.free_rects[i]
                rj = self.free_rects[j]

                # Check if one contains the other
                if (ri.x <= rj.x and ri.y <= rj.y and
                    ri.x + ri.width >= rj.x + rj.width and
                    ri.y + ri.height >= rj.y + rj.height):
                    self.free_rects.pop(j)
                elif (rj.x <= ri.x and rj.y <= ri.y and
                      rj.x + rj.width >= ri.x + ri.width and
                      rj.y + rj.height >= ri.y + ri.height):
                    self.free_rects.pop(i)
                    i -= 1
                    break
                else:
                    j += 1
            i += 1


def pack_sprites(sprites: List[Tuple[str, Canvas]],
                 max_width: int = 512,
                 max_height: int = 512,
                 padding: int = 1,
                 power_of_two: bool = True) -> Tuple[Canvas, List[PackedSprite]]:
    """Pack sprites into an atlas.

    Args:
        sprites: List of (name, canvas) tuples
        max_width: Maximum atlas width
        max_height: Maximum atlas height
        padding: Padding between sprites
        power_of_two: Constrain dimensions to power of 2

    Returns:
        (atlas_canvas, packed_sprites) tuple
    """
    if not sprites:
        return Canvas(1, 1, (0, 0, 0, 0)), []

    # Sort by area (largest first)
    sorted_sprites = sorted(sprites, key=lambda s: s[1].width * s[1].height, reverse=True)

    # Try packing with increasing sizes
    for size_mult in range(1, 10):
        width = min(max_width, 64 * size_mult)
        height = min(max_height, 64 * size_mult)

        if power_of_two:
            # Round up to power of 2
            width = 1 << (width - 1).bit_length()
            height = 1 << (height - 1).bit_length()

        packer = BinPacker(width, height, padding)
        packed = []
        success = True

        for name, canvas in sorted_sprites:
            rect = packer.insert(canvas.width, canvas.height)
            if rect is None:
                success = False
                break

            packed.append(PackedSprite(
                name=name,
                canvas=canvas,
                x=rect.x,
                y=rect.y,
                width=canvas.width,
                height=canvas.height
            ))

        if success:
            # Create atlas
            atlas = Canvas(width, height, (0, 0, 0, 0))
            for sprite in packed:
                atlas.blit(sprite.canvas, sprite.x, sprite.y)

            return atlas, packed

    raise ValueError(f"Could not pack {len(sprites)} sprites into {max_width}x{max_height}")


def create_grid_sheet(sprites: List[Canvas],
                      columns: int,
                      padding: int = 0,
                      background: Tuple[int, int, int, int] = (0, 0, 0, 0)
                      ) -> Canvas:
    """Create a simple grid-based sprite sheet.

    Args:
        sprites: List of sprite canvases
        columns: Number of columns
        padding: Padding between sprites
        background: Background color

    Returns:
        Sprite sheet canvas
    """
    if not sprites:
        return Canvas(1, 1, background)

    # Find max dimensions
    max_w = max(s.width for s in sprites)
    max_h = max(s.height for s in sprites)

    rows = (len(sprites) + columns - 1) // columns

    cell_w = max_w + padding * 2
    cell_h = max_h + padding * 2

    sheet = Canvas(columns * cell_w, rows * cell_h, background)

    for idx, sprite in enumerate(sprites):
        col = idx % columns
        row = idx // columns

        x = col * cell_w + padding + (max_w - sprite.width) // 2
        y = row * cell_h + padding + (max_h - sprite.height) // 2

        sheet.blit(sprite, x, y)

    return sheet


def create_animation_sheet(animations: Dict[str, List[Canvas]],
                           columns: int = 8,
                           padding: int = 1) -> Tuple[Canvas, Dict[str, Any]]:
    """Create sprite sheet from multiple animations.

    Args:
        animations: Dict of animation_name -> list of frames
        columns: Columns per animation row
        padding: Padding between frames

    Returns:
        (sheet_canvas, metadata) tuple
    """
    if not animations:
        return Canvas(1, 1, (0, 0, 0, 0)), {}

    # Find max frame size
    max_w = 0
    max_h = 0
    for frames in animations.values():
        for frame in frames:
            max_w = max(max_w, frame.width)
            max_h = max(max_h, frame.height)

    cell_w = max_w + padding * 2
    cell_h = max_h + padding * 2

    # Calculate sheet dimensions
    max_cols = max(min(len(f), columns) for f in animations.values())
    total_rows = sum((len(f) + columns - 1) // columns for f in animations.values())

    sheet = Canvas(max_cols * cell_w, total_rows * cell_h, (0, 0, 0, 0))

    metadata = {
        'frame_width': max_w,
        'frame_height': max_h,
        'animations': {}
    }

    current_row = 0
    for anim_name, frames in animations.items():
        anim_meta = {
            'start_row': current_row,
            'frame_count': len(frames),
            'frames': []
        }

        for idx, frame in enumerate(frames):
            col = idx % columns
            row = current_row + idx // columns

            x = col * cell_w + padding
            y = row * cell_h + padding

            sheet.blit(frame, x, y)

            anim_meta['frames'].append({
                'x': x,
                'y': y,
                'width': frame.width,
                'height': frame.height
            })

        rows_used = (len(frames) + columns - 1) // columns
        current_row += rows_used
        metadata['animations'][anim_name] = anim_meta

    return sheet, metadata


def export_atlas_json(packed_sprites: List[PackedSprite],
                      atlas_width: int, atlas_height: int,
                      filepath: str) -> None:
    """Export atlas metadata as JSON.

    Args:
        packed_sprites: List of packed sprites
        atlas_width: Atlas width
        atlas_height: Atlas height
        filepath: Output JSON path
    """
    data = {
        'atlas': {
            'width': atlas_width,
            'height': atlas_height
        },
        'sprites': {}
    }

    for sprite in packed_sprites:
        data['sprites'][sprite.name] = {
            'x': sprite.x,
            'y': sprite.y,
            'width': sprite.width,
            'height': sprite.height,
            'rotated': sprite.rotated
        }

    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)


def load_atlas_json(filepath: str) -> Dict[str, Any]:
    """Load atlas metadata from JSON.

    Args:
        filepath: JSON file path

    Returns:
        Atlas metadata dict
    """
    with open(filepath, 'r') as f:
        return json.load(f)


class SpriteAtlas:
    """High-level sprite atlas manager."""

    def __init__(self, max_width: int = 512, max_height: int = 512,
                 padding: int = 1):
        """Initialize atlas.

        Args:
            max_width: Maximum atlas width
            max_height: Maximum atlas height
            padding: Padding between sprites
        """
        self.max_width = max_width
        self.max_height = max_height
        self.padding = padding
        self.sprites: List[Tuple[str, Canvas]] = []

    def add(self, name: str, canvas: Canvas) -> None:
        """Add a sprite to the atlas.

        Args:
            name: Sprite name
            canvas: Sprite canvas
        """
        self.sprites.append((name, canvas))

    def add_multiple(self, sprites: Dict[str, Canvas]) -> None:
        """Add multiple sprites.

        Args:
            sprites: Dict of name -> canvas
        """
        for name, canvas in sprites.items():
            self.add(name, canvas)

    def build(self) -> Tuple[Canvas, List[PackedSprite]]:
        """Build the atlas.

        Returns:
            (atlas_canvas, packed_sprites) tuple
        """
        return pack_sprites(
            self.sprites,
            self.max_width,
            self.max_height,
            self.padding
        )

    def save(self, image_path: str, json_path: Optional[str] = None) -> None:
        """Save atlas to file.

        Args:
            image_path: PNG output path
            json_path: Optional JSON metadata path
        """
        atlas, packed = self.build()
        atlas.save(image_path)

        if json_path:
            export_atlas_json(packed, atlas.width, atlas.height, json_path)

    def clear(self) -> None:
        """Clear all sprites."""
        self.sprites.clear()


# Convenience functions
def create_tileset_sheet(tiles: List[Canvas], columns: int = 16) -> Canvas:
    """Create a tileset sprite sheet.

    Args:
        tiles: List of tile canvases
        columns: Number of columns

    Returns:
        Tileset sprite sheet
    """
    return create_grid_sheet(tiles, columns, padding=0)


def create_character_sheet(idle: List[Canvas],
                           walk: Optional[List[Canvas]] = None,
                           run: Optional[List[Canvas]] = None,
                           attack: Optional[List[Canvas]] = None,
                           columns: int = 8) -> Tuple[Canvas, Dict]:
    """Create a character animation sprite sheet.

    Args:
        idle: Idle animation frames
        walk: Walk animation frames
        run: Run animation frames
        attack: Attack animation frames
        columns: Frames per row

    Returns:
        (sheet, metadata) tuple
    """
    animations = {'idle': idle}
    if walk:
        animations['walk'] = walk
    if run:
        animations['run'] = run
    if attack:
        animations['attack'] = attack

    return create_animation_sheet(animations, columns)


def split_sheet(sheet: Canvas, frame_width: int, frame_height: int,
                count: Optional[int] = None) -> List[Canvas]:
    """Split a sprite sheet into individual frames.

    Args:
        sheet: Sprite sheet canvas
        frame_width: Width of each frame
        frame_height: Height of each frame
        count: Number of frames (None = calculate from dimensions)

    Returns:
        List of frame canvases
    """
    cols = sheet.width // frame_width
    rows = sheet.height // frame_height
    total = cols * rows

    if count is not None:
        total = min(total, count)

    frames = []
    for i in range(total):
        col = i % cols
        row = i // cols

        x = col * frame_width
        y = row * frame_height

        frame = Canvas(frame_width, frame_height, (0, 0, 0, 0))
        for fy in range(frame_height):
            for fx in range(frame_width):
                if x + fx < sheet.width and y + fy < sheet.height:
                    frame.pixels[fy][fx] = sheet.pixels[y + fy][x + fx]

        frames.append(frame)

    return frames

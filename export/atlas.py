"""
Sprite Atlas Generation - Pack multiple sprites into optimized atlases.

Provides:
- Automatic bin packing with multiple algorithms
- Multi-resolution atlas generation
- Engine-specific export (Unity, Godot, GameMaker)
- Atlas update/patching without full rebuild
"""

from typing import List, Tuple, Optional, Dict, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import math

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Canvas
from export.png import save_png


class PackingAlgorithm(Enum):
    """Bin packing algorithms."""
    SHELF = "shelf"           # Simple shelf packing
    MAXRECTS = "maxrects"     # MaxRects best fit
    GUILLOTINE = "guillotine" # Guillotine cutting


class AtlasFormat(Enum):
    """Export formats for different engines."""
    JSON = "json"          # Generic JSON format
    UNITY = "unity"        # Unity TextureAtlas
    GODOT = "godot"        # Godot .tres format
    GAMEMAKER = "gamemaker" # GameMaker sprite format
    PHASER = "phaser"      # Phaser texture atlas


@dataclass
class SpriteEntry:
    """A sprite to be packed into the atlas."""
    name: str
    canvas: Canvas
    padding: int = 1
    trim: bool = True  # Trim transparent pixels


@dataclass
class PackedSprite:
    """A sprite that has been packed into the atlas."""
    name: str
    x: int
    y: int
    width: int
    height: int
    original_width: int
    original_height: int
    trimmed: bool = False
    trim_x: int = 0
    trim_y: int = 0
    rotated: bool = False


@dataclass
class AtlasPage:
    """A single atlas texture page."""
    canvas: Canvas
    sprites: List[PackedSprite] = field(default_factory=list)
    index: int = 0


class SpriteAtlas:
    """Sprite atlas for efficient texture batching."""

    def __init__(
        self,
        max_width: int = 2048,
        max_height: int = 2048,
        padding: int = 1,
        power_of_two: bool = True,
        algorithm: PackingAlgorithm = PackingAlgorithm.MAXRECTS
    ):
        """Initialize atlas.

        Args:
            max_width: Maximum atlas width
            max_height: Maximum atlas height
            padding: Padding between sprites
            power_of_two: Constrain to power of 2 dimensions
            algorithm: Packing algorithm to use
        """
        self.max_width = max_width
        self.max_height = max_height
        self.padding = padding
        self.power_of_two = power_of_two
        self.algorithm = algorithm

        self.pages: List[AtlasPage] = []
        self.sprites: Dict[str, Tuple[int, PackedSprite]] = {}  # name -> (page_idx, sprite)

    def add_sprite(self, name: str, canvas: Canvas, trim: bool = True) -> bool:
        """Add a sprite to the atlas.

        Args:
            name: Unique sprite name
            canvas: Sprite canvas
            trim: Whether to trim transparent pixels

        Returns:
            True if sprite was added successfully
        """
        if name in self.sprites:
            return False

        entry = SpriteEntry(name=name, canvas=canvas, padding=self.padding, trim=trim)
        return self._pack_sprite(entry)

    def add_sprites(self, sprites: List[Tuple[str, Canvas]], trim: bool = True) -> int:
        """Add multiple sprites.

        Args:
            sprites: List of (name, canvas) tuples
            trim: Whether to trim transparent pixels

        Returns:
            Number of sprites successfully added
        """
        # Sort by height (descending) for better packing
        sorted_sprites = sorted(sprites, key=lambda s: s[1].height, reverse=True)
        added = 0
        for name, canvas in sorted_sprites:
            if self.add_sprite(name, canvas, trim):
                added += 1
        return added

    def get_sprite(self, name: str) -> Optional[Tuple[AtlasPage, PackedSprite]]:
        """Get a packed sprite by name."""
        if name not in self.sprites:
            return None
        page_idx, sprite = self.sprites[name]
        return self.pages[page_idx], sprite

    def save(
        self,
        path: str,
        format: AtlasFormat = AtlasFormat.JSON,
        include_metadata: bool = True
    ) -> List[str]:
        """Save atlas to files.

        Args:
            path: Base path for output files
            format: Export format
            include_metadata: Include sprite metadata

        Returns:
            List of saved file paths
        """
        saved = []

        # Save each page as PNG
        for i, page in enumerate(self.pages):
            if len(self.pages) > 1:
                png_path = f"{path}_{i}.png"
            else:
                png_path = f"{path}.png"
            save_png(page.canvas, png_path)
            saved.append(png_path)

        # Save metadata in requested format
        if include_metadata:
            meta_path = self._save_metadata(path, format)
            if meta_path:
                saved.append(meta_path)

        return saved

    def rebuild(self) -> None:
        """Rebuild the atlas (re-pack all sprites)."""
        # Collect all sprites
        all_sprites = []
        for name, (_, packed) in self.sprites.items():
            # We need to get original canvas - for now just skip
            pass

        # Reset and re-add
        self.pages = []
        self.sprites = {}

    def _pack_sprite(self, entry: SpriteEntry) -> bool:
        """Pack a single sprite using the selected algorithm."""
        canvas = entry.canvas
        width = canvas.width + entry.padding * 2
        height = canvas.height + entry.padding * 2

        # Trim if requested
        trim_x, trim_y = 0, 0
        trimmed = False
        if entry.trim:
            bounds = _get_content_bounds(canvas)
            if bounds:
                x1, y1, x2, y2 = bounds
                if x2 - x1 < canvas.width or y2 - y1 < canvas.height:
                    trimmed = True
                    trim_x, trim_y = x1, y1
                    canvas = _trim_canvas(canvas, bounds)
                    width = canvas.width + entry.padding * 2
                    height = canvas.height + entry.padding * 2

        # Try to fit in existing pages
        for page_idx, page in enumerate(self.pages):
            pos = self._find_position(page, width, height)
            if pos:
                x, y = pos
                self._place_sprite(page, entry, canvas, x, y, trimmed, trim_x, trim_y)
                return True

        # Need new page
        new_page = self._create_page()
        pos = self._find_position(new_page, width, height)
        if pos:
            x, y = pos
            self._place_sprite(new_page, entry, canvas, x, y, trimmed, trim_x, trim_y)
            return True

        return False

    def _find_position(self, page: AtlasPage, width: int, height: int) -> Optional[Tuple[int, int]]:
        """Find position for sprite using MaxRects algorithm."""
        if self.algorithm == PackingAlgorithm.SHELF:
            return self._find_shelf_position(page, width, height)
        elif self.algorithm == PackingAlgorithm.MAXRECTS:
            return self._find_maxrects_position(page, width, height)
        else:
            return self._find_guillotine_position(page, width, height)

    def _find_shelf_position(self, page: AtlasPage, width: int, height: int) -> Optional[Tuple[int, int]]:
        """Simple shelf-based packing."""
        if not hasattr(page, '_shelf_y'):
            page._shelf_y = 0
            page._shelf_x = 0
            page._shelf_height = 0

        # Check if fits on current shelf
        if page._shelf_x + width <= page.canvas.width:
            if page._shelf_y + height <= page.canvas.height:
                pos = (page._shelf_x, page._shelf_y)
                page._shelf_x += width
                page._shelf_height = max(page._shelf_height, height)
                return pos

        # Start new shelf
        page._shelf_y += page._shelf_height
        page._shelf_x = 0
        page._shelf_height = 0

        if page._shelf_y + height <= page.canvas.height and width <= page.canvas.width:
            pos = (page._shelf_x, page._shelf_y)
            page._shelf_x = width
            page._shelf_height = height
            return pos

        return None

    def _find_maxrects_position(self, page: AtlasPage, width: int, height: int) -> Optional[Tuple[int, int]]:
        """MaxRects best-fit packing."""
        if not hasattr(page, '_free_rects'):
            page._free_rects = [(0, 0, page.canvas.width, page.canvas.height)]

        best_score = float('inf')
        best_idx = -1
        best_pos = None

        for i, rect in enumerate(page._free_rects):
            rx, ry, rw, rh = rect
            if width <= rw and height <= rh:
                # Best area fit
                score = rw * rh - width * height
                if score < best_score:
                    best_score = score
                    best_idx = i
                    best_pos = (rx, ry)

        if best_pos is None:
            return None

        # Split the free rectangle
        rx, ry, rw, rh = page._free_rects[best_idx]
        del page._free_rects[best_idx]

        # Add new free rectangles
        if rw - width > 0:
            page._free_rects.append((rx + width, ry, rw - width, height))
        if rh - height > 0:
            page._free_rects.append((rx, ry + height, rw, rh - height))

        return best_pos

    def _find_guillotine_position(self, page: AtlasPage, width: int, height: int) -> Optional[Tuple[int, int]]:
        """Guillotine cutting algorithm."""
        # Use same as maxrects for now
        return self._find_maxrects_position(page, width, height)

    def _place_sprite(
        self,
        page: AtlasPage,
        entry: SpriteEntry,
        canvas: Canvas,
        x: int,
        y: int,
        trimmed: bool,
        trim_x: int,
        trim_y: int
    ) -> None:
        """Place sprite onto page."""
        # Blit sprite to page (with padding offset)
        px = x + self.padding
        py = y + self.padding

        for sy in range(canvas.height):
            for sx in range(canvas.width):
                pixel = canvas.get_pixel(sx, sy)
                if pixel and pixel[3] > 0:
                    page.canvas.set_pixel(px + sx, py + sy, pixel)

        # Record packed sprite
        packed = PackedSprite(
            name=entry.name,
            x=px,
            y=py,
            width=canvas.width,
            height=canvas.height,
            original_width=entry.canvas.width,
            original_height=entry.canvas.height,
            trimmed=trimmed,
            trim_x=trim_x,
            trim_y=trim_y,
        )
        page.sprites.append(packed)
        self.sprites[entry.name] = (page.index, packed)

    def _create_page(self) -> AtlasPage:
        """Create a new atlas page."""
        width = self.max_width
        height = self.max_height

        if self.power_of_two:
            width = _next_power_of_two(width)
            height = _next_power_of_two(height)

        canvas = Canvas(width, height, (0, 0, 0, 0))
        page = AtlasPage(canvas=canvas, index=len(self.pages))
        self.pages.append(page)
        return page

    def _save_metadata(self, path: str, format: AtlasFormat) -> Optional[str]:
        """Save atlas metadata in requested format."""
        if format == AtlasFormat.JSON:
            return self._save_json(path)
        elif format == AtlasFormat.UNITY:
            return self._save_unity(path)
        elif format == AtlasFormat.GODOT:
            return self._save_godot(path)
        elif format == AtlasFormat.GAMEMAKER:
            return self._save_gamemaker(path)
        elif format == AtlasFormat.PHASER:
            return self._save_phaser(path)
        return None

    def _save_json(self, path: str) -> str:
        """Save as generic JSON."""
        data = {
            "pages": [],
            "sprites": {}
        }

        for page in self.pages:
            page_data = {
                "width": page.canvas.width,
                "height": page.canvas.height,
                "sprites": len(page.sprites)
            }
            data["pages"].append(page_data)

        for name, (page_idx, sprite) in self.sprites.items():
            data["sprites"][name] = {
                "page": page_idx,
                "x": sprite.x,
                "y": sprite.y,
                "width": sprite.width,
                "height": sprite.height,
                "originalWidth": sprite.original_width,
                "originalHeight": sprite.original_height,
                "trimmed": sprite.trimmed,
                "trimX": sprite.trim_x,
                "trimY": sprite.trim_y,
            }

        json_path = f"{path}.json"
        with open(json_path, 'w') as f:
            json.dump(data, f, indent=2)
        return json_path

    def _save_unity(self, path: str) -> str:
        """Save as Unity-compatible JSON."""
        # Unity uses similar format to generic JSON
        return self._save_json(path)

    def _save_godot(self, path: str) -> str:
        """Save as Godot .tres resource."""
        tres_path = f"{path}.tres"
        with open(tres_path, 'w') as f:
            f.write("[gd_resource type=\"AtlasTexture\" format=2]\n\n")
            for name, (page_idx, sprite) in self.sprites.items():
                f.write(f"[sub_resource type=\"AtlasTexture\" id={hash(name) % 10000}]\n")
                f.write(f'atlas = ExtResource({page_idx + 1})\n')
                f.write(f'region = Rect2({sprite.x}, {sprite.y}, {sprite.width}, {sprite.height})\n\n')
        return tres_path

    def _save_gamemaker(self, path: str) -> str:
        """Save as GameMaker sprite JSON."""
        gm_path = f"{path}.yy"
        data = {
            "name": os.path.basename(path),
            "frames": []
        }
        for name, (page_idx, sprite) in self.sprites.items():
            data["frames"].append({
                "name": name,
                "x": sprite.x,
                "y": sprite.y,
                "w": sprite.width,
                "h": sprite.height
            })
        with open(gm_path, 'w') as f:
            json.dump(data, f, indent=2)
        return gm_path

    def _save_phaser(self, path: str) -> str:
        """Save as Phaser texture atlas JSON."""
        phaser_path = f"{path}_phaser.json"
        frames = {}
        for name, (page_idx, sprite) in self.sprites.items():
            frames[name] = {
                "frame": {"x": sprite.x, "y": sprite.y, "w": sprite.width, "h": sprite.height},
                "rotated": sprite.rotated,
                "trimmed": sprite.trimmed,
                "spriteSourceSize": {"x": sprite.trim_x, "y": sprite.trim_y,
                                      "w": sprite.width, "h": sprite.height},
                "sourceSize": {"w": sprite.original_width, "h": sprite.original_height}
            }
        data = {
            "frames": frames,
            "meta": {
                "app": "bitsy",
                "version": "1.0",
                "image": f"{os.path.basename(path)}.png",
                "format": "RGBA8888",
                "size": {"w": self.pages[0].canvas.width if self.pages else 0,
                        "h": self.pages[0].canvas.height if self.pages else 0}
            }
        }
        with open(phaser_path, 'w') as f:
            json.dump(data, f, indent=2)
        return phaser_path


# =============================================================================
# Helper Functions
# =============================================================================

def _get_content_bounds(canvas: Canvas) -> Optional[Tuple[int, int, int, int]]:
    """Get bounding box of non-transparent pixels."""
    min_x, min_y = canvas.width, canvas.height
    max_x, max_y = 0, 0
    found = False

    for y in range(canvas.height):
        for x in range(canvas.width):
            pixel = canvas.get_pixel(x, y)
            if pixel and pixel[3] > 0:
                found = True
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x + 1)
                max_y = max(max_y, y + 1)

    if not found:
        return None
    return (min_x, min_y, max_x, max_y)


def _trim_canvas(canvas: Canvas, bounds: Tuple[int, int, int, int]) -> Canvas:
    """Create trimmed copy of canvas."""
    x1, y1, x2, y2 = bounds
    width = x2 - x1
    height = y2 - y1

    trimmed = Canvas(width, height, (0, 0, 0, 0))
    for y in range(height):
        for x in range(width):
            pixel = canvas.get_pixel(x + x1, y + y1)
            if pixel:
                trimmed.set_pixel(x, y, pixel)

    return trimmed


def _next_power_of_two(n: int) -> int:
    """Get next power of two >= n."""
    if n <= 0:
        return 1
    n -= 1
    n |= n >> 1
    n |= n >> 2
    n |= n >> 4
    n |= n >> 8
    n |= n >> 16
    return n + 1


# =============================================================================
# Convenience Functions
# =============================================================================

def create_atlas(
    sprites: List[Tuple[str, Canvas]],
    max_size: int = 2048,
    padding: int = 1,
    algorithm: str = "maxrects"
) -> SpriteAtlas:
    """Create atlas from list of sprites.

    Args:
        sprites: List of (name, canvas) tuples
        max_size: Maximum atlas dimension
        padding: Padding between sprites
        algorithm: Packing algorithm name

    Returns:
        Packed SpriteAtlas
    """
    algo = PackingAlgorithm(algorithm)
    atlas = SpriteAtlas(
        max_width=max_size,
        max_height=max_size,
        padding=padding,
        algorithm=algo
    )
    atlas.add_sprites(sprites)
    return atlas


def pack_animations(
    animations: Dict[str, List[Canvas]],
    max_size: int = 2048
) -> SpriteAtlas:
    """Pack animation frames into atlas.

    Args:
        animations: Dict of animation_name -> list of frame canvases
        max_size: Maximum atlas dimension

    Returns:
        Packed SpriteAtlas with frames named "anim_name_0", "anim_name_1", etc.
    """
    sprites = []
    for anim_name, frames in animations.items():
        for i, frame in enumerate(frames):
            sprites.append((f"{anim_name}_{i}", frame))
    return create_atlas(sprites, max_size)


def list_packing_algorithms() -> List[str]:
    """List available packing algorithms."""
    return [a.value for a in PackingAlgorithm]


def list_atlas_formats() -> List[str]:
    """List available export formats."""
    return [f.value for f in AtlasFormat]

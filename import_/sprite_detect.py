"""Automatic sprite detection in sprite sheets."""

from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Set, Dict
from collections import deque

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Canvas

Color = Tuple[int, int, int, int]


@dataclass
class DetectedSprite:
    """A detected sprite with its bounds and extracted canvas."""
    bounds: Tuple[int, int, int, int]  # x, y, width, height
    canvas: Canvas
    label: Optional[str] = None

    @property
    def x(self) -> int:
        return self.bounds[0]

    @property
    def y(self) -> int:
        return self.bounds[1]

    @property
    def width(self) -> int:
        return self.bounds[2]

    @property
    def height(self) -> int:
        return self.bounds[3]


@dataclass
class DetectionConfig:
    """Configuration for sprite detection."""
    min_size: int = 4  # Minimum sprite dimension
    max_size: int = 256  # Maximum sprite dimension
    background_color: Optional[Color] = None  # Auto-detect if None
    margin: int = 0  # Extra margin around detected sprites
    merge_nearby: bool = True  # Merge sprites close together
    merge_threshold: int = 2  # Max gap to merge
    alpha_threshold: int = 10  # Alpha below this is background
    ignore_single_pixels: bool = True  # Ignore 1x1 detections


@dataclass
class Region:
    """A connected region of pixels."""
    pixels: Set[Tuple[int, int]] = field(default_factory=set)
    min_x: int = float('inf')
    min_y: int = float('inf')
    max_x: int = float('-inf')
    max_y: int = float('-inf')

    def add_pixel(self, x: int, y: int):
        """Add a pixel to the region."""
        self.pixels.add((x, y))
        self.min_x = min(self.min_x, x)
        self.min_y = min(self.min_y, y)
        self.max_x = max(self.max_x, x)
        self.max_y = max(self.max_y, y)

    @property
    def bounds(self) -> Tuple[int, int, int, int]:
        """Return bounding box (x, y, width, height)."""
        if not self.pixels:
            return (0, 0, 0, 0)
        return (
            self.min_x,
            self.min_y,
            self.max_x - self.min_x + 1,
            self.max_y - self.min_y + 1
        )

    @property
    def width(self) -> int:
        return self.max_x - self.min_x + 1 if self.pixels else 0

    @property
    def height(self) -> int:
        return self.max_y - self.min_y + 1 if self.pixels else 0

    def merge(self, other: 'Region'):
        """Merge another region into this one."""
        self.pixels.update(other.pixels)
        self.min_x = min(self.min_x, other.min_x)
        self.min_y = min(self.min_y, other.min_y)
        self.max_x = max(self.max_x, other.max_x)
        self.max_y = max(self.max_y, other.max_y)

    def overlaps_with_margin(self, other: 'Region', margin: int) -> bool:
        """Check if regions overlap or are within margin."""
        return not (
            self.max_x + margin < other.min_x or
            other.max_x + margin < self.min_x or
            self.max_y + margin < other.min_y or
            other.max_y + margin < self.min_y
        )


class SpriteDetector:
    """Detects individual sprites in sprite sheets."""

    def __init__(self, config: Optional[DetectionConfig] = None):
        self.config = config or DetectionConfig()

    def detect(self, canvas: Canvas) -> List[DetectedSprite]:
        """Detect sprites in canvas.

        Args:
            canvas: Source canvas (sprite sheet)

        Returns:
            List of detected sprites
        """
        # Detect background color
        bg = self.config.background_color
        if bg is None:
            bg = self.detect_background(canvas)

        # Find connected regions
        regions = self.find_connected_regions(canvas, bg)

        # Filter by size
        regions = [
            r for r in regions
            if (r.width >= self.config.min_size and
                r.height >= self.config.min_size and
                r.width <= self.config.max_size and
                r.height <= self.config.max_size)
        ]

        # Filter single pixels
        if self.config.ignore_single_pixels:
            regions = [r for r in regions if len(r.pixels) > 1]

        # Merge nearby regions
        if self.config.merge_nearby and self.config.merge_threshold > 0:
            regions = self._merge_regions(regions, self.config.merge_threshold)

        # Extract sprites
        sprites = []
        for i, region in enumerate(regions):
            bounds = region.bounds
            margin = self.config.margin

            # Apply margin (clamped to canvas bounds)
            x = max(0, bounds[0] - margin)
            y = max(0, bounds[1] - margin)
            x2 = min(canvas.width, bounds[0] + bounds[2] + margin)
            y2 = min(canvas.height, bounds[1] + bounds[3] + margin)
            w = x2 - x
            h = y2 - y

            # Extract sprite canvas
            sprite_canvas = Canvas(w, h)
            for sy in range(h):
                for sx in range(w):
                    color = canvas.get_pixel(x + sx, y + sy)
                    sprite_canvas.set_pixel(sx, sy, color)

            sprites.append(DetectedSprite(
                bounds=(x, y, w, h),
                canvas=sprite_canvas,
                label=f"sprite_{i}"
            ))

        # Sort by position (top-left to bottom-right)
        sprites.sort(key=lambda s: (s.y, s.x))

        return sprites

    def detect_background(self, canvas: Canvas) -> Color:
        """Detect the background color of a canvas.

        Uses edge colors and most common color as heuristics.
        """
        color_counts: Dict[Color, int] = {}

        # Count edge colors
        edge_weight = 3  # Weight edge colors more heavily

        # Top and bottom edges
        for x in range(canvas.width):
            for y in [0, canvas.height - 1]:
                color = canvas.get_pixel(x, y)
                color_counts[color] = color_counts.get(color, 0) + edge_weight

        # Left and right edges
        for y in range(canvas.height):
            for x in [0, canvas.width - 1]:
                color = canvas.get_pixel(x, y)
                color_counts[color] = color_counts.get(color, 0) + edge_weight

        # Count all colors
        for y in range(canvas.height):
            for x in range(canvas.width):
                color = canvas.get_pixel(x, y)
                color_counts[color] = color_counts.get(color, 0) + 1

        # Prefer transparent or most common edge color
        transparent = (0, 0, 0, 0)
        if transparent in color_counts:
            # Check if transparent is significant
            total = sum(color_counts.values())
            if color_counts[transparent] > total * 0.1:
                return transparent

        # Find most common color
        if color_counts:
            return max(color_counts.items(), key=lambda x: x[1])[0]

        return (0, 0, 0, 0)

    def find_connected_regions(self, canvas: Canvas, bg: Color) -> List[Region]:
        """Find connected non-background regions using flood fill."""
        visited: Set[Tuple[int, int]] = set()
        regions: List[Region] = []

        for y in range(canvas.height):
            for x in range(canvas.width):
                if (x, y) in visited:
                    continue

                color = canvas.get_pixel(x, y)
                if self._is_background(color, bg):
                    visited.add((x, y))
                    continue

                # Start new region with flood fill
                region = Region()
                queue = deque([(x, y)])

                while queue:
                    px, py = queue.popleft()

                    if (px, py) in visited:
                        continue
                    if px < 0 or px >= canvas.width or py < 0 or py >= canvas.height:
                        continue

                    pixel_color = canvas.get_pixel(px, py)
                    if self._is_background(pixel_color, bg):
                        visited.add((px, py))
                        continue

                    visited.add((px, py))
                    region.add_pixel(px, py)

                    # Add neighbors (4-connected)
                    queue.append((px + 1, py))
                    queue.append((px - 1, py))
                    queue.append((px, py + 1))
                    queue.append((px, py - 1))

                if region.pixels:
                    regions.append(region)

        return regions

    def _is_background(self, color: Color, bg: Color) -> bool:
        """Check if color is background."""
        # Transparent pixels are always background
        if color[3] < self.config.alpha_threshold:
            return True

        # Exact match
        if color == bg:
            return True

        return False

    def _merge_regions(self, regions: List[Region], threshold: int) -> List[Region]:
        """Merge regions that are close together."""
        if not regions:
            return []

        # Keep merging until no more merges possible
        merged = True
        while merged:
            merged = False
            new_regions = []
            used = [False] * len(regions)

            for i, r1 in enumerate(regions):
                if used[i]:
                    continue

                # Find all regions to merge with r1
                merged_region = Region()
                merged_region.merge(r1)
                used[i] = True

                for j, r2 in enumerate(regions):
                    if i == j or used[j]:
                        continue

                    if merged_region.overlaps_with_margin(r2, threshold):
                        merged_region.merge(r2)
                        used[j] = True
                        merged = True

                new_regions.append(merged_region)

            regions = new_regions

        return regions


# Convenience functions

def detect_sprites(canvas: Canvas, **kwargs) -> List[DetectedSprite]:
    """Detect sprites in a canvas.

    Args:
        canvas: Source canvas
        **kwargs: Detection config options (min_size, max_size, margin, etc.)

    Returns:
        List of detected sprites
    """
    config = DetectionConfig(**kwargs)
    detector = SpriteDetector(config)
    return detector.detect(canvas)


def detect_background(canvas: Canvas) -> Color:
    """Detect background color of a canvas.

    Args:
        canvas: Source canvas

    Returns:
        Detected background color
    """
    detector = SpriteDetector()
    return detector.detect_background(canvas)


def find_sprite_bounds(canvas: Canvas,
                       background_color: Optional[Color] = None) -> Tuple[int, int, int, int]:
    """Find bounding box of non-background content.

    Args:
        canvas: Source canvas
        background_color: Background color (auto-detect if None)

    Returns:
        Tuple of (x, y, width, height)
    """
    detector = SpriteDetector(DetectionConfig(
        background_color=background_color,
        min_size=1,
        merge_nearby=True
    ))

    sprites = detector.detect(canvas)
    if not sprites:
        return (0, 0, canvas.width, canvas.height)

    # Find overall bounds
    min_x = min(s.x for s in sprites)
    min_y = min(s.y for s in sprites)
    max_x = max(s.x + s.width for s in sprites)
    max_y = max(s.y + s.height for s in sprites)

    return (min_x, min_y, max_x - min_x, max_y - min_y)


def split_by_color(canvas: Canvas, separator_color: Color) -> List[Canvas]:
    """Split canvas by separator color (like grid lines).

    Args:
        canvas: Source canvas
        separator_color: Color of separator lines

    Returns:
        List of extracted canvases
    """
    detector = SpriteDetector(DetectionConfig(
        background_color=separator_color,
        min_size=1,
        merge_nearby=False
    ))

    sprites = detector.detect(canvas)
    return [s.canvas for s in sprites]

"""
Selection and Masking - Tools for selecting and masking regions.

Provides:
- Rectangular and elliptical selections
- Freeform polygon selections
- Magic wand (color-based) selection
- Selection operations (union, subtract, intersect)
- Mask creation and application
"""

from typing import List, Tuple, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Canvas
from core.color import color_distance_rgb as color_distance


class SelectionMode(Enum):
    """Selection combination modes."""
    REPLACE = "replace"
    ADD = "add"
    SUBTRACT = "subtract"
    INTERSECT = "intersect"


@dataclass
class Selection:
    """A selection representing a set of selected pixels.

    Selections are stored as a set of (x, y) coordinates.
    """
    width: int
    height: int
    pixels: Set[Tuple[int, int]] = field(default_factory=set)

    def __contains__(self, point: Tuple[int, int]) -> bool:
        """Check if a point is in the selection."""
        return point in self.pixels

    def __len__(self) -> int:
        """Get number of selected pixels."""
        return len(self.pixels)

    def __bool__(self) -> bool:
        """Check if selection is non-empty."""
        return len(self.pixels) > 0

    def add(self, x: int, y: int) -> None:
        """Add a pixel to the selection."""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.pixels.add((x, y))

    def remove(self, x: int, y: int) -> None:
        """Remove a pixel from the selection."""
        self.pixels.discard((x, y))

    def clear(self) -> None:
        """Clear the selection."""
        self.pixels.clear()

    def invert(self) -> 'Selection':
        """Create an inverted selection."""
        result = Selection(self.width, self.height)
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) not in self.pixels:
                    result.pixels.add((x, y))
        return result

    def union(self, other: 'Selection') -> 'Selection':
        """Combine with another selection (add)."""
        result = Selection(self.width, self.height)
        result.pixels = self.pixels | other.pixels
        return result

    def subtract(self, other: 'Selection') -> 'Selection':
        """Subtract another selection."""
        result = Selection(self.width, self.height)
        result.pixels = self.pixels - other.pixels
        return result

    def intersect(self, other: 'Selection') -> 'Selection':
        """Intersect with another selection."""
        result = Selection(self.width, self.height)
        result.pixels = self.pixels & other.pixels
        return result

    def copy(self) -> 'Selection':
        """Create a copy of this selection."""
        result = Selection(self.width, self.height)
        result.pixels = self.pixels.copy()
        return result

    def get_bounds(self) -> Optional[Tuple[int, int, int, int]]:
        """Get bounding rectangle (x, y, width, height).

        Returns:
            Bounding box tuple or None if empty
        """
        if not self.pixels:
            return None

        min_x = min(p[0] for p in self.pixels)
        max_x = max(p[0] for p in self.pixels)
        min_y = min(p[1] for p in self.pixels)
        max_y = max(p[1] for p in self.pixels)

        return (min_x, min_y, max_x - min_x + 1, max_y - min_y + 1)

    def expand(self, amount: int = 1) -> 'Selection':
        """Expand selection by amount pixels."""
        result = Selection(self.width, self.height)
        for x, y in self.pixels:
            for dy in range(-amount, amount + 1):
                for dx in range(-amount, amount + 1):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        result.pixels.add((nx, ny))
        return result

    def contract(self, amount: int = 1) -> 'Selection':
        """Contract selection by amount pixels."""
        # Expand the inverse, then invert back
        inv = self.invert()
        expanded_inv = inv.expand(amount)
        return expanded_inv.invert()

    def feather(self, radius: int = 1) -> 'Mask':
        """Create a feathered mask from selection.

        Args:
            radius: Feather radius in pixels

        Returns:
            Mask with soft edges
        """
        mask = Mask(self.width, self.height)

        for y in range(self.height):
            for x in range(self.width):
                if (x, y) in self.pixels:
                    mask.set(x, y, 1.0)
                else:
                    # Calculate distance to nearest selected pixel
                    min_dist = float('inf')
                    for dx in range(-radius, radius + 1):
                        for dy in range(-radius, radius + 1):
                            if (x + dx, y + dy) in self.pixels:
                                dist = (dx * dx + dy * dy) ** 0.5
                                min_dist = min(min_dist, dist)

                    if min_dist <= radius:
                        mask.set(x, y, 1.0 - (min_dist / radius))

        return mask


@dataclass
class Mask:
    """A mask with per-pixel opacity values (0.0 to 1.0)."""
    width: int
    height: int
    data: List[List[float]] = field(default_factory=list)

    def __post_init__(self):
        if not self.data:
            self.data = [[0.0] * self.width for _ in range(self.height)]

    def get(self, x: int, y: int) -> float:
        """Get mask value at position."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.data[y][x]
        return 0.0

    def set(self, x: int, y: int, value: float) -> None:
        """Set mask value at position."""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.data[y][x] = max(0.0, min(1.0, value))

    def fill(self, value: float) -> None:
        """Fill entire mask with value."""
        value = max(0.0, min(1.0, value))
        for y in range(self.height):
            for x in range(self.width):
                self.data[y][x] = value

    def invert(self) -> 'Mask':
        """Create an inverted mask."""
        result = Mask(self.width, self.height)
        for y in range(self.height):
            for x in range(self.width):
                result.data[y][x] = 1.0 - self.data[y][x]
        return result

    def to_selection(self, threshold: float = 0.5) -> Selection:
        """Convert mask to selection using threshold."""
        sel = Selection(self.width, self.height)
        for y in range(self.height):
            for x in range(self.width):
                if self.data[y][x] >= threshold:
                    sel.pixels.add((x, y))
        return sel

    def copy(self) -> 'Mask':
        """Create a copy of this mask."""
        result = Mask(self.width, self.height)
        for y in range(self.height):
            for x in range(self.width):
                result.data[y][x] = self.data[y][x]
        return result


# ============ Selection Tools ============

def select_rect(width: int, height: int,
                x: int, y: int, w: int, h: int) -> Selection:
    """Create rectangular selection.

    Args:
        width, height: Canvas dimensions
        x, y: Top-left corner
        w, h: Rectangle dimensions

    Returns:
        Selection containing the rectangle
    """
    sel = Selection(width, height)
    for py in range(max(0, y), min(height, y + h)):
        for px in range(max(0, x), min(width, x + w)):
            sel.pixels.add((px, py))
    return sel


def select_ellipse(width: int, height: int,
                   cx: int, cy: int, rx: int, ry: int) -> Selection:
    """Create elliptical selection.

    Args:
        width, height: Canvas dimensions
        cx, cy: Center point
        rx, ry: X and Y radii

    Returns:
        Selection containing the ellipse
    """
    sel = Selection(width, height)
    for py in range(max(0, cy - ry), min(height, cy + ry + 1)):
        for px in range(max(0, cx - rx), min(width, cx + rx + 1)):
            # Check if point is inside ellipse
            dx = (px - cx) / rx if rx > 0 else 0
            dy = (py - cy) / ry if ry > 0 else 0
            if dx * dx + dy * dy <= 1.0:
                sel.pixels.add((px, py))
    return sel


def select_polygon(width: int, height: int,
                   points: List[Tuple[int, int]]) -> Selection:
    """Create polygon selection.

    Args:
        width, height: Canvas dimensions
        points: List of polygon vertices

    Returns:
        Selection containing the polygon
    """
    if len(points) < 3:
        return Selection(width, height)

    sel = Selection(width, height)

    # Find bounding box
    min_x = max(0, min(p[0] for p in points))
    max_x = min(width - 1, max(p[0] for p in points))
    min_y = max(0, min(p[1] for p in points))
    max_y = min(height - 1, max(p[1] for p in points))

    # Point-in-polygon test for each pixel
    for py in range(min_y, max_y + 1):
        for px in range(min_x, max_x + 1):
            if _point_in_polygon(px, py, points):
                sel.pixels.add((px, py))

    return sel


def _point_in_polygon(x: int, y: int,
                      polygon: List[Tuple[int, int]]) -> bool:
    """Ray casting algorithm for point-in-polygon test."""
    n = len(polygon)
    inside = False

    j = n - 1
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]

        if ((yi > y) != (yj > y)) and \
           (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            inside = not inside

        j = i

    return inside


def select_by_color(canvas: Canvas, x: int, y: int,
                    tolerance: float = 0.0,
                    contiguous: bool = True) -> Selection:
    """Magic wand selection by color.

    Args:
        canvas: Source canvas
        x, y: Starting point
        tolerance: Color matching tolerance (0.0 to 1.0)
        contiguous: If True, only select connected pixels

    Returns:
        Selection of matching pixels
    """
    sel = Selection(canvas.width, canvas.height)

    target = canvas.get_pixel(x, y)
    if target is None:
        return sel

    tolerance_dist = tolerance * 441.67  # Max RGB distance

    if contiguous:
        # Flood fill
        stack = [(x, y)]
        visited = set()

        while stack:
            px, py = stack.pop()

            if (px, py) in visited:
                continue
            visited.add((px, py))

            if not (0 <= px < canvas.width and 0 <= py < canvas.height):
                continue

            pixel = canvas.get_pixel(px, py)
            if pixel is None:
                continue

            dist = color_distance(target, pixel)
            if dist <= tolerance_dist:
                sel.pixels.add((px, py))
                # Add neighbors
                stack.extend([
                    (px + 1, py), (px - 1, py),
                    (px, py + 1), (px, py - 1)
                ])
    else:
        # Select all matching pixels
        for py in range(canvas.height):
            for px in range(canvas.width):
                pixel = canvas.get_pixel(px, py)
                if pixel:
                    dist = color_distance(target, pixel)
                    if dist <= tolerance_dist:
                        sel.pixels.add((px, py))

    return sel


def select_all(canvas: Canvas) -> Selection:
    """Select all non-transparent pixels.

    Args:
        canvas: Source canvas

    Returns:
        Selection of all opaque pixels
    """
    sel = Selection(canvas.width, canvas.height)
    for y in range(canvas.height):
        for x in range(canvas.width):
            pixel = canvas.get_pixel(x, y)
            if pixel and pixel[3] > 0:
                sel.pixels.add((x, y))
    return sel


# ============ Mask Operations ============

def create_mask_from_selection(selection: Selection) -> Mask:
    """Create a mask from a selection (binary)."""
    mask = Mask(selection.width, selection.height)
    for x, y in selection.pixels:
        mask.set(x, y, 1.0)
    return mask


def create_mask_from_alpha(canvas: Canvas) -> Mask:
    """Create a mask from canvas alpha channel."""
    mask = Mask(canvas.width, canvas.height)
    for y in range(canvas.height):
        for x in range(canvas.width):
            pixel = canvas.get_pixel(x, y)
            if pixel:
                mask.set(x, y, pixel[3] / 255.0)
    return mask


def apply_mask(canvas: Canvas, mask: Mask) -> Canvas:
    """Apply mask to canvas, modifying alpha.

    Args:
        canvas: Source canvas
        mask: Mask to apply

    Returns:
        New canvas with mask applied
    """
    result = canvas.copy()
    for y in range(result.height):
        for x in range(result.width):
            pixel = result.pixels[y][x]
            mask_val = mask.get(x, y)
            new_alpha = int(pixel[3] * mask_val)
            result.pixels[y][x] = (pixel[0], pixel[1], pixel[2], new_alpha)
    return result


def copy_selection(canvas: Canvas, selection: Selection) -> Canvas:
    """Copy selected region to new canvas.

    Args:
        canvas: Source canvas
        selection: Selection to copy

    Returns:
        New canvas containing only selected pixels
    """
    result = Canvas(canvas.width, canvas.height, (0, 0, 0, 0))
    for x, y in selection.pixels:
        pixel = canvas.get_pixel(x, y)
        if pixel:
            result.set_pixel(x, y, pixel)
    return result


def fill_selection(canvas: Canvas, selection: Selection,
                   color: Tuple[int, int, int, int]) -> Canvas:
    """Fill selection with color.

    Args:
        canvas: Source canvas
        selection: Region to fill
        color: Fill color

    Returns:
        New canvas with selection filled
    """
    result = canvas.copy()
    for x, y in selection.pixels:
        result.set_pixel_solid(x, y, color)
    return result


def clear_selection(canvas: Canvas, selection: Selection) -> Canvas:
    """Clear (make transparent) selected pixels.

    Args:
        canvas: Source canvas
        selection: Region to clear

    Returns:
        New canvas with selection cleared
    """
    return fill_selection(canvas, selection, (0, 0, 0, 0))

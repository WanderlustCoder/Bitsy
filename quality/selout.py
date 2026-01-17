"""
Selective Outline (Selout) - Color-aware outline generation.

Selout creates outlines where each outline pixel's color is derived from
its adjacent interior fill color, rather than using a uniform outline color.
This creates more natural, professional-looking pixel art.

Example: A character with purple hair and tan skin will have purple outlines
around the hair and brown outlines around the skin.
"""

from typing import Optional, Tuple, List, Dict
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.canvas import Canvas
from core.color import Color, darken, adjust_saturation


# Direction vectors for neighbor sampling (8-directional)
NEIGHBOR_OFFSETS = [
    (-1, -1), (0, -1), (1, -1),
    (-1, 0),           (1, 0),
    (-1, 1),  (0, 1),  (1, 1)
]

# Cardinal directions only
CARDINAL_OFFSETS = [
    (0, -1),  # up
    (-1, 0),  # left
    (1, 0),   # right
    (0, 1),   # down
]


def is_edge_pixel(canvas: Canvas, x: int, y: int) -> bool:
    """Check if a pixel is on the edge (has transparent neighbor).

    Args:
        canvas: Source canvas
        x, y: Pixel coordinates

    Returns:
        True if pixel is opaque and has at least one transparent neighbor
    """
    pixel = canvas.get_pixel(x, y)
    if pixel is None or pixel[3] < 128:  # Transparent or nearly transparent
        return False

    # Check neighbors for transparency
    for dx, dy in NEIGHBOR_OFFSETS:
        nx, ny = x + dx, y + dy
        neighbor = canvas.get_pixel(nx, ny)
        if neighbor is None or neighbor[3] < 128:
            return True

    return False


def get_interior_neighbor_color(canvas: Canvas, x: int, y: int) -> Optional[Color]:
    """Find the dominant interior (non-edge) neighbor color.

    For an edge pixel, samples the neighbors that are NOT on the edge
    to find the interior fill color that should determine the outline.

    Args:
        canvas: Source canvas
        x, y: Edge pixel coordinates

    Returns:
        Interior neighbor color, or None if not found
    """
    interior_colors = []

    for dx, dy in NEIGHBOR_OFFSETS:
        nx, ny = x + dx, y + dy
        neighbor = canvas.get_pixel(nx, ny)

        # Skip transparent neighbors
        if neighbor is None or neighbor[3] < 128:
            continue

        # Check if this neighbor is interior (not on edge)
        if not is_edge_pixel(canvas, nx, ny):
            interior_colors.append(neighbor)
        else:
            # Even edge neighbors can contribute if they're more "inside"
            # Weight based on how many opaque neighbors they have
            opaque_count = 0
            for ddx, ddy in CARDINAL_OFFSETS:
                nnx, nny = nx + ddx, ny + ddy
                nn = canvas.get_pixel(nnx, nny)
                if nn is not None and nn[3] >= 128:
                    opaque_count += 1
            if opaque_count >= 3:  # Mostly surrounded by opaque
                interior_colors.append(neighbor)

    if not interior_colors:
        # Fallback: use current pixel color
        pixel = canvas.get_pixel(x, y)
        return pixel if pixel else None

    # Return the most common interior color (simple mode selection)
    # For better results, could do weighted averaging
    return interior_colors[0]


def derive_selout_color(fill_color: Color,
                        darken_factor: float = 0.30,
                        saturation_factor: float = 0.85) -> Color:
    """Create outline color from fill color for selout.

    Args:
        fill_color: Interior fill color
        darken_factor: How much to darken (0-1)
        saturation_factor: Saturation multiplier

    Returns:
        Outline color derived from fill
    """
    # Adjust saturation first, then darken
    color = adjust_saturation(fill_color, saturation_factor)
    color = darken(color, darken_factor)
    return color


def apply_selout(canvas: Canvas,
                 darken_factor: float = 0.30,
                 saturation_factor: float = 0.85,
                 replace_existing: bool = True) -> Canvas:
    """Apply selective outline to a canvas.

    Scans for edge pixels and replaces them with outline colors derived
    from their interior neighbors.

    Args:
        canvas: Source canvas (not modified)
        darken_factor: How much to darken outline colors
        saturation_factor: Saturation adjustment for outlines
        replace_existing: If True, replace edge pixels; if False, draw on transparent

    Returns:
        New canvas with selout applied
    """
    result = canvas.copy()
    width, height = canvas.width, canvas.height

    # First pass: identify all edge pixels
    edge_pixels = []
    for y in range(height):
        for x in range(width):
            if is_edge_pixel(canvas, x, y):
                edge_pixels.append((x, y))

    # Second pass: apply selout colors
    for x, y in edge_pixels:
        interior_color = get_interior_neighbor_color(canvas, x, y)

        if interior_color is not None:
            outline_color = derive_selout_color(
                interior_color,
                darken_factor,
                saturation_factor
            )
            result.set_pixel_solid(x, y, outline_color)

    return result


def apply_selout_to_region(canvas: Canvas,
                           x: int, y: int,
                           width: int, height: int,
                           darken_factor: float = 0.30,
                           saturation_factor: float = 0.85) -> None:
    """Apply selout to a specific region of a canvas (in-place).

    Args:
        canvas: Canvas to modify
        x, y: Top-left corner of region
        width, height: Region dimensions
        darken_factor: How much to darken outline colors
        saturation_factor: Saturation adjustment
    """
    # Identify edge pixels in region
    edge_pixels = []
    for py in range(y, min(y + height, canvas.height)):
        for px in range(x, min(x + width, canvas.width)):
            if is_edge_pixel(canvas, px, py):
                edge_pixels.append((px, py))

    # Apply selout colors
    for px, py in edge_pixels:
        interior_color = get_interior_neighbor_color(canvas, px, py)

        if interior_color is not None:
            outline_color = derive_selout_color(
                interior_color,
                darken_factor,
                saturation_factor
            )
            canvas.set_pixel_solid(px, py, outline_color)


def create_selout_outline(canvas: Canvas,
                          thickness: int = 1,
                          darken_factor: float = 0.30,
                          saturation_factor: float = 0.85) -> Canvas:
    """Create a selout outline on transparent pixels around the sprite.

    Unlike apply_selout which replaces edge pixels, this draws new outline
    pixels on the transparent areas adjacent to the sprite.

    Args:
        canvas: Source canvas (not modified)
        thickness: Outline thickness in pixels
        darken_factor: How much to darken outline colors
        saturation_factor: Saturation adjustment

    Returns:
        New canvas with selout outline added
    """
    result = canvas.copy()
    width, height = canvas.width, canvas.height

    # Find all transparent pixels adjacent to opaque pixels
    outline_positions = []

    for y in range(height):
        for x in range(width):
            pixel = canvas.get_pixel(x, y)

            # Skip opaque pixels
            if pixel is not None and pixel[3] >= 128:
                continue

            # Check if any neighbor within thickness is opaque
            for dy in range(-thickness, thickness + 1):
                for dx in range(-thickness, thickness + 1):
                    if dx == 0 and dy == 0:
                        continue

                    nx, ny = x + dx, y + dy
                    neighbor = canvas.get_pixel(nx, ny)

                    if neighbor is not None and neighbor[3] >= 128:
                        # This transparent pixel should get an outline
                        outline_positions.append((x, y, neighbor))
                        break
                else:
                    continue
                break

    # Apply outline colors
    for x, y, adjacent_color in outline_positions:
        outline_color = derive_selout_color(
            adjacent_color,
            darken_factor,
            saturation_factor
        )
        result.set_pixel_solid(x, y, outline_color)

    return result

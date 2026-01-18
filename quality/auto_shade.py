"""
Auto Shade - Intelligent shading and outline generation for pixel art.

Provides automatic shading based on:
- Edge detection
- Light direction
- Shape analysis

Features:
- Smart outlining (thin at curves, thick at corners)
- Cel shading with configurable levels
- Highlight and shadow placement
"""

import sys
import os
from typing import List, Tuple, Dict, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import math

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Canvas
from core.color import (
    Color, rgb_to_hsv, hsv_to_rgb, shift_hue, adjust_saturation,
    lighten, darken, blend, color_distance_weighted
)
from core.style import Style, ShadingConfig


class EdgeType(Enum):
    """Types of edges detected."""
    NONE = 0
    OUTER = 1       # Edge to transparent
    INNER = 2       # Edge between colors
    CORNER = 3      # Corner point
    CURVE = 4       # Curved edge


@dataclass
class EdgePixel:
    """Information about an edge pixel."""
    x: int
    y: int
    edge_type: EdgeType
    normal: Tuple[float, float]  # Outward normal direction
    curvature: float = 0.0       # Curvature at this point


@dataclass
class EdgeMap:
    """Map of all edges in a canvas."""
    width: int
    height: int
    edges: Dict[Tuple[int, int], EdgePixel] = field(default_factory=dict)

    def get(self, x: int, y: int) -> Optional[EdgePixel]:
        return self.edges.get((x, y))

    def is_edge(self, x: int, y: int) -> bool:
        return (x, y) in self.edges

    def get_outer_edges(self) -> List[EdgePixel]:
        return [e for e in self.edges.values() if e.edge_type == EdgeType.OUTER]

    def get_corners(self) -> List[EdgePixel]:
        return [e for e in self.edges.values() if e.edge_type == EdgeType.CORNER]


def detect_edges(canvas: Canvas, detect_inner: bool = True) -> EdgeMap:
    """
    Detect edges in a canvas.

    Args:
        canvas: Canvas to analyze
        detect_inner: Also detect edges between different colored regions

    Returns:
        EdgeMap with all detected edges
    """
    edge_map = EdgeMap(width=canvas.width, height=canvas.height)

    # Direction offsets for 8-connectivity
    directions = [
        (-1, -1), (0, -1), (1, -1),
        (-1, 0),          (1, 0),
        (-1, 1),  (0, 1),  (1, 1)
    ]

    # Cardinal directions for normal calculation
    cardinals = [(0, -1), (1, 0), (0, 1), (-1, 0)]

    for y in range(canvas.height):
        for x in range(canvas.width):
            pixel = canvas.pixels[y][x]

            # Skip transparent pixels
            if pixel[3] == 0:
                continue

            # Check for edges
            transparent_neighbors = 0
            different_neighbors = 0
            normal_x, normal_y = 0.0, 0.0

            for dx, dy in cardinals:
                nx, ny = x + dx, y + dy

                if not (0 <= nx < canvas.width and 0 <= ny < canvas.height):
                    # Outside canvas = transparent
                    transparent_neighbors += 1
                    normal_x -= dx
                    normal_y -= dy
                else:
                    neighbor = canvas.pixels[ny][nx]
                    if neighbor[3] == 0:
                        transparent_neighbors += 1
                        normal_x -= dx
                        normal_y -= dy
                    elif detect_inner:
                        dist = color_distance_weighted(
                            (pixel[0], pixel[1], pixel[2], pixel[3]),
                            (neighbor[0], neighbor[1], neighbor[2], neighbor[3])
                        )
                        if dist > 30:  # Different color threshold
                            different_neighbors += 1

            # Determine edge type
            edge_type = EdgeType.NONE

            if transparent_neighbors > 0:
                edge_type = EdgeType.OUTER
            elif different_neighbors > 0 and detect_inner:
                edge_type = EdgeType.INNER

            if edge_type != EdgeType.NONE:
                # Normalize the normal vector
                length = math.sqrt(normal_x ** 2 + normal_y ** 2)
                if length > 0:
                    normal_x /= length
                    normal_y /= length

                # Detect corners (multiple transparent directions)
                if transparent_neighbors >= 2:
                    # Check if it's a corner vs curve
                    # Corners have transparent in non-adjacent directions
                    corner_score = 0
                    for i, (dx1, dy1) in enumerate(cardinals):
                        dx2, dy2 = cardinals[(i + 1) % 4]
                        nx1, ny1 = x + dx1, y + dy1
                        nx2, ny2 = x + dx2, y + dy2

                        t1 = not (0 <= nx1 < canvas.width and 0 <= ny1 < canvas.height) or canvas.pixels[ny1][nx1][3] == 0
                        t2 = not (0 <= nx2 < canvas.width and 0 <= ny2 < canvas.height) or canvas.pixels[ny2][nx2][3] == 0

                        if t1 and t2:
                            corner_score += 1

                    if corner_score >= 1:
                        edge_type = EdgeType.CORNER

                edge_map.edges[(x, y)] = EdgePixel(
                    x=x, y=y,
                    edge_type=edge_type,
                    normal=(normal_x, normal_y),
                    curvature=0.0
                )

    # Calculate curvature for edges
    _calculate_curvature(edge_map)

    return edge_map


def _calculate_curvature(edge_map: EdgeMap) -> None:
    """Calculate curvature at each edge point."""
    for (x, y), edge in edge_map.edges.items():
        if edge.edge_type == EdgeType.CORNER:
            edge.curvature = 1.0
            continue

        # Sample nearby edge normals
        nearby_normals = []
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                if dx == 0 and dy == 0:
                    continue
                neighbor = edge_map.get(x + dx, y + dy)
                if neighbor:
                    nearby_normals.append(neighbor.normal)

        if len(nearby_normals) < 2:
            continue

        # Curvature = variation in normal direction
        angles = []
        for nx, ny in nearby_normals:
            angle = math.atan2(ny, nx)
            angles.append(angle)

        if angles:
            angle_variance = sum((a - sum(angles)/len(angles))**2 for a in angles) / len(angles)
            edge.curvature = min(1.0, angle_variance * 2)


def smart_outline(canvas: Canvas, outline_color: Optional[Color] = None,
                  thin_at_curves: bool = True, thick_at_corners: bool = True) -> Canvas:
    """
    Apply smart outline that varies based on edge features.

    Args:
        canvas: Canvas to outline
        outline_color: Color for outline (None = auto-darken)
        thin_at_curves: Use thinner outline at curved edges
        thick_at_corners: Use thicker outline at corners

    Returns:
        New canvas with outline applied
    """
    result = canvas.copy()
    edge_map = detect_edges(canvas, detect_inner=False)

    for (x, y), edge in edge_map.edges.items():
        if edge.edge_type == EdgeType.NONE:
            continue

        pixel = canvas.pixels[y][x]

        # Determine outline color
        if outline_color is not None:
            color = outline_color
        else:
            # Auto-darken based on pixel color
            color = darken((pixel[0], pixel[1], pixel[2], pixel[3]), 0.4)

        # Determine if we should draw outline here
        draw = True

        if thin_at_curves and edge.curvature < 0.3 and edge.edge_type != EdgeType.CORNER:
            # Skip some curve pixels for thinner appearance
            # Use checkerboard pattern
            if (x + y) % 2 == 0:
                draw = False

        if draw:
            result.pixels[y][x] = list(color)

            # Add extra thickness at corners
            if thick_at_corners and edge.edge_type == EdgeType.CORNER:
                # Extend outline in normal direction
                nx = int(round(x + edge.normal[0]))
                ny = int(round(y + edge.normal[1]))
                if 0 <= nx < result.width and 0 <= ny < result.height:
                    if canvas.pixels[ny][nx][3] == 0:
                        result.pixels[ny][nx] = list(color)

    return result


def apply_cel_shading(canvas: Canvas, levels: int = 3,
                      light_direction: Tuple[float, float] = (1.0, -1.0),
                      edge_map: Optional[EdgeMap] = None) -> Canvas:
    """
    Apply cel shading to a canvas.

    Args:
        canvas: Canvas to shade
        levels: Number of shading levels (2-5 recommended)
        light_direction: Direction light is coming from (normalized)
        edge_map: Pre-computed edge map (optional)

    Returns:
        New canvas with cel shading applied
    """
    result = canvas.copy()

    if edge_map is None:
        edge_map = detect_edges(canvas, detect_inner=False)

    # Normalize light direction
    lx, ly = light_direction
    length = math.sqrt(lx ** 2 + ly ** 2)
    if length > 0:
        lx /= length
        ly /= length

    # Process each opaque pixel
    for y in range(canvas.height):
        for x in range(canvas.width):
            pixel = canvas.pixels[y][x]
            if pixel[3] == 0:
                continue

            # Get edge info if available
            edge = edge_map.get(x, y)

            # Calculate shading factor based on normal
            if edge and edge.edge_type in (EdgeType.OUTER, EdgeType.CORNER, EdgeType.CURVE):
                # Dot product of normal with light direction
                dot = edge.normal[0] * lx + edge.normal[1] * ly
            else:
                # Interior pixel - estimate based on nearby edges
                dot = _estimate_interior_lighting(canvas, edge_map, x, y, lx, ly)

            # Map dot product to shading level
            # dot ranges from -1 (shadow) to 1 (highlight)
            normalized = (dot + 1) / 2  # 0 to 1
            level = int(normalized * levels)
            level = max(0, min(levels - 1, level))

            # Apply shading
            shade_factor = level / (levels - 1) if levels > 1 else 0.5

            # Adjust color based on shade level
            h, s, v = rgb_to_hsv(pixel[0], pixel[1], pixel[2])

            # Shadows: darker, shift toward cool, less saturated
            # Highlights: lighter, shift toward warm
            if shade_factor < 0.5:
                # Shadow
                shadow_amount = 1 - shade_factor * 2  # 1 at full shadow, 0 at mid
                new_v = v * (0.5 + 0.5 * (1 - shadow_amount))
                new_h = (h - 15 * shadow_amount) % 360  # Shift toward blue
                new_s = s * (0.9 + 0.1 * (1 - shadow_amount))
            else:
                # Highlight
                highlight_amount = (shade_factor - 0.5) * 2  # 0 at mid, 1 at full highlight
                new_v = v + (1 - v) * highlight_amount * 0.4
                new_h = (h + 10 * highlight_amount) % 360  # Shift toward yellow
                new_s = s * (1 - 0.1 * highlight_amount)

            r, g, b = hsv_to_rgb(new_h, max(0, min(1, new_s)), max(0, min(1, new_v)))
            result.pixels[y][x] = [r, g, b, pixel[3]]

    return result


def _estimate_interior_lighting(canvas: Canvas, edge_map: EdgeMap,
                                  x: int, y: int, lx: float, ly: float) -> float:
    """Estimate lighting for interior pixel based on nearby edges."""
    total_dot = 0.0
    weight_sum = 0.0

    # Sample nearby edge pixels
    search_radius = 5
    for dy in range(-search_radius, search_radius + 1):
        for dx in range(-search_radius, search_radius + 1):
            edge = edge_map.get(x + dx, y + dy)
            if edge:
                dist = math.sqrt(dx ** 2 + dy ** 2)
                if dist > 0:
                    weight = 1 / dist
                    dot = edge.normal[0] * lx + edge.normal[1] * ly
                    total_dot += dot * weight
                    weight_sum += weight

    if weight_sum > 0:
        return total_dot / weight_sum
    return 0.0


def add_highlights(canvas: Canvas, light_direction: Tuple[float, float] = (1.0, -1.0),
                   intensity: float = 0.3, color_shift: float = 15) -> Canvas:
    """
    Add highlights to lit areas.

    Args:
        canvas: Canvas to modify
        light_direction: Direction of light source
        intensity: Highlight intensity (0-1)
        color_shift: Degrees to shift hue toward warm

    Returns:
        New canvas with highlights added
    """
    result = canvas.copy()
    edge_map = detect_edges(canvas, detect_inner=False)

    lx, ly = light_direction
    length = math.sqrt(lx ** 2 + ly ** 2)
    if length > 0:
        lx /= length
        ly /= length

    for (x, y), edge in edge_map.edges.items():
        if edge.edge_type == EdgeType.NONE:
            continue

        # Only add highlights where normal faces toward light
        dot = edge.normal[0] * lx + edge.normal[1] * ly
        if dot < 0.3:
            continue

        pixel = canvas.pixels[y][x]
        h, s, v = rgb_to_hsv(pixel[0], pixel[1], pixel[2])

        # Apply highlight
        highlight_strength = (dot - 0.3) / 0.7 * intensity
        new_v = v + (1 - v) * highlight_strength
        new_h = (h + color_shift * highlight_strength) % 360
        new_s = s * (1 - 0.15 * highlight_strength)

        r, g, b = hsv_to_rgb(new_h, max(0, min(1, new_s)), max(0, min(1, new_v)))
        result.pixels[y][x] = [r, g, b, pixel[3]]

    return result


def add_shadows(canvas: Canvas, light_direction: Tuple[float, float] = (1.0, -1.0),
                intensity: float = 0.3, color_shift: float = -20) -> Canvas:
    """
    Add shadows to unlit areas.

    Args:
        canvas: Canvas to modify
        light_direction: Direction of light source
        intensity: Shadow intensity (0-1)
        color_shift: Degrees to shift hue toward cool

    Returns:
        New canvas with shadows added
    """
    result = canvas.copy()
    edge_map = detect_edges(canvas, detect_inner=False)

    lx, ly = light_direction
    length = math.sqrt(lx ** 2 + ly ** 2)
    if length > 0:
        lx /= length
        ly /= length

    for (x, y), edge in edge_map.edges.items():
        if edge.edge_type == EdgeType.NONE:
            continue

        # Only add shadows where normal faces away from light
        dot = edge.normal[0] * lx + edge.normal[1] * ly
        if dot > -0.2:
            continue

        pixel = canvas.pixels[y][x]
        h, s, v = rgb_to_hsv(pixel[0], pixel[1], pixel[2])

        # Apply shadow
        shadow_strength = (abs(dot) - 0.2) / 0.8 * intensity
        new_v = v * (1 - shadow_strength * 0.5)
        new_h = (h + color_shift * shadow_strength) % 360
        new_s = s * (1 - 0.1 * shadow_strength)

        r, g, b = hsv_to_rgb(new_h, max(0, min(1, new_s)), max(0, min(1, new_v)))
        result.pixels[y][x] = [r, g, b, pixel[3]]

    return result


def calculate_highlight_position(shape_mask: Canvas,
                                  light_dir: Tuple[float, float] = (1.0, -1.0),
                                  margin: float = 0.2) -> Tuple[int, int]:
    """
    Find optimal highlight position based on shape and lighting.

    Instead of centering highlights geometrically, this calculates where
    a specular highlight would naturally appear based on:
    1. The shape's bounding area
    2. The light direction
    3. Surface normal estimation

    Args:
        shape_mask: Canvas where opaque pixels define the shape
        light_dir: Direction light is coming FROM (e.g., (1, -1) = upper-right)
        margin: How far from edge to place highlight (0.0-0.5, as fraction of size)

    Returns:
        (x, y) position for highlight center
    """
    # Find bounding box of opaque pixels
    min_x, min_y = shape_mask.width, shape_mask.height
    max_x, max_y = 0, 0
    opaque_pixels = []

    for y in range(shape_mask.height):
        for x in range(shape_mask.width):
            pixel = shape_mask.get_pixel(x, y)
            if pixel and pixel[3] > 128:
                opaque_pixels.append((x, y))
                min_x = min(min_x, x)
                max_x = max(max_x, x)
                min_y = min(min_y, y)
                max_y = max(max_y, y)

    if not opaque_pixels:
        # Empty shape, return center
        return (shape_mask.width // 2, shape_mask.height // 2)

    # Normalize light direction
    lx, ly = light_dir
    length = math.sqrt(lx * lx + ly * ly)
    if length > 0:
        lx /= length
        ly /= length

    # Calculate shape center and size
    cx = (min_x + max_x) / 2
    cy = (min_y + max_y) / 2
    width = max_x - min_x + 1
    height = max_y - min_y + 1

    # Highlight position: offset from center toward light source
    # The highlight appears where light "hits" the surface
    # For a convex shape, this is toward the light direction
    offset_x = lx * width * (0.5 - margin)
    offset_y = ly * height * (0.5 - margin)

    highlight_x = int(cx + offset_x)
    highlight_y = int(cy + offset_y)

    # Ensure highlight is within the shape
    # Find nearest opaque pixel if we're outside
    if shape_mask.get_pixel(highlight_x, highlight_y) is None or \
       shape_mask.get_pixel(highlight_x, highlight_y)[3] < 128:
        # Find closest opaque pixel
        best_dist = float('inf')
        best_pos = (int(cx), int(cy))
        for px, py in opaque_pixels:
            dist = (px - highlight_x) ** 2 + (py - highlight_y) ** 2
            if dist < best_dist:
                best_dist = dist
                best_pos = (px, py)
        highlight_x, highlight_y = best_pos

    return (highlight_x, highlight_y)


def apply_specular_highlight(canvas: Canvas, cx: int, cy: int,
                             radius: int = 2, intensity: float = 0.8) -> Canvas:
    """
    Apply a specular highlight at a specific position.

    Creates a small bright spot that simulates light reflection,
    commonly used on eyes, buttons, gems, and glossy surfaces.

    Args:
        canvas: Canvas to modify
        cx, cy: Center position for highlight
        radius: Highlight radius in pixels
        intensity: Brightness (0-1, where 1 = full white)

    Returns:
        New canvas with highlight applied
    """
    result = canvas.copy()

    for y in range(cy - radius, cy + radius + 1):
        for x in range(cx - radius, cx + radius + 1):
            if not (0 <= x < canvas.width and 0 <= y < canvas.height):
                continue

            pixel = canvas.get_pixel(x, y)
            if not pixel or pixel[3] < 128:
                continue

            # Calculate distance from center
            dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
            if dist > radius:
                continue

            # Falloff from center
            falloff = 1.0 - (dist / radius)
            strength = falloff * intensity

            # Blend toward white
            r = int(pixel[0] + (255 - pixel[0]) * strength)
            g = int(pixel[1] + (255 - pixel[1]) * strength)
            b = int(pixel[2] + (255 - pixel[2]) * strength)

            result.pixels[y][x] = [r, g, b, pixel[3]]

    return result


def auto_highlight(canvas: Canvas, light_dir: Tuple[float, float] = (1.0, -1.0),
                   radius: int = 2, intensity: float = 0.6) -> Canvas:
    """
    Automatically place and apply a specular highlight.

    Combines calculate_highlight_position and apply_specular_highlight
    for convenient single-function use.

    Args:
        canvas: Canvas to add highlight to
        light_dir: Direction light is coming from
        radius: Highlight radius
        intensity: Highlight brightness

    Returns:
        New canvas with highlight applied
    """
    hx, hy = calculate_highlight_position(canvas, light_dir)
    return apply_specular_highlight(canvas, hx, hy, radius, intensity)


def auto_shade(canvas: Canvas, style: Optional[Style] = None,
               light_direction: Tuple[float, float] = (1.0, -1.0)) -> Canvas:
    """
    Automatically apply shading based on style configuration.

    Args:
        canvas: Canvas to shade
        style: Style configuration (None = use defaults)
        light_direction: Direction of light source

    Returns:
        New canvas with shading applied
    """
    if style is None:
        # Default modern HD style
        result = apply_cel_shading(canvas, levels=4, light_direction=light_direction)
        result = add_highlights(result, light_direction, intensity=0.25)
        result = add_shadows(result, light_direction, intensity=0.2)
        return result

    # Apply based on style settings
    shading = style.shading

    if shading.mode == 'flat':
        return canvas.copy()

    elif shading.mode == 'cel':
        result = apply_cel_shading(
            canvas,
            levels=shading.levels,
            light_direction=light_direction
        )
        return result

    elif shading.mode == 'gradient':
        # Gradient uses more levels for smoother shading
        result = apply_cel_shading(
            canvas,
            levels=max(5, shading.levels * 2),
            light_direction=light_direction
        )
        return result

    else:  # dither or other
        result = apply_cel_shading(
            canvas,
            levels=shading.levels,
            light_direction=light_direction
        )
        # Could add dithering here
        return result

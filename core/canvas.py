"""
Canvas - Drawing surface with primitives for pixel art.

Provides a 2D canvas with methods for drawing shapes, lines,
and other primitives commonly needed for sprite generation.
"""

import math
from typing import List, Tuple, Optional
from .png_writer import (
    Color, create_png, save_png, create_blank_canvas, blend_colors
)


def lerp_color(c1: Color, c2: Color, t: float) -> Color:
    """Linear interpolation between two colors."""
    t = max(0.0, min(1.0, t))
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t),
        int(c1[3] + (c2[3] - c1[3]) * t)
    )


def hex_to_rgba(hex_color: str, alpha: int = 255) -> Color:
    """Convert hex color string to RGBA tuple."""
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return (r, g, b, alpha)


class Canvas:
    """Drawing canvas with pixel art primitives."""

    def __init__(self, width: int, height: int, bg_color: Color = (0, 0, 0, 0)):
        self.width = width
        self.height = height
        self.pixels = create_blank_canvas(width, height, bg_color)

    def clear(self, color: Color = (0, 0, 0, 0)) -> None:
        """Clear the canvas with a color."""
        self.pixels = create_blank_canvas(self.width, self.height, color)

    def get_pixel(self, x: int, y: int) -> Optional[Color]:
        """Get pixel color at position."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.pixels[y][x]
        return None

    def set_pixel(self, x: int, y: int, color: Color) -> None:
        """Set a single pixel with alpha blending."""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.pixels[y][x] = blend_colors(self.pixels[y][x], color)

    def set_pixel_solid(self, x: int, y: int, color: Color) -> None:
        """Set a single pixel without alpha blending (replace)."""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.pixels[y][x] = color

    # === Shape Primitives ===

    def fill_rect(self, x: int, y: int, w: int, h: int, color: Color) -> None:
        """Fill a rectangle."""
        for py in range(max(0, y), min(self.height, y + h)):
            for px in range(max(0, x), min(self.width, x + w)):
                self.set_pixel(px, py, color)

    def draw_rect(self, x: int, y: int, w: int, h: int, color: Color) -> None:
        """Draw rectangle outline."""
        for px in range(x, x + w):
            self.set_pixel(px, y, color)
            self.set_pixel(px, y + h - 1, color)
        for py in range(y, y + h):
            self.set_pixel(x, py, color)
            self.set_pixel(x + w - 1, py, color)

    def fill_circle(self, cx: int, cy: int, r: int, color: Color) -> None:
        """Fill a circle."""
        for py in range(max(0, cy - r), min(self.height, cy + r + 1)):
            for px in range(max(0, cx - r), min(self.width, cx + r + 1)):
                if (px - cx) ** 2 + (py - cy) ** 2 <= r * r:
                    self.set_pixel(px, py, color)

    def draw_circle(self, cx: int, cy: int, r: int, color: Color) -> None:
        """Draw circle outline using midpoint algorithm."""
        x, y = r, 0
        err = 1 - r

        while x >= y:
            self.set_pixel(cx + x, cy + y, color)
            self.set_pixel(cx + y, cy + x, color)
            self.set_pixel(cx - y, cy + x, color)
            self.set_pixel(cx - x, cy + y, color)
            self.set_pixel(cx - x, cy - y, color)
            self.set_pixel(cx - y, cy - x, color)
            self.set_pixel(cx + y, cy - x, color)
            self.set_pixel(cx + x, cy - y, color)

            y += 1
            if err < 0:
                err += 2 * y + 1
            else:
                x -= 1
                err += 2 * (y - x + 1)

    def fill_ellipse(self, cx: int, cy: int, rx: int, ry: int, color: Color) -> None:
        """Fill an ellipse."""
        for py in range(max(0, cy - ry), min(self.height, cy + ry + 1)):
            for px in range(max(0, cx - rx), min(self.width, cx + rx + 1)):
                dx = (px - cx) / max(rx, 0.1)
                dy = (py - cy) / max(ry, 0.1)
                if dx * dx + dy * dy <= 1.0:
                    self.set_pixel(px, py, color)

    # === Line Drawing ===

    def draw_line(self, x1: int, y1: int, x2: int, y2: int, color: Color, thickness: int = 1) -> None:
        """Draw a line using Bresenham's algorithm."""
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy

        while True:
            if thickness == 1:
                self.set_pixel(x1, y1, color)
            else:
                self.fill_circle(x1, y1, thickness // 2, color)

            if x1 == x2 and y1 == y2:
                break

            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy

    # === Polygon ===

    def fill_polygon(self, points: List[Tuple[int, int]], color: Color) -> None:
        """Fill a polygon using scanline algorithm."""
        if len(points) < 3:
            return

        min_y = max(0, min(p[1] for p in points))
        max_y = min(self.height - 1, max(p[1] for p in points))

        for y in range(min_y, max_y + 1):
            intersections = []
            n = len(points)
            for i in range(n):
                p1 = points[i]
                p2 = points[(i + 1) % n]

                if p1[1] == p2[1]:
                    continue

                if p1[1] > p2[1]:
                    p1, p2 = p2, p1

                if p1[1] <= y < p2[1]:
                    x = p1[0] + (y - p1[1]) * (p2[0] - p1[0]) / (p2[1] - p1[1])
                    intersections.append(int(x))

            intersections.sort()

            for i in range(0, len(intersections) - 1, 2):
                x1 = max(0, intersections[i])
                x2 = min(self.width - 1, intersections[i + 1])
                for x in range(x1, x2 + 1):
                    self.set_pixel(x, y, color)

    # === Gradients ===

    def gradient_vertical(self, x: int, y: int, w: int, h: int,
                          top_color: Color, bottom_color: Color) -> None:
        """Fill rectangle with vertical gradient."""
        for py in range(max(0, y), min(self.height, y + h)):
            t = (py - y) / max(h - 1, 1)
            color = lerp_color(top_color, bottom_color, t)
            for px in range(max(0, x), min(self.width, x + w)):
                self.set_pixel(px, py, color)

    def gradient_radial(self, cx: int, cy: int, r: int,
                        center_color: Color, edge_color: Color) -> None:
        """Fill circle with radial gradient."""
        for py in range(max(0, cy - r), min(self.height, cy + r + 1)):
            for px in range(max(0, cx - r), min(self.width, cx + r + 1)):
                dist = math.sqrt((px - cx) ** 2 + (py - cy) ** 2)
                if dist <= r:
                    t = dist / r
                    color = lerp_color(center_color, edge_color, t)
                    self.set_pixel(px, py, color)

    # === Sprite Operations ===

    def blit(self, other: 'Canvas', x: int, y: int) -> None:
        """Draw another canvas onto this one at position (x, y)."""
        for py in range(other.height):
            for px in range(other.width):
                color = other.get_pixel(px, py)
                if color and color[3] > 0:
                    self.set_pixel(x + px, y + py, color)

    def blit_rotated(self, other: 'Canvas', x: int, y: int, angle: float) -> None:
        """Draw another canvas rotated by angle (radians) around its center."""
        cos_a = math.cos(-angle)
        sin_a = math.sin(-angle)
        ocx, ocy = other.width / 2, other.height / 2

        for py in range(-other.height, other.height * 2):
            for px in range(-other.width, other.width * 2):
                # Rotate point back to source coordinates
                rx = (px - ocx) * cos_a - (py - ocy) * sin_a + ocx
                ry = (px - ocx) * sin_a + (py - ocy) * cos_a + ocy

                if 0 <= rx < other.width and 0 <= ry < other.height:
                    color = other.get_pixel(int(rx), int(ry))
                    if color and color[3] > 0:
                        self.set_pixel(x + px, y + py, color)

    def flip_horizontal(self) -> 'Canvas':
        """Return a horizontally flipped copy."""
        flipped = Canvas(self.width, self.height)
        for y in range(self.height):
            for x in range(self.width):
                flipped.set_pixel_solid(self.width - 1 - x, y, self.pixels[y][x])
        return flipped

    def flip_vertical(self) -> 'Canvas':
        """Return a vertically flipped copy."""
        flipped = Canvas(self.width, self.height)
        for y in range(self.height):
            for x in range(self.width):
                flipped.set_pixel_solid(x, self.height - 1 - y, self.pixels[y][x])
        return flipped

    def scale(self, factor: int) -> 'Canvas':
        """Return a scaled copy (nearest neighbor)."""
        scaled = Canvas(self.width * factor, self.height * factor)
        for y in range(self.height):
            for x in range(self.width):
                color = self.pixels[y][x]
                for dy in range(factor):
                    for dx in range(factor):
                        scaled.set_pixel_solid(x * factor + dx, y * factor + dy, color)
        return scaled

    # === Output ===

    def save(self, filepath: str) -> None:
        """Save canvas to PNG file."""
        save_png(filepath, self.width, self.height, self.pixels)

    def to_bytes(self) -> bytes:
        """Get PNG as bytes."""
        return create_png(self.width, self.height, self.pixels)

    def copy(self) -> 'Canvas':
        """Create a copy of this canvas."""
        new_canvas = Canvas(self.width, self.height)
        for y in range(self.height):
            for x in range(self.width):
                new_canvas.pixels[y][x] = self.pixels[y][x]
        return new_canvas

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
        r_sq = r * r
        y_start = max(0, cy - r)
        y_end = min(self.height, cy + r + 1)
        x_start = max(0, cx - r)
        x_end = min(self.width, cx + r + 1)

        for py in range(y_start, y_end):
            dy_sq = (py - cy) ** 2
            for px in range(x_start, x_end):
                if (px - cx) ** 2 + dy_sq <= r_sq:
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
        """Fill an ellipse.

        Uses integer math for performance: compares (dx*ry)^2 + (dy*rx)^2 <= (rx*ry)^2
        """
        if rx <= 0 or ry <= 0:
            return

        # Precompute squared values for integer comparison
        rx_sq = rx * rx
        ry_sq = ry * ry
        threshold = rx_sq * ry_sq

        y_start = max(0, cy - ry)
        y_end = min(self.height, cy + ry + 1)
        x_start = max(0, cx - rx)
        x_end = min(self.width, cx + rx + 1)

        for py in range(y_start, y_end):
            dy = py - cy
            dy_term = dy * dy * rx_sq
            for px in range(x_start, x_end):
                dx = px - cx
                if dx * dx * ry_sq + dy_term <= threshold:
                    self.set_pixel(px, py, color)

    # === Anti-Aliased Shapes ===

    def fill_circle_aa(self, cx: int, cy: int, r: int, color: Color) -> None:
        """Fill a circle with anti-aliased edges.

        Uses distance-based coverage calculation for smooth edges.
        """
        for py in range(max(0, cy - r - 1), min(self.height, cy + r + 2)):
            for px in range(max(0, cx - r - 1), min(self.width, cx + r + 2)):
                dist = math.sqrt((px - cx) ** 2 + (py - cy) ** 2)
                if dist <= r - 0.5:
                    # Fully inside
                    self.set_pixel(px, py, color)
                elif dist <= r + 0.5:
                    # Edge pixel - calculate coverage
                    coverage = 1.0 - (dist - r + 0.5)
                    coverage = max(0.0, min(1.0, coverage))
                    alpha = int(color[3] * coverage)
                    if alpha > 0:  # Skip fully transparent pixels
                        aa_color = (color[0], color[1], color[2], alpha)
                        self.set_pixel(px, py, aa_color)

    def fill_ellipse_aa(self, cx: int, cy: int, rx: int, ry: int, color: Color) -> None:
        """Fill an ellipse with anti-aliased edges.

        Uses normalized distance for smooth edges.
        """
        if rx <= 0 or ry <= 0:
            return

        for py in range(max(0, cy - ry - 1), min(self.height, cy + ry + 2)):
            for px in range(max(0, cx - rx - 1), min(self.width, cx + rx + 2)):
                dx = (px - cx) / rx
                dy = (py - cy) / ry
                dist = math.sqrt(dx * dx + dy * dy)

                if dist <= 0.95:
                    # Fully inside
                    self.set_pixel(px, py, color)
                elif dist <= 1.05:
                    # Edge pixel - calculate coverage
                    coverage = 1.0 - (dist - 0.95) / 0.1
                    coverage = max(0.0, min(1.0, coverage))
                    alpha = int(color[3] * coverage)
                    if alpha > 0:  # Skip fully transparent pixels
                        aa_color = (color[0], color[1], color[2], alpha)
                        self.set_pixel(px, py, aa_color)

    def draw_circle_aa(self, cx: int, cy: int, r: int, color: Color) -> None:
        """Draw circle outline with anti-aliasing.

        Uses distance-based coverage for smooth outline.
        """
        thickness = 1.0
        for py in range(max(0, cy - r - 2), min(self.height, cy + r + 3)):
            for px in range(max(0, cx - r - 2), min(self.width, cx + r + 3)):
                dist = math.sqrt((px - cx) ** 2 + (py - cy) ** 2)
                edge_dist = abs(dist - r)

                if edge_dist <= thickness:
                    # On the outline
                    coverage = 1.0 - edge_dist / thickness
                    coverage = max(0.0, min(1.0, coverage))
                    alpha = int(color[3] * coverage)
                    if alpha > 0:  # Skip fully transparent pixels
                        aa_color = (color[0], color[1], color[2], alpha)
                        self.set_pixel(px, py, aa_color)

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

    def draw_line_aa(self, x0: int, y0: int, x1: int, y1: int, color: Color) -> None:
        """Draw anti-aliased line using Wu's algorithm.

        Produces smooth lines with subpixel precision.
        """
        def plot(x: int, y: int, brightness: float) -> None:
            if brightness <= 0:
                return
            brightness = min(1.0, brightness)
            alpha = int(color[3] * brightness)
            if alpha > 0:  # Skip fully transparent pixels
                aa_color = (color[0], color[1], color[2], alpha)
                self.set_pixel(x, y, aa_color)

        def fpart(x: float) -> float:
            return x - int(x)

        def rfpart(x: float) -> float:
            return 1.0 - fpart(x)

        steep = abs(y1 - y0) > abs(x1 - x0)

        if steep:
            x0, y0 = y0, x0
            x1, y1 = y1, x1

        if x0 > x1:
            x0, x1 = x1, x0
            y0, y1 = y1, y0

        dx = x1 - x0
        dy = y1 - y0
        gradient = dy / dx if dx != 0 else 1.0

        # Handle first endpoint
        xend = round(x0)
        yend = y0 + gradient * (xend - x0)
        xgap = rfpart(x0 + 0.5)
        xpxl1 = xend
        ypxl1 = int(yend)

        if steep:
            plot(ypxl1, xpxl1, rfpart(yend) * xgap)
            plot(ypxl1 + 1, xpxl1, fpart(yend) * xgap)
        else:
            plot(xpxl1, ypxl1, rfpart(yend) * xgap)
            plot(xpxl1, ypxl1 + 1, fpart(yend) * xgap)

        intery = yend + gradient

        # Handle second endpoint
        xend = round(x1)
        yend = y1 + gradient * (xend - x1)
        xgap = fpart(x1 + 0.5)
        xpxl2 = xend
        ypxl2 = int(yend)

        if steep:
            plot(ypxl2, xpxl2, rfpart(yend) * xgap)
            plot(ypxl2 + 1, xpxl2, fpart(yend) * xgap)
        else:
            plot(xpxl2, ypxl2, rfpart(yend) * xgap)
            plot(xpxl2, ypxl2 + 1, fpart(yend) * xgap)

        # Main loop
        if steep:
            for x in range(xpxl1 + 1, xpxl2):
                plot(int(intery), x, rfpart(intery))
                plot(int(intery) + 1, x, fpart(intery))
                intery += gradient
        else:
            for x in range(xpxl1 + 1, xpxl2):
                plot(x, int(intery), rfpart(intery))
                plot(x, int(intery) + 1, fpart(intery))
                intery += gradient

    # === Bezier Curves ===

    def _bezier_quadratic(self, t: float, p0: Tuple[float, float],
                          p1: Tuple[float, float], p2: Tuple[float, float]) -> Tuple[float, float]:
        """Evaluate quadratic bezier curve at parameter t (0-1)."""
        x = (1-t)**2 * p0[0] + 2*(1-t)*t * p1[0] + t**2 * p2[0]
        y = (1-t)**2 * p0[1] + 2*(1-t)*t * p1[1] + t**2 * p2[1]
        return (x, y)

    def _bezier_cubic(self, t: float, p0: Tuple[float, float], p1: Tuple[float, float],
                      p2: Tuple[float, float], p3: Tuple[float, float]) -> Tuple[float, float]:
        """Evaluate cubic bezier curve at parameter t (0-1)."""
        x = (1-t)**3 * p0[0] + 3*(1-t)**2*t * p1[0] + 3*(1-t)*t**2 * p2[0] + t**3 * p3[0]
        y = (1-t)**3 * p0[1] + 3*(1-t)**2*t * p1[1] + 3*(1-t)*t**2 * p2[1] + t**3 * p3[1]
        return (x, y)

    def draw_bezier(self, points: List[Tuple[float, float]], color: Color,
                    thickness: int = 1, segments: int = 20) -> None:
        """Draw a bezier curve.

        Args:
            points: Control points (3 for quadratic, 4 for cubic)
            color: Line color
            thickness: Line thickness
            segments: Number of line segments to approximate curve
        """
        if len(points) < 3:
            return

        prev_point = None
        for i in range(segments + 1):
            t = i / segments
            if len(points) == 3:
                pt = self._bezier_quadratic(t, points[0], points[1], points[2])
            else:
                pt = self._bezier_cubic(t, points[0], points[1], points[2], points[3])

            if prev_point is not None:
                self.draw_line(int(prev_point[0]), int(prev_point[1]),
                              int(pt[0]), int(pt[1]), color, thickness)
            prev_point = pt

    def draw_bezier_aa(self, points: List[Tuple[float, float]], color: Color,
                       segments: int = 30) -> None:
        """Draw an anti-aliased bezier curve.

        Args:
            points: Control points (3 for quadratic, 4 for cubic)
            color: Line color
            segments: Number of line segments to approximate curve
        """
        if len(points) < 3:
            return

        prev_point = None
        for i in range(segments + 1):
            t = i / segments
            if len(points) == 3:
                pt = self._bezier_quadratic(t, points[0], points[1], points[2])
            else:
                pt = self._bezier_cubic(t, points[0], points[1], points[2], points[3])

            if prev_point is not None:
                self.draw_line_aa(int(prev_point[0]), int(prev_point[1]),
                                 int(pt[0]), int(pt[1]), color)
            prev_point = pt

    def draw_bezier_tapered(self, points: List[Tuple[float, float]], color: Color,
                            start_thickness: float = 2.0, end_thickness: float = 0.5,
                            segments: int = 25) -> None:
        """Draw a bezier curve with tapered thickness (for hair strands).

        Args:
            points: Control points (3 for quadratic, 4 for cubic)
            color: Line color
            start_thickness: Thickness at start of curve
            end_thickness: Thickness at end of curve
            segments: Number of line segments
        """
        if len(points) < 3:
            return

        prev_point = None
        for i in range(segments + 1):
            t = i / segments
            if len(points) == 3:
                pt = self._bezier_quadratic(t, points[0], points[1], points[2])
            else:
                pt = self._bezier_cubic(t, points[0], points[1], points[2], points[3])

            if prev_point is not None:
                # Interpolate thickness
                thickness = int(start_thickness + (end_thickness - start_thickness) * t)
                thickness = max(1, thickness)
                self.draw_line(int(prev_point[0]), int(prev_point[1]),
                              int(pt[0]), int(pt[1]), color, thickness)
            prev_point = pt

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

    def fill_ellipse_gradient(self, cx: int, cy: int, rx: int, ry: int,
                              color1: Color, color2: Color, angle: float = 0) -> None:
        """Fill ellipse with directional gradient.

        Args:
            cx, cy: Center position
            rx, ry: X and Y radii
            color1: Start color (at angle direction)
            color2: End color (opposite angle direction)
            angle: Gradient direction in degrees (0 = left-to-right)
        """
        rad = math.radians(angle)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)

        for py in range(max(0, cy - ry), min(self.height, cy + ry + 1)):
            for px in range(max(0, cx - rx), min(self.width, cx + rx + 1)):
                # Check if point is inside ellipse
                nx = (px - cx) / max(rx, 1)
                ny = (py - cy) / max(ry, 1)
                if nx*nx + ny*ny <= 1.0:
                    # Calculate gradient parameter based on angle
                    # Project point onto gradient direction
                    proj = (px - cx) * cos_a + (py - cy) * sin_a
                    max_proj = rx * abs(cos_a) + ry * abs(sin_a)
                    t = (proj / max_proj + 1) / 2  # Normalize to 0-1
                    t = max(0.0, min(1.0, t))
                    color = lerp_color(color1, color2, t)
                    self.set_pixel(px, py, color)

    def fill_ellipse_radial_gradient(self, cx: int, cy: int, rx: int, ry: int,
                                      center_color: Color, edge_color: Color) -> None:
        """Fill ellipse with radial gradient (center to edge).

        Args:
            cx, cy: Center position
            rx, ry: X and Y radii
            center_color: Color at center
            edge_color: Color at edge
        """
        for py in range(max(0, cy - ry), min(self.height, cy + ry + 1)):
            for px in range(max(0, cx - rx), min(self.width, cx + rx + 1)):
                # Normalized distance from center
                nx = (px - cx) / max(rx, 1)
                ny = (py - cy) / max(ry, 1)
                dist_sq = nx*nx + ny*ny
                if dist_sq <= 1.0:
                    t = math.sqrt(dist_sq)  # 0 at center, 1 at edge
                    color = lerp_color(center_color, edge_color, t)
                    self.set_pixel(px, py, color)

    def fill_ellipse_dithered(self, cx: int, cy: int, rx: int, ry: int,
                              color1: Color, color2: Color,
                              dither_size: int = 4) -> None:
        """Fill ellipse with dithered color transition (center to edge).

        Uses ordered dithering for smooth color transitions without banding.

        Args:
            cx, cy: Center position
            rx, ry: X and Y radii
            color1: Color at center
            color2: Color at edge
            dither_size: Dither pattern size (2, 4, or 8)
        """
        # Bayer dither matrices
        bayer_2x2 = [[0, 2], [3, 1]]
        bayer_4x4 = [
            [0, 8, 2, 10],
            [12, 4, 14, 6],
            [3, 11, 1, 9],
            [15, 7, 13, 5]
        ]
        bayer_8x8 = [
            [0, 32, 8, 40, 2, 34, 10, 42],
            [48, 16, 56, 24, 50, 18, 58, 26],
            [12, 44, 4, 36, 14, 46, 6, 38],
            [60, 28, 52, 20, 62, 30, 54, 22],
            [3, 35, 11, 43, 1, 33, 9, 41],
            [51, 19, 59, 27, 49, 17, 57, 25],
            [15, 47, 7, 39, 13, 45, 5, 37],
            [63, 31, 55, 23, 61, 29, 53, 21]
        ]

        if dither_size == 2:
            matrix = bayer_2x2
            divisor = 4
        elif dither_size == 8:
            matrix = bayer_8x8
            divisor = 64
        else:
            matrix = bayer_4x4
            divisor = 16

        size = len(matrix)

        for py in range(max(0, cy - ry), min(self.height, cy + ry + 1)):
            for px in range(max(0, cx - rx), min(self.width, cx + rx + 1)):
                # Normalized distance from center
                nx = (px - cx) / max(rx, 1)
                ny = (py - cy) / max(ry, 1)
                dist_sq = nx*nx + ny*ny
                if dist_sq <= 1.0:
                    t = math.sqrt(dist_sq)  # 0 at center, 1 at edge

                    # Apply dithering threshold
                    threshold = matrix[py % size][px % size] / divisor
                    if t < threshold:
                        self.set_pixel(px, py, color1)
                    else:
                        self.set_pixel(px, py, color2)

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

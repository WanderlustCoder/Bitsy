"""Triangle rasterization for projected 3D models."""

import math
from typing import List, Tuple

from core import Canvas
from core.png_writer import Color

Vec2 = Tuple[float, float]
Face = Tuple[int, int, int]


def _edge(ax: float, ay: float, bx: float, by: float, px: float, py: float) -> float:
    return (px - ax) * (by - ay) - (py - ay) * (bx - ax)


def rasterize_triangles(
    canvas: Canvas,
    vertices: List[Vec2],
    faces: List[Face],
    colors: List[Color],
    depths: List[float],
) -> None:
    """Rasterize triangles onto a canvas using a depth buffer."""
    width = canvas.width
    height = canvas.height
    zbuffer = [[math.inf for _ in range(width)] for _ in range(height)]

    for face, color in zip(faces, colors):
        i0, i1, i2 = face
        x0, y0 = vertices[i0]
        x1, y1 = vertices[i1]
        x2, y2 = vertices[i2]
        d0 = depths[i0]
        d1 = depths[i1]
        d2 = depths[i2]

        area = _edge(x0, y0, x1, y1, x2, y2)
        if area == 0:
            continue
        inv_area = 1.0 / area

        min_x = max(0, int(math.floor(min(x0, x1, x2))))
        max_x = min(width - 1, int(math.ceil(max(x0, x1, x2))))
        min_y = max(0, int(math.floor(min(y0, y1, y2))))
        max_y = min(height - 1, int(math.ceil(max(y0, y1, y2))))

        for py in range(min_y, max_y + 1):
            for px in range(min_x, max_x + 1):
                sample_x = px + 0.5
                sample_y = py + 0.5

                w0 = _edge(x1, y1, x2, y2, sample_x, sample_y)
                w1 = _edge(x2, y2, x0, y0, sample_x, sample_y)
                w2 = _edge(x0, y0, x1, y1, sample_x, sample_y)

                if (w0 >= 0 and w1 >= 0 and w2 >= 0) or (w0 <= 0 and w1 <= 0 and w2 <= 0):
                    w0 *= inv_area
                    w1 *= inv_area
                    w2 *= inv_area
                    depth = d0 * w0 + d1 * w1 + d2 * w2
                    if depth < zbuffer[py][px]:
                        zbuffer[py][px] = depth
                        canvas.set_pixel_solid(px, py, color)

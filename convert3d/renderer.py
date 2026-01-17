"""High-level rendering pipeline for 3D to pixel art sprites."""

import math
from typing import Iterable, List, Optional, Tuple, Union

from core import Canvas, Palette
from core.png_writer import Color

from .obj_parser import Model
from .projection import project_vertices
from .rasterizer import rasterize_triangles

Vec3 = Tuple[float, float, float]


def _normalize(vec: Vec3) -> Vec3:
    length = math.sqrt(vec[0] ** 2 + vec[1] ** 2 + vec[2] ** 2)
    if length == 0:
        return (0.0, 0.0, 0.0)
    return (vec[0] / length, vec[1] / length, vec[2] / length)


def _dot(a: Vec3, b: Vec3) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _sub(a: Vec3, b: Vec3) -> Vec3:
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _cross(a: Vec3, b: Vec3) -> Vec3:
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def _lerp_color(c1: Color, c2: Color, t: float) -> Color:
    t = max(0.0, min(1.0, t))
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t),
        int(c1[3] + (c2[3] - c1[3]) * t),
    )


def _coerce_palette(palette: Optional[Union[Palette, Iterable[Color]]]) -> Palette:
    if palette is None:
        return Palette([
            (30, 30, 30, 255),
            (90, 90, 90, 255),
            (160, 160, 160, 255),
            (230, 230, 230, 255),
        ], name="Default3D")
    if isinstance(palette, Palette):
        return palette
    return Palette(list(palette), name="Custom")


def _project_to_screen(
    points: List[Tuple[float, float]],
    width: int,
    height: int,
    padding: float = 1.0,
) -> List[Tuple[float, float]]:
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]

    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    span_x = max_x - min_x
    span_y = max_y - min_y

    if span_x == 0:
        scale_x = 1.0
    else:
        scale_x = (width - 2 * padding) / span_x
    if span_y == 0:
        scale_y = 1.0
    else:
        scale_y = (height - 2 * padding) / span_y

    scale = min(scale_x, scale_y)
    if scale <= 0:
        scale = 1.0

    offset_x = (width - span_x * scale) / 2 - min_x * scale
    offset_y = (height - span_y * scale) / 2 + max_y * scale

    result: List[Tuple[float, float]] = []
    for x, y in points:
        screen_x = x * scale + offset_x
        screen_y = -y * scale + offset_y
        result.append((screen_x, screen_y))

    return result


def _shade_face(normal: Vec3, light_dir: Vec3, palette: Palette) -> Color:
    intensity = max(0.0, _dot(normal, light_dir))
    shade = 0.2 + 0.8 * intensity
    shaded = _lerp_color((40, 40, 40, 255), (220, 220, 220, 255), shade)
    return palette.quantize(shaded)


def _apply_outline(canvas: Canvas, outline_color: Color) -> None:
    width = canvas.width
    height = canvas.height
    outline_pixels: List[Tuple[int, int]] = []

    for y in range(height):
        for x in range(width):
            color = canvas.get_pixel(x, y)
            if not color or color[3] == 0:
                continue
            if (
                (x > 0 and canvas.get_pixel(x - 1, y)[3] == 0) or
                (x < width - 1 and canvas.get_pixel(x + 1, y)[3] == 0) or
                (y > 0 and canvas.get_pixel(x, y - 1)[3] == 0) or
                (y < height - 1 and canvas.get_pixel(x, y + 1)[3] == 0)
            ):
                outline_pixels.append((x, y))

    for x, y in outline_pixels:
        canvas.set_pixel_solid(x, y, outline_color)


def render_sprite(
    model: Model,
    width: int,
    height: int,
    projection: str = "isometric",
    view: str = "front",
    light_direction: Vec3 = (1, 1, 1),
    outline: bool = True,
    palette: Optional[Union[Palette, Iterable[Color]]] = None,
) -> Canvas:
    """Render a 3D model into a pixel art sprite."""
    if width <= 0 or height <= 0:
        raise ValueError("Width and height must be positive")

    palette_obj = _coerce_palette(palette)
    projected, depths = project_vertices(model.vertices, projection=projection, view=view)
    screen_vertices = _project_to_screen(projected, width, height, padding=1.0)

    light_dir = _normalize(light_direction)
    face_colors: List[Color] = []
    for face in model.faces:
        v0 = model.vertices[face[0]]
        v1 = model.vertices[face[1]]
        v2 = model.vertices[face[2]]
        normal = _normalize(_cross(_sub(v1, v0), _sub(v2, v0)))
        face_colors.append(_shade_face(normal, light_dir, palette_obj))

    canvas = Canvas(width, height)
    rasterize_triangles(canvas, screen_vertices, model.faces, face_colors, depths)

    if outline:
        outline_color = palette_obj.quantize((0, 0, 0, 255))
        _apply_outline(canvas, outline_color)

    return canvas

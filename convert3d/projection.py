"""Projection helpers for 3D to 2D conversion."""

import math
from typing import List, Tuple

Vec3 = Tuple[float, float, float]
Vec2 = Tuple[float, float]


def orthographic_projection(vertices: List[Vec3], view: str = "front") -> Tuple[List[Vec2], List[float]]:
    """Project vertices using orthographic projection.

    Views:
        front: x/y plane, depth = z
        side: z/y plane, depth = x
        top: x/z plane, depth = y
    """
    projected: List[Vec2] = []
    depths: List[float] = []

    view = view.lower()
    for x, y, z in vertices:
        if view == "front":
            projected.append((x, y))
            depths.append(z)
        elif view == "side":
            projected.append((z, y))
            depths.append(x)
        elif view == "top":
            projected.append((x, z))
            depths.append(y)
        else:
            raise ValueError(f"Unknown orthographic view: {view}")

    return projected, depths


def isometric_projection(vertices: List[Vec3]) -> Tuple[List[Vec2], List[float]]:
    """Project vertices using classic isometric projection."""
    projected: List[Vec2] = []
    depths: List[float] = []

    cos_y = math.cos(math.radians(45))
    sin_y = math.sin(math.radians(45))
    cos_x = math.cos(math.radians(35.2643897))
    sin_x = math.sin(math.radians(35.2643897))

    for x, y, z in vertices:
        x1 = x * cos_y - z * sin_y
        z1 = x * sin_y + z * cos_y
        y1 = y

        y2 = y1 * cos_x - z1 * sin_x
        z2 = y1 * sin_x + z1 * cos_x
        x2 = x1

        projected.append((x2, y2))
        depths.append(z2)

    return projected, depths


def project_vertices(vertices: List[Vec3], projection: str = "orthographic", view: str = "front") -> Tuple[List[Vec2], List[float]]:
    """Project vertices based on projection type."""
    projection = projection.lower()
    if projection == "orthographic":
        return orthographic_projection(vertices, view=view)
    if projection == "isometric":
        return isometric_projection(vertices)
    raise ValueError(f"Unknown projection: {projection}")

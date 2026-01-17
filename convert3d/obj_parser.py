"""
OBJ parser for simple 3D models (vertices and faces only).
"""

from dataclasses import dataclass
from typing import Iterable, List, Tuple

Vec3 = Tuple[float, float, float]
Face = Tuple[int, int, int]


@dataclass
class Model:
    """Simple 3D model with vertices and triangle faces."""

    vertices: List[Vec3]
    faces: List[Face]


def _parse_vertex(parts: List[str]) -> Vec3:
    if len(parts) < 4:
        raise ValueError(f"Invalid vertex line: {' '.join(parts)}")
    return (float(parts[1]), float(parts[2]), float(parts[3]))


def _parse_face(parts: List[str], vertex_count: int) -> List[Face]:
    if len(parts) < 4:
        raise ValueError(f"Invalid face line: {' '.join(parts)}")

    indices: List[int] = []
    for token in parts[1:]:
        value = token.split('/')[0]
        if not value:
            raise ValueError(f"Invalid face token: {token}")
        idx = int(value)
        if idx < 0:
            idx = vertex_count + idx
        else:
            idx = idx - 1
        if idx < 0 or idx >= vertex_count:
            raise ValueError(f"Face index out of range: {token}")
        indices.append(idx)

    faces: List[Face] = []
    v0 = indices[0]
    for i in range(1, len(indices) - 1):
        faces.append((v0, indices[i], indices[i + 1]))
    return faces


def parse_obj_lines(lines: Iterable[str]) -> Model:
    """Parse OBJ content from an iterable of lines."""
    vertices: List[Vec3] = []
    faces: List[Face] = []

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        parts = stripped.split()
        if parts[0] == 'v':
            vertices.append(_parse_vertex(parts))
        elif parts[0] == 'f':
            faces.extend(_parse_face(parts, len(vertices)))

    if not vertices or not faces:
        raise ValueError("OBJ must contain vertices and faces")

    return Model(vertices=vertices, faces=faces)


def load_obj(path: str) -> Model:
    """Load and parse a .obj file from disk."""
    with open(path, 'r', encoding='utf-8') as handle:
        return parse_obj_lines(handle)

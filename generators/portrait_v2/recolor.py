"""Recoloring utilities for portrait_v2."""

from typing import List, Tuple, Optional


PLACEHOLDER_PALETTE = {
    "base": (255, 0, 0, 255),
    "shadow1": (200, 0, 0, 255),
    "shadow2": (150, 0, 0, 255),
    "highlight1": (255, 100, 100, 255),
    "highlight2": (255, 180, 180, 255),
    "outline": (100, 0, 0, 255),
    "secondary": (0, 255, 0, 255),
}

PLACEHOLDER_LIST = [
    (255, 0, 0, 255),
    (200, 0, 0, 255),
    (150, 0, 0, 255),
    (255, 100, 100, 255),
    (255, 180, 180, 255),
    (100, 0, 0, 255),
    (0, 255, 0, 255),
]


def color_distance(c1: Tuple[int, ...], c2: Tuple[int, ...]) -> int:
    """Calculate squared RGB distance between colors."""
    return sum((a - b) ** 2 for a, b in zip(c1[:3], c2[:3]))


def find_placeholder_index(
    color: Tuple[int, int, int, int],
    threshold: int = 100
) -> Optional[int]:
    """Find the placeholder index for a color, or None if no match."""
    if color[3] < 32:
        return None

    for i, placeholder in enumerate(PLACEHOLDER_LIST):
        if color_distance(color, placeholder) < threshold:
            return i
    return None


def recolor_template(
    pixels: List[List[Tuple[int, int, int, int]]],
    target_palette: List[Tuple[int, int, int, int]],
    secondary_palette: Optional[List[Tuple[int, int, int, int]]] = None
) -> List[List[Tuple[int, int, int, int]]]:
    """Recolor a template by swapping placeholder colors with target palette."""
    height = len(pixels)
    width = len(pixels[0]) if height > 0 else 0

    result = []
    for y in range(height):
        row = []
        for x in range(width):
            color = pixels[y][x]

            if color[3] < 32:
                row.append(color)
                continue

            idx = find_placeholder_index(color)
            if idx is not None:
                if idx == 6 and secondary_palette:
                    new_color = secondary_palette[0]
                elif idx < len(target_palette):
                    new_color = target_palette[idx]
                else:
                    new_color = color
                row.append((new_color[0], new_color[1], new_color[2], color[3]))
            else:
                row.append(color)
        result.append(row)

    return result


def create_skin_palette(
    base_color: Tuple[int, int, int],
    use_hue_shift: bool = True
) -> List[Tuple[int, int, int, int]]:
    """Create a 6-color skin palette from a base color."""
    r, g, b = base_color

    if use_hue_shift:
        shadow1 = (int(r * 0.82), int(g * 0.78), int(b * 0.85), 255)
        shadow2 = (int(r * 0.65), int(g * 0.58), int(b * 0.68), 255)
        highlight1 = (
            min(255, int(r * 1.08)),
            min(255, int(g * 1.05)),
            min(255, int(b * 0.98)),
            255,
        )
        highlight2 = (
            min(255, int(r * 1.15)),
            min(255, int(g * 1.12)),
            min(255, int(b * 1.02)),
            255,
        )
    else:
        shadow1 = (int(r * 0.8), int(g * 0.8), int(b * 0.8), 255)
        shadow2 = (int(r * 0.6), int(g * 0.6), int(b * 0.6), 255)
        highlight1 = (
            min(255, int(r * 1.1)),
            min(255, int(g * 1.1)),
            min(255, int(b * 1.1)),
            255,
        )
        highlight2 = (
            min(255, int(r * 1.2)),
            min(255, int(g * 1.2)),
            min(255, int(b * 1.2)),
            255,
        )

    outline = (int(r * 0.4), int(g * 0.35), int(b * 0.4), 255)

    return [
        (r, g, b, 255),
        shadow1,
        shadow2,
        highlight1,
        highlight2,
        outline,
    ]

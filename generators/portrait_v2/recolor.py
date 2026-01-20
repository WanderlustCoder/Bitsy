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
    "rim": (255, 150, 200, 255),  # Rim/edge light
    "highlight_soft": (255, 50, 50, 255),  # Soft highlight
}

PLACEHOLDER_LIST = [
    (255, 0, 0, 255),        # 0: base
    (200, 0, 0, 255),        # 1: shadow1 (mid)
    (150, 0, 0, 255),        # 2: shadow2 (dark)
    (255, 100, 100, 255),    # 3: highlight1 (bright)
    (255, 180, 180, 255),    # 4: highlight2 (very bright)
    (100, 0, 0, 255),        # 5: outline (darkest)
    (0, 255, 0, 255),        # 6: secondary color
    (255, 150, 200, 255),    # 7: rim light
    (255, 50, 50, 255),      # 8: soft highlight
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
    """Create a 9-color skin palette from a base color.

    Uses warm-to-cool hue shifting for anime-style shading:
    - Shadows shift toward cool purple/red
    - Highlights shift toward warm yellow/orange
    """
    r, g, b = base_color

    if use_hue_shift:
        # Based on reference pixel analysis: extremely uniform skin
        # Reference shows almost no visible shading at 64x96 scale
        # All skin pixels cluster around (253,181,115) ± 2
        shadow1 = (
            int(r * 0.96),           # Very subtle
            int(g * 0.94),           # Minimal variation
            int(b * 0.95),           # Keep uniformity
            255
        )
        shadow2 = (
            int(r * 0.90),           # Still subtle
            int(g * 0.85),           # Slightly more contrast
            int(b * 0.88),           # Warm
            255
        )
        # Highlights: minimal, almost same as base
        highlight1 = (
            min(255, int(r * 1.01)),
            min(255, int(g * 1.02)),
            min(255, int(b * 0.99)),
            255,
        )
        highlight2 = (
            min(255, int(r * 1.02)),
            min(255, int(g * 1.03)),
            min(255, int(b * 0.98)),
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

    # Outline: deep warm shadow
    outline = (int(r * 0.45), int(g * 0.32), int(b * 0.38), 255)

    # Rim light - cool blue/purple tint for anime style
    rim = (
        min(255, int(r * 0.65 + 70)),
        min(255, int(g * 0.60 + 85)),
        min(255, int(b * 0.75 + 110)),
        255,
    )

    # Soft highlight - subtle warm
    highlight_soft = (
        min(255, int(r * 1.03)),
        min(255, int(g * 1.04)),
        min(255, int(b * 0.96)),
        255,
    )

    return [
        (r, g, b, 255),    # 0: base
        shadow1,           # 1: shadow1
        shadow2,           # 2: shadow2
        highlight1,        # 3: highlight1
        highlight2,        # 4: highlight2
        outline,           # 5: outline
        (r, g, b, 255),    # 6: secondary (placeholder)
        rim,               # 7: rim light
        highlight_soft,    # 8: soft highlight
    ]


def create_hair_palette(
    base_color: Tuple[int, int, int],
    rim_color: Optional[Tuple[int, int, int]] = None,
    use_hue_shift: bool = True
) -> List[Tuple[int, int, int, int]]:
    """Create a 9-color hair palette with rim lighting support."""
    r, g, b = base_color

    if use_hue_shift:
        # Shadows shift toward cooler/more saturated
        shadow1 = (int(r * 0.75), int(g * 0.70), int(b * 0.80), 255)
        shadow2 = (int(r * 0.55), int(g * 0.48), int(b * 0.60), 255)
        outline = (int(r * 0.35), int(g * 0.28), int(b * 0.40), 255)
        # Highlights shift warmer
        highlight1 = (
            min(255, int(r * 1.15)),
            min(255, int(g * 1.10)),
            min(255, int(b * 1.05)),
            255,
        )
        highlight2 = (
            min(255, int(r * 1.30)),
            min(255, int(g * 1.25)),
            min(255, int(b * 1.15)),
            255,
        )
        highlight_soft = (
            min(255, int(r * 1.08)),
            min(255, int(g * 1.05)),
            min(255, int(b * 1.02)),
            255,
        )
    else:
        shadow1 = (int(r * 0.75), int(g * 0.75), int(b * 0.75), 255)
        shadow2 = (int(r * 0.55), int(g * 0.55), int(b * 0.55), 255)
        outline = (int(r * 0.35), int(g * 0.35), int(b * 0.35), 255)
        highlight1 = (
            min(255, int(r * 1.15)),
            min(255, int(g * 1.15)),
            min(255, int(b * 1.15)),
            255,
        )
        highlight2 = (
            min(255, int(r * 1.30)),
            min(255, int(g * 1.30)),
            min(255, int(b * 1.30)),
            255,
        )
        highlight_soft = (
            min(255, int(r * 1.08)),
            min(255, int(g * 1.08)),
            min(255, int(b * 1.08)),
            255,
        )

    # Rim light - cool blue/purple tint for anime style
    if rim_color:
        rim = (rim_color[0], rim_color[1], rim_color[2], 255)
    else:
        # Default: shift toward cool purple/blue
        rim = (
            min(255, int(r * 0.6 + 80)),
            min(255, int(g * 0.5 + 90)),
            min(255, int(b * 0.7 + 120)),
            255,
        )

    return [
        (r, g, b, 255),    # 0: base
        shadow1,           # 1: shadow1 (mid)
        shadow2,           # 2: shadow2 (dark)
        highlight1,        # 3: highlight1 (bright)
        highlight2,        # 4: highlight2 (very bright)
        outline,           # 5: outline (darkest)
        (r, g, b, 255),    # 6: secondary (placeholder)
        rim,               # 7: rim light
        highlight_soft,    # 8: soft highlight
    ]

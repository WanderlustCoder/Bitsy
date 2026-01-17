"""
Effect application tools.

Provides AI-accessible tools for applying visual effects to sprites.
"""

from typing import Optional, List, Dict, Any
import time

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from .definitions import tool
from .results import GenerationResult, ToolResult

from quality.auto_shade import (
    add_shadows,
    add_highlights,
    apply_cel_shading,
    smart_outline,
)
from quality.selout import apply_selout
from editor.palette_tools import remap_to_palette, create_palette_from_colors
from core import Color


# Built-in palettes (RGB tuples)
BUILTIN_PALETTES = {
    "gameboy": [
        (15, 56, 15), (48, 98, 48), (139, 172, 15), (155, 188, 15),
    ],
    "nes": [
        (0, 0, 0), (252, 252, 252), (188, 188, 188), (124, 124, 124),
        (252, 0, 0), (0, 168, 0), (0, 88, 248), (248, 184, 0),
    ],
    "pico8": [
        (0, 0, 0), (29, 43, 83), (126, 37, 83), (0, 135, 81),
        (171, 82, 54), (95, 87, 79), (194, 195, 199), (255, 241, 232),
        (255, 0, 77), (255, 163, 0), (255, 236, 39), (0, 228, 54),
        (41, 173, 255), (131, 118, 156), (255, 119, 168), (255, 204, 170),
    ],
    "grayscale": [
        (0, 0, 0), (64, 64, 64), (128, 128, 128), (192, 192, 192), (255, 255, 255),
    ],
    "sepia": [
        (44, 33, 24), (80, 60, 43), (120, 90, 65), (160, 130, 100), (200, 175, 145),
    ],
}


def get_palette(name: str):
    """Get a palette by name."""
    colors = BUILTIN_PALETTES.get(name.lower())
    if colors:
        return create_palette_from_colors([(r, g, b, 255) for r, g, b in colors])
    return None


def list_palettes():
    """List available palette names."""
    return list(BUILTIN_PALETTES.keys())


AVAILABLE_EFFECTS = [
    "outline",
    "selout",
    "shadow",
    "highlight",
    "cel_shading",
]


@tool(name="apply_effect", category="effects", tags=["post-processing"])
def apply_effect(
    sprite: GenerationResult,
    effect: str,
    intensity: float = 1.0,
    color: Optional[str] = None,
    **params,
) -> ToolResult:
    """Apply visual effect to sprite.

    Args:
        sprite: Source sprite to modify
        effect: Effect name (outline, selout, shadow, highlight, cel_shading)
        intensity: Effect intensity 0.0-1.0
        color: Optional color for effect
        **params: Additional effect-specific parameters

    Returns:
        ToolResult with modified sprite
    """
    start_time = time.time()

    try:
        canvas = sprite.canvas

        if effect == "outline":
            canvas = smart_outline(canvas)
        elif effect == "selout":
            canvas = apply_selout(canvas)
        elif effect == "shadow":
            canvas = add_shadows(canvas, intensity=intensity)
        elif effect == "highlight":
            canvas = add_highlights(canvas, intensity=intensity)
        elif effect == "cel_shading":
            canvas = apply_cel_shading(canvas, levels=int(3 + intensity * 2))
        else:
            return ToolResult.fail(f"Unknown effect: {effect}", "ValueError")

        result = GenerationResult(
            canvas=canvas,
            parameters={
                **sprite.parameters,
                "effect": effect,
                "intensity": intensity,
            },
            seed=sprite.seed,
            sprite_type=sprite.sprite_type,
            generator_name=f"apply_effect:{effect}",
            generation_time_ms=(time.time() - start_time) * 1000,
            metadata={**sprite.metadata, "effect_applied": effect},
        )
        return ToolResult.ok(result)

    except Exception as e:
        return ToolResult.fail(str(e), "EffectError")


@tool(name="apply_palette", category="effects", tags=["color"])
def apply_palette(
    sprite: GenerationResult,
    palette_name: str,
) -> ToolResult:
    """Apply palette to sprite.

    Args:
        sprite: Source sprite to modify
        palette_name: Name of palette to apply

    Returns:
        ToolResult with recolored sprite
    """
    start_time = time.time()

    try:
        palette = get_palette(palette_name)
        if palette is None:
            return ToolResult.fail(f"Unknown palette: {palette_name}", "ValueError")

        canvas = remap_to_palette(sprite.canvas, palette)

        result = GenerationResult(
            canvas=canvas,
            parameters={
                **sprite.parameters,
                "palette": palette_name,
            },
            seed=sprite.seed,
            sprite_type=sprite.sprite_type,
            generator_name="apply_palette",
            generation_time_ms=(time.time() - start_time) * 1000,
            metadata={**sprite.metadata, "palette_applied": palette_name},
        )
        return ToolResult.ok(result)

    except Exception as e:
        return ToolResult.fail(str(e), "PaletteError")


@tool(name="list_effects", category="info", tags=["effects"])
def list_effects() -> List[str]:
    """List available visual effects.

    Returns:
        List of effect names
    """
    return AVAILABLE_EFFECTS.copy()


@tool(name="list_palettes", category="info", tags=["color"])
def get_available_palettes() -> List[str]:
    """List available palettes.

    Returns:
        List of palette names
    """
    return list_palettes()

"""
Export tools.

Provides AI-accessible tools for exporting sprites and animations.
"""

from typing import Optional, List
import time
import os

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from .definitions import tool
from .results import GenerationResult, AnimationResult, ToolResult

from export import (
    save_gif,
    save_apng,
    create_atlas,
    list_atlas_formats,
)
from export.png import save_png


@tool(name="export_sprite", category="export", tags=["file"])
def export_sprite(
    sprite: GenerationResult,
    path: str,
    format: str = "png",
) -> ToolResult:
    """Export sprite to file.

    Args:
        sprite: Sprite to export
        path: Output file path
        format: Export format (png)

    Returns:
        ToolResult with export path
    """
    start_time = time.time()

    try:
        if format.lower() == "png":
            save_png(sprite.canvas, path)
        else:
            return ToolResult.fail(f"Unsupported format: {format}", "ExportError")

        result = GenerationResult(
            canvas=sprite.canvas,
            parameters={**sprite.parameters, "export_path": path, "format": format},
            seed=sprite.seed,
            sprite_type=sprite.sprite_type,
            generator_name="export_sprite",
            generation_time_ms=(time.time() - start_time) * 1000,
            metadata={**sprite.metadata, "exported_to": path},
        )
        return ToolResult.ok(result)

    except Exception as e:
        return ToolResult.fail(str(e), "ExportError")


@tool(name="export_animation", category="export", tags=["file", "animation"])
def export_animation(
    animation: AnimationResult,
    path: str,
    format: str = "gif",
) -> ToolResult:
    """Export animation to file.

    Args:
        animation: Animation to export
        path: Output file path
        format: Export format (gif, apng)

    Returns:
        ToolResult with export path
    """
    start_time = time.time()

    try:
        if format.lower() == "gif":
            save_gif(path, animation.frames, animation.frame_delays)
        elif format.lower() == "apng":
            save_apng(path, animation.frames, fps=animation.fps)
        else:
            return ToolResult.fail(f"Unsupported format: {format}", "ExportError")

        # Return success with path info
        result = GenerationResult(
            canvas=animation.frames[0] if animation.frames else None,
            parameters={
                **animation.parameters,
                "export_path": path,
                "format": format,
            },
            seed=animation.seed,
            generator_name="export_animation",
            generation_time_ms=(time.time() - start_time) * 1000,
            metadata={"exported_to": path, "frame_count": len(animation.frames)},
        )
        return ToolResult.ok(result)

    except Exception as e:
        return ToolResult.fail(str(e), "ExportError")


@tool(name="export_atlas", category="export", tags=["file", "atlas"])
def export_atlas(
    sprites: List[GenerationResult],
    path: str,
    format: str = "json",
    max_size: int = 2048,
) -> ToolResult:
    """Export multiple sprites as texture atlas.

    Args:
        sprites: List of sprites to pack
        path: Output base path
        format: Metadata format (json, unity, godot, gamemaker)
        max_size: Maximum atlas dimension

    Returns:
        ToolResult with export paths
    """
    start_time = time.time()

    try:
        # Prepare sprites for atlas
        sprite_list = [
            (f"sprite_{i}", s.canvas)
            for i, s in enumerate(sprites)
        ]

        atlas = create_atlas(sprite_list, max_size=max_size)
        saved_files = atlas.save(path)

        result = GenerationResult(
            canvas=atlas.pages[0].canvas if atlas.pages else None,
            parameters={
                "sprite_count": len(sprites),
                "format": format,
                "max_size": max_size,
            },
            seed=0,
            generator_name="export_atlas",
            generation_time_ms=(time.time() - start_time) * 1000,
            metadata={"exported_files": saved_files},
        )
        return ToolResult.ok(result)

    except Exception as e:
        return ToolResult.fail(str(e), "ExportError")


@tool(name="list_export_formats", category="info", tags=["export"])
def get_export_formats() -> dict:
    """List available export formats.

    Returns:
        Dict of format categories and their options
    """
    return {
        "sprite": ["png"],
        "animation": ["gif", "apng"],
        "atlas": list_atlas_formats(),
    }

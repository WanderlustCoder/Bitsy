"""
Animation generation tools.

Provides AI-accessible tools for creating animations.
"""

from typing import Optional, List
import time
import random

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from .definitions import tool
from .results import GenerationResult, AnimationResult, ToolResult

from animation import (
    AnimationType,
    IdleStyle,
    generate_idle,
    generate_animation_set,
    list_animation_types,
    list_idle_styles,
    create_cycle,
    list_cycles,
)


@tool(name="create_animation", category="animation", tags=["animation"])
def create_animation(
    sprite: GenerationResult,
    animation_type: str = "idle",
    frames: int = 4,
    fps: int = 12,
    style: Optional[str] = None,
    seed: Optional[int] = None,
) -> ToolResult:
    """Create animation from a sprite.

    Args:
        sprite: Source sprite to animate
        animation_type: Animation type (idle, walk, run, attack, etc.)
        frames: Number of frames
        fps: Frames per second
        style: Animation style variant
        seed: Random seed for reproducibility

    Returns:
        ToolResult with animation
    """
    start_time = time.time()
    seed = seed or random.randint(0, 2**31)

    try:
        # Parse animation type
        try:
            anim_type = AnimationType(animation_type.lower())
        except ValueError:
            anim_type = AnimationType.IDLE

        # Generate based on type
        if anim_type == AnimationType.IDLE:
            idle_style = IdleStyle.SUBTLE
            if style:
                try:
                    idle_style = IdleStyle(style.lower())
                except ValueError:
                    pass

            cycle = generate_idle(
                sprite.canvas,
                frames=frames,
                style=idle_style,
                seed=seed,
            )
        else:
            # Use pre-built cycles for other types
            cycle_name = f"{animation_type}_{frames}frame"
            if cycle_name in list_cycles():
                cycle = create_cycle(cycle_name)
            else:
                # Fall back to idle
                cycle = generate_idle(sprite.canvas, frames=frames, seed=seed)

        # Convert cycle to frames
        animation_frames = cycle.frames if hasattr(cycle, 'frames') else [sprite.canvas] * frames
        frame_delays = [int(1000 / fps)] * len(animation_frames)

        result = AnimationResult(
            frames=animation_frames,
            frame_delays=frame_delays,
            parameters={
                "animation_type": animation_type,
                "frames": frames,
                "fps": fps,
                "style": style,
            },
            seed=seed,
            animation_type=animation_type,
            fps=fps,
        )
        return ToolResult.ok_animation(result)

    except Exception as e:
        return ToolResult.fail(str(e), "AnimationError")


@tool(name="create_animation_set", category="animation", tags=["animation"])
def create_animation_set(
    sprite: GenerationResult,
    types: List[str] = None,
    fps: int = 12,
    seed: Optional[int] = None,
) -> ToolResult:
    """Create a complete set of animations for a sprite.

    Args:
        sprite: Source sprite
        types: List of animation types to generate (default: idle, walk, attack)
        fps: Frames per second
        seed: Random seed

    Returns:
        ToolResult with animation set metadata
    """
    start_time = time.time()
    seed = seed or random.randint(0, 2**31)

    if types is None:
        types = ["idle", "walk", "attack"]

    try:
        anim_set = generate_animation_set(sprite.canvas, seed=seed)

        # Return first animation as result
        first_anim = anim_set.get(types[0]) if types else None

        if first_anim:
            result = AnimationResult(
                frames=first_anim.frames,
                frame_delays=[int(1000 / fps)] * len(first_anim.frames),
                parameters={"types": types, "fps": fps},
                seed=seed,
                animation_type="set",
                fps=fps,
                metadata={"animation_count": len(anim_set)},
            )
            return ToolResult.ok_animation(result)
        else:
            return ToolResult.fail("No animations generated", "AnimationError")

    except Exception as e:
        return ToolResult.fail(str(e), "AnimationError")


@tool(name="list_animation_types", category="info", tags=["animation"])
def get_animation_types() -> List[str]:
    """List available animation types.

    Returns:
        List of animation type names
    """
    return list_animation_types()


@tool(name="list_animation_cycles", category="info", tags=["animation"])
def get_animation_cycles() -> List[str]:
    """List available pre-built animation cycles.

    Returns:
        List of cycle names
    """
    return list_cycles()

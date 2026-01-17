"""
Scene generation tools.

Provides AI-accessible tools for generating scenes and backgrounds.
"""

from typing import Optional, List, Dict, Any
import time
import random

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from .definitions import tool
from .results import GenerationResult, ToolResult, SpriteType

from generators import (
    create_scene,
    generate_parallax_background,
    TimeOfDay,
    WeatherType,
    SceneConfig,
)
from generators import generate_parallax as _generate_parallax
from core import Canvas


@tool(name="generate_scene", category="generation", tags=["scene", "environment"])
def generate_scene(
    description: str,
    width: int = 320,
    height: int = 180,
    time_of_day: str = "noon",
    weather: str = "clear",
    seed: Optional[int] = None,
) -> ToolResult:
    """Generate a scene/environment from description."""
    start_time = time.time()
    seed = seed or random.randint(0, 2**31)

    try:
        time_enum = _parse_time_of_day(time_of_day)
        weather_enum = _parse_weather(weather)

        config = SceneConfig(
            width=width,
            height=height,
            time_of_day=time_enum,
            weather=weather_enum,
            seed=seed,
        )
        scene = create_scene(width=width, height=height, config=config)

        background_layers = generate_parallax_background(
            width=width,
            height=height,
            layers=3,
            seed=seed,
        )
        for layer in background_layers:
            scene.add_layer(layer)

        canvas = scene.render()

        result = GenerationResult(
            canvas=canvas,
            parameters={
                "description": description,
                "width": width,
                "height": height,
                "time_of_day": time_of_day,
                "weather": weather,
            },
            seed=seed,
            sprite_type=SpriteType.ENVIRONMENT,
            generator_name="generate_scene",
            generation_time_ms=(time.time() - start_time) * 1000,
            metadata={"layers": background_layers},
        )
        return ToolResult.ok(result)

    except Exception as e:
        return ToolResult.fail(str(e), "GenerationError")


@tool(name="generate_background", category="generation", tags=["scene"])
def generate_background(
    style: str = "forest",
    layers: int = 3,
    width: int = 320,
    height: int = 180,
    seed: Optional[int] = None,
) -> ToolResult:
    """Generate parallax background layers."""
    start_time = time.time()
    seed = seed or random.randint(0, 2**31)

    try:
        layer_canvases = _generate_parallax(
            width=width,
            height=height,
            theme=style,
            num_layers=layers,
            seed=seed,
        )

        composite = Canvas(width, height, (0, 0, 0, 0))
        for layer in layer_canvases:
            composite.blit(layer, 0, 0)

        result = GenerationResult(
            canvas=composite,
            parameters={
                "style": style,
                "layers": layers,
                "width": width,
                "height": height,
            },
            seed=seed,
            sprite_type=SpriteType.ENVIRONMENT,
            generator_name="generate_background",
            generation_time_ms=(time.time() - start_time) * 1000,
            metadata={"layers": layer_canvases},
        )
        return ToolResult.ok(result)

    except Exception as e:
        return ToolResult.fail(str(e), "GenerationError")


def _parse_time_of_day(time_of_day: str) -> TimeOfDay:
    normalized = (time_of_day or "").strip().lower()
    for value in TimeOfDay:
        if value.value == normalized:
            return value
    available = ", ".join(t.value for t in TimeOfDay)
    raise ValueError(f"Unknown time_of_day '{time_of_day}'. Available: {available}")


def _parse_weather(weather: str) -> WeatherType:
    normalized = (weather or "").strip().lower()
    for value in WeatherType:
        if value.value == normalized:
            return value
    available = ", ".join(w.value for w in WeatherType)
    raise ValueError(f"Unknown weather '{weather}'. Available: {available}")

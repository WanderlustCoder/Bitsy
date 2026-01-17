"""
Item and prop generation tools.

Provides AI-accessible tools for generating items and props.
"""

from typing import Optional, List
import time
import random

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from .definitions import tool
from .results import GenerationResult, ToolResult, SpriteType

from generators import (
    generate_item as _generate_item,
    list_item_types as _list_item_types,
    generate_prop as _generate_prop,
    list_prop_types as _list_prop_types,
)


@tool(name="generate_item", category="generation", tags=["item"])
def generate_item(
    item_type: str,
    variant: Optional[str] = None,
    seed: Optional[int] = None,
) -> ToolResult:
    """Generate an item sprite."""
    start_time = time.time()
    seed = seed or random.randint(0, 2**31)

    try:
        available = _list_item_types()
        resolved_type = _resolve_item_type(item_type, variant, available)
        canvas = _generate_item(item_type=resolved_type, seed=seed)

        result = GenerationResult(
            canvas=canvas,
            parameters={
                "item_type": item_type,
                "variant": variant,
                "resolved_type": resolved_type,
            },
            seed=seed,
            sprite_type=SpriteType.ITEM,
            generator_name="generate_item",
            generation_time_ms=(time.time() - start_time) * 1000,
        )
        return ToolResult.ok(result)

    except Exception as e:
        return ToolResult.fail(str(e), "GenerationError")


@tool(name="generate_prop", category="generation", tags=["prop"])
def generate_prop(
    prop_type: str,
    seed: Optional[int] = None,
) -> ToolResult:
    """Generate a prop sprite."""
    start_time = time.time()
    seed = seed or random.randint(0, 2**31)

    try:
        available = _list_prop_types()
        normalized = _normalize_key(prop_type)
        if normalized not in available:
            available_str = ", ".join(sorted(available))
            raise ValueError(f"Unknown prop type '{prop_type}'. Available: {available_str}")

        canvas = _generate_prop(prop_type=normalized, seed=seed)

        result = GenerationResult(
            canvas=canvas,
            parameters={"prop_type": prop_type, "resolved_type": normalized},
            seed=seed,
            sprite_type=SpriteType.PROP,
            generator_name="generate_prop",
            generation_time_ms=(time.time() - start_time) * 1000,
        )
        return ToolResult.ok(result)

    except Exception as e:
        return ToolResult.fail(str(e), "GenerationError")


@tool(name="list_item_types", category="info")
def list_item_types() -> List[str]:
    """List available item types."""
    return _list_item_types()


@tool(name="list_prop_types", category="info")
def list_prop_types() -> List[str]:
    """List available prop types."""
    return _list_prop_types()


def _resolve_item_type(item_type: str, variant: Optional[str], available: List[str]) -> str:
    base = _normalize_key(item_type)
    if variant:
        variant_key = _normalize_key(variant)
        combined = f"{base}_{variant_key}"
        if combined in available:
            return combined
    if base in available:
        return base
    available_str = ", ".join(sorted(available))
    raise ValueError(f"Unknown item type '{item_type}'. Available: {available_str}")


def _normalize_key(value: str) -> str:
    return (value or "").strip().lower().replace(" ", "_")

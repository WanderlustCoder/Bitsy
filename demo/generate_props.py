#!/usr/bin/env python3
"""Generate demo props from the Bitsy PropGenerator."""

import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from generators.prop import (
    generate_prop,
    list_chest_types,
    list_container_types,
    list_furniture_types,
    list_vegetation_types,
)


OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "props")


def _ensure_variant(label: str, variant: str, options: list[str]) -> None:
    if variant not in options:
        raise ValueError(f"Unknown {label} '{variant}'. Options: {options}")


def _save_prop(base_name: str, prop_type: str, variant: str, width: int, height: int) -> None:
    canvas = generate_prop(prop_type, variant, width, height)
    output_path = os.path.join(OUTPUT_DIR, f"{base_name}.png")
    canvas.save(output_path)

    scaled = canvas.scale(4)
    scaled_path = os.path.join(OUTPUT_DIR, f"{base_name}_4x.png")
    scaled.save(scaled_path)


def main() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    chest_variants = ["wooden", "iron", "gold", "treasure"]
    container_types = ["barrel", "crate", "pot", "vase", "sack"]
    furniture_types = ["table", "chair", "bed", "bookshelf", "throne"]
    vegetation_types = ["tree", "bush", "flower", "grass", "mushroom", "cactus"]

    available_chests = list_chest_types()
    available_containers = list_container_types()
    available_furniture = list_furniture_types()
    available_vegetation = list_vegetation_types()

    for variant in chest_variants:
        _ensure_variant("chest", variant, available_chests)
        _save_prop(f"chest_{variant}", "chest", variant, 16, 16)

    for prop_type in container_types:
        _ensure_variant("container", prop_type, available_containers)
        _save_prop(f"container_{prop_type}", prop_type, None, 16, 16)

    for prop_type in furniture_types:
        _ensure_variant("furniture", prop_type, available_furniture)
        _save_prop(f"furniture_{prop_type}", prop_type, None, 16, 16)

    for prop_type in vegetation_types:
        _ensure_variant("vegetation", prop_type, available_vegetation)
        size = 32 if prop_type == "tree" else 16
        _save_prop(f"vegetation_{prop_type}", prop_type, None, size, size)


if __name__ == "__main__":
    main()

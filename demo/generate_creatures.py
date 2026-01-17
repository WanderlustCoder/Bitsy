"""Generate creature PNGs for demo usage."""

from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from generators.creature import (
    CreatureGenerator,
    generate_creature,
    list_creature_types,
    list_slime_variants,
)

OUTPUT_DIR = Path(__file__).resolve().parent / "creatures"

SLIME_VARIANTS = [
    "basic",
    "blue",
    "red",
    "purple",
    "fire",
    "ice",
    "poison",
    "metal",
]

CREATURE_TYPES = [
    "ghost",
    "skeleton",
    "zombie",
    "wolf",
    "bat",
    "spider",
    "fire_elemental",
    "ice_elemental",
]


def _validate_variants() -> None:
    available_slimes = set(list_slime_variants())
    missing_slimes = [variant for variant in SLIME_VARIANTS if variant not in available_slimes]
    if missing_slimes:
        raise ValueError(f"Missing slime variants: {', '.join(missing_slimes)}")

    available_creatures = set(list_creature_types())
    missing_creatures = [creature for creature in CREATURE_TYPES if creature not in available_creatures]
    if missing_creatures:
        raise ValueError(f"Missing creature types: {', '.join(missing_creatures)}")


def _save_canvas(canvas, base_name: str) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    canvas.save(str(OUTPUT_DIR / f"{base_name}.png"))
    canvas.scale(4).save(str(OUTPUT_DIR / f"{base_name}_4x.png"))


def _generate_slimes() -> None:
    for variant in SLIME_VARIANTS:
        canvas = generate_creature("slime", variant=variant, width=16, height=16, seed=42)
        _save_canvas(canvas, f"slime_{variant}")


def _generate_creatures() -> None:
    for creature_type in CREATURE_TYPES:
        generator = CreatureGenerator(width=16, height=16, seed=42)
        canvas = generator.generate(creature_type)
        _save_canvas(canvas, f"creature_{creature_type}")


def main() -> None:
    _validate_variants()
    _generate_slimes()
    _generate_creatures()


if __name__ == "__main__":
    main()

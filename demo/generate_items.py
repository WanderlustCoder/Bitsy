import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from export.png import save_png
from generators.item import ItemGenerator, generate_item, list_item_types


OUTPUT_DIR = os.path.join("demo", "items")
SIZE = 16
SCALE = 4

REQUESTED_ITEMS = {
    "weapon": ["sword", "dagger", "axe", "spear", "bow", "staff", "wand", "hammer"],
    "consumable": ["health_potion", "mana_potion", "buff_potion", "food", "scroll"],
    "material": ["gem", "ore", "herb", "crystal"],
    "key": ["key"],
}

# Map requested names to available generator types/variants.
ITEM_TYPE_MAP = {
    "weapon": {
        "sword": ("sword", None),
        "dagger": ("sword", "rapier"),
        "axe": ("axe", None),
        "spear": ("staff", None),
        "bow": ("bow", None),
        "staff": ("staff", None),
        "wand": ("staff", None),
        "hammer": ("axe", None),
    },
    "consumable": {
        "health_potion": ("potion", "health"),
        "mana_potion": ("potion", "mana"),
        "buff_potion": ("potion", "buff"),
        "food": ("potion", "stamina"),
        "scroll": ("scroll", None),
    },
    "material": {
        "gem": ("gem", "red"),
        "ore": ("gem", "yellow"),
        "herb": ("gem", "green"),
        "crystal": ("gem", "purple"),
    },
    "key": {
        "key": ("key", None),
    },
}


def _ensure_output_dir() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def _normalize_key(value: str | None) -> str:
    return (value or "").strip().lower().replace(" ", "_")


def _resolve_item_type(item_type: str, variant: str | None, available: list[str]) -> str:
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


def _generate_item_variant(
    item_type: str, variant: str | None, width: int, height: int, seed: int
):
    available = list_item_types()
    resolved = _resolve_item_type(item_type, variant, available)
    return generate_item(item_type=resolved, width=width, height=height, seed=seed)


def main() -> None:
    _ensure_output_dir()
    seed = 42

    for category, names in REQUESTED_ITEMS.items():
        for name in names:
            item_type, variant = ITEM_TYPE_MAP[category][name]
            canvas = _generate_item_variant(item_type, variant, SIZE, SIZE, seed)
            base_name = f"{category}_{name}"
            save_png(canvas, os.path.join(OUTPUT_DIR, f"{base_name}.png"))
            save_png(canvas.scale(SCALE), os.path.join(OUTPUT_DIR, f"{base_name}_4x.png"))
            seed += 1


if __name__ == "__main__":
    main()

"""Generate before/after comparison images for HD quality improvements."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Canvas, Style, Palette, hex_to_rgba
from characters import CharacterBuilder
from quality.selout import apply_selout

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "comparison")
SCALE_FACTOR = 4
SIZE = 48  # Use same size for fair comparison
BACKGROUND = hex_to_rgba("#2a2d38")
PADDING = 8


def save_scaled(canvas: Canvas, filename: str) -> None:
    path = os.path.join(OUTPUT_DIR, filename)
    canvas.scale(SCALE_FACTOR).save(path)


def create_character_comparison() -> tuple[Canvas, Canvas]:
    """Create same character with old vs new quality settings."""
    # Old style: chibi, 3-level shading, no selout
    old_char = (CharacterBuilder(width=SIZE, height=SIZE, style='chibi', seed=42)
        .head('round')
        .body('chibi')
        .hair('long', color='brown')
        .eyes('large', color='green', expression='happy')
        .skin('warm')
        .outfit('blue')
        .build())

    # New style: modern, 5-level shading with hue shifts, selout
    new_char = (CharacterBuilder(width=SIZE, height=SIZE, style='modern', seed=42)
        .head('round')
        .body('chibi')
        .hair('long', color='brown')
        .eyes('large', color='green', expression='happy')
        .skin('warm')
        .outfit('blue')
        .build())

    old_sprite = old_char.render()
    new_sprite = apply_selout(new_char.render())

    return old_sprite, new_sprite


def create_hair_comparison() -> tuple[Canvas, Canvas]:
    """Compare hair rendering quality."""
    old_char = (CharacterBuilder(width=SIZE, height=SIZE, style='chibi', seed=7)
        .head('round')
        .body('chibi')
        .hair('long', color='lavender')
        .eyes('large', color='blue')
        .skin('cool')
        .build())

    new_char = (CharacterBuilder(width=SIZE, height=SIZE, style='professional_hd', seed=7)
        .head('round')
        .body('chibi')
        .hair('long', color='lavender')
        .eyes('large', color='blue')
        .skin('cool')
        .build())

    return old_char.render(), apply_selout(new_char.render())


def create_equipment_comparison() -> tuple[Canvas, Canvas]:
    """Compare equipped character quality."""
    old_char = (CharacterBuilder(width=SIZE, height=SIZE, style='chibi', seed=99)
        .head('square')
        .body('muscular')
        .hair('short', color='black')
        .eyes('round', color='blue')
        .skin('cool')
        .equip_set('knight')
        .build())

    new_char = (CharacterBuilder(width=SIZE, height=SIZE, style='professional_hd', seed=99)
        .head('square')
        .body('muscular')
        .hair('short', color='black')
        .eyes('round', color='blue')
        .skin('cool')
        .equip_set('knight')
        .build())

    return old_char.render(), apply_selout(new_char.render())


def create_side_by_side(old: Canvas, new: Canvas, label: str) -> Canvas:
    """Create side-by-side comparison canvas."""
    canvas_width = (SIZE * 2) + (PADDING * 3)
    canvas_height = SIZE + PADDING * 2
    canvas = Canvas(canvas_width, canvas_height, BACKGROUND)

    canvas.blit(old, PADDING, PADDING)
    canvas.blit(new, SIZE + PADDING * 2, PADDING)

    return canvas


def main() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Generate comparison pairs
    old_char, new_char = create_character_comparison()
    old_hair, new_hair = create_hair_comparison()
    old_equip, new_equip = create_equipment_comparison()

    # Save side-by-side comparisons
    save_scaled(create_side_by_side(old_char, new_char, "Character"), "compare_character.png")
    save_scaled(create_side_by_side(old_hair, new_hair, "Hair"), "compare_hair.png")
    save_scaled(create_side_by_side(old_equip, new_equip, "Equipment"), "compare_equipment.png")

    # Save individual images for detailed view
    save_scaled(old_char, "old_character.png")
    save_scaled(new_char, "new_character.png")
    save_scaled(old_hair, "old_hair.png")
    save_scaled(new_hair, "new_hair.png")
    save_scaled(old_equip, "old_equipment.png")
    save_scaled(new_equip, "new_equipment.png")

    print(f"Generated comparison images in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()

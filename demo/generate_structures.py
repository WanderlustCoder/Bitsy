from pathlib import Path
from math import ceil
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from core import Canvas
from generators.structure import (
    generate_house,
    generate_castle_wall,
    generate_castle_tower,
    generate_dungeon_tile,
    generate_dungeon_tileset,
    list_building_styles,
    list_roof_styles,
    list_dungeon_tile_types,
)


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def save_canvas(canvas: Canvas, path: Path) -> None:
    canvas.save(str(path))


def build_tileset_spritesheet(tiles: dict, tile_size: int, columns: int = 4) -> Canvas:
    order = list_dungeon_tile_types()
    count = len(order)
    rows = ceil(count / columns)
    sheet = Canvas(columns * tile_size, rows * tile_size)

    for idx, tile_type in enumerate(order):
        tile = tiles.get(tile_type)
        if tile is None:
            continue
        x = (idx % columns) * tile_size
        y = (idx // columns) * tile_size
        sheet.blit(tile, x, y)

    return sheet


def main() -> None:
    output_dir = Path(__file__).resolve().parent / "structures"
    ensure_dir(output_dir)

    seed = 42

    for style in list_building_styles():
        house = generate_house(width=32, height=32, style=style, seed=seed)
        save_canvas(house, output_dir / f"house_{style}.png")

    wall = generate_castle_wall(width=32, height=32, seed=seed)
    save_canvas(wall, output_dir / "castle_wall.png")

    tower = generate_castle_tower(width=32, height=32, seed=seed)
    save_canvas(tower, output_dir / "castle_tower.png")

    tileset = generate_dungeon_tileset(size=16, seed=seed)
    for tile_type in list_dungeon_tile_types():
        tileset.setdefault(tile_type, generate_dungeon_tile(tile_type, size=16, seed=seed))

    for tile_type, tile in tileset.items():
        save_canvas(tile, output_dir / f"dungeon_{tile_type}.png")

    spritesheet = build_tileset_spritesheet(tileset, tile_size=16, columns=4)
    save_canvas(spritesheet, output_dir / "dungeon_tileset.png")

    _ = list_roof_styles()


if __name__ == "__main__":
    main()

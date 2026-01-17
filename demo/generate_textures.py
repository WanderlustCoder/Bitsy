import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from core import Canvas
from generators.texture import (
    TextureGenerator,
    generate_texture,
    list_texture_types,
    TextureType,
    TexturePalette,
)


OUTPUT_DIR = Path(__file__).resolve().parent / "textures"


def tile_canvas(source: Canvas, tiles_x: int = 2, tiles_y: int = 2) -> Canvas:
    """Return a tiled canvas to demonstrate seamless repetition."""
    tiled = Canvas(source.width * tiles_x, source.height * tiles_y)
    for ty in range(tiles_y):
        for tx in range(tiles_x):
            tiled.blit(source, tx * source.width, ty * source.height)
    return tiled


def generate_textures() -> None:
    available = set(list_texture_types())
    textures = [
        (TextureType.BRICK, "brick", TexturePalette.brick()),
        (TextureType.STONE, "stone", TexturePalette.stone()),
        (TextureType.WOOD, "wood", TexturePalette.wood()),
        (TextureType.GRASS, "grass", TexturePalette.grass()),
        (TextureType.FABRIC, "fabric", TexturePalette.fabric_red()),
        (TextureType.METAL, "metal", TexturePalette.metal()),
    ]

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for index, (texture_type, name, palette) in enumerate(textures):
        if texture_type.value not in available:
            raise ValueError(f"Texture type '{texture_type.value}' is not available.")

        seed = 42 + index * 7
        base = generate_texture(
            texture_type.value,
            width=32,
            height=32,
            seed=seed,
            palette=palette,
        )
        base.save(str(OUTPUT_DIR / f"texture_{name}.png"))

        tiled = tile_canvas(base, tiles_x=2, tiles_y=2)
        tiled.save(str(OUTPUT_DIR / f"texture_{name}_tiled.png"))


if __name__ == "__main__":
    generate_textures()

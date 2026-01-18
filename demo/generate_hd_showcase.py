import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Canvas, Style, Palette, hex_to_rgba
from core.style import PROFESSIONAL_HD, MODERN_HD
from quality.selout import apply_selout
from characters import CharacterBuilder, presets
from parts.hair_hd import BunHairHD, LongHairHD, PonytailHairHD, ShortHairHD
from parts.base import PartConfig


SIZE = 64
SCALE_FACTOR = 4
PADDING = 8
BACKGROUND = hex_to_rgba("#2a2d38")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "hd_showcase")


def save_scaled(canvas: Canvas, filename: str) -> None:
    path = os.path.join(OUTPUT_DIR, filename)
    canvas.scale(SCALE_FACTOR).save(path)


def build_base_character(style) -> Canvas:
    char = (CharacterBuilder(width=SIZE, height=SIZE, seed=42)
        .style(style)
        .head("round")
        .body("chibi")
        .hair("long", color="brown")
        .eyes("large", color="green", expression="happy")
        .skin("warm")
        .outfit("blue")
        .build())
    return char.render()


def create_style_comparison() -> Canvas:
    styles = [
        ("chibi", "chibi"),
        ("modern_hd", MODERN_HD),
        ("professional_hd", PROFESSIONAL_HD),
    ]

    canvas_width = (SIZE * len(styles)) + (PADDING * (len(styles) + 1))
    canvas = Canvas(canvas_width, SIZE + PADDING * 2, BACKGROUND)

    for i, (_, style) in enumerate(styles):
        sprite = build_base_character(style)
        x = PADDING + i * (SIZE + PADDING)
        canvas.blit(sprite, x, PADDING)

    return canvas


def create_selout_demo() -> Canvas:
    canvas_width = SIZE * 2 + PADDING * 3
    canvas = Canvas(canvas_width, SIZE + PADDING * 2, BACKGROUND)

    base_char = presets.hero(width=SIZE, height=SIZE, seed=7).render()
    selout_char = apply_selout(base_char)

    canvas.blit(base_char, PADDING, PADDING)
    canvas.blit(selout_char, SIZE + PADDING * 2, PADDING)

    return canvas


def create_aa_comparison() -> Canvas:
    canvas_width = SIZE * 2 + PADDING * 3
    canvas = Canvas(canvas_width, SIZE + PADDING * 2, BACKGROUND)

    aa_style = Style.modern_hd()
    colors = aa_style.get_shading_colors(hex_to_rgba("#5aa7ff"), 3)
    circle_color = colors[1]

    left_x = PADDING + SIZE // 2
    right_x = PADDING * 2 + SIZE + SIZE // 2
    cy = PADDING + SIZE // 2
    radius = SIZE // 3

    canvas.fill_circle(left_x, cy, radius, circle_color)
    canvas.fill_circle_aa(right_x, cy, radius, circle_color)

    return canvas


def create_hd_hair_showcase() -> Canvas:
    hair_palette = Palette([
        hex_to_rgba("#e5c4ff"),
        hex_to_rgba("#b689f2"),
        hex_to_rgba("#7a4bb6"),
    ], name="Lavender HD")

    config = PartConfig(
        base_color=hair_palette.get(1),
        palette=hair_palette,
        style=PROFESSIONAL_HD,
    )

    hair_styles = [
        BunHairHD,
        LongHairHD,
        PonytailHairHD,
        ShortHairHD,
    ]

    canvas_width = (SIZE * len(hair_styles)) + (PADDING * (len(hair_styles) + 1))
    canvas = Canvas(canvas_width, SIZE + PADDING * 2, BACKGROUND)

    for i, hair_class in enumerate(hair_styles):
        x = PADDING + i * (SIZE + PADDING) + SIZE // 2
        y = PADDING + SIZE // 2
        hair = hair_class(config)
        hair.draw(canvas, x, y, SIZE - 10, SIZE - 14)

    return canvas


def create_professional_portrait() -> Canvas:
    char = (CharacterBuilder(width=SIZE, height=SIZE, seed=99)
        .style(PROFESSIONAL_HD)
        .head("square")
        .body("muscular")
        .hair("short", color="black")
        .eyes("round", color="blue", expression="neutral")
        .skin("cool")
        .equip_set("knight")
        .build())

    portrait = apply_selout(char.render())
    canvas = Canvas(SIZE + PADDING * 2, SIZE + PADDING * 2, BACKGROUND)
    canvas.blit(portrait, PADDING, PADDING)
    return canvas


def main() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    save_scaled(create_style_comparison(), "hd_style_comparison.png")
    save_scaled(create_selout_demo(), "hd_selout_demo.png")
    save_scaled(create_aa_comparison(), "hd_aa_comparison.png")
    save_scaled(create_hd_hair_showcase(), "hd_hair_styles.png")
    save_scaled(create_professional_portrait(), "hd_portrait.png")


if __name__ == "__main__":
    main()

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from characters import CharacterBuilder, presets
from generators.creature import CreatureGenerator, CreaturePalette
from export.gif import save_gif
from core.animation import Animation


OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "animations")
SPRITE_SIZE = 48


def animation_to_gif(animation: Animation, filepath: str) -> None:
    frames = [kf.frame for kf in animation.keyframes]
    delays = [
        max(1, int(kf.duration * 100 / animation.fps))
        for kf in animation.keyframes
    ]
    save_gif(filepath, frames, delays, loop=0)


def save_animation_outputs(animation: Animation, base_name: str) -> None:
    gif_path = os.path.join(OUTPUT_DIR, f"{base_name}.gif")
    sheet_path = os.path.join(OUTPUT_DIR, f"{base_name}.png")
    animation_to_gif(animation, gif_path)
    animation.save_spritesheet(sheet_path)


def translate_canvas(canvas, dx: int, dy: int):
    shifted = canvas.__class__(canvas.width, canvas.height, (0, 0, 0, 0))
    shifted.blit(canvas, dx, dy)
    return shifted


def scale_canvas_y(canvas, scale_y: float, anchor_y: float):
    scaled = canvas.__class__(canvas.width, canvas.height, (0, 0, 0, 0))
    for y in range(canvas.height):
        src_y = int(round((y - anchor_y) / scale_y + anchor_y))
        if src_y < 0 or src_y >= canvas.height:
            continue
        for x in range(canvas.width):
            color = canvas.get_pixel(x, src_y)
            if color and color[3] > 0:
                scaled.set_pixel_solid(x, y, color)
    return scaled


def generate_hero_idle() -> Animation:
    hero = presets.hero(width=SPRITE_SIZE, height=SPRITE_SIZE)
    return hero.animate("idle", fps=8)


def generate_hero_walk() -> Animation:
    hero = presets.hero(width=SPRITE_SIZE, height=SPRITE_SIZE)
    return hero.animate("walk", fps=8)


def generate_knight_idle() -> Animation:
    knight = (CharacterBuilder(width=SPRITE_SIZE, height=SPRITE_SIZE)
        .equip_set("knight")
        .build())
    return knight.animate("idle")


def generate_knight_walk() -> Animation:
    knight = (CharacterBuilder(width=SPRITE_SIZE, height=SPRITE_SIZE)
        .equip_set("knight")
        .build())
    return knight.animate("walk")


def generate_wizard_idle() -> Animation:
    wizard = presets.wizard(width=SPRITE_SIZE, height=SPRITE_SIZE)
    return wizard.animate("idle", fps=8)


def append_animation(target: Animation, source: Animation) -> None:
    for kf in source.keyframes:
        target.add_frame(kf.frame, duration=kf.duration, name=kf.name)


def generate_expression_transitions() -> Animation:
    char = presets.hero(width=SPRITE_SIZE, height=SPRITE_SIZE)
    base = Animation("expression_transitions", fps=8)
    append_animation(base, char.animate("idle", fps=8))
    append_animation(base, char.animate("happy", fps=8))
    append_animation(base, char.animate("sad", fps=8))
    append_animation(base, char.animate("idle", fps=8))
    return base


def generate_slime_bounce() -> Animation:
    gen = CreatureGenerator(width=SPRITE_SIZE, height=SPRITE_SIZE, seed=12)
    gen.set_palette(CreaturePalette.green_slime())
    base = gen.generate("slime", "green")

    anim = Animation("slime_bounce", fps=8)
    anchor_y = base.height - 1
    for scale_y in (0.9, 1.0, 1.1, 1.0):
        frame = scale_canvas_y(base, scale_y, anchor_y)
        anim.add_frame(frame, duration=2)
    return anim


def generate_ghost_float() -> Animation:
    gen = CreatureGenerator(width=SPRITE_SIZE, height=SPRITE_SIZE, seed=21)
    base = gen.generate("ghost")

    anim = Animation("ghost_float", fps=8)
    for offset in (-1, 0, 1, 0):
        frame = translate_canvas(base, 0, offset)
        anim.add_frame(frame, duration=2)
    return anim


def main() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    animations = {
        "hero_idle": generate_hero_idle(),
        "hero_walk": generate_hero_walk(),
        "knight_idle": generate_knight_idle(),
        "knight_walk": generate_knight_walk(),
        "wizard_idle": generate_wizard_idle(),
        "expression_transitions": generate_expression_transitions(),
        "slime_bounce": generate_slime_bounce(),
        "ghost_float": generate_ghost_float(),
    }

    for name, animation in animations.items():
        save_animation_outputs(animation, name)


if __name__ == "__main__":
    main()

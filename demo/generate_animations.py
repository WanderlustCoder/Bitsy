import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from generators.character import CharacterGenerator
from generators.creature import CreatureGenerator, CreaturePalette
from export.gif import save_gif
from core.animation import Animation
from core.canvas import Canvas


OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "animations")


def animation_to_gif(animation: Animation, filepath: str) -> None:
    frames = [kf.frame for kf in animation.keyframes]
    delays = [
        max(1, int(kf.duration * 100 / animation.fps))
        for kf in animation.keyframes
    ]
    save_gif(filepath, frames, delays, loop=0)


def translate_canvas(canvas: Canvas, dx: int, dy: int) -> Canvas:
    shifted = Canvas(canvas.width, canvas.height, (0, 0, 0, 0))
    shifted.blit(canvas, dx, dy)
    return shifted


def scale_canvas_y(canvas: Canvas, scale_y: float, anchor_y: float) -> Canvas:
    scaled = Canvas(canvas.width, canvas.height, (0, 0, 0, 0))
    for y in range(canvas.height):
        src_y = int(round((y - anchor_y) / scale_y + anchor_y))
        if src_y < 0 or src_y >= canvas.height:
            continue
        for x in range(canvas.width):
            color = canvas.get_pixel(x, src_y)
            if color and color[3] > 0:
                scaled.set_pixel_solid(x, y, color)
    return scaled


def generate_character_idle() -> Animation:
    gen = CharacterGenerator(width=32, height=32, seed=3)
    return gen.render_animation("idle", fps=8)


def generate_character_walk() -> Animation:
    gen = CharacterGenerator(width=32, height=32, seed=7)
    return gen.render_animation("walk", fps=8)


def generate_slime_bounce() -> Animation:
    gen = CreatureGenerator(width=16, height=16, seed=12)
    gen.set_palette(CreaturePalette.green_slime())
    base = gen.generate("slime", "green")

    anim = Animation("slime_bounce", fps=8)
    anchor_y = base.height - 1
    for scale_y in (0.9, 1.0, 1.1, 1.0):
        frame = scale_canvas_y(base, scale_y, anchor_y)
        anim.add_frame(frame, duration=2)
    return anim


def generate_ghost_float() -> Animation:
    gen = CreatureGenerator(width=16, height=16, seed=21)
    base = gen.generate("ghost")

    anim = Animation("ghost_float", fps=8)
    for offset in (-1, 0, 1, 0):
        frame = translate_canvas(base, 0, offset)
        anim.add_frame(frame, duration=2)
    return anim


def main() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    animations = {
        "character_idle.gif": generate_character_idle(),
        "character_walk.gif": generate_character_walk(),
        "slime_bounce.gif": generate_slime_bounce(),
        "ghost_float.gif": generate_ghost_float(),
    }

    for filename, animation in animations.items():
        path = os.path.join(OUTPUT_DIR, filename)
        animation_to_gif(animation, path)


if __name__ == "__main__":
    main()

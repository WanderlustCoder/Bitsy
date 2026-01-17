import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from generators.character import CharacterGenerator, generate_character


OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "characters")
SIZE = 32
SCALE_FACTOR = 4


def save_variants(canvas, base_name):
    path_1x = os.path.join(OUTPUT_DIR, f"{base_name}.png")
    path_4x = os.path.join(OUTPUT_DIR, f"{base_name}_4x.png")
    canvas.save(path_1x)
    canvas.scale(SCALE_FACTOR).save(path_4x)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 01: default chibi character via convenience function
    default_canvas = generate_character(width=SIZE, height=SIZE)
    save_variants(default_canvas, "char_01_default")

    # 02: blue hair + green eyes
    gen = CharacterGenerator(width=SIZE, height=SIZE)
    gen.set_hair("fluffy", palette="blue")
    gen.set_eyes("large", color="green")
    save_variants(gen.render(), "char_02_blue")

    # 03: brown hair + purple eyes + red outfit
    gen = CharacterGenerator(width=SIZE, height=SIZE)
    gen.set_hair("fluffy", palette="brown")
    gen.set_eyes("large", color="purple")
    gen.set_outfit("cloth_red")
    save_variants(gen.render(), "char_03_brown_purple_red")

    # 04: blonde hair + gold eyes
    gen = CharacterGenerator(width=SIZE, height=SIZE)
    gen.set_hair("fluffy", palette="blonde")
    gen.set_eyes("large", color="gold")
    save_variants(gen.render(), "char_04_blonde")

    # 05: pink hair + sparkle eyes + purple outfit
    gen = CharacterGenerator(width=SIZE, height=SIZE)
    gen.set_hair("fluffy", palette="pink")
    gen.set_eyes("sparkle", color="purple")
    gen.set_outfit("cloth_purple")
    save_variants(gen.render(), "char_05_pink_sparkle")

    # 06: black hair + brown eyes + green outfit
    gen = CharacterGenerator(width=SIZE, height=SIZE)
    gen.set_hair("fluffy", palette="black")
    gen.set_eyes("large", color="brown")
    gen.set_outfit("cloth_green")
    save_variants(gen.render(), "char_06_black_brown_green")

    # 07: red hair + blue eyes
    gen = CharacterGenerator(width=SIZE, height=SIZE)
    gen.set_hair("fluffy", palette="red")
    gen.set_eyes("large", color="blue")
    save_variants(gen.render(), "char_07_red")

    # 08: randomized character
    gen = CharacterGenerator(width=SIZE, height=SIZE)
    gen.randomize()
    save_variants(gen.render(), "char_08_random")


if __name__ == "__main__":
    main()

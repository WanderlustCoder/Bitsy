#!/usr/bin/env python3
"""Generate showcase images demonstrating PortraitGenerator features."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from generators.portrait import PortraitGenerator, HairStyle, EyeShape, NoseType, LipShape
from export.spritesheet import create_grid_sheet


def generate_skin_tones():
    """Generate portraits showcasing different skin tones."""
    print("Generating portrait_skin_tones.png...")

    tones = [
        ("pale", "cool"),
        ("light", "neutral"),
        ("medium", "warm"),
        ("tan", "neutral"),
        ("dark", "warm"),
    ]

    sprites = []
    for tone, undertone in tones:
        portrait = (PortraitGenerator(seed=42)
            .set_skin(tone, undertone)
            .set_hair(HairStyle.WAVY, "brown")
            .set_eyes(EyeShape.ROUND, "brown")
            .render())
        sprites.append(portrait)

    sheet = create_grid_sheet(sprites, columns=5, padding=4)
    sheet.save('assets/showcase/portrait_skin_tones.png')
    print("  Saved: assets/showcase/portrait_skin_tones.png")


def generate_hair_styles():
    """Generate portraits showcasing different hair styles."""
    print("Generating portrait_hair_styles.png...")

    styles = [HairStyle.WAVY, HairStyle.STRAIGHT, HairStyle.CURLY,
              HairStyle.SHORT, HairStyle.PONYTAIL, HairStyle.BUN]

    sprites = []
    for style in styles:
        portrait = (PortraitGenerator(seed=100)
            .set_skin("light", "neutral")
            .set_hair(style, "brown")
            .set_eyes(EyeShape.ROUND, "green")
            .render())
        sprites.append(portrait)

    sheet = create_grid_sheet(sprites, columns=3, padding=4)
    sheet.save('assets/showcase/portrait_hair_styles.png')
    print("  Saved: assets/showcase/portrait_hair_styles.png")


def generate_hair_colors():
    """Generate portraits showcasing different hair colors."""
    print("Generating portrait_hair_colors.png...")

    colors = ["black", "brown", "blonde", "red", "auburn", "gray", "silver", "pink"]

    sprites = []
    for color in colors:
        portrait = (PortraitGenerator(seed=200)
            .set_skin("light", "neutral")
            .set_hair(HairStyle.WAVY, color)
            .set_eyes(EyeShape.ROUND, "brown")
            .render())
        sprites.append(portrait)

    sheet = create_grid_sheet(sprites, columns=4, padding=4)
    sheet.save('assets/showcase/portrait_hair_colors.png')
    print("  Saved: assets/showcase/portrait_hair_colors.png")


def generate_eye_colors():
    """Generate portraits showcasing different eye colors."""
    print("Generating portrait_eye_colors.png...")

    colors = ["brown", "blue", "green", "hazel", "amber", "gray", "violet"]

    sprites = []
    for color in colors:
        portrait = (PortraitGenerator(seed=300)
            .set_skin("light", "neutral")
            .set_hair(HairStyle.WAVY, "brown")
            .set_eyes(EyeShape.ROUND, color)
            .render())
        sprites.append(portrait)

    # Add heterochromia example
    portrait = (PortraitGenerator(seed=300)
        .set_skin("light", "neutral")
        .set_hair(HairStyle.WAVY, "brown")
        .set_eyes(EyeShape.ROUND, "blue", right_color="green")
        .render())
    sprites.append(portrait)

    sheet = create_grid_sheet(sprites, columns=4, padding=4)
    sheet.save('assets/showcase/portrait_eye_colors.png')
    print("  Saved: assets/showcase/portrait_eye_colors.png")


def generate_eye_shapes():
    """Generate portraits showcasing different eye shapes."""
    print("Generating portrait_eye_shapes.png...")

    shapes = [EyeShape.ROUND, EyeShape.ALMOND, EyeShape.DROOPY, EyeShape.SHARP]

    sprites = []
    for shape in shapes:
        portrait = (PortraitGenerator(seed=400)
            .set_skin("light", "neutral")
            .set_hair(HairStyle.WAVY, "brown")
            .set_eyes(shape, "blue")
            .render())
        sprites.append(portrait)

    sheet = create_grid_sheet(sprites, columns=4, padding=4)
    sheet.save('assets/showcase/portrait_eye_shapes.png')
    print("  Saved: assets/showcase/portrait_eye_shapes.png")


def generate_makeup_looks():
    """Generate portraits showcasing makeup options."""
    print("Generating portrait_makeup.png...")

    sprites = []

    # Natural look
    portrait = (PortraitGenerator(seed=500)
        .set_skin("light", "neutral")
        .set_hair(HairStyle.WAVY, "brown")
        .set_eyes(EyeShape.ROUND, "brown")
        .render())
    sprites.append(portrait)

    # Lipstick
    portrait = (PortraitGenerator(seed=500)
        .set_skin("light", "neutral")
        .set_hair(HairStyle.WAVY, "brown")
        .set_eyes(EyeShape.ROUND, "brown")
        .set_lipstick("red", 0.8)
        .render())
    sprites.append(portrait)

    # Eyeshadow
    portrait = (PortraitGenerator(seed=500)
        .set_skin("light", "neutral")
        .set_hair(HairStyle.WAVY, "brown")
        .set_eyes(EyeShape.ROUND, "brown")
        .set_eyeshadow("purple", 0.7)
        .render())
    sprites.append(portrait)

    # Eyeliner
    portrait = (PortraitGenerator(seed=500)
        .set_skin("light", "neutral")
        .set_hair(HairStyle.WAVY, "brown")
        .set_eyes(EyeShape.ROUND, "brown")
        .set_eyeliner("winged", "black")
        .render())
    sprites.append(portrait)

    # Blush
    portrait = (PortraitGenerator(seed=500)
        .set_skin("light", "neutral")
        .set_hair(HairStyle.WAVY, "brown")
        .set_eyes(EyeShape.ROUND, "brown")
        .set_blush("coral", 0.6)
        .render())
    sprites.append(portrait)

    # Full glam
    portrait = (PortraitGenerator(seed=500)
        .set_skin("light", "neutral")
        .set_hair(HairStyle.WAVY, "brown")
        .set_eyes(EyeShape.ROUND, "brown")
        .set_lipstick("berry", 0.8)
        .set_eyeshadow("gold", 0.8)
        .set_eyeliner("winged", "black")
        .set_blush("peach", 0.5)
        .render())
    sprites.append(portrait)

    sheet = create_grid_sheet(sprites, columns=3, padding=4)
    sheet.save('assets/showcase/portrait_makeup.png')
    print("  Saved: assets/showcase/portrait_makeup.png")


def generate_accessories():
    """Generate portraits showcasing accessories."""
    print("Generating portrait_accessories.png...")

    sprites = []

    # Base portrait
    portrait = (PortraitGenerator(seed=600)
        .set_skin("light", "neutral")
        .set_hair(HairStyle.WAVY, "brown")
        .set_eyes(EyeShape.ROUND, "blue")
        .render())
    sprites.append(portrait)

    # Glasses
    portrait = (PortraitGenerator(seed=600)
        .set_skin("light", "neutral")
        .set_hair(HairStyle.WAVY, "brown")
        .set_eyes(EyeShape.ROUND, "blue")
        .set_glasses("round")
        .render())
    sprites.append(portrait)

    # Earrings
    portrait = (PortraitGenerator(seed=600)
        .set_skin("light", "neutral")
        .set_hair(HairStyle.WAVY, "brown")
        .set_eyes(EyeShape.ROUND, "blue")
        .set_earrings("stud")
        .render())
    sprites.append(portrait)

    # Freckles
    portrait = (PortraitGenerator(seed=600)
        .set_skin("light", "neutral")
        .set_hair(HairStyle.WAVY, "brown")
        .set_eyes(EyeShape.ROUND, "blue")
        .set_freckles(0.6)
        .render())
    sprites.append(portrait)

    # Beauty mark
    portrait = (PortraitGenerator(seed=600)
        .set_skin("light", "neutral")
        .set_hair(HairStyle.WAVY, "brown")
        .set_eyes(EyeShape.ROUND, "blue")
        .set_beauty_mark("cheek")
        .render())
    sprites.append(portrait)

    # Headband
    portrait = (PortraitGenerator(seed=600)
        .set_skin("light", "neutral")
        .set_hair(HairStyle.WAVY, "brown")
        .set_eyes(EyeShape.ROUND, "blue")
        .set_hair_accessory("headband", "pink")
        .render())
    sprites.append(portrait)

    sheet = create_grid_sheet(sprites, columns=3, padding=4)
    sheet.save('assets/showcase/portrait_accessories.png')
    print("  Saved: assets/showcase/portrait_accessories.png")


def generate_facial_features():
    """Generate portraits showcasing facial feature variations."""
    print("Generating portrait_facial_features.png...")

    sprites = []

    # Different nose types
    for nose in [NoseType.SMALL, NoseType.BUTTON, NoseType.POINTED, NoseType.WIDE]:
        portrait = (PortraitGenerator(seed=700)
            .set_skin("light", "neutral")
            .set_hair(HairStyle.WAVY, "brown")
            .set_eyes(EyeShape.ROUND, "brown")
            .set_nose(nose)
            .render())
        sprites.append(portrait)

    # Different lip shapes
    for lip in [LipShape.THIN, LipShape.FULL, LipShape.HEART, LipShape.NEUTRAL]:
        portrait = (PortraitGenerator(seed=700)
            .set_skin("light", "neutral")
            .set_hair(HairStyle.WAVY, "brown")
            .set_eyes(EyeShape.ROUND, "brown")
            .set_lips(lip)
            .render())
        sprites.append(portrait)

    sheet = create_grid_sheet(sprites, columns=4, padding=4)
    sheet.save('assets/showcase/portrait_facial_features.png')
    print("  Saved: assets/showcase/portrait_facial_features.png")


def generate_face_shapes():
    """Generate portraits showcasing different face shapes."""
    print("Generating portrait_face_shapes.png...")

    shapes = ["oval", "round", "square", "heart", "oblong", "diamond"]

    sprites = []
    for shape in shapes:
        portrait = (PortraitGenerator(seed=800)
            .set_skin("light", "neutral")
            .set_hair(HairStyle.WAVY, "brown")
            .set_eyes(EyeShape.ROUND, "brown")
            .set_face_shape(shape)
            .render())
        sprites.append(portrait)

    sheet = create_grid_sheet(sprites, columns=3, padding=4)
    sheet.save('assets/showcase/portrait_face_shapes.png')
    print("  Saved: assets/showcase/portrait_face_shapes.png")


def generate_iris_brightness():
    """Generate portraits showcasing iris brightness variations."""
    print("Generating portrait_iris_brightness.png...")

    brightnesses = [0.5, 0.75, 1.0, 1.25, 1.5]

    sprites = []
    for brightness in brightnesses:
        portrait = (PortraitGenerator(seed=900)
            .set_skin("light", "neutral")
            .set_hair(HairStyle.WAVY, "brown")
            .set_eyes(EyeShape.ROUND, "blue")
            .set_iris_brightness(brightness)
            .render())
        sprites.append(portrait)

    sheet = create_grid_sheet(sprites, columns=5, padding=4)
    sheet.save('assets/showcase/portrait_iris_brightness.png')
    print("  Saved: assets/showcase/portrait_iris_brightness.png")


def generate_eyebrow_variations():
    """Generate portraits showcasing eyebrow arch positions."""
    print("Generating portrait_eyebrows.png...")

    sprites = []

    # Different arch positions
    for arch_pos in [0.3, 0.5, 0.7]:
        portrait = (PortraitGenerator(seed=1000)
            .set_skin("light", "neutral")
            .set_hair(HairStyle.WAVY, "brown")
            .set_eyes(EyeShape.ROUND, "brown")
            .set_eyebrow_arch_position(arch_pos)
            .render())
        sprites.append(portrait)

    # Different shapes
    for shape in ["natural", "straight", "arched", "angular"]:
        portrait = (PortraitGenerator(seed=1000)
            .set_skin("light", "neutral")
            .set_hair(HairStyle.WAVY, "brown")
            .set_eyes(EyeShape.ROUND, "brown")
            .set_eyebrows(shape=shape)
            .render())
        sprites.append(portrait)

    sheet = create_grid_sheet(sprites, columns=4, padding=4)
    sheet.save('assets/showcase/portrait_eyebrows.png')
    print("  Saved: assets/showcase/portrait_eyebrows.png")


def generate_diversity_grid():
    """Generate a diverse grid of portraits."""
    print("Generating portrait_diversity.png...")

    configs = [
        # Row 1: Various skin tones and hair colors
        {"seed": 1, "skin": ("pale", "cool"), "hair": (HairStyle.STRAIGHT, "black"), "eyes": ("brown", EyeShape.ALMOND)},
        {"seed": 2, "skin": ("light", "warm"), "hair": (HairStyle.WAVY, "auburn"), "eyes": ("green", EyeShape.ROUND)},
        {"seed": 3, "skin": ("medium", "neutral"), "hair": (HairStyle.CURLY, "brown"), "eyes": ("amber", EyeShape.ROUND)},
        {"seed": 4, "skin": ("tan", "warm"), "hair": (HairStyle.WAVY, "black"), "eyes": ("brown", EyeShape.ALMOND)},
        # Row 2: More diversity
        {"seed": 5, "skin": ("dark", "warm"), "hair": (HairStyle.CURLY, "black"), "eyes": ("brown", EyeShape.ROUND)},
        {"seed": 6, "skin": ("light", "cool"), "hair": (HairStyle.SHORT, "blonde"), "eyes": ("blue", EyeShape.SHARP)},
        {"seed": 7, "skin": ("medium", "warm"), "hair": (HairStyle.PONYTAIL, "brown"), "eyes": ("hazel", EyeShape.DROOPY)},
        {"seed": 8, "skin": ("tan", "neutral"), "hair": (HairStyle.BUN, "black"), "eyes": ("gray", EyeShape.ALMOND)},
    ]

    sprites = []
    for cfg in configs:
        portrait = (PortraitGenerator(seed=cfg["seed"])
            .set_skin(cfg["skin"][0], cfg["skin"][1])
            .set_hair(cfg["hair"][0], cfg["hair"][1])
            .set_eyes(cfg["eyes"][1], cfg["eyes"][0])
            .render())
        sprites.append(portrait)

    sheet = create_grid_sheet(sprites, columns=4, padding=6)
    sheet.save('assets/showcase/portrait_diversity.png')
    print("  Saved: assets/showcase/portrait_diversity.png")


def generate_hero_portrait():
    """Generate a single detailed hero portrait."""
    print("Generating portrait_hero.png...")

    portrait = (PortraitGenerator(seed=42)
        .set_skin("light", "warm", shine=0.4)
        .set_hair(HairStyle.WAVY, "auburn", length=1.2, volume=1.1)
        .set_hair_shine(0.6)
        .set_eyes(EyeShape.ROUND, "green", size=1.1)
        .set_iris_brightness(1.2)
        .set_catchlight("double", brightness=1.2)
        .set_eyebrows(shape="natural")
        .set_lips(LipShape.FULL)
        .set_lipstick("nude", 0.4)
        .set_blush("peach", 0.4)
        .set_freckles(0.3)
        .render())

    scaled = portrait.scale(2)
    scaled.save('assets/showcase/portrait_hero.png')
    print("  Saved: assets/showcase/portrait_hero.png")


def main():
    print("=" * 60)
    print("BITSY PORTRAIT SHOWCASE GENERATOR")
    print("=" * 60)

    os.makedirs('assets/showcase', exist_ok=True)

    generate_hero_portrait()
    generate_skin_tones()
    generate_hair_styles()
    generate_hair_colors()
    generate_eye_colors()
    generate_eye_shapes()
    generate_makeup_looks()
    generate_accessories()
    generate_facial_features()
    generate_face_shapes()
    generate_iris_brightness()
    generate_eyebrow_variations()
    generate_diversity_grid()

    print("\n" + "=" * 60)
    print("Portrait showcase generation complete!")
    print("=" * 60)


if __name__ == '__main__':
    main()

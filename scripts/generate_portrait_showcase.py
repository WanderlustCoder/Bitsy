#!/usr/bin/env python3
"""
Portrait Showcase Generator

Generates a variety of portraits demonstrating the PortraitGenerator's
capabilities including different hair styles, skin tones, and features.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from generators.portrait import (
    PortraitGenerator,
    HairStyle,
    EyeShape,
    NoseType,
    LipShape,
)
from core.canvas import Canvas


def create_portrait_grid(portraits: list, cols: int = 4, padding: int = 4) -> Canvas:
    """Combine multiple portraits into a grid."""
    if not portraits:
        return Canvas(1, 1)

    # Get dimensions from first portrait
    pw, ph = portraits[0].width, portraits[0].height
    rows = (len(portraits) + cols - 1) // cols

    # Create combined canvas
    total_width = cols * pw + (cols - 1) * padding
    total_height = rows * ph + (rows - 1) * padding
    grid = Canvas(total_width, total_height)

    # Blit each portrait
    for i, portrait in enumerate(portraits):
        row = i // cols
        col = i % cols
        x = col * (pw + padding)
        y = row * (ph + padding)
        grid.blit(portrait, x, y)

    return grid


def main():
    output_dir = "output/portraits"
    os.makedirs(output_dir, exist_ok=True)

    print("Generating Portrait Showcase...")
    print("=" * 50)

    # 1. Hair style showcase
    print("\n1. Hair Style Showcase")
    hair_portraits = []
    for i, style in enumerate(HairStyle):
        gen = PortraitGenerator(width=96, height=120, seed=42 + i)
        gen.set_skin("light")
        gen.set_hair(style, "brown")
        gen.set_eyes(EyeShape.ROUND, "blue")
        p = gen.render()
        p.save(f"{output_dir}/hair_{style.value}.png")
        hair_portraits.append(p)
        print(f"  - {style.value}")

    hair_grid = create_portrait_grid(hair_portraits, cols=3)
    hair_grid.save(f"{output_dir}/showcase_hair_styles.png")
    print(f"  Saved hair style grid")

    # 2. Skin tone showcase
    print("\n2. Skin Tone Showcase")
    skin_portraits = []
    skin_tones = ["pale", "light", "medium", "tan", "olive", "brown", "dark"]
    for i, tone in enumerate(skin_tones):
        gen = PortraitGenerator(width=96, height=120, seed=100 + i)
        gen.set_skin(tone)
        gen.set_hair(HairStyle.WAVY, "dark_brown")
        gen.set_eyes(EyeShape.ALMOND, "brown")
        p = gen.render()
        p.save(f"{output_dir}/skin_{tone}.png")
        skin_portraits.append(p)
        print(f"  - {tone}")

    skin_grid = create_portrait_grid(skin_portraits, cols=4)
    skin_grid.save(f"{output_dir}/showcase_skin_tones.png")
    print(f"  Saved skin tone grid")

    # 3. Hair color showcase
    print("\n3. Hair Color Showcase")
    hair_color_portraits = []
    hair_colors = ["black", "brown", "auburn", "blonde", "red", "gray", "blue", "pink"]
    for i, color in enumerate(hair_colors):
        gen = PortraitGenerator(width=96, height=120, seed=200 + i)
        gen.set_skin("medium")
        gen.set_hair(HairStyle.STRAIGHT, color)
        gen.set_eyes(EyeShape.ROUND, "green")
        p = gen.render()
        p.save(f"{output_dir}/hair_color_{color}.png")
        hair_color_portraits.append(p)
        print(f"  - {color}")

    hair_color_grid = create_portrait_grid(hair_color_portraits, cols=4)
    hair_color_grid.save(f"{output_dir}/showcase_hair_colors.png")
    print(f"  Saved hair color grid")

    # 4. Eye color showcase
    print("\n4. Eye Color Showcase")
    eye_portraits = []
    eye_colors = ["brown", "hazel", "green", "blue", "gray", "amber", "violet"]
    for i, color in enumerate(eye_colors):
        gen = PortraitGenerator(width=96, height=120, seed=300 + i)
        gen.set_skin("light")
        gen.set_hair(HairStyle.CURLY, "dark_brown")
        gen.set_eyes(EyeShape.ROUND, color)
        p = gen.render()
        p.save(f"{output_dir}/eye_{color}.png")
        eye_portraits.append(p)
        print(f"  - {color}")

    eye_grid = create_portrait_grid(eye_portraits, cols=4)
    eye_grid.save(f"{output_dir}/showcase_eye_colors.png")
    print(f"  Saved eye color grid")

    # 5. Character variety showcase
    print("\n5. Character Variety Showcase")
    variety_portraits = []
    character_configs = [
        ("light", HairStyle.WAVY, "auburn", "green"),
        ("tan", HairStyle.CURLY, "black", "brown"),
        ("pale", HairStyle.STRAIGHT, "blonde", "blue"),
        ("dark", HairStyle.SHORT, "black", "brown"),
        ("medium", HairStyle.WAVY, "brown", "hazel"),
        ("olive", HairStyle.STRAIGHT, "dark_brown", "amber"),
        ("light", HairStyle.CURLY, "red", "green"),
        ("brown", HairStyle.WAVY, "black", "brown"),
    ]
    for i, (skin, hair_style, hair_color, eye_color) in enumerate(character_configs):
        gen = PortraitGenerator(width=96, height=120, seed=400 + i)
        gen.set_skin(skin)
        gen.set_hair(hair_style, hair_color)
        gen.set_eyes(EyeShape.ROUND, eye_color)
        p = gen.render()
        variety_portraits.append(p)
        print(f"  - Character {i+1}: {skin} skin, {hair_style.value} {hair_color} hair, {eye_color} eyes")

    variety_grid = create_portrait_grid(variety_portraits, cols=4)
    variety_grid.save(f"{output_dir}/showcase_variety.png")
    print(f"  Saved character variety grid")

    # 6. Expression showcase
    print("\n6. Expression Showcase")
    expr_portraits = []
    expressions = ["neutral", "happy", "sad", "surprised", "angry", "sleepy"]
    for i, expr in enumerate(expressions):
        gen = PortraitGenerator(width=96, height=120, seed=500 + i)
        gen.set_skin("light")
        gen.set_hair(HairStyle.WAVY, "auburn")
        gen.set_eyes(EyeShape.ROUND, "blue")
        gen.set_expression(expr)
        p = gen.render()
        p.save(f"{output_dir}/expr_{expr}.png")
        expr_portraits.append(p)
        print(f"  - {expr}")

    expr_grid = create_portrait_grid(expr_portraits, cols=3)
    expr_grid.save(f"{output_dir}/showcase_expressions.png")
    print(f"  Saved expression grid")

    # 7. High-resolution portrait with all features
    print("\n7. High Resolution Portrait (160x200)")
    gen_hd = PortraitGenerator(width=160, height=200, seed=42)
    gen_hd.set_skin("light")
    gen_hd.set_hair(HairStyle.PONYTAIL, "purple")  # Bun style, purple like reference
    gen_hd.set_eyes(EyeShape.ROUND, "brown")
    gen_hd.set_glasses("round")
    gen_hd.set_expression("happy")
    gen_hd.set_background(gradient=((25, 25, 45), (35, 35, 65)))  # Dark gradient
    hd_portrait = gen_hd.render()
    hd_portrait.save(f"{output_dir}/portrait_hd.png")
    print(f"  Saved HD portrait with bun, glasses, shoulders, background (160x200)")

    # 8. Reference-style portrait comparison
    print("\n8. Reference-Style Portrait (larger)")
    gen_ref = PortraitGenerator(width=180, height=240, seed=123)
    gen_ref.set_skin("tan")
    gen_ref.set_hair(HairStyle.PONYTAIL, "purple")
    gen_ref.set_eyes(EyeShape.ROUND, "brown")
    gen_ref.set_glasses("round")
    gen_ref.set_expression("happy")
    gen_ref.set_background(gradient=((20, 20, 40), (30, 30, 60)))
    ref_portrait = gen_ref.render()
    ref_portrait.save(f"{output_dir}/portrait_reference_style.png")
    print(f"  Saved reference-style portrait (180x240)")

    print("\n" + "=" * 50)
    print(f"Portrait showcase complete! Files saved to {output_dir}/")


if __name__ == "__main__":
    main()

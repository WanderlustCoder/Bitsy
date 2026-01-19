#!/usr/bin/env python3
"""Generate showcase images for the README gallery."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from characters import CharacterBuilder, presets, random_character
from export.spritesheet import create_grid_sheet
from export import save_gif_from_animation
from core import Style


def generate_hero():
    """Generate a fully equipped hero character."""
    print("Generating showcase_hero.png...")

    char = (CharacterBuilder(width=64, height=64, seed=42)
        .style('chibi')
        .head('round')
        .body('chibi')
        .hair('spiky', color='blonde')
        .eyes('large', color='blue', expression='determined')
        .skin('fair')
        .equip_set('knight')
        .cape('royal')
        .build())

    sprite = char.render()
    scaled = sprite.scale(2)
    scaled.save('assets/showcase/showcase_hero.png')
    print("  Saved: assets/showcase/showcase_hero.png")


def generate_styles():
    """Generate same character in 4 different styles."""
    print("Generating showcase_styles.png...")

    styles = ['chibi', 'retro_nes', 'retro_snes', 'modern_hd']
    sprites = []

    for style_name in styles:
        char = (CharacterBuilder(width=32, height=32, seed=100)
            .style(style_name)
            .head('round')
            .body('chibi')
            .hair('short', color='brown')
            .eyes('round', color='green')
            .outfit('blue')
            .build())
        sprites.append(char.render())

    sheet = create_grid_sheet(sprites, columns=4, padding=4)
    scaled = sheet.scale(3)
    scaled.save('assets/showcase/showcase_styles.png')
    print("  Saved: assets/showcase/showcase_styles.png")


def generate_expressions():
    """Generate expression grid."""
    print("Generating showcase_expressions.png...")

    base_char = (CharacterBuilder(width=32, height=32, seed=200)
        .head('round')
        .body('chibi')
        .hair('fluffy', color='orange')
        .eyes('large', color='green')
        .build())

    expressions = ['neutral', 'happy', 'sad', 'angry', 'surprised', 'worried', 'sleepy', 'excited']
    sprites = []

    for expr in expressions:
        char = base_char.with_expression(expr)
        sprites.append(char.render())

    sheet = create_grid_sheet(sprites, columns=4, padding=2)
    scaled = sheet.scale(2)
    scaled.save('assets/showcase/showcase_expressions.png')
    print("  Saved: assets/showcase/showcase_expressions.png")


def generate_characters():
    """Generate variety of random characters."""
    print("Generating showcase_characters.png...")

    sprites = []
    for seed in [10, 25, 42, 77, 123, 200, 333, 500]:
        char = random_character(seed=seed, width=32, height=32)
        sprites.append(char.render())

    sheet = create_grid_sheet(sprites, columns=4, padding=2)
    scaled = sheet.scale(2)
    scaled.save('assets/showcase/showcase_characters.png')
    print("  Saved: assets/showcase/showcase_characters.png")


def generate_party():
    """Generate an RPG party."""
    print("Generating showcase_party.png...")

    party = [
        presets.warrior(hair_color='black', outfit_color='red'),
        presets.wizard(hair_color='white', outfit_color='purple'),
        presets.rogue(hair_color='brown', outfit_color='gray'),
        presets.princess(hair_color='blonde', outfit_color='pink'),
    ]

    sprites = [char.render() for char in party]
    sheet = create_grid_sheet(sprites, columns=4, padding=4)
    scaled = sheet.scale(2)
    scaled.save('assets/showcase/showcase_party.png')
    print("  Saved: assets/showcase/showcase_party.png")


def generate_walk_cycle():
    """Generate animated walk cycle GIF."""
    print("Generating showcase_walk.gif...")

    char = presets.hero(seed=42)
    walk_anim = char.animate('walk', fps=8)
    walk_anim.save_gif('assets/showcase/showcase_walk.gif', scale=3)
    print("  Saved: assets/showcase/showcase_walk.gif")


def generate_equipment():
    """Generate equipment showcase."""
    print("Generating showcase_equipment.png...")

    equipment_sets = ['knight', 'wizard', 'ranger', 'warrior', 'rogue', 'royal']
    sprites = []

    for eq_set in equipment_sets:
        char = (CharacterBuilder(width=32, height=32)
            .head('round')
            .body('chibi')
            .eyes('round', color='brown')
            .equip_set(eq_set)
            .build())
        sprites.append(char.render())

    sheet = create_grid_sheet(sprites, columns=6, padding=2)
    scaled = sheet.scale(2)
    scaled.save('assets/showcase/showcase_equipment.png')
    print("  Saved: assets/showcase/showcase_equipment.png")


def main():
    print("=" * 50)
    print("BITSY SHOWCASE GENERATOR")
    print("=" * 50)

    os.makedirs('assets/showcase', exist_ok=True)

    generate_hero()
    generate_styles()
    generate_expressions()
    generate_characters()
    generate_party()
    generate_walk_cycle()
    generate_equipment()

    print("\n" + "=" * 50)
    print("Showcase generation complete!")
    print("=" * 50)


if __name__ == '__main__':
    main()

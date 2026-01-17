#!/usr/bin/env python3
"""
Character Builder Demo - Demonstrates the character assembly system.

This example shows how to use CharacterBuilder to create custom characters
and the preset system for quick character creation.

Run with:
    python -m examples.character_builder_demo
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.canvas import Canvas
from characters import (
    CharacterBuilder,
    build_character,
    presets,
    list_presets,
    random_character,
)
from export.spritesheet import create_grid_sheet


def demo_basic_builder():
    """Demonstrate basic CharacterBuilder usage."""
    print("=== Basic CharacterBuilder ===")

    # Create a simple character with the builder
    char = (CharacterBuilder()
        .head('round')
        .body('chibi')
        .hair('spiky', color='brown')
        .eyes('large', color='blue')
        .build())

    sprite = char.render()
    sprite.save('output/char_basic.png')
    print(f"Created: {char}")
    print("Saved: output/char_basic.png")


def demo_full_customization():
    """Demonstrate full character customization."""
    print("\n=== Full Customization ===")

    char = (CharacterBuilder(width=64, height=64, seed=42)
        .style('chibi')
        .head('heart')
        .body('slim')
        .hair('long', color='lavender', has_bangs=True)
        .eyes('sparkle', color='purple', expression='happy')
        .skin('pale')
        .outfit('pink')
        .build())

    sprite = char.render()
    sprite.save('output/char_custom.png')
    print(f"Created: {char}")
    print("Saved: output/char_custom.png")


def demo_expressions():
    """Demonstrate character expressions."""
    print("\n=== Expression Variations ===")

    base_char = (CharacterBuilder(width=32, height=32, seed=123)
        .head('round')
        .body('chibi')
        .hair('fluffy', color='brown')
        .eyes('large', color='green')
        .build())

    expressions = ['neutral', 'happy', 'sad', 'angry']
    sprites = []

    for expr in expressions:
        char = base_char.with_expression(expr)
        sprites.append(char.render())

    # Create a sheet with all expressions
    sheet = create_grid_sheet(sprites, columns=4, padding=2)
    sheet.save('output/char_expressions.png')
    print(f"Created expressions: {expressions}")
    print("Saved: output/char_expressions.png")


def demo_presets():
    """Demonstrate character presets."""
    print("\n=== Character Presets ===")

    available = list_presets()
    print(f"Available presets: {available}")

    # Create a few preset characters
    hero_char = presets.hero()
    wizard_char = presets.wizard()
    princess_char = presets.princess()
    monster_char = presets.monster()

    sprites = [
        hero_char.render(),
        wizard_char.render(),
        princess_char.render(),
        monster_char.render(),
    ]

    sheet = create_grid_sheet(sprites, columns=4, padding=2)
    sheet.save('output/char_presets.png')
    print("Saved: output/char_presets.png (hero, wizard, princess, monster)")


def demo_preset_customization():
    """Demonstrate customizing presets."""
    print("\n=== Customized Presets ===")

    # Presets accept customization parameters
    heroes = [
        presets.hero(hair_color='brown', outfit_color='blue'),
        presets.hero(hair_color='blonde', outfit_color='gold'),
        presets.hero(hair_color='black', outfit_color='red'),
        presets.hero(hair_color='red', outfit_color='green'),
    ]

    sprites = [h.render() for h in heroes]
    sheet = create_grid_sheet(sprites, columns=4, padding=2)
    sheet.save('output/char_hero_variants.png')
    print("Saved: output/char_hero_variants.png (4 hero variants)")


def demo_random_characters():
    """Demonstrate random character generation."""
    print("\n=== Random Characters ===")

    # Generate deterministic random characters
    sprites = []
    for seed in range(8):
        char = random_character(seed=seed * 100)
        sprites.append(char.render())

    sheet = create_grid_sheet(sprites, columns=4, padding=2)
    sheet.save('output/char_random.png')
    print("Saved: output/char_random.png (8 random characters)")


def demo_animation():
    """Demonstrate character animation."""
    print("\n=== Character Animation ===")

    char = presets.hero(seed=42)

    # Generate idle animation
    idle_anim = char.animate('idle', fps=8)
    idle_anim.save_spritesheet('output/char_idle_anim.png')
    print(f"Idle animation: {idle_anim.frame_count} frames")
    print("Saved: output/char_idle_anim.png")

    # Generate walk animation
    walk_anim = char.animate('walk', fps=8)
    walk_anim.save_spritesheet('output/char_walk_anim.png')
    print(f"Walk animation: {walk_anim.frame_count} frames")
    print("Saved: output/char_walk_anim.png")


def demo_party():
    """Create an RPG party."""
    print("\n=== RPG Party ===")

    party = [
        presets.warrior(hair_color='black', outfit_color='red'),
        presets.wizard(hair_color='white', outfit_color='purple'),
        presets.rogue(hair_color='brown', outfit_color='black'),
        presets.princess(hair_color='blonde', outfit_color='pink'),
    ]

    sprites = [char.render() for char in party]
    sheet = create_grid_sheet(sprites, columns=4, padding=4)
    sheet.save('output/char_party.png')
    print("Saved: output/char_party.png (warrior, wizard, rogue, princess)")


def demo_npc_crowd():
    """Create a crowd of NPCs."""
    print("\n=== NPC Crowd ===")

    npcs = []
    for i in range(16):
        # Mix of villagers and other NPCs
        if i % 4 == 0:
            npc = presets.child(seed=i)
        elif i % 4 == 1:
            npc = presets.elder(seed=i)
        else:
            npc = presets.villager(seed=i)
        npcs.append(npc)

    sprites = [npc.render() for npc in npcs]
    sheet = create_grid_sheet(sprites, columns=4, padding=2)
    sheet.save('output/char_npc_crowd.png')
    print("Saved: output/char_npc_crowd.png (16 NPCs)")


def demo_build_character_function():
    """Demonstrate the build_character convenience function."""
    print("\n=== build_character() Function ===")

    # Quick character creation with keyword arguments
    char = build_character(
        width=32,
        height=32,
        head='oval',
        body='muscular',
        hair='short',
        hair_color='black',
        eyes='round',
        eye_color='brown',
        skin='tan',
        outfit='gold',
        seed=999
    )

    sprite = char.render()
    sprite.save('output/char_quick.png')
    print(f"Created: {char}")
    print("Saved: output/char_quick.png")


def demo_equipment_sets():
    """Demonstrate equipment sets."""
    print("\n=== Equipment Sets ===")

    # Create characters with different equipment sets
    knight = (CharacterBuilder()
        .head('round')
        .body('chibi')
        .hair('short', color='brown')
        .eyes('round', color='blue')
        .equip_set('knight')
        .build())

    wizard = (CharacterBuilder()
        .head('round')
        .body('slim')
        .hair('long', color='white')
        .eyes('large', color='purple')
        .equip_set('wizard')
        .build())

    ranger = (CharacterBuilder()
        .head('oval')
        .body('slim')
        .hair('ponytail', color='brown')
        .eyes('round', color='green')
        .equip_set('ranger')
        .build())

    warrior = (CharacterBuilder()
        .head('square')
        .body('muscular')
        .hair('short', color='black')
        .eyes('round', color='brown')
        .equip_set('warrior')
        .build())

    rogue = (CharacterBuilder()
        .head('round')
        .body('slim')
        .hair('spiky', color='black')
        .eyes('round', color='brown')
        .equip_set('rogue')
        .build())

    royal = (CharacterBuilder()
        .head('heart')
        .body('slim')
        .hair('long', color='blonde')
        .eyes('sparkle', color='blue')
        .equip_set('royal')
        .build())

    sprites = [
        knight.render(),
        wizard.render(),
        ranger.render(),
        warrior.render(),
        rogue.render(),
        royal.render(),
    ]

    sheet = create_grid_sheet(sprites, columns=6, padding=2)
    sheet.save('output/char_equipment_sets.png')
    print("Saved: output/char_equipment_sets.png (knight, wizard, ranger, warrior, rogue, royal)")


def demo_custom_equipment():
    """Demonstrate individual equipment pieces."""
    print("\n=== Custom Equipment ===")

    # Mix and match equipment pieces
    char1 = (CharacterBuilder()
        .head('round')
        .body('chibi')
        .hair('spiky', color='red')
        .eyes('large', color='blue')
        .helmet('crown')
        .weapon('sword')
        .cape('royal')
        .build())

    char2 = (CharacterBuilder()
        .head('oval')
        .body('slim')
        .hair('long', color='silver')
        .eyes('angry', color='red')
        .helmet('hood')
        .armor('leather')
        .weapon('dagger')
        .build())

    char3 = (CharacterBuilder()
        .head('round')
        .body('muscular')
        .eyes('round', color='brown')
        .helmet('knight')
        .armor('breastplate')
        .legs('greaves')
        .boots('plate')
        .weapon('longsword')
        .shield('kite')
        .build())

    char4 = (CharacterBuilder()
        .head('round')
        .body('slim')
        .hair('fluffy', color='purple')
        .eyes('sparkle', color='purple')
        .helmet('wizard_hat')
        .armor('robe')
        .weapon('magic_staff')
        .build())

    sprites = [
        char1.render(),
        char2.render(),
        char3.render(),
        char4.render(),
    ]

    sheet = create_grid_sheet(sprites, columns=4, padding=2)
    sheet.save('output/char_custom_equipment.png')
    print("Saved: output/char_custom_equipment.png (4 custom equipment builds)")


def demo_weapons():
    """Demonstrate different weapon types."""
    print("\n=== Weapon Types ===")

    weapons = ['sword', 'longsword', 'dagger', 'axe', 'hammer', 'spear',
               'staff', 'magic_staff', 'wand', 'bow', 'crossbow']

    sprites = []
    for weapon_type in weapons:
        char = (CharacterBuilder()
            .head('round')
            .body('chibi')
            .eyes('round', color='brown')
            .weapon(weapon_type)
            .build())
        sprites.append(char.render())

    # Add one more to make a 4x3 grid
    char = (CharacterBuilder()
        .head('round')
        .body('chibi')
        .eyes('round', color='brown')
        .weapon('double_axe')
        .build())
    sprites.append(char.render())

    sheet = create_grid_sheet(sprites, columns=4, padding=2)
    sheet.save('output/char_weapons.png')
    print("Saved: output/char_weapons.png (12 weapon types)")


def demo_armor_types():
    """Demonstrate different armor types."""
    print("\n=== Armor Types ===")

    armor_combos = [
        ('simple', 'leather', 'pants', 'leather'),     # Light
        ('knight', 'breastplate', 'greaves', 'plate'), # Heavy
        ('wizard_hat', 'robe', 'pants', 'sandals'),    # Mage
        ('hood', 'chainmail', 'pants', 'leather'),     # Mixed
    ]

    sprites = []
    for helmet, chest, legs, boots in armor_combos:
        char = (CharacterBuilder()
            .head('round')
            .body('chibi')
            .eyes('round', color='brown')
            .helmet(helmet)
            .armor(chest)
            .legs(legs)
            .boots(boots)
            .build())
        sprites.append(char.render())

    sheet = create_grid_sheet(sprites, columns=4, padding=2)
    sheet.save('output/char_armor.png')
    print("Saved: output/char_armor.png (light, heavy, mage, mixed armor)")


def demo_accessories():
    """Demonstrate accessory equipment."""
    print("\n=== Accessories ===")

    # Characters with different accessories
    chars = []

    # Character with cape
    chars.append((CharacterBuilder()
        .head('round')
        .body('chibi')
        .hair('long', color='blonde')
        .eyes('large', color='blue')
        .cape('royal')
        .build()))

    # Character with tattered cape
    chars.append((CharacterBuilder()
        .head('round')
        .body('muscular')
        .hair('short', color='black')
        .eyes('angry', color='red')
        .cape('tattered')
        .build()))

    # Character with shield only
    chars.append((CharacterBuilder()
        .head('round')
        .body('chibi')
        .hair('spiky', color='brown')
        .eyes('round', color='green')
        .shield('tower')
        .build()))

    # Character with belt
    chars.append((CharacterBuilder()
        .head('round')
        .body('slim')
        .hair('ponytail', color='red')
        .eyes('round', color='brown')
        .belt('utility')
        .weapon('dagger')
        .build()))

    sprites = [char.render() for char in chars]
    sheet = create_grid_sheet(sprites, columns=4, padding=2)
    sheet.save('output/char_accessories.png')
    print("Saved: output/char_accessories.png (cape, tattered cape, shield, belt)")


def main():
    """Run all demos."""
    print("=" * 60)
    print("BITSY CHARACTER BUILDER DEMO")
    print("=" * 60)

    # Ensure output directory exists
    os.makedirs('output', exist_ok=True)

    demo_basic_builder()
    demo_full_customization()
    demo_expressions()
    demo_presets()
    demo_preset_customization()
    demo_random_characters()
    demo_animation()
    demo_party()
    demo_npc_crowd()
    demo_build_character_function()

    # Equipment demos
    demo_equipment_sets()
    demo_custom_equipment()
    demo_weapons()
    demo_armor_types()
    demo_accessories()

    print("\n" + "=" * 60)
    print("All demos complete! Check the output/ directory for results.")
    print("=" * 60)


if __name__ == '__main__':
    main()

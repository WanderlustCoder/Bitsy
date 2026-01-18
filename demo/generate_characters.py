import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from characters import CharacterBuilder, presets, list_presets, random_character
from export.spritesheet import create_grid_sheet


OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "characters")
SIZE = 48
SCALE_FACTOR = 4


def save_variants(sprite, base_name):
    path_1x = os.path.join(OUTPUT_DIR, f"{base_name}.png")
    path_4x = os.path.join(OUTPUT_DIR, f"{base_name}_4x.png")
    sprite.save(path_1x)
    sprite.scale(SCALE_FACTOR).save(path_4x)


def save_character(char, base_name):
    sprite = char.render()
    save_variants(sprite, base_name)
    return sprite


def save_sheet(sprites, base_name, columns, padding=2):
    sheet = create_grid_sheet(sprites, columns=columns, padding=padding)
    save_variants(sheet, base_name)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 01: RPG Party (equipment)
    party = [
        ("rpg_party_knight", (CharacterBuilder(width=SIZE, height=SIZE)
            .head('square')
            .body('muscular')
            .hair('short', color='brown')
            .eyes('round', color='blue')
            .equip_set('knight')
            .build())),
        ("rpg_party_wizard", presets.wizard(hair_color='white', outfit_color='purple', width=SIZE, height=SIZE)),
        ("rpg_party_rogue", presets.rogue(outfit_color='black', width=SIZE, height=SIZE)),
        ("rpg_party_princess", presets.princess(hair_color='blonde', width=SIZE, height=SIZE)),
    ]

    party_sprites = [save_character(char, name) for name, char in party]
    save_sheet(party_sprites, "sheet_rpg_party", columns=4, padding=2)

    # 02: NPC Variety
    npcs = [
        ("npc_villager", presets.villager(width=SIZE, height=SIZE)),
        ("npc_elder", presets.elder(width=SIZE, height=SIZE)),
        ("npc_child", presets.child(width=SIZE, height=SIZE)),
        ("npc_merchant", presets.hero(hair_color='black', outfit_color='brown', width=SIZE, height=SIZE)),
    ]

    npc_sprites = [save_character(char, name) for name, char in npcs]
    save_sheet(npc_sprites, "sheet_npc_variety", columns=4, padding=2)

    # 03: Fantasy Species
    species = [
        ("species_human_hero", presets.hero(width=SIZE, height=SIZE)),
        ("species_elf", (CharacterBuilder(width=SIZE, height=SIZE)
            .head('triangle')
            .body('slim')
            .hair('long', color='silver')
            .eyes('large', color='green', expression='neutral')
            .skin('pale')
            .outfit('green')
            .build())),
        ("species_dwarf", (CharacterBuilder(width=SIZE, height=SIZE)
            .head('square')
            .body('muscular')
            .hair('short', color='brown')
            .eyes('round', color='brown', expression='neutral')
            .skin('tan')
            .outfit('red')
            .build())),
        ("species_orc", presets.monster(skin_color='olive', width=SIZE, height=SIZE)),
    ]

    species_sprites = [save_character(char, name) for name, char in species]
    save_sheet(species_sprites, "sheet_fantasy_species", columns=4, padding=2)

    # 04: Expressions
    base_char = (CharacterBuilder(width=SIZE, height=SIZE)
        .head('round')
        .body('chibi')
        .hair('fluffy', color='brown')
        .eyes('large', color='blue')
        .outfit('blue')
        .build())

    expression_names = ['neutral', 'happy', 'sad', 'angry']
    expression_chars = [
        (f"expression_{expr}", base_char.with_expression(expr))
        for expr in expression_names
    ]

    expression_sprites = [save_character(char, name) for name, char in expression_chars]
    save_sheet(expression_sprites, "sheet_expressions", columns=4, padding=2)

    # 05: Equipment Showcase
    equipment_sets = [
        ("equip_knight", 'knight', 'square', 'muscular', 'short', 'brown', 'blue'),
        ("equip_wizard", 'wizard', 'oval', 'slim', 'long', 'white', 'purple'),
        ("equip_ranger", 'ranger', 'oval', 'slim', 'ponytail', 'brown', 'green'),
        ("equip_warrior", 'warrior', 'square', 'muscular', 'spiky', 'black', 'brown'),
        ("equip_rogue", 'rogue', 'triangle', 'slim', 'short', 'black', 'green'),
        ("equip_royal", 'royal', 'heart', 'slim', 'long', 'blonde', 'blue'),
    ]

    equipment_chars = []
    for base_name, equip, head, body, hair, hair_color, eye_color in equipment_sets:
        char = (CharacterBuilder(width=SIZE, height=SIZE)
            .head(head)
            .body(body)
            .hair(hair, color=hair_color)
            .eyes('round', color=eye_color)
            .equip_set(equip)
            .build())
        equipment_chars.append((base_name, char))

    equipment_sprites = [save_character(char, name) for name, char in equipment_chars]
    save_sheet(equipment_sprites, "sheet_equipment_showcase", columns=6, padding=2)


if __name__ == "__main__":
    main()

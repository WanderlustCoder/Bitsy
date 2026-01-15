"""
Bitsy Characters - Character assembly and templates.

This module provides tools for creating characters from parts:

- Character: Assembled character ready for rendering
- CharacterBuilder: Fluent builder for composing characters
- Presets: Ready-to-use character templates

Quick Start:
    from bitsy.characters import CharacterBuilder

    # Build a custom character
    char = (CharacterBuilder()
        .head('round')
        .body('chibi')
        .hair('spiky', color='brown')
        .eyes('large', color='blue')
        .build())

    sprite = char.render()
    sprite.save('my_character.png')

Using Presets:
    from bitsy.characters import presets

    hero = presets.hero()
    wizard = presets.wizard(hair_color='purple')
    random_npc = presets.random_character(seed=42)
"""

from characters.character import (
    Character,
    CharacterParts,
    CharacterPalettes,
    CharacterLayout,
)

from characters.builder import (
    CharacterBuilder,
    build_character,
    HAIR_PALETTES,
    OUTFIT_PALETTES,
    SKIN_PALETTES,
)

from characters import presets
from characters.presets import (
    list_presets,
    get_preset,
    random_character,
    # Individual presets
    hero,
    heroine,
    villager,
    wizard,
    warrior,
    rogue,
    knight,
    princess,
    monster,
    ghost,
    child,
    elder,
    cat_person,
)


__all__ = [
    # Core classes
    'Character',
    'CharacterParts',
    'CharacterPalettes',
    'CharacterLayout',

    # Builder
    'CharacterBuilder',
    'build_character',

    # Palette mappings
    'HAIR_PALETTES',
    'OUTFIT_PALETTES',
    'SKIN_PALETTES',

    # Presets module
    'presets',
    'list_presets',
    'get_preset',
    'random_character',

    # Individual preset functions
    'hero',
    'heroine',
    'villager',
    'wizard',
    'warrior',
    'rogue',
    'knight',
    'princess',
    'monster',
    'ghost',
    'child',
    'elder',
    'cat_person',
]

"""
Character Presets - Ready-to-use character templates.

Provides pre-configured characters for common archetypes like
heroes, villagers, wizards, etc.
"""

from typing import Dict, List, Optional

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from characters.character import Character
from characters.builder import CharacterBuilder


def hero(
    hair_color: str = 'brown',
    eye_color: str = 'blue',
    outfit_color: str = 'blue',
    width: int = 32,
    height: int = 32,
    seed: Optional[int] = None
) -> Character:
    """Create a hero character.

    Classic adventure hero with determined expression.

    Args:
        hair_color: Hair color (default: brown)
        eye_color: Eye color (default: blue)
        outfit_color: Outfit color (default: blue)
        width, height: Sprite dimensions
        seed: Random seed for determinism
    """
    return (CharacterBuilder(width=width, height=height, seed=seed)
        .style('chibi')
        .head('round')
        .body('simple')
        .hair('spiky', color=hair_color)
        .eyes('large', color=eye_color, expression='neutral')
        .skin('warm')
        .outfit(outfit_color)
        .build())


def heroine(
    hair_color: str = 'lavender',
    eye_color: str = 'green',
    outfit_color: str = 'red',
    width: int = 32,
    height: int = 32,
    seed: Optional[int] = None
) -> Character:
    """Create a heroine character.

    Female hero with flowing hair.

    Args:
        hair_color: Hair color (default: lavender)
        eye_color: Eye color (default: green)
        outfit_color: Outfit color (default: red)
        width, height: Sprite dimensions
        seed: Random seed for determinism
    """
    return (CharacterBuilder(width=width, height=height, seed=seed)
        .style('chibi')
        .head('oval')
        .body('slim')
        .hair('long', color=hair_color)
        .eyes('sparkle', color=eye_color, expression='neutral')
        .skin('pale')
        .outfit(outfit_color)
        .build())


def villager(
    hair_color: str = 'brown',
    outfit_color: str = 'green',
    width: int = 32,
    height: int = 32,
    seed: Optional[int] = None
) -> Character:
    """Create a villager/NPC character.

    Simple, friendly townsperson.

    Args:
        hair_color: Hair color (default: brown)
        outfit_color: Outfit color (default: green)
        width, height: Sprite dimensions
        seed: Random seed for determinism
    """
    return (CharacterBuilder(width=width, height=height, seed=seed)
        .style('chibi')
        .head('round')
        .body('chibi')
        .hair('short', color=hair_color)
        .eyes('round', color='brown', expression='happy')
        .skin('warm')
        .outfit(outfit_color)
        .build())


def wizard(
    hair_color: str = 'white',
    outfit_color: str = 'purple',
    width: int = 32,
    height: int = 32,
    seed: Optional[int] = None
) -> Character:
    """Create a wizard character.

    Mystical spellcaster with wise appearance.

    Args:
        hair_color: Hair color (default: white/gray)
        outfit_color: Outfit color (default: purple)
        width, height: Sprite dimensions
        seed: Random seed for determinism
    """
    return (CharacterBuilder(width=width, height=height, seed=seed)
        .style('chibi')
        .head('oval')
        .body('slim')
        .hair('long', color=hair_color)
        .eyes('round', color='purple', expression='neutral')
        .skin('pale')
        .outfit(outfit_color)
        .build())


def warrior(
    hair_color: str = 'black',
    outfit_color: str = 'red',
    width: int = 32,
    height: int = 32,
    seed: Optional[int] = None
) -> Character:
    """Create a warrior character.

    Strong fighter with determined look.

    Args:
        hair_color: Hair color (default: black)
        outfit_color: Outfit color (default: red)
        width, height: Sprite dimensions
        seed: Random seed for determinism
    """
    return (CharacterBuilder(width=width, height=height, seed=seed)
        .style('chibi')
        .head('square')
        .body('muscular')
        .hair('spiky', color=hair_color)
        .eyes('large', color='brown', expression='neutral')
        .skin('tan')
        .outfit(outfit_color)
        .build())


def rogue(
    hair_color: str = 'black',
    outfit_color: str = 'black',
    width: int = 32,
    height: int = 32,
    seed: Optional[int] = None
) -> Character:
    """Create a rogue/thief character.

    Sneaky character with sharp features.

    Args:
        hair_color: Hair color (default: black)
        outfit_color: Outfit color (default: black)
        width, height: Sprite dimensions
        seed: Random seed for determinism
    """
    return (CharacterBuilder(width=width, height=height, seed=seed)
        .style('chibi')
        .head('triangle')
        .body('slim')
        .hair('short', color=hair_color)
        .eyes('large', color='green', expression='neutral')
        .skin('cool')
        .outfit(outfit_color)
        .build())


def knight(
    outfit_color: str = 'gold',
    width: int = 32,
    height: int = 32,
    seed: Optional[int] = None
) -> Character:
    """Create a knight character.

    Armored warrior with noble bearing.

    Args:
        outfit_color: Armor color (default: gold)
        width, height: Sprite dimensions
        seed: Random seed for determinism
    """
    return (CharacterBuilder(width=width, height=height, seed=seed)
        .style('chibi')
        .head('square')
        .body('muscular')
        .hair('short', color='blonde')
        .eyes('round', color='blue', expression='neutral')
        .skin('warm')
        .outfit(outfit_color)
        .build())


def princess(
    hair_color: str = 'blonde',
    outfit_color: str = 'pink',
    width: int = 32,
    height: int = 32,
    seed: Optional[int] = None
) -> Character:
    """Create a princess character.

    Royal character with elegant appearance.

    Args:
        hair_color: Hair color (default: blonde)
        outfit_color: Dress color (default: pink)
        width, height: Sprite dimensions
        seed: Random seed for determinism
    """
    return (CharacterBuilder(width=width, height=height, seed=seed)
        .style('chibi')
        .head('heart')
        .body('slim')
        .hair('long', color=hair_color)
        .eyes('sparkle', color='blue', expression='happy')
        .skin('pale')
        .outfit(outfit_color)
        .build())


def monster(
    skin_color: str = 'olive',
    width: int = 32,
    height: int = 32,
    seed: Optional[int] = None
) -> Character:
    """Create a monster/enemy character.

    Generic enemy creature.

    Args:
        skin_color: Skin tone (default: olive/green)
        width, height: Sprite dimensions
        seed: Random seed for determinism
    """
    return (CharacterBuilder(width=width, height=height, seed=seed)
        .style('chibi')
        .head('square')
        .body('muscular')
        .hair('bald')
        .eyes('angry', color='red', expression='angry')
        .skin(skin_color)
        .outfit('brown')
        .build())


def ghost(
    width: int = 32,
    height: int = 32,
    seed: Optional[int] = None
) -> Character:
    """Create a ghost character.

    Spooky ethereal spirit.

    Args:
        width, height: Sprite dimensions
        seed: Random seed for determinism
    """
    return (CharacterBuilder(width=width, height=height, seed=seed)
        .style('chibi')
        .head('oval')
        .body('chibi')
        .hair('bald')
        .eyes('simple', color='blue', expression='sad')
        .skin('pale')
        .outfit('white')
        .build())


def child(
    hair_color: str = 'brown',
    outfit_color: str = 'yellow',
    width: int = 32,
    height: int = 32,
    seed: Optional[int] = None
) -> Character:
    """Create a child character.

    Small, cute kid.

    Args:
        hair_color: Hair color (default: brown)
        outfit_color: Outfit color (default: yellow)
        width, height: Sprite dimensions
        seed: Random seed for determinism
    """
    return (CharacterBuilder(width=width, height=height, seed=seed)
        .style('chibi')
        .head('chibi')
        .body('chibi')
        .hair('fluffy', color=hair_color)
        .eyes('sparkle', color='brown', expression='happy')
        .skin('warm')
        .outfit(outfit_color)
        .build())


def elder(
    outfit_color: str = 'brown',
    width: int = 32,
    height: int = 32,
    seed: Optional[int] = None
) -> Character:
    """Create an elder/old person character.

    Wise elderly character.

    Args:
        outfit_color: Outfit color (default: brown)
        width, height: Sprite dimensions
        seed: Random seed for determinism
    """
    return (CharacterBuilder(width=width, height=height, seed=seed)
        .style('chibi')
        .head('oval')
        .body('slim')
        .hair('bald')
        .eyes('round', color='brown', expression='neutral')
        .skin('warm')
        .outfit(outfit_color)
        .build())


def cat_person(
    hair_color: str = 'orange',
    width: int = 32,
    height: int = 32,
    seed: Optional[int] = None
) -> Character:
    """Create a cat-person character.

    Feline humanoid with playful appearance.

    Args:
        hair_color: Hair/fur color (default: orange)
        width, height: Sprite dimensions
        seed: Random seed for determinism
    """
    return (CharacterBuilder(width=width, height=height, seed=seed)
        .style('chibi')
        .head('triangle')
        .body('slim')
        .hair('fluffy', color=hair_color)
        .eyes('large', color='gold', expression='happy')
        .skin('warm')
        .outfit('brown')
        .build())


# Preset registry
PRESETS: Dict[str, callable] = {
    'hero': hero,
    'heroine': heroine,
    'villager': villager,
    'wizard': wizard,
    'warrior': warrior,
    'rogue': rogue,
    'knight': knight,
    'princess': princess,
    'monster': monster,
    'ghost': ghost,
    'child': child,
    'elder': elder,
    'cat_person': cat_person,
}


def list_presets() -> List[str]:
    """Get list of available preset names."""
    return list(PRESETS.keys())


def get_preset(name: str, **kwargs) -> Character:
    """Get a preset character by name.

    Args:
        name: Preset name
        **kwargs: Override default parameters

    Returns:
        Character instance
    """
    if name not in PRESETS:
        raise ValueError(f"Unknown preset: {name}. Available: {list_presets()}")
    return PRESETS[name](**kwargs)


def random_character(
    width: int = 32,
    height: int = 32,
    seed: Optional[int] = None
) -> Character:
    """Generate a fully randomized character.

    Args:
        width, height: Sprite dimensions
        seed: Random seed for determinism

    Returns:
        Randomized Character instance
    """
    return (CharacterBuilder(width=width, height=height, seed=seed)
        .randomize(hair=True, eyes=True, outfit=True, skin=True)
        .build())

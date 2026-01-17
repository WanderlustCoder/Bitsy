"""
Character generation tools.

Provides AI-accessible tools for generating characters,
with both high-level convenience and granular control.
"""

from typing import Optional, Tuple, Dict, Any, List
import time
import random

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from .definitions import tool
from .results import GenerationResult, ToolResult, SpriteType

from generators import generate_character as _gen_character
from characters import (
    CharacterBuilder,
    Character,
    get_preset,
    list_presets,
    random_character,
    Species,
    get_species_modifiers,
)
from core import Canvas


@tool(name="generate_sprite", category="generation", tags=["character", "creature", "item"])
def generate_sprite(
    description: str,
    sprite_type: str = "auto",
    style: str = "default",
    size: Tuple[int, int] = (32, 32),
    seed: Optional[int] = None,
) -> ToolResult:
    """Generate a sprite from a text description.

    This is the main entry point for sprite generation. It analyzes
    the description and routes to the appropriate generator.

    Args:
        description: Natural language description of the sprite
        sprite_type: Type hint (auto, character, creature, item, prop, structure)
        style: Visual style preset
        size: Output size as (width, height)
        seed: Random seed for reproducibility

    Returns:
        ToolResult with generated sprite
    """
    start_time = time.time()
    seed = seed or random.randint(0, 2**31)

    # Determine sprite type from description if auto
    if sprite_type == "auto":
        sprite_type = _infer_sprite_type(description)

    try:
        if sprite_type == "character":
            result = _generate_character_from_description(description, size, seed)
        elif sprite_type == "creature":
            result = _generate_creature_from_description(description, size, seed)
        elif sprite_type == "item":
            result = _generate_item_from_description(description, size, seed)
        elif sprite_type == "prop":
            result = _generate_prop_from_description(description, size, seed)
        else:
            # Default to character
            result = _generate_character_from_description(description, size, seed)

        result.generation_time_ms = (time.time() - start_time) * 1000
        return ToolResult.ok(result)

    except Exception as e:
        return ToolResult.fail(str(e), "GenerationError")


@tool(name="generate_character", category="generation", tags=["character"])
def generate_character(
    preset: Optional[str] = None,
    species: str = "human",
    hair_style: Optional[str] = None,
    hair_color: Optional[str] = None,
    skin_tone: Optional[str] = None,
    outfit: Optional[str] = None,
    size: Tuple[int, int] = (32, 32),
    seed: Optional[int] = None,
) -> ToolResult:
    """Generate a character with specific attributes.

    Args:
        preset: Character preset (hero, warrior, mage, etc.)
        species: Species type (human, elf, dwarf, orc, goblin)
        hair_style: Hair style name
        hair_color: Hair color name or hex
        skin_tone: Skin tone name
        outfit: Outfit style
        size: Output size as (width, height)
        seed: Random seed for reproducibility

    Returns:
        ToolResult with generated character
    """
    start_time = time.time()
    seed = seed or random.randint(0, 2**31)

    try:
        # Use preset if specified
        if preset and preset in list_presets():
            preset_func = get_preset(preset)
            character = preset_func(seed=seed)
        else:
            # Build custom character
            builder = CharacterBuilder(seed=seed)

            if species and species.lower() != "human":
                try:
                    species_enum = Species[species.upper()]
                    builder = builder.species(species_enum)
                except KeyError:
                    pass

            if hair_style:
                builder = builder.hair(hair_style, color=hair_color or "brown")
            if skin_tone:
                builder = builder.skin(skin_tone)
            if outfit:
                builder = builder.outfit(outfit)

            character = builder.build()

        canvas = character.render()

        result = GenerationResult(
            canvas=canvas,
            parameters={
                "preset": preset,
                "species": species,
                "hair_style": hair_style,
                "hair_color": hair_color,
                "skin_tone": skin_tone,
                "outfit": outfit,
            },
            seed=seed,
            sprite_type=SpriteType.CHARACTER,
            generator_name="generate_character",
            generation_time_ms=(time.time() - start_time) * 1000,
        )
        return ToolResult.ok(result)

    except Exception as e:
        return ToolResult.fail(str(e), "GenerationError")


@tool(name="list_character_presets", category="info", tags=["character"])
def list_character_presets() -> List[str]:
    """List available character presets.

    Returns:
        List of preset names
    """
    return list_presets()


@tool(name="list_species", category="info", tags=["character"])
def list_species() -> List[str]:
    """List available species types.

    Returns:
        List of species names
    """
    return [s.value for s in Species]


# =============================================================================
# Internal helpers
# =============================================================================

def _infer_sprite_type(description: str) -> str:
    """Infer sprite type from description."""
    desc_lower = description.lower()

    character_keywords = [
        "warrior", "mage", "knight", "rogue", "hero", "wizard",
        "person", "man", "woman", "boy", "girl", "character",
        "elf", "dwarf", "orc", "human", "villager", "npc",
    ]
    creature_keywords = [
        "slime", "goblin", "dragon", "skeleton", "monster", "beast",
        "creature", "demon", "ghost", "zombie", "spider", "wolf",
    ]
    item_keywords = [
        "sword", "potion", "key", "coin", "gem", "scroll",
        "weapon", "armor", "shield", "staff", "wand", "item",
    ]
    prop_keywords = [
        "chest", "barrel", "crate", "table", "chair", "tree",
        "rock", "bush", "flower", "lamp", "sign", "door",
    ]

    for kw in character_keywords:
        if kw in desc_lower:
            return "character"
    for kw in creature_keywords:
        if kw in desc_lower:
            return "creature"
    for kw in item_keywords:
        if kw in desc_lower:
            return "item"
    for kw in prop_keywords:
        if kw in desc_lower:
            return "prop"

    return "character"  # Default


def _generate_character_from_description(
    description: str,
    size: Tuple[int, int],
    seed: int
) -> GenerationResult:
    """Generate character from natural language description."""
    # Extract attributes from description
    desc_lower = description.lower()

    # Determine preset
    preset = None
    for p in list_presets():
        if p in desc_lower:
            preset = p
            break

    # Detect species
    species = "human"
    for s in Species:
        if s.value in desc_lower:
            species = s.value
            break

    # Build character
    if preset:
        character = get_preset(preset)(seed=seed)
    else:
        builder = CharacterBuilder(seed=seed)
        if species != "human":
            builder = builder.species(Species[species.upper()])
        character = builder.build()

    canvas = character.render()

    return GenerationResult(
        canvas=canvas,
        parameters={
            "description": description,
            "inferred_preset": preset,
            "inferred_species": species,
        },
        seed=seed,
        sprite_type=SpriteType.CHARACTER,
        generator_name="generate_sprite",
    )


def _generate_creature_from_description(
    description: str,
    size: Tuple[int, int],
    seed: int
) -> GenerationResult:
    """Generate creature from description."""
    from generators import generate_creature, list_creature_types

    desc_lower = description.lower()
    creature_type = "slime"  # Default

    for ct in list_creature_types():
        if ct in desc_lower:
            creature_type = ct
            break

    canvas = generate_creature(creature_type=creature_type, seed=seed)

    return GenerationResult(
        canvas=canvas,
        parameters={"description": description, "creature_type": creature_type},
        seed=seed,
        sprite_type=SpriteType.CREATURE,
        generator_name="generate_sprite",
    )


def _generate_item_from_description(
    description: str,
    size: Tuple[int, int],
    seed: int
) -> GenerationResult:
    """Generate item from description."""
    from generators import generate_item, list_item_types

    desc_lower = description.lower()
    item_type = "potion"  # Default

    for it in list_item_types():
        if it in desc_lower:
            item_type = it
            break

    canvas = generate_item(item_type=item_type, seed=seed)

    return GenerationResult(
        canvas=canvas,
        parameters={"description": description, "item_type": item_type},
        seed=seed,
        sprite_type=SpriteType.ITEM,
        generator_name="generate_sprite",
    )


def _generate_prop_from_description(
    description: str,
    size: Tuple[int, int],
    seed: int
) -> GenerationResult:
    """Generate prop from description."""
    from generators import generate_prop, list_prop_types

    desc_lower = description.lower()
    prop_type = "chest"  # Default

    for pt in list_prop_types():
        if pt in desc_lower:
            prop_type = pt
            break

    canvas = generate_prop(prop_type=prop_type, seed=seed)

    return GenerationResult(
        canvas=canvas,
        parameters={"description": description, "prop_type": prop_type},
        seed=seed,
        sprite_type=SpriteType.PROP,
        generator_name="generate_sprite",
    )

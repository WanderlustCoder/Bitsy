"""
Species templates for character generation.

Defines species-specific proportion and palette adjustments.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional


class Species(Enum):
    HUMAN = "human"
    ELF = "elf"
    DWARF = "dwarf"
    ORC = "orc"
    GOBLIN = "goblin"


@dataclass(frozen=True)
class ProportionAdjustments:
    """Scale adjustments applied to character layout proportions."""

    height_scale: float = 1.0
    head_scale: float = 1.0
    body_width_scale: float = 1.0
    limb_length_scale: float = 1.0


@dataclass(frozen=True)
class PaletteAdjustments:
    """Palette shift parameters for hue/saturation/value."""

    hue_degrees: float = 0.0
    sat_factor: float = 1.0
    val_factor: float = 1.0


@dataclass(frozen=True)
class SpeciesModifiers:
    """Container for species-specific adjustments."""

    proportions: ProportionAdjustments
    palette: Dict[str, PaletteAdjustments]


SPECIES_MODIFIERS: Dict[Species, SpeciesModifiers] = {
    Species.HUMAN: SpeciesModifiers(
        proportions=ProportionAdjustments(),
        palette={
            "skin": PaletteAdjustments(),
            "hair": PaletteAdjustments(),
            "outfit": PaletteAdjustments(),
        },
    ),
    Species.ELF: SpeciesModifiers(
        proportions=ProportionAdjustments(
            height_scale=1.05,
            head_scale=0.95,
            body_width_scale=0.95,
            limb_length_scale=1.05,
        ),
        palette={
            "skin": PaletteAdjustments(hue_degrees=-5.0, sat_factor=0.95, val_factor=1.05),
            "hair": PaletteAdjustments(),
            "outfit": PaletteAdjustments(),
        },
    ),
    Species.DWARF: SpeciesModifiers(
        proportions=ProportionAdjustments(
            height_scale=0.9,
            head_scale=1.05,
            body_width_scale=1.1,
            limb_length_scale=0.9,
        ),
        palette={
            "skin": PaletteAdjustments(hue_degrees=10.0, sat_factor=1.05, val_factor=0.95),
            "hair": PaletteAdjustments(),
            "outfit": PaletteAdjustments(),
        },
    ),
    Species.ORC: SpeciesModifiers(
        proportions=ProportionAdjustments(
            height_scale=1.05,
            head_scale=1.0,
            body_width_scale=1.1,
            limb_length_scale=1.0,
        ),
        palette={
            "skin": PaletteAdjustments(hue_degrees=90.0, sat_factor=1.1, val_factor=0.9),
            "hair": PaletteAdjustments(),
            "outfit": PaletteAdjustments(),
        },
    ),
    Species.GOBLIN: SpeciesModifiers(
        proportions=ProportionAdjustments(
            height_scale=0.85,
            head_scale=1.05,
            body_width_scale=0.9,
            limb_length_scale=0.85,
        ),
        palette={
            "skin": PaletteAdjustments(hue_degrees=100.0, sat_factor=1.2, val_factor=1.0),
            "hair": PaletteAdjustments(),
            "outfit": PaletteAdjustments(),
        },
    ),
}


def _normalize_species(species: Optional[object]) -> Species:
    if species is None:
        return Species.HUMAN
    if isinstance(species, Species):
        return species
    if isinstance(species, str):
        try:
            return Species[species.upper()]
        except KeyError as exc:
            available = ", ".join(s.name for s in Species)
            raise ValueError(f"Unknown species '{species}'. Available: {available}") from exc
    raise TypeError(f"Species must be Species or str, got {type(species).__name__}")


def get_species_modifiers(species: Optional[object] = None) -> SpeciesModifiers:
    """Return proportion and palette adjustments for a species."""
    normalized = _normalize_species(species)
    return SPECIES_MODIFIERS[normalized]

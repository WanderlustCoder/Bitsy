"""Tests for character species templates."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests.framework import TestCase
from characters.species import (
    Species,
    ProportionAdjustments,
    PaletteAdjustments,
    SpeciesModifiers,
    get_species_modifiers,
)


class TestSpeciesEnum(TestCase):
    """Tests for Species enum values."""

    def test_species_values(self):
        """Species values are lowercase strings."""
        self.assertEqual(Species.HUMAN.value, "human")
        self.assertEqual(Species.ELF.value, "elf")
        self.assertEqual(Species.DWARF.value, "dwarf")
        self.assertEqual(Species.ORC.value, "orc")
        self.assertEqual(Species.GOBLIN.value, "goblin")


class TestGetSpeciesModifiers(TestCase):
    """Tests for get_species_modifiers function."""

    def test_species_default(self):
        """Default species is human."""
        modifiers = get_species_modifiers()
        self.assertIsInstance(modifiers, SpeciesModifiers)
        self.assertEqual(modifiers, get_species_modifiers(Species.HUMAN))

    def test_species_accepts_string(self):
        """String species names are accepted."""
        modifiers = get_species_modifiers("elf")
        self.assertEqual(modifiers, get_species_modifiers(Species.ELF))

    def test_species_accepts_string_case(self):
        """String species names are case-insensitive."""
        for species in Species:
            self.assertEqual(get_species_modifiers(species.value), get_species_modifiers(species))
            self.assertEqual(get_species_modifiers(species.name), get_species_modifiers(species))

    def test_species_accepts_enum(self):
        """Species enum values are accepted."""
        for species in Species:
            modifiers = get_species_modifiers(species)
            self.assertIsInstance(modifiers, SpeciesModifiers)
            self.assertIsInstance(modifiers.proportions, ProportionAdjustments)

    def test_species_rejects_invalid_species(self):
        """Invalid species string raises ValueError."""
        with self.assertRaises(ValueError):
            get_species_modifiers("elflord")

    def test_species_rejects_invalid_type(self):
        """Invalid species type raises TypeError."""
        with self.assertRaises(TypeError):
            get_species_modifiers(123)

    def test_species_none_defaults_to_human(self):
        """None input returns human defaults."""
        self.assertEqual(get_species_modifiers(None), get_species_modifiers(Species.HUMAN))

    def test_species_modifier_structure(self):
        """Modifiers include proportion and palette adjustments."""
        modifiers = get_species_modifiers("orc")
        self.assertIsInstance(modifiers.proportions, ProportionAdjustments)
        self.assertIsInstance(modifiers.palette, dict)
        self.assertIn("skin", modifiers.palette)
        self.assertIn("hair", modifiers.palette)
        self.assertIn("outfit", modifiers.palette)
        self.assertIsInstance(modifiers.palette["skin"], PaletteAdjustments)

    def test_species_specific_adjustments(self):
        """Species modifiers apply distinct adjustments."""
        orc_mods = get_species_modifiers("orc")
        goblin_mods = get_species_modifiers("goblin")
        self.assertGreater(orc_mods.palette["skin"].hue_degrees, 0)
        self.assertGreater(goblin_mods.palette["skin"].hue_degrees, 0)

    def test_species_proportion_values(self):
        """Species proportion values match templates."""
        expected = {
            Species.HUMAN: ProportionAdjustments(
                height_scale=1.0,
                head_scale=1.0,
                body_width_scale=1.0,
                limb_length_scale=1.0,
            ),
            Species.ELF: ProportionAdjustments(
                height_scale=1.05,
                head_scale=0.95,
                body_width_scale=0.95,
                limb_length_scale=1.05,
            ),
            Species.DWARF: ProportionAdjustments(
                height_scale=0.9,
                head_scale=1.05,
                body_width_scale=1.1,
                limb_length_scale=0.9,
            ),
            Species.ORC: ProportionAdjustments(
                height_scale=1.05,
                head_scale=1.0,
                body_width_scale=1.1,
                limb_length_scale=1.0,
            ),
            Species.GOBLIN: ProportionAdjustments(
                height_scale=0.85,
                head_scale=1.05,
                body_width_scale=0.9,
                limb_length_scale=0.85,
            ),
        }
        for species, proportions in expected.items():
            self.assertEqual(get_species_modifiers(species).proportions, proportions)

    def test_species_proportion_characteristics(self):
        """Species proportions reflect expected height and build."""
        human = get_species_modifiers(Species.HUMAN).proportions
        elf = get_species_modifiers(Species.ELF).proportions
        dwarf = get_species_modifiers(Species.DWARF).proportions
        orc = get_species_modifiers(Species.ORC).proportions
        goblin = get_species_modifiers(Species.GOBLIN).proportions

        self.assertGreater(elf.height_scale, human.height_scale)
        self.assertGreater(orc.height_scale, human.height_scale)
        self.assertGreater(human.height_scale, dwarf.height_scale)
        self.assertGreater(human.height_scale, goblin.height_scale)
        self.assertGreater(elf.limb_length_scale, human.limb_length_scale)
        self.assertGreater(human.limb_length_scale, dwarf.limb_length_scale)
        self.assertGreater(human.limb_length_scale, goblin.limb_length_scale)
        self.assertGreater(dwarf.body_width_scale, human.body_width_scale)
        self.assertGreater(orc.body_width_scale, human.body_width_scale)
        self.assertGreater(human.body_width_scale, elf.body_width_scale)
        self.assertGreater(human.body_width_scale, goblin.body_width_scale)


class TestProportionAdjustments(TestCase):
    """Tests for ProportionAdjustments dataclass."""

    def test_species_proportion_defaults(self):
        """Default values match human proportions."""
        adjustments = ProportionAdjustments()
        self.assertEqual(adjustments.height_scale, 1.0)
        self.assertEqual(adjustments.head_scale, 1.0)
        self.assertEqual(adjustments.body_width_scale, 1.0)
        self.assertEqual(adjustments.limb_length_scale, 1.0)

    def test_species_proportion_custom_fields(self):
        """Custom values are stored on the dataclass."""
        adjustments = ProportionAdjustments(
            height_scale=0.9,
            head_scale=1.1,
            body_width_scale=0.95,
            limb_length_scale=0.8,
        )
        self.assertEqual(adjustments.height_scale, 0.9)
        self.assertEqual(adjustments.head_scale, 1.1)
        self.assertEqual(adjustments.body_width_scale, 0.95)
        self.assertEqual(adjustments.limb_length_scale, 0.8)


class TestPaletteAdjustments(TestCase):
    """Tests for PaletteAdjustments dataclass."""

    def test_species_palette_defaults(self):
        """Default values apply no palette changes."""
        adjustments = PaletteAdjustments()
        self.assertEqual(adjustments.hue_degrees, 0.0)
        self.assertEqual(adjustments.sat_factor, 1.0)
        self.assertEqual(adjustments.val_factor, 1.0)

    def test_species_palette_custom_fields(self):
        """Custom values are stored on the dataclass."""
        adjustments = PaletteAdjustments(hue_degrees=25.0, sat_factor=0.8, val_factor=1.2)
        self.assertEqual(adjustments.hue_degrees, 25.0)
        self.assertEqual(adjustments.sat_factor, 0.8)
        self.assertEqual(adjustments.val_factor, 1.2)

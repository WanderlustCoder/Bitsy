"""Tests for equipment system."""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.canvas import Canvas
from core.palette import Palette
from parts.equipment import (
    Equipment, EquipmentConfig, EquipmentSlot, DrawLayer, AttachmentPoint,
    MATERIAL_PALETTES, get_material_palette, list_materials,
    metal_iron, metal_gold, metal_silver, metal_bronze,
    leather_brown, leather_black, cloth_white,
    magic_blue, magic_purple, magic_green
)
from parts.armor import (
    create_helmet, create_chest_armor, create_leg_armor, create_boots,
    list_helmet_types, list_chest_armor_types, list_leg_armor_types, list_boot_types,
    SimpleHelmet, KnightHelmet, WizardHat, Crown, Hood,
    Breastplate, ChainMail, Robe, LeatherArmor,
    Greaves, Pants, PlateBoots, LeatherBoots, Sandals
)
from parts.weapons import (
    create_weapon, list_weapon_types,
    Sword, Longsword, Dagger, Staff, MagicStaff, Wand,
    Bow, Crossbow, Axe, DoubleAxe, Hammer, Spear
)
from parts.accessories import (
    create_cape, create_shield, create_belt,
    list_cape_types, list_shield_types, list_belt_types,
    SimpleCape, RoyalCape, TatteredCape,
    RoundShield, KiteShield, TowerShield, BucklerShield,
    SimpleBelt, UtilityBelt, Wings, Scarf, Backpack
)


class TestEquipmentSlots(unittest.TestCase):
    """Tests for equipment slot system."""

    def test_all_slots_exist(self):
        """Test all expected equipment slots exist."""
        expected_slots = ['HEAD', 'BODY', 'LEGS', 'FEET', 'HAND_RIGHT',
                         'HAND_LEFT', 'BACK', 'NECK', 'BELT']
        for slot_name in expected_slots:
            self.assertTrue(hasattr(EquipmentSlot, slot_name))

    def test_slot_values_unique(self):
        """Test all slot values are unique."""
        values = [slot.value for slot in EquipmentSlot]
        self.assertEqual(len(values), len(set(values)))


class TestDrawLayers(unittest.TestCase):
    """Tests for draw layer system."""

    def test_all_layers_exist(self):
        """Test all expected draw layers exist."""
        expected_layers = ['BACK_FAR', 'BACK', 'BODY_BACK', 'BODY',
                          'BODY_FRONT', 'FRONT', 'FRONT_FAR']
        for layer_name in expected_layers:
            self.assertTrue(hasattr(DrawLayer, layer_name))

    def test_layer_ordering(self):
        """Test layers are ordered correctly for rendering."""
        # Back layers should have lower values than front
        self.assertLess(DrawLayer.BACK_FAR.value, DrawLayer.FRONT_FAR.value)
        self.assertLess(DrawLayer.BACK.value, DrawLayer.FRONT.value)
        self.assertLess(DrawLayer.BODY.value, DrawLayer.FRONT.value)


class TestAttachmentPoint(unittest.TestCase):
    """Tests for attachment point configuration."""

    def test_default_attachment(self):
        """Test default attachment point values."""
        att = AttachmentPoint()
        self.assertEqual(att.offset_x, 0.0)
        self.assertEqual(att.offset_y, 0.0)
        self.assertEqual(att.scale_x, 1.0)
        self.assertEqual(att.scale_y, 1.0)
        self.assertEqual(att.rotation, 0.0)

    def test_custom_attachment(self):
        """Test custom attachment point values."""
        att = AttachmentPoint(
            offset_x=0.5,
            offset_y=-0.3,
            scale_x=1.2,
            scale_y=0.8,
            rotation=0.5
        )
        self.assertEqual(att.offset_x, 0.5)
        self.assertEqual(att.offset_y, -0.3)
        self.assertEqual(att.scale_x, 1.2)
        self.assertEqual(att.scale_y, 0.8)
        self.assertEqual(att.rotation, 0.5)


class TestEquipmentConfig(unittest.TestCase):
    """Tests for EquipmentConfig dataclass."""

    def test_default_config(self):
        """Test default equipment configuration."""
        config = EquipmentConfig()
        self.assertEqual(config.slot, EquipmentSlot.BODY)
        self.assertEqual(config.layer, DrawLayer.BODY)
        self.assertFalse(config.metallic)
        self.assertFalse(config.glowing)
        self.assertFalse(config.damaged)

    def test_custom_config(self):
        """Test custom equipment configuration."""
        config = EquipmentConfig(
            slot=EquipmentSlot.HEAD,
            layer=DrawLayer.FRONT,
            metallic=True,
            glowing=True,
            damaged=True
        )
        self.assertEqual(config.slot, EquipmentSlot.HEAD)
        self.assertEqual(config.layer, DrawLayer.FRONT)
        self.assertTrue(config.metallic)
        self.assertTrue(config.glowing)
        self.assertTrue(config.damaged)


class TestMaterialPalettes(unittest.TestCase):
    """Tests for material palette system."""

    def test_material_palettes_exist(self):
        """Test all expected material palettes exist."""
        expected_materials = ['iron', 'steel', 'gold', 'bronze', 'silver',
                             'leather', 'leather_brown', 'leather_black',
                             'cloth', 'cloth_white', 'magic_blue',
                             'magic_purple', 'magic_green']
        for material in expected_materials:
            self.assertIn(material, MATERIAL_PALETTES)

    def test_material_palette_functions(self):
        """Test material palette functions return Palette objects."""
        palette_funcs = [
            metal_iron, metal_gold, metal_silver, metal_bronze,
            leather_brown, leather_black, cloth_white,
            magic_blue, magic_purple, magic_green
        ]
        for func in palette_funcs:
            palette = func()
            self.assertIsInstance(palette, Palette)
            self.assertGreater(len(palette.colors), 0)

    def test_get_material_palette(self):
        """Test get_material_palette function."""
        iron = get_material_palette('iron')
        self.assertIsInstance(iron, Palette)

        gold = get_material_palette('gold')
        self.assertIsInstance(gold, Palette)

        # Test fallback to default
        unknown = get_material_palette('unknown_material')
        self.assertIsInstance(unknown, Palette)

    def test_list_materials(self):
        """Test list_materials function."""
        materials = list_materials()
        self.assertIsInstance(materials, list)
        self.assertIn('iron', materials)
        self.assertIn('gold', materials)


class TestBaseEquipment(unittest.TestCase):
    """Tests for base Equipment class."""

    def test_equipment_creation(self):
        """Test basic equipment creation."""
        equip = Equipment('test_equipment')
        self.assertEqual(equip.name, 'test_equipment')

    def test_equipment_with_config(self):
        """Test equipment creation with config."""
        config = EquipmentConfig(
            slot=EquipmentSlot.HEAD,
            metallic=True
        )
        equip = Equipment('golden_helm', config=config)
        self.assertEqual(equip.name, 'golden_helm')
        self.assertEqual(equip.equip_config.slot, EquipmentSlot.HEAD)
        self.assertTrue(equip.equip_config.metallic)

    def test_equipment_slot_property(self):
        """Test slot property."""
        config = EquipmentConfig(slot=EquipmentSlot.FEET)
        equip = Equipment('boots', config=config)
        self.assertEqual(equip.slot, EquipmentSlot.FEET)

    def test_equipment_layer_property(self):
        """Test layer property."""
        config = EquipmentConfig(layer=DrawLayer.FRONT)
        equip = Equipment('weapon', config=config)
        self.assertEqual(equip.layer, DrawLayer.FRONT)

    def test_equipment_attachment(self):
        """Test equipment attachment point calculation."""
        equip = Equipment('test')
        x, y, w, h = equip.get_attachment(16, 16, 10, 10)
        # Default attachment returns same position
        self.assertEqual(x, 16)
        self.assertEqual(y, 16)
        self.assertEqual(w, 10)
        self.assertEqual(h, 10)

    def test_equipment_attachment_with_offset(self):
        """Test attachment with offset."""
        config = EquipmentConfig(
            attachment=AttachmentPoint(offset_x=0.5, offset_y=-0.5)
        )
        equip = Equipment('test', config=config)
        x, y, w, h = equip.get_attachment(16, 16, 10, 10)
        self.assertEqual(x, 21)  # 16 + 0.5 * 10
        self.assertEqual(y, 11)  # 16 - 0.5 * 10

    def test_equipment_attachment_with_scale(self):
        """Test attachment with scale."""
        config = EquipmentConfig(
            attachment=AttachmentPoint(scale_x=1.5, scale_y=0.5)
        )
        equip = Equipment('test', config=config)
        x, y, w, h = equip.get_attachment(16, 16, 10, 10)
        self.assertEqual(w, 15)  # 10 * 1.5
        self.assertEqual(h, 5)   # 10 * 0.5


class TestHelmetTypes(unittest.TestCase):
    """Tests for helmet equipment."""

    def test_list_helmet_types(self):
        """Test listing available helmet types."""
        types = list_helmet_types()
        self.assertIn('simple', types)
        self.assertIn('knight', types)
        self.assertIn('wizard_hat', types)
        self.assertIn('crown', types)
        self.assertIn('hood', types)

    def test_create_all_helmet_types(self):
        """Test creating all helmet types via factory."""
        for helmet_type in list_helmet_types():
            helmet = create_helmet(helmet_type)
            self.assertIsNotNone(helmet)
            self.assertIsInstance(helmet, Equipment)

    def test_simple_helmet(self):
        """Test SimpleHelmet creation and rendering."""
        helmet = SimpleHelmet()
        self.assertEqual(helmet.slot, EquipmentSlot.HEAD)
        canvas = Canvas(32, 32)
        helmet.draw(canvas, 16, 8, 12, 8)

    def test_knight_helmet(self):
        """Test KnightHelmet with visor."""
        helmet = KnightHelmet()
        canvas = Canvas(32, 32)
        helmet.draw(canvas, 16, 8, 12, 10)

    def test_wizard_hat(self):
        """Test WizardHat creation."""
        hat = WizardHat()
        canvas = Canvas(32, 32)
        hat.draw(canvas, 16, 8, 14, 16)

    def test_crown(self):
        """Test Crown with gems."""
        crown = Crown()
        canvas = Canvas(32, 32)
        crown.draw(canvas, 16, 6, 12, 6)

    def test_hood(self):
        """Test Hood creation."""
        hood = Hood()
        canvas = Canvas(32, 32)
        hood.draw(canvas, 16, 10, 14, 12)


class TestChestArmorTypes(unittest.TestCase):
    """Tests for chest armor equipment."""

    def test_list_chest_armor_types(self):
        """Test listing available chest armor types."""
        types = list_chest_armor_types()
        self.assertIn('breastplate', types)
        self.assertIn('chainmail', types)
        self.assertIn('robe', types)
        self.assertIn('leather', types)

    def test_create_all_chest_types(self):
        """Test creating all chest armor types via factory."""
        for chest_type in list_chest_armor_types():
            chest = create_chest_armor(chest_type)
            self.assertIsNotNone(chest)
            self.assertIsInstance(chest, Equipment)

    def test_breastplate(self):
        """Test Breastplate creation and rendering."""
        armor = Breastplate()
        self.assertEqual(armor.slot, EquipmentSlot.BODY)
        canvas = Canvas(32, 32)
        armor.draw(canvas, 16, 20, 14, 12)

    def test_chainmail(self):
        """Test ChainMail pattern."""
        armor = ChainMail()
        canvas = Canvas(32, 32)
        armor.draw(canvas, 16, 20, 14, 12)

    def test_robe(self):
        """Test Robe creation."""
        robe = Robe()
        canvas = Canvas(32, 32)
        robe.draw(canvas, 16, 20, 16, 14)

    def test_leather_armor(self):
        """Test LeatherArmor creation."""
        armor = LeatherArmor()
        canvas = Canvas(32, 32)
        armor.draw(canvas, 16, 20, 14, 12)


class TestLegArmorTypes(unittest.TestCase):
    """Tests for leg armor equipment."""

    def test_list_leg_armor_types(self):
        """Test listing available leg armor types."""
        types = list_leg_armor_types()
        self.assertIn('greaves', types)
        self.assertIn('pants', types)

    def test_create_all_leg_types(self):
        """Test creating all leg armor types via factory."""
        for leg_type in list_leg_armor_types():
            legs = create_leg_armor(leg_type)
            self.assertIsNotNone(legs)
            self.assertIsInstance(legs, Equipment)

    def test_greaves(self):
        """Test Greaves creation."""
        greaves = Greaves()
        self.assertEqual(greaves.slot, EquipmentSlot.LEGS)
        canvas = Canvas(32, 32)
        greaves.draw(canvas, 16, 24, 10, 8)

    def test_pants(self):
        """Test Pants creation."""
        pants = Pants()
        canvas = Canvas(32, 32)
        pants.draw(canvas, 16, 24, 10, 8)


class TestBootTypes(unittest.TestCase):
    """Tests for boot equipment."""

    def test_list_boot_types(self):
        """Test listing available boot types."""
        types = list_boot_types()
        self.assertIn('plate', types)
        self.assertIn('leather', types)
        self.assertIn('sandals', types)

    def test_create_all_boot_types(self):
        """Test creating all boot types via factory."""
        for boot_type in list_boot_types():
            boots = create_boots(boot_type)
            self.assertIsNotNone(boots)
            self.assertIsInstance(boots, Equipment)

    def test_plate_boots(self):
        """Test PlateBoots creation."""
        boots = PlateBoots()
        self.assertEqual(boots.slot, EquipmentSlot.FEET)
        canvas = Canvas(32, 32)
        boots.draw(canvas, 16, 28, 10, 4)

    def test_leather_boots(self):
        """Test LeatherBoots creation."""
        boots = LeatherBoots()
        canvas = Canvas(32, 32)
        boots.draw(canvas, 16, 28, 10, 4)

    def test_sandals(self):
        """Test Sandals creation."""
        sandals = Sandals()
        canvas = Canvas(32, 32)
        sandals.draw(canvas, 16, 28, 10, 3)


class TestWeaponTypes(unittest.TestCase):
    """Tests for weapon equipment."""

    def test_list_weapon_types(self):
        """Test listing available weapon types."""
        types = list_weapon_types()
        expected = ['sword', 'longsword', 'dagger', 'staff', 'magic_staff',
                   'wand', 'bow', 'crossbow', 'axe', 'double_axe', 'hammer', 'spear']
        for weapon_type in expected:
            self.assertIn(weapon_type, types)

    def test_create_all_weapon_types(self):
        """Test creating all weapon types via factory."""
        for weapon_type in list_weapon_types():
            weapon = create_weapon(weapon_type)
            self.assertIsNotNone(weapon)
            self.assertIsInstance(weapon, Equipment)

    def test_sword(self):
        """Test Sword creation and rendering."""
        sword = Sword()
        self.assertEqual(sword.slot, EquipmentSlot.HAND_RIGHT)
        canvas = Canvas(32, 32)
        sword.draw(canvas, 24, 16, 6, 16)

    def test_longsword(self):
        """Test Longsword (larger sword)."""
        sword = Longsword()
        canvas = Canvas(32, 32)
        sword.draw(canvas, 24, 14, 8, 20)

    def test_dagger(self):
        """Test Dagger creation."""
        dagger = Dagger()
        canvas = Canvas(32, 32)
        dagger.draw(canvas, 24, 18, 4, 10)

    def test_staff(self):
        """Test Staff creation."""
        staff = Staff()
        canvas = Canvas(32, 32)
        staff.draw(canvas, 24, 10, 4, 24)

    def test_magic_staff(self):
        """Test MagicStaff with orb."""
        staff = MagicStaff()
        canvas = Canvas(32, 32)
        staff.draw(canvas, 24, 10, 6, 24)

    def test_wand(self):
        """Test Wand creation."""
        wand = Wand()
        canvas = Canvas(32, 32)
        wand.draw(canvas, 24, 16, 3, 12)

    def test_bow(self):
        """Test Bow creation."""
        bow = Bow()
        canvas = Canvas(32, 32)
        bow.draw(canvas, 26, 14, 6, 18)

    def test_crossbow(self):
        """Test Crossbow creation."""
        crossbow = Crossbow()
        canvas = Canvas(32, 32)
        crossbow.draw(canvas, 24, 16, 10, 12)

    def test_axe(self):
        """Test Axe creation."""
        axe = Axe()
        canvas = Canvas(32, 32)
        axe.draw(canvas, 24, 14, 8, 16)

    def test_double_axe(self):
        """Test DoubleAxe creation."""
        axe = DoubleAxe()
        canvas = Canvas(32, 32)
        axe.draw(canvas, 24, 12, 10, 20)

    def test_hammer(self):
        """Test Hammer creation."""
        hammer = Hammer()
        canvas = Canvas(32, 32)
        hammer.draw(canvas, 24, 12, 8, 18)

    def test_spear(self):
        """Test Spear creation."""
        spear = Spear()
        canvas = Canvas(32, 32)
        spear.draw(canvas, 24, 8, 4, 26)


class TestCapeTypes(unittest.TestCase):
    """Tests for cape accessories."""

    def test_list_cape_types(self):
        """Test listing available cape types."""
        types = list_cape_types()
        self.assertIn('simple', types)
        self.assertIn('royal', types)
        self.assertIn('tattered', types)

    def test_create_all_cape_types(self):
        """Test creating all cape types via factory."""
        for cape_type in list_cape_types():
            cape = create_cape(cape_type)
            self.assertIsNotNone(cape)
            self.assertIsInstance(cape, Equipment)

    def test_simple_cape(self):
        """Test SimpleCape creation."""
        cape = SimpleCape()
        self.assertEqual(cape.slot, EquipmentSlot.BACK)
        self.assertEqual(cape.layer, DrawLayer.BACK_FAR)
        canvas = Canvas(32, 32)
        cape.draw(canvas, 16, 16, 14, 18)

    def test_royal_cape(self):
        """Test RoyalCape with trim."""
        cape = RoyalCape()
        canvas = Canvas(32, 32)
        cape.draw(canvas, 16, 16, 16, 20)

    def test_tattered_cape(self):
        """Test TatteredCape creation."""
        cape = TatteredCape()
        canvas = Canvas(32, 32)
        cape.draw(canvas, 16, 16, 14, 18)


class TestShieldTypes(unittest.TestCase):
    """Tests for shield accessories."""

    def test_list_shield_types(self):
        """Test listing available shield types."""
        types = list_shield_types()
        self.assertIn('round', types)
        self.assertIn('kite', types)
        self.assertIn('tower', types)
        self.assertIn('buckler', types)

    def test_create_all_shield_types(self):
        """Test creating all shield types via factory."""
        for shield_type in list_shield_types():
            shield = create_shield(shield_type)
            self.assertIsNotNone(shield)
            self.assertIsInstance(shield, Equipment)

    def test_round_shield(self):
        """Test RoundShield creation."""
        shield = RoundShield()
        self.assertEqual(shield.slot, EquipmentSlot.HAND_LEFT)
        canvas = Canvas(32, 32)
        shield.draw(canvas, 8, 18, 8, 8)

    def test_kite_shield(self):
        """Test KiteShield creation."""
        shield = KiteShield()
        canvas = Canvas(32, 32)
        shield.draw(canvas, 8, 18, 8, 12)

    def test_tower_shield(self):
        """Test TowerShield creation."""
        shield = TowerShield()
        canvas = Canvas(32, 32)
        shield.draw(canvas, 6, 18, 10, 16)

    def test_buckler_shield(self):
        """Test BucklerShield (small)."""
        shield = BucklerShield()
        canvas = Canvas(32, 32)
        shield.draw(canvas, 8, 18, 6, 6)


class TestBeltTypes(unittest.TestCase):
    """Tests for belt accessories."""

    def test_list_belt_types(self):
        """Test listing available belt types."""
        types = list_belt_types()
        self.assertIn('simple', types)
        self.assertIn('utility', types)

    def test_create_all_belt_types(self):
        """Test creating all belt types via factory."""
        for belt_type in list_belt_types():
            belt = create_belt(belt_type)
            self.assertIsNotNone(belt)
            self.assertIsInstance(belt, Equipment)

    def test_simple_belt(self):
        """Test SimpleBelt creation."""
        belt = SimpleBelt()
        self.assertEqual(belt.slot, EquipmentSlot.BELT)
        canvas = Canvas(32, 32)
        belt.draw(canvas, 16, 22, 14, 3)

    def test_utility_belt(self):
        """Test UtilityBelt with pouches."""
        belt = UtilityBelt()
        canvas = Canvas(32, 32)
        belt.draw(canvas, 16, 22, 16, 4)


class TestOtherAccessories(unittest.TestCase):
    """Tests for other accessory types."""

    def test_wings(self):
        """Test Wings creation."""
        wings = Wings()
        self.assertEqual(wings.slot, EquipmentSlot.BACK)
        canvas = Canvas(32, 32)
        wings.draw(canvas, 16, 14, 24, 16)

    def test_scarf(self):
        """Test Scarf creation."""
        scarf = Scarf()
        self.assertEqual(scarf.slot, EquipmentSlot.NECK)
        canvas = Canvas(32, 32)
        scarf.draw(canvas, 16, 16, 10, 8)

    def test_backpack(self):
        """Test Backpack creation."""
        backpack = Backpack()
        self.assertEqual(backpack.slot, EquipmentSlot.BACK)
        canvas = Canvas(32, 32)
        backpack.draw(canvas, 10, 20, 8, 10)


class TestEquipmentIntegration(unittest.TestCase):
    """Integration tests for equipment with characters."""

    def test_full_armor_set(self):
        """Test creating a full armor set."""
        helmet = create_helmet('knight')
        chest = create_chest_armor('breastplate')
        legs = create_leg_armor('greaves')
        boots = create_boots('plate')

        # All should be valid equipment
        canvas = Canvas(32, 32)
        helmet.draw(canvas, 16, 8, 12, 10)
        chest.draw(canvas, 16, 18, 14, 12)
        legs.draw(canvas, 16, 24, 10, 6)
        boots.draw(canvas, 16, 28, 10, 4)

    def test_wizard_set(self):
        """Test creating a wizard equipment set."""
        hat = create_helmet('wizard_hat')
        robe = create_chest_armor('robe')
        boots = create_boots('sandals')
        staff = create_weapon('magic_staff')

        canvas = Canvas(32, 32)
        hat.draw(canvas, 16, 6, 14, 14)
        robe.draw(canvas, 16, 18, 16, 14)
        boots.draw(canvas, 16, 28, 10, 3)
        staff.draw(canvas, 24, 10, 6, 24)

    def test_warrior_set(self):
        """Test creating a warrior equipment set."""
        helmet = create_helmet('simple')
        chest = create_chest_armor('leather')
        weapon = create_weapon('axe')
        shield = create_shield('round')
        cape = create_cape('tattered')

        canvas = Canvas(32, 32)
        cape.draw(canvas, 16, 16, 14, 18)
        chest.draw(canvas, 16, 18, 14, 12)
        helmet.draw(canvas, 16, 8, 12, 8)
        weapon.draw(canvas, 24, 14, 8, 16)
        shield.draw(canvas, 8, 18, 8, 8)


class TestEquipmentWithCharacterBuilder(unittest.TestCase):
    """Tests for equipment integration with CharacterBuilder."""

    def test_character_with_equipment_set(self):
        """Test building character with equipment set."""
        from characters import CharacterBuilder

        char = (CharacterBuilder()
            .head('round')
            .body('chibi')
            .equip_set('knight')
            .build())

        self.assertIsNotNone(char)
        canvas = char.render()
        self.assertEqual(canvas.width, 32)
        self.assertEqual(canvas.height, 32)

    def test_character_with_individual_equipment(self):
        """Test building character with individual equipment pieces."""
        from characters import CharacterBuilder

        char = (CharacterBuilder()
            .head('round')
            .body('chibi')
            .helmet('crown')
            .weapon('staff')
            .cape('royal')
            .build())

        self.assertIsNotNone(char)
        canvas = char.render()
        self.assertEqual(canvas.width, 32)

    def test_all_equipment_sets(self):
        """Test all predefined equipment sets."""
        from characters import CharacterBuilder

        sets = ['knight', 'wizard', 'ranger', 'warrior', 'rogue', 'royal']
        for set_name in sets:
            char = (CharacterBuilder()
                .head('round')
                .body('chibi')
                .equip_set(set_name)
                .build())
            self.assertIsNotNone(char, f"Failed to build character with {set_name} set")
            canvas = char.render()
            self.assertEqual(canvas.width, 32)


if __name__ == '__main__':
    unittest.main()

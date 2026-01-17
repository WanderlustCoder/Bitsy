"""
CharacterBuilder - Fluent builder for assembling characters from parts.

Provides a clean, chainable API for creating characters piece by piece.
"""

from typing import Dict, Optional, Tuple, Union
import random

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.canvas import Canvas
from core.palette import Palette
from core.style import Style, get_style
from core.color import Color

from rig.skeleton import Skeleton, create_skeleton
from rig.pose import PoseLibrary, create_pose_library

from parts.base import PartConfig
from parts.heads import create_head, list_head_types
from parts.bodies import create_body, list_body_types
from parts.hair import create_hair, list_hair_types
from parts.eyes import create_eyes, get_eye_colors, list_eye_types

from characters.character import (
    Character, CharacterParts, CharacterPalettes, CharacterLayout, CharacterEquipment
)

from parts.equipment import EquipmentConfig, get_material_palette
from parts.armor import (
    create_helmet, create_chest_armor, create_leg_armor, create_boots,
    list_helmet_types, list_chest_armor_types, list_leg_armor_types, list_boot_types
)
from parts.weapons import create_weapon, list_weapon_types
from parts.accessories import (
    create_cape, create_shield, create_belt,
    list_cape_types, list_shield_types, list_belt_types
)


# Hair color palette mappings
HAIR_PALETTES = {
    'brown': lambda: Palette.hair_brown(),
    'lavender': lambda: Palette.hair_lavender(),
    'pink': lambda: Palette.hair_lavender().shift_all(hue_degrees=-30),
    'blue': lambda: Palette.hair_lavender().shift_all(hue_degrees=60),
    'red': lambda: Palette.hair_brown().shift_all(hue_degrees=-20, sat_factor=1.3),
    'blonde': lambda: Palette.hair_brown().shift_all(hue_degrees=10, val_factor=1.4),
    'black': lambda: Palette.hair_brown().shift_all(sat_factor=0.3, val_factor=0.3),
    'white': lambda: Palette.hair_brown().shift_all(sat_factor=0.1, val_factor=1.5),
    'green': lambda: Palette.hair_lavender().shift_all(hue_degrees=120),
    'purple': lambda: Palette.hair_lavender().shift_all(hue_degrees=-60),
    'orange': lambda: Palette.hair_brown().shift_all(hue_degrees=-10, sat_factor=1.4),
    'silver': lambda: Palette.hair_brown().shift_all(sat_factor=0.15, val_factor=1.3),
}

# Outfit color palette mappings
OUTFIT_PALETTES = {
    'blue': lambda: Palette.cloth_blue(),
    'red': lambda: Palette.cloth_blue().shift_all(hue_degrees=-120),
    'green': lambda: Palette.cloth_blue().shift_all(hue_degrees=80),
    'purple': lambda: Palette.cloth_blue().shift_all(hue_degrees=-60),
    'yellow': lambda: Palette.cloth_blue().shift_all(hue_degrees=160),
    'orange': lambda: Palette.cloth_blue().shift_all(hue_degrees=-150),
    'pink': lambda: Palette.cloth_blue().shift_all(hue_degrees=-90),
    'cyan': lambda: Palette.cloth_blue().shift_all(hue_degrees=40),
    'brown': lambda: Palette.cloth_blue().shift_all(hue_degrees=-140, sat_factor=0.6),
    'black': lambda: Palette.cloth_blue().shift_all(sat_factor=0.2, val_factor=0.3),
    'white': lambda: Palette.cloth_blue().shift_all(sat_factor=0.1, val_factor=1.5),
    'gold': lambda: Palette.metal_gold(),
}

# Skin palette mappings
SKIN_PALETTES = {
    'warm': lambda: Palette.skin_warm(),
    'cool': lambda: Palette.skin_cool(),
    'pale': lambda: Palette.skin_warm().shift_all(sat_factor=0.5, val_factor=1.2),
    'tan': lambda: Palette.skin_warm().shift_all(sat_factor=1.2, val_factor=0.85),
    'dark': lambda: Palette.skin_warm().shift_all(sat_factor=0.8, val_factor=0.6),
    'olive': lambda: Palette.skin_warm().shift_all(hue_degrees=15, sat_factor=0.7),
}


class CharacterBuilder:
    """Fluent builder for creating characters from parts.

    Usage:
        char = (CharacterBuilder()
            .style('chibi')
            .head('round')
            .body('chibi')
            .hair('spiky', color='brown')
            .eyes('large', color='blue', expression='happy')
            .skin('warm')
            .outfit('blue')
            .build())

        # Render the character
        sprite = char.render()

    All methods return self for chaining. Call build() at the end
    to create the final Character object.
    """

    def __init__(
        self,
        width: int = 32,
        height: int = 32,
        style: Union[str, Style] = 'chibi',
        seed: Optional[int] = None
    ):
        """Initialize the builder.

        Args:
            width: Sprite width in pixels
            height: Sprite height in pixels
            style: Art style name or Style object
            seed: Random seed for deterministic generation
        """
        self._width = width
        self._height = height
        self._seed = seed
        self._rng = random.Random(seed)

        # Style
        if isinstance(style, str):
            self._style = get_style(style)
            self._style_name = style
        else:
            self._style = style
            self._style_name = 'custom'

        # Part types (strings)
        self._head_type: str = 'chibi'
        self._body_type: str = 'chibi'
        self._hair_type: str = 'fluffy'
        self._eye_type: str = 'large'

        # Colors/palettes
        self._skin_palette: Palette = Palette.skin_warm()
        self._hair_palette: Palette = Palette.hair_lavender()
        self._outfit_palette: Palette = Palette.cloth_blue()
        self._eye_color: str = 'blue'
        self._expression: str = 'neutral'

        # Options
        self._has_bangs: bool = True

        # Skeleton
        self._skeleton_type: str = 'chibi'

        # Equipment (None = not equipped)
        self._helmet_type: Optional[str] = None
        self._chest_type: Optional[str] = None
        self._legs_type: Optional[str] = None
        self._boots_type: Optional[str] = None
        self._weapon_type: Optional[str] = None
        self._shield_type: Optional[str] = None
        self._cape_type: Optional[str] = None
        self._belt_type: Optional[str] = None

        # Equipment materials/palettes
        self._armor_material: str = 'iron'
        self._weapon_material: str = 'iron'
        self._cape_palette: Palette = Palette.cloth_blue()

    def style(self, style: Union[str, Style]) -> 'CharacterBuilder':
        """Set the art style.

        Args:
            style: Style name ('chibi', 'retro_nes', etc.) or Style object

        Available styles:
            - chibi: Big head, small body, cute proportions
            - retro_nes: 8-bit NES style
            - retro_snes: 16-bit SNES style
            - retro_gameboy: Gameboy 4-color palette
            - modern_hd: High detail modern pixel art
            - minimalist: Simple, clean lines
            - silhouette: Solid color silhouettes
        """
        if isinstance(style, str):
            self._style = get_style(style)
            self._style_name = style
        else:
            self._style = style
            self._style_name = 'custom'
        return self

    def size(self, width: int, height: int) -> 'CharacterBuilder':
        """Set sprite dimensions.

        Args:
            width: Sprite width in pixels
            height: Sprite height in pixels
        """
        self._width = width
        self._height = height
        return self

    def head(self, head_type: str) -> 'CharacterBuilder':
        """Set head shape.

        Args:
            head_type: Head type name

        Available types:
            - round: Simple circular head
            - oval: Egg-shaped, taller than wide
            - square: Blocky with rounded corners
            - chibi: Wide, large eye area
            - triangle: Pointed chin
            - heart: Wide at eyes, pointed chin
        """
        self._head_type = head_type
        return self

    def body(self, body_type: str) -> 'CharacterBuilder':
        """Set body type.

        Args:
            body_type: Body type name

        Available types:
            - chibi: Blob-like, cute proportions
            - simple: Basic trapezoid shape
            - muscular: Wide shoulders, defined chest
            - slim: Thin, elongated
        """
        self._body_type = body_type
        return self

    def hair(
        self,
        hair_type: str,
        color: Optional[str] = None,
        has_bangs: bool = True
    ) -> 'CharacterBuilder':
        """Set hair style and color.

        Args:
            hair_type: Hair style name
            color: Hair color name (optional)
            has_bangs: Whether to draw front bangs

        Available hair types:
            - fluffy: Rounded, soft
            - spiky: Anime spikes
            - long: Flowing, extends down
            - short: Short cap
            - bald: No hair
            - ponytail: Back ponytail
            - twintails: Side pigtails

        Available colors:
            brown, lavender, pink, blue, red, blonde, black,
            white, green, purple, orange, silver
        """
        self._hair_type = hair_type
        self._has_bangs = has_bangs

        if color:
            if color in HAIR_PALETTES:
                self._hair_palette = HAIR_PALETTES[color]()
            else:
                # Try to interpret as a palette shift
                self._hair_palette = Palette.hair_brown()
        return self

    def eyes(
        self,
        eye_type: str,
        color: Optional[str] = None,
        expression: Optional[str] = None
    ) -> 'CharacterBuilder':
        """Set eye style, color, and expression.

        Args:
            eye_type: Eye style name
            color: Eye color name (optional)
            expression: Facial expression (optional)

        Available eye types:
            - simple: Minimal dots
            - round: Classic round with iris
            - large: Anime-style large eyes
            - sparkle: Extra sparkly
            - closed: Eyes closed (curves)
            - angry: Narrowed with brows
            - sad: Droopy with worry

        Available colors:
            blue, green, brown, purple, red, gold

        Available expressions:
            neutral, happy, sad, angry
        """
        self._eye_type = eye_type
        if color:
            self._eye_color = color
        if expression:
            self._expression = expression
        return self

    def expression(self, expression: str) -> 'CharacterBuilder':
        """Set facial expression.

        Args:
            expression: Expression name ('neutral', 'happy', 'sad', 'angry')
        """
        self._expression = expression
        return self

    def skin(self, palette: Union[str, Palette]) -> 'CharacterBuilder':
        """Set skin color palette.

        Args:
            palette: Palette name or Palette object

        Available skin palettes:
            warm, cool, pale, tan, dark, olive
        """
        if isinstance(palette, str):
            if palette in SKIN_PALETTES:
                self._skin_palette = SKIN_PALETTES[palette]()
        else:
            self._skin_palette = palette
        return self

    def outfit(self, palette: Union[str, Palette]) -> 'CharacterBuilder':
        """Set outfit color palette.

        Args:
            palette: Palette name or Palette object

        Available outfit colors:
            blue, red, green, purple, yellow, orange,
            pink, cyan, brown, black, white, gold
        """
        if isinstance(palette, str):
            if palette in OUTFIT_PALETTES:
                self._outfit_palette = OUTFIT_PALETTES[palette]()
        else:
            self._outfit_palette = palette
        return self

    def skeleton(self, skeleton_type: str) -> 'CharacterBuilder':
        """Set skeleton type for animation.

        Args:
            skeleton_type: Skeleton preset name ('chibi', 'humanoid', 'simple')
        """
        self._skeleton_type = skeleton_type
        return self

    # ==================== Equipment Methods ====================

    def helmet(self, helmet_type: str, material: Optional[str] = None) -> 'CharacterBuilder':
        """Equip a helmet.

        Args:
            helmet_type: Helmet type name
            material: Material/palette name (optional)

        Available helmet types:
            simple, knight, wizard_hat, crown, hood
        """
        self._helmet_type = helmet_type
        if material:
            self._armor_material = material
        return self

    def armor(self, chest_type: str, material: Optional[str] = None) -> 'CharacterBuilder':
        """Equip chest armor.

        Args:
            chest_type: Armor type name
            material: Material/palette name (optional)

        Available armor types:
            breastplate, chainmail, robe, leather
        """
        self._chest_type = chest_type
        if material:
            self._armor_material = material
        return self

    def legs(self, leg_type: str) -> 'CharacterBuilder':
        """Equip leg armor.

        Args:
            leg_type: Leg armor type name

        Available types:
            greaves, pants
        """
        self._legs_type = leg_type
        return self

    def boots(self, boot_type: str) -> 'CharacterBuilder':
        """Equip boots.

        Args:
            boot_type: Boot type name

        Available types:
            plate, leather, sandals
        """
        self._boots_type = boot_type
        return self

    def weapon(self, weapon_type: str, material: Optional[str] = None) -> 'CharacterBuilder':
        """Equip a weapon (right hand).

        Args:
            weapon_type: Weapon type name
            material: Material/palette name (optional)

        Available weapon types:
            sword, longsword, dagger, staff, magic_staff, wand,
            bow, crossbow, axe, double_axe, hammer, spear
        """
        self._weapon_type = weapon_type
        if material:
            self._weapon_material = material
        return self

    def shield(self, shield_type: str, material: Optional[str] = None) -> 'CharacterBuilder':
        """Equip a shield (left hand).

        Args:
            shield_type: Shield type name
            material: Material/palette name (optional)

        Available shield types:
            round, kite, tower, buckler
        """
        self._shield_type = shield_type
        if material:
            self._armor_material = material
        return self

    def cape(self, cape_type: str, color: Optional[str] = None) -> 'CharacterBuilder':
        """Equip a cape/cloak.

        Args:
            cape_type: Cape type name
            color: Cape color (optional)

        Available cape types:
            simple, royal, tattered
        """
        self._cape_type = cape_type
        if color and color in OUTFIT_PALETTES:
            self._cape_palette = OUTFIT_PALETTES[color]()
        return self

    def belt(self, belt_type: str) -> 'CharacterBuilder':
        """Equip a belt.

        Args:
            belt_type: Belt type name

        Available belt types:
            simple, utility
        """
        self._belt_type = belt_type
        return self

    def equip_set(self, set_name: str) -> 'CharacterBuilder':
        """Equip a predefined equipment set.

        Args:
            set_name: Equipment set name

        Available sets:
            knight: Full plate armor with sword and shield
            wizard: Wizard hat, robe, and magic staff
            ranger: Leather armor, hood, and bow
            warrior: Breastplate, greaves, and longsword
            rogue: Leather armor and daggers
        """
        sets = {
            'knight': {
                'helmet': 'knight', 'chest': 'breastplate', 'legs': 'greaves',
                'boots': 'plate', 'weapon': 'sword', 'shield': 'kite',
                'material': 'iron'
            },
            'wizard': {
                'helmet': 'wizard_hat', 'chest': 'robe',
                'boots': 'sandals', 'weapon': 'magic_staff',
                'material': 'cloth'
            },
            'ranger': {
                'helmet': 'hood', 'chest': 'leather', 'legs': 'pants',
                'boots': 'leather', 'weapon': 'bow', 'cape': 'simple',
                'material': 'leather'
            },
            'warrior': {
                'chest': 'breastplate', 'legs': 'greaves',
                'boots': 'plate', 'weapon': 'longsword',
                'material': 'iron'
            },
            'rogue': {
                'helmet': 'hood', 'chest': 'leather', 'legs': 'pants',
                'boots': 'leather', 'weapon': 'dagger', 'belt': 'utility',
                'material': 'leather_black'
            },
            'royal': {
                'helmet': 'crown', 'chest': 'robe', 'cape': 'royal',
                'boots': 'leather', 'material': 'gold'
            },
        }

        if set_name not in sets:
            return self

        eq = sets[set_name]
        if 'helmet' in eq:
            self._helmet_type = eq['helmet']
        if 'chest' in eq:
            self._chest_type = eq['chest']
        if 'legs' in eq:
            self._legs_type = eq['legs']
        if 'boots' in eq:
            self._boots_type = eq['boots']
        if 'weapon' in eq:
            self._weapon_type = eq['weapon']
        if 'shield' in eq:
            self._shield_type = eq['shield']
        if 'cape' in eq:
            self._cape_type = eq['cape']
        if 'belt' in eq:
            self._belt_type = eq['belt']
        if 'material' in eq:
            self._armor_material = eq['material']
            self._weapon_material = eq['material']

        return self

    def randomize(
        self,
        hair: bool = True,
        eyes: bool = True,
        outfit: bool = True,
        skin: bool = False
    ) -> 'CharacterBuilder':
        """Randomize selected attributes.

        Args:
            hair: Randomize hair style and color
            eyes: Randomize eye color
            outfit: Randomize outfit color
            skin: Randomize skin tone
        """
        if hair:
            hair_types = [h for h in list_hair_types() if h != 'bald']
            self._hair_type = self._rng.choice(hair_types)
            self._hair_palette = HAIR_PALETTES[self._rng.choice(list(HAIR_PALETTES.keys()))]()

        if eyes:
            self._eye_color = self._rng.choice(['blue', 'green', 'brown', 'purple', 'red', 'gold'])

        if outfit:
            self._outfit_palette = OUTFIT_PALETTES[self._rng.choice(list(OUTFIT_PALETTES.keys()))]()

        if skin:
            self._skin_palette = SKIN_PALETTES[self._rng.choice(list(SKIN_PALETTES.keys()))]()

        return self

    def _build_equipment(self) -> Optional[CharacterEquipment]:
        """Build equipment from current configuration."""
        # Check if any equipment is set
        has_equipment = any([
            self._helmet_type, self._chest_type, self._legs_type,
            self._boots_type, self._weapon_type, self._shield_type,
            self._cape_type, self._belt_type
        ])

        if not has_equipment:
            return None

        # Get material palettes
        armor_palette = get_material_palette(self._armor_material)
        weapon_palette = get_material_palette(self._weapon_material)

        # Create equipment config
        armor_config = EquipmentConfig(
            base_color=armor_palette.get(1),
            palette=armor_palette,
            style=self._style,
            metallic=self._armor_material in ['iron', 'steel', 'gold', 'silver', 'bronze'],
            seed=self._rng.randint(0, 2**31)
        )

        weapon_config = EquipmentConfig(
            base_color=weapon_palette.get(1),
            palette=weapon_palette,
            style=self._style,
            metallic=self._weapon_material in ['iron', 'steel', 'gold', 'silver', 'bronze'],
            seed=self._rng.randint(0, 2**31)
        )

        cape_config = EquipmentConfig(
            base_color=self._cape_palette.get(1),
            palette=self._cape_palette,
            style=self._style,
            metallic=False,
            seed=self._rng.randint(0, 2**31)
        )

        # Create equipment pieces
        helmet = create_helmet(self._helmet_type, armor_config) if self._helmet_type else None
        chest = create_chest_armor(self._chest_type, armor_config) if self._chest_type else None
        legs = create_leg_armor(self._legs_type, armor_config) if self._legs_type else None
        boots = create_boots(self._boots_type, armor_config) if self._boots_type else None
        weapon = create_weapon(self._weapon_type, weapon_config) if self._weapon_type else None
        shield = create_shield(self._shield_type, armor_config) if self._shield_type else None
        cape = create_cape(self._cape_type, cape_config) if self._cape_type else None
        belt = create_belt(self._belt_type, armor_config) if self._belt_type else None

        return CharacterEquipment(
            helmet=helmet,
            chest=chest,
            legs=legs,
            boots=boots,
            weapon=weapon,
            shield=shield,
            cape=cape,
            belt=belt
        )

    def build(self) -> Character:
        """Build the final Character object.

        Returns:
            Fully configured Character ready for rendering.
        """
        # Create part configs
        head_config = PartConfig(
            base_color=self._skin_palette.get(2),
            palette=self._skin_palette,
            style=self._style,
            seed=self._rng.randint(0, 2**31)
        )

        body_config = PartConfig(
            base_color=self._outfit_palette.get(1),
            palette=self._outfit_palette,
            style=self._style,
            seed=self._rng.randint(0, 2**31)
        )

        hair_config = PartConfig(
            base_color=self._hair_palette.get(2),
            palette=self._hair_palette,
            style=self._style,
            seed=self._rng.randint(0, 2**31)
        )

        eye_config = PartConfig(
            base_color=self._skin_palette.get(2),
            style=self._style,
            seed=self._rng.randint(0, 2**31)
        )

        # Create parts
        head = create_head(self._head_type, head_config)
        body = create_body(self._body_type, body_config)
        hair = create_hair(self._hair_type, hair_config)
        hair.has_bangs = self._has_bangs

        eyes = create_eyes(self._eye_type, eye_config)
        eyes.eye_colors = get_eye_colors(self._eye_color)
        eyes.set_expression(self._expression)

        # Create equipment
        equipment = self._build_equipment()

        parts = CharacterParts(
            head=head,
            body=body,
            hair=hair,
            eyes=eyes,
            equipment=equipment
        )

        palettes = CharacterPalettes(
            skin=self._skin_palette,
            hair=self._hair_palette,
            outfit=self._outfit_palette
        )

        # Create layout based on style
        layout = CharacterLayout.for_style(self._style, self._width, self._height)

        # Create skeleton and pose library
        skeleton = create_skeleton(self._skeleton_type)
        pose_library = create_pose_library(self._skeleton_type)

        return Character(
            parts=parts,
            palettes=palettes,
            style=self._style,
            layout=layout,
            skeleton=skeleton,
            pose_library=pose_library,
            expression=self._expression,
            seed=self._seed
        )

    def render(self) -> Canvas:
        """Convenience method to build and render in one call.

        Returns:
            Canvas with rendered character.
        """
        return self.build().render()


# Convenience function
def build_character(**kwargs) -> Character:
    """Quick function to build a character.

    Args:
        **kwargs: Arguments passed to CharacterBuilder methods.

    Example:
        char = build_character(
            head='round',
            body='chibi',
            hair='spiky',
            hair_color='brown',
            eyes='large',
            eye_color='blue'
        )

    Returns:
        Built Character object.
    """
    builder = CharacterBuilder(
        width=kwargs.get('width', 32),
        height=kwargs.get('height', 32),
        style=kwargs.get('style', 'chibi'),
        seed=kwargs.get('seed')
    )

    if 'head' in kwargs:
        builder.head(kwargs['head'])
    if 'body' in kwargs:
        builder.body(kwargs['body'])
    if 'hair' in kwargs:
        builder.hair(
            kwargs['hair'],
            color=kwargs.get('hair_color'),
            has_bangs=kwargs.get('has_bangs', True)
        )
    if 'eyes' in kwargs:
        builder.eyes(
            kwargs['eyes'],
            color=kwargs.get('eye_color'),
            expression=kwargs.get('expression')
        )
    if 'skin' in kwargs:
        builder.skin(kwargs['skin'])
    if 'outfit' in kwargs:
        builder.outfit(kwargs['outfit'])

    return builder.build()

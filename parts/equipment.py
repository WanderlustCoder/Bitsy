"""
Equipment - Base classes for character equipment.

Equipment pieces are special parts that can be attached to characters
to customize their appearance. They support layering and attachment points.
"""

from enum import Enum
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.canvas import Canvas
from core.color import Color
from core.palette import Palette
from core.style import Style
from parts.base import Part, PartConfig


class EquipmentSlot(Enum):
    """Slots where equipment can be attached."""
    HEAD = 'head'           # Helmets, hats, crowns
    BODY = 'body'           # Armor, robes, shirts
    LEGS = 'legs'           # Pants, leg armor
    FEET = 'feet'           # Boots, shoes
    HAND_RIGHT = 'hand_r'   # Right-hand weapons/items
    HAND_LEFT = 'hand_l'    # Left-hand weapons/shields
    BACK = 'back'           # Capes, wings, backpacks
    NECK = 'neck'           # Necklaces, scarves
    BELT = 'belt'           # Belts, pouches


class DrawLayer(Enum):
    """Drawing layers for equipment (back to front)."""
    BACK_FAR = 0        # Behind everything (capes, wings)
    BACK = 1            # Behind body (back of weapons)
    BODY_BACK = 2       # Behind body parts but in front of back items
    BODY = 3            # At body level (armor)
    BODY_FRONT = 4      # In front of body (belts, pouches)
    FRONT = 5           # In front of character (weapons, shields)
    FRONT_FAR = 6       # Topmost layer (effects, auras)


@dataclass
class AttachmentPoint:
    """Defines where equipment attaches relative to a body part."""
    # Offset from part center (as fraction of part size)
    offset_x: float = 0.0
    offset_y: float = 0.0
    # Scale relative to part size
    scale_x: float = 1.0
    scale_y: float = 1.0
    # Rotation in radians
    rotation: float = 0.0


@dataclass
class EquipmentConfig(PartConfig):
    """Extended configuration for equipment."""
    # Equipment-specific options
    slot: EquipmentSlot = EquipmentSlot.BODY
    layer: DrawLayer = DrawLayer.BODY
    attachment: AttachmentPoint = field(default_factory=AttachmentPoint)

    # Visual style
    metallic: bool = False      # Use metallic shading
    glowing: bool = False       # Add glow effect
    damaged: bool = False       # Show wear/damage


class Equipment(Part):
    """Base class for equipment pieces.

    Equipment extends Part with:
    - Slot assignment (where it's worn)
    - Layer information (draw order)
    - Attachment points (positioning)
    """

    def __init__(self, name: str, config: Optional[EquipmentConfig] = None):
        # Convert PartConfig to EquipmentConfig if needed
        if config is None:
            config = EquipmentConfig()
        elif not isinstance(config, EquipmentConfig):
            # Upgrade PartConfig to EquipmentConfig
            config = EquipmentConfig(
                base_color=config.base_color,
                palette=config.palette,
                style=config.style,
                outline=config.outline,
                shading=config.shading,
                flip_x=config.flip_x,
                scale=config.scale,
                rotation=config.rotation,
                seed=config.seed
            )

        super().__init__(name, config)
        self.equip_config = config

    @property
    def slot(self) -> EquipmentSlot:
        """Get equipment slot."""
        return self.equip_config.slot

    @property
    def layer(self) -> DrawLayer:
        """Get draw layer."""
        return self.equip_config.layer

    def get_attachment(self, body_x: int, body_y: int,
                       body_w: int, body_h: int) -> Tuple[int, int, int, int]:
        """Calculate actual position based on attachment point.

        Args:
            body_x, body_y: Body part center position
            body_w, body_h: Body part dimensions

        Returns:
            (x, y, width, height) for equipment rendering
        """
        att = self.equip_config.attachment

        x = body_x + int(att.offset_x * body_w)
        y = body_y + int(att.offset_y * body_h)
        w = int(body_w * att.scale_x)
        h = int(body_h * att.scale_y)

        return x, y, w, h

    def _get_metallic_colors(self, num_levels: int = 4) -> List[Color]:
        """Get colors with metallic shading effect."""
        base = self.config.base_color
        r, g, b, a = base

        # Metallic has higher contrast and a bright highlight
        colors = []
        for i in range(num_levels):
            t = i / (num_levels - 1) if num_levels > 1 else 0.5

            if t < 0.3:
                # Deep shadow
                factor = 0.3 + t
            elif t < 0.7:
                # Mid tones
                factor = 0.6 + (t - 0.3) * 0.8
            else:
                # Bright highlight
                factor = 0.9 + (t - 0.7) * 0.5

            colors.append((
                min(255, int(r * factor)),
                min(255, int(g * factor)),
                min(255, int(b * factor)),
                a
            ))

        return colors

    def _get_colors(self, num_levels: int = 3) -> List[Color]:
        """Override to support metallic shading."""
        if self.equip_config.metallic:
            return self._get_metallic_colors(num_levels)
        return super()._get_colors(num_levels)


# Equipment palettes
def metal_iron() -> Palette:
    """Iron/steel metal palette."""
    return Palette([
        (60, 65, 75, 255),      # Dark steel
        (100, 105, 115, 255),   # Steel
        (140, 145, 155, 255),   # Light steel
        (180, 185, 195, 255),   # Highlight
    ])


def metal_gold() -> Palette:
    """Gold metal palette."""
    return Palette([
        (140, 100, 30, 255),    # Dark gold
        (200, 160, 50, 255),    # Gold
        (240, 200, 80, 255),    # Light gold
        (255, 240, 150, 255),   # Bright highlight
    ])


def metal_bronze() -> Palette:
    """Bronze metal palette."""
    return Palette([
        (100, 60, 30, 255),     # Dark bronze
        (150, 100, 50, 255),    # Bronze
        (190, 140, 80, 255),    # Light bronze
        (220, 180, 120, 255),   # Highlight
    ])


def metal_silver() -> Palette:
    """Silver metal palette."""
    return Palette([
        (100, 105, 115, 255),   # Dark silver
        (160, 165, 175, 255),   # Silver
        (200, 205, 215, 255),   # Light silver
        (240, 245, 255, 255),   # Bright highlight
    ])


def leather_brown() -> Palette:
    """Brown leather palette."""
    return Palette([
        (60, 40, 25, 255),      # Dark leather
        (100, 70, 45, 255),     # Leather
        (140, 100, 65, 255),    # Light leather
        (170, 130, 90, 255),    # Highlight
    ])


def leather_black() -> Palette:
    """Black leather palette."""
    return Palette([
        (25, 25, 30, 255),      # Deep black
        (45, 45, 50, 255),      # Black
        (70, 70, 75, 255),      # Dark gray
        (100, 100, 105, 255),   # Highlight
    ])


def cloth_white() -> Palette:
    """White cloth palette."""
    return Palette([
        (180, 180, 185, 255),   # Shadow
        (220, 220, 225, 255),   # Base
        (245, 245, 250, 255),   # Light
        (255, 255, 255, 255),   # Highlight
    ])


def magic_blue() -> Palette:
    """Magic blue glow palette."""
    return Palette([
        (20, 60, 150, 255),     # Deep blue
        (50, 100, 200, 255),    # Blue
        (100, 150, 240, 255),   # Light blue
        (180, 210, 255, 255),   # Glow
    ])


def magic_purple() -> Palette:
    """Magic purple glow palette."""
    return Palette([
        (80, 20, 120, 255),     # Deep purple
        (130, 50, 180, 255),    # Purple
        (180, 100, 220, 255),   # Light purple
        (220, 160, 255, 255),   # Glow
    ])


def magic_green() -> Palette:
    """Magic green glow palette."""
    return Palette([
        (20, 100, 40, 255),     # Deep green
        (50, 160, 70, 255),     # Green
        (100, 210, 120, 255),   # Light green
        (180, 255, 200, 255),   # Glow
    ])


# Material palette registry
MATERIAL_PALETTES = {
    'iron': metal_iron,
    'steel': metal_iron,
    'gold': metal_gold,
    'bronze': metal_bronze,
    'silver': metal_silver,
    'leather': leather_brown,
    'leather_brown': leather_brown,
    'leather_black': leather_black,
    'cloth': cloth_white,
    'cloth_white': cloth_white,
    'magic_blue': magic_blue,
    'magic_purple': magic_purple,
    'magic_green': magic_green,
}


def get_material_palette(material: str) -> Palette:
    """Get a material palette by name."""
    if material in MATERIAL_PALETTES:
        return MATERIAL_PALETTES[material]()
    # Default to iron
    return metal_iron()


def list_materials() -> List[str]:
    """List available material names."""
    return list(MATERIAL_PALETTES.keys())

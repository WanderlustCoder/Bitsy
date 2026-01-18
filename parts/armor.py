"""
Armor - Armor equipment pieces for characters.

Includes helmets, chest armor, leg armor, and boots.
"""

import math
from typing import List, Optional, Dict

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.canvas import Canvas
from core.color import Color
from core.palette import Palette
from parts.equipment import (
    Equipment, EquipmentConfig, EquipmentSlot, DrawLayer,
    AttachmentPoint, get_material_palette
)


# ==================== Helmets ====================

class Helmet(Equipment):
    """Base class for helmet equipment."""

    def __init__(self, name: str, config: Optional[EquipmentConfig] = None):
        if config is None:
            config = EquipmentConfig()
        config.slot = EquipmentSlot.HEAD
        config.layer = DrawLayer.FRONT
        super().__init__(name, config)


class SimpleHelmet(Helmet):
    """Basic rounded helmet."""

    def __init__(self, config: Optional[EquipmentConfig] = None):
        super().__init__('simple_helmet', config)

    def draw(self, canvas: Canvas, x: int, y: int, width: int, height: int) -> None:
        colors = self._get_colors(3)
        hw, hh = width // 2, height // 2

        # Main dome
        self._draw_shaded_ellipse(canvas, x, y - hh // 4, hw, hh * 3 // 4, colors)

        # Brim/rim at bottom
        rim_y = y + hh // 3
        canvas.fill_rect(x - hw, rim_y, width, height // 6, colors[1])

        if self.config.outline:
            outline = self._get_outline_color()
            canvas.draw_rect(x - hw, rim_y, width, height // 6, outline)


class KnightHelmet(Helmet):
    """Full knight helmet with visor."""

    def __init__(self, config: Optional[EquipmentConfig] = None):
        super().__init__('knight_helmet', config)

    def draw(self, canvas: Canvas, x: int, y: int, width: int, height: int) -> None:
        colors = self._get_colors(4)
        hw, hh = width // 2, height // 2

        # Main helmet body
        self._draw_shaded_ellipse(canvas, x, y - hh // 6, hw, hh * 2 // 3, colors[:3])

        # Visor (darker slit)
        visor_y = y
        visor_h = height // 5
        dark_color = (30, 30, 35, 255)
        canvas.fill_rect(x - hw + 2, visor_y - visor_h // 2, width - 4, visor_h, dark_color)

        # Top crest/ridge
        crest_y = y - hh * 2 // 3
        for i in range(3):
            cy = crest_y + i * 2
            cw = width // 4 - i * 2
            if cw > 0:
                canvas.fill_rect(x - cw // 2, cy, cw, 2, colors[2])

        if self.config.outline:
            outline = self._get_outline_color()
            # Visor outline
            canvas.draw_rect(x - hw + 2, visor_y - visor_h // 2, width - 4, visor_h, outline)


class WizardHat(Helmet):
    """Pointed wizard/mage hat."""

    def __init__(self, config: Optional[EquipmentConfig] = None):
        super().__init__('wizard_hat', config)
        self.equip_config.metallic = False

    def draw(self, canvas: Canvas, x: int, y: int, width: int, height: int) -> None:
        colors = self._get_colors(3)
        hw, hh = width // 2, height // 2

        # Cone (triangle)
        tip_y = y - hh - height // 3
        base_y = y

        # Draw cone as series of horizontal lines
        cone_height = base_y - tip_y
        for row in range(cone_height):
            t = row / cone_height if cone_height > 0 else 0
            row_width = int(width * t * 0.8)
            if row_width > 0:
                row_y = tip_y + row
                color_idx = min(int(t * len(colors)), len(colors) - 1)
                canvas.fill_rect(x - row_width // 2, row_y, row_width, 1, colors[color_idx])

        # Brim (wide ellipse)
        brim_h = height // 6
        self._draw_shaded_ellipse(canvas, x, base_y, hw + 4, brim_h, colors)


class Crown(Helmet):
    """Royal crown with points."""

    def __init__(self, config: Optional[EquipmentConfig] = None):
        super().__init__('crown', config)
        self.equip_config.metallic = True

    def draw(self, canvas: Canvas, x: int, y: int, width: int, height: int) -> None:
        colors = self._get_colors(4)
        hw, hh = width // 2, height // 2

        # Base band
        band_h = height // 3
        band_y = y
        canvas.fill_rect(x - hw, band_y, width, band_h, colors[1])

        # Points (5 points)
        num_points = 5
        point_spacing = width // num_points
        point_height = height // 2

        for i in range(num_points):
            px = x - hw + point_spacing // 2 + i * point_spacing
            # Draw triangle point
            for row in range(point_height):
                t = 1 - (row / point_height if point_height > 0 else 0)
                row_width = max(1, int(point_spacing * 0.6 * t))
                py = band_y - row
                color_idx = min(int((1 - t) * len(colors)), len(colors) - 1)
                canvas.fill_rect(px - row_width // 2, py, row_width, 1, colors[color_idx])

        # Gems on points (center point has bigger gem)
        gem_color = (200, 50, 50, 255)  # Ruby red
        for i in range(num_points):
            px = x - hw + point_spacing // 2 + i * point_spacing
            gem_y = band_y - point_height + 3
            gem_size = 3 if i == num_points // 2 else 2
            canvas.fill_circle(px, gem_y, gem_size, gem_color)

        if self.config.outline:
            outline = self._get_outline_color()
            canvas.draw_rect(x - hw, band_y, width, band_h, outline)


class Hood(Helmet):
    """Cloth hood."""

    def __init__(self, config: Optional[EquipmentConfig] = None):
        super().__init__('hood', config)
        self.equip_config.metallic = False

    def draw(self, canvas: Canvas, x: int, y: int, width: int, height: int) -> None:
        colors = self._get_colors(3)
        hw, hh = width // 2, height // 2

        # Main hood shape (rounded top, draping sides)
        self._draw_shaded_ellipse(canvas, x, y - hh // 4, hw + 2, hh * 3 // 4, colors)

        # Side drapes
        drape_h = height // 2
        for side in [-1, 1]:
            drape_x = x + side * (hw - 2)
            for row in range(drape_h):
                t = row / drape_h if drape_h > 0 else 0
                row_w = max(1, int(4 * (1 - t * 0.5)))
                drape_y = y + row
                canvas.fill_rect(drape_x - row_w // 2, drape_y, row_w, 1, colors[1])


# ==================== Chest Armor ====================

class ChestArmor(Equipment):
    """Base class for chest/body armor."""

    def __init__(self, name: str, config: Optional[EquipmentConfig] = None):
        if config is None:
            config = EquipmentConfig()
        config.slot = EquipmentSlot.BODY
        config.layer = DrawLayer.BODY
        super().__init__(name, config)


class Breastplate(ChestArmor):
    """Metal breastplate armor."""

    def __init__(self, config: Optional[EquipmentConfig] = None):
        super().__init__('breastplate', config)
        self.equip_config.metallic = True

    def draw(self, canvas: Canvas, x: int, y: int, width: int, height: int) -> None:
        colors = self._get_colors(4)
        hw, hh = width // 2, height // 2

        # Main plate (slightly curved rectangle)
        self._draw_shaded_ellipse(canvas, x, y, hw - 1, hh, colors[:3])

        # Center ridge/line
        ridge_color = colors[3] if len(colors) > 3 else colors[-1]
        canvas.fill_rect(x - 1, y - hh + 2, 2, height - 4, ridge_color)

        # Shoulder areas (small bumps)
        shoulder_w = width // 4
        for side in [-1, 1]:
            sx = x + side * (hw - shoulder_w // 2)
            sy = y - hh // 2
            self._draw_shaded_ellipse(canvas, sx, sy, shoulder_w // 2, hh // 4, colors[:3])


class ChainMail(ChestArmor):
    """Chain mail armor with ring pattern."""

    def __init__(self, config: Optional[EquipmentConfig] = None):
        super().__init__('chainmail', config)

    def draw(self, canvas: Canvas, x: int, y: int, width: int, height: int) -> None:
        colors = self._get_colors(3)
        hw, hh = width // 2, height // 2

        # Base shape
        canvas.fill_rect(x - hw + 1, y - hh + 1, width - 2, height - 2, colors[1])

        # Chain pattern (small circles)
        ring_spacing = 3
        ring_color = colors[2]
        dark_color = colors[0]

        for row in range(-hh + 2, hh - 1, ring_spacing):
            offset = (row // ring_spacing) % 2
            for col in range(-hw + 2 + offset, hw - 1, ring_spacing):
                rx, ry = x + col, y + row
                canvas.set_pixel(rx, ry, ring_color)
                canvas.set_pixel(rx + 1, ry, dark_color)
                canvas.set_pixel(rx, ry + 1, dark_color)

        if self.config.outline:
            outline = self._get_outline_color()
            canvas.draw_rect(x - hw + 1, y - hh + 1, width - 2, height - 2, outline)


class Robe(ChestArmor):
    """Cloth robe/tunic."""

    def __init__(self, config: Optional[EquipmentConfig] = None):
        super().__init__('robe', config)
        self.equip_config.metallic = False

    def draw(self, canvas: Canvas, x: int, y: int, width: int, height: int) -> None:
        colors = self._get_colors(3)
        hw, hh = width // 2, height // 2

        # Main robe shape (trapezoid, wider at bottom)
        for row in range(height):
            t = row / height if height > 0 else 0
            row_width = int(width * (0.7 + 0.3 * t))
            row_y = y - hh + row
            color_idx = min(int(t * len(colors) * 0.7), len(colors) - 1)
            canvas.fill_rect(x - row_width // 2, row_y, row_width, 1, colors[color_idx])

        # Collar/neckline (V shape)
        collar_depth = height // 4
        for row in range(collar_depth):
            t = row / collar_depth if collar_depth > 0 else 0
            gap = int(width * 0.2 * (1 - t))
            if gap > 0:
                canvas.fill_rect(x - gap // 2, y - hh + row, gap, 1, (0, 0, 0, 0))


class LeatherArmor(ChestArmor):
    """Leather armor/vest."""

    def __init__(self, config: Optional[EquipmentConfig] = None):
        super().__init__('leather_armor', config)

    def draw(self, canvas: Canvas, x: int, y: int, width: int, height: int) -> None:
        colors = self._get_colors(3)
        hw, hh = width // 2, height // 2

        # Main body
        self._draw_shaded_rect(canvas, x - hw + 1, y - hh + 1, width - 2, height - 2, colors)

        # Stitching detail
        stitch_color = colors[0]
        # Vertical stitches on sides
        for side in [-1, 1]:
            sx = x + side * (hw - 3)
            for sy in range(y - hh + 3, y + hh - 2, 3):
                canvas.set_pixel(sx, sy, stitch_color)


# ==================== Leg Armor ====================

class LegArmor(Equipment):
    """Base class for leg armor."""

    def __init__(self, name: str, config: Optional[EquipmentConfig] = None):
        if config is None:
            config = EquipmentConfig()
        config.slot = EquipmentSlot.LEGS
        config.layer = DrawLayer.BODY
        super().__init__(name, config)


class Greaves(LegArmor):
    """Metal leg greaves."""

    def __init__(self, config: Optional[EquipmentConfig] = None):
        super().__init__('greaves', config)
        self.equip_config.metallic = True

    def draw(self, canvas: Canvas, x: int, y: int, width: int, height: int) -> None:
        colors = self._get_colors(3)
        hw, hh = width // 2, height // 2

        # Two leg pieces
        leg_width = width // 3
        leg_spacing = width // 4

        for side in [-1, 1]:
            lx = x + side * leg_spacing
            self._draw_shaded_rect(canvas, lx - leg_width // 2, y - hh, leg_width, height, colors)

            # Knee guard (bump)
            knee_y = y - hh // 3
            self._draw_shaded_ellipse(canvas, lx, knee_y, leg_width // 2 + 1, height // 6, colors)


class Pants(LegArmor):
    """Cloth pants/trousers."""

    def __init__(self, config: Optional[EquipmentConfig] = None):
        super().__init__('pants', config)
        self.equip_config.metallic = False

    def draw(self, canvas: Canvas, x: int, y: int, width: int, height: int) -> None:
        colors = self._get_colors(3)
        hw, hh = width // 2, height // 2

        # Two leg shapes
        leg_width = width // 3
        leg_spacing = width // 4

        for side in [-1, 1]:
            lx = x + side * leg_spacing
            # Slightly tapered leg
            for row in range(height):
                t = row / height if height > 0 else 0
                row_width = int(leg_width * (1 - 0.2 * t))
                row_y = y - hh + row
                color_idx = min(int(t * 0.5 * len(colors)), len(colors) - 1)
                canvas.fill_rect(lx - row_width // 2, row_y, row_width, 1, colors[color_idx])


# ==================== Boots ====================

class Boots(Equipment):
    """Base class for boot equipment."""

    def __init__(self, name: str, config: Optional[EquipmentConfig] = None):
        if config is None:
            config = EquipmentConfig()
        config.slot = EquipmentSlot.FEET
        config.layer = DrawLayer.BODY
        super().__init__(name, config)


class PlateBoots(Boots):
    """Heavy plate armor boots."""

    def __init__(self, config: Optional[EquipmentConfig] = None):
        super().__init__('plate_boots', config)
        self.equip_config.metallic = True

    def draw(self, canvas: Canvas, x: int, y: int, width: int, height: int) -> None:
        colors = self._get_colors(3)
        hw, hh = width // 2, height // 2

        boot_width = width // 3
        boot_spacing = width // 4

        for side in [-1, 1]:
            bx = x + side * boot_spacing

            # Boot shaft
            shaft_h = height * 2 // 3
            self._draw_shaded_rect(canvas, bx - boot_width // 2, y - hh, boot_width, shaft_h, colors)

            # Foot part (wider)
            foot_h = height - shaft_h
            foot_w = boot_width + 2
            canvas.fill_rect(bx - foot_w // 2, y - hh + shaft_h, foot_w, foot_h, colors[1])


class LeatherBoots(Boots):
    """Leather boots."""

    def __init__(self, config: Optional[EquipmentConfig] = None):
        super().__init__('leather_boots', config)

    def draw(self, canvas: Canvas, x: int, y: int, width: int, height: int) -> None:
        colors = self._get_colors(3)
        hw, hh = width // 2, height // 2

        boot_width = width // 3
        boot_spacing = width // 4

        for side in [-1, 1]:
            bx = x + side * boot_spacing
            self._draw_shaded_ellipse(canvas, bx, y, boot_width // 2, hh, colors)


class Sandals(Boots):
    """Simple sandals."""

    def __init__(self, config: Optional[EquipmentConfig] = None):
        super().__init__('sandals', config)

    def draw(self, canvas: Canvas, x: int, y: int, width: int, height: int) -> None:
        colors = self._get_colors(2)
        hw, hh = width // 2, height // 2

        boot_spacing = width // 4

        for side in [-1, 1]:
            bx = x + side * boot_spacing

            # Sole
            sole_w = width // 4
            sole_h = height // 4
            canvas.fill_rect(bx - sole_w // 2, y + hh - sole_h, sole_w, sole_h, colors[0])

            # Straps
            strap_color = colors[1]
            canvas.fill_rect(bx - 1, y, 2, hh, strap_color)


# ==================== Factory Functions ====================

HELMET_TYPES = {
    'simple': SimpleHelmet,
    'knight': KnightHelmet,
    'wizard_hat': WizardHat,
    'crown': Crown,
    'hood': Hood,
}

CHEST_TYPES = {
    'breastplate': Breastplate,
    'chainmail': ChainMail,
    'robe': Robe,
    'leather': LeatherArmor,
}

LEG_TYPES = {
    'greaves': Greaves,
    'pants': Pants,
}

BOOT_TYPES = {
    'plate': PlateBoots,
    'leather': LeatherBoots,
    'sandals': Sandals,
}


def create_helmet(helmet_type: str, config: Optional[EquipmentConfig] = None) -> Helmet:
    """Create a helmet by type name."""
    if helmet_type not in HELMET_TYPES:
        raise ValueError(f"Unknown helmet type: {helmet_type}. Available: {list(HELMET_TYPES.keys())}")
    return HELMET_TYPES[helmet_type](config)


def create_chest_armor(armor_type: str, config: Optional[EquipmentConfig] = None) -> ChestArmor:
    """Create chest armor by type name."""
    if armor_type not in CHEST_TYPES:
        raise ValueError(f"Unknown chest armor type: {armor_type}. Available: {list(CHEST_TYPES.keys())}")
    return CHEST_TYPES[armor_type](config)


def create_leg_armor(armor_type: str, config: Optional[EquipmentConfig] = None) -> LegArmor:
    """Create leg armor by type name."""
    if armor_type not in LEG_TYPES:
        raise ValueError(f"Unknown leg armor type: {armor_type}. Available: {list(LEG_TYPES.keys())}")
    return LEG_TYPES[armor_type](config)


def create_boots(boot_type: str, config: Optional[EquipmentConfig] = None) -> Boots:
    """Create boots by type name."""
    if boot_type not in BOOT_TYPES:
        raise ValueError(f"Unknown boot type: {boot_type}. Available: {list(BOOT_TYPES.keys())}")
    return BOOT_TYPES[boot_type](config)


def list_helmet_types() -> List[str]:
    """List available helmet types."""
    return list(HELMET_TYPES.keys())


def list_chest_armor_types() -> List[str]:
    """List available chest armor types."""
    return list(CHEST_TYPES.keys())


def list_leg_armor_types() -> List[str]:
    """List available leg armor types."""
    return list(LEG_TYPES.keys())


def list_boot_types() -> List[str]:
    """List available boot types."""
    return list(BOOT_TYPES.keys())

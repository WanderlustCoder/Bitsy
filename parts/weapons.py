"""
Weapons - Weapon equipment pieces for characters.

Includes swords, staffs, bows, axes, and other weapons.
"""

import math
from typing import List, Optional

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.canvas import Canvas
from core.color import Color
from parts.equipment import (
    Equipment, EquipmentConfig, EquipmentSlot, DrawLayer,
    AttachmentPoint, get_material_palette
)


class Weapon(Equipment):
    """Base class for weapon equipment."""

    def __init__(self, name: str, config: Optional[EquipmentConfig] = None):
        if config is None:
            config = EquipmentConfig()
        config.slot = EquipmentSlot.HAND_RIGHT
        config.layer = DrawLayer.FRONT
        super().__init__(name, config)


# ==================== Swords ====================

class Sword(Weapon):
    """Basic sword."""

    def __init__(self, config: Optional[EquipmentConfig] = None):
        super().__init__('sword', config)
        self.equip_config.metallic = True

    def draw(self, canvas: Canvas, x: int, y: int, width: int, height: int) -> None:
        colors = self._get_colors(4)
        hw, hh = width // 2, height // 2

        # Blade (long thin rectangle, angled)
        blade_length = height
        blade_width = max(2, width // 4)

        # Draw blade
        blade_top = y - hh
        for row in range(blade_length):
            t = row / blade_length if blade_length > 0 else 0
            # Taper toward tip
            row_width = max(1, int(blade_width * (1 - t * 0.3)))
            row_y = blade_top + row

            # Shading across blade width
            color_idx = 1 if row_width > 1 else 2
            canvas.fill_rect(x - row_width // 2, row_y, row_width, 1, colors[color_idx])

            # Bright edge on one side
            if row_width > 1:
                canvas.set_pixel(x + row_width // 2 - 1, row_y, colors[3])

        # Crossguard
        guard_y = y + hh - height // 6
        guard_w = width
        guard_h = max(2, height // 8)
        guard_color = colors[0]  # Darker
        canvas.fill_rect(x - guard_w // 2, guard_y, guard_w, guard_h, guard_color)

        # Handle
        handle_color = (80, 50, 30, 255)  # Brown
        handle_y = guard_y + guard_h
        handle_h = height // 6
        handle_w = max(2, blade_width - 1)
        canvas.fill_rect(x - handle_w // 2, handle_y, handle_w, handle_h, handle_color)

        # Pommel
        pommel_y = handle_y + handle_h
        canvas.fill_circle(x, pommel_y + 1, 2, colors[1])


class Longsword(Weapon):
    """Large two-handed sword."""

    def __init__(self, config: Optional[EquipmentConfig] = None):
        super().__init__('longsword', config)
        self.equip_config.metallic = True

    def draw(self, canvas: Canvas, x: int, y: int, width: int, height: int) -> None:
        colors = self._get_colors(4)
        hw, hh = width // 2, height // 2

        # Longer, wider blade
        blade_length = int(height * 1.2)
        blade_width = max(3, width // 3)

        blade_top = y - hh - height // 5
        for row in range(blade_length):
            t = row / blade_length if blade_length > 0 else 0
            row_width = max(2, int(blade_width * (1 - t * 0.4)))
            row_y = blade_top + row

            # Fuller (groove) in center
            if row_width > 2 and t < 0.7:
                canvas.fill_rect(x - row_width // 2, row_y, row_width, 1, colors[1])
                canvas.set_pixel(x, row_y, colors[0])  # Dark center line
            else:
                canvas.fill_rect(x - row_width // 2, row_y, row_width, 1, colors[2])

        # Large crossguard
        guard_y = y + hh - height // 8
        guard_w = int(width * 1.2)
        canvas.fill_rect(x - guard_w // 2, guard_y, guard_w, 3, colors[0])

        # Long handle
        handle_color = (60, 40, 25, 255)
        handle_h = height // 4
        canvas.fill_rect(x - 1, guard_y + 3, 3, handle_h, handle_color)

        # Pommel
        canvas.fill_circle(x, guard_y + 3 + handle_h + 2, 3, colors[1])


class Dagger(Weapon):
    """Short dagger/knife."""

    def __init__(self, config: Optional[EquipmentConfig] = None):
        super().__init__('dagger', config)
        self.equip_config.metallic = True

    def draw(self, canvas: Canvas, x: int, y: int, width: int, height: int) -> None:
        colors = self._get_colors(3)
        hw, hh = width // 2, height // 2

        # Short blade
        blade_length = height // 2
        blade_width = max(2, width // 5)

        blade_top = y - hh
        for row in range(blade_length):
            t = row / blade_length if blade_length > 0 else 0
            row_width = max(1, int(blade_width * (1 - t * 0.5)))
            row_y = blade_top + row
            canvas.fill_rect(x - row_width // 2, row_y, row_width, 1, colors[1])
            if row_width > 1:
                canvas.set_pixel(x + row_width // 2 - 1, row_y, colors[2])

        # Small guard
        guard_y = blade_top + blade_length
        canvas.fill_rect(x - width // 4, guard_y, width // 2, 2, colors[0])

        # Handle
        handle_color = (70, 45, 25, 255)
        canvas.fill_rect(x - 1, guard_y + 2, 2, height // 4, handle_color)


# ==================== Staffs ====================

class Staff(Weapon):
    """Wooden staff."""

    def __init__(self, config: Optional[EquipmentConfig] = None):
        super().__init__('staff', config)
        self.equip_config.metallic = False

    def draw(self, canvas: Canvas, x: int, y: int, width: int, height: int) -> None:
        colors = self._get_colors(3)
        hw, hh = width // 2, height // 2

        # Wood colors
        wood_dark = (60, 40, 25, 255)
        wood_mid = (100, 70, 45, 255)
        wood_light = (130, 95, 65, 255)

        # Long shaft
        shaft_h = int(height * 1.3)
        shaft_w = max(2, width // 6)
        shaft_top = y - hh - height // 4

        for row in range(shaft_h):
            t = row / shaft_h if shaft_h > 0 else 0
            row_y = shaft_top + row
            # Wood grain shading
            color = wood_mid if (row % 4) < 2 else wood_dark
            canvas.fill_rect(x - shaft_w // 2, row_y, shaft_w, 1, color)
            # Highlight edge
            if shaft_w > 1:
                canvas.set_pixel(x + shaft_w // 2 - 1, row_y, wood_light)


class MagicStaff(Weapon):
    """Staff with magic crystal/orb."""

    def __init__(self, config: Optional[EquipmentConfig] = None):
        super().__init__('magic_staff', config)

    def draw(self, canvas: Canvas, x: int, y: int, width: int, height: int) -> None:
        colors = self._get_colors(4)
        hw, hh = width // 2, height // 2

        # Wood staff
        wood_color = (80, 55, 35, 255)
        shaft_h = int(height * 1.1)
        shaft_w = max(2, width // 5)
        shaft_top = y - hh

        canvas.fill_rect(x - shaft_w // 2, shaft_top, shaft_w, shaft_h, wood_color)

        # Ornate top (curved prongs)
        prong_y = shaft_top - height // 8
        for side in [-1, 1]:
            px = x + side * (shaft_w)
            for row in range(height // 6):
                t = row / (height // 6) if height > 0 else 0
                py = prong_y + row
                offset = int(side * shaft_w * (1 - t))
                canvas.set_pixel(x + offset, py, wood_color)

        # Magic orb/crystal at top
        orb_y = prong_y - 2
        orb_r = max(3, width // 4)

        # Orb glow (outer)
        glow_color = (colors[2][0], colors[2][1], colors[2][2], 128)
        canvas.fill_circle(x, orb_y, orb_r + 1, glow_color)

        # Orb core
        self._draw_shaded_circle(canvas, x, orb_y, orb_r, colors)


class Wand(Weapon):
    """Short magic wand."""

    def __init__(self, config: Optional[EquipmentConfig] = None):
        super().__init__('wand', config)

    def draw(self, canvas: Canvas, x: int, y: int, width: int, height: int) -> None:
        colors = self._get_colors(3)
        hw, hh = width // 2, height // 2

        # Short shaft
        wood_color = (90, 60, 40, 255)
        shaft_h = height // 2
        shaft_w = max(2, width // 6)

        # Tapered shaft
        for row in range(shaft_h):
            t = row / shaft_h if shaft_h > 0 else 0
            row_width = max(1, int(shaft_w * (1 - t * 0.3)))
            row_y = y - hh // 2 + row
            canvas.fill_rect(x - row_width // 2, row_y, row_width, 1, wood_color)

        # Glowing tip
        tip_y = y - hh // 2 - 2
        tip_r = max(2, width // 5)
        self._draw_shaded_circle(canvas, x, tip_y, tip_r, colors)


# ==================== Bows ====================

class Bow(Weapon):
    """Wooden bow."""

    def __init__(self, config: Optional[EquipmentConfig] = None):
        super().__init__('bow', config)
        self.equip_config.slot = EquipmentSlot.HAND_LEFT

    def draw(self, canvas: Canvas, x: int, y: int, width: int, height: int) -> None:
        colors = self._get_colors(3)
        hw, hh = width // 2, height // 2

        wood_dark = (70, 45, 25, 255)
        wood_light = (110, 80, 50, 255)

        # Curved bow shape
        bow_height = int(height * 1.1)
        curve_depth = width // 3

        for row in range(bow_height):
            t = (row / bow_height) if bow_height > 0 else 0
            # Parabolic curve
            curve = int(curve_depth * (1 - 4 * (t - 0.5) ** 2))
            bx = x - curve
            by = y - bow_height // 2 + row

            color = wood_dark if (row % 3) == 0 else wood_light
            canvas.set_pixel(bx, by, color)
            if curve > 1:
                canvas.set_pixel(bx + 1, by, wood_dark)

        # String
        string_color = (200, 190, 170, 255)
        string_x = x - curve_depth + 2
        for row in range(bow_height):
            by = y - bow_height // 2 + row
            canvas.set_pixel(string_x, by, string_color)


class Crossbow(Weapon):
    """Mechanical crossbow."""

    def __init__(self, config: Optional[EquipmentConfig] = None):
        super().__init__('crossbow', config)

    def draw(self, canvas: Canvas, x: int, y: int, width: int, height: int) -> None:
        colors = self._get_colors(3)
        hw, hh = width // 2, height // 2

        wood_color = (80, 55, 35, 255)
        metal_color = (120, 125, 135, 255)

        # Stock (horizontal)
        stock_w = width
        stock_h = max(2, height // 6)
        stock_y = y
        canvas.fill_rect(x - stock_w // 2, stock_y, stock_w, stock_h, wood_color)

        # Bow arms (at front)
        arm_y = stock_y
        arm_w = width // 4
        arm_h = height // 2

        for side in [-1, 1]:
            ax = x - hw + (0 if side == -1 else width - arm_w)
            for row in range(arm_h):
                t = row / arm_h if arm_h > 0 else 0
                curve = int(side * arm_w * 0.5 * t)
                ay = arm_y - arm_h // 2 + row
                canvas.set_pixel(ax + curve, ay, metal_color)

        # String
        string_y = arm_y - arm_h // 4
        canvas.draw_line(x - hw, string_y, x + hw, string_y, (180, 170, 150, 255))


# ==================== Axes ====================

class Axe(Weapon):
    """Battle axe."""

    def __init__(self, config: Optional[EquipmentConfig] = None):
        super().__init__('axe', config)
        self.equip_config.metallic = True

    def draw(self, canvas: Canvas, x: int, y: int, width: int, height: int) -> None:
        colors = self._get_colors(4)
        hw, hh = width // 2, height // 2

        # Handle
        handle_color = (70, 45, 25, 255)
        handle_w = max(2, width // 6)
        handle_h = int(height * 0.9)
        handle_top = y - hh + height // 10
        canvas.fill_rect(x - handle_w // 2, handle_top, handle_w, handle_h, handle_color)

        # Axe head (curved blade)
        head_y = handle_top + height // 8
        head_h = height // 2
        head_w = width // 2

        for row in range(head_h):
            t = row / head_h if head_h > 0 else 0
            # Curved edge
            curve = int(head_w * math.sin(t * math.pi))
            row_y = head_y + row

            if curve > 0:
                canvas.fill_rect(x, row_y, curve, 1, colors[1])
                # Sharp edge highlight
                canvas.set_pixel(x + curve - 1, row_y, colors[3])

        # Back of head
        canvas.fill_rect(x - 2, head_y, 3, head_h, colors[0])


class DoubleAxe(Weapon):
    """Double-headed battle axe."""

    def __init__(self, config: Optional[EquipmentConfig] = None):
        super().__init__('double_axe', config)
        self.equip_config.metallic = True

    def draw(self, canvas: Canvas, x: int, y: int, width: int, height: int) -> None:
        colors = self._get_colors(4)
        hw, hh = width // 2, height // 2

        # Handle
        handle_color = (70, 45, 25, 255)
        handle_w = max(2, width // 6)
        handle_h = int(height * 0.85)
        handle_top = y - hh + height // 10
        canvas.fill_rect(x - handle_w // 2, handle_top, handle_w, handle_h, handle_color)

        # Double axe heads
        head_y = handle_top + height // 10
        head_h = height // 3
        head_w = width // 3

        for side in [-1, 1]:
            for row in range(head_h):
                t = row / head_h if head_h > 0 else 0
                curve = int(head_w * math.sin(t * math.pi))
                row_y = head_y + row

                if curve > 0:
                    if side == 1:
                        canvas.fill_rect(x + 1, row_y, curve, 1, colors[1])
                        canvas.set_pixel(x + curve, row_y, colors[3])
                    else:
                        canvas.fill_rect(x - curve, row_y, curve, 1, colors[1])
                        canvas.set_pixel(x - curve, row_y, colors[3])


# ==================== Other Weapons ====================

class Hammer(Weapon):
    """War hammer."""

    def __init__(self, config: Optional[EquipmentConfig] = None):
        super().__init__('hammer', config)
        self.equip_config.metallic = True

    def draw(self, canvas: Canvas, x: int, y: int, width: int, height: int) -> None:
        colors = self._get_colors(3)
        hw, hh = width // 2, height // 2

        # Handle
        handle_color = (70, 45, 25, 255)
        handle_w = max(2, width // 5)
        handle_h = int(height * 0.85)
        handle_top = y - hh + height // 8
        canvas.fill_rect(x - handle_w // 2, handle_top, handle_w, handle_h, handle_color)

        # Hammer head (rectangular)
        head_w = width * 2 // 3
        head_h = height // 3
        head_y = handle_top
        head_x = x - head_w // 2

        self._draw_shaded_rect(canvas, head_x, head_y, head_w, head_h, colors)


class Spear(Weapon):
    """Long spear."""

    def __init__(self, config: Optional[EquipmentConfig] = None):
        super().__init__('spear', config)

    def draw(self, canvas: Canvas, x: int, y: int, width: int, height: int) -> None:
        colors = self._get_colors(3)
        hw, hh = width // 2, height // 2

        # Long shaft
        wood_color = (90, 65, 40, 255)
        shaft_h = int(height * 1.4)
        shaft_w = max(2, width // 8)
        shaft_top = y - hh - height // 3

        canvas.fill_rect(x - shaft_w // 2, shaft_top + height // 5, shaft_w, shaft_h, wood_color)

        # Spear tip (triangle)
        tip_h = height // 4
        tip_w = width // 4
        tip_top = shaft_top

        for row in range(tip_h):
            t = row / tip_h if tip_h > 0 else 0
            row_width = max(1, int(tip_w * t))
            row_y = tip_top + row
            canvas.fill_rect(x - row_width // 2, row_y, row_width, 1, colors[1])
            if row_width > 1:
                canvas.set_pixel(x + row_width // 2 - 1, row_y, colors[2])


# ==================== Factory Functions ====================

WEAPON_TYPES = {
    'sword': Sword,
    'longsword': Longsword,
    'dagger': Dagger,
    'staff': Staff,
    'magic_staff': MagicStaff,
    'wand': Wand,
    'bow': Bow,
    'crossbow': Crossbow,
    'axe': Axe,
    'double_axe': DoubleAxe,
    'hammer': Hammer,
    'spear': Spear,
}


def create_weapon(weapon_type: str, config: Optional[EquipmentConfig] = None) -> Weapon:
    """Create a weapon by type name."""
    if weapon_type not in WEAPON_TYPES:
        raise ValueError(f"Unknown weapon type: {weapon_type}. Available: {list(WEAPON_TYPES.keys())}")
    return WEAPON_TYPES[weapon_type](config)


def list_weapon_types() -> List[str]:
    """List available weapon types."""
    return list(WEAPON_TYPES.keys())

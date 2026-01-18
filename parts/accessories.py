"""
Accessories - Accessory equipment pieces for characters.

Includes capes, shields, belts, and other accessories.
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
    AttachmentPoint
)


# ==================== Capes ====================

class Cape(Equipment):
    """Base class for capes/cloaks."""

    def __init__(self, name: str, config: Optional[EquipmentConfig] = None):
        if config is None:
            config = EquipmentConfig()
        config.slot = EquipmentSlot.BACK
        config.layer = DrawLayer.BACK_FAR
        super().__init__(name, config)


class SimpleCape(Cape):
    """Basic cloth cape."""

    def __init__(self, config: Optional[EquipmentConfig] = None):
        super().__init__('simple_cape', config)

    def draw(self, canvas: Canvas, x: int, y: int, width: int, height: int) -> None:
        colors = self._get_colors(3)
        hw, hh = width // 2, height // 2

        # Cape shape (wider at bottom, flowing)
        cape_height = int(height * 1.2)

        for row in range(cape_height):
            t = row / cape_height if cape_height > 0 else 0
            # Wider at bottom
            row_width = int(width * (0.6 + 0.5 * t))
            row_y = y - hh // 2 + row

            # Color gradient (darker at edges)
            color_idx = min(int(t * 0.5 * len(colors)), len(colors) - 1)
            canvas.fill_rect(x - row_width // 2, row_y, row_width, 1, colors[color_idx])

            # Edge shading
            if row_width > 4:
                canvas.set_pixel(x - row_width // 2, row_y, colors[0])
                canvas.set_pixel(x + row_width // 2 - 1, row_y, colors[0])


class RoyalCape(Cape):
    """Fancy royal cape with fur trim."""

    def __init__(self, config: Optional[EquipmentConfig] = None):
        super().__init__('royal_cape', config)

    def draw(self, canvas: Canvas, x: int, y: int, width: int, height: int) -> None:
        colors = self._get_colors(3)
        hw, hh = width // 2, height // 2

        # Main cape
        cape_height = int(height * 1.3)
        for row in range(cape_height):
            t = row / cape_height if cape_height > 0 else 0
            row_width = int(width * (0.7 + 0.4 * t))
            row_y = y - hh // 2 + row
            color_idx = min(int(t * 0.6 * len(colors)), len(colors) - 1)
            canvas.fill_rect(x - row_width // 2, row_y, row_width, 1, colors[color_idx])

        # Fur trim at neck (white/cream)
        fur_color = (240, 235, 220, 255)
        fur_dark = (200, 195, 180, 255)
        trim_w = int(width * 0.8)
        trim_h = height // 6

        for row in range(trim_h):
            t = row / trim_h if trim_h > 0 else 0
            row_w = int(trim_w * (1 - t * 0.3))
            row_y = y - hh // 2 + row

            # Fuzzy texture
            color = fur_color if (row + x) % 2 == 0 else fur_dark
            canvas.fill_rect(x - row_w // 2, row_y, row_w, 1, color)


class TatteredCape(Cape):
    """Worn, torn cape."""

    def __init__(self, config: Optional[EquipmentConfig] = None):
        super().__init__('tattered_cape', config)

    def draw(self, canvas: Canvas, x: int, y: int, width: int, height: int) -> None:
        colors = self._get_colors(3)
        hw, hh = width // 2, height // 2

        cape_height = int(height * 1.1)

        for row in range(cape_height):
            t = row / cape_height if cape_height > 0 else 0
            base_width = int(width * (0.6 + 0.4 * t))
            row_y = y - hh // 2 + row

            # Irregular edges (tattered look)
            noise = self._random_int(-2, 2) if t > 0.5 else 0
            row_width = max(1, base_width + noise)

            # Skip some pixels at bottom for holes
            if t > 0.7 and self._random() > 0.7:
                continue

            color_idx = min(int(t * 0.5 * len(colors)), len(colors) - 1)
            canvas.fill_rect(x - row_width // 2, row_y, row_width, 1, colors[color_idx])


# ==================== Shields ====================

class Shield(Equipment):
    """Base class for shields."""

    def __init__(self, name: str, config: Optional[EquipmentConfig] = None):
        if config is None:
            config = EquipmentConfig()
        config.slot = EquipmentSlot.HAND_LEFT
        config.layer = DrawLayer.FRONT
        super().__init__(name, config)


class RoundShield(Shield):
    """Circular shield."""

    def __init__(self, config: Optional[EquipmentConfig] = None):
        super().__init__('round_shield', config)

    def draw(self, canvas: Canvas, x: int, y: int, width: int, height: int) -> None:
        colors = self._get_colors(4)
        hw, hh = width // 2, height // 2

        radius = min(hw, hh)

        # Main shield body
        self._draw_shaded_circle(canvas, x, y, radius, colors[:3])

        # Boss (center bump)
        boss_r = radius // 3
        boss_colors = colors[1:] if len(colors) > 1 else colors
        self._draw_shaded_circle(canvas, x, y, boss_r, boss_colors)

        # Rivets around edge
        rivet_color = colors[-1] if colors else (180, 180, 190, 255)
        num_rivets = 8
        for i in range(num_rivets):
            angle = i * 2 * math.pi / num_rivets
            rx = x + int((radius - 2) * math.cos(angle))
            ry = y + int((radius - 2) * math.sin(angle))
            canvas.set_pixel(rx, ry, rivet_color)


class KiteShield(Shield):
    """Kite-shaped medieval shield."""

    def __init__(self, config: Optional[EquipmentConfig] = None):
        super().__init__('kite_shield', config)
        self.equip_config.metallic = True

    def draw(self, canvas: Canvas, x: int, y: int, width: int, height: int) -> None:
        colors = self._get_colors(4)
        hw, hh = width // 2, height // 2

        # Kite shape (rounded top, pointed bottom)
        shield_height = int(height * 1.1)

        for row in range(shield_height):
            t = row / shield_height if shield_height > 0 else 0
            row_y = y - hh + row

            if t < 0.4:
                # Rounded top
                row_width = int(width * (0.6 + 0.4 * (t / 0.4)))
            else:
                # Tapered bottom
                taper = (t - 0.4) / 0.6
                row_width = int(width * (1 - taper * 0.9))

            row_width = max(1, row_width)
            color_idx = min(int(abs(0.5 - t) * 2 * len(colors)), len(colors) - 1)
            canvas.fill_rect(x - row_width // 2, row_y, row_width, 1, colors[color_idx])

        # Central stripe/cross
        stripe_color = colors[-1] if colors else (200, 200, 210, 255)
        canvas.fill_rect(x - 1, y - hh, 2, shield_height, stripe_color)


class TowerShield(Shield):
    """Large rectangular tower shield."""

    def __init__(self, config: Optional[EquipmentConfig] = None):
        super().__init__('tower_shield', config)
        self.equip_config.metallic = True

    def draw(self, canvas: Canvas, x: int, y: int, width: int, height: int) -> None:
        colors = self._get_colors(4)
        hw, hh = width // 2, height // 2

        # Large rectangle
        shield_w = int(width * 0.9)
        shield_h = int(height * 1.2)

        self._draw_shaded_rect(canvas, x - shield_w // 2, y - shield_h // 2,
                               shield_w, shield_h, colors[:3])

        # Horizontal bands
        band_color = colors[-1] if colors else (150, 150, 160, 255)
        for i in range(3):
            band_y = y - shield_h // 2 + (i + 1) * shield_h // 4
            canvas.fill_rect(x - shield_w // 2, band_y, shield_w, 2, band_color)


class BucklerShield(Shield):
    """Small buckler shield."""

    def __init__(self, config: Optional[EquipmentConfig] = None):
        super().__init__('buckler', config)

    def draw(self, canvas: Canvas, x: int, y: int, width: int, height: int) -> None:
        colors = self._get_colors(3)
        hw, hh = width // 2, height // 2

        # Small circle
        radius = min(hw, hh) * 2 // 3

        self._draw_shaded_circle(canvas, x, y, radius, colors)

        # Central boss
        boss_r = radius // 2
        if boss_r > 0:
            canvas.fill_circle(x, y, boss_r, colors[-1] if colors else (180, 180, 190, 255))


# ==================== Belts ====================

class Belt(Equipment):
    """Base class for belts."""

    def __init__(self, name: str, config: Optional[EquipmentConfig] = None):
        if config is None:
            config = EquipmentConfig()
        config.slot = EquipmentSlot.BELT
        config.layer = DrawLayer.BODY_FRONT
        super().__init__(name, config)


class SimpleBelt(Belt):
    """Basic leather belt."""

    def __init__(self, config: Optional[EquipmentConfig] = None):
        super().__init__('simple_belt', config)

    def draw(self, canvas: Canvas, x: int, y: int, width: int, height: int) -> None:
        colors = self._get_colors(2)
        hw, hh = width // 2, height // 2

        belt_w = width
        belt_h = max(2, height // 4)

        canvas.fill_rect(x - belt_w // 2, y - belt_h // 2, belt_w, belt_h, colors[0])

        # Buckle
        buckle_color = (180, 170, 130, 255)  # Brass
        buckle_w = max(2, width // 5)
        canvas.fill_rect(x - buckle_w // 2, y - belt_h // 2, buckle_w, belt_h, buckle_color)


class UtilityBelt(Belt):
    """Belt with pouches."""

    def __init__(self, config: Optional[EquipmentConfig] = None):
        super().__init__('utility_belt', config)

    def draw(self, canvas: Canvas, x: int, y: int, width: int, height: int) -> None:
        colors = self._get_colors(2)
        hw, hh = width // 2, height // 2

        # Main belt
        belt_w = width
        belt_h = max(2, height // 4)
        canvas.fill_rect(x - belt_w // 2, y - belt_h // 2, belt_w, belt_h, colors[0])

        # Pouches
        pouch_color = colors[1] if len(colors) > 1 else colors[0]
        pouch_w = width // 5
        pouch_h = height // 3

        for side in [-1, 0, 1]:
            px = x + side * (width // 3)
            py = y + belt_h // 2
            canvas.fill_rect(px - pouch_w // 2, py, pouch_w, pouch_h, pouch_color)

        # Buckle
        buckle_color = (160, 150, 120, 255)
        canvas.fill_rect(x - 2, y - belt_h // 2, 4, belt_h, buckle_color)


# ==================== Other Accessories ====================

class Wings(Equipment):
    """Decorative wings."""

    def __init__(self, config: Optional[EquipmentConfig] = None):
        if config is None:
            config = EquipmentConfig()
        config.slot = EquipmentSlot.BACK
        config.layer = DrawLayer.BACK_FAR
        super().__init__('wings', config)

    def draw(self, canvas: Canvas, x: int, y: int, width: int, height: int) -> None:
        colors = self._get_colors(3)
        hw, hh = width // 2, height // 2

        wing_span = int(width * 1.5)
        wing_height = height

        for side in [-1, 1]:
            wing_x = x + side * (hw + wing_span // 4)

            # Wing shape (curved)
            for row in range(wing_height):
                t = row / wing_height if wing_height > 0 else 0
                # Wing width varies with height
                row_width = int(wing_span // 2 * math.sin((1 - t) * math.pi * 0.8))
                row_y = y - hh // 2 + row

                if row_width > 0:
                    color_idx = min(int(t * len(colors)), len(colors) - 1)
                    if side == 1:
                        canvas.fill_rect(wing_x, row_y, row_width, 1, colors[color_idx])
                    else:
                        canvas.fill_rect(wing_x - row_width, row_y, row_width, 1, colors[color_idx])


class Scarf(Equipment):
    """Flowing scarf."""

    def __init__(self, config: Optional[EquipmentConfig] = None):
        if config is None:
            config = EquipmentConfig()
        config.slot = EquipmentSlot.NECK
        config.layer = DrawLayer.FRONT
        super().__init__('scarf', config)

    def draw(self, canvas: Canvas, x: int, y: int, width: int, height: int) -> None:
        colors = self._get_colors(2)
        hw, hh = width // 2, height // 2

        # Neck wrap
        wrap_w = width
        wrap_h = height // 4
        canvas.fill_rect(x - wrap_w // 2, y - hh, wrap_w, wrap_h, colors[0])

        # Trailing end
        tail_length = int(height * 0.8)
        tail_w = width // 3

        for row in range(tail_length):
            t = row / tail_length if tail_length > 0 else 0
            # Wavy motion
            wave = int(3 * math.sin(t * math.pi * 2))
            row_y = y - hh + wrap_h + row
            row_width = max(1, int(tail_w * (1 - t * 0.3)))

            color = colors[0] if (row % 4) < 2 else colors[1] if len(colors) > 1 else colors[0]
            canvas.fill_rect(x + wave - row_width // 2, row_y, row_width, 1, color)


class Backpack(Equipment):
    """Travel backpack."""

    def __init__(self, config: Optional[EquipmentConfig] = None):
        if config is None:
            config = EquipmentConfig()
        config.slot = EquipmentSlot.BACK
        config.layer = DrawLayer.BACK
        super().__init__('backpack', config)

    def draw(self, canvas: Canvas, x: int, y: int, width: int, height: int) -> None:
        colors = self._get_colors(3)
        hw, hh = width // 2, height // 2

        # Main pack
        pack_w = int(width * 0.7)
        pack_h = int(height * 0.8)

        self._draw_shaded_rect(canvas, x - pack_w // 2, y - pack_h // 2, pack_w, pack_h, colors)

        # Flap at top
        flap_h = pack_h // 4
        canvas.fill_rect(x - pack_w // 2, y - pack_h // 2, pack_w, flap_h, colors[0])

        # Straps
        strap_color = colors[0]
        for side in [-1, 1]:
            sx = x + side * (pack_w // 2 - 1)
            canvas.fill_rect(sx, y - pack_h // 2, 2, pack_h + 4, strap_color)


# ==================== Factory Functions ====================

CAPE_TYPES = {
    'simple': SimpleCape,
    'royal': RoyalCape,
    'tattered': TatteredCape,
}

SHIELD_TYPES = {
    'round': RoundShield,
    'kite': KiteShield,
    'tower': TowerShield,
    'buckler': BucklerShield,
}

BELT_TYPES = {
    'simple': SimpleBelt,
    'utility': UtilityBelt,
}

ACCESSORY_TYPES = {
    'wings': Wings,
    'scarf': Scarf,
    'backpack': Backpack,
}


def create_cape(cape_type: str, config: Optional[EquipmentConfig] = None) -> Cape:
    """Create a cape by type name."""
    if cape_type not in CAPE_TYPES:
        raise ValueError(f"Unknown cape type: {cape_type}. Available: {list(CAPE_TYPES.keys())}")
    return CAPE_TYPES[cape_type](config)


def create_shield(shield_type: str, config: Optional[EquipmentConfig] = None) -> Shield:
    """Create a shield by type name."""
    if shield_type not in SHIELD_TYPES:
        raise ValueError(f"Unknown shield type: {shield_type}. Available: {list(SHIELD_TYPES.keys())}")
    return SHIELD_TYPES[shield_type](config)


def create_belt(belt_type: str, config: Optional[EquipmentConfig] = None) -> Belt:
    """Create a belt by type name."""
    if belt_type not in BELT_TYPES:
        raise ValueError(f"Unknown belt type: {belt_type}. Available: {list(BELT_TYPES.keys())}")
    return BELT_TYPES[belt_type](config)


def create_accessory(accessory_type: str, config: Optional[EquipmentConfig] = None) -> Equipment:
    """Create an accessory by type name."""
    if accessory_type not in ACCESSORY_TYPES:
        raise ValueError(f"Unknown accessory type: {accessory_type}. Available: {list(ACCESSORY_TYPES.keys())}")
    return ACCESSORY_TYPES[accessory_type](config)


def list_cape_types() -> List[str]:
    """List available cape types."""
    return list(CAPE_TYPES.keys())


def list_shield_types() -> List[str]:
    """List available shield types."""
    return list(SHIELD_TYPES.keys())


def list_belt_types() -> List[str]:
    """List available belt types."""
    return list(BELT_TYPES.keys())


def list_accessory_types() -> List[str]:
    """List available accessory types."""
    return list(ACCESSORY_TYPES.keys())

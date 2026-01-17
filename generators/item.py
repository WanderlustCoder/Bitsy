"""
Item Generator - Procedural generation of game items.

Generates pixel art for:
- Weapons (swords, axes, bows, staffs, etc.)
- Armor (helmets, shields, etc.)
- Consumables (potions, food, scrolls)
- Materials (gems, ores, crafting items)
- Keys and tools
"""

import math
import random
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Canvas, Style, PROFESSIONAL_HD


class ItemCategory(Enum):
    """Item categories."""
    WEAPON = 'weapon'
    ARMOR = 'armor'
    CONSUMABLE = 'consumable'
    MATERIAL = 'material'
    TOOL = 'tool'
    KEY = 'key'


class WeaponType(Enum):
    """Weapon subtypes."""
    SWORD = 'sword'
    DAGGER = 'dagger'
    AXE = 'axe'
    SPEAR = 'spear'
    BOW = 'bow'
    STAFF = 'staff'
    WAND = 'wand'
    HAMMER = 'hammer'


class ConsumableType(Enum):
    """Consumable subtypes."""
    HEALTH_POTION = 'health_potion'
    MANA_POTION = 'mana_potion'
    BUFF_POTION = 'buff_potion'
    FOOD = 'food'
    SCROLL = 'scroll'


class MaterialType(Enum):
    """Material subtypes."""
    GEM = 'gem'
    ORE = 'ore'
    HERB = 'herb'
    CRYSTAL = 'crystal'
    ESSENCE = 'essence'


@dataclass
class ItemPalette:
    """Color palette for item generation."""
    primary: Tuple[int, int, int, int] = (180, 180, 180, 255)
    secondary: Tuple[int, int, int, int] = (120, 100, 80, 255)
    accent: Tuple[int, int, int, int] = (255, 200, 100, 255)
    highlight: Tuple[int, int, int, int] = (255, 255, 255, 255)
    shadow: Tuple[int, int, int, int] = (80, 80, 80, 255)

    @classmethod
    def iron(cls) -> 'ItemPalette':
        return cls(
            primary=(180, 180, 190, 255),
            secondary=(100, 80, 60, 255),
            accent=(200, 200, 210, 255),
            highlight=(220, 220, 230, 255),
            shadow=(100, 100, 110, 255)
        )

    @classmethod
    def gold(cls) -> 'ItemPalette':
        return cls(
            primary=(255, 200, 50, 255),
            secondary=(180, 140, 30, 255),
            accent=(255, 230, 150, 255),
            highlight=(255, 255, 200, 255),
            shadow=(150, 110, 20, 255)
        )

    @classmethod
    def wood(cls) -> 'ItemPalette':
        return cls(
            primary=(140, 100, 60, 255),
            secondary=(100, 70, 40, 255),
            accent=(180, 140, 100, 255),
            highlight=(200, 160, 120, 255),
            shadow=(80, 50, 30, 255)
        )

    @classmethod
    def magic(cls) -> 'ItemPalette':
        return cls(
            primary=(150, 100, 200, 255),
            secondary=(100, 60, 150, 255),
            accent=(200, 150, 255, 255),
            highlight=(255, 200, 255, 255),
            shadow=(80, 40, 120, 255)
        )

    @classmethod
    def fire(cls) -> 'ItemPalette':
        return cls(
            primary=(255, 100, 50, 255),
            secondary=(200, 60, 30, 255),
            accent=(255, 200, 100, 255),
            highlight=(255, 255, 150, 255),
            shadow=(150, 40, 20, 255)
        )

    @classmethod
    def ice(cls) -> 'ItemPalette':
        return cls(
            primary=(150, 200, 255, 255),
            secondary=(100, 150, 220, 255),
            accent=(200, 230, 255, 255),
            highlight=(255, 255, 255, 255),
            shadow=(80, 120, 180, 255)
        )


class ItemGenerator:
    """Generates pixel art items."""

    def __init__(self, width: int = 16, height: int = 16, seed: int = 42,
                 style: Optional[Style] = None, hd_mode: bool = False):
        """Initialize item generator.

        Args:
            width: Item width in pixels
            height: Item height in pixels
            seed: Random seed for reproducibility
            style: Art style (default: PROFESSIONAL_HD if hd_mode, else None)
            hd_mode: Enable HD quality features (selout, etc.)
        """
        self.width = width
        self.height = height
        self.seed = seed
        self.rng = random.Random(seed)
        self.palette = ItemPalette.iron()
        self.hd_mode = hd_mode
        self.style = style or (PROFESSIONAL_HD if hd_mode else None)

    def finalize(self, canvas: Canvas) -> Canvas:
        """Apply HD post-processing to a canvas.

        Args:
            canvas: Source canvas

        Returns:
            Processed canvas (with selout if HD mode enabled)
        """
        if self.hd_mode and self.style and self.style.outline.selout_enabled:
            from quality.selout import apply_selout
            return apply_selout(
                canvas,
                darken_factor=self.style.outline.selout_darken,
                saturation_factor=self.style.outline.selout_saturation
            )
        return canvas

    def set_palette(self, palette: ItemPalette) -> 'ItemGenerator':
        """Set the color palette."""
        self.palette = palette
        return self

    def generate_sword(self, style: str = 'basic') -> Canvas:
        """Generate a sword sprite.

        Args:
            style: Sword style ('basic', 'broad', 'rapier', 'curved')
        """
        canvas = Canvas(self.width, self.height, (0, 0, 0, 0))

        cx = self.width // 2
        blade_length = int(self.height * 0.7)
        handle_length = self.height - blade_length - 1

        if style == 'basic':
            # Blade
            blade_width = max(2, self.width // 6)
            for y in range(blade_length):
                for dx in range(-blade_width // 2, blade_width // 2 + 1):
                    x = cx + dx
                    # Taper at tip
                    if y < 3:
                        if abs(dx) > y:
                            continue
                    color = self.palette.primary if dx <= 0 else self.palette.highlight
                    if y == 0:
                        color = self.palette.highlight
                    canvas.set_pixel(x, y, color)

            # Guard
            guard_y = blade_length
            guard_width = max(4, self.width // 3)
            for dx in range(-guard_width // 2, guard_width // 2 + 1):
                canvas.set_pixel(cx + dx, guard_y, self.palette.accent)

            # Handle
            for y in range(guard_y + 1, guard_y + handle_length):
                canvas.set_pixel(cx, y, self.palette.secondary)
                if self.width > 12:
                    canvas.set_pixel(cx - 1, y, self.palette.shadow)

            # Pommel
            canvas.set_pixel(cx, guard_y + handle_length, self.palette.accent)

        elif style == 'broad':
            # Wider blade
            blade_width = max(3, self.width // 4)
            for y in range(blade_length):
                width_at_y = blade_width if y > 2 else max(1, blade_width - (2 - y))
                for dx in range(-width_at_y // 2, width_at_y // 2 + 1):
                    x = cx + dx
                    color = self.palette.primary
                    if dx == -width_at_y // 2:
                        color = self.palette.shadow
                    elif dx == width_at_y // 2:
                        color = self.palette.highlight
                    canvas.set_pixel(x, y, color)

            # Guard and handle
            guard_y = blade_length
            for dx in range(-2, 3):
                canvas.set_pixel(cx + dx, guard_y, self.palette.accent)
            for y in range(guard_y + 1, self.height - 1):
                canvas.set_pixel(cx, y, self.palette.secondary)
            canvas.set_pixel(cx, self.height - 1, self.palette.accent)

        elif style == 'rapier':
            # Thin blade
            for y in range(blade_length):
                color = self.palette.primary if y % 2 == 0 else self.palette.highlight
                canvas.set_pixel(cx, y, color)

            # Ornate guard
            guard_y = blade_length
            canvas.set_pixel(cx, guard_y, self.palette.accent)
            canvas.set_pixel(cx - 1, guard_y, self.palette.accent)
            canvas.set_pixel(cx + 1, guard_y, self.palette.accent)
            canvas.set_pixel(cx - 2, guard_y + 1, self.palette.accent)
            canvas.set_pixel(cx + 2, guard_y + 1, self.palette.accent)

            # Handle
            for y in range(guard_y + 1, self.height - 1):
                canvas.set_pixel(cx, y, self.palette.secondary)
            canvas.set_pixel(cx, self.height - 1, self.palette.accent)

        elif style == 'curved':
            # Curved blade
            for y in range(blade_length):
                curve = int(math.sin(y * 0.2) * 2)
                x = cx + curve
                canvas.set_pixel(x, y, self.palette.primary)
                if y > 2:
                    canvas.set_pixel(x + 1, y, self.palette.highlight)

            # Guard and handle
            guard_y = blade_length
            for dx in range(-1, 2):
                canvas.set_pixel(cx + dx, guard_y, self.palette.accent)
            for y in range(guard_y + 1, self.height):
                canvas.set_pixel(cx, y, self.palette.secondary)

        return canvas

    def generate_axe(self) -> Canvas:
        """Generate an axe sprite."""
        canvas = Canvas(self.width, self.height, (0, 0, 0, 0))

        cx = self.width // 2
        handle_length = int(self.height * 0.7)
        head_height = self.height - handle_length

        # Handle
        for y in range(head_height, self.height):
            canvas.set_pixel(cx, y, self.palette.secondary)

        # Axe head
        head_width = max(4, self.width // 2)
        for y in range(head_height):
            # Create curved axe head shape
            progress = y / head_height
            width = int(head_width * math.sin(progress * math.pi))
            width = max(1, width)

            for dx in range(width):
                x = cx + dx
                if x < self.width:
                    color = self.palette.primary
                    if dx == width - 1:
                        color = self.palette.highlight
                    elif dx == 0:
                        color = self.palette.shadow
                    canvas.set_pixel(x, y, color)

        # Edge highlight
        for y in range(1, head_height - 1):
            progress = y / head_height
            width = int(head_width * math.sin(progress * math.pi))
            x = cx + width - 1
            if x < self.width:
                canvas.set_pixel(x, y, self.palette.highlight)

        return canvas

    def generate_bow(self) -> Canvas:
        """Generate a bow sprite."""
        canvas = Canvas(self.width, self.height, (0, 0, 0, 0))

        cx = self.width // 2

        # Draw curved bow shape
        for y in range(self.height):
            # Parabolic curve
            t = (y - self.height / 2) / (self.height / 2)
            curve = int((1 - t * t) * (self.width // 3))
            x = cx - curve

            if 0 <= x < self.width:
                canvas.set_pixel(x, y, self.palette.secondary)
                if x + 1 < self.width:
                    canvas.set_pixel(x + 1, y, self.palette.primary)

        # Bowstring
        for y in range(self.height):
            canvas.set_pixel(cx + 1, y, self.palette.shadow)

        # Grip area (center)
        grip_start = self.height // 2 - 2
        grip_end = self.height // 2 + 2
        for y in range(grip_start, grip_end):
            t = (y - self.height / 2) / (self.height / 2)
            curve = int((1 - t * t) * (self.width // 3))
            x = cx - curve
            if 0 <= x < self.width:
                canvas.set_pixel(x, y, self.palette.accent)

        return canvas

    def generate_staff(self, style: str = 'basic') -> Canvas:
        """Generate a magic staff sprite."""
        canvas = Canvas(self.width, self.height, (0, 0, 0, 0))

        cx = self.width // 2
        staff_length = int(self.height * 0.85)
        orb_size = max(2, (self.height - staff_length))

        # Staff pole
        for y in range(orb_size, self.height):
            canvas.set_pixel(cx, y, self.palette.secondary)
            # Wood grain detail
            if y % 3 == 0 and self.width > 12:
                canvas.set_pixel(cx - 1, y, self.palette.shadow)

        # Magic orb at top
        orb_cy = orb_size // 2 + 1
        for dy in range(-orb_size // 2, orb_size // 2 + 1):
            for dx in range(-orb_size // 2, orb_size // 2 + 1):
                if dx * dx + dy * dy <= (orb_size // 2) ** 2:
                    x = cx + dx
                    y = orb_cy + dy
                    if 0 <= x < self.width and 0 <= y < self.height:
                        # Gradient shading on orb
                        if dx < 0 and dy < 0:
                            color = self.palette.highlight
                        elif dx > 0 or dy > 0:
                            color = self.palette.shadow
                        else:
                            color = self.palette.accent
                        canvas.set_pixel(x, y, color)

        # Sparkle on orb
        if orb_size > 2:
            canvas.set_pixel(cx - 1, orb_cy - 1, self.palette.highlight)

        return canvas

    def generate_potion(self, potion_type: str = 'health') -> Canvas:
        """Generate a potion bottle sprite."""
        canvas = Canvas(self.width, self.height, (0, 0, 0, 0))

        cx = self.width // 2
        bottle_width = max(4, self.width // 2)
        neck_width = max(2, bottle_width // 3)
        neck_height = max(2, self.height // 5)
        body_height = self.height - neck_height - 1

        # Determine liquid color based on type
        liquid_colors = {
            'health': ((255, 50, 80, 255), (200, 30, 60, 255)),
            'mana': ((80, 100, 255, 255), (50, 70, 200, 255)),
            'stamina': ((80, 255, 100, 255), (50, 200, 70, 255)),
            'buff': ((255, 200, 50, 255), (200, 150, 30, 255)),
        }
        liquid, liquid_dark = liquid_colors.get(potion_type, liquid_colors['health'])

        # Cork
        for dx in range(-neck_width // 2, neck_width // 2 + 1):
            canvas.set_pixel(cx + dx, 0, self.palette.secondary)

        # Neck
        for y in range(1, neck_height):
            for dx in range(-neck_width // 2, neck_width // 2 + 1):
                x = cx + dx
                # Glass effect
                if dx == -neck_width // 2:
                    color = (200, 220, 255, 200)
                elif dx == neck_width // 2:
                    color = (150, 170, 200, 200)
                else:
                    color = (180, 200, 230, 150)
                canvas.set_pixel(x, y, color)

        # Body
        for y in range(neck_height, self.height):
            body_y = y - neck_height
            # Widen from neck
            if body_y < 2:
                width = neck_width + body_y
            else:
                width = bottle_width

            for dx in range(-width // 2, width // 2 + 1):
                x = cx + dx
                if 0 <= x < self.width:
                    # Glass or liquid
                    is_edge = abs(dx) >= width // 2 - 1
                    is_bottom = y >= self.height - 2

                    if is_edge:
                        # Glass edge
                        if dx < 0:
                            color = (200, 220, 255, 220)
                        else:
                            color = (150, 170, 200, 220)
                    elif is_bottom:
                        color = liquid_dark
                    else:
                        color = liquid

                    canvas.set_pixel(x, y, color)

        # Highlight on glass
        canvas.set_pixel(cx - bottle_width // 2 + 1, neck_height + 2, (255, 255, 255, 150))

        return canvas

    def generate_gem(self, gem_color: str = 'red') -> Canvas:
        """Generate a gem/crystal sprite."""
        canvas = Canvas(self.width, self.height, (0, 0, 0, 0))

        gem_colors = {
            'red': ((255, 80, 100, 255), (200, 50, 70, 255), (150, 30, 50, 255)),
            'blue': ((100, 150, 255, 255), (70, 100, 200, 255), (50, 70, 150, 255)),
            'green': ((80, 255, 120, 255), (50, 200, 80, 255), (30, 150, 60, 255)),
            'yellow': ((255, 255, 100, 255), (230, 200, 50, 255), (180, 150, 30, 255)),
            'purple': ((200, 100, 255, 255), (150, 70, 200, 255), (100, 50, 150, 255)),
        }
        light, mid, dark = gem_colors.get(gem_color, gem_colors['red'])

        cx = self.width // 2
        cy = self.height // 2

        # Diamond shape
        size = min(self.width, self.height) // 2 - 1

        for y in range(self.height):
            for x in range(self.width):
                dx = abs(x - cx)
                dy = abs(y - cy)

                # Diamond bounds
                if dx + dy <= size:
                    # Faceted shading
                    if x < cx and y < cy:
                        color = light
                    elif x >= cx and y < cy:
                        color = mid
                    elif x < cx and y >= cy:
                        color = mid
                    else:
                        color = dark

                    canvas.set_pixel(x, y, color)

        # Center sparkle
        canvas.set_pixel(cx - 1, cy - 1, (255, 255, 255, 255))

        return canvas

    def generate_key(self, style: str = 'basic') -> Canvas:
        """Generate a key sprite."""
        canvas = Canvas(self.width, self.height, (0, 0, 0, 0))

        cx = self.width // 2

        # Key bow (round part)
        bow_radius = max(2, self.width // 4)
        bow_cy = bow_radius + 1

        for dy in range(-bow_radius, bow_radius + 1):
            for dx in range(-bow_radius, bow_radius + 1):
                dist = dx * dx + dy * dy
                if dist <= bow_radius ** 2 and dist >= (bow_radius - 1) ** 2:
                    x = cx + dx
                    y = bow_cy + dy
                    if 0 <= x < self.width and 0 <= y < self.height:
                        color = self.palette.primary if dx <= 0 else self.palette.highlight
                        canvas.set_pixel(x, y, color)

        # Key shaft
        shaft_start = bow_cy + bow_radius
        shaft_end = self.height - 3
        for y in range(shaft_start, shaft_end):
            canvas.set_pixel(cx, y, self.palette.primary)
            if self.width > 10:
                canvas.set_pixel(cx + 1, y, self.palette.highlight)

        # Key teeth
        teeth_y = shaft_end
        for y in range(teeth_y, self.height):
            canvas.set_pixel(cx, y, self.palette.primary)
            # Teeth pattern
            if y % 2 == 0:
                canvas.set_pixel(cx + 1, y, self.palette.primary)
                canvas.set_pixel(cx + 2, y, self.palette.shadow)

        return canvas

    def generate_shield(self, style: str = 'round') -> Canvas:
        """Generate a shield sprite."""
        canvas = Canvas(self.width, self.height, (0, 0, 0, 0))

        cx = self.width // 2
        cy = self.height // 2

        if style == 'round':
            radius = min(self.width, self.height) // 2 - 1
            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    if dx * dx + dy * dy <= radius ** 2:
                        x = cx + dx
                        y = cy + dy
                        # Shading
                        if dx < 0 and dy < 0:
                            color = self.palette.highlight
                        elif dx > radius // 2 or dy > radius // 2:
                            color = self.palette.shadow
                        else:
                            color = self.palette.primary
                        canvas.set_pixel(x, y, color)

            # Center emblem
            canvas.set_pixel(cx, cy, self.palette.accent)
            canvas.set_pixel(cx - 1, cy, self.palette.accent)
            canvas.set_pixel(cx + 1, cy, self.palette.accent)
            canvas.set_pixel(cx, cy - 1, self.palette.accent)
            canvas.set_pixel(cx, cy + 1, self.palette.accent)

        elif style == 'kite':
            # Kite shield shape
            for y in range(self.height):
                progress = y / self.height
                if progress < 0.5:
                    width = int(self.width * 0.8 * (progress * 2))
                else:
                    width = int(self.width * 0.8 * (1 - (progress - 0.5) * 2))
                width = max(1, width)

                for dx in range(-width // 2, width // 2 + 1):
                    x = cx + dx
                    if 0 <= x < self.width:
                        if dx == -width // 2:
                            color = self.palette.highlight
                        elif dx == width // 2 - 1:
                            color = self.palette.shadow
                        else:
                            color = self.palette.primary
                        canvas.set_pixel(x, y, color)

        return canvas

    def generate_scroll(self) -> Canvas:
        """Generate a scroll sprite."""
        canvas = Canvas(self.width, self.height, (0, 0, 0, 0))

        cx = self.width // 2
        scroll_width = max(6, int(self.width * 0.7))
        roll_height = max(2, self.height // 5)

        # Paper color
        paper = (240, 230, 200, 255)
        paper_dark = (200, 190, 160, 255)
        roll_color = (220, 200, 160, 255)

        # Top roll
        for y in range(roll_height):
            for dx in range(-scroll_width // 2, scroll_width // 2 + 1):
                x = cx + dx
                if 0 <= x < self.width:
                    canvas.set_pixel(x, y, roll_color)

        # Paper body
        for y in range(roll_height, self.height - roll_height):
            for dx in range(-scroll_width // 2 + 1, scroll_width // 2):
                x = cx + dx
                if 0 <= x < self.width:
                    color = paper if dx < 0 else paper_dark
                    canvas.set_pixel(x, y, color)

        # Bottom roll
        for y in range(self.height - roll_height, self.height):
            for dx in range(-scroll_width // 2, scroll_width // 2 + 1):
                x = cx + dx
                if 0 <= x < self.width:
                    canvas.set_pixel(x, y, roll_color)

        # Text lines (simple)
        text_color = (100, 80, 60, 255)
        for line in range(3):
            y = roll_height + 2 + line * 2
            if y < self.height - roll_height - 1:
                for dx in range(-scroll_width // 2 + 2, scroll_width // 2 - 2):
                    if self.rng.random() > 0.3:
                        canvas.set_pixel(cx + dx, y, text_color)

        return canvas

    def generate_coin(self) -> Canvas:
        """Generate a coin sprite."""
        canvas = Canvas(self.width, self.height, (0, 0, 0, 0))

        cx = self.width // 2
        cy = self.height // 2
        radius = min(self.width, self.height) // 2 - 1

        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                if dx * dx + dy * dy <= radius ** 2:
                    x = cx + dx
                    y = cy + dy
                    # Gold gradient
                    if dx < -radius // 3 and dy < -radius // 3:
                        color = self.palette.highlight
                    elif dx > radius // 3 or dy > radius // 3:
                        color = self.palette.shadow
                    else:
                        color = self.palette.primary
                    canvas.set_pixel(x, y, color)

        # Simple emblem
        canvas.set_pixel(cx, cy, self.palette.accent)

        return canvas

    def randomize(self) -> 'ItemGenerator':
        """Randomize generator settings."""
        palettes = [
            ItemPalette.iron(),
            ItemPalette.gold(),
            ItemPalette.wood(),
            ItemPalette.magic(),
            ItemPalette.fire(),
            ItemPalette.ice(),
        ]
        self.palette = self.rng.choice(palettes)
        return self


# =============================================================================
# Item Generation Registry
# =============================================================================

ITEM_GENERATORS = {
    'sword': lambda g: g.generate_sword('basic'),
    'sword_broad': lambda g: g.generate_sword('broad'),
    'sword_rapier': lambda g: g.generate_sword('rapier'),
    'sword_curved': lambda g: g.generate_sword('curved'),
    'axe': lambda g: g.generate_axe(),
    'bow': lambda g: g.generate_bow(),
    'staff': lambda g: g.generate_staff(),
    'potion_health': lambda g: g.generate_potion('health'),
    'potion_mana': lambda g: g.generate_potion('mana'),
    'potion_stamina': lambda g: g.generate_potion('stamina'),
    'potion_buff': lambda g: g.generate_potion('buff'),
    'gem_red': lambda g: g.generate_gem('red'),
    'gem_blue': lambda g: g.generate_gem('blue'),
    'gem_green': lambda g: g.generate_gem('green'),
    'gem_yellow': lambda g: g.generate_gem('yellow'),
    'gem_purple': lambda g: g.generate_gem('purple'),
    'key': lambda g: g.generate_key(),
    'shield_round': lambda g: g.generate_shield('round'),
    'shield_kite': lambda g: g.generate_shield('kite'),
    'scroll': lambda g: g.generate_scroll(),
    'coin': lambda g: g.generate_coin(),
}


def generate_item(item_type: str, width: int = 16, height: int = 16,
                  seed: int = 42, palette: Optional[ItemPalette] = None,
                  hd_mode: bool = False, style: Optional[Style] = None) -> Canvas:
    """Generate an item by type name.

    Args:
        item_type: Item type name (see ITEM_GENERATORS)
        width: Item width
        height: Item height
        seed: Random seed
        palette: Optional color palette
        hd_mode: Enable HD quality features (selout postprocessing)
        style: Optional style for HD mode (default: PROFESSIONAL_HD)

    Returns:
        Canvas with generated item
    """
    if item_type not in ITEM_GENERATORS:
        available = ', '.join(sorted(ITEM_GENERATORS.keys()))
        raise ValueError(f"Unknown item type '{item_type}'. Available: {available}")

    gen = ItemGenerator(width, height, seed, style=style, hd_mode=hd_mode)
    if palette:
        gen.set_palette(palette)

    canvas = ITEM_GENERATORS[item_type](gen)
    return gen.finalize(canvas)


def list_item_types() -> List[str]:
    """Get list of available item types."""
    return sorted(ITEM_GENERATORS.keys())

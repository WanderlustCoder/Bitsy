"""
Prop Generator - Procedural generation of props and objects.

Generates pixel art for:
- Chests (treasure, wooden, iron)
- Barrels and crates
- Furniture (tables, chairs, beds)
- Vegetation (trees, bushes, flowers)
- Containers (pots, vases, sacks)
- Decorations (torches, candles, signs)
"""

import math
import random
from typing import Dict, List, Tuple, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Canvas, Style, PROFESSIONAL_HD
from core.color import darken, lighten


class ChestType(Enum):
    """Chest variants."""
    WOODEN = 'wooden'
    IRON = 'iron'
    GOLD = 'gold'
    TREASURE = 'treasure'
    MIMIC = 'mimic'


class ContainerType(Enum):
    """Container variants."""
    BARREL = 'barrel'
    CRATE = 'crate'
    POT = 'pot'
    VASE = 'vase'
    SACK = 'sack'
    JAR = 'jar'


class FurnitureType(Enum):
    """Furniture variants."""
    TABLE = 'table'
    CHAIR = 'chair'
    BED = 'bed'
    BOOKSHELF = 'bookshelf'
    THRONE = 'throne'
    BENCH = 'bench'


class VegetationType(Enum):
    """Vegetation variants."""
    TREE = 'tree'
    BUSH = 'bush'
    FLOWER = 'flower'
    GRASS = 'grass'
    MUSHROOM = 'mushroom'
    CACTUS = 'cactus'


class DecorationTypeEnum(Enum):
    """Decoration variants."""
    TORCH = 'torch'
    CANDLE = 'candle'
    SIGN = 'sign'
    FLAG = 'flag'
    STATUE = 'statue'
    GRAVESTONE = 'gravestone'


@dataclass
class PropPalette:
    """Color palette for prop generation."""
    primary: Tuple[int, int, int, int] = (150, 100, 60, 255)
    secondary: Tuple[int, int, int, int] = (120, 80, 50, 255)
    highlight: Tuple[int, int, int, int] = (180, 140, 100, 255)
    shadow: Tuple[int, int, int, int] = (80, 50, 30, 255)
    accent: Tuple[int, int, int, int] = (200, 180, 120, 255)
    outline: Tuple[int, int, int, int] = (50, 30, 20, 255)

    @classmethod
    def wood(cls) -> 'PropPalette':
        return cls(
            primary=(140, 95, 60, 255),
            secondary=(110, 75, 50, 255),
            highlight=(170, 130, 90, 255),
            shadow=(70, 45, 30, 255),
            accent=(180, 150, 100, 255),
            outline=(50, 30, 20, 255)
        )

    @classmethod
    def iron(cls) -> 'PropPalette':
        return cls(
            primary=(120, 120, 130, 255),
            secondary=(90, 90, 100, 255),
            highlight=(160, 160, 170, 255),
            shadow=(60, 60, 70, 255),
            accent=(140, 140, 150, 255),
            outline=(40, 40, 50, 255)
        )

    @classmethod
    def gold(cls) -> 'PropPalette':
        return cls(
            primary=(220, 180, 80, 255),
            secondary=(180, 140, 60, 255),
            highlight=(255, 230, 150, 255),
            shadow=(140, 100, 40, 255),
            accent=(240, 200, 100, 255),
            outline=(100, 70, 30, 255)
        )

    @classmethod
    def stone(cls) -> 'PropPalette':
        return cls(
            primary=(130, 130, 140, 255),
            secondary=(100, 100, 110, 255),
            highlight=(160, 160, 170, 255),
            shadow=(70, 70, 80, 255),
            accent=(120, 120, 130, 255),
            outline=(50, 50, 60, 255)
        )

    @classmethod
    def plant(cls) -> 'PropPalette':
        return cls(
            primary=(80, 140, 60, 255),
            secondary=(60, 110, 45, 255),
            highlight=(120, 180, 90, 255),
            shadow=(40, 80, 30, 255),
            accent=(100, 160, 70, 255),
            outline=(30, 60, 20, 255)
        )

    @classmethod
    def fabric(cls) -> 'PropPalette':
        return cls(
            primary=(180, 60, 60, 255),
            secondary=(140, 45, 45, 255),
            highlight=(220, 100, 100, 255),
            shadow=(100, 30, 30, 255),
            accent=(200, 80, 80, 255),
            outline=(70, 20, 20, 255)
        )


class PropGenerator:
    """Generates pixel art props and objects."""

    def __init__(self, width: int = 16, height: int = 16, seed: int = 42,
                 style: Optional['Style'] = None, hd_mode: bool = False):
        """Initialize prop generator.

        Args:
            width: Prop width in pixels (default: 16)
            height: Prop height in pixels (default: 16)
            seed: Random seed for reproducibility
            style: Style configuration for quality settings (default: Style.default() unless hd_mode)
            hd_mode: Enable HD quality features (selout, AA)
        """
        self.width = width
        self.height = height
        self.seed = seed
        self.rng = random.Random(seed)
        self.palette = PropPalette.wood()
        self.hd_mode = hd_mode
        self.style = style or (PROFESSIONAL_HD if hd_mode else Style.default())

    def finalize(self, canvas: Canvas) -> Canvas:
        """Apply HD post-processing effects.

        Args:
            canvas: Raw canvas to process

        Returns:
            Processed canvas with selout applied if HD mode
        """
        if self.hd_mode and self.style and self.style.outline.selout_enabled:
            from quality.selout import apply_selout
            return apply_selout(
                canvas,
                darken_factor=self.style.outline.selout_darken,
                saturation_factor=self.style.outline.selout_saturation
            )
        return canvas

    def set_palette(self, palette: PropPalette) -> 'PropGenerator':
        """Set color palette."""
        self.palette = palette
        return self

    def set_seed(self, seed: int) -> 'PropGenerator':
        """Set random seed."""
        self.seed = seed
        self.rng = random.Random(seed)
        return self

    def generate(self, prop_type: str, variant: str = None) -> Canvas:
        """Generate a prop of the specified type.

        Args:
            prop_type: Type of prop (chest, barrel, table, tree, etc.)
            variant: Optional variant (wooden, iron, gold, etc.)

        Returns:
            Canvas with generated prop
        """
        prop_type = prop_type.lower()

        generators = {
            'chest': self._generate_chest,
            'barrel': self._generate_barrel,
            'crate': self._generate_crate,
            'pot': self._generate_pot,
            'vase': self._generate_vase,
            'sack': self._generate_sack,
            'table': self._generate_table,
            'chair': self._generate_chair,
            'bed': self._generate_bed,
            'bookshelf': self._generate_bookshelf,
            'tree': self._generate_tree,
            'bush': self._generate_bush,
            'flower': self._generate_flower,
            'mushroom': self._generate_mushroom,
            'torch': self._generate_torch,
            'candle': self._generate_candle,
            'sign': self._generate_sign,
            'gravestone': self._generate_gravestone,
        }

        if prop_type in generators:
            canvas = generators[prop_type](variant)
            return self.finalize(canvas)

        canvas = self._generate_crate(variant)
        return self.finalize(canvas)

    def _generate_chest(self, variant: str = None) -> Canvas:
        """Generate a chest."""
        canvas = Canvas(self.width, self.height)

        # Set palette based on variant
        if variant == 'iron':
            self.palette = PropPalette.iron()
        elif variant in ('gold', 'treasure'):
            self.palette = PropPalette.gold()
        else:
            self.palette = PropPalette.wood()

        cx = self.width // 2
        base_y = self.height - 2

        chest_w = self.width - 4
        chest_h = self.height - 4
        left = cx - chest_w // 2
        top = base_y - chest_h

        # Main body
        canvas.fill_rect(left, top + chest_h // 3, chest_w, chest_h * 2 // 3,
                         self.palette.primary)

        # Lid (curved top)
        for y in range(chest_h // 3):
            curve = int((1 - (y / (chest_h // 3)) ** 2) * 2)
            row_left = left + curve
            row_width = chest_w - curve * 2
            canvas.fill_rect(row_left, top + y, row_width, 1, self.palette.secondary)

        # Metal bands
        band_color = PropPalette.iron().primary if variant != 'iron' else self.palette.highlight
        # Top band
        canvas.fill_rect(left, top + chest_h // 3, chest_w, 2, band_color)
        # Middle band
        canvas.fill_rect(left, top + chest_h // 2, chest_w, 1, band_color)
        # Side bands
        canvas.fill_rect(left + 2, top + 2, 2, chest_h - 4, band_color)
        canvas.fill_rect(left + chest_w - 4, top + 2, 2, chest_h - 4, band_color)

        # Lock/clasp
        lock_color = PropPalette.gold().primary
        lock_x = cx - 1
        lock_y = top + chest_h // 3 - 1
        canvas.fill_rect(lock_x, lock_y, 3, 4, lock_color)

        # Highlight
        canvas.fill_rect(left + 3, top + 3, 3, 2, self.palette.highlight)

        # Outline
        for x in range(left, left + chest_w):
            canvas.set_pixel_solid(x, top, self.palette.outline)
            canvas.set_pixel_solid(x, base_y, self.palette.outline)
        for y in range(top, base_y + 1):
            canvas.set_pixel_solid(left, y, self.palette.outline)
            canvas.set_pixel_solid(left + chest_w - 1, y, self.palette.outline)

        return canvas

    def _generate_barrel(self, variant: str = None) -> Canvas:
        """Generate a barrel."""
        canvas = Canvas(self.width, self.height)
        self.palette = PropPalette.wood()

        cx = self.width // 2
        base_y = self.height - 1

        barrel_w = self.width - 4
        barrel_h = self.height - 2

        # Draw barrel body (vertical ellipse)
        for y in range(barrel_h):
            # Barrel bulges in middle
            progress = y / barrel_h
            bulge = math.sin(progress * math.pi) * 0.2
            row_width = int(barrel_w * (0.8 + bulge))
            row_left = cx - row_width // 2

            for x in range(row_width):
                px = row_left + x
                if 0 <= px < self.width:
                    # Wood grain pattern
                    if x % 3 == 0:
                        canvas.set_pixel_solid(px, base_y - y, self.palette.secondary)
                    else:
                        canvas.set_pixel_solid(px, base_y - y, self.palette.primary)

        # Metal bands
        band_color = PropPalette.iron().primary
        band_positions = [2, barrel_h // 2, barrel_h - 3]

        for band_y in band_positions:
            y = base_y - band_y
            if 0 <= y < self.height:
                progress = band_y / barrel_h
                bulge = math.sin(progress * math.pi) * 0.2
                row_width = int(barrel_w * (0.8 + bulge))
                row_left = cx - row_width // 2

                for x in range(row_width):
                    px = row_left + x
                    if 0 <= px < self.width:
                        canvas.set_pixel_solid(px, y, band_color)

        return canvas

    def _generate_crate(self, variant: str = None) -> Canvas:
        """Generate a wooden crate."""
        canvas = Canvas(self.width, self.height)
        self.palette = PropPalette.wood()

        margin = 2
        crate_left = margin
        crate_top = margin
        crate_w = self.width - margin * 2
        crate_h = self.height - margin * 2

        # Main body
        canvas.fill_rect(crate_left, crate_top, crate_w, crate_h, self.palette.primary)

        # Planks
        plank_spacing = 3
        for x in range(crate_left, crate_left + crate_w, plank_spacing):
            for y in range(crate_top, crate_top + crate_h):
                canvas.set_pixel_solid(x, y, self.palette.secondary)

        # Cross planks
        for y in range(crate_top + 2, crate_top + crate_h - 2, plank_spacing):
            for x in range(crate_left, crate_left + crate_w):
                canvas.set_pixel_solid(x, y, self.palette.secondary)

        # Corner reinforcements
        corner_size = 2
        for dx, dy in [(0, 0), (crate_w - corner_size, 0),
                       (0, crate_h - corner_size), (crate_w - corner_size, crate_h - corner_size)]:
            canvas.fill_rect(crate_left + dx, crate_top + dy,
                             corner_size, corner_size, self.palette.shadow)

        # Outline
        for x in range(crate_left, crate_left + crate_w):
            canvas.set_pixel_solid(x, crate_top, self.palette.outline)
            canvas.set_pixel_solid(x, crate_top + crate_h - 1, self.palette.outline)
        for y in range(crate_top, crate_top + crate_h):
            canvas.set_pixel_solid(crate_left, y, self.palette.outline)
            canvas.set_pixel_solid(crate_left + crate_w - 1, y, self.palette.outline)

        return canvas

    def _generate_pot(self, variant: str = None) -> Canvas:
        """Generate a clay pot."""
        canvas = Canvas(self.width, self.height)

        # Clay colors
        pot_color = (180, 120, 90, 255)
        pot_light = (210, 150, 120, 255)
        pot_dark = (130, 80, 60, 255)

        cx = self.width // 2
        base_y = self.height - 1

        pot_h = self.height - 3
        max_width = self.width - 4

        for y in range(pot_h):
            progress = y / pot_h
            # Pot shape: wide at top, narrow at bottom
            if progress < 0.2:
                width = int(max_width * 0.8)  # Rim
            elif progress < 0.4:
                width = int(max_width * (0.6 + progress))  # Neck
            else:
                width = int(max_width * (1 - (progress - 0.4) * 0.5))  # Body to base

            half_w = width // 2

            for dx in range(-half_w, half_w + 1):
                px = cx + dx
                py = base_y - y
                if 0 <= px < self.width and 0 <= py < self.height:
                    # Shading
                    if dx < -half_w + 2:
                        canvas.set_pixel_solid(px, py, pot_dark)
                    elif dx > half_w - 2:
                        canvas.set_pixel_solid(px, py, pot_dark)
                    elif dx < 0:
                        canvas.set_pixel_solid(px, py, pot_light)
                    else:
                        canvas.set_pixel_solid(px, py, pot_color)

        return canvas

    def _generate_vase(self, variant: str = None) -> Canvas:
        """Generate a decorative vase."""
        canvas = Canvas(self.width, self.height)

        # Ceramic colors
        vase_color = (100, 120, 180, 255)
        vase_light = (140, 160, 220, 255)
        vase_dark = (60, 80, 140, 255)
        gold = (200, 180, 100, 255)

        cx = self.width // 2
        base_y = self.height - 1

        vase_h = self.height - 2

        for y in range(vase_h):
            progress = y / vase_h

            # Vase shape: curved
            if progress < 0.15:
                width = 3  # Narrow neck
            elif progress < 0.3:
                width = int(3 + (progress - 0.15) * 40)  # Flare
            elif progress < 0.7:
                width = int(self.width - 6 - (progress - 0.3) * 10)  # Body
            else:
                width = int(self.width - 8 - (progress - 0.7) * 15)  # Base

            width = max(2, min(width, self.width - 4))
            half_w = width // 2

            for dx in range(-half_w, half_w + 1):
                px = cx + dx
                py = base_y - y
                if 0 <= px < self.width and 0 <= py < self.height:
                    if dx < 0:
                        canvas.set_pixel_solid(px, py, vase_light)
                    else:
                        canvas.set_pixel_solid(px, py, vase_color)

        # Gold trim
        for dx in range(-3, 4):
            px = cx + dx
            if 0 <= px < self.width:
                canvas.set_pixel_solid(px, base_y - vase_h + 5, gold)
                canvas.set_pixel_solid(px, base_y - 3, gold)

        return canvas

    def _generate_sack(self, variant: str = None) -> Canvas:
        """Generate a cloth sack."""
        canvas = Canvas(self.width, self.height)

        # Burlap colors
        sack_color = (180, 160, 120, 255)
        sack_light = (200, 180, 140, 255)
        sack_dark = (140, 120, 90, 255)
        tie_color = (120, 100, 70, 255)

        cx = self.width // 2
        base_y = self.height - 1

        sack_h = self.height - 3
        max_width = self.width - 4

        # Draw bulging sack shape
        for y in range(sack_h):
            progress = y / sack_h

            # Sack shape: tied at top, bulges at bottom
            if progress < 0.2:
                width = int(4 + progress * 20)  # Tied top
            else:
                bulge = math.sin((progress - 0.2) / 0.8 * math.pi) * 0.3
                width = int(max_width * (0.7 + bulge))

            half_w = width // 2

            for dx in range(-half_w, half_w + 1):
                px = cx + dx
                py = base_y - y
                if 0 <= px < self.width and 0 <= py < self.height:
                    # Folds and creases
                    if abs(dx) > half_w - 2:
                        canvas.set_pixel_solid(px, py, sack_dark)
                    elif (px + py) % 4 == 0:
                        canvas.set_pixel_solid(px, py, sack_light)
                    else:
                        canvas.set_pixel_solid(px, py, sack_color)

        # Tie at top
        tie_y = base_y - sack_h + 3
        for dx in range(-2, 3):
            canvas.set_pixel_solid(cx + dx, tie_y, tie_color)
            canvas.set_pixel_solid(cx + dx, tie_y + 1, tie_color)

        return canvas

    def _generate_table(self, variant: str = None) -> Canvas:
        """Generate a table."""
        canvas = Canvas(self.width, self.height)
        self.palette = PropPalette.wood()

        # Table dimensions
        table_width = self.width - 4
        table_height = 3
        leg_height = self.height - table_height - 2
        leg_width = 2

        cx = self.width // 2
        table_left = cx - table_width // 2
        table_top = 2

        # Table top
        canvas.fill_rect(table_left, table_top, table_width, table_height,
                         self.palette.primary)
        # Highlight on top
        canvas.fill_rect(table_left + 1, table_top, table_width - 2, 1,
                         self.palette.highlight)

        # Legs
        leg_y = table_top + table_height
        # Left leg
        canvas.fill_rect(table_left + 1, leg_y, leg_width, leg_height,
                         self.palette.secondary)
        # Right leg
        canvas.fill_rect(table_left + table_width - leg_width - 1, leg_y,
                         leg_width, leg_height, self.palette.secondary)

        return canvas

    def _generate_chair(self, variant: str = None) -> Canvas:
        """Generate a chair."""
        canvas = Canvas(self.width, self.height)
        self.palette = PropPalette.wood()

        cx = self.width // 2
        base_y = self.height - 1

        # Seat
        seat_width = self.width - 6
        seat_height = 2
        seat_y = base_y - self.height // 2
        seat_left = cx - seat_width // 2

        canvas.fill_rect(seat_left, seat_y, seat_width, seat_height,
                         self.palette.primary)

        # Back
        back_width = seat_width - 2
        back_height = self.height // 3
        back_left = cx - back_width // 2

        canvas.fill_rect(back_left, seat_y - back_height, back_width, back_height,
                         self.palette.secondary)
        # Back slats
        for x in range(back_left + 2, back_left + back_width - 2, 3):
            canvas.fill_rect(x, seat_y - back_height + 1, 1, back_height - 2,
                             self.palette.primary)

        # Legs
        leg_width = 1
        leg_height = self.height // 2 - seat_height
        # Front legs
        canvas.fill_rect(seat_left + 1, seat_y + seat_height, leg_width, leg_height,
                         self.palette.shadow)
        canvas.fill_rect(seat_left + seat_width - 2, seat_y + seat_height,
                         leg_width, leg_height, self.palette.shadow)
        # Back legs (connected to back)
        canvas.fill_rect(back_left, seat_y, leg_width, leg_height + seat_height,
                         self.palette.shadow)
        canvas.fill_rect(back_left + back_width - 1, seat_y, leg_width,
                         leg_height + seat_height, self.palette.shadow)

        return canvas

    def _generate_bed(self, variant: str = None) -> Canvas:
        """Generate a bed."""
        canvas = Canvas(self.width, self.height)

        wood = PropPalette.wood()
        fabric = PropPalette.fabric()

        # Bed frame
        frame_h = self.height // 3
        frame_y = self.height - frame_h

        # Frame base
        canvas.fill_rect(2, frame_y, self.width - 4, frame_h - 1, wood.primary)

        # Mattress
        mattress_h = frame_h - 2
        canvas.fill_rect(3, frame_y - mattress_h, self.width - 6, mattress_h,
                         (240, 235, 220, 255))

        # Pillow
        pillow_w = self.width // 3
        canvas.fill_rect(4, frame_y - mattress_h - 2, pillow_w, 3,
                         (255, 255, 255, 255))

        # Blanket
        blanket_y = frame_y - mattress_h + 2
        canvas.fill_rect(4 + pillow_w, blanket_y, self.width - pillow_w - 8,
                         mattress_h - 2, fabric.primary)

        # Headboard
        headboard_h = self.height // 2
        canvas.fill_rect(2, frame_y - mattress_h - headboard_h, 3, headboard_h,
                         wood.secondary)

        # Footboard
        canvas.fill_rect(self.width - 5, frame_y - mattress_h - 3, 3, 4,
                         wood.secondary)

        return canvas

    def _generate_bookshelf(self, variant: str = None) -> Canvas:
        """Generate a bookshelf."""
        canvas = Canvas(self.width, self.height)
        self.palette = PropPalette.wood()

        # Shelf frame
        shelf_left = 2
        shelf_width = self.width - 4
        shelf_height = self.height - 2

        # Back
        canvas.fill_rect(shelf_left, 1, shelf_width, shelf_height,
                         self.palette.shadow)

        # Sides
        canvas.fill_rect(shelf_left, 1, 2, shelf_height, self.palette.primary)
        canvas.fill_rect(shelf_left + shelf_width - 2, 1, 2, shelf_height,
                         self.palette.primary)

        # Shelves
        num_shelves = 3
        shelf_spacing = shelf_height // (num_shelves + 1)

        for i in range(num_shelves + 1):
            y = 1 + i * shelf_spacing
            canvas.fill_rect(shelf_left, y, shelf_width, 2, self.palette.primary)

        # Books on shelves
        book_colors = [
            (180, 50, 50, 255), (50, 100, 180, 255), (50, 150, 80, 255),
            (180, 150, 50, 255), (150, 80, 150, 255), (100, 100, 100, 255)
        ]

        for i in range(num_shelves):
            shelf_y = 3 + i * shelf_spacing
            book_x = shelf_left + 3

            while book_x < shelf_left + shelf_width - 4:
                book_width = self.rng.randint(1, 3)
                book_height = shelf_spacing - 3
                book_color = self.rng.choice(book_colors)

                canvas.fill_rect(book_x, shelf_y, book_width, book_height,
                                 book_color)
                book_x += book_width + 1

        return canvas

    def _generate_tree(self, variant: str = None) -> Canvas:
        """Generate a tree."""
        canvas = Canvas(self.width, self.height)

        trunk_color = (100, 70, 50, 255)
        trunk_dark = (70, 50, 35, 255)
        leaf_color = (60, 130, 50, 255)
        leaf_light = (90, 160, 70, 255)
        leaf_dark = (40, 90, 35, 255)

        cx = self.width // 2
        base_y = self.height - 1

        # Trunk
        trunk_width = max(2, self.width // 6)
        trunk_height = self.height // 3

        for y in range(trunk_height):
            width = trunk_width + y // 3
            for dx in range(-width // 2, width // 2 + 1):
                px = cx + dx
                py = base_y - y
                if 0 <= px < self.width:
                    if dx < 0:
                        canvas.set_pixel_solid(px, py, trunk_dark)
                    else:
                        canvas.set_pixel_solid(px, py, trunk_color)

        # Foliage (layered circles)
        foliage_y = base_y - trunk_height
        foliage_radius = self.width // 3

        for layer in range(3):
            layer_y = foliage_y - layer * foliage_radius // 2
            layer_r = foliage_radius - layer * 2

            for dy in range(-layer_r, layer_r + 1):
                for dx in range(-layer_r, layer_r + 1):
                    dist = math.sqrt(dx * dx + dy * dy)
                    if dist <= layer_r:
                        px = cx + dx
                        py = layer_y + dy
                        if 0 <= px < self.width and 0 <= py < self.height:
                            # Vary leaf color
                            if dist < layer_r * 0.5:
                                color = leaf_light
                            elif dist < layer_r * 0.8:
                                color = leaf_color
                            else:
                                color = leaf_dark
                            # Add noise
                            if self.rng.random() < 0.2:
                                color = leaf_dark
                            canvas.set_pixel_solid(px, py, color)

        return canvas

    def _generate_bush(self, variant: str = None) -> Canvas:
        """Generate a bush."""
        canvas = Canvas(self.width, self.height)

        leaf_color = (70, 140, 50, 255)
        leaf_light = (100, 170, 70, 255)
        leaf_dark = (45, 100, 35, 255)

        cx = self.width // 2
        cy = self.height // 2 + 2

        bush_rx = self.width // 2 - 2
        bush_ry = self.height // 3

        # Draw bush as ellipse with noise
        for y in range(self.height):
            for x in range(self.width):
                dx = x - cx
                dy = y - cy
                dist = (dx / bush_rx) ** 2 + (dy / bush_ry) ** 2

                if dist <= 1.0:
                    noise = self.rng.random()
                    if dist < 0.4:
                        color = leaf_light
                    elif dist < 0.7 or noise < 0.7:
                        color = leaf_color
                    else:
                        color = leaf_dark
                    canvas.set_pixel_solid(x, y, color)

        return canvas

    def _generate_flower(self, variant: str = None) -> Canvas:
        """Generate a flower."""
        canvas = Canvas(self.width, self.height)

        # Random flower color
        flower_colors = [
            (255, 100, 100, 255),  # Red
            (255, 200, 100, 255),  # Yellow
            (255, 150, 200, 255),  # Pink
            (150, 100, 255, 255),  # Purple
            (100, 200, 255, 255),  # Blue
        ]
        petal_color = self.rng.choice(flower_colors)
        center_color = (255, 220, 100, 255)
        stem_color = (60, 130, 50, 255)

        cx = self.width // 2
        base_y = self.height - 1

        # Stem
        stem_height = self.height // 2
        for y in range(stem_height):
            canvas.set_pixel_solid(cx, base_y - y, stem_color)

        # Flower head
        flower_y = base_y - stem_height - 2
        petal_size = max(2, self.width // 4)

        # Petals (4 directions)
        offsets = [(0, -petal_size), (petal_size, 0), (0, petal_size), (-petal_size, 0)]
        for dx, dy in offsets:
            canvas.fill_circle(cx + dx, flower_y + dy, petal_size - 1, petal_color)

        # Center
        canvas.fill_circle(cx, flower_y, petal_size - 2, center_color)

        return canvas

    def _generate_mushroom(self, variant: str = None) -> Canvas:
        """Generate a mushroom."""
        canvas = Canvas(self.width, self.height)

        # Mushroom colors
        cap_color = (200, 60, 60, 255)
        cap_light = (230, 100, 100, 255)
        spot_color = (255, 255, 220, 255)
        stem_color = (240, 230, 200, 255)
        stem_dark = (200, 190, 160, 255)

        cx = self.width // 2
        base_y = self.height - 1

        # Stem
        stem_width = max(3, self.width // 4)
        stem_height = self.height // 2

        for y in range(stem_height):
            progress = y / stem_height
            width = int(stem_width * (0.8 + progress * 0.4))
            for dx in range(-width // 2, width // 2 + 1):
                px = cx + dx
                py = base_y - y
                if 0 <= px < self.width:
                    if dx < 0:
                        canvas.set_pixel_solid(px, py, stem_color)
                    else:
                        canvas.set_pixel_solid(px, py, stem_dark)

        # Cap
        cap_y = base_y - stem_height
        cap_radius = self.width // 2 - 1

        for dy in range(-cap_radius, 1):
            for dx in range(-cap_radius, cap_radius + 1):
                dist = math.sqrt(dx * dx + dy * dy)
                if dist <= cap_radius and dy <= 0:
                    px = cx + dx
                    py = cap_y + dy
                    if 0 <= px < self.width and 0 <= py < self.height:
                        if dy > -cap_radius // 2:
                            canvas.set_pixel_solid(px, py, cap_color)
                        else:
                            canvas.set_pixel_solid(px, py, cap_light)

        # Spots
        spot_positions = [(cx - 2, cap_y - 3), (cx + 2, cap_y - 2), (cx, cap_y - 4)]
        for sx, sy in spot_positions:
            if 0 <= sx < self.width and 0 <= sy < self.height:
                canvas.set_pixel_solid(sx, sy, spot_color)

        return canvas

    def _generate_torch(self, variant: str = None) -> Canvas:
        """Generate a wall torch."""
        canvas = Canvas(self.width, self.height)

        handle_color = (100, 70, 50, 255)
        metal_color = (120, 120, 130, 255)
        flame_inner = (255, 220, 100, 255)
        flame_mid = (255, 150, 50, 255)
        flame_outer = (255, 100, 50, 255)

        cx = self.width // 2
        base_y = self.height - 2

        # Handle
        handle_width = 2
        handle_height = self.height // 2

        for y in range(handle_height):
            for dx in range(-handle_width // 2, handle_width // 2 + 1):
                px = cx + dx
                py = base_y - y
                if 0 <= px < self.width:
                    canvas.set_pixel_solid(px, py, handle_color)

        # Metal holder
        holder_y = base_y - handle_height
        canvas.fill_rect(cx - 2, holder_y, 4, 3, metal_color)

        # Flame
        flame_y = holder_y - 3
        flame_height = 5

        for y in range(flame_height):
            progress = y / flame_height
            width = int(3 * (1 - progress * 0.7))

            for dx in range(-width, width + 1):
                px = cx + dx
                py = flame_y - y
                if 0 <= px < self.width and 0 <= py < self.height:
                    if progress < 0.3:
                        canvas.set_pixel_solid(px, py, flame_inner)
                    elif progress < 0.6:
                        canvas.set_pixel_solid(px, py, flame_mid)
                    else:
                        canvas.set_pixel_solid(px, py, flame_outer)

        return canvas

    def _generate_candle(self, variant: str = None) -> Canvas:
        """Generate a candle."""
        canvas = Canvas(self.width, self.height)

        wax_color = (240, 235, 220, 255)
        wax_light = (255, 250, 240, 255)
        wick_color = (60, 50, 40, 255)
        flame_inner = (255, 255, 200, 255)
        flame_outer = (255, 200, 100, 255)

        cx = self.width // 2
        base_y = self.height - 2

        # Candle body
        candle_width = max(4, self.width // 3)
        candle_height = self.height // 2

        for y in range(candle_height):
            for dx in range(-candle_width // 2, candle_width // 2 + 1):
                px = cx + dx
                py = base_y - y
                if 0 <= px < self.width:
                    if dx < 0:
                        canvas.set_pixel_solid(px, py, wax_light)
                    else:
                        canvas.set_pixel_solid(px, py, wax_color)

        # Wick
        wick_y = base_y - candle_height
        for y in range(3):
            canvas.set_pixel_solid(cx, wick_y - y, wick_color)

        # Flame
        flame_y = wick_y - 4
        canvas.fill_circle(cx, flame_y, 2, flame_inner)
        canvas.set_pixel_solid(cx, flame_y - 2, flame_outer)
        canvas.set_pixel_solid(cx - 1, flame_y, flame_outer)
        canvas.set_pixel_solid(cx + 1, flame_y, flame_outer)

        return canvas

    def _generate_sign(self, variant: str = None) -> Canvas:
        """Generate a wooden sign."""
        canvas = Canvas(self.width, self.height)
        self.palette = PropPalette.wood()

        cx = self.width // 2
        base_y = self.height - 1

        # Post
        post_width = 2
        post_height = self.height // 2

        for y in range(post_height):
            for dx in range(-post_width // 2, post_width // 2 + 1):
                px = cx + dx
                py = base_y - y
                if 0 <= px < self.width:
                    canvas.set_pixel_solid(px, py, self.palette.shadow)

        # Sign board
        board_width = self.width - 4
        board_height = self.height // 2 - 2
        board_y = base_y - post_height - board_height

        canvas.fill_rect(cx - board_width // 2, board_y, board_width, board_height,
                         self.palette.primary)

        # Border
        border_left = cx - board_width // 2
        for x in range(board_width):
            canvas.set_pixel_solid(border_left + x, board_y, self.palette.shadow)
            canvas.set_pixel_solid(border_left + x, board_y + board_height - 1,
                                   self.palette.shadow)
        for y in range(board_height):
            canvas.set_pixel_solid(border_left, board_y + y, self.palette.shadow)
            canvas.set_pixel_solid(border_left + board_width - 1, board_y + y,
                                   self.palette.shadow)

        return canvas

    def _generate_gravestone(self, variant: str = None) -> Canvas:
        """Generate a gravestone."""
        canvas = Canvas(self.width, self.height)

        stone_color = (120, 120, 130, 255)
        stone_light = (150, 150, 160, 255)
        stone_dark = (80, 80, 90, 255)
        moss_color = (60, 90, 50, 255)

        cx = self.width // 2
        base_y = self.height - 2

        stone_width = self.width - 6
        stone_height = self.height - 4
        stone_left = cx - stone_width // 2

        # Main stone body
        canvas.fill_rect(stone_left, base_y - stone_height + 3,
                         stone_width, stone_height - 3, stone_color)

        # Rounded top
        for y in range(3):
            curve = int((1 - (y / 3) ** 2) * 2)
            row_left = stone_left + curve
            row_width = stone_width - curve * 2
            canvas.fill_rect(row_left, base_y - stone_height + y, row_width, 1,
                             stone_color)

        # Shading
        for y in range(stone_height):
            py = base_y - y
            # Left edge highlight
            canvas.set_pixel_solid(stone_left + 1, py, stone_light)
            # Right edge shadow
            canvas.set_pixel_solid(stone_left + stone_width - 2, py, stone_dark)

        # Moss at base
        for x in range(stone_left, stone_left + stone_width):
            if self.rng.random() < 0.4:
                canvas.set_pixel_solid(x, base_y - 1, moss_color)
                if self.rng.random() < 0.3:
                    canvas.set_pixel_solid(x, base_y - 2, moss_color)

        # Cross or RIP text (simplified)
        text_y = base_y - stone_height // 2
        # Horizontal line
        canvas.fill_rect(stone_left + 3, text_y, stone_width - 6, 1, stone_dark)
        # Vertical line
        canvas.fill_rect(cx, text_y - 2, 1, 5, stone_dark)

        return canvas


# Convenience functions
def generate_prop(prop_type: str, variant: str = None,
                  width: int = 16, height: int = 16, seed: int = 42,
                  hd_mode: bool = False, style: Optional['Style'] = None) -> Canvas:
    """Generate a prop of the specified type.

    Args:
        prop_type: Type of prop
        variant: Optional variant
        width: Canvas width
        height: Canvas height
        seed: Random seed
        hd_mode: Enable HD quality features (selout, AA)
        style: Style configuration for quality settings

    Returns:
        Canvas with generated prop
    """
    gen = PropGenerator(width, height, seed, style=style, hd_mode=hd_mode)
    return gen.generate(prop_type, variant)


def list_prop_types() -> List[str]:
    """List all available prop types."""
    return [
        'chest', 'barrel', 'crate', 'pot', 'vase', 'sack',
        'table', 'chair', 'bed', 'bookshelf',
        'tree', 'bush', 'flower', 'mushroom',
        'torch', 'candle', 'sign', 'gravestone'
    ]


def list_chest_types() -> List[str]:
    """List chest variants."""
    return [c.value for c in ChestType]


def list_container_types() -> List[str]:
    """List container types."""
    return [c.value for c in ContainerType]


def list_furniture_types() -> List[str]:
    """List furniture types."""
    return [f.value for f in FurnitureType]


def list_vegetation_types() -> List[str]:
    """List vegetation types."""
    return [v.value for v in VegetationType]


def list_decoration_types() -> List[str]:
    """List decoration types."""
    return [d.value for d in DecorationTypeEnum]

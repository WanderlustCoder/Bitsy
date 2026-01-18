"""
Held Items - Books, bags, cups, and other items characters can hold.

Provides items that can be held in the character's hands:
- Books (open and closed)
- Bags and satchels
- Cups and mugs
- Flowers
- Other small props

These require the character to be in a holding pose.
"""

import math
from typing import Optional, List, Tuple
from dataclasses import dataclass

from .base import Part, PartConfig
from .equipment import Equipment, EquipmentConfig, EquipmentSlot, DrawLayer

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.canvas import Canvas
from core.color import Color, lighten, darken


class HeldItem(Equipment):
    """Base class for items held in hands."""

    def __init__(self, name: str, config: Optional[EquipmentConfig] = None,
                 hand: str = 'both'):
        if config is None:
            config = EquipmentConfig()
        config.slot = EquipmentSlot.HAND_RIGHT
        config.layer = DrawLayer.FRONT
        super().__init__(name, config)
        self.hand = hand  # 'left', 'right', 'both'


class Book(HeldItem):
    """A book held in both hands.

    Features:
    - Cover with customizable color
    - Visible pages
    - Spine detail
    - Page line textures
    """

    def __init__(self, config: Optional[EquipmentConfig] = None,
                 cover_color: Optional[Color] = None):
        super().__init__("book", config, hand='both')

        # Default colors
        self.cover_color = cover_color or (120, 70, 50, 255)  # Brown leather
        self.pages_color = (250, 245, 235, 255)  # Cream pages
        self.spine_color = darken(self.cover_color, 0.3)
        self.page_line_color = darken(self.pages_color, 0.15)

    def draw(self, canvas: Canvas, x: int, y: int, width: int, height: int) -> None:
        """Draw the book at the specified position.

        Args:
            x, y: Center position
            width, height: Available space
        """
        # Book dimensions (relative to available space)
        book_w = int(width * 0.75)
        book_h = int(height * 0.55)

        # Position adjustments
        bx = x - book_w // 2
        by = y - book_h // 2

        # Back cover shadow
        shadow_color = darken(self.cover_color, 0.4)
        canvas.fill_rect(bx + 2, by + 2, book_w, book_h, shadow_color)

        # Pages (slightly inset, visible at edge)
        pages_inset = 2
        canvas.fill_rect(bx + pages_inset, by,
                        book_w - pages_inset - 1, book_h - 1, self.pages_color)

        # Front cover (main)
        cover_w = book_w - pages_inset - 3
        canvas.fill_rect(bx, by, cover_w, book_h, self.cover_color)

        # Cover highlight
        highlight = lighten(self.cover_color, 0.25)
        canvas.fill_rect(bx + 2, by + 2, cover_w // 3, 2, highlight)

        # Cover shadow at bottom
        cover_shadow = darken(self.cover_color, 0.2)
        canvas.fill_rect(bx, by + book_h - 2, cover_w, 2, cover_shadow)

        # Spine
        spine_w = 3
        canvas.fill_rect(bx, by, spine_w, book_h, self.spine_color)

        # Spine highlight
        spine_highlight = lighten(self.spine_color, 0.3)
        canvas.draw_line(bx + 1, by + 2, bx + 1, by + book_h - 2, spine_highlight)

        # Page lines (texture)
        page_start_x = bx + cover_w + 1
        num_lines = min(5, book_h // 4)
        for i in range(num_lines):
            line_y = by + 3 + i * (book_h - 6) // max(1, num_lines - 1)
            canvas.draw_line(page_start_x, line_y,
                           bx + book_w - 2, line_y, self.page_line_color)


class OpenBook(HeldItem):
    """An open book showing pages."""

    def __init__(self, config: Optional[EquipmentConfig] = None,
                 cover_color: Optional[Color] = None):
        super().__init__("open_book", config, hand='both')

        self.cover_color = cover_color or (120, 70, 50, 255)
        self.pages_color = (250, 245, 235, 255)
        self.text_color = (60, 50, 45, 255)

    def draw(self, canvas: Canvas, x: int, y: int, width: int, height: int) -> None:
        book_w = int(width * 0.9)
        book_h = int(height * 0.6)

        bx = x - book_w // 2
        by = y - book_h // 2

        # Back covers (slightly visible)
        back_color = darken(self.cover_color, 0.3)
        canvas.fill_rect(bx - 1, by + 2, book_w + 2, book_h, back_color)

        # Left page
        page_w = book_w // 2 - 2
        canvas.fill_rect(bx, by, page_w, book_h, self.pages_color)

        # Right page
        canvas.fill_rect(x + 2, by, page_w, book_h, self.pages_color)

        # Spine shadow in center
        spine_shadow = (200, 190, 180, 255)
        canvas.fill_rect(x - 1, by, 2, book_h, spine_shadow)

        # Text lines on left page
        for i in range(4):
            line_y = by + 3 + i * 3
            line_w = page_w - 4 - (i % 2) * 3  # Varying line lengths
            canvas.draw_line(bx + 2, line_y, bx + 2 + line_w, line_y, self.text_color)

        # Text lines on right page
        for i in range(4):
            line_y = by + 3 + i * 3
            line_w = page_w - 4 - ((i + 1) % 2) * 3
            canvas.draw_line(x + 4, line_y, x + 4 + line_w, line_y, self.text_color)

        # Page curl shadow on right
        curl_shadow = darken(self.pages_color, 0.1)
        canvas.fill_rect(x + 2 + page_w - 2, by, 2, book_h, curl_shadow)


class Scroll(HeldItem):
    """A rolled scroll."""

    def __init__(self, config: Optional[EquipmentConfig] = None):
        super().__init__("scroll", config, hand='both')

        self.paper_color = (245, 235, 210, 255)
        self.rod_color = (100, 70, 50, 255)
        self.text_color = (50, 40, 35, 255)

    def draw(self, canvas: Canvas, x: int, y: int, width: int, height: int) -> None:
        scroll_w = int(width * 0.7)
        scroll_h = int(height * 0.65)

        sx = x - scroll_w // 2
        sy = y - scroll_h // 2

        # Paper roll
        canvas.fill_rect(sx, sy + 2, scroll_w, scroll_h - 4, self.paper_color)

        # Shadow at edges
        shadow = darken(self.paper_color, 0.15)
        canvas.fill_rect(sx, sy + 2, 2, scroll_h - 4, shadow)
        canvas.fill_rect(sx + scroll_w - 2, sy + 2, 2, scroll_h - 4, shadow)

        # Top rod
        canvas.fill_rect(sx - 2, sy, scroll_w + 4, 3, self.rod_color)
        canvas.fill_circle(sx - 2, sy + 1, 2, self.rod_color)
        canvas.fill_circle(sx + scroll_w + 2, sy + 1, 2, self.rod_color)

        # Bottom rod
        canvas.fill_rect(sx - 2, sy + scroll_h - 3, scroll_w + 4, 3, self.rod_color)

        # Text lines
        for i in range(3):
            line_y = sy + 5 + i * 4
            line_w = scroll_w - 6 - (i % 2) * 4
            canvas.draw_line(sx + 3, line_y, sx + 3 + line_w, line_y, self.text_color)


class Flower(HeldItem):
    """A single flower."""

    def __init__(self, config: Optional[EquipmentConfig] = None,
                 petal_color: Optional[Color] = None):
        super().__init__("flower", config, hand='right')

        self.petal_color = petal_color or (255, 150, 180, 255)  # Pink
        self.center_color = (255, 220, 100, 255)  # Yellow center
        self.stem_color = (80, 140, 60, 255)  # Green

    def draw(self, canvas: Canvas, x: int, y: int, width: int, height: int) -> None:
        # Stem
        stem_bottom = y + height // 3
        canvas.draw_line(x, y, x, stem_bottom, self.stem_color, thickness=2)

        # Leaf
        canvas.fill_ellipse(x + 3, y + height // 6, 3, 2, self.stem_color)

        # Petals
        petal_r = max(3, width // 5)
        offsets = [(-petal_r // 2, -petal_r // 2), (petal_r // 2, -petal_r // 2),
                   (-petal_r // 2, petal_r // 2), (petal_r // 2, petal_r // 2),
                   (0, -petal_r), (0, petal_r)]

        flower_y = y - height // 4
        for dx, dy in offsets:
            canvas.fill_ellipse(x + dx, flower_y + dy, petal_r, petal_r - 1, self.petal_color)

        # Center
        canvas.fill_circle(x, flower_y, petal_r // 2, self.center_color)


class Cup(HeldItem):
    """A cup or mug."""

    def __init__(self, config: Optional[EquipmentConfig] = None,
                 cup_color: Optional[Color] = None):
        super().__init__("cup", config, hand='right')

        self.cup_color = cup_color or (220, 200, 180, 255)  # Ceramic
        self.liquid_color = (100, 70, 50, 255)  # Coffee/tea
        self.handle_color = darken(self.cup_color, 0.1)

    def draw(self, canvas: Canvas, x: int, y: int, width: int, height: int) -> None:
        cup_w = int(width * 0.4)
        cup_h = int(height * 0.5)

        cx = x - cup_w // 2
        cy = y - cup_h // 2

        # Cup body
        canvas.fill_rect(cx, cy, cup_w, cup_h, self.cup_color)

        # Highlight
        highlight = lighten(self.cup_color, 0.2)
        canvas.fill_rect(cx + 1, cy + 1, 2, cup_h - 2, highlight)

        # Shadow
        shadow = darken(self.cup_color, 0.15)
        canvas.fill_rect(cx + cup_w - 2, cy + 1, 2, cup_h - 2, shadow)

        # Liquid surface
        liquid_y = cy + 2
        canvas.fill_rect(cx + 1, liquid_y, cup_w - 2, 3, self.liquid_color)

        # Handle
        handle_x = cx + cup_w
        handle_cy = cy + cup_h // 2
        canvas.draw_circle(handle_x + 2, handle_cy, 3, self.handle_color)


class Bag(HeldItem):
    """A small bag or satchel."""

    def __init__(self, config: Optional[EquipmentConfig] = None,
                 bag_color: Optional[Color] = None):
        super().__init__("bag", config, hand='left')

        self.bag_color = bag_color or (100, 70, 50, 255)  # Leather brown
        self.strap_color = darken(self.bag_color, 0.2)
        self.buckle_color = (180, 160, 100, 255)  # Brass

    def draw(self, canvas: Canvas, x: int, y: int, width: int, height: int) -> None:
        bag_w = int(width * 0.5)
        bag_h = int(height * 0.6)

        bx = x - bag_w // 2
        by = y - bag_h // 2

        # Bag body
        canvas.fill_rect(bx, by, bag_w, bag_h, self.bag_color)

        # Flap
        flap_h = bag_h // 3
        canvas.fill_rect(bx - 1, by - 1, bag_w + 2, flap_h + 2, self.bag_color)

        # Highlight
        highlight = lighten(self.bag_color, 0.2)
        canvas.fill_rect(bx + 1, by + 1, bag_w // 3, flap_h - 2, highlight)

        # Shadow under flap
        shadow = darken(self.bag_color, 0.2)
        canvas.fill_rect(bx, by + flap_h, bag_w, 2, shadow)

        # Strap
        canvas.draw_line(bx, by - 2, bx - width // 4, by - height // 3, self.strap_color)
        canvas.draw_line(bx + bag_w, by - 2, bx + bag_w + width // 4, by - height // 3, self.strap_color)

        # Buckle
        buckle_x = x - 1
        buckle_y = by + flap_h - 1
        canvas.fill_rect(buckle_x, buckle_y, 3, 2, self.buckle_color)


# Registry of held item types
HELD_ITEM_TYPES = {
    'book': Book,
    'open_book': OpenBook,
    'scroll': Scroll,
    'flower': Flower,
    'cup': Cup,
    'bag': Bag,
}


def create_held_item(item_type: str,
                     config: Optional[EquipmentConfig] = None,
                     **kwargs) -> HeldItem:
    """Create a held item by type name.

    Args:
        item_type: Type name ('book', 'flower', etc.)
        config: Optional equipment configuration
        **kwargs: Additional arguments for specific item types

    Returns:
        HeldItem instance
    """
    if item_type not in HELD_ITEM_TYPES:
        available = ', '.join(HELD_ITEM_TYPES.keys())
        raise ValueError(f"Unknown held item '{item_type}'. Available: {available}")

    return HELD_ITEM_TYPES[item_type](config, **kwargs)


def list_held_item_types() -> List[str]:
    """List available held item types."""
    return list(HELD_ITEM_TYPES.keys())

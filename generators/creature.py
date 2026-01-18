"""
Creature Generator - Procedural generation of monsters and enemies.

Generates pixel art for:
- Slimes (various sizes and colors)
- Beasts (wolves, bears, boars)
- Undead (skeletons, zombies, ghosts)
- Elementals (fire, ice, earth, lightning)
- Insects (spiders, beetles, bees)
- Mythical (dragons, phoenixes, basilisks)
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
from core.color import darken, lighten, shift_hue
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.style import Style as StyleType


class CreatureType(Enum):
    """Main creature categories."""
    SLIME = 'slime'
    BEAST = 'beast'
    UNDEAD = 'undead'
    ELEMENTAL = 'elemental'
    INSECT = 'insect'
    MYTHICAL = 'mythical'
    HUMANOID = 'humanoid'


class SlimeVariant(Enum):
    """Slime variants."""
    BASIC = 'basic'
    KING = 'king'
    METAL = 'metal'
    POISON = 'poison'
    FIRE = 'fire'
    ICE = 'ice'


class BeastVariant(Enum):
    """Beast variants."""
    WOLF = 'wolf'
    BEAR = 'bear'
    BOAR = 'boar'
    BAT = 'bat'
    RAT = 'rat'


class UndeadVariant(Enum):
    """Undead variants."""
    SKELETON = 'skeleton'
    ZOMBIE = 'zombie'
    GHOST = 'ghost'
    WRAITH = 'wraith'
    VAMPIRE = 'vampire'


class ElementalVariant(Enum):
    """Elemental variants."""
    FIRE = 'fire'
    ICE = 'ice'
    EARTH = 'earth'
    LIGHTNING = 'lightning'
    WATER = 'water'
    WIND = 'wind'


class InsectVariant(Enum):
    """Insect variants."""
    SPIDER = 'spider'
    BEETLE = 'beetle'
    BEE = 'bee'
    SCORPION = 'scorpion'
    ANT = 'ant'


@dataclass
class CreaturePalette:
    """Color palette for creature generation."""
    body: Tuple[int, int, int, int] = (100, 150, 100, 255)
    body_light: Tuple[int, int, int, int] = (130, 180, 130, 255)
    body_dark: Tuple[int, int, int, int] = (70, 110, 70, 255)
    eyes: Tuple[int, int, int, int] = (255, 50, 50, 255)
    accent: Tuple[int, int, int, int] = (200, 200, 100, 255)
    outline: Tuple[int, int, int, int] = (40, 60, 40, 255)

    @classmethod
    def green_slime(cls) -> 'CreaturePalette':
        return cls(
            body=(100, 200, 100, 255),
            body_light=(150, 230, 150, 255),
            body_dark=(60, 140, 60, 255),
            eyes=(255, 255, 255, 255),
            accent=(80, 160, 80, 255),
            outline=(40, 100, 40, 255)
        )

    @classmethod
    def blue_slime(cls) -> 'CreaturePalette':
        return cls(
            body=(100, 150, 220, 255),
            body_light=(150, 190, 250, 255),
            body_dark=(60, 100, 170, 255),
            eyes=(255, 255, 255, 255),
            accent=(80, 130, 200, 255),
            outline=(40, 80, 140, 255)
        )

    @classmethod
    def red_slime(cls) -> 'CreaturePalette':
        return cls(
            body=(220, 80, 80, 255),
            body_light=(250, 120, 120, 255),
            body_dark=(170, 50, 50, 255),
            eyes=(255, 255, 200, 255),
            accent=(200, 60, 60, 255),
            outline=(140, 30, 30, 255)
        )

    @classmethod
    def purple_slime(cls) -> 'CreaturePalette':
        return cls(
            body=(180, 100, 220, 255),
            body_light=(210, 150, 250, 255),
            body_dark=(130, 60, 170, 255),
            eyes=(255, 200, 255, 255),
            accent=(160, 80, 200, 255),
            outline=(100, 40, 140, 255)
        )

    @classmethod
    def metal_slime(cls) -> 'CreaturePalette':
        return cls(
            body=(180, 180, 200, 255),
            body_light=(220, 220, 240, 255),
            body_dark=(130, 130, 150, 255),
            eyes=(100, 100, 120, 255),
            accent=(200, 200, 220, 255),
            outline=(100, 100, 120, 255)
        )

    @classmethod
    def wolf(cls) -> 'CreaturePalette':
        return cls(
            body=(120, 110, 100, 255),
            body_light=(160, 150, 140, 255),
            body_dark=(80, 70, 60, 255),
            eyes=(200, 180, 50, 255),
            accent=(180, 170, 160, 255),
            outline=(50, 45, 40, 255)
        )

    @classmethod
    def skeleton(cls) -> 'CreaturePalette':
        return cls(
            body=(230, 220, 200, 255),
            body_light=(250, 245, 235, 255),
            body_dark=(180, 170, 150, 255),
            eyes=(200, 50, 50, 255),
            accent=(200, 190, 170, 255),
            outline=(140, 130, 110, 255)
        )

    @classmethod
    def zombie(cls) -> 'CreaturePalette':
        return cls(
            body=(100, 140, 90, 255),
            body_light=(130, 170, 120, 255),
            body_dark=(70, 100, 60, 255),
            eyes=(200, 200, 50, 255),
            accent=(120, 80, 80, 255),
            outline=(50, 70, 40, 255)
        )

    @classmethod
    def ghost(cls) -> 'CreaturePalette':
        return cls(
            body=(200, 210, 230, 200),
            body_light=(230, 240, 255, 180),
            body_dark=(160, 170, 200, 220),
            eyes=(100, 150, 255, 255),
            accent=(180, 190, 220, 190),
            outline=(140, 150, 180, 180)
        )

    @classmethod
    def fire_elemental(cls) -> 'CreaturePalette':
        return cls(
            body=(255, 150, 50, 255),
            body_light=(255, 220, 100, 255),
            body_dark=(220, 80, 30, 255),
            eyes=(255, 255, 200, 255),
            accent=(255, 100, 50, 255),
            outline=(180, 50, 20, 255)
        )

    @classmethod
    def ice_elemental(cls) -> 'CreaturePalette':
        return cls(
            body=(150, 200, 255, 255),
            body_light=(200, 230, 255, 255),
            body_dark=(100, 150, 220, 255),
            eyes=(255, 255, 255, 255),
            accent=(180, 220, 255, 255),
            outline=(80, 120, 180, 255)
        )

    @classmethod
    def spider(cls) -> 'CreaturePalette':
        return cls(
            body=(60, 50, 50, 255),
            body_light=(90, 80, 80, 255),
            body_dark=(40, 30, 30, 255),
            eyes=(200, 50, 50, 255),
            accent=(80, 70, 70, 255),
            outline=(30, 20, 20, 255)
        )


class CreatureGenerator:
    """Generates pixel art creatures."""

    def __init__(self, width: int = 32, height: int = 32, seed: int = 42,
                 style: Optional['Style'] = None, hd_mode: bool = False):
        """Initialize creature generator.

        Args:
            width: Creature width in pixels (default: 32)
            height: Creature height in pixels (default: 32)
            seed: Random seed for reproducibility
            style: Style configuration for quality settings (default: Style.default() unless hd_mode)
            hd_mode: Enable HD quality features (selout, AA)
        """
        self.width = width
        self.height = height
        self.seed = seed
        self.rng = random.Random(seed)
        self.palette = CreaturePalette.green_slime()
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

    def set_palette(self, palette: CreaturePalette) -> 'CreatureGenerator':
        """Set the color palette."""
        self.palette = palette
        return self

    def set_seed(self, seed: int) -> 'CreatureGenerator':
        """Set random seed."""
        self.seed = seed
        self.rng = random.Random(seed)
        return self

    def generate(self, creature_type: str, variant: str = None) -> Canvas:
        """Generate a creature of the specified type.

        Args:
            creature_type: Type of creature (slime, beast, undead, etc.)
            variant: Optional variant (basic, fire, skeleton, etc.)

        Returns:
            Canvas with the generated creature
        """
        creature_type = creature_type.lower()

        generators = {
            'slime': self._generate_slime,
            'beast': self._generate_beast,
            'undead': self._generate_undead,
            'elemental': self._generate_elemental,
            'insect': self._generate_insect,
            'ghost': self._generate_ghost,
            'skeleton': self._generate_skeleton,
            'zombie': self._generate_zombie,
            'wolf': self._generate_wolf,
            'bat': self._generate_bat,
            'spider': self._generate_spider,
            'fire_elemental': self._generate_fire_elemental,
            'ice_elemental': self._generate_ice_elemental,
        }

        if creature_type in generators:
            canvas = generators[creature_type](variant)
            return self.finalize(canvas)

        # Default to slime
        canvas = self._generate_slime(variant)
        return self.finalize(canvas)

    def _generate_slime(self, variant: str = None) -> Canvas:
        """Generate a slime creature."""
        canvas = Canvas(self.width, self.height)

        # Set palette based on variant
        if variant == 'fire':
            self.palette = CreaturePalette.red_slime()
        elif variant == 'ice':
            self.palette = CreaturePalette.blue_slime()
        elif variant == 'poison':
            self.palette = CreaturePalette.purple_slime()
        elif variant == 'metal':
            self.palette = CreaturePalette.metal_slime()
        elif variant == 'blue':
            self.palette = CreaturePalette.blue_slime()
        elif variant in (None, 'basic', 'green'):
            self.palette = CreaturePalette.green_slime()

        cx = self.width // 2
        cy = self.height // 2 + 2

        # Main body - rounded blob shape
        body_width = self.width - 4
        body_height = self.height - 5

        # Draw body as ellipse
        rx = body_width // 2
        ry = body_height // 2

        # Draw body (bottom-heavy ellipse)
        for y in range(self.height):
            for x in range(self.width):
                # Squash factor - wider at bottom
                dy = y - cy
                squash = 1.0 + dy * 0.03 if dy > 0 else 1.0

                dx = (x - cx) / squash
                dist_x = dx / rx if rx > 0 else 0
                dist_y = dy / ry if ry > 0 else 0
                dist = dist_x * dist_x + dist_y * dist_y

                if dist <= 1.0:
                    # Determine shading
                    if dist < 0.3:
                        # Highlight area (upper left)
                        if dx < 0 and dy < 0:
                            canvas.set_pixel_solid(x, y, self.palette.body_light)
                        else:
                            canvas.set_pixel_solid(x, y, self.palette.body)
                    elif dist < 0.7:
                        canvas.set_pixel_solid(x, y, self.palette.body)
                    else:
                        # Edge - darker or outline
                        if dist > 0.85:
                            canvas.set_pixel_solid(x, y, self.palette.outline)
                        else:
                            canvas.set_pixel_solid(x, y, self.palette.body_dark)

        # Draw eyes
        eye_y = cy - ry // 2
        eye_spacing = max(2, rx // 2)

        # Left eye
        canvas.set_pixel_solid(cx - eye_spacing, eye_y, self.palette.eyes)
        canvas.set_pixel_solid(cx - eye_spacing, eye_y + 1, self.palette.eyes)

        # Right eye
        canvas.set_pixel_solid(cx + eye_spacing - 1, eye_y, self.palette.eyes)
        canvas.set_pixel_solid(cx + eye_spacing - 1, eye_y + 1, self.palette.eyes)

        # Add shine/highlight
        highlight_x = cx - rx // 2
        highlight_y = cy - ry // 2 - 1
        if 0 <= highlight_x < self.width and 0 <= highlight_y < self.height:
            canvas.set_pixel_solid(highlight_x, highlight_y, self.palette.body_light)
            if highlight_x + 1 < self.width:
                canvas.set_pixel_solid(highlight_x + 1, highlight_y, self.palette.body_light)

        return canvas

    def _generate_ghost(self, variant: str = None) -> Canvas:
        """Generate a ghost creature."""
        canvas = Canvas(self.width, self.height)
        self.palette = CreaturePalette.ghost()

        cx = self.width // 2
        head_y = 3

        # Draw ghostly body - rounded top, wavy bottom
        body_width = self.width - 4
        head_radius = body_width // 2

        # Head (circle)
        for y in range(self.height - 3):
            for x in range(self.width):
                dx = x - cx
                dy = y - head_y - head_radius

                # Upper part - circular head
                if dy <= 0:
                    dist = math.sqrt(dx * dx + dy * dy)
                    if dist <= head_radius:
                        if dist < head_radius - 2:
                            canvas.set_pixel_solid(x, y, self.palette.body)
                        elif dist < head_radius - 1:
                            canvas.set_pixel_solid(x, y, self.palette.body_dark)
                        else:
                            canvas.set_pixel_solid(x, y, self.palette.outline)
                # Lower part - trailing body
                else:
                    if abs(dx) < head_radius:
                        # Wavy bottom edge
                        wave = int(math.sin((x + self.rng.random() * 2) * 0.8) * 2)
                        max_y = self.height - 3 + wave

                        if y < max_y:
                            if y > max_y - 2:
                                canvas.set_pixel_solid(x, y, self.palette.body_dark)
                            else:
                                canvas.set_pixel_solid(x, y, self.palette.body)

        # Draw eyes
        eye_y = head_y + head_radius - 2
        eye_spacing = head_radius // 2

        canvas.set_pixel_solid(cx - eye_spacing, eye_y, self.palette.eyes)
        canvas.set_pixel_solid(cx - eye_spacing + 1, eye_y, self.palette.eyes)
        canvas.set_pixel_solid(cx + eye_spacing - 1, eye_y, self.palette.eyes)
        canvas.set_pixel_solid(cx + eye_spacing, eye_y, self.palette.eyes)

        return canvas

    def _generate_skeleton(self, variant: str = None) -> Canvas:
        """Generate a skeleton creature."""
        canvas = Canvas(self.width, self.height)
        self.palette = CreaturePalette.skeleton()

        cx = self.width // 2

        # Skull
        skull_y = 2
        skull_size = 5

        # Draw skull
        canvas.fill_circle(cx, skull_y + skull_size // 2, skull_size // 2, self.palette.body)

        # Eye sockets
        eye_y = skull_y + skull_size // 2
        canvas.set_pixel_solid(cx - 2, eye_y, self.palette.eyes)
        canvas.set_pixel_solid(cx + 1, eye_y, self.palette.eyes)

        # Nose hole
        canvas.set_pixel_solid(cx, eye_y + 2, self.palette.body_dark)

        # Spine
        spine_top = skull_y + skull_size
        for y in range(spine_top, self.height - 3):
            canvas.set_pixel_solid(cx, y, self.palette.body)
            if y % 2 == 0:
                canvas.set_pixel_solid(cx - 1, y, self.palette.body_dark)
                canvas.set_pixel_solid(cx + 1, y, self.palette.body_dark)

        # Ribs
        rib_y = spine_top + 1
        for i in range(3):
            y = rib_y + i * 2
            if y < self.height - 4:
                for dx in range(1, 4):
                    canvas.set_pixel_solid(cx - dx, y, self.palette.body)
                    canvas.set_pixel_solid(cx + dx, y, self.palette.body)

        # Arms
        arm_y = spine_top + 1
        # Left arm
        for i in range(4):
            canvas.set_pixel_solid(cx - 4 - i, arm_y + i, self.palette.body)
        # Right arm
        for i in range(4):
            canvas.set_pixel_solid(cx + 4 + i, arm_y + i, self.palette.body)

        # Legs
        leg_y = self.height - 4
        # Left leg
        for i in range(3):
            canvas.set_pixel_solid(cx - 2, leg_y + i, self.palette.body)
        # Right leg
        for i in range(3):
            canvas.set_pixel_solid(cx + 2, leg_y + i, self.palette.body)

        return canvas

    def _generate_zombie(self, variant: str = None) -> Canvas:
        """Generate a zombie creature."""
        canvas = Canvas(self.width, self.height)
        self.palette = CreaturePalette.zombie()

        cx = self.width // 2

        # Head
        head_y = 2
        head_size = 5
        canvas.fill_circle(cx, head_y + head_size // 2, head_size // 2, self.palette.body)

        # Tattered features
        canvas.set_pixel_solid(cx - 2, head_y + 2, self.palette.eyes)
        canvas.set_pixel_solid(cx + 1, head_y + 2, self.palette.eyes)

        # Mouth
        for dx in range(-1, 2):
            canvas.set_pixel_solid(cx + dx, head_y + head_size - 1, self.palette.body_dark)

        # Body - hunched
        body_top = head_y + head_size
        body_width = 6
        body_height = 6

        for y in range(body_top, body_top + body_height):
            offset = (y - body_top) // 2
            for dx in range(-body_width // 2 + offset, body_width // 2 - offset + 1):
                canvas.set_pixel_solid(cx + dx, y, self.palette.body)

        # Arms (reaching forward)
        arm_y = body_top + 1
        # Left arm extended
        for i in range(5):
            canvas.set_pixel_solid(cx - 4 - i, arm_y, self.palette.body)
            canvas.set_pixel_solid(cx - 4 - i, arm_y + 1, self.palette.body_dark)
        # Right arm drooping
        for i in range(4):
            canvas.set_pixel_solid(cx + 4 + i // 2, arm_y + i, self.palette.body)

        # Legs
        leg_y = body_top + body_height
        for i in range(3):
            canvas.set_pixel_solid(cx - 2, leg_y + i, self.palette.body)
            canvas.set_pixel_solid(cx + 1, leg_y + i, self.palette.body)

        return canvas

    def _generate_wolf(self, variant: str = None) -> Canvas:
        """Generate a wolf creature."""
        canvas = Canvas(self.width, self.height)
        self.palette = CreaturePalette.wolf()

        # Body center (horizontal creature)
        body_cx = self.width // 2
        body_cy = self.height - 5

        # Body (oval, horizontal)
        body_rx = 5
        body_ry = 3

        for y in range(self.height):
            for x in range(self.width):
                dx = x - body_cx
                dy = y - body_cy
                dist = (dx / body_rx) ** 2 + (dy / body_ry) ** 2

                if dist <= 1.0:
                    if dist < 0.5:
                        canvas.set_pixel_solid(x, y, self.palette.body)
                    else:
                        canvas.set_pixel_solid(x, y, self.palette.body_dark)

        # Head
        head_cx = body_cx + body_rx - 1
        head_cy = body_cy - 1
        head_r = 3

        canvas.fill_circle(head_cx, head_cy, head_r, self.palette.body)

        # Snout
        snout_x = head_cx + head_r
        for dx in range(3):
            canvas.set_pixel_solid(snout_x + dx, head_cy, self.palette.body)
            canvas.set_pixel_solid(snout_x + dx, head_cy + 1, self.palette.body_dark)

        # Nose
        canvas.set_pixel_solid(snout_x + 2, head_cy, self.palette.outline)

        # Eye
        canvas.set_pixel_solid(head_cx + 1, head_cy - 1, self.palette.eyes)

        # Ears
        canvas.set_pixel_solid(head_cx - 1, head_cy - head_r, self.palette.body)
        canvas.set_pixel_solid(head_cx + 1, head_cy - head_r, self.palette.body)

        # Legs
        leg_y = body_cy + body_ry
        for i in range(3):
            canvas.set_pixel_solid(body_cx - 3, leg_y + i, self.palette.body_dark)
            canvas.set_pixel_solid(body_cx - 1, leg_y + i, self.palette.body_dark)
            canvas.set_pixel_solid(body_cx + 1, leg_y + i, self.palette.body_dark)
            canvas.set_pixel_solid(body_cx + 3, leg_y + i, self.palette.body_dark)

        # Tail
        tail_x = body_cx - body_rx
        for i in range(3):
            canvas.set_pixel_solid(tail_x - i, body_cy - i, self.palette.body)

        return canvas

    def _generate_bat(self, variant: str = None) -> Canvas:
        """Generate a bat creature."""
        canvas = Canvas(self.width, self.height)

        # Dark palette for bat
        self.palette = CreaturePalette(
            body=(80, 60, 80, 255),
            body_light=(100, 80, 100, 255),
            body_dark=(50, 40, 50, 255),
            eyes=(255, 50, 50, 255),
            accent=(90, 70, 90, 255),
            outline=(30, 20, 30, 255)
        )

        cx = self.width // 2
        cy = self.height // 2

        # Body (small oval)
        body_rx = 2
        body_ry = 3

        for y in range(self.height):
            for x in range(self.width):
                dx = x - cx
                dy = y - cy
                dist = (dx / body_rx) ** 2 + (dy / body_ry) ** 2

                if dist <= 1.0:
                    canvas.set_pixel_solid(x, y, self.palette.body)

        # Head
        head_y = cy - body_ry
        canvas.fill_circle(cx, head_y, 2, self.palette.body)

        # Ears
        canvas.set_pixel_solid(cx - 2, head_y - 2, self.palette.body)
        canvas.set_pixel_solid(cx + 1, head_y - 2, self.palette.body)

        # Eyes
        canvas.set_pixel_solid(cx - 1, head_y, self.palette.eyes)
        canvas.set_pixel_solid(cx + 1, head_y, self.palette.eyes)

        # Wings (spread out)
        wing_y = cy - 1
        for i in range(5):
            # Left wing
            canvas.set_pixel_solid(cx - 3 - i, wing_y + i // 2, self.palette.body)
            canvas.set_pixel_solid(cx - 3 - i, wing_y + i // 2 + 1, self.palette.body_dark)
            # Right wing
            canvas.set_pixel_solid(cx + 3 + i, wing_y + i // 2, self.palette.body)
            canvas.set_pixel_solid(cx + 3 + i, wing_y + i // 2 + 1, self.palette.body_dark)

        # Wing membrane
        for i in range(3):
            for j in range(i + 2):
                canvas.set_pixel_solid(cx - 3 - j, wing_y + i, self.palette.body_dark)
                canvas.set_pixel_solid(cx + 3 + j, wing_y + i, self.palette.body_dark)

        return canvas

    def _generate_spider(self, variant: str = None) -> Canvas:
        """Generate a spider creature."""
        canvas = Canvas(self.width, self.height)
        self.palette = CreaturePalette.spider()

        cx = self.width // 2
        cy = self.height // 2

        # Body segments
        # Abdomen (larger, back)
        abd_cx = cx
        abd_cy = cy + 2
        canvas.fill_circle(abd_cx, abd_cy, 4, self.palette.body)
        canvas.fill_circle(abd_cx, abd_cy, 3, self.palette.body_light)

        # Cephalothorax (smaller, front)
        head_cx = cx
        head_cy = cy - 2
        canvas.fill_circle(head_cx, head_cy, 2, self.palette.body)

        # Eyes (multiple)
        canvas.set_pixel_solid(head_cx - 1, head_cy - 1, self.palette.eyes)
        canvas.set_pixel_solid(head_cx + 1, head_cy - 1, self.palette.eyes)
        canvas.set_pixel_solid(head_cx - 1, head_cy, self.palette.eyes)
        canvas.set_pixel_solid(head_cx + 1, head_cy, self.palette.eyes)

        # Legs (8 legs, 4 on each side)
        leg_positions = [
            (-2, -1), (-3, 0), (-3, 1), (-2, 2),
            (2, -1), (3, 0), (3, 1), (2, 2)
        ]

        for lx, ly in leg_positions:
            start_x = cx + (1 if lx > 0 else -1)
            start_y = cy + ly

            # Draw leg segments
            for i in range(4):
                px = start_x + (i + 1) * (1 if lx > 0 else -1)
                py = start_y + (i if ly < 1 else -i // 2)

                if 0 <= px < self.width and 0 <= py < self.height:
                    canvas.set_pixel_solid(px, py, self.palette.body_dark)

        return canvas

    def _generate_fire_elemental(self, variant: str = None) -> Canvas:
        """Generate a fire elemental."""
        canvas = Canvas(self.width, self.height)
        self.palette = CreaturePalette.fire_elemental()

        cx = self.width // 2
        base_y = self.height - 3

        # Flame body - irregular, rising shape
        for y in range(self.height):
            # Width narrows toward top
            progress = y / self.height
            max_width = int((1 - progress * 0.7) * (self.width // 2))

            for x in range(self.width):
                dx = abs(x - cx)

                # Add randomness to edges
                edge_var = self.rng.random() * 2

                if dx < max_width - edge_var:
                    if dx < max_width // 2:
                        # Inner core - bright
                        canvas.set_pixel_solid(x, y, self.palette.body_light)
                    else:
                        canvas.set_pixel_solid(x, y, self.palette.body)
                elif dx < max_width:
                    canvas.set_pixel_solid(x, y, self.palette.body_dark)

        # Flame tips at top
        tips = [cx - 2, cx, cx + 2]
        for tip_x in tips:
            tip_height = self.rng.randint(2, 4)
            for i in range(tip_height):
                if 0 <= tip_x < self.width and i < self.height:
                    canvas.set_pixel_solid(tip_x, i, self.palette.body)

        # Eyes
        eye_y = self.height // 2
        canvas.set_pixel_solid(cx - 2, eye_y, self.palette.eyes)
        canvas.set_pixel_solid(cx + 2, eye_y, self.palette.eyes)

        return canvas

    def _generate_ice_elemental(self, variant: str = None) -> Canvas:
        """Generate an ice elemental."""
        canvas = Canvas(self.width, self.height)
        self.palette = CreaturePalette.ice_elemental()

        cx = self.width // 2
        cy = self.height // 2

        # Crystal body - geometric shapes
        # Main body crystal
        points = [
            (cx, 2),  # Top
            (cx + 5, cy),  # Right
            (cx, self.height - 2),  # Bottom
            (cx - 5, cy),  # Left
        ]

        # Fill crystal shape
        for y in range(self.height):
            for x in range(self.width):
                # Check if inside diamond shape
                dx = abs(x - cx)
                dy = abs(y - cy)
                max_x = 5 * (1 - dy / (self.height // 2))

                if dx <= max_x and dy <= self.height // 2:
                    if dx < max_x - 1:
                        canvas.set_pixel_solid(x, y, self.palette.body)
                    else:
                        canvas.set_pixel_solid(x, y, self.palette.body_light)

        # Crystal facets (lighter lines)
        for i in range(cy - 2, cy + 3):
            canvas.set_pixel_solid(cx, i, self.palette.body_light)

        # Eyes
        eye_y = cy - 1
        canvas.set_pixel_solid(cx - 2, eye_y, self.palette.eyes)
        canvas.set_pixel_solid(cx + 2, eye_y, self.palette.eyes)

        return canvas

    def _generate_beast(self, variant: str = None) -> Canvas:
        """Generate a beast creature."""
        if variant == 'wolf':
            return self._generate_wolf(variant)
        elif variant == 'bat':
            return self._generate_bat(variant)
        else:
            return self._generate_wolf(variant)

    def _generate_undead(self, variant: str = None) -> Canvas:
        """Generate an undead creature."""
        if variant == 'skeleton':
            return self._generate_skeleton(variant)
        elif variant == 'zombie':
            return self._generate_zombie(variant)
        elif variant == 'ghost':
            return self._generate_ghost(variant)
        else:
            return self._generate_skeleton(variant)

    def _generate_elemental(self, variant: str = None) -> Canvas:
        """Generate an elemental creature."""
        if variant == 'fire':
            return self._generate_fire_elemental(variant)
        elif variant == 'ice':
            return self._generate_ice_elemental(variant)
        else:
            return self._generate_fire_elemental(variant)

    def _generate_insect(self, variant: str = None) -> Canvas:
        """Generate an insect creature."""
        if variant == 'spider':
            return self._generate_spider(variant)
        else:
            return self._generate_spider(variant)


# Convenience functions
def generate_creature(creature_type: str, variant: str = None,
                      width: int = 16, height: int = 16, seed: int = 42,
                      hd_mode: bool = False, style: Optional['Style'] = None) -> Canvas:
    """Generate a creature of the specified type.

    Args:
        creature_type: Type of creature
        variant: Optional variant
        width: Canvas width
        height: Canvas height
        seed: Random seed
        hd_mode: Enable HD quality features (selout, AA)
        style: Style configuration for quality settings

    Returns:
        Canvas with generated creature
    """
    gen = CreatureGenerator(width, height, seed, style=style, hd_mode=hd_mode)
    return gen.generate(creature_type, variant)


def list_creature_types() -> List[str]:
    """List all available creature types."""
    return [
        'slime', 'ghost', 'skeleton', 'zombie', 'wolf', 'bat',
        'spider', 'fire_elemental', 'ice_elemental'
    ]


def list_slime_variants() -> List[str]:
    """List all slime variants."""
    return ['basic', 'green', 'blue', 'red', 'purple', 'fire', 'ice', 'poison', 'metal']


# Creature generators registry
CREATURE_GENERATORS: Dict[str, Callable] = {
    'slime': lambda g, v: g._generate_slime(v),
    'ghost': lambda g, v: g._generate_ghost(v),
    'skeleton': lambda g, v: g._generate_skeleton(v),
    'zombie': lambda g, v: g._generate_zombie(v),
    'wolf': lambda g, v: g._generate_wolf(v),
    'bat': lambda g, v: g._generate_bat(v),
    'spider': lambda g, v: g._generate_spider(v),
    'fire_elemental': lambda g, v: g._generate_fire_elemental(v),
    'ice_elemental': lambda g, v: g._generate_ice_elemental(v),
}

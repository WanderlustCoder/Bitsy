"""
Icons - Pixel art icon generator for UI elements.

Provides:
- Common UI icons (arrows, checkmarks, settings, etc.)
- Status icons (health, mana, buffs)
- Action icons (attack, defend, use)
- Navigation icons (menu, back, close)
"""

import sys
import os
import math
from typing import Tuple, Optional, List, Dict, Callable
from dataclasses import dataclass
from enum import Enum

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Canvas


class IconStyle(Enum):
    """Icon drawing styles."""
    SOLID = "solid"
    OUTLINE = "outline"
    FILLED = "filled"
    PIXEL = "pixel"


@dataclass
class IconPalette:
    """Color palette for icons."""
    primary: Tuple[int, int, int, int] = (255, 255, 255, 255)
    secondary: Tuple[int, int, int, int] = (200, 200, 200, 255)
    accent: Tuple[int, int, int, int] = (255, 200, 100, 255)
    shadow: Tuple[int, int, int, int] = (60, 60, 70, 255)
    background: Tuple[int, int, int, int] = (0, 0, 0, 0)

    @classmethod
    def default(cls) -> 'IconPalette':
        """Default white icons."""
        return cls()

    @classmethod
    def dark(cls) -> 'IconPalette':
        """Dark icons for light backgrounds."""
        return cls(
            primary=(40, 40, 50, 255),
            secondary=(80, 80, 90, 255),
            accent=(100, 150, 200, 255),
            shadow=(20, 20, 25, 255),
        )

    @classmethod
    def gold(cls) -> 'IconPalette':
        """Gold/bronze icons."""
        return cls(
            primary=(255, 200, 100, 255),
            secondary=(200, 150, 60, 255),
            accent=(255, 240, 180, 255),
            shadow=(120, 80, 30, 255),
        )

    @classmethod
    def green(cls) -> 'IconPalette':
        """Green/nature icons."""
        return cls(
            primary=(100, 200, 100, 255),
            secondary=(60, 150, 60, 255),
            accent=(180, 255, 180, 255),
            shadow=(30, 80, 30, 255),
        )

    @classmethod
    def red(cls) -> 'IconPalette':
        """Red/danger icons."""
        return cls(
            primary=(220, 80, 80, 255),
            secondary=(180, 50, 50, 255),
            accent=(255, 150, 150, 255),
            shadow=(100, 30, 30, 255),
        )

    @classmethod
    def blue(cls) -> 'IconPalette':
        """Blue/magic icons."""
        return cls(
            primary=(80, 140, 220, 255),
            secondary=(50, 100, 180, 255),
            accent=(150, 200, 255, 255),
            shadow=(30, 60, 100, 255),
        )


class IconGenerator:
    """Generates pixel art icons for UI."""

    def __init__(self, size: int = 16,
                 palette: Optional[IconPalette] = None,
                 style: IconStyle = IconStyle.SOLID):
        """Initialize icon generator.

        Args:
            size: Icon size (width and height)
            palette: Color palette
            style: Drawing style
        """
        self.size = size
        self.palette = palette or IconPalette.default()
        self.style = style

    def _create_canvas(self) -> Canvas:
        """Create a blank canvas for icon."""
        return Canvas(self.size, self.size, self.palette.background)

    # ========== Arrow Icons ==========

    def arrow_right(self) -> Canvas:
        """Generate right arrow icon."""
        canvas = self._create_canvas()
        s = self.size
        cx, cy = s // 2, s // 2

        # Draw arrow pointing right
        for i in range(s // 3):
            y1 = cy - i
            y2 = cy + i
            x = cx + i
            if 0 <= x < s:
                if 0 <= y1 < s:
                    canvas.set_pixel(x, y1, self.palette.primary)
                if 0 <= y2 < s and y2 != y1:
                    canvas.set_pixel(x, y2, self.palette.primary)

        # Arrow shaft
        shaft_len = s // 3
        for x in range(cx - shaft_len, cx):
            canvas.set_pixel(x, cy, self.palette.primary)

        return canvas

    def arrow_left(self) -> Canvas:
        """Generate left arrow icon."""
        return self.arrow_right().flip_horizontal()

    def arrow_up(self) -> Canvas:
        """Generate up arrow icon."""
        canvas = self._create_canvas()
        s = self.size
        cx, cy = s // 2, s // 2

        # Draw arrow pointing up
        for i in range(s // 3):
            x1 = cx - i
            x2 = cx + i
            y = cy - i
            if 0 <= y < s:
                if 0 <= x1 < s:
                    canvas.set_pixel(x1, y, self.palette.primary)
                if 0 <= x2 < s and x2 != x1:
                    canvas.set_pixel(x2, y, self.palette.primary)

        # Arrow shaft
        shaft_len = s // 3
        for y in range(cy, cy + shaft_len):
            if y < s:
                canvas.set_pixel(cx, y, self.palette.primary)

        return canvas

    def arrow_down(self) -> Canvas:
        """Generate down arrow icon."""
        return self.arrow_up().flip_vertical()

    # ========== Common UI Icons ==========

    def checkmark(self) -> Canvas:
        """Generate checkmark icon."""
        canvas = self._create_canvas()
        s = self.size

        # Draw checkmark shape
        points = [
            (s // 4, s // 2),
            (s // 2 - 1, s * 3 // 4 - 1),
            (s * 3 // 4, s // 4),
        ]

        # Draw first leg
        self._draw_line(canvas, points[0][0], points[0][1],
                        points[1][0], points[1][1], self.palette.primary)
        # Draw second leg
        self._draw_line(canvas, points[1][0], points[1][1],
                        points[2][0], points[2][1], self.palette.primary)

        return canvas

    def cross(self) -> Canvas:
        """Generate X/cross icon."""
        canvas = self._create_canvas()
        s = self.size
        margin = s // 4

        # Draw X shape
        self._draw_line(canvas, margin, margin,
                        s - margin - 1, s - margin - 1, self.palette.primary)
        self._draw_line(canvas, s - margin - 1, margin,
                        margin, s - margin - 1, self.palette.primary)

        return canvas

    def plus(self) -> Canvas:
        """Generate plus/add icon."""
        canvas = self._create_canvas()
        s = self.size
        cx, cy = s // 2, s // 2
        arm = s // 3

        # Vertical line
        for y in range(cy - arm, cy + arm + 1):
            if 0 <= y < s:
                canvas.set_pixel(cx, y, self.palette.primary)

        # Horizontal line
        for x in range(cx - arm, cx + arm + 1):
            if 0 <= x < s:
                canvas.set_pixel(x, cy, self.palette.primary)

        return canvas

    def minus(self) -> Canvas:
        """Generate minus/remove icon."""
        canvas = self._create_canvas()
        s = self.size
        cx, cy = s // 2, s // 2
        arm = s // 3

        # Horizontal line only
        for x in range(cx - arm, cx + arm + 1):
            if 0 <= x < s:
                canvas.set_pixel(x, cy, self.palette.primary)

        return canvas

    def gear(self) -> Canvas:
        """Generate settings gear icon."""
        canvas = self._create_canvas()
        s = self.size
        cx, cy = s // 2, s // 2
        outer_r = s // 2 - 2
        inner_r = s // 4

        # Draw gear teeth
        num_teeth = 8
        for i in range(num_teeth):
            angle = (i / num_teeth) * 2 * math.pi
            # Outer point
            ox = int(cx + math.cos(angle) * outer_r)
            oy = int(cy + math.sin(angle) * outer_r)
            # Inner point
            ix = int(cx + math.cos(angle) * (inner_r + 2))
            iy = int(cy + math.sin(angle) * (inner_r + 2))

            self._draw_line(canvas, ix, iy, ox, oy, self.palette.primary)

        # Center circle
        for y in range(s):
            for x in range(s):
                dx = x - cx
                dy = y - cy
                dist = (dx * dx + dy * dy) ** 0.5
                if inner_r - 1 <= dist <= inner_r + 1:
                    canvas.set_pixel(x, y, self.palette.primary)

        return canvas

    def menu(self) -> Canvas:
        """Generate hamburger menu icon."""
        canvas = self._create_canvas()
        s = self.size
        margin = s // 4
        spacing = (s - margin * 2) // 3

        # Three horizontal lines
        for i in range(3):
            y = margin + i * spacing + spacing // 2
            for x in range(margin, s - margin):
                canvas.set_pixel(x, y, self.palette.primary)

        return canvas

    def search(self) -> Canvas:
        """Generate search/magnifying glass icon."""
        canvas = self._create_canvas()
        s = self.size
        cx, cy = s // 3, s // 3
        radius = s // 4

        # Draw circle
        for angle in range(360):
            rad = math.radians(angle)
            x = int(cx + math.cos(rad) * radius)
            y = int(cy + math.sin(rad) * radius)
            if 0 <= x < s and 0 <= y < s:
                canvas.set_pixel(x, y, self.palette.primary)

        # Draw handle
        handle_start = (cx + radius, cy + radius)
        handle_end = (s - 2, s - 2)
        self._draw_line(canvas, handle_start[0], handle_start[1],
                        handle_end[0], handle_end[1], self.palette.primary)

        return canvas

    # ========== Status Icons ==========

    def heart(self, filled: bool = True) -> Canvas:
        """Generate heart icon (health)."""
        canvas = self._create_canvas()
        s = self.size
        color = self.palette.primary if filled else self.palette.secondary

        # Heart shape using pixel coordinates
        cx, cy = s // 2, s // 2

        for y in range(s):
            for x in range(s):
                # Normalized coordinates
                nx = (x - cx) / (s / 2)
                ny = (y - cy) / (s / 2)

                # Heart equation approximation
                heart_val = (nx * nx + ny * ny - 1) ** 3 - nx * nx * ny * ny * ny

                if filled:
                    if heart_val < 0 and ny > -0.6:
                        canvas.set_pixel(x, y, color)
                else:
                    if abs(heart_val) < 0.3 and ny > -0.6:
                        canvas.set_pixel(x, y, color)

        return canvas

    def star(self, filled: bool = True) -> Canvas:
        """Generate star icon."""
        canvas = self._create_canvas()
        s = self.size
        cx, cy = s // 2, s // 2
        outer_r = s // 2 - 1
        inner_r = s // 4

        color = self.palette.primary if filled else self.palette.secondary

        # Generate star points
        points = []
        for i in range(10):
            angle = math.radians(i * 36 - 90)
            r = outer_r if i % 2 == 0 else inner_r
            px = int(cx + math.cos(angle) * r)
            py = int(cy + math.sin(angle) * r)
            points.append((px, py))

        if filled:
            # Fill star
            self._fill_polygon(canvas, points, color)
        else:
            # Draw outline
            for i in range(len(points)):
                p1 = points[i]
                p2 = points[(i + 1) % len(points)]
                self._draw_line(canvas, p1[0], p1[1], p2[0], p2[1], color)

        return canvas

    def shield(self) -> Canvas:
        """Generate shield icon (defense)."""
        canvas = self._create_canvas()
        s = self.size
        cx = s // 2

        # Shield shape
        top = 2
        bottom = s - 2
        width = s - 4

        for y in range(top, bottom):
            # Calculate width at this height
            progress = (y - top) / (bottom - top)
            if progress < 0.6:
                w = width // 2
            else:
                # Taper to point
                taper = (progress - 0.6) / 0.4
                w = int((width // 2) * (1 - taper))

            for x in range(cx - w, cx + w + 1):
                if 0 <= x < s:
                    # Border or fill
                    if x == cx - w or x == cx + w or y == top:
                        canvas.set_pixel(x, y, self.palette.primary)
                    else:
                        canvas.set_pixel(x, y, self.palette.secondary)

        return canvas

    def lightning(self) -> Canvas:
        """Generate lightning bolt icon (energy/mana)."""
        canvas = self._create_canvas()
        s = self.size

        # Lightning bolt shape
        points = [
            (s * 3 // 4, 1),
            (s // 3, s // 2 - 1),
            (s * 2 // 3, s // 2),
            (s // 4, s - 2),
            (s // 2 + 1, s // 2 + 1),
            (s // 3 - 1, s // 2),
        ]

        # Draw lightning bolt
        for i in range(len(points) - 1):
            self._draw_line(canvas, points[i][0], points[i][1],
                           points[i + 1][0], points[i + 1][1], self.palette.primary)

        return canvas

    # ========== Action Icons ==========

    def sword(self) -> Canvas:
        """Generate sword icon (attack)."""
        canvas = self._create_canvas()
        s = self.size

        # Blade
        self._draw_line(canvas, s - 3, 2, s // 3, s * 2 // 3, self.palette.primary)
        self._draw_line(canvas, s - 4, 3, s // 3 - 1, s * 2 // 3, self.palette.secondary)

        # Guard
        guard_y = s * 2 // 3
        for x in range(s // 4, s // 2 + 2):
            canvas.set_pixel(x, guard_y, self.palette.primary)

        # Handle
        self._draw_line(canvas, s // 3, s * 2 // 3 + 1, s // 5, s - 2, self.palette.accent)

        return canvas

    def potion(self) -> Canvas:
        """Generate potion icon (use item)."""
        canvas = self._create_canvas()
        s = self.size
        cx = s // 2

        # Bottle neck
        neck_top = 2
        neck_bottom = s // 3
        neck_width = s // 6

        for y in range(neck_top, neck_bottom):
            for x in range(cx - neck_width, cx + neck_width + 1):
                if x == cx - neck_width or x == cx + neck_width:
                    canvas.set_pixel(x, y, self.palette.primary)
                elif y == neck_top:
                    canvas.set_pixel(x, y, self.palette.primary)

        # Bottle body
        body_top = neck_bottom
        body_bottom = s - 2
        body_width = s // 3

        for y in range(body_top, body_bottom):
            # Expand from neck to body
            if y < body_top + 2:
                w = neck_width + (y - body_top)
            else:
                w = body_width

            for x in range(cx - w, cx + w + 1):
                if x == cx - w or x == cx + w or y == body_bottom - 1:
                    canvas.set_pixel(x, y, self.palette.primary)
                elif y > body_top + 3:
                    # Liquid
                    canvas.set_pixel(x, y, self.palette.accent)

        return canvas

    def coin(self) -> Canvas:
        """Generate coin icon (currency)."""
        canvas = self._create_canvas()
        s = self.size
        cx, cy = s // 2, s // 2
        radius = s // 2 - 2

        # Draw circular coin
        for y in range(s):
            for x in range(s):
                dx = x - cx
                dy = y - cy
                dist = (dx * dx + dy * dy) ** 0.5

                if dist <= radius:
                    if dist >= radius - 1:
                        canvas.set_pixel(x, y, self.palette.shadow)
                    elif dist >= radius - 2:
                        canvas.set_pixel(x, y, self.palette.primary)
                    else:
                        canvas.set_pixel(x, y, self.palette.accent)

        # Add symbol in center
        canvas.set_pixel(cx, cy, self.palette.primary)
        canvas.set_pixel(cx, cy - 1, self.palette.primary)
        canvas.set_pixel(cx, cy + 1, self.palette.primary)

        return canvas

    # ========== Navigation Icons ==========

    def home(self) -> Canvas:
        """Generate home icon."""
        canvas = self._create_canvas()
        s = self.size
        cx = s // 2

        # Roof
        roof_top = 2
        roof_bottom = s // 2
        for y in range(roof_top, roof_bottom):
            offset = y - roof_top
            x1 = cx - offset - 1
            x2 = cx + offset
            if 0 <= x1 < s:
                canvas.set_pixel(x1, y, self.palette.primary)
            if 0 <= x2 < s:
                canvas.set_pixel(x2, y, self.palette.primary)

        # House body
        body_top = roof_bottom - 1
        body_bottom = s - 2
        body_width = s // 3

        for y in range(body_top, body_bottom):
            for x in range(cx - body_width, cx + body_width + 1):
                if x == cx - body_width or x == cx + body_width:
                    canvas.set_pixel(x, y, self.palette.primary)
                elif y == body_bottom - 1:
                    canvas.set_pixel(x, y, self.palette.primary)

        # Door
        door_width = s // 6
        for y in range(body_bottom - 3, body_bottom):
            for x in range(cx - door_width, cx + door_width + 1):
                canvas.set_pixel(x, y, self.palette.secondary)

        return canvas

    def back(self) -> Canvas:
        """Generate back arrow icon."""
        return self.arrow_left()

    def forward(self) -> Canvas:
        """Generate forward arrow icon."""
        return self.arrow_right()

    def close(self) -> Canvas:
        """Generate close/X icon."""
        return self.cross()

    def refresh(self) -> Canvas:
        """Generate refresh/reload icon."""
        canvas = self._create_canvas()
        s = self.size
        cx, cy = s // 2, s // 2
        radius = s // 3

        # Draw circular arrow
        for angle in range(45, 315):
            rad = math.radians(angle)
            x = int(cx + math.cos(rad) * radius)
            y = int(cy + math.sin(rad) * radius)
            if 0 <= x < s and 0 <= y < s:
                canvas.set_pixel(x, y, self.palette.primary)

        # Arrowhead at end
        end_angle = math.radians(315)
        ax = int(cx + math.cos(end_angle) * radius)
        ay = int(cy + math.sin(end_angle) * radius)

        # Simple arrowhead
        canvas.set_pixel(ax + 1, ay - 1, self.palette.primary)
        canvas.set_pixel(ax + 2, ay, self.palette.primary)
        canvas.set_pixel(ax + 1, ay + 1, self.palette.primary)

        return canvas

    # ========== Utility Methods ==========

    def _draw_line(self, canvas: Canvas, x1: int, y1: int,
                   x2: int, y2: int, color: Tuple[int, int, int, int]) -> None:
        """Draw a line between two points."""
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        steps = max(dx, dy, 1)

        for i in range(steps + 1):
            t = i / steps if steps > 0 else 0
            x = int(x1 + (x2 - x1) * t)
            y = int(y1 + (y2 - y1) * t)
            if 0 <= x < canvas.width and 0 <= y < canvas.height:
                canvas.set_pixel(x, y, color)

    def _fill_polygon(self, canvas: Canvas, points: List[Tuple[int, int]],
                      color: Tuple[int, int, int, int]) -> None:
        """Fill a polygon using scanline algorithm."""
        if not points:
            return

        min_y = min(p[1] for p in points)
        max_y = max(p[1] for p in points)

        for y in range(min_y, max_y + 1):
            intersections = []

            for i in range(len(points)):
                p1 = points[i]
                p2 = points[(i + 1) % len(points)]

                if p1[1] == p2[1]:
                    continue

                if min(p1[1], p2[1]) <= y < max(p1[1], p2[1]):
                    x = p1[0] + (y - p1[1]) * (p2[0] - p1[0]) / (p2[1] - p1[1])
                    intersections.append(int(x))

            intersections.sort()

            for i in range(0, len(intersections) - 1, 2):
                for x in range(intersections[i], intersections[i + 1] + 1):
                    if 0 <= x < canvas.width and 0 <= y < canvas.height:
                        canvas.set_pixel(x, y, color)


# Icon registry for easy access
ICON_GENERATORS: Dict[str, Callable[[IconGenerator], Canvas]] = {
    # Arrows
    'arrow_right': lambda g: g.arrow_right(),
    'arrow_left': lambda g: g.arrow_left(),
    'arrow_up': lambda g: g.arrow_up(),
    'arrow_down': lambda g: g.arrow_down(),
    # Common UI
    'checkmark': lambda g: g.checkmark(),
    'check': lambda g: g.checkmark(),
    'cross': lambda g: g.cross(),
    'x': lambda g: g.cross(),
    'plus': lambda g: g.plus(),
    'add': lambda g: g.plus(),
    'minus': lambda g: g.minus(),
    'remove': lambda g: g.minus(),
    'gear': lambda g: g.gear(),
    'settings': lambda g: g.gear(),
    'menu': lambda g: g.menu(),
    'hamburger': lambda g: g.menu(),
    'search': lambda g: g.search(),
    # Status
    'heart': lambda g: g.heart(),
    'heart_empty': lambda g: g.heart(filled=False),
    'star': lambda g: g.star(),
    'star_empty': lambda g: g.star(filled=False),
    'shield': lambda g: g.shield(),
    'lightning': lambda g: g.lightning(),
    'energy': lambda g: g.lightning(),
    # Actions
    'sword': lambda g: g.sword(),
    'attack': lambda g: g.sword(),
    'potion': lambda g: g.potion(),
    'use': lambda g: g.potion(),
    'coin': lambda g: g.coin(),
    'gold': lambda g: g.coin(),
    # Navigation
    'home': lambda g: g.home(),
    'back': lambda g: g.back(),
    'forward': lambda g: g.forward(),
    'close': lambda g: g.close(),
    'refresh': lambda g: g.refresh(),
    'reload': lambda g: g.refresh(),
}


def create_icon(name: str, size: int = 16,
                palette: Optional[IconPalette] = None,
                style: IconStyle = IconStyle.SOLID) -> Canvas:
    """Create an icon by name.

    Args:
        name: Icon name (see list_icons())
        size: Icon size
        palette: Color palette
        style: Drawing style

    Returns:
        Canvas with generated icon
    """
    generator = IconGenerator(size, palette, style)

    if name not in ICON_GENERATORS:
        raise ValueError(f"Unknown icon: {name}. Available: {list_icons()}")

    return ICON_GENERATORS[name](generator)


def list_icons() -> List[str]:
    """List all available icon names."""
    return sorted(set(ICON_GENERATORS.keys()))


def create_icon_sheet(icons: Optional[List[str]] = None,
                      size: int = 16,
                      palette: Optional[IconPalette] = None,
                      columns: int = 8) -> Canvas:
    """Create a sprite sheet of multiple icons.

    Args:
        icons: List of icon names (None for all)
        size: Icon size
        palette: Color palette
        columns: Number of columns in sheet

    Returns:
        Canvas with icon sprite sheet
    """
    if icons is None:
        # Get unique icons (remove aliases)
        unique_icons = ['arrow_right', 'arrow_left', 'arrow_up', 'arrow_down',
                        'checkmark', 'cross', 'plus', 'minus', 'gear', 'menu',
                        'search', 'heart', 'star', 'shield', 'lightning',
                        'sword', 'potion', 'coin', 'home', 'back', 'close', 'refresh']
        icons = unique_icons

    rows = (len(icons) + columns - 1) // columns
    width = columns * size
    height = rows * size

    canvas = Canvas(width, height, (0, 0, 0, 0))
    generator = IconGenerator(size, palette)

    for idx, icon_name in enumerate(icons):
        col = idx % columns
        row = idx // columns
        x = col * size
        y = row * size

        if icon_name in ICON_GENERATORS:
            icon = ICON_GENERATORS[icon_name](generator)
            canvas.blit(icon, x, y)

    return canvas

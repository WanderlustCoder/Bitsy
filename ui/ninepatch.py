"""
NinePatch - 9-slice scaling for UI panels and frames.

Provides:
- NinePatch class for scalable UI elements
- Panel presets (fantasy, modern, retro)
- Border and decoration generators
"""

import sys
import os
from typing import Tuple, Optional, List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Canvas


class BorderStyle(Enum):
    """Border drawing styles."""
    SOLID = "solid"
    DOUBLE = "double"
    DASHED = "dashed"
    DOTTED = "dotted"
    GROOVE = "groove"
    RIDGE = "ridge"
    ORNATE = "ornate"


@dataclass
class NinePatchConfig:
    """Configuration for a 9-patch panel.

    Attributes:
        corner_size: Size of corner regions in pixels
        edge_size: Size of edge regions (if different from corner)
        border_color: Main border color
        fill_color: Interior fill color
        highlight_color: Highlight/bevel color
        shadow_color: Shadow/bevel color
        border_width: Border thickness
        border_style: Style of border
        corner_style: How corners are drawn
        has_bevel: Whether to add 3D bevel effect
        has_shadow: Whether to add drop shadow
        shadow_offset: Shadow offset (x, y)
    """
    corner_size: int = 8
    edge_size: Optional[int] = None
    border_color: Tuple[int, int, int, int] = (60, 50, 40, 255)
    fill_color: Tuple[int, int, int, int] = (180, 160, 140, 255)
    highlight_color: Tuple[int, int, int, int] = (220, 200, 180, 255)
    shadow_color: Tuple[int, int, int, int] = (100, 80, 60, 255)
    border_width: int = 2
    border_style: BorderStyle = BorderStyle.SOLID
    corner_style: str = "square"  # square, rounded, cut, ornate
    has_bevel: bool = True
    has_shadow: bool = False
    shadow_offset: Tuple[int, int] = (2, 2)


class NinePatch:
    """9-slice scalable panel generator.

    Divides a panel into 9 regions:
    - 4 corners (fixed size)
    - 4 edges (stretch in one direction)
    - 1 center (stretches both directions)

    This allows panels to scale to any size while maintaining
    crisp corners and edges.
    """

    def __init__(self, config: Optional[NinePatchConfig] = None, seed: int = 42):
        """Initialize 9-patch generator.

        Args:
            config: Panel configuration
            seed: Random seed for decorations
        """
        self.config = config or NinePatchConfig()
        self.seed = seed

        import random
        self.rng = random.Random(seed)

        # Cache for generated patches
        self._corner_tl: Optional[Canvas] = None
        self._corner_tr: Optional[Canvas] = None
        self._corner_bl: Optional[Canvas] = None
        self._corner_br: Optional[Canvas] = None
        self._edge_t: Optional[Canvas] = None
        self._edge_b: Optional[Canvas] = None
        self._edge_l: Optional[Canvas] = None
        self._edge_r: Optional[Canvas] = None
        self._center: Optional[Canvas] = None

    def generate(self, width: int, height: int) -> Canvas:
        """Generate a panel of the specified size.

        Args:
            width: Panel width in pixels
            height: Panel height in pixels

        Returns:
            Canvas with the generated panel
        """
        cfg = self.config
        corner = cfg.corner_size
        edge = cfg.edge_size or corner

        # Ensure minimum size
        min_width = corner * 2 + 2
        min_height = corner * 2 + 2
        width = max(width, min_width)
        height = max(height, min_height)

        canvas = Canvas(width, height, (0, 0, 0, 0))

        # Draw drop shadow first if enabled
        if cfg.has_shadow:
            self._draw_shadow(canvas, width, height)

        # Generate patches if not cached
        self._generate_patches()

        # Draw center (stretched)
        center_width = width - corner * 2
        center_height = height - corner * 2
        if center_width > 0 and center_height > 0:
            self._tile_region(canvas, self._center,
                            corner, corner, center_width, center_height)

        # Draw edges
        if center_width > 0:
            # Top edge
            self._tile_region(canvas, self._edge_t,
                            corner, 0, center_width, edge)
            # Bottom edge
            self._tile_region(canvas, self._edge_b,
                            corner, height - edge, center_width, edge)

        if center_height > 0:
            # Left edge
            self._tile_region(canvas, self._edge_l,
                            0, corner, edge, center_height)
            # Right edge
            self._tile_region(canvas, self._edge_r,
                            width - edge, corner, edge, center_height)

        # Draw corners
        canvas.blit(self._corner_tl, 0, 0)
        canvas.blit(self._corner_tr, width - corner, 0)
        canvas.blit(self._corner_bl, 0, height - corner)
        canvas.blit(self._corner_br, width - corner, height - corner)

        return canvas

    def _generate_patches(self) -> None:
        """Generate all 9 patch regions."""
        cfg = self.config
        corner = cfg.corner_size
        edge = cfg.edge_size or corner

        # Generate based on corner style
        if cfg.corner_style == "rounded":
            self._generate_rounded_patches()
        elif cfg.corner_style == "cut":
            self._generate_cut_patches()
        elif cfg.corner_style == "ornate":
            self._generate_ornate_patches()
        else:  # square
            self._generate_square_patches()

    def _generate_square_patches(self) -> None:
        """Generate square-cornered patches."""
        cfg = self.config
        corner = cfg.corner_size
        edge = cfg.edge_size or corner
        bw = cfg.border_width

        # Corner patches
        self._corner_tl = Canvas(corner, corner, (0, 0, 0, 0))
        self._corner_tr = Canvas(corner, corner, (0, 0, 0, 0))
        self._corner_bl = Canvas(corner, corner, (0, 0, 0, 0))
        self._corner_br = Canvas(corner, corner, (0, 0, 0, 0))

        # Fill corners
        for c in [self._corner_tl, self._corner_tr, self._corner_bl, self._corner_br]:
            c.fill_rect(0, 0, corner, corner, cfg.fill_color)

        # Draw borders on corners
        self._draw_corner_border(self._corner_tl, "tl")
        self._draw_corner_border(self._corner_tr, "tr")
        self._draw_corner_border(self._corner_bl, "bl")
        self._draw_corner_border(self._corner_br, "br")

        # Edge patches (1 pixel wide, will be tiled)
        self._edge_t = Canvas(1, edge, (0, 0, 0, 0))
        self._edge_b = Canvas(1, edge, (0, 0, 0, 0))
        self._edge_l = Canvas(edge, 1, (0, 0, 0, 0))
        self._edge_r = Canvas(edge, 1, (0, 0, 0, 0))

        # Fill and border edges
        self._edge_t.fill_rect(0, 0, 1, edge, cfg.fill_color)
        self._edge_b.fill_rect(0, 0, 1, edge, cfg.fill_color)
        self._edge_l.fill_rect(0, 0, edge, 1, cfg.fill_color)
        self._edge_r.fill_rect(0, 0, edge, 1, cfg.fill_color)

        # Border on edges
        for y in range(bw):
            self._edge_t.set_pixel(0, y, cfg.border_color)
            self._edge_b.set_pixel(0, edge - 1 - y, cfg.border_color)
        for x in range(bw):
            self._edge_l.set_pixel(x, 0, cfg.border_color)
            self._edge_r.set_pixel(edge - 1 - x, 0, cfg.border_color)

        # Bevel on edges
        if cfg.has_bevel:
            if bw < edge:
                self._edge_t.set_pixel(0, bw, cfg.highlight_color)
                self._edge_l.set_pixel(bw, 0, cfg.highlight_color)
                if edge > bw + 1:
                    self._edge_b.set_pixel(0, edge - 1 - bw, cfg.shadow_color)
                    self._edge_r.set_pixel(edge - 1 - bw, 0, cfg.shadow_color)

        # Center patch (1x1, will be tiled)
        self._center = Canvas(1, 1, cfg.fill_color)

    def _generate_rounded_patches(self) -> None:
        """Generate rounded corner patches."""
        cfg = self.config
        corner = cfg.corner_size
        edge = cfg.edge_size or corner
        bw = cfg.border_width

        # Start with square patches
        self._generate_square_patches()

        # Round the corners by making outer pixels transparent
        radius = corner - bw

        for corner_canvas, is_right, is_bottom in [
            (self._corner_tl, False, False),
            (self._corner_tr, True, False),
            (self._corner_bl, False, True),
            (self._corner_br, True, True),
        ]:
            cx = corner - 1 if is_right else 0
            cy = corner - 1 if is_bottom else 0

            for y in range(corner):
                for x in range(corner):
                    # Calculate distance from corner
                    dx = x if not is_right else corner - 1 - x
                    dy = y if not is_bottom else corner - 1 - y

                    # Round corner effect
                    if dx + dy < bw + 1:
                        # Border region - check if outside rounded area
                        dist = (dx * dx + dy * dy) ** 0.5
                        if dist < bw * 0.7:
                            corner_canvas.set_pixel(x, y, (0, 0, 0, 0))

    def _generate_cut_patches(self) -> None:
        """Generate cut/chamfered corner patches."""
        cfg = self.config
        corner = cfg.corner_size
        edge = cfg.edge_size or corner
        bw = cfg.border_width
        cut_size = corner // 2

        # Start with square patches
        self._generate_square_patches()

        # Cut the corners diagonally
        for corner_canvas, is_right, is_bottom in [
            (self._corner_tl, False, False),
            (self._corner_tr, True, False),
            (self._corner_bl, False, True),
            (self._corner_br, True, True),
        ]:
            for y in range(corner):
                for x in range(corner):
                    dx = x if not is_right else corner - 1 - x
                    dy = y if not is_bottom else corner - 1 - y

                    # Cut corner
                    if dx + dy < cut_size:
                        corner_canvas.set_pixel(x, y, (0, 0, 0, 0))
                    elif dx + dy < cut_size + bw:
                        corner_canvas.set_pixel(x, y, cfg.border_color)

    def _generate_ornate_patches(self) -> None:
        """Generate ornate/decorated corner patches."""
        cfg = self.config
        corner = cfg.corner_size
        bw = cfg.border_width

        # Start with square patches
        self._generate_square_patches()

        # Add decorative elements to corners
        for corner_canvas, is_right, is_bottom in [
            (self._corner_tl, False, False),
            (self._corner_tr, True, False),
            (self._corner_bl, False, True),
            (self._corner_br, True, True),
        ]:
            # Add corner accent
            ax = corner - 3 if is_right else 2
            ay = corner - 3 if is_bottom else 2

            if corner >= 6:
                # Small decorative dot
                corner_canvas.set_pixel(ax, ay, cfg.highlight_color)
                if corner >= 8:
                    corner_canvas.set_pixel(ax + 1, ay, cfg.shadow_color)
                    corner_canvas.set_pixel(ax, ay + 1, cfg.shadow_color)

    def _draw_corner_border(self, canvas: Canvas, corner_type: str) -> None:
        """Draw border on a corner patch."""
        cfg = self.config
        corner = cfg.corner_size
        bw = cfg.border_width

        # Draw border lines
        for i in range(bw):
            if corner_type in ("tl", "tr"):
                # Top border
                for x in range(corner):
                    canvas.set_pixel(x, i, cfg.border_color)
            if corner_type in ("bl", "br"):
                # Bottom border
                for x in range(corner):
                    canvas.set_pixel(x, corner - 1 - i, cfg.border_color)
            if corner_type in ("tl", "bl"):
                # Left border
                for y in range(corner):
                    canvas.set_pixel(i, y, cfg.border_color)
            if corner_type in ("tr", "br"):
                # Right border
                for y in range(corner):
                    canvas.set_pixel(corner - 1 - i, y, cfg.border_color)

        # Add bevel effect
        if cfg.has_bevel and bw < corner - 1:
            if corner_type == "tl":
                # Highlight on inner top-left
                for x in range(bw, corner):
                    canvas.set_pixel(x, bw, cfg.highlight_color)
                for y in range(bw, corner):
                    canvas.set_pixel(bw, y, cfg.highlight_color)
            elif corner_type == "tr":
                for x in range(0, corner - bw):
                    canvas.set_pixel(x, bw, cfg.highlight_color)
                for y in range(bw, corner):
                    canvas.set_pixel(corner - 1 - bw, y, cfg.shadow_color)
            elif corner_type == "bl":
                for x in range(bw, corner):
                    canvas.set_pixel(x, corner - 1 - bw, cfg.shadow_color)
                for y in range(0, corner - bw):
                    canvas.set_pixel(bw, y, cfg.highlight_color)
            elif corner_type == "br":
                for x in range(0, corner - bw):
                    canvas.set_pixel(x, corner - 1 - bw, cfg.shadow_color)
                for y in range(0, corner - bw):
                    canvas.set_pixel(corner - 1 - bw, y, cfg.shadow_color)

    def _tile_region(self, canvas: Canvas, patch: Canvas,
                     x: int, y: int, width: int, height: int) -> None:
        """Tile a patch to fill a region."""
        pw = patch.width
        ph = patch.height

        for ty in range(0, height, ph):
            for tx in range(0, width, pw):
                # Calculate how much of the patch to copy
                copy_w = min(pw, width - tx)
                copy_h = min(ph, height - ty)

                for py in range(copy_h):
                    for px in range(copy_w):
                        color = patch.pixels[py][px]
                        if color[3] > 0:
                            canvas.set_pixel(x + tx + px, y + ty + py, color)

    def _draw_shadow(self, canvas: Canvas, width: int, height: int) -> None:
        """Draw drop shadow behind panel."""
        cfg = self.config
        ox, oy = cfg.shadow_offset
        shadow_color = (0, 0, 0, 80)

        # Draw shadow rectangle offset from panel
        for y in range(oy, height):
            for x in range(ox, width):
                canvas.set_pixel(x, y, shadow_color)


# Preset configurations
class PanelPresets:
    """Pre-configured panel styles."""

    @staticmethod
    def fantasy_wood() -> NinePatchConfig:
        """Fantasy-style wooden panel."""
        return NinePatchConfig(
            corner_size=10,
            border_color=(60, 40, 25, 255),
            fill_color=(140, 100, 60, 255),
            highlight_color=(180, 140, 90, 255),
            shadow_color=(80, 55, 30, 255),
            border_width=2,
            corner_style="ornate",
            has_bevel=True,
        )

    @staticmethod
    def fantasy_stone() -> NinePatchConfig:
        """Fantasy-style stone panel."""
        return NinePatchConfig(
            corner_size=10,
            border_color=(50, 50, 55, 255),
            fill_color=(120, 115, 110, 255),
            highlight_color=(160, 155, 150, 255),
            shadow_color=(70, 65, 60, 255),
            border_width=3,
            corner_style="cut",
            has_bevel=True,
        )

    @staticmethod
    def fantasy_gold() -> NinePatchConfig:
        """Ornate gold-trimmed panel."""
        return NinePatchConfig(
            corner_size=12,
            border_color=(180, 140, 40, 255),
            fill_color=(40, 35, 50, 255),
            highlight_color=(255, 220, 100, 255),
            shadow_color=(120, 90, 20, 255),
            border_width=2,
            corner_style="ornate",
            has_bevel=True,
        )

    @staticmethod
    def modern_dark() -> NinePatchConfig:
        """Modern dark UI panel."""
        return NinePatchConfig(
            corner_size=6,
            border_color=(80, 80, 90, 255),
            fill_color=(35, 35, 45, 255),
            highlight_color=(100, 100, 115, 255),
            shadow_color=(20, 20, 28, 255),
            border_width=1,
            corner_style="rounded",
            has_bevel=True,
        )

    @staticmethod
    def modern_light() -> NinePatchConfig:
        """Modern light UI panel."""
        return NinePatchConfig(
            corner_size=6,
            border_color=(180, 180, 190, 255),
            fill_color=(245, 245, 250, 255),
            highlight_color=(255, 255, 255, 255),
            shadow_color=(200, 200, 210, 255),
            border_width=1,
            corner_style="rounded",
            has_bevel=True,
        )

    @staticmethod
    def retro_blue() -> NinePatchConfig:
        """Retro RPG blue menu."""
        return NinePatchConfig(
            corner_size=8,
            border_color=(255, 255, 255, 255),
            fill_color=(0, 0, 170, 255),
            highlight_color=(100, 100, 255, 255),
            shadow_color=(0, 0, 100, 255),
            border_width=2,
            corner_style="rounded",
            has_bevel=True,
        )

    @staticmethod
    def retro_simple() -> NinePatchConfig:
        """Simple retro bordered panel."""
        return NinePatchConfig(
            corner_size=4,
            border_color=(0, 0, 0, 255),
            fill_color=(255, 255, 255, 255),
            highlight_color=(255, 255, 255, 255),
            shadow_color=(200, 200, 200, 255),
            border_width=1,
            corner_style="square",
            has_bevel=False,
        )

    @staticmethod
    def tooltip() -> NinePatchConfig:
        """Tooltip/hover panel."""
        return NinePatchConfig(
            corner_size=4,
            border_color=(60, 60, 70, 255),
            fill_color=(250, 250, 240, 255),
            highlight_color=(255, 255, 255, 255),
            shadow_color=(230, 230, 220, 255),
            border_width=1,
            corner_style="square",
            has_bevel=False,
            has_shadow=True,
            shadow_offset=(2, 2),
        )

    @staticmethod
    def dialog() -> NinePatchConfig:
        """Dialog/speech bubble."""
        return NinePatchConfig(
            corner_size=8,
            border_color=(40, 40, 50, 255),
            fill_color=(255, 255, 255, 255),
            highlight_color=(255, 255, 255, 255),
            shadow_color=(220, 220, 230, 255),
            border_width=2,
            corner_style="rounded",
            has_bevel=False,
        )


class FrameGenerator:
    """Generates decorative frames and borders."""

    def __init__(self, seed: int = 42):
        """Initialize frame generator."""
        self.seed = seed
        import random
        self.rng = random.Random(seed)

    def generate_frame(self, width: int, height: int,
                       border_width: int = 3,
                       outer_color: Tuple[int, int, int, int] = (60, 50, 40, 255),
                       inner_color: Tuple[int, int, int, int] = (100, 80, 60, 255),
                       highlight: Tuple[int, int, int, int] = (140, 120, 100, 255),
                       ) -> Canvas:
        """Generate a simple decorative frame.

        Args:
            width: Frame width
            height: Frame height
            border_width: Border thickness
            outer_color: Outer border color
            inner_color: Inner border color
            highlight: Highlight color

        Returns:
            Canvas with frame (transparent center)
        """
        canvas = Canvas(width, height, (0, 0, 0, 0))

        # Outer border
        for i in range(border_width):
            # Determine color based on depth
            if i == 0:
                color = outer_color
            elif i == border_width - 1:
                color = highlight
            else:
                color = inner_color

            # Top
            for x in range(width):
                canvas.set_pixel(x, i, color)
            # Bottom
            for x in range(width):
                canvas.set_pixel(x, height - 1 - i, color)
            # Left
            for y in range(height):
                canvas.set_pixel(i, y, color)
            # Right
            for y in range(height):
                canvas.set_pixel(width - 1 - i, y, color)

        return canvas

    def generate_ornate_frame(self, width: int, height: int,
                              style: str = "classic") -> Canvas:
        """Generate an ornate decorative frame.

        Args:
            width: Frame width
            height: Frame height
            style: Frame style (classic, gothic, elegant)

        Returns:
            Canvas with ornate frame
        """
        canvas = Canvas(width, height, (0, 0, 0, 0))

        if style == "classic":
            colors = {
                'outer': (80, 60, 40, 255),
                'mid': (140, 110, 70, 255),
                'inner': (180, 150, 100, 255),
                'accent': (220, 190, 130, 255),
            }
        elif style == "gothic":
            colors = {
                'outer': (30, 30, 35, 255),
                'mid': (60, 55, 65, 255),
                'inner': (90, 85, 100, 255),
                'accent': (140, 130, 160, 255),
            }
        else:  # elegant
            colors = {
                'outer': (180, 160, 140, 255),
                'mid': (220, 200, 180, 255),
                'inner': (245, 235, 225, 255),
                'accent': (255, 250, 245, 255),
            }

        border = 4

        # Draw multiple border layers
        for i in range(border):
            if i == 0:
                color = colors['outer']
            elif i == 1:
                color = colors['mid']
            elif i == 2:
                color = colors['inner']
            else:
                color = colors['accent']

            for x in range(i, width - i):
                canvas.set_pixel(x, i, color)
                canvas.set_pixel(x, height - 1 - i, color)
            for y in range(i, height - i):
                canvas.set_pixel(i, y, color)
                canvas.set_pixel(width - 1 - i, y, color)

        # Add corner decorations
        corner_size = min(8, width // 4, height // 4)
        self._draw_corner_decoration(canvas, 0, 0, corner_size, colors, "tl")
        self._draw_corner_decoration(canvas, width - corner_size, 0, corner_size, colors, "tr")
        self._draw_corner_decoration(canvas, 0, height - corner_size, corner_size, colors, "bl")
        self._draw_corner_decoration(canvas, width - corner_size, height - corner_size, corner_size, colors, "br")

        return canvas

    def _draw_corner_decoration(self, canvas: Canvas, x: int, y: int,
                                 size: int, colors: dict, corner: str) -> None:
        """Draw decorative element in corner."""
        if size < 4:
            return

        # Simple corner accent
        cx = x + size // 2
        cy = y + size // 2

        if corner == "tl":
            cx, cy = x + 2, y + 2
        elif corner == "tr":
            cx, cy = x + size - 3, y + 2
        elif corner == "bl":
            cx, cy = x + 2, y + size - 3
        else:
            cx, cy = x + size - 3, y + size - 3

        # Draw small decorative element
        if 0 <= cx < canvas.width and 0 <= cy < canvas.height:
            canvas.set_pixel(cx, cy, colors['accent'])
            if cx + 1 < canvas.width:
                canvas.set_pixel(cx + 1, cy, colors['mid'])
            if cy + 1 < canvas.height:
                canvas.set_pixel(cx, cy + 1, colors['mid'])


class ProgressBar:
    """Generates progress bar UI elements."""

    def __init__(self, width: int, height: int = 8,
                 bg_color: Tuple[int, int, int, int] = (40, 40, 50, 255),
                 fill_color: Tuple[int, int, int, int] = (80, 180, 80, 255),
                 border_color: Tuple[int, int, int, int] = (60, 60, 70, 255)):
        """Initialize progress bar.

        Args:
            width: Bar width
            height: Bar height
            bg_color: Background color
            fill_color: Fill/progress color
            border_color: Border color
        """
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.fill_color = fill_color
        self.border_color = border_color

    def render(self, progress: float) -> Canvas:
        """Render progress bar at given progress level.

        Args:
            progress: Progress value 0.0 to 1.0

        Returns:
            Canvas with progress bar
        """
        canvas = Canvas(self.width, self.height, self.bg_color)

        progress = max(0.0, min(1.0, progress))
        fill_width = int((self.width - 2) * progress)

        # Draw fill
        if fill_width > 0:
            # Main fill
            canvas.fill_rect(1, 1, fill_width, self.height - 2, self.fill_color)

            # Highlight on top
            highlight = (
                min(255, self.fill_color[0] + 40),
                min(255, self.fill_color[1] + 40),
                min(255, self.fill_color[2] + 40),
                255
            )
            canvas.fill_rect(1, 1, fill_width, 1, highlight)

            # Shadow on bottom
            shadow = (
                max(0, self.fill_color[0] - 30),
                max(0, self.fill_color[1] - 30),
                max(0, self.fill_color[2] - 30),
                255
            )
            canvas.fill_rect(1, self.height - 2, fill_width, 1, shadow)

        # Draw border
        for x in range(self.width):
            canvas.set_pixel(x, 0, self.border_color)
            canvas.set_pixel(x, self.height - 1, self.border_color)
        for y in range(self.height):
            canvas.set_pixel(0, y, self.border_color)
            canvas.set_pixel(self.width - 1, y, self.border_color)

        return canvas


class HealthBar(ProgressBar):
    """Specialized health bar with color transitions."""

    def __init__(self, width: int, height: int = 8):
        super().__init__(
            width, height,
            bg_color=(30, 10, 10, 255),
            fill_color=(220, 50, 50, 255),
            border_color=(60, 30, 30, 255)
        )
        self.high_color = (80, 200, 80, 255)
        self.mid_color = (220, 180, 50, 255)
        self.low_color = (220, 50, 50, 255)

    def render(self, progress: float) -> Canvas:
        """Render health bar with color based on health level."""
        # Determine color based on progress
        if progress > 0.6:
            self.fill_color = self.high_color
        elif progress > 0.3:
            self.fill_color = self.mid_color
        else:
            self.fill_color = self.low_color

        return super().render(progress)


class ManaBar(ProgressBar):
    """Specialized mana/magic bar."""

    def __init__(self, width: int, height: int = 8):
        super().__init__(
            width, height,
            bg_color=(10, 10, 30, 255),
            fill_color=(50, 100, 220, 255),
            border_color=(30, 30, 60, 255)
        )


# Convenience functions
def create_panel(width: int, height: int,
                 preset: str = "fantasy_wood",
                 seed: int = 42) -> Canvas:
    """Create a panel using a preset style.

    Args:
        width: Panel width
        height: Panel height
        preset: Preset name (fantasy_wood, modern_dark, retro_blue, etc.)
        seed: Random seed

    Returns:
        Canvas with generated panel
    """
    presets = {
        'fantasy_wood': PanelPresets.fantasy_wood,
        'fantasy_stone': PanelPresets.fantasy_stone,
        'fantasy_gold': PanelPresets.fantasy_gold,
        'modern_dark': PanelPresets.modern_dark,
        'modern_light': PanelPresets.modern_light,
        'retro_blue': PanelPresets.retro_blue,
        'retro_simple': PanelPresets.retro_simple,
        'tooltip': PanelPresets.tooltip,
        'dialog': PanelPresets.dialog,
    }

    config_fn = presets.get(preset, PanelPresets.fantasy_wood)
    config = config_fn()

    generator = NinePatch(config, seed)
    return generator.generate(width, height)


def list_panel_presets() -> List[str]:
    """List available panel preset names."""
    return [
        'fantasy_wood',
        'fantasy_stone',
        'fantasy_gold',
        'modern_dark',
        'modern_light',
        'retro_blue',
        'retro_simple',
        'tooltip',
        'dialog',
    ]

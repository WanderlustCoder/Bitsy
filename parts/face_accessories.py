"""
Face Accessories - Glasses, masks, and other face decorations.

Provides accessories worn on the face including:
- Glasses (various frame styles)
- Goggles
- Eye patches
- Face masks

These are rendered at eye level on the character's face.
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


@dataclass
class GlassesConfig(PartConfig):
    """Configuration for glasses."""
    frame_color: Optional[Color] = None  # Frame color (None = default dark)
    lens_color: Optional[Color] = None   # Lens tint color
    lens_opacity: int = 60               # Lens transparency (0-255)
    frame_thickness: int = 1             # Frame line thickness
    bridge_style: str = 'bar'            # 'bar', 'double', 'rimless'


class FaceAccessory(Equipment):
    """Base class for face-worn accessories."""

    def __init__(self, name: str, config: Optional[EquipmentConfig] = None):
        if config is None:
            config = EquipmentConfig()
        config.slot = EquipmentSlot.HEAD  # Use HEAD slot for face items
        config.layer = DrawLayer.FRONT    # Render in front of face
        super().__init__(name, config)


class Glasses(FaceAccessory):
    """Glasses with customizable frames and lens tint.

    Features:
    - Customizable frame color and thickness
    - Semi-transparent lens tint
    - Reflection highlights
    - Multiple frame styles
    """

    def __init__(self, config: Optional[GlassesConfig] = None):
        equip_config = EquipmentConfig(
            slot=EquipmentSlot.HEAD,
            layer=DrawLayer.FRONT
        )
        super().__init__("glasses", equip_config)

        self.glasses_config = config or GlassesConfig()

        # Default colors
        self.frame_color = self.glasses_config.frame_color or (45, 35, 30, 255)
        self.lens_color = self.glasses_config.lens_color or (200, 220, 240, self.glasses_config.lens_opacity)
        self.reflection_color = (255, 255, 255, 150)

    def draw(self, canvas: Canvas, x: int, y: int, width: int, height: int) -> None:
        """Draw glasses at the specified position.

        Args:
            x, y: Center position (at eye level)
            width, height: Face width/height for proportional sizing
        """
        hw, hh = width // 2, height // 2

        # Calculate lens dimensions based on face size
        lens_rx = max(3, int(hw * 0.30))  # Lens width radius
        lens_ry = max(2, int(hh * 0.20))  # Lens height radius
        lens_spacing = int(hw * 0.15)     # Space between lenses

        # Left lens position
        left_cx = x - lens_spacing - lens_rx // 2
        left_cy = y

        # Right lens position
        right_cx = x + lens_spacing + lens_rx // 2
        right_cy = y

        # Draw lenses (semi-transparent)
        self._draw_lens(canvas, left_cx, left_cy, lens_rx, lens_ry)
        self._draw_lens(canvas, right_cx, right_cy, lens_rx, lens_ry)

        # Draw frames
        self._draw_frame(canvas, left_cx, left_cy, lens_rx, lens_ry)
        self._draw_frame(canvas, right_cx, right_cy, lens_rx, lens_ry)

        # Draw bridge
        bridge_y = y
        self._draw_bridge(canvas, left_cx + lens_rx, bridge_y,
                         right_cx - lens_rx, bridge_y)

        # Draw arms (extending to sides)
        arm_y = y
        self._draw_arm(canvas, left_cx - lens_rx, arm_y, left_cx - lens_rx - hw // 3, arm_y)
        self._draw_arm(canvas, right_cx + lens_rx, arm_y, right_cx + lens_rx + hw // 3, arm_y)

    def _draw_lens(self, canvas: Canvas, cx: int, cy: int, rx: int, ry: int) -> None:
        """Draw a semi-transparent lens with reflection."""
        # Lens fill
        canvas.fill_ellipse(cx, cy, rx, ry, self.lens_color)

        # Reflection highlight (top-left area)
        ref_rx = max(1, rx // 3)
        ref_ry = max(1, ry // 3)
        ref_x = cx - rx // 3
        ref_y = cy - ry // 3
        canvas.fill_ellipse(ref_x, ref_y, ref_rx, ref_ry, self.reflection_color)

    def _draw_frame(self, canvas: Canvas, cx: int, cy: int, rx: int, ry: int) -> None:
        """Draw lens frame outline."""
        # Draw ellipse outline using pixel sampling
        steps = max(24, rx * 4)
        for i in range(steps):
            angle = 2 * math.pi * i / steps
            px = cx + int(rx * math.cos(angle))
            py = cy + int(ry * math.sin(angle))
            canvas.set_pixel(px, py, self.frame_color)

            # Thicker frame
            if self.glasses_config.frame_thickness > 1:
                canvas.set_pixel(px + 1, py, self.frame_color)
                canvas.set_pixel(px, py + 1, self.frame_color)

    def _draw_bridge(self, canvas: Canvas, x1: int, y1: int, x2: int, y2: int) -> None:
        """Draw the nose bridge connecting lenses."""
        if self.glasses_config.bridge_style == 'bar':
            canvas.draw_line(x1, y1, x2, y2, self.frame_color)
        elif self.glasses_config.bridge_style == 'double':
            canvas.draw_line(x1, y1 - 1, x2, y2 - 1, self.frame_color)
            canvas.draw_line(x1, y1 + 1, x2, y2 + 1, self.frame_color)
        # 'rimless' has no bridge

    def _draw_arm(self, canvas: Canvas, x1: int, y1: int, x2: int, y2: int) -> None:
        """Draw a glasses arm (temple)."""
        canvas.draw_line(x1, y1, x2, y2, self.frame_color)


class RoundGlasses(Glasses):
    """Round-framed glasses."""

    def __init__(self, config: Optional[GlassesConfig] = None):
        super().__init__(config)
        self.name = "round_glasses"


class SquareGlasses(Glasses):
    """Square-framed glasses."""

    def __init__(self, config: Optional[GlassesConfig] = None):
        super().__init__(config)
        self.name = "square_glasses"

    def _draw_lens(self, canvas: Canvas, cx: int, cy: int, rx: int, ry: int) -> None:
        """Draw a square lens."""
        # Convert to rectangle coordinates
        x = cx - rx
        y = cy - ry
        w = rx * 2
        h = ry * 2
        canvas.fill_rect(x, y, w, h, self.lens_color)

        # Reflection
        ref_w = max(1, w // 3)
        ref_h = max(1, h // 3)
        canvas.fill_rect(x + 1, y + 1, ref_w, ref_h, self.reflection_color)

    def _draw_frame(self, canvas: Canvas, cx: int, cy: int, rx: int, ry: int) -> None:
        """Draw square frame outline."""
        x = cx - rx
        y = cy - ry
        w = rx * 2
        h = ry * 2
        canvas.draw_rect(x, y, w, h, self.frame_color)


class Goggles(FaceAccessory):
    """Goggles covering both eyes with a single lens."""

    def __init__(self, config: Optional[GlassesConfig] = None):
        equip_config = EquipmentConfig(
            slot=EquipmentSlot.HEAD,
            layer=DrawLayer.FRONT
        )
        super().__init__("goggles", equip_config)

        glasses_config = config or GlassesConfig()
        self.frame_color = glasses_config.frame_color or (60, 50, 45, 255)
        self.lens_color = glasses_config.lens_color or (180, 200, 220, 100)
        self.strap_color = (40, 35, 30, 255)

    def draw(self, canvas: Canvas, x: int, y: int, width: int, height: int) -> None:
        hw, hh = width // 2, height // 2

        # Single wide lens
        lens_rx = int(hw * 0.7)
        lens_ry = int(hh * 0.25)

        # Draw strap behind
        canvas.draw_line(x - lens_rx - 5, y, x - lens_rx, y, self.strap_color)
        canvas.draw_line(x + lens_rx + 5, y, x + lens_rx, y, self.strap_color)

        # Draw lens
        canvas.fill_ellipse(x, y, lens_rx, lens_ry, self.lens_color)

        # Frame
        steps = 36
        for i in range(steps):
            angle = 2 * math.pi * i / steps
            px = x + int(lens_rx * math.cos(angle))
            py = y + int(lens_ry * math.sin(angle))
            canvas.set_pixel(px, py, self.frame_color)

        # Divider line in middle
        canvas.draw_line(x, y - lens_ry + 1, x, y + lens_ry - 1, self.frame_color)

        # Reflections
        ref_color = (255, 255, 255, 120)
        canvas.fill_ellipse(x - lens_rx // 3, y - lens_ry // 3,
                           lens_rx // 4, lens_ry // 3, ref_color)


class EyePatch(FaceAccessory):
    """Eye patch covering one eye."""

    def __init__(self, side: str = 'left', config: Optional[PartConfig] = None):
        equip_config = EquipmentConfig(
            slot=EquipmentSlot.HEAD,
            layer=DrawLayer.FRONT
        )
        super().__init__("eye_patch", equip_config)
        self.side = side  # 'left' or 'right'
        self.patch_color = (30, 25, 20, 255)
        self.strap_color = (50, 40, 35, 255)

    def draw(self, canvas: Canvas, x: int, y: int, width: int, height: int) -> None:
        hw, hh = width // 2, height // 2

        # Patch position based on side
        if self.side == 'left':
            patch_x = x - int(hw * 0.3)
        else:
            patch_x = x + int(hw * 0.3)

        patch_rx = max(3, int(hw * 0.25))
        patch_ry = max(2, int(hh * 0.18))

        # Draw strap
        canvas.draw_line(x - hw, y - 2, x + hw, y - 2, self.strap_color)

        # Draw patch
        canvas.fill_ellipse(patch_x, y, patch_rx, patch_ry, self.patch_color)

        # Strap attachment points
        canvas.fill_circle(patch_x - patch_rx, y, 1, self.strap_color)
        canvas.fill_circle(patch_x + patch_rx, y, 1, self.strap_color)


# Registry of face accessories
FACE_ACCESSORY_TYPES = {
    'glasses': Glasses,
    'round_glasses': RoundGlasses,
    'square_glasses': SquareGlasses,
    'goggles': Goggles,
    'eye_patch': EyePatch,
}


def create_face_accessory(accessory_type: str,
                          config: Optional[GlassesConfig] = None) -> FaceAccessory:
    """Create a face accessory by type name.

    Args:
        accessory_type: Type name ('glasses', 'goggles', etc.)
        config: Optional configuration

    Returns:
        FaceAccessory instance
    """
    if accessory_type not in FACE_ACCESSORY_TYPES:
        available = ', '.join(FACE_ACCESSORY_TYPES.keys())
        raise ValueError(f"Unknown face accessory '{accessory_type}'. Available: {available}")

    return FACE_ACCESSORY_TYPES[accessory_type](config)


def list_face_accessory_types() -> List[str]:
    """List available face accessory types."""
    return list(FACE_ACCESSORY_TYPES.keys())

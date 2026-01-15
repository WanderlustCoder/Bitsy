"""
Layers - Layer management system for sprite editing.

Provides:
- Layer stack with ordering
- Multiple blend modes
- Layer effects (opacity, visibility)
- Grouping and merging
"""

import sys
import os
from typing import List, Optional, Tuple, Dict, Callable
from dataclasses import dataclass, field
from enum import Enum
from copy import deepcopy

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Canvas


class BlendMode(Enum):
    """Layer blend modes."""
    NORMAL = "normal"
    MULTIPLY = "multiply"
    SCREEN = "screen"
    OVERLAY = "overlay"
    DARKEN = "darken"
    LIGHTEN = "lighten"
    COLOR_DODGE = "color_dodge"
    COLOR_BURN = "color_burn"
    HARD_LIGHT = "hard_light"
    SOFT_LIGHT = "soft_light"
    DIFFERENCE = "difference"
    EXCLUSION = "exclusion"
    ADD = "add"
    SUBTRACT = "subtract"


def _clamp(value: int) -> int:
    """Clamp value to 0-255 range."""
    return max(0, min(255, value))


def _blend_normal(base: int, blend: int, alpha: float) -> int:
    """Normal blend mode."""
    return _clamp(int(base * (1 - alpha) + blend * alpha))


def _blend_multiply(base: int, blend: int, alpha: float) -> int:
    """Multiply blend mode."""
    result = (base * blend) // 255
    return _clamp(int(base * (1 - alpha) + result * alpha))


def _blend_screen(base: int, blend: int, alpha: float) -> int:
    """Screen blend mode."""
    result = 255 - ((255 - base) * (255 - blend)) // 255
    return _clamp(int(base * (1 - alpha) + result * alpha))


def _blend_overlay(base: int, blend: int, alpha: float) -> int:
    """Overlay blend mode."""
    if base < 128:
        result = (2 * base * blend) // 255
    else:
        result = 255 - (2 * (255 - base) * (255 - blend)) // 255
    return _clamp(int(base * (1 - alpha) + result * alpha))


def _blend_darken(base: int, blend: int, alpha: float) -> int:
    """Darken blend mode."""
    result = min(base, blend)
    return _clamp(int(base * (1 - alpha) + result * alpha))


def _blend_lighten(base: int, blend: int, alpha: float) -> int:
    """Lighten blend mode."""
    result = max(base, blend)
    return _clamp(int(base * (1 - alpha) + result * alpha))


def _blend_color_dodge(base: int, blend: int, alpha: float) -> int:
    """Color dodge blend mode."""
    if blend >= 255:
        result = 255
    else:
        result = min(255, (base * 255) // (255 - blend))
    return _clamp(int(base * (1 - alpha) + result * alpha))


def _blend_color_burn(base: int, blend: int, alpha: float) -> int:
    """Color burn blend mode."""
    if blend <= 0:
        result = 0
    else:
        result = max(0, 255 - ((255 - base) * 255) // blend)
    return _clamp(int(base * (1 - alpha) + result * alpha))


def _blend_hard_light(base: int, blend: int, alpha: float) -> int:
    """Hard light blend mode."""
    if blend < 128:
        result = (2 * base * blend) // 255
    else:
        result = 255 - (2 * (255 - base) * (255 - blend)) // 255
    return _clamp(int(base * (1 - alpha) + result * alpha))


def _blend_soft_light(base: int, blend: int, alpha: float) -> int:
    """Soft light blend mode."""
    if blend < 128:
        result = base - ((255 - 2 * blend) * base * (255 - base)) // (255 * 255)
    else:
        if base < 64:
            d = ((16 * base - 12 * 255) * base + 4 * 255) * base // (255 * 255)
        else:
            d = int((base ** 0.5) * 16) - 255  # Simplified sqrt
        result = base + (2 * blend - 255) * (d - base) // 255
    return _clamp(int(base * (1 - alpha) + result * alpha))


def _blend_difference(base: int, blend: int, alpha: float) -> int:
    """Difference blend mode."""
    result = abs(base - blend)
    return _clamp(int(base * (1 - alpha) + result * alpha))


def _blend_exclusion(base: int, blend: int, alpha: float) -> int:
    """Exclusion blend mode."""
    result = base + blend - (2 * base * blend) // 255
    return _clamp(int(base * (1 - alpha) + result * alpha))


def _blend_add(base: int, blend: int, alpha: float) -> int:
    """Additive blend mode."""
    result = min(255, base + blend)
    return _clamp(int(base * (1 - alpha) + result * alpha))


def _blend_subtract(base: int, blend: int, alpha: float) -> int:
    """Subtractive blend mode."""
    result = max(0, base - blend)
    return _clamp(int(base * (1 - alpha) + result * alpha))


# Blend function lookup
BLEND_FUNCTIONS: Dict[BlendMode, Callable[[int, int, float], int]] = {
    BlendMode.NORMAL: _blend_normal,
    BlendMode.MULTIPLY: _blend_multiply,
    BlendMode.SCREEN: _blend_screen,
    BlendMode.OVERLAY: _blend_overlay,
    BlendMode.DARKEN: _blend_darken,
    BlendMode.LIGHTEN: _blend_lighten,
    BlendMode.COLOR_DODGE: _blend_color_dodge,
    BlendMode.COLOR_BURN: _blend_color_burn,
    BlendMode.HARD_LIGHT: _blend_hard_light,
    BlendMode.SOFT_LIGHT: _blend_soft_light,
    BlendMode.DIFFERENCE: _blend_difference,
    BlendMode.EXCLUSION: _blend_exclusion,
    BlendMode.ADD: _blend_add,
    BlendMode.SUBTRACT: _blend_subtract,
}


@dataclass
class Layer:
    """A single layer in the layer stack.

    Attributes:
        name: Layer name
        canvas: Layer content
        visible: Whether layer is visible
        opacity: Layer opacity (0.0 to 1.0)
        blend_mode: How layer blends with layers below
        locked: Whether layer is locked for editing
        offset_x: X offset from canvas origin
        offset_y: Y offset from canvas origin
    """
    name: str
    canvas: Canvas
    visible: bool = True
    opacity: float = 1.0
    blend_mode: BlendMode = BlendMode.NORMAL
    locked: bool = False
    offset_x: int = 0
    offset_y: int = 0

    def copy(self) -> 'Layer':
        """Create a copy of this layer."""
        return Layer(
            name=self.name + " copy",
            canvas=self.canvas.copy(),
            visible=self.visible,
            opacity=self.opacity,
            blend_mode=self.blend_mode,
            locked=self.locked,
            offset_x=self.offset_x,
            offset_y=self.offset_y
        )


class LayerStack:
    """Stack of layers for image editing.

    Layers are ordered bottom-to-top (index 0 is bottom).
    """

    def __init__(self, width: int, height: int,
                 background: Optional[Tuple[int, int, int, int]] = None):
        """Initialize layer stack.

        Args:
            width: Canvas width
            height: Canvas height
            background: Optional background color
        """
        self.width = width
        self.height = height
        self.layers: List[Layer] = []
        self.background = background or (0, 0, 0, 0)

    def add_layer(self, name: str,
                  canvas: Optional[Canvas] = None,
                  index: Optional[int] = None) -> Layer:
        """Add a new layer.

        Args:
            name: Layer name
            canvas: Layer content (creates empty if None)
            index: Position to insert (top if None)

        Returns:
            The created layer
        """
        if canvas is None:
            canvas = Canvas(self.width, self.height, (0, 0, 0, 0))

        layer = Layer(name=name, canvas=canvas)

        if index is None:
            self.layers.append(layer)
        else:
            self.layers.insert(index, layer)

        return layer

    def remove_layer(self, name_or_index) -> Optional[Layer]:
        """Remove a layer.

        Args:
            name_or_index: Layer name or index

        Returns:
            Removed layer or None
        """
        index = self._resolve_index(name_or_index)
        if index is not None:
            return self.layers.pop(index)
        return None

    def get_layer(self, name_or_index) -> Optional[Layer]:
        """Get a layer by name or index.

        Args:
            name_or_index: Layer name or index

        Returns:
            Layer or None
        """
        index = self._resolve_index(name_or_index)
        if index is not None:
            return self.layers[index]
        return None

    def _resolve_index(self, name_or_index) -> Optional[int]:
        """Resolve layer name or index to index."""
        if isinstance(name_or_index, int):
            if 0 <= name_or_index < len(self.layers):
                return name_or_index
        elif isinstance(name_or_index, str):
            for i, layer in enumerate(self.layers):
                if layer.name == name_or_index:
                    return i
        return None

    def move_layer(self, name_or_index, new_index: int) -> bool:
        """Move a layer to a new position.

        Args:
            name_or_index: Layer to move
            new_index: New position

        Returns:
            True if successful
        """
        old_index = self._resolve_index(name_or_index)
        if old_index is None:
            return False

        layer = self.layers.pop(old_index)
        new_index = max(0, min(new_index, len(self.layers)))
        self.layers.insert(new_index, layer)
        return True

    def move_up(self, name_or_index) -> bool:
        """Move layer up one position."""
        index = self._resolve_index(name_or_index)
        if index is not None and index < len(self.layers) - 1:
            self.layers[index], self.layers[index + 1] = \
                self.layers[index + 1], self.layers[index]
            return True
        return False

    def move_down(self, name_or_index) -> bool:
        """Move layer down one position."""
        index = self._resolve_index(name_or_index)
        if index is not None and index > 0:
            self.layers[index], self.layers[index - 1] = \
                self.layers[index - 1], self.layers[index]
            return True
        return False

    def duplicate_layer(self, name_or_index) -> Optional[Layer]:
        """Duplicate a layer.

        Args:
            name_or_index: Layer to duplicate

        Returns:
            New layer or None
        """
        index = self._resolve_index(name_or_index)
        if index is None:
            return None

        original = self.layers[index]
        copy = original.copy()
        self.layers.insert(index + 1, copy)
        return copy

    def merge_down(self, name_or_index) -> bool:
        """Merge layer with the one below it.

        Args:
            name_or_index: Layer to merge down

        Returns:
            True if successful
        """
        index = self._resolve_index(name_or_index)
        if index is None or index == 0:
            return False

        top = self.layers[index]
        bottom = self.layers[index - 1]

        if bottom.locked:
            return False

        # Composite top onto bottom
        self._composite_layer(bottom.canvas, top)

        # Remove top layer
        self.layers.pop(index)
        return True

    def merge_visible(self) -> Layer:
        """Merge all visible layers into a new layer.

        Returns:
            New merged layer (added to top)
        """
        result = Canvas(self.width, self.height, self.background)

        for layer in self.layers:
            if layer.visible:
                self._composite_layer(result, layer)

        merged = self.add_layer("Merged", result)
        return merged

    def flatten(self) -> Canvas:
        """Flatten all visible layers into a single canvas.

        Returns:
            Flattened canvas
        """
        result = Canvas(self.width, self.height, self.background)

        for layer in self.layers:
            if layer.visible:
                self._composite_layer(result, layer)

        return result

    def _composite_layer(self, base: Canvas, layer: Layer) -> None:
        """Composite a layer onto a base canvas.

        Args:
            base: Base canvas (modified in place)
            layer: Layer to composite
        """
        blend_fn = BLEND_FUNCTIONS.get(layer.blend_mode, _blend_normal)

        for y in range(layer.canvas.height):
            for x in range(layer.canvas.width):
                # Calculate position on base canvas
                bx = x + layer.offset_x
                by = y + layer.offset_y

                if 0 <= bx < base.width and 0 <= by < base.height:
                    src = layer.canvas.pixels[y][x]
                    dst = base.pixels[by][bx]

                    # Calculate effective alpha
                    src_alpha = (src[3] / 255.0) * layer.opacity

                    if src_alpha > 0:
                        # Blend each channel
                        r = blend_fn(dst[0], src[0], src_alpha)
                        g = blend_fn(dst[1], src[1], src_alpha)
                        b = blend_fn(dst[2], src[2], src_alpha)

                        # Calculate output alpha
                        dst_alpha = dst[3] / 255.0
                        out_alpha = src_alpha + dst_alpha * (1 - src_alpha)
                        a = _clamp(int(out_alpha * 255))

                        base.pixels[by][bx] = (r, g, b, a)

    def set_layer_opacity(self, name_or_index, opacity: float) -> bool:
        """Set layer opacity.

        Args:
            name_or_index: Layer identifier
            opacity: Opacity value (0.0 to 1.0)

        Returns:
            True if successful
        """
        layer = self.get_layer(name_or_index)
        if layer:
            layer.opacity = max(0.0, min(1.0, opacity))
            return True
        return False

    def set_layer_blend_mode(self, name_or_index, mode: BlendMode) -> bool:
        """Set layer blend mode.

        Args:
            name_or_index: Layer identifier
            mode: Blend mode

        Returns:
            True if successful
        """
        layer = self.get_layer(name_or_index)
        if layer:
            layer.blend_mode = mode
            return True
        return False

    def set_layer_visible(self, name_or_index, visible: bool) -> bool:
        """Set layer visibility.

        Args:
            name_or_index: Layer identifier
            visible: Visibility

        Returns:
            True if successful
        """
        layer = self.get_layer(name_or_index)
        if layer:
            layer.visible = visible
            return True
        return False

    def __len__(self) -> int:
        """Get number of layers."""
        return len(self.layers)

    def __iter__(self):
        """Iterate over layers (bottom to top)."""
        return iter(self.layers)

    @property
    def layer_names(self) -> List[str]:
        """Get list of layer names."""
        return [layer.name for layer in self.layers]


class LayerGroup:
    """Group of layers that can be manipulated together."""

    def __init__(self, name: str):
        """Initialize layer group.

        Args:
            name: Group name
        """
        self.name = name
        self.layers: List[Layer] = []
        self.visible = True
        self.opacity = 1.0
        self.collapsed = False

    def add(self, layer: Layer) -> None:
        """Add layer to group."""
        self.layers.append(layer)

    def remove(self, layer: Layer) -> bool:
        """Remove layer from group."""
        if layer in self.layers:
            self.layers.remove(layer)
            return True
        return False

    def set_visible(self, visible: bool) -> None:
        """Set visibility of all layers in group."""
        self.visible = visible
        for layer in self.layers:
            layer.visible = visible

    def set_opacity(self, opacity: float) -> None:
        """Set opacity of all layers in group."""
        self.opacity = opacity
        for layer in self.layers:
            layer.opacity = opacity


# Convenience functions
def create_layer_stack(width: int, height: int,
                       background: Tuple[int, int, int, int] = (0, 0, 0, 0)
                       ) -> LayerStack:
    """Create a new layer stack.

    Args:
        width: Canvas width
        height: Canvas height
        background: Background color

    Returns:
        New LayerStack
    """
    return LayerStack(width, height, background)


def blend_canvases(base: Canvas, overlay: Canvas,
                   mode: BlendMode = BlendMode.NORMAL,
                   opacity: float = 1.0,
                   offset: Tuple[int, int] = (0, 0)) -> Canvas:
    """Blend two canvases together.

    Args:
        base: Base canvas
        overlay: Overlay canvas
        mode: Blend mode
        opacity: Overlay opacity
        offset: Overlay offset (x, y)

    Returns:
        New blended canvas
    """
    result = base.copy()
    layer = Layer("temp", overlay, opacity=opacity, blend_mode=mode,
                  offset_x=offset[0], offset_y=offset[1])

    stack = LayerStack(base.width, base.height)
    stack._composite_layer(result, layer)

    return result


def list_blend_modes() -> List[str]:
    """List available blend modes."""
    return [mode.value for mode in BlendMode]

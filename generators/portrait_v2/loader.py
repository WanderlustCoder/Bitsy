"""
Template loader for portrait_v2.

Loads PNG templates and their JSON metadata.
Supports automatic scaling for different canvas sizes.
"""

import json
import os
from dataclasses import dataclass
from typing import Dict, List, Tuple

from core.png_writer import load_png


@dataclass
class Template:
    """Loaded template image and metadata."""
    name: str
    pixels: List[List[Tuple[int, int, int, int]]]
    width: int
    height: int
    anchor: Tuple[int, int]
    symmetric: bool
    flip_for_right: bool


class TemplateLoader:
    """Loads and manages portrait templates."""

    # Original canvas size templates were designed for
    # Templates have already been resized for 64x96 canvas
    ORIGINAL_CANVAS_SIZE = (64, 96)

    def __init__(self, base_path: str, target_canvas_size: Tuple[int, int] = None):
        self.base_path = base_path
        self._cache: Dict[str, Template] = {}
        self.target_canvas_size = target_canvas_size

        # Calculate scale factor if target size differs from original
        if target_canvas_size:
            # Use height ratio for uniform scaling to avoid distortion
            self.scale = target_canvas_size[1] / self.ORIGINAL_CANVAS_SIZE[1]
        else:
            self.scale = 1.0

    def load(self, name: str, subdir: str = "") -> Template:
        cache_key = f"{subdir}/{name}_{self.scale}" if subdir else f"{name}_{self.scale}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        dir_path = os.path.join(self.base_path, subdir) if subdir else self.base_path
        png_path = os.path.join(dir_path, f"{name}.png")
        json_path = os.path.join(dir_path, f"{name}.json")

        if not os.path.exists(png_path):
            raise FileNotFoundError(f"Template not found: {png_path}")

        pixels = load_png(png_path)
        height = len(pixels)
        width = len(pixels[0]) if height else 0

        metadata = self._load_metadata(json_path, width, height)
        anchor = tuple(metadata.get("anchor", (width // 2, height // 2)))

        # Apply scaling if needed
        if self.scale != 1.0:
            pixels = self._scale_pixels(pixels, self.scale)
            width = int(width * self.scale)
            height = int(height * self.scale)
            anchor = (int(anchor[0] * self.scale), int(anchor[1] * self.scale))

        template = Template(
            name=name,
            pixels=pixels,
            width=width,
            height=height,
            anchor=anchor,
            symmetric=metadata.get("symmetric", False),
            flip_for_right=metadata.get("flip_for_right", False),
        )

        self._cache[cache_key] = template
        return template

    def _scale_pixels(
        self,
        pixels: List[List[Tuple[int, int, int, int]]],
        scale: float
    ) -> List[List[Tuple[int, int, int, int]]]:
        """Scale pixel data using nearest-neighbor interpolation for pixel art."""
        if not pixels:
            return pixels

        orig_height = len(pixels)
        orig_width = len(pixels[0])
        new_height = max(1, int(orig_height * scale))
        new_width = max(1, int(orig_width * scale))

        result = []
        for new_y in range(new_height):
            row = []
            orig_y = min(int(new_y / scale), orig_height - 1)
            for new_x in range(new_width):
                orig_x = min(int(new_x / scale), orig_width - 1)
                row.append(pixels[orig_y][orig_x])
            result.append(row)

        return result

    def _load_metadata(self, json_path: str, width: int, height: int) -> dict:
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as handle:
                return json.load(handle)
        return {
            "anchor": (width // 2, height // 2),
            "symmetric": False,
            "flip_for_right": False,
        }

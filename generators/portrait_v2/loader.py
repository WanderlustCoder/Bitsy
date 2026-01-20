"""
Template loader for portrait_v2.

Loads PNG templates and their JSON metadata.
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

    def __init__(self, base_path: str):
        self.base_path = base_path
        self._cache: Dict[str, Template] = {}

    def load(self, name: str, subdir: str = "") -> Template:
        cache_key = f"{subdir}/{name}" if subdir else name
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

        template = Template(
            name=name,
            pixels=pixels,
            width=width,
            height=height,
            anchor=tuple(metadata.get("anchor", (width // 2, height // 2))),
            symmetric=metadata.get("symmetric", False),
            flip_for_right=metadata.get("flip_for_right", False),
        )

        self._cache[cache_key] = template
        return template

    def _load_metadata(self, json_path: str, width: int, height: int) -> dict:
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as handle:
                return json.load(handle)
        return {
            "anchor": (width // 2, height // 2),
            "symmetric": False,
            "flip_for_right": False,
        }

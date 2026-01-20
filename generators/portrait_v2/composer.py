"""Template composition and portrait generation."""
import os
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.canvas import Canvas
from generators.portrait_v2.loader import TemplateLoader, Template
from generators.portrait_v2.recolor import recolor_template, create_skin_palette


@dataclass
class StyleProfile:
    """Loaded style profile configuration."""
    name: str
    canvas_size: Tuple[int, int]
    proportions: Dict[str, float]
    templates: Dict[str, List[str]]
    coloring: Dict[str, any]
    post_processing: Dict[str, any]


class TemplatePortraitGenerator:
    """
    Generate portraits by compositing pre-designed templates.
    """

    def __init__(
        self,
        style_path: str = "templates/anime_standard",
        skin_color: Tuple[int, int, int] = (232, 190, 160),
        eye_color: Tuple[int, int, int] = (100, 80, 60),
        hair_color: Tuple[int, int, int] = (60, 40, 30),
        clothing_color: Tuple[int, int, int] = (80, 60, 120),
        seed: Optional[int] = None,
    ):
        self.style_path = style_path
        self.skin_color = skin_color
        self.eye_color = eye_color
        self.hair_color = hair_color
        self.clothing_color = clothing_color

        self.profile = self._load_profile()
        self.loader = TemplateLoader(style_path)

        self.skin_palette = create_skin_palette(skin_color,
            use_hue_shift=self.profile.coloring.get("use_hue_shift", True))
        self.eye_palette = create_skin_palette(eye_color, use_hue_shift=True)
        self.hair_palette = create_skin_palette(hair_color, use_hue_shift=True)
        self.clothing_palette = create_skin_palette(clothing_color, use_hue_shift=True)

        self.sclera_palette = [
            (250, 248, 245, 255),
            (235, 230, 225, 255),
            (220, 210, 205, 255),
            (255, 252, 250, 255),
            (255, 255, 255, 255),
            (200, 190, 185, 255),
        ]

    def _load_profile(self) -> StyleProfile:
        profile_path = os.path.join(self.style_path, "profile.json")

        with open(profile_path, 'r') as f:
            data = json.load(f)

        return StyleProfile(
            name=data["name"],
            canvas_size=tuple(data["canvas_size"]),
            proportions=data["proportions"],
            templates=data["templates"],
            coloring=data.get("coloring", {}),
            post_processing=data.get("post_processing", {}),
        )

    def render(self) -> Canvas:
        width, height = self.profile.canvas_size
        canvas = Canvas(width, height)

        props = self.profile.proportions

        head_y = int(height * props.get("head_y", 0.08))
        head_height = int(height * props.get("head_height_ratio", 0.38))
        face_width = int(width * props.get("face_width_ratio", 0.35))

        face_cx = width // 2
        face_cy = head_y + head_height // 2

        # Render layers back to front:
        # 1. Back hair (behind everything)
        self._render_hair_back(canvas, face_cx, head_y)

        # 2. Body (shoulders, torso)
        body_y = head_y + head_height - 8  # Overlap slightly with head
        self._render_body(canvas, face_cx, body_y)

        # 3. Face base
        self._render_face(canvas, face_cx, face_cy)

        # 4. Eyes
        eye_y = head_y + int(head_height * props.get("eye_y", 0.42))
        eye_spacing = int(face_width * props.get("eye_spacing", 0.24))
        self._render_eyes(canvas, face_cx, eye_y, eye_spacing)

        # 5. Nose
        nose_y = head_y + int(head_height * props.get("nose_y", 0.58))
        self._render_nose(canvas, face_cx, nose_y)

        # 6. Mouth
        mouth_y = head_y + int(head_height * props.get("mouth_y", 0.68))
        self._render_mouth(canvas, face_cx, mouth_y)

        # 7. Front hair (bangs, on top of face)
        self._render_hair_front(canvas, face_cx, head_y)

        return canvas

    def _render_face(self, canvas: Canvas, cx: int, cy: int) -> None:
        face_templates = self.profile.templates.get("faces", ["oval"])
        template = self.loader.load(face_templates[0], "faces")
        recolored = recolor_template(template.pixels, self.skin_palette)
        self._composite(canvas, recolored,
                       cx - template.anchor[0],
                       cy - template.anchor[1])

    def _render_eyes(self, canvas: Canvas, cx: int, y: int, spacing: int) -> None:
        eye_templates = self.profile.templates.get("eyes", ["large"])
        template = self.loader.load(eye_templates[0], "eyes")
        recolored = recolor_template(template.pixels, self.eye_palette,
                                     secondary_palette=self.sclera_palette)

        left_x = cx - spacing - template.anchor[0]
        self._composite(canvas, recolored, left_x, y - template.anchor[1])

        right_x = cx + spacing - (template.width - template.anchor[0])
        if template.flip_for_right:
            flipped = self._flip_horizontal(recolored)
            self._composite(canvas, flipped, right_x, y - template.anchor[1])
        else:
            self._composite(canvas, recolored, right_x, y - template.anchor[1])

    def _render_nose(self, canvas: Canvas, cx: int, y: int) -> None:
        nose_templates = self.profile.templates.get("noses", ["dot"])
        template = self.loader.load(nose_templates[0], "noses")
        recolored = recolor_template(template.pixels, self.skin_palette)
        self._composite(canvas, recolored,
                       cx - template.anchor[0],
                       y - template.anchor[1])

    def _render_mouth(self, canvas: Canvas, cx: int, y: int) -> None:
        mouth_templates = self.profile.templates.get("mouths", ["neutral"])
        template = self.loader.load(mouth_templates[0], "mouths")
        recolored = recolor_template(template.pixels, self.skin_palette)
        self._composite(canvas, recolored,
                       cx - template.anchor[0],
                       y - template.anchor[1])

    def _render_hair_back(self, canvas: Canvas, cx: int, head_y: int) -> None:
        """Render back hair layer (behind face)."""
        hair_templates = self.profile.templates.get("hair_back", [])
        if not hair_templates:
            return
        try:
            template = self.loader.load(hair_templates[0], "hair")
            recolored = recolor_template(template.pixels, self.hair_palette)
            # Position hair centered on head
            self._composite(canvas, recolored,
                           cx - template.anchor[0],
                           head_y - template.anchor[1] + 5)
        except FileNotFoundError:
            pass  # Template not yet created

    def _render_hair_front(self, canvas: Canvas, cx: int, head_y: int) -> None:
        """Render front hair layer (bangs, on top of face)."""
        hair_templates = self.profile.templates.get("hair_front", [])
        if not hair_templates:
            return
        try:
            template = self.loader.load(hair_templates[0], "hair")
            recolored = recolor_template(template.pixels, self.hair_palette)
            # Position bangs at forehead
            self._composite(canvas, recolored,
                           cx - template.anchor[0],
                           head_y + 5)
        except FileNotFoundError:
            pass  # Template not yet created

    def _render_body(self, canvas: Canvas, cx: int, y: int) -> None:
        """Render body (shoulders and torso)."""
        body_templates = self.profile.templates.get("bodies", [])
        if not body_templates:
            return
        try:
            template = self.loader.load(body_templates[0], "bodies")
            # Body uses clothing color, with skin for neck (secondary)
            recolored = recolor_template(template.pixels, self.clothing_palette,
                                        secondary_palette=self.skin_palette)
            self._composite(canvas, recolored,
                           cx - template.anchor[0],
                           y - template.anchor[1])
        except FileNotFoundError:
            pass  # Template not yet created

    def _composite(self, canvas: Canvas,
                   pixels: List[List[Tuple[int, int, int, int]]],
                   x: int, y: int) -> None:
        for py, row in enumerate(pixels):
            for px, color in enumerate(row):
                if color[3] > 0:
                    canvas_x = x + px
                    canvas_y = y + py
                    if 0 <= canvas_x < canvas.width and 0 <= canvas_y < canvas.height:
                        if color[3] >= 255:
                            canvas.set_pixel_solid(canvas_x, canvas_y, color)
                        else:
                            existing = canvas.get_pixel(canvas_x, canvas_y)
                            if existing:
                                alpha = color[3] / 255
                                blended = (
                                    int(color[0] * alpha + existing[0] * (1 - alpha)),
                                    int(color[1] * alpha + existing[1] * (1 - alpha)),
                                    int(color[2] * alpha + existing[2] * (1 - alpha)),
                                    255
                                )
                                canvas.set_pixel_solid(canvas_x, canvas_y, blended)
                            else:
                                canvas.set_pixel_solid(canvas_x, canvas_y, color)

    def _flip_horizontal(self,
                         pixels: List[List[Tuple[int, int, int, int]]]
                         ) -> List[List[Tuple[int, int, int, int]]]:
        return [list(reversed(row)) for row in pixels]

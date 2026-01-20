"""Template composition and portrait generation."""
import os
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.canvas import Canvas
from generators.portrait_v2.loader import TemplateLoader, Template
from generators.portrait_v2.recolor import recolor_template, create_skin_palette, create_hair_palette
from generators.portrait_parts.post_processing import apply_silhouette_rim_light, apply_outline


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
        accessory_color: Tuple[int, int, int] = (60, 50, 40),
        prop_color: Tuple[int, int, int] = (139, 90, 43),
        # Glasses
        has_glasses: bool = False,
        glasses_style: str = "round",
        # Props
        has_prop: bool = False,
        prop_type: str = "book",
        # Hair style
        hair_style: str = "wavy",
        # Face shape
        face_shape: str = "oval",
        # Expressions
        mouth_expression: str = "neutral",
        eye_expression: str = "normal",
        # Eyebrows
        eyebrow_style: str = "normal",
        # Hair accessories
        has_hair_accessory: bool = False,
        hair_accessory_style: str = "none",
        # Earrings
        has_earrings: bool = False,
        earring_style: str = "stud",
        seed: Optional[int] = None,
    ):
        self.style_path = style_path
        self.skin_color = skin_color
        self.eye_color = eye_color
        self.hair_color = hair_color
        self.clothing_color = clothing_color
        self.accessory_color = accessory_color
        self.prop_color = prop_color
        self.has_glasses = has_glasses
        self.glasses_style = glasses_style
        self.has_prop = has_prop
        self.prop_type = prop_type
        self.hair_style = hair_style
        self.face_shape = face_shape
        self.mouth_expression = mouth_expression
        self.eye_expression = eye_expression
        self.eyebrow_style = eyebrow_style
        self.has_hair_accessory = has_hair_accessory
        self.hair_accessory_style = hair_accessory_style
        self.has_earrings = has_earrings
        self.earring_style = earring_style

        self.profile = self._load_profile()
        self.loader = TemplateLoader(style_path)

        self.skin_palette = create_skin_palette(skin_color,
            use_hue_shift=self.profile.coloring.get("use_hue_shift", True))
        self.eye_palette = create_skin_palette(eye_color, use_hue_shift=True)
        self.hair_palette = create_hair_palette(hair_color, use_hue_shift=True)
        self.clothing_palette = create_skin_palette(clothing_color, use_hue_shift=True)
        self.accessory_palette = create_skin_palette(accessory_color, use_hue_shift=True)
        self.prop_palette = create_skin_palette(prop_color, use_hue_shift=True)

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

        # 3. Props behind body (like book being held)
        if self.has_prop:
            self._render_prop(canvas, face_cx, body_y)

        # 4. Face base
        self._render_face(canvas, face_cx, face_cy)

        # 5. Earrings (behind face features)
        if self.has_earrings:
            self._render_earrings(canvas, face_cx, face_cy)

        # 6. Eyebrows
        eyebrow_y = head_y + int(head_height * props.get("eyebrow_y", 0.35))
        self._render_eyebrows(canvas, face_cx, eyebrow_y)

        # 7. Eyes
        eye_y = head_y + int(head_height * props.get("eye_y", 0.42))
        eye_spacing = int(face_width * props.get("eye_spacing", 0.24))
        self._render_eyes(canvas, face_cx, eye_y, eye_spacing)

        # 8. Accessories (glasses, etc.) - rendered on top of eyes
        self._render_accessories(canvas, face_cx, eye_y, eye_spacing)

        # 9. Nose
        nose_y = head_y + int(head_height * props.get("nose_y", 0.58))
        self._render_nose(canvas, face_cx, nose_y)

        # 10. Mouth
        mouth_y = head_y + int(head_height * props.get("mouth_y", 0.68))
        self._render_mouth(canvas, face_cx, mouth_y)

        # 11. Front hair (bangs, on top of face)
        self._render_hair_front(canvas, face_cx, head_y)

        # 12. Hair accessories (on top of hair)
        if self.has_hair_accessory:
            self._render_hair_accessory(canvas, face_cx, head_y)

        # 13. Post-processing: rim lighting
        self._apply_rim_lighting(canvas)

        # 14. Post-processing: outline
        self._apply_outline(canvas)

        return canvas

    def _apply_rim_lighting(self, canvas: Canvas) -> None:
        """Apply rim lighting post-processing for dramatic anime effect."""
        coloring = self.profile.coloring
        rim_color = tuple(coloring.get("rim_light_color", [180, 210, 255]))
        rim_intensity = coloring.get("rim_light_intensity", 0.7)

        apply_silhouette_rim_light(
            canvas,
            rim_color=rim_color,
            intensity=rim_intensity,
            thickness=2,
            direction="right"  # Light from right side
        )

    def _apply_outline(self, canvas: Canvas) -> None:
        """Apply outline around the portrait silhouette."""
        post = self.profile.post_processing
        outline_mode = post.get("outline", "none")

        if outline_mode == "none":
            return

        outline_color = tuple(post.get("outline_color", [40, 30, 50])) + (255,)
        thickness = 1 if outline_mode == "thin" else 2

        apply_outline(canvas, outline_color=outline_color, thickness=thickness)

    def _render_face(self, canvas: Canvas, cx: int, cy: int) -> None:
        # Use face_shape parameter to select template
        template_name = self.face_shape if self.face_shape else "oval"
        try:
            template = self.loader.load(template_name, "faces")
        except FileNotFoundError:
            template = self.loader.load("oval", "faces")  # Fallback
        recolored = recolor_template(template.pixels, self.skin_palette)
        self._composite(canvas, recolored,
                       cx - template.anchor[0],
                       cy - template.anchor[1])

    def _render_eyes(self, canvas: Canvas, cx: int, y: int, spacing: int) -> None:
        # Map expression to template name
        eye_template_map = {
            "normal": "large",
            "closed": "closed",
            "happy": "happy",
            "wink": "wink",
            "surprised": "surprised",
        }
        template_name = eye_template_map.get(self.eye_expression, "large")
        try:
            template = self.loader.load(template_name, "eyes")
        except FileNotFoundError:
            template = self.loader.load("large", "eyes")  # Fallback

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

    def _render_accessories(self, canvas: Canvas, cx: int, eye_y: int, eye_spacing: int) -> None:
        """Render accessories like glasses on top of eyes."""
        if not self.has_glasses:
            return

        # Map glasses style to template name
        glasses_templates = {
            "round": "glasses_round",
            "square": "glasses_square",
            "rectangular": "glasses_square",
            "cateye": "glasses_cateye",
            "cat_eye": "glasses_cateye",
        }
        template_name = glasses_templates.get(self.glasses_style.lower(), "glasses_round")

        try:
            template = self.loader.load(template_name, "accessories")
            recolored = recolor_template(template.pixels, self.accessory_palette)
            # Center glasses on face at eye level
            self._composite(canvas, recolored,
                           cx - template.anchor[0],
                           eye_y - template.anchor[1])
        except FileNotFoundError:
            pass  # Template not yet created

    def _render_nose(self, canvas: Canvas, cx: int, y: int) -> None:
        nose_templates = self.profile.templates.get("noses", ["dot"])
        template = self.loader.load(nose_templates[0], "noses")
        recolored = recolor_template(template.pixels, self.skin_palette)
        self._composite(canvas, recolored,
                       cx - template.anchor[0],
                       y - template.anchor[1])

    def _render_mouth(self, canvas: Canvas, cx: int, y: int) -> None:
        # Map expression to template name
        mouth_template_map = {
            "neutral": "neutral",
            "smile": "smile",
            "open": "open",
            "frown": "frown",
            "pout": "pout",
        }
        template_name = mouth_template_map.get(self.mouth_expression, "neutral")
        try:
            template = self.loader.load(template_name, "mouths")
        except FileNotFoundError:
            template = self.loader.load("neutral", "mouths")  # Fallback

        recolored = recolor_template(template.pixels, self.skin_palette)
        self._composite(canvas, recolored,
                       cx - template.anchor[0],
                       y - template.anchor[1])

    def _render_hair_back(self, canvas: Canvas, cx: int, head_y: int) -> None:
        """Render back hair layer (behind face)."""
        # Use hair_style to select template
        template_name = f"{self.hair_style}_back"
        try:
            template = self.loader.load(template_name, "hair")
            recolored = recolor_template(template.pixels, self.hair_palette)
            self._composite(canvas, recolored,
                           cx - template.anchor[0],
                           head_y - template.anchor[1] + 5)
        except FileNotFoundError:
            # Fallback to wavy
            try:
                template = self.loader.load("wavy_back", "hair")
                recolored = recolor_template(template.pixels, self.hair_palette)
                self._composite(canvas, recolored,
                               cx - template.anchor[0],
                               head_y - template.anchor[1] + 5)
            except FileNotFoundError:
                pass

    def _render_hair_front(self, canvas: Canvas, cx: int, head_y: int) -> None:
        """Render front hair layer (bangs, on top of face)."""
        # Use hair_style to select template
        template_name = f"{self.hair_style}_front"
        try:
            template = self.loader.load(template_name, "hair")
            recolored = recolor_template(template.pixels, self.hair_palette)
            self._composite(canvas, recolored,
                           cx - template.anchor[0],
                           head_y + 5)
        except FileNotFoundError:
            # Fallback to wavy
            try:
                template = self.loader.load("wavy_front", "hair")
                recolored = recolor_template(template.pixels, self.hair_palette)
                self._composite(canvas, recolored,
                               cx - template.anchor[0],
                               head_y + 5)
            except FileNotFoundError:
                pass

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

    def _render_eyebrows(self, canvas: Canvas, cx: int, y: int) -> None:
        """Render eyebrows above eyes."""
        eyebrow_map = {
            "normal": "normal",
            "thick": "thick",
            "thin": "thin",
            "arched": "arched",
            "angry": "angry",
            "worried": "worried",
        }
        template_name = eyebrow_map.get(self.eyebrow_style, "normal")
        try:
            template = self.loader.load(template_name, "eyebrows")
            # Eyebrows use hair color
            recolored = recolor_template(template.pixels, self.hair_palette)
            self._composite(canvas, recolored,
                           cx - template.anchor[0],
                           y - template.anchor[1])
        except FileNotFoundError:
            pass  # Template not yet created

    def _render_prop(self, canvas: Canvas, cx: int, body_y: int) -> None:
        """Render held prop like book, cup, or flower."""
        prop_map = {
            "book": "book",
            "cup": "cup",
            "flower": "flower",
            "phone": "phone",
        }
        template_name = prop_map.get(self.prop_type, "book")
        try:
            template = self.loader.load(template_name, "props")
            recolored = recolor_template(template.pixels, self.prop_palette)
            # Position prop at lower body area (hands position)
            self._composite(canvas, recolored,
                           cx - template.anchor[0],
                           body_y + 20)
        except FileNotFoundError:
            pass  # Template not yet created

    def _render_hair_accessory(self, canvas: Canvas, cx: int, head_y: int) -> None:
        """Render hair accessory like headband, bow, or clip."""
        accessory_map = {
            "headband": "headband",
            "bow": "bow",
            "clip": "clip",
            "ribbon": "ribbon",
            "flower": "hair_flower",
        }
        template_name = accessory_map.get(self.hair_accessory_style, "headband")
        try:
            template = self.loader.load(template_name, "hair_accessories")
            recolored = recolor_template(template.pixels, self.accessory_palette)
            # Position at top of head
            self._composite(canvas, recolored,
                           cx - template.anchor[0],
                           head_y - 5)
        except FileNotFoundError:
            pass  # Template not yet created

    def _render_earrings(self, canvas: Canvas, cx: int, face_cy: int) -> None:
        """Render earrings on sides of face."""
        earring_map = {
            "stud": "stud",
            "hoop": "hoop",
            "drop": "drop",
            "dangle": "dangle",
        }
        template_name = earring_map.get(self.earring_style, "stud")
        try:
            template = self.loader.load(template_name, "earrings")
            recolored = recolor_template(template.pixels, self.accessory_palette)
            # Position at ear level (sides of face)
            # Left earring
            self._composite(canvas, recolored,
                           cx - 18 - template.anchor[0],
                           face_cy + 5)
            # Right earring (flipped)
            flipped = self._flip_horizontal(recolored)
            self._composite(canvas, flipped,
                           cx + 18 - (template.width - template.anchor[0]),
                           face_cy + 5)
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

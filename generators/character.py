"""
Character Generator - Assembles parts into complete characters.

Provides a high-level interface for generating characters from
specifications or programmatic configuration.
"""

import random
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.canvas import Canvas
from core.color import Color, hex_to_rgba
from core.style import Style, PROFESSIONAL_HD
from core.palette import Palette
from core.animation import Animation

from quality.color_harmony import (
    ColorHarmony,
    generate_harmonious_palette,
    HarmonyType,
    create_shading_ramp,
)

from rig.skeleton import Skeleton, create_skeleton
from rig.pose import Pose, PoseLibrary, create_pose_library, blend_poses

from parts.base import PartConfig
from parts.heads import Head, create_head, list_head_types
from parts.bodies import Body, create_body, create_limb, list_body_types
from parts.hair import Hair, create_hair, list_hair_types
from parts.eyes import Eyes, create_eyes, get_eye_colors, list_eye_types


@dataclass
class CharacterConfig:
    """Configuration for character generation."""

    # Size
    width: int = 48
    height: int = 48

    # Style
    style: Optional[Style] = None
    style_name: str = 'modern'

    # Random seed (for determinism)
    seed: Optional[int] = None

    # Body
    body_type: str = 'chibi'
    skin_palette: str = 'warm'

    # Head
    head_type: str = 'chibi'

    # Hair
    hair_type: str = 'fluffy'
    hair_palette: str = 'lavender'
    has_bangs: bool = True

    # Eyes
    eye_type: str = 'large'
    eye_color: str = 'blue'
    expression: str = 'neutral'

    # Outfit
    outfit_color: Optional[str] = None
    outfit_palette_name: str = 'cloth_blue'


class CharacterGenerator:
    """Generates complete character sprites from configuration.

    Usage:
        gen = CharacterGenerator(width=48, height=48, seed=42)
        gen.set_style('chibi')
        gen.set_body('chibi', skin='warm')
        gen.set_hair('fluffy', palette='lavender')
        gen.set_eyes('large', color='blue')

        sprite = gen.render()
        sprite.save('character.png')
    """

    def __init__(self, width: int = 48, height: int = 48,
                 style: Optional[Style] = None, seed: Optional[int] = None,
                 hd_mode: bool = False):
        """Initialize character generator.

        Args:
            width, height: Output sprite size (default: 48x48)
            style: Art style to use (defaults to Style.default() unless hd_mode)
            seed: Random seed for deterministic generation
            hd_mode: Enable HD quality features (selout, AA)
        """
        self.hd_mode = hd_mode
        self.config = CharacterConfig(width=width, height=height, seed=seed)

        if style:
            self.config.style = style
            self.config.style_name = style.name
        elif hd_mode:
            self.config.style = PROFESSIONAL_HD
            self.config.style_name = PROFESSIONAL_HD.name
        else:
            self.config.style = Style.default()
            self.config.style_name = self.config.style.name

        self._rng = random.Random(seed)

        # Skeleton and poses
        self.skeleton: Optional[Skeleton] = None
        self.pose_library: Optional[PoseLibrary] = None
        self.current_pose: Optional[Pose] = None

        # Palettes
        self.skin_palette: Optional[Palette] = None
        self.hair_palette: Optional[Palette] = None
        self.outfit_palette: Optional[Palette] = None

        # Parts
        self.head: Optional[Head] = None
        self.body: Optional[Body] = None
        self.hair: Optional[Hair] = None
        self.eyes: Optional[Eyes] = None

        # Initialize with defaults
        self._setup_defaults()

    def _setup_defaults(self) -> None:
        """Set up default parts and skeleton."""
        # Create skeleton
        self.skeleton = create_skeleton('chibi')
        self.pose_library = create_pose_library('chibi')

        # Default palettes
        self.skin_palette = Palette.skin_warm()
        self.hair_palette = Palette.hair_lavender()
        self.outfit_palette = Palette.cloth_blue()

        # Create default parts
        self._create_parts()

    def _create_parts(self) -> None:
        """Create part objects from current config."""
        style = self.config.style

        # Head
        head_config = PartConfig(
            base_color=self.skin_palette.get(2) if self.skin_palette else (240, 200, 180, 255),
            palette=self.skin_palette,
            style=style,
            seed=self._rng.randint(0, 2**31)
        )
        self.head = create_head(self.config.head_type, head_config)

        # Body
        body_config = PartConfig(
            base_color=self.outfit_palette.get(1) if self.outfit_palette else (100, 120, 160, 255),
            palette=self.outfit_palette,
            style=style,
            seed=self._rng.randint(0, 2**31)
        )
        self.body = create_body(self.config.body_type, body_config)

        # Hair
        hair_config = PartConfig(
            base_color=self.hair_palette.get(2) if self.hair_palette else (180, 140, 200, 255),
            palette=self.hair_palette,
            style=style,
            seed=self._rng.randint(0, 2**31)
        )
        self.hair = create_hair(self.config.hair_type, hair_config)
        self.hair.has_bangs = self.config.has_bangs

        # Eyes
        eye_config = PartConfig(
            base_color=self.skin_palette.get(2) if self.skin_palette else (240, 200, 180, 255),
            style=style,
            seed=self._rng.randint(0, 2**31)
        )
        self.eyes = create_eyes(self.config.eye_type, eye_config)
        self.eyes.eye_colors = get_eye_colors(self.config.eye_color)
        self.eyes.set_expression(self.config.expression)

    def set_style(self, style_name: str) -> 'CharacterGenerator':
        """Set art style by name.

        Args:
            style_name: Style name ('chibi', 'retro_nes', etc.)
        """
        from core.style import get_style
        self.config.style = get_style(style_name)
        self.config.style_name = style_name
        self._create_parts()
        return self

    def set_body(self, body_type: str, skin: str = 'warm') -> 'CharacterGenerator':
        """Configure body.

        Args:
            body_type: Body type ('chibi', 'simple', 'muscular', 'slim')
            skin: Skin palette name ('warm', 'cool')
        """
        self.config.body_type = body_type
        self.config.skin_palette = skin

        if skin == 'warm':
            self.skin_palette = Palette.skin_warm()
        elif skin == 'cool':
            self.skin_palette = Palette.skin_cool()
        else:
            self.skin_palette = Palette.skin_warm()

        self._create_parts()
        return self

    def set_head(self, head_type: str) -> 'CharacterGenerator':
        """Configure head shape.

        Args:
            head_type: Head type ('round', 'oval', 'chibi', etc.)
        """
        self.config.head_type = head_type
        self._create_parts()
        return self

    def set_hair(self, hair_type: str, palette: str = 'lavender',
                 has_bangs: bool = True) -> 'CharacterGenerator':
        """Configure hair.

        Args:
            hair_type: Hair style ('fluffy', 'spiky', 'long', etc.)
            palette: Hair color palette name
            has_bangs: Whether to draw bangs
        """
        self.config.hair_type = hair_type
        self.config.hair_palette = palette
        self.config.has_bangs = has_bangs

        # Get palette
        if palette == 'lavender':
            self.hair_palette = Palette.hair_lavender()
        elif palette == 'brown':
            self.hair_palette = Palette.hair_brown()
        elif palette == 'pink':
            self.hair_palette = Palette.hair_lavender().shift_all(hue_degrees=-30)
        elif palette == 'blue':
            self.hair_palette = Palette.hair_lavender().shift_all(hue_degrees=60)
        elif palette == 'red':
            self.hair_palette = Palette.hair_brown().shift_all(hue_degrees=-20, sat_factor=1.3)
        elif palette == 'blonde':
            self.hair_palette = Palette.hair_brown().shift_all(hue_degrees=10, val_factor=1.4)
        elif palette == 'black':
            self.hair_palette = Palette.hair_brown().shift_all(sat_factor=0.3, val_factor=0.3)
        else:
            self.hair_palette = Palette.hair_lavender()

        self._create_parts()
        return self

    def set_eyes(self, eye_type: str, color: str = 'blue',
                 expression: str = 'neutral') -> 'CharacterGenerator':
        """Configure eyes.

        Args:
            eye_type: Eye style ('simple', 'round', 'large', 'sparkle', etc.)
            color: Eye color ('blue', 'green', 'brown', 'purple', 'red', 'gold')
            expression: Expression ('neutral', 'happy', 'sad', 'angry')
        """
        self.config.eye_type = eye_type
        self.config.eye_color = color
        self.config.expression = expression
        self._create_parts()
        return self

    def set_outfit(self, palette: str = 'cloth_blue') -> 'CharacterGenerator':
        """Configure outfit colors.

        Args:
            palette: Outfit palette name
        """
        self.config.outfit_palette_name = palette

        if palette == 'cloth_blue':
            self.outfit_palette = Palette.cloth_blue()
        elif palette == 'cloth_red':
            self.outfit_palette = Palette.cloth_blue().shift_all(hue_degrees=-120)
        elif palette == 'cloth_green':
            self.outfit_palette = Palette.cloth_blue().shift_all(hue_degrees=80)
        elif palette == 'cloth_purple':
            self.outfit_palette = Palette.cloth_blue().shift_all(hue_degrees=-60)
        elif palette == 'metal_gold':
            self.outfit_palette = Palette.metal_gold()
        else:
            self.outfit_palette = Palette.cloth_blue()

        self._create_parts()
        return self

    def set_pose(self, pose_name: str) -> 'CharacterGenerator':
        """Set character pose.

        Args:
            pose_name: Name of pose from pose library
        """
        if self.pose_library:
            pose = self.pose_library.get(pose_name)
            if pose:
                self.current_pose = pose
                if self.skeleton:
                    self.skeleton.apply_pose(pose.rotations)
        return self

    def finalize(self, canvas: Canvas) -> Canvas:
        """Apply HD post-processing effects.

        Args:
            canvas: Raw canvas to process

        Returns:
            Processed canvas with selout applied if HD mode
        """
        style = self.config.style
        if self.hd_mode and style and style.outline.selout_enabled:
            from quality.selout import apply_selout
            return apply_selout(
                canvas,
                darken_factor=style.outline.selout_darken,
                saturation_factor=style.outline.selout_saturation
            )
        return canvas

    def render(self) -> Canvas:
        """Render the character to a canvas.

        Returns:
            Canvas with rendered character
        """
        w, h = self.config.width, self.config.height
        canvas = Canvas(w, h, (0, 0, 0, 0))

        # Calculate part sizes based on style
        style = self.config.style

        # For chibi, head is large
        if style.head_ratio >= 0.4:
            head_h = int(h * 0.55)
            body_h = int(h * 0.35)
        else:
            head_h = int(h * style.head_ratio * 1.5)
            body_h = int(h * 0.5)

        head_w = int(w * 0.8)
        body_w = int(w * 0.5)

        # Center positions
        cx = w // 2
        head_cy = int(h * 0.35)
        body_cy = int(h * 0.7)

        # Draw order (back to front):
        # 1. Hair back
        # 2. Body
        # 3. Head
        # 4. Eyes
        # 5. Hair front (bangs)

        # 1. Hair back layer
        if self.hair and self.hair.has_back:
            self.hair.draw_back(canvas, cx, head_cy, head_w + 8, head_h + 8)

        # 2. Body
        if self.body:
            self.body.draw(canvas, cx, body_cy, body_w, body_h)

        # 3. Head
        if self.head:
            self.head.draw(canvas, cx, head_cy, head_w, head_h)

        # 4. Eyes
        if self.eyes and self.head:
            face_layout = self.head.get_face_layout(cx, head_cy, head_w, head_h)
            eye_w, eye_h = self.head.get_eye_size(head_w, head_h)

            left_pos = face_layout['eye_left']
            right_pos = face_layout['eye_right']

            self.eyes.draw_pair(
                canvas,
                left_pos[0], left_pos[1],
                right_pos[0], right_pos[1],
                eye_w, eye_h
            )

        # 5. Hair front (bangs)
        if self.hair and self.hair.has_bangs:
            self.hair.draw_front(canvas, cx, head_cy - head_h//6, head_w, head_h//2)

        return self.finalize(canvas)

    def render_animation(self, animation_name: str, fps: int = 8) -> Animation:
        """Render an animation sequence.

        Args:
            animation_name: Animation type ('idle', 'walk')
            fps: Frames per second

        Returns:
            Animation with rendered frames
        """
        anim = Animation(animation_name, fps=fps)

        if animation_name == 'idle':
            # Simple breathing animation
            poses = ['idle_1', 'idle_2', 'idle_1', 'idle_2']
            for pose_name in poses:
                self.set_pose(pose_name)
                frame = self.render()
                anim.add_frame(frame, duration=4)

        elif animation_name == 'walk':
            # Walk cycle
            poses = ['walk_1', 'walk_2', 'walk_3', 'walk_4']
            for pose_name in poses:
                self.set_pose(pose_name)
                frame = self.render()
                anim.add_frame(frame, duration=2)

        else:
            # Just render current pose
            frame = self.render()
            anim.add_frame(frame, duration=1)

        return anim

    def randomize(self) -> 'CharacterGenerator':
        """Randomize character appearance.

        Uses the generator's seed for determinism.
        """
        # Random hair
        hair_types = list_hair_types()
        self.config.hair_type = self._rng.choice([h for h in hair_types if h != 'bald'])

        # Random hair color
        hair_colors = ['lavender', 'brown', 'pink', 'blue', 'red', 'blonde', 'black']
        hair_color = self._rng.choice(hair_colors)

        # Random eyes
        eye_colors = ['blue', 'green', 'brown', 'purple', 'red', 'gold']
        eye_color = self._rng.choice(eye_colors)

        # Apply
        self.set_hair(self.config.hair_type, hair_color)
        self.set_eyes(self.config.eye_type, eye_color)

        base_color = self.hair_palette.get(len(self.hair_palette) // 2) if self.hair_palette else (180, 140, 200, 255)
        harmonious_colors = self._generate_harmonious_colors(base_color, count=3)
        outfit_base = harmonious_colors[0] if harmonious_colors else base_color
        self.outfit_palette = Palette(create_shading_ramp(outfit_base, levels=6), "Harmonious Outfit")
        self.config.outfit_palette_name = 'harmonious'
        self._create_parts()

        return self

    def _generate_harmonious_colors(self, base_color: Color, count: int = 3) -> List[Color]:
        """Generate harmonious colors for outfit and accessories."""
        if self._rng.random() < 0.5:
            harmony = ColorHarmony.analogous(base_color, count=count + 1, include_base=True)
        else:
            harmony = ColorHarmony.triadic(base_color, include_base=True)

        colors = [color for color in harmony.colors if color != base_color]

        if len(colors) < count:
            fallback = generate_harmonious_palette(
                base_color,
                harmony_type=HarmonyType.ANALOGOUS,
                count=count + 1,
                include_base=True
            )
            for color in fallback.colors:
                if color != base_color and color not in colors:
                    colors.append(color)
                if len(colors) >= count:
                    break

        return colors[:count]

    @classmethod
    def from_spec(cls, spec: Dict[str, Any]) -> 'CharacterGenerator':
        """Create generator from a specification dict.

        Args:
            spec: Character specification

        Returns:
            Configured CharacterGenerator
        """
        size = spec.get('size', [32, 32])
        gen = cls(
            width=size[0],
            height=size[1],
            seed=spec.get('seed')
        )

        if 'style' in spec:
            gen.set_style(spec['style'])

        body = spec.get('body', {})
        gen.set_body(
            body.get('type', 'chibi'),
            body.get('skin_palette', 'warm')
        )

        head = spec.get('head', {})
        gen.set_head(head.get('shape', 'chibi'))

        hair = spec.get('hair', {})
        gen.set_hair(
            hair.get('style', 'fluffy'),
            hair.get('palette', 'lavender'),
            hair.get('has_bangs', True)
        )

        eyes = spec.get('eyes', {})
        gen.set_eyes(
            eyes.get('style', 'large'),
            eyes.get('color', 'blue'),
            eyes.get('expression', 'neutral')
        )

        outfit = spec.get('outfit', {})
        gen.set_outfit(outfit.get('palette', 'cloth_blue'))

        return gen


def generate_character(width: int = 32, height: int = 32,
                       seed: Optional[int] = None,
                       hd_mode: bool = False, **kwargs) -> Canvas:
    """Quick function to generate a character sprite.

    Args:
        width, height: Sprite size
        seed: Random seed
        hd_mode: Enable HD quality features (selout, AA)
        **kwargs: Additional configuration (hair, eyes, etc.)

    Returns:
        Canvas with rendered character
    """
    gen = CharacterGenerator(width=width, height=height, seed=seed, hd_mode=hd_mode)

    if 'style' in kwargs:
        gen.set_style(kwargs['style'])

    if 'hair' in kwargs:
        hair = kwargs['hair']
        if isinstance(hair, dict):
            gen.set_hair(hair.get('type', 'fluffy'), hair.get('color', 'lavender'))
        else:
            gen.set_hair(hair)

    if 'eyes' in kwargs:
        eyes = kwargs['eyes']
        if isinstance(eyes, dict):
            gen.set_eyes(eyes.get('type', 'large'), eyes.get('color', 'blue'))
        else:
            gen.set_eyes('large', eyes)

    if 'randomize' in kwargs and kwargs['randomize']:
        gen.randomize()

    return gen.render()

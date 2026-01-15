"""
Character - Represents an assembled character with all its parts.

A Character is an immutable representation of a fully configured
character sprite that can be rendered, animated, and modified
(by creating new instances with different properties).
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
import copy

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.canvas import Canvas
from core.palette import Palette
from core.style import Style
from core.animation import Animation

from rig.skeleton import Skeleton, create_skeleton
from rig.pose import Pose, PoseLibrary, create_pose_library

from parts.base import PartConfig
from parts.heads import Head, create_head
from parts.bodies import Body, create_body
from parts.hair import Hair, create_hair
from parts.eyes import Eyes, create_eyes, get_eye_colors


@dataclass
class CharacterParts:
    """Container for all character parts."""
    head: Optional[Head] = None
    body: Optional[Body] = None
    hair: Optional[Hair] = None
    eyes: Optional[Eyes] = None
    # Future: arms, legs, equipment, accessories


@dataclass
class CharacterPalettes:
    """Container for character color palettes."""
    skin: Optional[Palette] = None
    hair: Optional[Palette] = None
    outfit: Optional[Palette] = None
    eyes: Optional[Tuple[int, int, int, int]] = None  # Eye color tuple


@dataclass
class CharacterLayout:
    """Defines positioning and sizing of character parts."""
    width: int = 32
    height: int = 32

    # Head positioning (as fraction of total height)
    head_y: float = 0.35  # Center Y position
    head_width: float = 0.8  # Fraction of total width
    head_height: float = 0.55  # Fraction of total height

    # Body positioning
    body_y: float = 0.7
    body_width: float = 0.5
    body_height: float = 0.35

    # Hair extends beyond head
    hair_padding: int = 8

    def get_head_rect(self) -> Tuple[int, int, int, int]:
        """Get head center position and dimensions."""
        cx = self.width // 2
        cy = int(self.height * self.head_y)
        w = int(self.width * self.head_width)
        h = int(self.height * self.head_height)
        return cx, cy, w, h

    def get_body_rect(self) -> Tuple[int, int, int, int]:
        """Get body center position and dimensions."""
        cx = self.width // 2
        cy = int(self.height * self.body_y)
        w = int(self.width * self.body_width)
        h = int(self.height * self.body_height)
        return cx, cy, w, h

    def get_hair_rect(self) -> Tuple[int, int, int, int]:
        """Get hair area (larger than head for overflow)."""
        hx, hy, hw, hh = self.get_head_rect()
        return hx, hy, hw + self.hair_padding, hh + self.hair_padding

    @classmethod
    def for_style(cls, style: Style, width: int = 32, height: int = 32) -> 'CharacterLayout':
        """Create layout appropriate for a given style."""
        layout = cls(width=width, height=height)

        # Adjust proportions based on style's head ratio
        if style.head_ratio >= 0.4:  # Chibi style
            layout.head_height = 0.55
            layout.body_height = 0.35
            layout.head_y = 0.35
            layout.body_y = 0.7
        else:  # More realistic proportions
            layout.head_height = style.head_ratio * 1.5
            layout.body_height = 0.5
            layout.head_y = 0.3
            layout.body_y = 0.65

        return layout


class Character:
    """An assembled character ready for rendering and animation.

    Characters are created using CharacterBuilder and are designed
    to be mostly immutable - modification methods return new instances.

    Usage:
        # Create via builder
        char = (CharacterBuilder()
            .head('round')
            .body('chibi')
            .hair('spiky', color='brown')
            .eyes('large', color='blue')
            .build())

        # Render
        sprite = char.render()
        sprite.save('character.png')

        # Create variations
        happy_char = char.with_expression('happy')
        walking_char = char.with_pose('walk_1')

        # Animate
        walk_anim = char.animate('walk')
    """

    def __init__(
        self,
        parts: CharacterParts,
        palettes: CharacterPalettes,
        style: Style,
        layout: CharacterLayout,
        skeleton: Optional[Skeleton] = None,
        pose_library: Optional[PoseLibrary] = None,
        current_pose: Optional[Pose] = None,
        expression: str = 'neutral',
        seed: Optional[int] = None
    ):
        """Initialize character (use CharacterBuilder instead of direct construction)."""
        self._parts = parts
        self._palettes = palettes
        self._style = style
        self._layout = layout
        self._skeleton = skeleton
        self._pose_library = pose_library
        self._current_pose = current_pose
        self._expression = expression
        self._seed = seed

    @property
    def width(self) -> int:
        """Character sprite width."""
        return self._layout.width

    @property
    def height(self) -> int:
        """Character sprite height."""
        return self._layout.height

    @property
    def style(self) -> Style:
        """Character's art style."""
        return self._style

    @property
    def expression(self) -> str:
        """Current facial expression."""
        return self._expression

    def render(self, canvas: Optional[Canvas] = None) -> Canvas:
        """Render the character to a canvas.

        Args:
            canvas: Optional canvas to render onto. If None, creates new canvas.

        Returns:
            Canvas with rendered character.
        """
        if canvas is None:
            canvas = Canvas(self._layout.width, self._layout.height, (0, 0, 0, 0))

        # Get layout positions
        head_cx, head_cy, head_w, head_h = self._layout.get_head_rect()
        body_cx, body_cy, body_w, body_h = self._layout.get_body_rect()
        hair_cx, hair_cy, hair_w, hair_h = self._layout.get_hair_rect()

        # Draw order (back to front):
        # 1. Hair back layer
        # 2. Body
        # 3. Head
        # 4. Eyes
        # 5. Hair front (bangs)

        # 1. Hair back layer
        if self._parts.hair and self._parts.hair.has_back:
            self._parts.hair.draw_back(canvas, hair_cx, hair_cy, hair_w, hair_h)

        # 2. Body
        if self._parts.body:
            self._parts.body.draw(canvas, body_cx, body_cy, body_w, body_h)

        # 3. Head
        if self._parts.head:
            self._parts.head.draw(canvas, head_cx, head_cy, head_w, head_h)

        # 4. Eyes
        if self._parts.eyes and self._parts.head:
            face_layout = self._parts.head.get_face_layout(head_cx, head_cy, head_w, head_h)
            eye_w, eye_h = self._parts.head.get_eye_size(head_w, head_h)

            left_pos = face_layout['eye_left']
            right_pos = face_layout['eye_right']

            self._parts.eyes.draw_pair(
                canvas,
                left_pos[0], left_pos[1],
                right_pos[0], right_pos[1],
                eye_w, eye_h
            )

        # 5. Hair front (bangs)
        if self._parts.hair and self._parts.hair.has_bangs:
            bangs_y = head_cy - head_h // 6
            bangs_h = head_h // 2
            self._parts.hair.draw_front(canvas, head_cx, bangs_y, head_w, bangs_h)

        return canvas

    def with_expression(self, expression: str) -> 'Character':
        """Create a new character with a different expression.

        Args:
            expression: Expression name ('neutral', 'happy', 'sad', 'angry')

        Returns:
            New Character instance with updated expression.
        """
        # Deep copy parts so we can modify eyes
        new_parts = copy.deepcopy(self._parts)
        if new_parts.eyes:
            new_parts.eyes.set_expression(expression)

        return Character(
            parts=new_parts,
            palettes=self._palettes,
            style=self._style,
            layout=self._layout,
            skeleton=self._skeleton,
            pose_library=self._pose_library,
            current_pose=self._current_pose,
            expression=expression,
            seed=self._seed
        )

    def with_pose(self, pose_name: str) -> 'Character':
        """Create a new character with a different pose.

        Args:
            pose_name: Name of pose from pose library

        Returns:
            New Character instance with updated pose.
        """
        new_pose = None
        if self._pose_library:
            new_pose = self._pose_library.get(pose_name)

        return Character(
            parts=self._parts,
            palettes=self._palettes,
            style=self._style,
            layout=self._layout,
            skeleton=self._skeleton,
            pose_library=self._pose_library,
            current_pose=new_pose,
            expression=self._expression,
            seed=self._seed
        )

    def animate(self, animation_name: str, fps: int = 8) -> Animation:
        """Generate an animation sequence.

        Args:
            animation_name: Animation type ('idle', 'walk', 'run', etc.)
            fps: Frames per second

        Returns:
            Animation with rendered frames.
        """
        anim = Animation(animation_name, fps=fps)

        # Animation definitions
        animations = {
            'idle': {
                'poses': ['idle', 'idle', 'idle', 'idle'],
                'expressions': ['neutral', 'neutral', 'neutral', 'neutral'],
                'duration': 4
            },
            'walk': {
                'poses': ['walk_1', 'walk_2', 'walk_3', 'walk_4'],
                'expressions': ['neutral', 'neutral', 'neutral', 'neutral'],
                'duration': 2
            },
            'happy': {
                'poses': ['idle', 'idle'],
                'expressions': ['happy', 'happy'],
                'duration': 4
            },
            'sad': {
                'poses': ['idle', 'idle'],
                'expressions': ['sad', 'sad'],
                'duration': 4
            },
            'blink': {
                'poses': ['idle', 'idle', 'idle', 'idle'],
                'expressions': ['neutral', 'neutral', 'neutral', 'neutral'],
                'duration': 2,
                'blink_frames': [2]  # Which frame to close eyes
            }
        }

        anim_def = animations.get(animation_name, animations['idle'])
        poses = anim_def['poses']
        expressions = anim_def['expressions']
        duration = anim_def['duration']

        for i, (pose_name, expr) in enumerate(zip(poses, expressions)):
            char = self.with_expression(expr)
            if self._pose_library:
                char = char.with_pose(pose_name)
            frame = char.render()
            anim.add_frame(frame, duration=duration)

        return anim

    def copy(self) -> 'Character':
        """Create a deep copy of this character."""
        return Character(
            parts=copy.deepcopy(self._parts),
            palettes=copy.deepcopy(self._palettes),
            style=self._style,
            layout=copy.deepcopy(self._layout),
            skeleton=self._skeleton,
            pose_library=self._pose_library,
            current_pose=self._current_pose,
            expression=self._expression,
            seed=self._seed
        )

    def __repr__(self) -> str:
        parts_list = []
        if self._parts.head:
            parts_list.append(f"head={self._parts.head.name}")
        if self._parts.body:
            parts_list.append(f"body={self._parts.body.name}")
        if self._parts.hair:
            parts_list.append(f"hair={self._parts.hair.name}")
        if self._parts.eyes:
            parts_list.append(f"eyes={self._parts.eyes.name}")

        return f"Character({', '.join(parts_list)}, expression='{self._expression}')"

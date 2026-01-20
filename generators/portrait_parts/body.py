"""
Anime-Style Upper Body Rendering

Provides skeleton-based body rendering with pose support for anime portraits.
Includes shoulder, arm, and hand positioning with clothing overlay.
"""

import math
from enum import Enum
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass, field

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.canvas import Canvas
from generators.color_utils import HueShiftPalette, create_hue_shifted_ramp


class BodyPose(Enum):
    """Predefined body poses for anime portraits."""
    NEUTRAL = "neutral"           # Arms at sides, relaxed
    HOLDING = "holding"           # Hands together, holding object
    ARMS_CROSSED = "arms_crossed" # Folded across chest
    HAND_ON_CHEST = "hand_on_chest"  # One hand on chest
    READING = "reading"           # Holding book/item up


class ClothingStyle(Enum):
    """Basic clothing styles."""
    SIMPLE = "simple"             # Plain shirt/top
    COLLAR = "collar"             # Collared shirt
    UNIFORM = "uniform"           # School uniform style
    DRESS = "dress"               # Dress/gown
    CASUAL = "casual"             # T-shirt style


@dataclass
class Bone:
    """A single bone in the skeleton."""
    name: str
    parent: Optional[str]
    base_position: Tuple[float, float]  # Relative to parent or origin
    length: float
    angle: float = 0.0  # Rotation in degrees

    def get_end_position(self, start: Tuple[float, float]) -> Tuple[float, float]:
        """Calculate end position from start and angle."""
        rad = math.radians(self.angle)
        return (
            start[0] + self.length * math.cos(rad),
            start[1] + self.length * math.sin(rad)
        )


@dataclass
class Skeleton:
    """Simple skeleton for upper body posing."""
    bones: Dict[str, Bone] = field(default_factory=dict)

    def __post_init__(self):
        if not self.bones:
            self._create_default_skeleton()

    def _create_default_skeleton(self):
        """Create default upper body skeleton."""
        # All positions relative to neck base (0, 0)
        self.bones = {
            "spine": Bone("spine", None, (0, 0), 20, 90),
            "neck": Bone("neck", "spine", (0, -20), 8, -90),
            "shoulder_l": Bone("shoulder_l", "spine", (-12, -18), 10, 180),
            "shoulder_r": Bone("shoulder_r", "spine", (12, -18), 10, 0),
            "upper_arm_l": Bone("upper_arm_l", "shoulder_l", (0, 0), 18, 100),
            "upper_arm_r": Bone("upper_arm_r", "shoulder_r", (0, 0), 18, 80),
            "lower_arm_l": Bone("lower_arm_l", "upper_arm_l", (0, 0), 16, 110),
            "lower_arm_r": Bone("lower_arm_r", "upper_arm_r", (0, 0), 16, 70),
            "hand_l": Bone("hand_l", "lower_arm_l", (0, 0), 6, 100),
            "hand_r": Bone("hand_r", "lower_arm_r", (0, 0), 6, 80),
        }

    def apply_pose(self, pose: BodyPose):
        """Apply a predefined pose to the skeleton."""
        if pose == BodyPose.NEUTRAL:
            self._apply_neutral_pose()
        elif pose == BodyPose.HOLDING:
            self._apply_holding_pose()
        elif pose == BodyPose.ARMS_CROSSED:
            self._apply_arms_crossed_pose()
        elif pose == BodyPose.HAND_ON_CHEST:
            self._apply_hand_on_chest_pose()
        elif pose == BodyPose.READING:
            self._apply_reading_pose()

    def _apply_neutral_pose(self):
        """Arms relaxed at sides."""
        self.bones["upper_arm_l"].angle = 100
        self.bones["upper_arm_r"].angle = 80
        self.bones["lower_arm_l"].angle = 95
        self.bones["lower_arm_r"].angle = 85
        self.bones["hand_l"].angle = 90
        self.bones["hand_r"].angle = 90

    def _apply_holding_pose(self):
        """Hands together in front, holding something."""
        self.bones["upper_arm_l"].angle = 45
        self.bones["upper_arm_r"].angle = 135
        self.bones["lower_arm_l"].angle = -30
        self.bones["lower_arm_r"].angle = 210
        self.bones["hand_l"].angle = -45
        self.bones["hand_r"].angle = 225

    def _apply_arms_crossed_pose(self):
        """Arms folded across chest."""
        self.bones["upper_arm_l"].angle = 30
        self.bones["upper_arm_r"].angle = 150
        self.bones["lower_arm_l"].angle = -60
        self.bones["lower_arm_r"].angle = 240
        self.bones["hand_l"].angle = -60
        self.bones["hand_r"].angle = 240

    def _apply_hand_on_chest_pose(self):
        """One hand on chest, other relaxed."""
        self.bones["upper_arm_l"].angle = 100
        self.bones["upper_arm_r"].angle = 120
        self.bones["lower_arm_l"].angle = 95
        self.bones["lower_arm_r"].angle = 200
        self.bones["hand_l"].angle = 90
        self.bones["hand_r"].angle = 200

    def _apply_reading_pose(self):
        """Holding book/item up at reading angle."""
        self.bones["upper_arm_l"].angle = 60
        self.bones["upper_arm_r"].angle = 120
        self.bones["lower_arm_l"].angle = -20
        self.bones["lower_arm_r"].angle = 200
        self.bones["hand_l"].angle = -30
        self.bones["hand_r"].angle = 210

    def get_bone_positions(self, origin: Tuple[int, int]) -> Dict[str, Tuple[Tuple[int, int], Tuple[int, int]]]:
        """
        Calculate all bone start/end positions from origin.

        Returns:
            Dict mapping bone name to (start, end) positions
        """
        positions = {}

        def calc_bone(bone_name: str, parent_end: Tuple[float, float]) -> Tuple[Tuple[int, int], Tuple[int, int]]:
            bone = self.bones[bone_name]

            if bone.parent:
                # Position relative to parent end
                start = (
                    parent_end[0] + bone.base_position[0],
                    parent_end[1] + bone.base_position[1]
                )
            else:
                # Root bone
                start = (
                    origin[0] + bone.base_position[0],
                    origin[1] + bone.base_position[1]
                )

            end = bone.get_end_position(start)
            return ((int(start[0]), int(start[1])), (int(end[0]), int(end[1])))

        # Calculate in dependency order
        spine_pos = calc_bone("spine", (origin[0], origin[1]))
        positions["spine"] = spine_pos

        neck_pos = calc_bone("neck", spine_pos[0])
        positions["neck"] = neck_pos

        shoulder_l_pos = calc_bone("shoulder_l", spine_pos[0])
        positions["shoulder_l"] = shoulder_l_pos

        shoulder_r_pos = calc_bone("shoulder_r", spine_pos[0])
        positions["shoulder_r"] = shoulder_r_pos

        upper_arm_l_pos = calc_bone("upper_arm_l", shoulder_l_pos[1])
        positions["upper_arm_l"] = upper_arm_l_pos

        upper_arm_r_pos = calc_bone("upper_arm_r", shoulder_r_pos[1])
        positions["upper_arm_r"] = upper_arm_r_pos

        lower_arm_l_pos = calc_bone("lower_arm_l", upper_arm_l_pos[1])
        positions["lower_arm_l"] = lower_arm_l_pos

        lower_arm_r_pos = calc_bone("lower_arm_r", upper_arm_r_pos[1])
        positions["lower_arm_r"] = lower_arm_r_pos

        hand_l_pos = calc_bone("hand_l", lower_arm_l_pos[1])
        positions["hand_l"] = hand_l_pos

        hand_r_pos = calc_bone("hand_r", lower_arm_r_pos[1])
        positions["hand_r"] = hand_r_pos

        return positions


@dataclass
class BodyConfig:
    """Configuration for body rendering."""
    pose: BodyPose = BodyPose.NEUTRAL
    shoulder_width: float = 1.0      # Multiplier for shoulder width
    clothing_style: ClothingStyle = ClothingStyle.SIMPLE
    clothing_color: Tuple[int, int, int] = (255, 255, 255)
    skin_color: Tuple[int, int, int] = (232, 196, 168)
    arm_visible: bool = True
    use_rim_light: bool = True
    rim_light_color: Tuple[int, int, int] = (180, 200, 255)
    rim_light_intensity: float = 0.4


def render_body_base(
    canvas: Canvas,
    neck_base: Tuple[int, int],
    config: BodyConfig,
    canvas_height: int
) -> Dict[str, any]:
    """
    Render the base body shape (torso/clothing).

    Args:
        buffer: Target buffer
        neck_base: Position where neck meets body
        config: Body configuration
        canvas_height: Total canvas height for body extent

    Returns:
        Dict with body bounds and skeleton positions
    """
    # Create clothing color ramp
    clothing_ramp = create_hue_shifted_ramp(config.clothing_color, 6)

    # Calculate body dimensions
    shoulder_width = int(36 * config.shoulder_width)
    body_top = neck_base[1]
    body_bottom = canvas_height - 2
    body_height = body_bottom - body_top

    # Draw torso shape
    for y in range(body_top, body_bottom):
        # Progress from top to bottom
        t = (y - body_top) / max(1, body_height - 1)

        # Shoulder line at top, narrower at bottom
        if t < 0.15:
            # Neck to shoulder transition
            width_t = t / 0.15
            half_width = int(6 + (shoulder_width // 2 - 6) * width_t)
        elif t < 0.3:
            # Full shoulder width
            half_width = shoulder_width // 2
        else:
            # Taper toward waist
            taper_t = (t - 0.3) / 0.7
            half_width = int(shoulder_width // 2 - taper_t * 4)

        # Determine shading level
        shade_level = 3  # Base color

        # Side shading
        for x in range(neck_base[0] - half_width, neck_base[0] + half_width + 1):
            if 0 <= x < canvas.width and 0 <= y < canvas.height:
                # Distance from center for side shading
                dist_from_center = abs(x - neck_base[0]) / max(1, half_width)

                if dist_from_center > 0.85:
                    # Edge - rim light or shadow
                    if config.use_rim_light and dist_from_center > 0.92:
                        color = _blend_rim_light(
                            clothing_ramp[4],
                            config.rim_light_color,
                            config.rim_light_intensity
                        )
                    else:
                        color = clothing_ramp[2]  # Shadow
                elif dist_from_center > 0.6:
                    color = clothing_ramp[2]  # Shadow
                elif dist_from_center < 0.3 and t < 0.5:
                    color = clothing_ramp[4]  # Highlight
                else:
                    color = clothing_ramp[3]  # Base

                canvas.set_pixel(x, y, color)

    # Add clothing details based on style
    if config.clothing_style == ClothingStyle.COLLAR:
        _draw_collar(buffer, neck_base, shoulder_width, clothing_ramp)
    elif config.clothing_style == ClothingStyle.UNIFORM:
        _draw_collar(buffer, neck_base, shoulder_width, clothing_ramp)
        _draw_uniform_details(buffer, neck_base, shoulder_width, clothing_ramp)

    # Create skeleton and apply pose
    skeleton = Skeleton()
    skeleton.apply_pose(config.pose)
    positions = skeleton.get_bone_positions(neck_base)

    return {
        "shoulder_width": shoulder_width,
        "body_top": body_top,
        "body_bottom": body_bottom,
        "skeleton_positions": positions
    }


def render_neck(
    canvas: Canvas,
    neck_base: Tuple[int, int],
    neck_top: Tuple[int, int],
    skin_color: Tuple[int, int, int],
    use_rim_light: bool = True,
    rim_light_color: Tuple[int, int, int] = (180, 200, 255)
):
    """
    Render the neck connecting head to body.

    Args:
        buffer: Target buffer
        neck_base: Bottom of neck (body connection)
        neck_top: Top of neck (chin connection)
        skin_color: Base skin color
        use_rim_light: Whether to apply rim lighting
        rim_light_color: Color for rim light
    """
    skin_ramp = create_hue_shifted_ramp(skin_color, 6)

    neck_width_base = 10
    neck_width_top = 8

    for y in range(neck_top[1], neck_base[1] + 1):
        t = (y - neck_top[1]) / max(1, neck_base[1] - neck_top[1])
        half_width = int(neck_width_top + (neck_width_base - neck_width_top) * t) // 2

        for x in range(neck_base[0] - half_width, neck_base[0] + half_width + 1):
            if 0 <= x < canvas.width and 0 <= y < canvas.height:
                dist_from_center = abs(x - neck_base[0]) / max(1, half_width)

                if dist_from_center > 0.8:
                    if use_rim_light and dist_from_center > 0.9:
                        color = _blend_rim_light(skin_ramp[4], rim_light_color, 0.3)
                    else:
                        color = skin_ramp[2]  # Shadow
                else:
                    color = skin_ramp[3]  # Base

                canvas.set_pixel(x, y, color)


def render_arms(
    canvas: Canvas,
    skeleton_positions: Dict[str, Tuple[Tuple[int, int], Tuple[int, int]]],
    config: BodyConfig,
    foreground_only: bool = False
) -> None:
    """
    Render arms based on skeleton positions.

    Args:
        buffer: Target buffer
        skeleton_positions: Bone positions from skeleton
        config: Body configuration
        foreground_only: If True, only render foreground arms
    """
    if not config.arm_visible:
        return

    skin_ramp = create_hue_shifted_ramp(config.skin_color, 6)
    clothing_ramp = create_hue_shifted_ramp(config.clothing_color, 6)

    # Determine which arms are foreground based on pose
    left_foreground = config.pose in [BodyPose.ARMS_CROSSED, BodyPose.HAND_ON_CHEST]
    right_foreground = config.pose in [BodyPose.HOLDING, BodyPose.READING, BodyPose.ARMS_CROSSED]

    # Draw arms (order based on foreground status)
    arms_to_draw = []

    if not foreground_only:
        # Background arms first
        if not left_foreground:
            arms_to_draw.append(("l", skin_ramp, clothing_ramp))
        if not right_foreground:
            arms_to_draw.append(("r", skin_ramp, clothing_ramp))

    if foreground_only:
        # Foreground arms
        if left_foreground:
            arms_to_draw.append(("l", skin_ramp, clothing_ramp))
        if right_foreground:
            arms_to_draw.append(("r", skin_ramp, clothing_ramp))

    for side, skin, clothing in arms_to_draw:
        # Upper arm (clothing)
        upper_start, upper_end = skeleton_positions[f"upper_arm_{side}"]
        _draw_limb_segment(canvas, upper_start, upper_end, 5, 4, clothing, config)

        # Lower arm (skin)
        lower_start, lower_end = skeleton_positions[f"lower_arm_{side}"]
        _draw_limb_segment(canvas, lower_start, lower_end, 4, 3, skin, config)

        # Hand
        hand_start, hand_end = skeleton_positions[f"hand_{side}"]
        _draw_hand(canvas, hand_start, hand_end, skin, config)


def _draw_limb_segment(
    canvas: Canvas,
    start: Tuple[int, int],
    end: Tuple[int, int],
    width_start: int,
    width_end: int,
    color_ramp: List[Tuple[int, int, int, int]],
    config: BodyConfig
):
    """Draw a limb segment (arm/leg part)."""
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    length = max(1, int(math.sqrt(dx*dx + dy*dy)))

    for i in range(length + 1):
        t = i / max(1, length)
        x = int(start[0] + dx * t)
        y = int(start[1] + dy * t)
        width = int(width_start + (width_end - width_start) * t)

        # Draw cross-section perpendicular to limb direction
        perp_x = -dy / max(1, length)
        perp_y = dx / max(1, length)

        for w in range(-width, width + 1):
            px = int(x + perp_x * w)
            py = int(y + perp_y * w)

            if 0 <= px < canvas.width and 0 <= py < canvas.height:
                dist = abs(w) / max(1, width)

                if dist > 0.8:
                    if config.use_rim_light and dist > 0.9:
                        color = _blend_rim_light(color_ramp[4], config.rim_light_color, config.rim_light_intensity)
                    else:
                        color = color_ramp[2]
                elif dist < 0.3:
                    color = color_ramp[4]
                else:
                    color = color_ramp[3]

                canvas.set_pixel(px, py, color)


def _draw_hand(
    canvas: Canvas,
    wrist: Tuple[int, int],
    fingertip: Tuple[int, int],
    skin_ramp: List[Tuple[int, int, int, int]],
    config: BodyConfig
):
    """Draw a simplified anime hand."""
    # Simple hand shape - palm and fingers suggestion
    dx = fingertip[0] - wrist[0]
    dy = fingertip[1] - wrist[1]
    length = max(1, int(math.sqrt(dx*dx + dy*dy)))

    # Palm
    palm_center = (
        wrist[0] + dx * 0.4,
        wrist[1] + dy * 0.4
    )
    palm_radius = 4

    for py in range(int(palm_center[1]) - palm_radius, int(palm_center[1]) + palm_radius + 1):
        for px in range(int(palm_center[0]) - palm_radius, int(palm_center[0]) + palm_radius + 1):
            if 0 <= px < canvas.width and 0 <= py < canvas.height:
                dist = math.sqrt((px - palm_center[0])**2 + (py - palm_center[1])**2)
                if dist <= palm_radius:
                    rel_dist = dist / palm_radius
                    if rel_dist > 0.7:
                        color = skin_ramp[2]
                    elif rel_dist < 0.3:
                        color = skin_ramp[4]
                    else:
                        color = skin_ramp[3]
                    canvas.set_pixel(px, py, color)

    # Fingers (simplified as extension)
    for i in range(length // 2):
        t = 0.6 + (i / max(1, length // 2)) * 0.4
        fx = int(wrist[0] + dx * t)
        fy = int(wrist[1] + dy * t)

        if 0 <= fx < canvas.width and 0 <= fy < canvas.height:
            canvas.set_pixel(fx, fy, skin_ramp[3])


def _draw_collar(
    canvas: Canvas,
    neck_base: Tuple[int, int],
    shoulder_width: int,
    color_ramp: List[Tuple[int, int, int, int]]
):
    """Draw collar detail."""
    collar_y = neck_base[1] + 2
    collar_width = 8

    # Left collar
    for i in range(collar_width):
        x = neck_base[0] - 3 - i
        y = collar_y + i // 2
        if 0 <= x < canvas.width and 0 <= y < canvas.height:
            color = color_ramp[4] if i < collar_width // 2 else color_ramp[2]
            canvas.set_pixel(x, y, color)

    # Right collar
    for i in range(collar_width):
        x = neck_base[0] + 3 + i
        y = collar_y + i // 2
        if 0 <= x < canvas.width and 0 <= y < canvas.height:
            color = color_ramp[4] if i < collar_width // 2 else color_ramp[2]
            canvas.set_pixel(x, y, color)


def _draw_uniform_details(
    canvas: Canvas,
    neck_base: Tuple[int, int],
    shoulder_width: int,
    color_ramp: List[Tuple[int, int, int, int]]
):
    """Draw uniform-style details (buttons, seams)."""
    # Center seam
    for y in range(neck_base[1] + 8, neck_base[1] + 30):
        if 0 <= y < canvas.height:
            canvas.set_pixel(neck_base[0], y, color_ramp[2])

    # Buttons
    for i in range(3):
        button_y = neck_base[1] + 12 + i * 6
        if 0 <= button_y < canvas.height:
            canvas.set_pixel(neck_base[0], button_y, color_ramp[5])


def _blend_rim_light(
    base_color: Tuple[int, int, int, int],
    rim_color: Tuple[int, int, int],
    intensity: float
) -> Tuple[int, int, int, int]:
    """Blend rim light color into base color."""
    return (
        int(base_color[0] * (1 - intensity) + rim_color[0] * intensity),
        int(base_color[1] * (1 - intensity) + rim_color[1] * intensity),
        int(base_color[2] * (1 - intensity) + rim_color[2] * intensity),
        base_color[3]
    )


def get_hand_position(
    skeleton_positions: Dict[str, Tuple[Tuple[int, int], Tuple[int, int]]],
    hand: str = "r"
) -> Tuple[int, int]:
    """
    Get the center position of a hand for prop attachment.

    Args:
        skeleton_positions: Bone positions from skeleton
        hand: "l" for left, "r" for right

    Returns:
        (x, y) center of hand
    """
    hand_start, hand_end = skeleton_positions[f"hand_{hand}"]
    return (
        (hand_start[0] + hand_end[0]) // 2,
        (hand_start[1] + hand_end[1]) // 2
    )

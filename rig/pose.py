"""
Pose - Pose definitions and interpolation for character animation.

Provides named poses, pose blending, and preset poses for common
character states (idle, walk, attack, etc.).
"""

import math
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field


@dataclass
class Pose:
    """A named pose storing bone rotations and positions.

    Poses store the transform values for bones that differ from
    the default/rest pose. Bones not specified use their default values.
    """

    name: str

    # Bone transforms (bone_name -> value)
    rotations: Dict[str, float] = field(default_factory=dict)  # Radians
    positions: Dict[str, Tuple[float, float]] = field(default_factory=dict)
    scales: Dict[str, float] = field(default_factory=dict)
    visibility: Dict[str, bool] = field(default_factory=dict)

    # Animation hints
    duration: float = 1.0  # Default duration when used in animation
    easing: str = 'linear'  # Easing function for transitions

    def set_rotation(self, bone_name: str, radians: float) -> 'Pose':
        """Set rotation for a bone in radians."""
        self.rotations[bone_name] = radians
        return self

    def set_rotation_degrees(self, bone_name: str, degrees: float) -> 'Pose':
        """Set rotation for a bone in degrees."""
        self.rotations[bone_name] = math.radians(degrees)
        return self

    def set_position(self, bone_name: str, x: float, y: float) -> 'Pose':
        """Set position for a bone."""
        self.positions[bone_name] = (x, y)
        return self

    def set_scale(self, bone_name: str, scale: float) -> 'Pose':
        """Set scale for a bone."""
        self.scales[bone_name] = scale
        return self

    def set_visible(self, bone_name: str, visible: bool) -> 'Pose':
        """Set visibility for a bone."""
        self.visibility[bone_name] = visible
        return self

    def get_rotation(self, bone_name: str, default: float = 0.0) -> float:
        """Get rotation for a bone (radians)."""
        return self.rotations.get(bone_name, default)

    def get_rotation_degrees(self, bone_name: str, default: float = 0.0) -> float:
        """Get rotation for a bone (degrees)."""
        return math.degrees(self.rotations.get(bone_name, math.radians(default)))

    def copy(self) -> 'Pose':
        """Create a copy of this pose."""
        return Pose(
            name=f"{self.name}_copy",
            rotations=self.rotations.copy(),
            positions=self.positions.copy(),
            scales=self.scales.copy(),
            visibility=self.visibility.copy(),
            duration=self.duration,
            easing=self.easing
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize pose to dictionary."""
        return {
            'name': self.name,
            'rotations': {k: math.degrees(v) for k, v in self.rotations.items()},
            'positions': self.positions,
            'scales': self.scales,
            'visibility': self.visibility,
            'duration': self.duration,
            'easing': self.easing
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Pose':
        """Create pose from dictionary."""
        return cls(
            name=data.get('name', 'unnamed'),
            rotations={k: math.radians(v) for k, v in data.get('rotations', {}).items()},
            positions={k: tuple(v) for k, v in data.get('positions', {}).items()},
            scales=data.get('scales', {}),
            visibility=data.get('visibility', {}),
            duration=data.get('duration', 1.0),
            easing=data.get('easing', 'linear')
        )


# =============================================================================
# Pose Interpolation
# =============================================================================

def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation."""
    return a + (b - a) * t


def lerp_angle(a: float, b: float, t: float) -> float:
    """Interpolate between angles, taking shortest path."""
    # Normalize to -pi to pi
    diff = b - a
    while diff > math.pi:
        diff -= 2 * math.pi
    while diff < -math.pi:
        diff += 2 * math.pi
    return a + diff * t


def apply_easing(t: float, easing: str) -> float:
    """Apply easing function to interpolation factor.

    Args:
        t: Linear factor 0-1
        easing: Easing function name

    Returns:
        Eased factor 0-1
    """
    t = max(0.0, min(1.0, t))

    if easing == 'linear':
        return t

    elif easing == 'ease_in':
        return t * t

    elif easing == 'ease_out':
        return 1 - (1 - t) * (1 - t)

    elif easing == 'ease_in_out':
        if t < 0.5:
            return 2 * t * t
        else:
            return 1 - (-2 * t + 2) ** 2 / 2

    elif easing == 'ease_in_cubic':
        return t * t * t

    elif easing == 'ease_out_cubic':
        return 1 - (1 - t) ** 3

    elif easing == 'ease_in_out_cubic':
        if t < 0.5:
            return 4 * t * t * t
        else:
            return 1 - (-2 * t + 2) ** 3 / 2

    elif easing == 'bounce':
        if t < 1 / 2.75:
            return 7.5625 * t * t
        elif t < 2 / 2.75:
            t -= 1.5 / 2.75
            return 7.5625 * t * t + 0.75
        elif t < 2.5 / 2.75:
            t -= 2.25 / 2.75
            return 7.5625 * t * t + 0.9375
        else:
            t -= 2.625 / 2.75
            return 7.5625 * t * t + 0.984375

    elif easing == 'elastic':
        if t == 0 or t == 1:
            return t
        return -math.pow(2, 10 * t - 10) * math.sin((t * 10 - 10.75) * (2 * math.pi) / 3)

    return t


def blend_poses(pose_a: Pose, pose_b: Pose, t: float, easing: str = 'linear') -> Pose:
    """Blend between two poses.

    Args:
        pose_a: Starting pose
        pose_b: Ending pose
        t: Blend factor 0-1 (0=pose_a, 1=pose_b)
        easing: Easing function name

    Returns:
        New pose with blended values
    """
    t = apply_easing(t, easing)

    result = Pose(name=f"{pose_a.name}_to_{pose_b.name}")

    # Blend rotations
    all_bones = set(pose_a.rotations.keys()) | set(pose_b.rotations.keys())
    for bone in all_bones:
        rot_a = pose_a.rotations.get(bone, 0.0)
        rot_b = pose_b.rotations.get(bone, 0.0)
        result.rotations[bone] = lerp_angle(rot_a, rot_b, t)

    # Blend positions
    all_pos_bones = set(pose_a.positions.keys()) | set(pose_b.positions.keys())
    for bone in all_pos_bones:
        pos_a = pose_a.positions.get(bone, (0, 0))
        pos_b = pose_b.positions.get(bone, (0, 0))
        result.positions[bone] = (
            lerp(pos_a[0], pos_b[0], t),
            lerp(pos_a[1], pos_b[1], t)
        )

    # Blend scales
    all_scale_bones = set(pose_a.scales.keys()) | set(pose_b.scales.keys())
    for bone in all_scale_bones:
        scale_a = pose_a.scales.get(bone, 1.0)
        scale_b = pose_b.scales.get(bone, 1.0)
        result.scales[bone] = lerp(scale_a, scale_b, t)

    # Visibility: use pose_b's value if t > 0.5
    if t > 0.5:
        result.visibility = pose_b.visibility.copy()
    else:
        result.visibility = pose_a.visibility.copy()

    return result


def blend_multiple_poses(poses: List[Tuple[Pose, float]]) -> Pose:
    """Blend multiple poses with weights.

    Args:
        poses: List of (pose, weight) tuples

    Returns:
        Blended pose
    """
    if not poses:
        return Pose(name="empty")

    if len(poses) == 1:
        return poses[0][0].copy()

    # Normalize weights
    total_weight = sum(w for _, w in poses)
    if total_weight == 0:
        return poses[0][0].copy()

    result = Pose(name="blended")

    # Collect all bones
    all_rot_bones = set()
    all_pos_bones = set()
    all_scale_bones = set()

    for pose, _ in poses:
        all_rot_bones.update(pose.rotations.keys())
        all_pos_bones.update(pose.positions.keys())
        all_scale_bones.update(pose.scales.keys())

    # Blend rotations (weighted average using sin/cos for angles)
    for bone in all_rot_bones:
        sin_sum = 0.0
        cos_sum = 0.0
        for pose, weight in poses:
            rot = pose.rotations.get(bone, 0.0)
            w = weight / total_weight
            sin_sum += math.sin(rot) * w
            cos_sum += math.cos(rot) * w
        result.rotations[bone] = math.atan2(sin_sum, cos_sum)

    # Blend positions
    for bone in all_pos_bones:
        x_sum = 0.0
        y_sum = 0.0
        for pose, weight in poses:
            pos = pose.positions.get(bone, (0, 0))
            w = weight / total_weight
            x_sum += pos[0] * w
            y_sum += pos[1] * w
        result.positions[bone] = (x_sum, y_sum)

    # Blend scales
    for bone in all_scale_bones:
        scale_sum = 0.0
        for pose, weight in poses:
            scale = pose.scales.get(bone, 1.0)
            w = weight / total_weight
            scale_sum += scale * w
        result.scales[bone] = scale_sum

    return result


# =============================================================================
# Pose Library
# =============================================================================

class PoseLibrary:
    """Collection of named poses for a character."""

    def __init__(self, name: str = "poses"):
        self.name = name
        self.poses: Dict[str, Pose] = {}

    def add(self, pose: Pose) -> None:
        """Add a pose to the library."""
        self.poses[pose.name] = pose

    def get(self, name: str) -> Optional[Pose]:
        """Get a pose by name."""
        return self.poses.get(name)

    def create(self, name: str) -> Pose:
        """Create and add a new empty pose."""
        pose = Pose(name=name)
        self.poses[name] = pose
        return pose

    def remove(self, name: str) -> bool:
        """Remove a pose by name."""
        if name in self.poses:
            del self.poses[name]
            return True
        return False

    def list_poses(self) -> List[str]:
        """Get list of pose names."""
        return list(self.poses.keys())

    def to_dict(self) -> Dict[str, Any]:
        """Serialize library to dictionary."""
        return {
            'name': self.name,
            'poses': [pose.to_dict() for pose in self.poses.values()]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PoseLibrary':
        """Create library from dictionary."""
        lib = cls(data.get('name', 'poses'))
        for pose_data in data.get('poses', []):
            lib.add(Pose.from_dict(pose_data))
        return lib


# =============================================================================
# Preset Poses
# =============================================================================

def create_chibi_poses() -> PoseLibrary:
    """Create common poses for chibi characters."""
    lib = PoseLibrary("chibi_poses")

    # Rest/default pose
    rest = Pose(name="rest")
    lib.add(rest)

    # Idle pose (slight variations for breathing)
    idle_1 = Pose(name="idle_1", duration=0.5)
    idle_1.set_rotation_degrees("spine", 2)
    idle_1.set_rotation_degrees("head", -2)
    lib.add(idle_1)

    idle_2 = Pose(name="idle_2", duration=0.5)
    idle_2.set_rotation_degrees("spine", -2)
    idle_2.set_rotation_degrees("head", 2)
    lib.add(idle_2)

    # Walk cycle poses
    walk_1 = Pose(name="walk_1", duration=0.15)
    walk_1.set_rotation_degrees("leg_l", 110)  # Forward
    walk_1.set_rotation_degrees("leg_r", 70)   # Back
    walk_1.set_rotation_degrees("arm_l", -30)  # Opposite to legs
    walk_1.set_rotation_degrees("arm_r", 60)
    walk_1.set_rotation_degrees("spine", 5)
    lib.add(walk_1)

    walk_2 = Pose(name="walk_2", duration=0.15)
    walk_2.set_rotation_degrees("leg_l", 90)
    walk_2.set_rotation_degrees("leg_r", 90)
    walk_2.set_rotation_degrees("arm_l", -45)
    walk_2.set_rotation_degrees("arm_r", 45)
    lib.add(walk_2)

    walk_3 = Pose(name="walk_3", duration=0.15)
    walk_3.set_rotation_degrees("leg_l", 70)   # Back
    walk_3.set_rotation_degrees("leg_r", 110)  # Forward
    walk_3.set_rotation_degrees("arm_l", 60)
    walk_3.set_rotation_degrees("arm_r", -30)
    walk_3.set_rotation_degrees("spine", -5)
    lib.add(walk_3)

    walk_4 = Pose(name="walk_4", duration=0.15)
    walk_4.set_rotation_degrees("leg_l", 90)
    walk_4.set_rotation_degrees("leg_r", 90)
    walk_4.set_rotation_degrees("arm_l", 45)
    walk_4.set_rotation_degrees("arm_r", -45)
    lib.add(walk_4)

    # Attack pose
    attack_wind = Pose(name="attack_wind", duration=0.1)
    attack_wind.set_rotation_degrees("arm_r", -60)
    attack_wind.set_rotation_degrees("spine", -10)
    lib.add(attack_wind)

    attack_swing = Pose(name="attack_swing", duration=0.1, easing='ease_out')
    attack_swing.set_rotation_degrees("arm_r", 120)
    attack_swing.set_rotation_degrees("spine", 15)
    lib.add(attack_swing)

    # Hurt pose
    hurt = Pose(name="hurt", duration=0.2, easing='bounce')
    hurt.set_rotation_degrees("spine", -15)
    hurt.set_rotation_degrees("head", 10)
    hurt.set_rotation_degrees("arm_l", -20)
    hurt.set_rotation_degrees("arm_r", 100)
    lib.add(hurt)

    # Jump poses
    jump_up = Pose(name="jump_up", duration=0.15)
    jump_up.set_rotation_degrees("leg_l", 60)
    jump_up.set_rotation_degrees("leg_r", 60)
    jump_up.set_rotation_degrees("arm_l", -70)
    jump_up.set_rotation_degrees("arm_r", 70)
    lib.add(jump_up)

    jump_fall = Pose(name="jump_fall", duration=0.2)
    jump_fall.set_rotation_degrees("leg_l", 100)
    jump_fall.set_rotation_degrees("leg_r", 100)
    jump_fall.set_rotation_degrees("arm_l", -30)
    jump_fall.set_rotation_degrees("arm_r", 30)
    lib.add(jump_fall)

    # Crouch pose
    crouch = Pose(name="crouch", duration=0.2)
    crouch.set_rotation_degrees("spine", 20)
    crouch.set_rotation_degrees("leg_l", 45)
    crouch.set_rotation_degrees("leg_r", 135)
    crouch.set_position("root", 0, 4)  # Lower body
    lib.add(crouch)

    return lib


def create_humanoid_poses() -> PoseLibrary:
    """Create common poses for humanoid characters."""
    lib = PoseLibrary("humanoid_poses")

    # Rest pose
    rest = Pose(name="rest")
    lib.add(rest)

    # Idle variations
    idle_1 = Pose(name="idle_1", duration=0.8)
    idle_1.set_rotation_degrees("spine_upper", 2)
    idle_1.set_rotation_degrees("head", -1)
    lib.add(idle_1)

    idle_2 = Pose(name="idle_2", duration=0.8)
    idle_2.set_rotation_degrees("spine_upper", -2)
    idle_2.set_rotation_degrees("head", 1)
    lib.add(idle_2)

    # Walk cycle
    walk_1 = Pose(name="walk_1", duration=0.2)
    walk_1.set_rotation_degrees("leg_upper_l", 110)
    walk_1.set_rotation_degrees("leg_lower_l", 20)
    walk_1.set_rotation_degrees("leg_upper_r", 70)
    walk_1.set_rotation_degrees("leg_lower_r", -20)
    walk_1.set_rotation_degrees("arm_upper_l", 70)
    walk_1.set_rotation_degrees("arm_upper_r", 110)
    lib.add(walk_1)

    walk_2 = Pose(name="walk_2", duration=0.2)
    walk_2.set_rotation_degrees("leg_upper_l", 90)
    walk_2.set_rotation_degrees("leg_lower_l", 0)
    walk_2.set_rotation_degrees("leg_upper_r", 90)
    walk_2.set_rotation_degrees("leg_lower_r", 0)
    walk_2.set_rotation_degrees("arm_upper_l", 90)
    walk_2.set_rotation_degrees("arm_upper_r", 90)
    lib.add(walk_2)

    walk_3 = Pose(name="walk_3", duration=0.2)
    walk_3.set_rotation_degrees("leg_upper_l", 70)
    walk_3.set_rotation_degrees("leg_lower_l", -20)
    walk_3.set_rotation_degrees("leg_upper_r", 110)
    walk_3.set_rotation_degrees("leg_lower_r", 20)
    walk_3.set_rotation_degrees("arm_upper_l", 110)
    walk_3.set_rotation_degrees("arm_upper_r", 70)
    lib.add(walk_3)

    walk_4 = Pose(name="walk_4", duration=0.2)
    walk_4.set_rotation_degrees("leg_upper_l", 90)
    walk_4.set_rotation_degrees("leg_lower_l", 0)
    walk_4.set_rotation_degrees("leg_upper_r", 90)
    walk_4.set_rotation_degrees("leg_lower_r", 0)
    walk_4.set_rotation_degrees("arm_upper_l", 90)
    walk_4.set_rotation_degrees("arm_upper_r", 90)
    lib.add(walk_4)

    return lib


# Pose library presets
POSE_LIBRARY_PRESETS = {
    'chibi': create_chibi_poses,
    'humanoid': create_humanoid_poses,
}


def create_pose_library(preset: str) -> PoseLibrary:
    """Create a pose library from a preset.

    Args:
        preset: Preset name ('chibi', 'humanoid')

    Returns:
        PoseLibrary with common poses
    """
    if preset not in POSE_LIBRARY_PRESETS:
        available = ', '.join(POSE_LIBRARY_PRESETS.keys())
        raise ValueError(f"Unknown pose library preset '{preset}'. Available: {available}")

    return POSE_LIBRARY_PRESETS[preset]()

"""
Skeleton - Bone hierarchy for character rigging.

Provides a skeletal system for posing and animating characters.
Bones form a parent-child hierarchy where child transforms are
relative to their parent.
"""

import math
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field


@dataclass
class Bone:
    """A single bone in a skeleton hierarchy.

    Bones have a position and rotation relative to their parent.
    The world transform is computed by traversing up the hierarchy.
    """

    name: str
    parent: Optional['Bone'] = None
    children: List['Bone'] = field(default_factory=list)

    # Local transform (relative to parent)
    local_x: float = 0.0
    local_y: float = 0.0
    local_rotation: float = 0.0  # Radians
    local_scale: float = 1.0

    # Bone properties
    length: float = 10.0  # Length of bone (for visualization/IK)

    # Rendering hints
    z_order: int = 0  # Draw order (higher = on top)
    flip_x: bool = False  # Mirror horizontally
    visible: bool = True

    def add_child(self, child: 'Bone') -> 'Bone':
        """Add a child bone."""
        child.parent = self
        self.children.append(child)
        return child

    def get_world_transform(self) -> Tuple[float, float, float, float]:
        """Get world position, rotation, and scale.

        Returns:
            (world_x, world_y, world_rotation, world_scale)
        """
        if self.parent is None:
            return (self.local_x, self.local_y, self.local_rotation, self.local_scale)

        # Get parent's world transform
        px, py, pr, ps = self.parent.get_world_transform()

        # Apply local transform relative to parent
        cos_r = math.cos(pr)
        sin_r = math.sin(pr)

        # Rotate local position by parent rotation
        world_x = px + (self.local_x * cos_r - self.local_y * sin_r) * ps
        world_y = py + (self.local_x * sin_r + self.local_y * cos_r) * ps
        world_rotation = pr + self.local_rotation
        world_scale = ps * self.local_scale

        return (world_x, world_y, world_rotation, world_scale)

    def get_world_position(self) -> Tuple[float, float]:
        """Get world position only."""
        x, y, _, _ = self.get_world_transform()
        return (x, y)

    def get_end_position(self) -> Tuple[float, float]:
        """Get the position of the bone's tip (end point)."""
        x, y, r, s = self.get_world_transform()
        end_x = x + math.cos(r) * self.length * s
        end_y = y + math.sin(r) * self.length * s
        return (end_x, end_y)

    def set_rotation_degrees(self, degrees: float) -> None:
        """Set local rotation in degrees."""
        self.local_rotation = math.radians(degrees)

    def get_rotation_degrees(self) -> float:
        """Get local rotation in degrees."""
        return math.degrees(self.local_rotation)

    def rotate(self, delta_radians: float) -> None:
        """Add to current rotation."""
        self.local_rotation += delta_radians

    def rotate_degrees(self, delta_degrees: float) -> None:
        """Add to current rotation in degrees."""
        self.local_rotation += math.radians(delta_degrees)

    def copy(self) -> 'Bone':
        """Create a shallow copy (without parent/children links)."""
        return Bone(
            name=self.name,
            local_x=self.local_x,
            local_y=self.local_y,
            local_rotation=self.local_rotation,
            local_scale=self.local_scale,
            length=self.length,
            z_order=self.z_order,
            flip_x=self.flip_x,
            visible=self.visible
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize bone to dictionary."""
        return {
            'name': self.name,
            'local_x': self.local_x,
            'local_y': self.local_y,
            'local_rotation': self.local_rotation,
            'local_scale': self.local_scale,
            'length': self.length,
            'z_order': self.z_order,
            'flip_x': self.flip_x,
            'visible': self.visible,
            'parent': self.parent.name if self.parent else None,
        }


class Skeleton:
    """A complete skeleton with bone hierarchy.

    The skeleton manages a tree of bones and provides methods for
    posing, querying transforms, and animation.
    """

    def __init__(self, name: str = "skeleton"):
        self.name = name
        self.root: Optional[Bone] = None
        self.bones: Dict[str, Bone] = {}

    def create_bone(self, name: str, parent_name: Optional[str] = None,
                    x: float = 0, y: float = 0, rotation: float = 0,
                    length: float = 10, z_order: int = 0) -> Bone:
        """Create and add a new bone.

        Args:
            name: Unique bone name
            parent_name: Name of parent bone (None for root)
            x, y: Local position relative to parent
            rotation: Local rotation in radians
            length: Bone length
            z_order: Draw order

        Returns:
            The created bone
        """
        bone = Bone(
            name=name,
            local_x=x,
            local_y=y,
            local_rotation=rotation,
            length=length,
            z_order=z_order
        )

        if parent_name is None:
            if self.root is None:
                self.root = bone
            else:
                raise ValueError("Skeleton already has a root bone")
        else:
            parent = self.bones.get(parent_name)
            if parent is None:
                raise ValueError(f"Parent bone '{parent_name}' not found")
            parent.add_child(bone)

        self.bones[name] = bone
        return bone

    def get_bone(self, name: str) -> Optional[Bone]:
        """Get a bone by name."""
        return self.bones.get(name)

    def set_bone_rotation(self, name: str, rotation: float) -> None:
        """Set a bone's local rotation in radians."""
        bone = self.bones.get(name)
        if bone:
            bone.local_rotation = rotation

    def set_bone_rotation_degrees(self, name: str, degrees: float) -> None:
        """Set a bone's local rotation in degrees."""
        bone = self.bones.get(name)
        if bone:
            bone.set_rotation_degrees(degrees)

    def set_bone_position(self, name: str, x: float, y: float) -> None:
        """Set a bone's local position."""
        bone = self.bones.get(name)
        if bone:
            bone.local_x = x
            bone.local_y = y

    def get_world_position(self, name: str) -> Optional[Tuple[float, float]]:
        """Get a bone's world position."""
        bone = self.bones.get(name)
        if bone:
            return bone.get_world_position()
        return None

    def get_bones_by_z_order(self) -> List[Bone]:
        """Get all bones sorted by z_order (for rendering)."""
        return sorted(self.bones.values(), key=lambda b: b.z_order)

    def get_visible_bones_by_z_order(self) -> List[Bone]:
        """Get visible bones sorted by z_order."""
        return sorted(
            [b for b in self.bones.values() if b.visible],
            key=lambda b: b.z_order
        )

    def reset_pose(self) -> None:
        """Reset all bones to default pose (zero rotation)."""
        for bone in self.bones.values():
            bone.local_rotation = 0.0

    def apply_pose(self, pose: Dict[str, float]) -> None:
        """Apply a pose (bone name -> rotation in radians).

        Args:
            pose: Dictionary mapping bone names to rotation values
        """
        for name, rotation in pose.items():
            self.set_bone_rotation(name, rotation)

    def apply_pose_degrees(self, pose: Dict[str, float]) -> None:
        """Apply a pose with rotations in degrees."""
        for name, degrees in pose.items():
            self.set_bone_rotation_degrees(name, degrees)

    def get_current_pose(self) -> Dict[str, float]:
        """Get current pose as bone name -> rotation dict."""
        return {name: bone.local_rotation for name, bone in self.bones.items()}

    def copy(self) -> 'Skeleton':
        """Create a deep copy of the skeleton."""
        new_skel = Skeleton(self.name)

        # Copy bones in hierarchy order (root first)
        def copy_bone_tree(bone: Bone, parent_name: Optional[str] = None):
            new_bone = new_skel.create_bone(
                name=bone.name,
                parent_name=parent_name,
                x=bone.local_x,
                y=bone.local_y,
                rotation=bone.local_rotation,
                length=bone.length,
                z_order=bone.z_order
            )
            new_bone.local_scale = bone.local_scale
            new_bone.flip_x = bone.flip_x
            new_bone.visible = bone.visible

            for child in bone.children:
                copy_bone_tree(child, bone.name)

        if self.root:
            copy_bone_tree(self.root)

        return new_skel

    def to_dict(self) -> Dict[str, Any]:
        """Serialize skeleton to dictionary."""
        return {
            'name': self.name,
            'bones': [bone.to_dict() for bone in self.bones.values()]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Skeleton':
        """Create skeleton from dictionary."""
        skel = cls(data.get('name', 'skeleton'))

        # First pass: create all bones without hierarchy
        bone_data_map = {b['name']: b for b in data.get('bones', [])}

        # Build in order (root first)
        def find_roots():
            return [b for b in data.get('bones', []) if b.get('parent') is None]

        def build_tree(bone_data: Dict, parent_name: Optional[str] = None):
            bone = skel.create_bone(
                name=bone_data['name'],
                parent_name=parent_name,
                x=bone_data.get('local_x', 0),
                y=bone_data.get('local_y', 0),
                rotation=bone_data.get('local_rotation', 0),
                length=bone_data.get('length', 10),
                z_order=bone_data.get('z_order', 0)
            )
            bone.local_scale = bone_data.get('local_scale', 1.0)
            bone.flip_x = bone_data.get('flip_x', False)
            bone.visible = bone_data.get('visible', True)

            # Find children
            for child_data in data.get('bones', []):
                if child_data.get('parent') == bone_data['name']:
                    build_tree(child_data, bone_data['name'])

        for root_data in find_roots():
            build_tree(root_data)

        return skel


# =============================================================================
# Preset Skeletons
# =============================================================================

def create_chibi_skeleton(base_x: float = 0, base_y: float = 0) -> Skeleton:
    """Create a chibi-style character skeleton.

    Chibi proportions: large head, small body, simple limbs.

    Bone structure:
        root (hips)
        ├── spine
        │   └── head
        │       ├── hair_back
        │       └── hair_front
        ├── arm_l
        │   └── hand_l
        ├── arm_r
        │   └── hand_r
        ├── leg_l
        │   └── foot_l
        └── leg_r
            └── foot_r
    """
    skel = Skeleton("chibi")

    # Root at hips
    skel.create_bone("root", None, base_x, base_y, 0, 0, z_order=0)

    # Spine and head (large head for chibi)
    skel.create_bone("spine", "root", 0, -4, 0, 6, z_order=5)
    skel.create_bone("head", "spine", 0, -6, 0, 12, z_order=10)

    # Hair layers
    skel.create_bone("hair_back", "head", 0, -2, 0, 8, z_order=8)
    skel.create_bone("hair_front", "head", 0, -4, 0, 6, z_order=15)

    # Arms (short for chibi)
    skel.create_bone("arm_l", "spine", -4, -2, math.radians(-45), 5, z_order=4)
    skel.create_bone("hand_l", "arm_l", 5, 0, 0, 3, z_order=4)

    skel.create_bone("arm_r", "spine", 4, -2, math.radians(45), 5, z_order=6)
    skel.create_bone("hand_r", "arm_r", 5, 0, 0, 3, z_order=6)

    # Legs (short stubs for chibi)
    skel.create_bone("leg_l", "root", -2, 2, math.radians(90), 4, z_order=2)
    skel.create_bone("foot_l", "leg_l", 4, 0, 0, 2, z_order=2)

    skel.create_bone("leg_r", "root", 2, 2, math.radians(90), 4, z_order=3)
    skel.create_bone("foot_r", "leg_r", 4, 0, 0, 2, z_order=3)

    return skel


def create_humanoid_skeleton(base_x: float = 0, base_y: float = 0) -> Skeleton:
    """Create a standard humanoid skeleton.

    More realistic proportions than chibi.

    Bone structure:
        root (hips)
        ├── spine_lower
        │   └── spine_upper
        │       ├── neck
        │       │   └── head
        │       ├── shoulder_l
        │       │   └── arm_upper_l
        │       │       └── arm_lower_l
        │       │           └── hand_l
        │       └── shoulder_r
        │           └── arm_upper_r
        │               └── arm_lower_r
        │                   └── hand_r
        ├── leg_upper_l
        │   └── leg_lower_l
        │       └── foot_l
        └── leg_upper_r
            └── leg_lower_r
                └── foot_r
    """
    skel = Skeleton("humanoid")

    # Root at hips
    skel.create_bone("root", None, base_x, base_y, 0, 0, z_order=0)

    # Spine
    skel.create_bone("spine_lower", "root", 0, -4, 0, 6, z_order=5)
    skel.create_bone("spine_upper", "spine_lower", 0, -6, 0, 6, z_order=5)

    # Neck and head
    skel.create_bone("neck", "spine_upper", 0, -6, 0, 3, z_order=6)
    skel.create_bone("head", "neck", 0, -3, 0, 8, z_order=10)

    # Left arm chain
    skel.create_bone("shoulder_l", "spine_upper", -6, -4, 0, 2, z_order=4)
    skel.create_bone("arm_upper_l", "shoulder_l", -2, 0, math.radians(90), 8, z_order=4)
    skel.create_bone("arm_lower_l", "arm_upper_l", 8, 0, 0, 7, z_order=4)
    skel.create_bone("hand_l", "arm_lower_l", 7, 0, 0, 4, z_order=4)

    # Right arm chain
    skel.create_bone("shoulder_r", "spine_upper", 6, -4, 0, 2, z_order=6)
    skel.create_bone("arm_upper_r", "shoulder_r", 2, 0, math.radians(90), 8, z_order=6)
    skel.create_bone("arm_lower_r", "arm_upper_r", 8, 0, 0, 7, z_order=6)
    skel.create_bone("hand_r", "arm_lower_r", 7, 0, 0, 4, z_order=6)

    # Left leg chain
    skel.create_bone("leg_upper_l", "root", -3, 2, math.radians(90), 10, z_order=2)
    skel.create_bone("leg_lower_l", "leg_upper_l", 10, 0, 0, 10, z_order=2)
    skel.create_bone("foot_l", "leg_lower_l", 10, 0, math.radians(-90), 4, z_order=2)

    # Right leg chain
    skel.create_bone("leg_upper_r", "root", 3, 2, math.radians(90), 10, z_order=3)
    skel.create_bone("leg_lower_r", "leg_upper_r", 10, 0, 0, 10, z_order=3)
    skel.create_bone("foot_r", "leg_lower_r", 10, 0, math.radians(-90), 4, z_order=3)

    return skel


def create_simple_skeleton(base_x: float = 0, base_y: float = 0) -> Skeleton:
    """Create a minimal skeleton for simple characters.

    Just root, body, head - useful for items or simple sprites.
    """
    skel = Skeleton("simple")

    skel.create_bone("root", None, base_x, base_y, 0, 0, z_order=0)
    skel.create_bone("body", "root", 0, -8, 0, 12, z_order=5)
    skel.create_bone("head", "body", 0, -12, 0, 8, z_order=10)

    return skel


# Skeleton type registry
SKELETON_PRESETS = {
    'chibi': create_chibi_skeleton,
    'humanoid': create_humanoid_skeleton,
    'simple': create_simple_skeleton,
}


def create_skeleton(preset: str, base_x: float = 0, base_y: float = 0) -> Skeleton:
    """Create a skeleton from a preset name.

    Args:
        preset: Preset name ('chibi', 'humanoid', 'simple')
        base_x, base_y: Base position for root bone

    Returns:
        Configured Skeleton instance
    """
    if preset not in SKELETON_PRESETS:
        available = ', '.join(SKELETON_PRESETS.keys())
        raise ValueError(f"Unknown skeleton preset '{preset}'. Available: {available}")

    return SKELETON_PRESETS[preset](base_x, base_y)

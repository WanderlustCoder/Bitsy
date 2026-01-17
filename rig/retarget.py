"""
Retarget - Animation retargeting between different skeleton types.

Allows animations created for one skeleton to be applied to characters
with different skeleton structures or proportions.
"""

import math
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field


@dataclass
class BoneMapping:
    """Defines how a source bone maps to target bone(s).

    Attributes:
        source: Source bone name
        targets: Target bone name(s) - can be one or multiple
        rotation_weights: How to distribute rotation across targets (sum to 1.0)
        position_scale: Scale factor for position offsets
    """

    source: str
    targets: List[str]
    rotation_weights: List[float] = field(default_factory=list)
    position_scale: float = 1.0

    def __post_init__(self):
        """Ensure rotation weights are valid."""
        if not self.rotation_weights:
            # Default to equal distribution
            self.rotation_weights = [1.0 / len(self.targets)] * len(self.targets)

        # Normalize weights to sum to 1.0
        total = sum(self.rotation_weights)
        if total > 0 and abs(total - 1.0) > 0.001:
            self.rotation_weights = [w / total for w in self.rotation_weights]


@dataclass
class SkeletonMapping:
    """Collection of bone mappings between two skeleton types.

    Attributes:
        name: Mapping name (e.g., "chibi_to_humanoid")
        source_type: Source skeleton type
        target_type: Target skeleton type
        bone_mappings: Dict of source bone name -> BoneMapping
        root_scale: Scale factor for root motion (x, y)
    """

    name: str
    source_type: str
    target_type: str
    bone_mappings: Dict[str, BoneMapping] = field(default_factory=dict)
    root_scale: Tuple[float, float] = (1.0, 1.0)

    def add_mapping(
        self,
        source: str,
        targets: List[str],
        rotation_weights: Optional[List[float]] = None,
        position_scale: float = 1.0
    ) -> 'SkeletonMapping':
        """Add a bone mapping.

        Args:
            source: Source bone name
            targets: Target bone name(s)
            rotation_weights: Distribution weights for rotation
            position_scale: Scale factor for positions

        Returns:
            Self for chaining
        """
        self.bone_mappings[source] = BoneMapping(
            source=source,
            targets=targets,
            rotation_weights=rotation_weights or [],
            position_scale=position_scale
        )
        return self

    def get_mapping(self, source_bone: str) -> Optional[BoneMapping]:
        """Get mapping for a source bone."""
        return self.bone_mappings.get(source_bone)

    def has_mapping(self, source_bone: str) -> bool:
        """Check if a mapping exists for source bone."""
        return source_bone in self.bone_mappings


@dataclass
class RetargetingConfig:
    """Configuration for retargeting behavior.

    Attributes:
        scale_positions: Whether to scale position offsets
        preserve_root_motion: Whether to keep root movement
        clamp_rotations: Whether to limit extreme angles
        rotation_limit: Maximum rotation in radians if clamping
    """

    scale_positions: bool = True
    preserve_root_motion: bool = True
    clamp_rotations: bool = False
    rotation_limit: float = 2.0  # ~115 degrees


def _clamp_rotation(rotation: float, limit: float) -> float:
    """Clamp rotation to within limit."""
    return max(-limit, min(limit, rotation))


def _distribute_rotation(
    rotation: float,
    weights: List[float],
    clamp: bool = False,
    limit: float = 2.0
) -> List[float]:
    """Distribute rotation across multiple bones by weight.

    Args:
        rotation: Total rotation in radians
        weights: Distribution weights (should sum to 1.0)
        clamp: Whether to clamp individual rotations
        limit: Clamp limit in radians

    Returns:
        List of rotations for each target bone
    """
    result = [rotation * w for w in weights]
    if clamp:
        result = [_clamp_rotation(r, limit) for r in result]
    return result


def _distribute_position(
    position: Tuple[float, float],
    num_targets: int,
    scale: float = 1.0
) -> List[Tuple[float, float]]:
    """Distribute position offset across multiple bones.

    For one-to-many mappings, only the first bone gets the offset.
    The offset is scaled by the position_scale factor.

    Args:
        position: (x, y) offset
        num_targets: Number of target bones
        scale: Position scale factor

    Returns:
        List of positions for each target bone
    """
    scaled = (position[0] * scale, position[1] * scale)
    # Only first bone gets the position offset
    result = [scaled] + [(0.0, 0.0)] * (num_targets - 1)
    return result


# =============================================================================
# Retargeting Functions
# =============================================================================

def retarget_pose(
    pose: 'Pose',
    mapping: SkeletonMapping,
    config: Optional[RetargetingConfig] = None
) -> 'Pose':
    """Retarget a pose from source to target skeleton.

    Args:
        pose: Source pose
        mapping: Skeleton mapping to use
        config: Retargeting configuration

    Returns:
        New pose with target bone names and adjusted values
    """
    from .pose import Pose

    config = config or RetargetingConfig()

    new_rotations: Dict[str, float] = {}
    new_positions: Dict[str, Tuple[float, float]] = {}
    new_scales: Dict[str, float] = {}
    new_visibility: Dict[str, bool] = {}

    # Process rotations
    for bone_name, rotation in pose.rotations.items():
        bone_mapping = mapping.get_mapping(bone_name)
        if bone_mapping:
            rotations = _distribute_rotation(
                rotation,
                bone_mapping.rotation_weights,
                config.clamp_rotations,
                config.rotation_limit
            )
            for target, rot in zip(bone_mapping.targets, rotations):
                new_rotations[target] = rot
        # Unmapped bones are skipped (target gets neutral)

    # Process positions
    for bone_name, position in pose.positions.items():
        bone_mapping = mapping.get_mapping(bone_name)
        if bone_mapping and config.scale_positions:
            positions = _distribute_position(
                position,
                len(bone_mapping.targets),
                bone_mapping.position_scale
            )
            for target, pos in zip(bone_mapping.targets, positions):
                if pos != (0.0, 0.0):
                    new_positions[target] = pos

    # Process scales (distribute evenly)
    for bone_name, scale in pose.scales.items():
        bone_mapping = mapping.get_mapping(bone_name)
        if bone_mapping:
            for target in bone_mapping.targets:
                new_scales[target] = scale

    # Process visibility
    for bone_name, visible in pose.visibility.items():
        bone_mapping = mapping.get_mapping(bone_name)
        if bone_mapping:
            for target in bone_mapping.targets:
                new_visibility[target] = visible

    return Pose(
        name=f"{pose.name}_retargeted",
        rotations=new_rotations,
        positions=new_positions,
        scales=new_scales,
        visibility=new_visibility,
        duration=pose.duration,
        easing=pose.easing
    )


def retarget_frame(
    frame: 'FrameData',
    mapping: SkeletonMapping,
    config: Optional[RetargetingConfig] = None
) -> 'FrameData':
    """Retarget a single animation frame.

    Args:
        frame: Source frame data
        mapping: Skeleton mapping to use
        config: Retargeting configuration

    Returns:
        New frame with target bone names and adjusted values
    """
    from animation.cycles import FrameData

    config = config or RetargetingConfig()

    new_rotations: Dict[str, float] = {}
    new_offsets: Dict[str, Tuple[float, float]] = {}

    # Process bone rotations
    for bone_name, rotation in frame.bone_rotations.items():
        bone_mapping = mapping.get_mapping(bone_name)
        if bone_mapping:
            rotations = _distribute_rotation(
                rotation,
                bone_mapping.rotation_weights,
                config.clamp_rotations,
                config.rotation_limit
            )
            for target, rot in zip(bone_mapping.targets, rotations):
                new_rotations[target] = rot

    # Process bone offsets
    for bone_name, offset in frame.bone_offsets.items():
        bone_mapping = mapping.get_mapping(bone_name)
        if bone_mapping and config.scale_positions:
            offsets = _distribute_position(
                offset,
                len(bone_mapping.targets),
                bone_mapping.position_scale
            )
            for target, off in zip(bone_mapping.targets, offsets):
                if off != (0.0, 0.0):
                    new_offsets[target] = off

    # Scale root offset
    root_offset = frame.root_offset
    if config.preserve_root_motion:
        root_offset = (
            root_offset[0] * mapping.root_scale[0],
            root_offset[1] * mapping.root_scale[1]
        )

    return FrameData(
        bone_rotations=new_rotations,
        bone_offsets=new_offsets,
        root_offset=root_offset,
        duration=frame.duration
    )


def retarget_animation(
    animation: 'AnimationCycle',
    mapping: SkeletonMapping,
    config: Optional[RetargetingConfig] = None
) -> 'AnimationCycle':
    """Retarget an animation cycle to a different skeleton.

    Args:
        animation: Source animation cycle
        mapping: Skeleton mapping to use
        config: Retargeting configuration

    Returns:
        New animation with target bone names and adjusted values
    """
    from animation.cycles import AnimationCycle

    config = config or RetargetingConfig()

    new_frames = [
        retarget_frame(frame, mapping, config)
        for frame in animation.frames
    ]

    return AnimationCycle(
        name=f"{animation.name}_{mapping.target_type}",
        frames=new_frames,
        loop=animation.loop,
        fps=animation.fps
    )


def retarget_timeline(
    timeline: 'Timeline',
    mapping: SkeletonMapping,
    config: Optional[RetargetingConfig] = None
) -> 'Timeline':
    """Retarget a timeline-based animation.

    Args:
        timeline: Source timeline
        mapping: Skeleton mapping to use
        config: Retargeting configuration

    Returns:
        New timeline with target bone tracks
    """
    from animation.timeline import Timeline, Track

    config = config or RetargetingConfig()

    new_timeline = Timeline(
        f"{timeline.name}_{mapping.target_type}",
        timeline.fps
    )
    new_timeline.loop = timeline.loop

    # Track name patterns: bone_rotation, bone_offset_x, bone_offset_y
    for track_name, track in timeline.tracks.items():
        # Handle root tracks first (before general offset patterns)
        if track_name in ('root_offset_x', 'root_offset_y'):
            new_track = Track(track_name)
            scale = mapping.root_scale[0] if track_name.endswith('_x') else mapping.root_scale[1]
            for kf in track.keyframes:
                value = kf.value * scale if config.preserve_root_motion else kf.value
                new_track.add_keyframe(kf.time, value, kf.easing)
            new_timeline.add_track(new_track)
            continue

        # Parse track name to find bone and property
        if track_name.endswith('_rotation'):
            bone_name = track_name[:-9]  # Remove '_rotation'
            property_type = 'rotation'
        elif track_name.endswith('_offset_x'):
            bone_name = track_name[:-9]
            property_type = 'offset_x'
        elif track_name.endswith('_offset_y'):
            bone_name = track_name[:-9]
            property_type = 'offset_y'
        else:
            # Unknown track format, pass through
            new_timeline.add_track(track)
            continue

        # Get mapping for this bone
        bone_mapping = mapping.get_mapping(bone_name)
        if not bone_mapping:
            continue  # Skip unmapped bones

        # Create tracks for target bones
        if property_type == 'rotation':
            for i, target in enumerate(bone_mapping.targets):
                new_track = Track(f'{target}_rotation')
                weight = bone_mapping.rotation_weights[i]
                for kf in track.keyframes:
                    value = kf.value * weight
                    if config.clamp_rotations:
                        value = _clamp_rotation(value, config.rotation_limit)
                    new_track.add_keyframe(kf.time, value, kf.easing)
                new_timeline.add_track(new_track)

        elif property_type in ('offset_x', 'offset_y'):
            if config.scale_positions:
                # Only first target gets the offset
                target = bone_mapping.targets[0]
                new_track = Track(f'{target}_{property_type}')
                for kf in track.keyframes:
                    value = kf.value * bone_mapping.position_scale
                    new_track.add_keyframe(kf.time, value, kf.easing)
                new_timeline.add_track(new_track)

    return new_timeline


# =============================================================================
# Pre-built Mappings
# =============================================================================

def _create_chibi_to_humanoid() -> SkeletonMapping:
    """Create mapping from chibi to humanoid skeleton."""
    mapping = SkeletonMapping(
        name='chibi_to_humanoid',
        source_type='chibi',
        target_type='humanoid',
        root_scale=(1.5, 1.5)  # Humanoid is larger
    )

    # Direct mappings
    mapping.add_mapping('root', ['root'])
    mapping.add_mapping('head', ['head'])

    # Spine splits
    mapping.add_mapping('spine', ['spine_lower', 'spine_upper'], [0.5, 0.5])

    # Arm splits (upper arm gets more rotation)
    mapping.add_mapping('arm_l', ['arm_upper_l', 'arm_lower_l'], [0.6, 0.4])
    mapping.add_mapping('arm_r', ['arm_upper_r', 'arm_lower_r'], [0.6, 0.4])
    mapping.add_mapping('hand_l', ['hand_l'])
    mapping.add_mapping('hand_r', ['hand_r'])

    # Leg splits
    mapping.add_mapping('leg_l', ['leg_upper_l', 'leg_lower_l'], [0.5, 0.5])
    mapping.add_mapping('leg_r', ['leg_upper_r', 'leg_lower_r'], [0.5, 0.5])
    mapping.add_mapping('foot_l', ['foot_l'])
    mapping.add_mapping('foot_r', ['foot_r'])

    # Hair
    mapping.add_mapping('hair_back', ['hair_back'])
    mapping.add_mapping('hair_front', ['hair_front'])

    return mapping


def _create_humanoid_to_chibi() -> SkeletonMapping:
    """Create mapping from humanoid to chibi skeleton."""
    mapping = SkeletonMapping(
        name='humanoid_to_chibi',
        source_type='humanoid',
        target_type='chibi',
        root_scale=(0.67, 0.67)  # Chibi is smaller
    )

    # Direct mappings
    mapping.add_mapping('root', ['root'])
    mapping.add_mapping('head', ['head'])
    mapping.add_mapping('neck', ['head'], [0.3])  # Neck rotation goes partly to head

    # Spine combines
    mapping.add_mapping('spine_lower', ['spine'], [0.5])
    mapping.add_mapping('spine_upper', ['spine'], [0.5])

    # Arms combine (both contribute to single arm)
    mapping.add_mapping('shoulder_l', ['arm_l'], [0.2])
    mapping.add_mapping('arm_upper_l', ['arm_l'], [0.5])
    mapping.add_mapping('arm_lower_l', ['arm_l'], [0.3])
    mapping.add_mapping('shoulder_r', ['arm_r'], [0.2])
    mapping.add_mapping('arm_upper_r', ['arm_r'], [0.5])
    mapping.add_mapping('arm_lower_r', ['arm_r'], [0.3])
    mapping.add_mapping('hand_l', ['hand_l'])
    mapping.add_mapping('hand_r', ['hand_r'])

    # Legs combine
    mapping.add_mapping('leg_upper_l', ['leg_l'], [0.5])
    mapping.add_mapping('leg_lower_l', ['leg_l'], [0.5])
    mapping.add_mapping('leg_upper_r', ['leg_r'], [0.5])
    mapping.add_mapping('leg_lower_r', ['leg_r'], [0.5])
    mapping.add_mapping('foot_l', ['foot_l'])
    mapping.add_mapping('foot_r', ['foot_r'])

    return mapping


def _create_chibi_to_simple() -> SkeletonMapping:
    """Create mapping from chibi to simple skeleton."""
    mapping = SkeletonMapping(
        name='chibi_to_simple',
        source_type='chibi',
        target_type='simple',
        root_scale=(1.0, 1.0)
    )

    mapping.add_mapping('root', ['root'])
    mapping.add_mapping('spine', ['body'])
    mapping.add_mapping('head', ['head'])
    # Arms and legs don't exist in simple, so they're dropped

    return mapping


def _create_simple_to_chibi() -> SkeletonMapping:
    """Create mapping from simple to chibi skeleton."""
    mapping = SkeletonMapping(
        name='simple_to_chibi',
        source_type='simple',
        target_type='chibi',
        root_scale=(1.0, 1.0)
    )

    mapping.add_mapping('root', ['root'])
    mapping.add_mapping('body', ['spine'])
    mapping.add_mapping('head', ['head'])

    return mapping


def _create_humanoid_to_simple() -> SkeletonMapping:
    """Create mapping from humanoid to simple skeleton."""
    mapping = SkeletonMapping(
        name='humanoid_to_simple',
        source_type='humanoid',
        target_type='simple',
        root_scale=(0.5, 0.5)
    )

    mapping.add_mapping('root', ['root'])
    mapping.add_mapping('spine_lower', ['body'], [0.5])
    mapping.add_mapping('spine_upper', ['body'], [0.5])
    mapping.add_mapping('head', ['head'])

    return mapping


def _create_simple_to_humanoid() -> SkeletonMapping:
    """Create mapping from simple to humanoid skeleton."""
    mapping = SkeletonMapping(
        name='simple_to_humanoid',
        source_type='simple',
        target_type='humanoid',
        root_scale=(2.0, 2.0)
    )

    mapping.add_mapping('root', ['root'])
    mapping.add_mapping('body', ['spine_lower', 'spine_upper'], [0.5, 0.5])
    mapping.add_mapping('head', ['head'])

    return mapping


# Registry of pre-built mappings
_MAPPING_REGISTRY: Dict[Tuple[str, str], SkeletonMapping] = {}


def _init_registry():
    """Initialize the mapping registry."""
    global _MAPPING_REGISTRY
    if not _MAPPING_REGISTRY:
        mappings = [
            _create_chibi_to_humanoid(),
            _create_humanoid_to_chibi(),
            _create_chibi_to_simple(),
            _create_simple_to_chibi(),
            _create_humanoid_to_simple(),
            _create_simple_to_humanoid(),
        ]
        for m in mappings:
            _MAPPING_REGISTRY[(m.source_type, m.target_type)] = m


def create_mapping(source_type: str, target_type: str) -> SkeletonMapping:
    """Get or create a skeleton mapping.

    Args:
        source_type: Source skeleton type ('chibi', 'humanoid', 'simple')
        target_type: Target skeleton type

    Returns:
        SkeletonMapping for the specified types

    Raises:
        ValueError: If no mapping exists for the type pair
    """
    _init_registry()

    if source_type == target_type:
        # Identity mapping
        return SkeletonMapping(
            name=f'{source_type}_to_{target_type}',
            source_type=source_type,
            target_type=target_type
        )

    key = (source_type, target_type)
    if key not in _MAPPING_REGISTRY:
        raise ValueError(
            f"No mapping from '{source_type}' to '{target_type}'. "
            f"Available: {list_mappings()}"
        )

    return _MAPPING_REGISTRY[key]


def list_mappings() -> List[Tuple[str, str]]:
    """List available skeleton mapping pairs.

    Returns:
        List of (source_type, target_type) tuples
    """
    _init_registry()
    return list(_MAPPING_REGISTRY.keys())


def infer_mapping(
    source_skeleton: 'Skeleton',
    target_skeleton: 'Skeleton'
) -> SkeletonMapping:
    """Attempt to infer a mapping between two skeletons.

    Uses bone name matching to create a best-effort mapping.
    For production use, prefer explicit mappings.

    Args:
        source_skeleton: Source skeleton
        target_skeleton: Target skeleton

    Returns:
        Inferred SkeletonMapping
    """
    mapping = SkeletonMapping(
        name='inferred',
        source_type='custom',
        target_type='custom'
    )

    source_bones = set(source_skeleton.bones.keys())
    target_bones = set(target_skeleton.bones.keys())

    # Direct name matches
    for bone in source_bones & target_bones:
        mapping.add_mapping(bone, [bone])

    # Try common patterns for unmatched bones
    unmatched_source = source_bones - set(mapping.bone_mappings.keys())
    unmatched_target = target_bones - {
        t for m in mapping.bone_mappings.values() for t in m.targets
    }

    # Pattern matching (e.g., arm_l -> arm_upper_l + arm_lower_l)
    for source_bone in unmatched_source:
        # Look for bones that start with source name
        matches = [t for t in unmatched_target if t.startswith(source_bone)]
        if matches:
            weights = [1.0 / len(matches)] * len(matches)
            mapping.add_mapping(source_bone, matches, weights)

    return mapping

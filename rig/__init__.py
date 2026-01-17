"""
Bitsy Rig - Skeletal rigging and pose system.

Provides bone hierarchies, pose definitions, and animation support
for character rigging.
"""

from .skeleton import (
    Bone,
    Skeleton,
    create_skeleton,
    create_chibi_skeleton,
    create_humanoid_skeleton,
    create_simple_skeleton,
    SKELETON_PRESETS,
)

from .pose import (
    Pose,
    PoseLibrary,
    blend_poses,
    blend_multiple_poses,
    apply_easing,
    lerp_angle,
    create_pose_library,
    create_chibi_poses,
    create_humanoid_poses,
    POSE_LIBRARY_PRESETS,
)

from .retarget import (
    BoneMapping,
    SkeletonMapping,
    RetargetingConfig,
    retarget_animation,
    retarget_pose,
    retarget_timeline,
    retarget_frame,
    create_mapping,
    list_mappings,
    infer_mapping,
)

__all__ = [
    # Skeleton
    'Bone',
    'Skeleton',
    'create_skeleton',
    'create_chibi_skeleton',
    'create_humanoid_skeleton',
    'create_simple_skeleton',
    'SKELETON_PRESETS',

    # Pose
    'Pose',
    'PoseLibrary',
    'blend_poses',
    'blend_multiple_poses',
    'apply_easing',
    'lerp_angle',
    'create_pose_library',
    'create_chibi_poses',
    'create_humanoid_poses',
    'POSE_LIBRARY_PRESETS',

    # Retargeting
    'BoneMapping',
    'SkeletonMapping',
    'RetargetingConfig',
    'retarget_animation',
    'retarget_pose',
    'retarget_timeline',
    'retarget_frame',
    'create_mapping',
    'list_mappings',
    'infer_mapping',
]

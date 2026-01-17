# Animation Retargeting Design

## Overview

Animation retargeting allows animations created for one skeleton type to be applied to characters with different skeleton structures or proportions. For example, a walk cycle designed for a chibi character can be automatically adapted to work with a humanoid character.

## Architecture

### Core Components

1. **BoneMapping** - Defines how a single source bone maps to one or more target bones
2. **SkeletonMapping** - Collection of bone mappings between two skeleton types
3. **RetargetingConfig** - Controls transform adjustment behavior
4. **retarget_animation()** - Core function that processes animations

### Data Structures

```python
@dataclass
class BoneMapping:
    source: str                      # Source bone name
    targets: List[str]               # Target bone name(s)
    rotation_weights: List[float]    # How to distribute rotation (sum to 1.0)
    position_scale: float            # Scale factor for position offsets

@dataclass
class SkeletonMapping:
    name: str                        # e.g., "chibi_to_humanoid"
    source_type: str                 # e.g., "chibi"
    target_type: str                 # e.g., "humanoid"
    bone_mappings: Dict[str, BoneMapping]
    root_scale: Tuple[float, float]  # (x_scale, y_scale) for root motion

@dataclass
class RetargetingConfig:
    scale_positions: bool = True      # Adjust offsets for proportion
    preserve_root_motion: bool = True # Keep movement distance
    clamp_rotations: bool = False     # Limit extreme angles
    rotation_limit: float = 2.0       # Max radians if clamping
```

## Bone Mapping Strategy

### One-to-One Mappings
Simple bones map directly:
- `head` → `head`
- `root` → `root`

### One-to-Many Mappings
Single bones split across multiple target bones with weighted rotation distribution:
- `arm_l` → `[arm_upper_l, arm_lower_l]` with weights `[0.6, 0.4]`
- `leg_l` → `[leg_upper_l, leg_lower_l]` with weights `[0.5, 0.5]`
- `spine` → `[spine_lower, spine_upper]` with weights `[0.5, 0.5]`

When a chibi arm rotates 30°, the humanoid upper arm rotates 18° (60%) and lower arm rotates 12° (40%).

### Pre-built Mappings
- `chibi_to_humanoid`
- `humanoid_to_chibi`
- `chibi_to_simple`
- `simple_to_chibi`
- `humanoid_to_simple`
- `simple_to_humanoid`

## Retargeting Process

For each animation frame:

1. **Read source frame** - Extract bone rotations and offsets
2. **Map bones** - For each source bone with a mapping:
   - Distribute rotation across target bones using weights
   - Scale position offsets by position_scale factor
3. **Handle unmapped bones** - Target bones without source data get neutral values (0 rotation, no offset)
4. **Scale root motion** - Apply root_scale to root offsets for proportion differences
5. **Build target frame** - Assemble new FrameData with target bone names

## Public API

```python
from rig import (
    # Core classes
    BoneMapping,
    SkeletonMapping,
    RetargetingConfig,

    # Functions
    retarget_animation,      # AnimationCycle → AnimationCycle
    retarget_pose,           # Pose → Pose
    retarget_timeline,       # Timeline → Timeline

    # Mapping utilities
    create_mapping,          # Factory: create_mapping('chibi', 'humanoid')
    list_mappings,           # Returns available mapping pairs
    infer_mapping,           # Auto-generate from two skeletons
)
```

## Module Structure

```
rig/
├── __init__.py      # Add retarget exports
├── skeleton.py      # Existing
├── pose.py          # Existing
└── retarget.py      # NEW - all retargeting code
```

## Usage Examples

```python
from rig import create_mapping, retarget_animation, RetargetingConfig
from animation import create_chibi_walk_cycle

# Get pre-built mapping
mapping = create_mapping('chibi', 'humanoid')

# Retarget an animation
chibi_walk = create_chibi_walk_cycle()
config = RetargetingConfig(scale_positions=True)
humanoid_walk = retarget_animation(chibi_walk, mapping, config)

# Retarget a pose
from rig import retarget_pose
chibi_pose = Pose(name='crouch', rotations={'spine': -0.3, 'leg_l': 0.5})
humanoid_pose = retarget_pose(chibi_pose, mapping)
```

## Testing Strategy

### Unit Tests
- BoneMapping rotation distribution math
- SkeletonMapping lookup and missing bone handling
- RetargetingConfig defaults and clamping

### Integration Tests
- Full animation retargeting chibi→humanoid
- Single pose retargeting
- Timeline-based animation retargeting
- Round-trip: chibi→humanoid→chibi similarity check

### Edge Cases
- Unmapped bones use neutral values
- Empty animations return empty
- Same skeleton type passes through unchanged
- Missing mapping raises clear error

## Design Decisions

1. **Explicit mapping over auto-detection** - Predictable behavior, easier to debug
2. **Weighted rotation distribution** - Natural-looking motion when splitting bones
3. **Position scaling** - Handles proportion differences between skeleton types
4. **Neutral values for unmapped bones** - Safe default, no NaN or broken poses

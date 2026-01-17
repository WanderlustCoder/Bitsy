"""
Animation Generator - Generate animations from skeleton definitions.

Provides:
- Idle animation generation (breathing, subtle movement)
- Walk/run cycle generation from skeleton
- Attack animation generation
- Transition animations between states
- Animation customization based on character properties
"""

from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import math
import random

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from animation.cycles import (
    AnimationCycle, FrameData,
    create_walk_cycle_4frame, create_walk_cycle_6frame,
    create_run_cycle_6frame, create_run_cycle_8frame,
    create_attack_slash, create_attack_stab, create_attack_overhead,
    create_jump_cycle, create_hurt_cycle, create_death_cycle,
)
from rig.skeleton import Skeleton


class AnimationType(Enum):
    """Types of animations that can be generated."""
    IDLE = "idle"
    IDLE_BREATHE = "idle_breathe"
    IDLE_BLINK = "idle_blink"
    IDLE_LOOK = "idle_look"
    WALK = "walk"
    RUN = "run"
    ATTACK_SLASH = "attack_slash"
    ATTACK_STAB = "attack_stab"
    ATTACK_OVERHEAD = "attack_overhead"
    JUMP = "jump"
    FALL = "fall"
    LAND = "land"
    HURT = "hurt"
    DEATH = "death"
    TRANSITION = "transition"


class IdleStyle(Enum):
    """Styles of idle animation."""
    SUBTLE = "subtle"      # Minimal movement, professional
    RELAXED = "relaxed"    # Casual stance, more movement
    ALERT = "alert"        # Ready for action
    TIRED = "tired"        # Droopy, slow
    EXCITED = "excited"    # Bouncy, energetic


@dataclass
class AnimationConfig:
    """Configuration for animation generation."""
    # Timing
    fps: int = 12
    frame_count: int = 8

    # Intensity
    movement_scale: float = 1.0
    rotation_scale: float = 1.0

    # Character properties that affect animation
    weight: float = 1.0      # Heavier = slower, more grounded
    energy: float = 1.0      # Higher = faster, more bouncy
    age_factor: float = 1.0  # Child = bouncy, elder = slower

    # Seed for deterministic generation
    seed: Optional[int] = None


# =============================================================================
# Idle Animation Generation
# =============================================================================

def generate_idle(
    skeleton: Optional[Skeleton] = None,
    style: IdleStyle = IdleStyle.SUBTLE,
    config: Optional[AnimationConfig] = None
) -> AnimationCycle:
    """Generate an idle animation.

    Args:
        skeleton: Optional skeleton for bone names (uses defaults if None)
        style: Style of idle animation
        config: Animation configuration

    Returns:
        AnimationCycle for idle animation
    """
    config = config or AnimationConfig()
    rng = random.Random(config.seed)

    cycle = AnimationCycle(f'idle_{style.value}', loop=True, fps=config.fps)

    # Get style-specific parameters
    params = _get_idle_params(style, config)

    # Generate breathing pattern
    breath_frames = _generate_breath_frames(params, config, rng)

    # Add subtle head movement
    head_frames = _generate_head_bob(params, config, rng)

    # Combine into frames
    frame_count = config.frame_count
    for i in range(frame_count):
        t = i / frame_count

        # Get breath offset at this point
        breath_idx = int(t * len(breath_frames)) % len(breath_frames)
        breath = breath_frames[breath_idx]

        # Get head movement at this point
        head_idx = int(t * len(head_frames)) % len(head_frames)
        head = head_frames[head_idx]

        frame = FrameData(
            bone_rotations={
                'torso': breath['torso_rot'] * config.rotation_scale,
                'head': head['head_rot'] * config.rotation_scale,
                'left_arm': breath['arm_rot'] * config.rotation_scale,
                'right_arm': -breath['arm_rot'] * config.rotation_scale,
            },
            bone_offsets={
                'head': (0, head['head_y'] * config.movement_scale),
            },
            root_offset=(0.0, breath['body_y'] * config.movement_scale),
            duration=1.0
        )
        cycle.frames.append(frame)

    return cycle


def _get_idle_params(style: IdleStyle, config: AnimationConfig) -> Dict:
    """Get parameters for idle style."""
    base_params = {
        'breath_amplitude': 1.0,
        'breath_speed': 1.0,
        'head_movement': 0.5,
        'body_sway': 0.3,
        'arm_movement': 0.5,
    }

    style_modifiers = {
        IdleStyle.SUBTLE: {
            'breath_amplitude': 0.5,
            'head_movement': 0.2,
            'body_sway': 0.1,
        },
        IdleStyle.RELAXED: {
            'breath_amplitude': 1.2,
            'body_sway': 0.5,
            'arm_movement': 0.8,
        },
        IdleStyle.ALERT: {
            'breath_amplitude': 0.6,
            'breath_speed': 1.3,
            'head_movement': 0.8,
            'body_sway': 0.2,
        },
        IdleStyle.TIRED: {
            'breath_amplitude': 1.5,
            'breath_speed': 0.7,
            'head_movement': 0.3,
            'body_sway': 0.4,
        },
        IdleStyle.EXCITED: {
            'breath_amplitude': 0.8,
            'breath_speed': 1.5,
            'head_movement': 1.0,
            'body_sway': 0.6,
            'arm_movement': 1.2,
        },
    }

    params = base_params.copy()
    if style in style_modifiers:
        params.update(style_modifiers[style])

    # Apply character modifiers
    params['breath_speed'] *= config.energy
    params['breath_amplitude'] *= config.weight

    return params


def _generate_breath_frames(params: Dict, config: AnimationConfig,
                            rng: random.Random) -> List[Dict]:
    """Generate breathing motion frames."""
    frames = []
    count = config.frame_count
    amp = params['breath_amplitude']

    for i in range(count):
        t = i / count
        # Sine wave for breathing
        breath = math.sin(t * 2 * math.pi) * amp

        frames.append({
            'body_y': breath * 0.5,  # Subtle up/down
            'torso_rot': breath * 0.3,  # Chest expansion
            'arm_rot': breath * 0.2,  # Arms follow body
        })

    return frames


def _generate_head_bob(params: Dict, config: AnimationConfig,
                       rng: random.Random) -> List[Dict]:
    """Generate subtle head movement."""
    frames = []
    count = config.frame_count
    amp = params['head_movement']

    for i in range(count):
        t = i / count
        # Slower, offset sine for head
        head_y = math.sin(t * 2 * math.pi + 0.5) * amp * 0.3
        head_rot = math.sin(t * 2 * math.pi * 0.5) * amp * 2

        frames.append({
            'head_y': head_y,
            'head_rot': head_rot,
        })

    return frames


def generate_idle_blink(
    config: Optional[AnimationConfig] = None
) -> AnimationCycle:
    """Generate a blinking idle variation.

    Returns:
        Short blink animation to overlay on idle
    """
    config = config or AnimationConfig(frame_count=4, fps=12)

    cycle = AnimationCycle('idle_blink', loop=False, fps=config.fps)

    # Open -> closing -> closed -> opening
    cycle.frames.append(FrameData(
        bone_offsets={'left_eye': (0, 0), 'right_eye': (0, 0)},
        duration=0.5
    ))
    cycle.frames.append(FrameData(
        bone_offsets={'left_eye': (0, 0.5), 'right_eye': (0, 0.5)},  # Half closed
        duration=0.5
    ))
    cycle.frames.append(FrameData(
        bone_offsets={'left_eye': (0, 1), 'right_eye': (0, 1)},  # Closed
        duration=1.0
    ))
    cycle.frames.append(FrameData(
        bone_offsets={'left_eye': (0, 0), 'right_eye': (0, 0)},  # Open
        duration=0.5
    ))

    return cycle


# =============================================================================
# Transition Animation Generation
# =============================================================================

def generate_transition(
    from_anim: AnimationType,
    to_anim: AnimationType,
    config: Optional[AnimationConfig] = None
) -> AnimationCycle:
    """Generate a transition animation between two states.

    Args:
        from_anim: Starting animation type
        to_anim: Target animation type
        config: Animation configuration

    Returns:
        Transition AnimationCycle
    """
    config = config or AnimationConfig(frame_count=4, fps=12)

    cycle = AnimationCycle(
        f'transition_{from_anim.value}_to_{to_anim.value}',
        loop=False,
        fps=config.fps
    )

    # Get key poses from source and target
    from_pose = _get_key_pose(from_anim)
    to_pose = _get_key_pose(to_anim)

    # Interpolate between poses
    for i in range(config.frame_count):
        t = i / (config.frame_count - 1) if config.frame_count > 1 else 1.0
        # Ease in-out
        t = _ease_in_out(t)

        frame = _interpolate_poses(from_pose, to_pose, t)
        cycle.frames.append(frame)

    return cycle


def _get_key_pose(anim_type: AnimationType) -> FrameData:
    """Get a representative pose for an animation type."""
    poses = {
        AnimationType.IDLE: FrameData(
            bone_rotations={'torso': 0, 'left_arm': 5, 'right_arm': -5},
            root_offset=(0, 0)
        ),
        AnimationType.WALK: FrameData(
            bone_rotations={'torso': 2, 'left_arm': 15, 'right_arm': -15,
                           'left_leg': -10, 'right_leg': 10},
            root_offset=(0, 0)
        ),
        AnimationType.RUN: FrameData(
            bone_rotations={'torso': 5, 'left_arm': 30, 'right_arm': -30,
                           'left_leg': -25, 'right_leg': 25},
            root_offset=(0, -1)
        ),
        AnimationType.ATTACK_SLASH: FrameData(
            bone_rotations={'torso': 10, 'right_arm': -90, 'left_arm': 20},
            root_offset=(1, 0)
        ),
        AnimationType.JUMP: FrameData(
            bone_rotations={'torso': -5, 'left_arm': -30, 'right_arm': -30,
                           'left_leg': 20, 'right_leg': 20},
            root_offset=(0, -2)
        ),
        AnimationType.HURT: FrameData(
            bone_rotations={'torso': -10, 'head': 15, 'left_arm': 30, 'right_arm': 30},
            root_offset=(-1, 0)
        ),
    }
    return poses.get(anim_type, FrameData())


def _interpolate_poses(from_pose: FrameData, to_pose: FrameData,
                       t: float) -> FrameData:
    """Interpolate between two poses."""
    # Interpolate rotations
    rotations = {}
    all_bones = set(from_pose.bone_rotations.keys()) | set(to_pose.bone_rotations.keys())
    for bone in all_bones:
        from_rot = from_pose.bone_rotations.get(bone, 0)
        to_rot = to_pose.bone_rotations.get(bone, 0)
        rotations[bone] = from_rot + (to_rot - from_rot) * t

    # Interpolate root offset
    from_x, from_y = from_pose.root_offset
    to_x, to_y = to_pose.root_offset
    root_offset = (
        from_x + (to_x - from_x) * t,
        from_y + (to_y - from_y) * t
    )

    return FrameData(
        bone_rotations=rotations,
        root_offset=root_offset,
        duration=1.0
    )


def _ease_in_out(t: float) -> float:
    """Smooth ease in-out curve."""
    return t * t * (3 - 2 * t)


# =============================================================================
# Animation Set Generation
# =============================================================================

@dataclass
class AnimationSet:
    """Complete set of animations for a character."""
    idle: AnimationCycle
    walk: AnimationCycle
    run: AnimationCycle
    attack: AnimationCycle
    jump: AnimationCycle
    hurt: AnimationCycle
    death: AnimationCycle
    transitions: Dict[str, AnimationCycle] = field(default_factory=dict)

    def get_all(self) -> Dict[str, AnimationCycle]:
        """Get all animations as a dictionary."""
        result = {
            'idle': self.idle,
            'walk': self.walk,
            'run': self.run,
            'attack': self.attack,
            'jump': self.jump,
            'hurt': self.hurt,
            'death': self.death,
        }
        result.update(self.transitions)
        return result


def generate_animation_set(
    skeleton: Optional[Skeleton] = None,
    config: Optional[AnimationConfig] = None,
    include_transitions: bool = True
) -> AnimationSet:
    """Generate a complete set of character animations.

    Args:
        skeleton: Character skeleton (uses defaults if None)
        config: Animation configuration
        include_transitions: Whether to generate transition animations

    Returns:
        Complete AnimationSet
    """
    config = config or AnimationConfig()

    # Generate base animations
    anim_set = AnimationSet(
        idle=generate_idle(skeleton, IdleStyle.SUBTLE, config),
        walk=create_walk_cycle_6frame(),
        run=create_run_cycle_6frame(),
        attack=create_attack_slash(),
        jump=create_jump_cycle(),
        hurt=create_hurt_cycle(),
        death=create_death_cycle(),
    )

    # Apply config scaling to all animations
    _apply_config_to_cycle(anim_set.walk, config)
    _apply_config_to_cycle(anim_set.run, config)
    _apply_config_to_cycle(anim_set.attack, config)

    # Generate transitions
    if include_transitions:
        anim_set.transitions = {
            'idle_to_walk': generate_transition(
                AnimationType.IDLE, AnimationType.WALK, config
            ),
            'walk_to_run': generate_transition(
                AnimationType.WALK, AnimationType.RUN, config
            ),
            'idle_to_attack': generate_transition(
                AnimationType.IDLE, AnimationType.ATTACK_SLASH, config
            ),
        }

    return anim_set


def _apply_config_to_cycle(cycle: AnimationCycle, config: AnimationConfig):
    """Apply configuration scaling to an existing cycle."""
    for frame in cycle.frames:
        # Scale rotations
        for bone in frame.bone_rotations:
            frame.bone_rotations[bone] *= config.rotation_scale

        # Scale offsets
        for bone in frame.bone_offsets:
            ox, oy = frame.bone_offsets[bone]
            frame.bone_offsets[bone] = (
                ox * config.movement_scale,
                oy * config.movement_scale
            )

        # Scale root offset
        rx, ry = frame.root_offset
        frame.root_offset = (
            rx * config.movement_scale,
            ry * config.movement_scale
        )


# =============================================================================
# Convenience Functions
# =============================================================================

def list_animation_types() -> List[str]:
    """List all available animation types."""
    return [t.value for t in AnimationType]


def list_idle_styles() -> List[str]:
    """List all available idle styles."""
    return [s.value for s in IdleStyle]


def get_animation(
    anim_type: Union[str, AnimationType],
    config: Optional[AnimationConfig] = None
) -> AnimationCycle:
    """Get a single animation by type.

    Args:
        anim_type: Animation type name or enum
        config: Animation configuration

    Returns:
        AnimationCycle for the requested type
    """
    if isinstance(anim_type, str):
        anim_type = AnimationType(anim_type)

    config = config or AnimationConfig()

    generators = {
        AnimationType.IDLE: lambda: generate_idle(config=config),
        AnimationType.IDLE_BREATHE: lambda: generate_idle(
            style=IdleStyle.RELAXED, config=config
        ),
        AnimationType.WALK: create_walk_cycle_6frame,
        AnimationType.RUN: create_run_cycle_6frame,
        AnimationType.ATTACK_SLASH: create_attack_slash,
        AnimationType.ATTACK_STAB: create_attack_stab,
        AnimationType.ATTACK_OVERHEAD: create_attack_overhead,
        AnimationType.JUMP: create_jump_cycle,
        AnimationType.HURT: create_hurt_cycle,
        AnimationType.DEATH: create_death_cycle,
    }

    if anim_type not in generators:
        raise ValueError(f"Unknown animation type: {anim_type}")

    cycle = generators[anim_type]()
    _apply_config_to_cycle(cycle, config)
    return cycle

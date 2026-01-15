"""
Cycles - Pre-built animation cycles for common actions.

Provides ready-to-use animation cycles for:
- Walk cycles (4/6/8 frame variants)
- Run cycles
- Attack animations
- Jump/fall
- Death/hurt reactions
"""

from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field

from .timeline import Timeline, Track
from .easing import apply_easing


@dataclass
class FrameData:
    """Data for a single animation frame.

    Attributes:
        bone_rotations: Bone name -> rotation angle mapping
        bone_offsets: Bone name -> (x, y) offset mapping
        root_offset: Global offset for entire character
        duration: Frame duration in animation time units
    """

    bone_rotations: Dict[str, float] = field(default_factory=dict)
    bone_offsets: Dict[str, Tuple[float, float]] = field(default_factory=dict)
    root_offset: Tuple[float, float] = (0.0, 0.0)
    duration: float = 1.0


@dataclass
class AnimationCycle:
    """A complete animation cycle definition.

    Attributes:
        name: Cycle name
        frames: List of frame data
        loop: Whether animation loops
        fps: Recommended frames per second
    """

    name: str
    frames: List[FrameData] = field(default_factory=list)
    loop: bool = True
    fps: int = 12

    def get_duration(self) -> float:
        """Get total cycle duration."""
        return sum(f.duration for f in self.frames)

    def to_timeline(self) -> Timeline:
        """Convert cycle to a Timeline for playback."""
        timeline = Timeline(self.name, self.fps)
        timeline.loop = self.loop

        # Collect all bone names used
        all_bones = set()
        for frame in self.frames:
            all_bones.update(frame.bone_rotations.keys())
            all_bones.update(frame.bone_offsets.keys())

        # Create tracks for each bone rotation
        for bone_name in all_bones:
            rot_track = Track(f'{bone_name}_rotation')
            offset_x_track = Track(f'{bone_name}_offset_x')
            offset_y_track = Track(f'{bone_name}_offset_y')

            current_time = 0.0
            for frame in self.frames:
                # Rotation
                if bone_name in frame.bone_rotations:
                    rot_track.add_keyframe(
                        current_time,
                        frame.bone_rotations[bone_name],
                        'ease_in_out_sine'
                    )

                # Offset
                if bone_name in frame.bone_offsets:
                    ox, oy = frame.bone_offsets[bone_name]
                    offset_x_track.add_keyframe(current_time, ox, 'ease_in_out_sine')
                    offset_y_track.add_keyframe(current_time, oy, 'ease_in_out_sine')

                current_time += frame.duration

            if rot_track.keyframes:
                timeline.add_track(rot_track)
            if offset_x_track.keyframes:
                timeline.add_track(offset_x_track)
            if offset_y_track.keyframes:
                timeline.add_track(offset_y_track)

        # Root offset tracks
        root_x = Track('root_offset_x')
        root_y = Track('root_offset_y')
        current_time = 0.0
        for frame in self.frames:
            root_x.add_keyframe(current_time, frame.root_offset[0], 'ease_in_out_sine')
            root_y.add_keyframe(current_time, frame.root_offset[1], 'ease_in_out_sine')
            current_time += frame.duration

        timeline.add_track(root_x)
        timeline.add_track(root_y)

        return timeline


# =============================================================================
# Walk Cycles
# =============================================================================

def create_walk_cycle_4frame() -> AnimationCycle:
    """Create a simple 4-frame walk cycle.

    Frame pattern: contact -> passing -> contact -> passing (mirrored)
    """
    cycle = AnimationCycle('walk_4', loop=True, fps=8)

    # Frame 1: Right foot contact
    cycle.frames.append(FrameData(
        bone_rotations={
            'torso': 2.0,
            'left_arm': 20.0,
            'right_arm': -20.0,
            'left_leg': -15.0,
            'right_leg': 15.0,
        },
        root_offset=(0.0, 0.0),
        duration=2.0
    ))

    # Frame 2: Right foot passing
    cycle.frames.append(FrameData(
        bone_rotations={
            'torso': 0.0,
            'left_arm': 0.0,
            'right_arm': 0.0,
            'left_leg': 0.0,
            'right_leg': 0.0,
        },
        root_offset=(0.0, -1.0),  # Slight bounce up
        duration=2.0
    ))

    # Frame 3: Left foot contact (mirror of frame 1)
    cycle.frames.append(FrameData(
        bone_rotations={
            'torso': -2.0,
            'left_arm': -20.0,
            'right_arm': 20.0,
            'left_leg': 15.0,
            'right_leg': -15.0,
        },
        root_offset=(0.0, 0.0),
        duration=2.0
    ))

    # Frame 4: Left foot passing (mirror of frame 2)
    cycle.frames.append(FrameData(
        bone_rotations={
            'torso': 0.0,
            'left_arm': 0.0,
            'right_arm': 0.0,
            'left_leg': 0.0,
            'right_leg': 0.0,
        },
        root_offset=(0.0, -1.0),
        duration=2.0
    ))

    return cycle


def create_walk_cycle_6frame() -> AnimationCycle:
    """Create a smoother 6-frame walk cycle.

    Frame pattern: contact -> recoil -> passing -> high -> contact -> low
    """
    cycle = AnimationCycle('walk_6', loop=True, fps=12)

    # Frame 1: Right foot contact (heel strike)
    cycle.frames.append(FrameData(
        bone_rotations={
            'torso': 3.0,
            'head': -2.0,
            'left_arm': 25.0,
            'right_arm': -25.0,
            'left_upper_arm': 15.0,
            'right_upper_arm': -15.0,
            'left_leg': -20.0,
            'right_leg': 20.0,
        },
        root_offset=(0.0, 0.0),
        duration=1.0
    ))

    # Frame 2: Right foot recoil
    cycle.frames.append(FrameData(
        bone_rotations={
            'torso': 2.0,
            'head': -1.0,
            'left_arm': 15.0,
            'right_arm': -15.0,
            'left_leg': -10.0,
            'right_leg': 10.0,
        },
        root_offset=(0.0, 1.0),  # Dip down
        duration=1.0
    ))

    # Frame 3: Passing position
    cycle.frames.append(FrameData(
        bone_rotations={
            'torso': 0.0,
            'head': 0.0,
            'left_arm': 0.0,
            'right_arm': 0.0,
            'left_leg': 5.0,
            'right_leg': -5.0,
        },
        root_offset=(0.0, -1.0),  # Highest point
        duration=1.0
    ))

    # Frame 4: Left foot contact (mirror)
    cycle.frames.append(FrameData(
        bone_rotations={
            'torso': -3.0,
            'head': 2.0,
            'left_arm': -25.0,
            'right_arm': 25.0,
            'left_leg': 20.0,
            'right_leg': -20.0,
        },
        root_offset=(0.0, 0.0),
        duration=1.0
    ))

    # Frame 5: Left foot recoil
    cycle.frames.append(FrameData(
        bone_rotations={
            'torso': -2.0,
            'head': 1.0,
            'left_arm': -15.0,
            'right_arm': 15.0,
            'left_leg': 10.0,
            'right_leg': -10.0,
        },
        root_offset=(0.0, 1.0),
        duration=1.0
    ))

    # Frame 6: Passing position (other side)
    cycle.frames.append(FrameData(
        bone_rotations={
            'torso': 0.0,
            'head': 0.0,
            'left_arm': 0.0,
            'right_arm': 0.0,
            'left_leg': -5.0,
            'right_leg': 5.0,
        },
        root_offset=(0.0, -1.0),
        duration=1.0
    ))

    return cycle


def create_walk_cycle_8frame() -> AnimationCycle:
    """Create a detailed 8-frame walk cycle.

    Most fluid walk animation with full gait phases.
    """
    cycle = AnimationCycle('walk_8', loop=True, fps=12)

    # Frame phases for each step:
    # 1. Contact, 2. Recoil, 3. Passing, 4. High point
    # Then mirror for other foot

    phases = [
        # Right step
        {'torso': 3, 'arm_swing': 30, 'leg_swing': 25, 'bounce': 0},
        {'torso': 2, 'arm_swing': 20, 'leg_swing': 15, 'bounce': 1.5},
        {'torso': 1, 'arm_swing': 5, 'leg_swing': 5, 'bounce': -0.5},
        {'torso': 0, 'arm_swing': -10, 'leg_swing': -10, 'bounce': -1.5},
        # Left step (mirrored)
        {'torso': -3, 'arm_swing': -30, 'leg_swing': -25, 'bounce': 0},
        {'torso': -2, 'arm_swing': -20, 'leg_swing': -15, 'bounce': 1.5},
        {'torso': -1, 'arm_swing': -5, 'leg_swing': -5, 'bounce': -0.5},
        {'torso': 0, 'arm_swing': 10, 'leg_swing': 10, 'bounce': -1.5},
    ]

    for phase in phases:
        cycle.frames.append(FrameData(
            bone_rotations={
                'torso': phase['torso'],
                'head': -phase['torso'] * 0.5,
                'left_arm': phase['arm_swing'],
                'right_arm': -phase['arm_swing'],
                'left_leg': -phase['leg_swing'],
                'right_leg': phase['leg_swing'],
            },
            root_offset=(0.0, phase['bounce']),
            duration=1.0
        ))

    return cycle


# =============================================================================
# Run Cycles
# =============================================================================

def create_run_cycle_6frame() -> AnimationCycle:
    """Create a 6-frame run cycle.

    Faster and more exaggerated than walk.
    """
    cycle = AnimationCycle('run_6', loop=True, fps=12)

    phases = [
        # Right step - contact to flight
        {'torso': 8, 'arm': 45, 'leg': 40, 'bounce': 0},
        {'torso': 5, 'arm': 30, 'leg': 25, 'bounce': 2},
        {'torso': 0, 'arm': 0, 'leg': 0, 'bounce': -3},  # Flight phase
        # Left step - contact to flight
        {'torso': -8, 'arm': -45, 'leg': -40, 'bounce': 0},
        {'torso': -5, 'arm': -30, 'leg': -25, 'bounce': 2},
        {'torso': 0, 'arm': 0, 'leg': 0, 'bounce': -3},  # Flight phase
    ]

    for phase in phases:
        cycle.frames.append(FrameData(
            bone_rotations={
                'torso': phase['torso'],
                'head': -phase['torso'] * 0.3,
                'left_arm': phase['arm'],
                'right_arm': -phase['arm'],
                'left_leg': -phase['leg'],
                'right_leg': phase['leg'],
            },
            root_offset=(0.0, phase['bounce']),
            duration=1.0
        ))

    return cycle


def create_run_cycle_8frame() -> AnimationCycle:
    """Create a detailed 8-frame run cycle."""
    cycle = AnimationCycle('run_8', loop=True, fps=16)

    phases = [
        # Right step
        {'torso': 10, 'arm': 50, 'leg': 45, 'bounce': 0, 'lean': 5},
        {'torso': 7, 'arm': 35, 'leg': 30, 'bounce': 1, 'lean': 3},
        {'torso': 3, 'arm': 15, 'leg': 10, 'bounce': -2, 'lean': 0},
        {'torso': 0, 'arm': -5, 'leg': -10, 'bounce': -4, 'lean': -2},  # Flight
        # Left step
        {'torso': -10, 'arm': -50, 'leg': -45, 'bounce': 0, 'lean': -5},
        {'torso': -7, 'arm': -35, 'leg': -30, 'bounce': 1, 'lean': -3},
        {'torso': -3, 'arm': -15, 'leg': -10, 'bounce': -2, 'lean': 0},
        {'torso': 0, 'arm': 5, 'leg': 10, 'bounce': -4, 'lean': 2},  # Flight
    ]

    for phase in phases:
        cycle.frames.append(FrameData(
            bone_rotations={
                'torso': phase['torso'] + phase['lean'],
                'head': -phase['torso'] * 0.2,
                'left_arm': phase['arm'],
                'right_arm': -phase['arm'],
                'left_leg': -phase['leg'],
                'right_leg': phase['leg'],
            },
            root_offset=(0.0, phase['bounce']),
            duration=1.0
        ))

    return cycle


# =============================================================================
# Attack Cycles
# =============================================================================

def create_attack_slash() -> AnimationCycle:
    """Create a melee slash attack animation."""
    cycle = AnimationCycle('attack_slash', loop=False, fps=12)

    # Anticipation
    cycle.frames.append(FrameData(
        bone_rotations={
            'torso': -15.0,
            'right_arm': -60.0,
            'right_forearm': -30.0,
            'left_arm': 10.0,
        },
        root_offset=(2.0, 0.0),
        duration=2.0
    ))

    # Wind-up
    cycle.frames.append(FrameData(
        bone_rotations={
            'torso': -20.0,
            'right_arm': -90.0,
            'right_forearm': -45.0,
            'left_arm': 20.0,
        },
        root_offset=(3.0, -1.0),
        duration=1.0
    ))

    # Strike (fast)
    cycle.frames.append(FrameData(
        bone_rotations={
            'torso': 25.0,
            'right_arm': 45.0,
            'right_forearm': 10.0,
            'left_arm': -15.0,
        },
        root_offset=(-2.0, 0.0),
        duration=1.0
    ))

    # Follow through
    cycle.frames.append(FrameData(
        bone_rotations={
            'torso': 30.0,
            'right_arm': 60.0,
            'right_forearm': 20.0,
            'left_arm': -20.0,
        },
        root_offset=(-3.0, 0.0),
        duration=2.0
    ))

    # Recovery
    cycle.frames.append(FrameData(
        bone_rotations={
            'torso': 10.0,
            'right_arm': 20.0,
            'right_forearm': 5.0,
            'left_arm': -5.0,
        },
        root_offset=(-1.0, 0.0),
        duration=2.0
    ))

    # Return to neutral
    cycle.frames.append(FrameData(
        bone_rotations={
            'torso': 0.0,
            'right_arm': 0.0,
            'right_forearm': 0.0,
            'left_arm': 0.0,
        },
        root_offset=(0.0, 0.0),
        duration=2.0
    ))

    return cycle


def create_attack_stab() -> AnimationCycle:
    """Create a thrusting/stabbing attack animation."""
    cycle = AnimationCycle('attack_stab', loop=False, fps=12)

    # Ready stance
    cycle.frames.append(FrameData(
        bone_rotations={
            'torso': 5.0,
            'right_arm': -30.0,
            'left_arm': 15.0,
        },
        root_offset=(0.0, 0.0),
        duration=1.0
    ))

    # Pull back
    cycle.frames.append(FrameData(
        bone_rotations={
            'torso': -10.0,
            'right_arm': -60.0,
            'left_arm': 30.0,
        },
        root_offset=(2.0, 0.0),
        duration=2.0
    ))

    # Thrust (fast)
    cycle.frames.append(FrameData(
        bone_rotations={
            'torso': 15.0,
            'right_arm': 30.0,
            'left_arm': -20.0,
        },
        root_offset=(-4.0, 0.0),
        duration=1.0
    ))

    # Hold
    cycle.frames.append(FrameData(
        bone_rotations={
            'torso': 15.0,
            'right_arm': 30.0,
            'left_arm': -20.0,
        },
        root_offset=(-4.0, 0.0),
        duration=2.0
    ))

    # Return
    cycle.frames.append(FrameData(
        bone_rotations={
            'torso': 0.0,
            'right_arm': 0.0,
            'left_arm': 0.0,
        },
        root_offset=(0.0, 0.0),
        duration=3.0
    ))

    return cycle


def create_attack_overhead() -> AnimationCycle:
    """Create an overhead smash attack animation."""
    cycle = AnimationCycle('attack_overhead', loop=False, fps=12)

    # Raise weapon
    cycle.frames.append(FrameData(
        bone_rotations={
            'torso': -5.0,
            'head': 10.0,
            'right_arm': -120.0,
            'left_arm': -100.0,
        },
        root_offset=(0.0, -2.0),
        duration=3.0
    ))

    # Peak
    cycle.frames.append(FrameData(
        bone_rotations={
            'torso': -10.0,
            'head': 15.0,
            'right_arm': -150.0,
            'left_arm': -130.0,
        },
        root_offset=(0.0, -3.0),
        duration=2.0
    ))

    # Smash down (fast)
    cycle.frames.append(FrameData(
        bone_rotations={
            'torso': 20.0,
            'head': -10.0,
            'right_arm': 30.0,
            'left_arm': 20.0,
        },
        root_offset=(0.0, 2.0),
        duration=1.0
    ))

    # Impact
    cycle.frames.append(FrameData(
        bone_rotations={
            'torso': 25.0,
            'head': -15.0,
            'right_arm': 40.0,
            'left_arm': 30.0,
        },
        root_offset=(0.0, 3.0),
        duration=2.0
    ))

    # Recovery
    cycle.frames.append(FrameData(
        bone_rotations={
            'torso': 0.0,
            'head': 0.0,
            'right_arm': 0.0,
            'left_arm': 0.0,
        },
        root_offset=(0.0, 0.0),
        duration=4.0
    ))

    return cycle


# =============================================================================
# Jump/Fall Cycles
# =============================================================================

def create_jump_cycle() -> AnimationCycle:
    """Create a jump animation (anticipation -> jump -> fall -> land)."""
    cycle = AnimationCycle('jump', loop=False, fps=12)

    # Anticipation (crouch)
    cycle.frames.append(FrameData(
        bone_rotations={
            'torso': 10.0,
            'left_leg': 30.0,
            'right_leg': 30.0,
            'left_arm': -20.0,
            'right_arm': -20.0,
        },
        root_offset=(0.0, 3.0),
        duration=2.0
    ))

    # Launch
    cycle.frames.append(FrameData(
        bone_rotations={
            'torso': -10.0,
            'left_leg': -20.0,
            'right_leg': -20.0,
            'left_arm': -60.0,
            'right_arm': -60.0,
        },
        root_offset=(0.0, -2.0),
        duration=1.0
    ))

    # Rising
    cycle.frames.append(FrameData(
        bone_rotations={
            'torso': -5.0,
            'left_leg': 10.0,
            'right_leg': -10.0,
            'left_arm': -45.0,
            'right_arm': -45.0,
        },
        root_offset=(0.0, -6.0),
        duration=2.0
    ))

    # Peak
    cycle.frames.append(FrameData(
        bone_rotations={
            'torso': 0.0,
            'left_leg': 20.0,
            'right_leg': -20.0,
            'left_arm': -30.0,
            'right_arm': -30.0,
        },
        root_offset=(0.0, -8.0),
        duration=2.0
    ))

    # Falling
    cycle.frames.append(FrameData(
        bone_rotations={
            'torso': 5.0,
            'left_leg': 25.0,
            'right_leg': 25.0,
            'left_arm': 20.0,
            'right_arm': 20.0,
        },
        root_offset=(0.0, -4.0),
        duration=2.0
    ))

    # Landing
    cycle.frames.append(FrameData(
        bone_rotations={
            'torso': 15.0,
            'left_leg': 40.0,
            'right_leg': 40.0,
            'left_arm': 10.0,
            'right_arm': 10.0,
        },
        root_offset=(0.0, 2.0),
        duration=1.0
    ))

    # Recovery
    cycle.frames.append(FrameData(
        bone_rotations={
            'torso': 0.0,
            'left_leg': 0.0,
            'right_leg': 0.0,
            'left_arm': 0.0,
            'right_arm': 0.0,
        },
        root_offset=(0.0, 0.0),
        duration=2.0
    ))

    return cycle


def create_fall_cycle() -> AnimationCycle:
    """Create a falling/airborne loop animation."""
    cycle = AnimationCycle('fall', loop=True, fps=12)

    # Falling pose 1
    cycle.frames.append(FrameData(
        bone_rotations={
            'torso': 5.0,
            'left_leg': 20.0,
            'right_leg': 25.0,
            'left_arm': 30.0,
            'right_arm': 25.0,
        },
        root_offset=(0.0, 0.0),
        duration=2.0
    ))

    # Falling pose 2 (slight flutter)
    cycle.frames.append(FrameData(
        bone_rotations={
            'torso': 3.0,
            'left_leg': 25.0,
            'right_leg': 20.0,
            'left_arm': 25.0,
            'right_arm': 30.0,
        },
        root_offset=(0.0, 0.5),
        duration=2.0
    ))

    return cycle


# =============================================================================
# Hurt/Death Cycles
# =============================================================================

def create_hurt_cycle() -> AnimationCycle:
    """Create a hurt/hit reaction animation."""
    cycle = AnimationCycle('hurt', loop=False, fps=12)

    # Impact
    cycle.frames.append(FrameData(
        bone_rotations={
            'torso': -15.0,
            'head': 20.0,
            'left_arm': 30.0,
            'right_arm': 40.0,
        },
        root_offset=(3.0, 0.0),
        duration=1.0
    ))

    # Recoil
    cycle.frames.append(FrameData(
        bone_rotations={
            'torso': -25.0,
            'head': 30.0,
            'left_arm': 45.0,
            'right_arm': 55.0,
        },
        root_offset=(5.0, -1.0),
        duration=2.0
    ))

    # Recovery start
    cycle.frames.append(FrameData(
        bone_rotations={
            'torso': -10.0,
            'head': 10.0,
            'left_arm': 15.0,
            'right_arm': 20.0,
        },
        root_offset=(2.0, 0.0),
        duration=2.0
    ))

    # Return to neutral
    cycle.frames.append(FrameData(
        bone_rotations={
            'torso': 0.0,
            'head': 0.0,
            'left_arm': 0.0,
            'right_arm': 0.0,
        },
        root_offset=(0.0, 0.0),
        duration=2.0
    ))

    return cycle


def create_death_cycle() -> AnimationCycle:
    """Create a death/knockout animation."""
    cycle = AnimationCycle('death', loop=False, fps=12)

    # Initial hit
    cycle.frames.append(FrameData(
        bone_rotations={
            'torso': -10.0,
            'head': 15.0,
            'left_arm': 20.0,
            'right_arm': 25.0,
            'left_leg': 5.0,
            'right_leg': 5.0,
        },
        root_offset=(2.0, 0.0),
        duration=1.0
    ))

    # Stagger
    cycle.frames.append(FrameData(
        bone_rotations={
            'torso': -30.0,
            'head': 35.0,
            'left_arm': 60.0,
            'right_arm': 70.0,
            'left_leg': 15.0,
            'right_leg': 10.0,
        },
        root_offset=(5.0, -1.0),
        duration=2.0
    ))

    # Falling
    cycle.frames.append(FrameData(
        bone_rotations={
            'torso': -60.0,
            'head': 50.0,
            'left_arm': 90.0,
            'right_arm': 100.0,
            'left_leg': 30.0,
            'right_leg': 25.0,
        },
        root_offset=(8.0, 2.0),
        duration=2.0
    ))

    # On ground
    cycle.frames.append(FrameData(
        bone_rotations={
            'torso': -80.0,
            'head': 60.0,
            'left_arm': 110.0,
            'right_arm': 120.0,
            'left_leg': 40.0,
            'right_leg': 35.0,
        },
        root_offset=(10.0, 8.0),
        duration=3.0
    ))

    return cycle


# =============================================================================
# Special Actions
# =============================================================================

def create_dodge_roll() -> AnimationCycle:
    """Create a dodge roll animation."""
    cycle = AnimationCycle('dodge_roll', loop=False, fps=16)

    # Crouch start
    cycle.frames.append(FrameData(
        bone_rotations={
            'torso': 30.0,
            'head': -20.0,
            'left_leg': 45.0,
            'right_leg': 45.0,
        },
        root_offset=(0.0, 4.0),
        duration=1.0
    ))

    # Roll phases
    for i in range(4):
        angle = 90.0 * (i + 1)
        cycle.frames.append(FrameData(
            bone_rotations={
                'torso': angle,
                'head': -30.0,
                'left_leg': 60.0,
                'right_leg': 60.0,
                'left_arm': 45.0,
                'right_arm': 45.0,
            },
            root_offset=(-3.0 * (i + 1), 2.0 if i % 2 == 0 else 4.0),
            duration=1.0
        ))

    # Recovery
    cycle.frames.append(FrameData(
        bone_rotations={
            'torso': 15.0,
            'head': 0.0,
            'left_leg': 30.0,
            'right_leg': 30.0,
        },
        root_offset=(-14.0, 3.0),
        duration=1.0
    ))

    # Stand
    cycle.frames.append(FrameData(
        bone_rotations={
            'torso': 0.0,
            'head': 0.0,
            'left_leg': 0.0,
            'right_leg': 0.0,
            'left_arm': 0.0,
            'right_arm': 0.0,
        },
        root_offset=(-16.0, 0.0),
        duration=2.0
    ))

    return cycle


def create_cast_spell() -> AnimationCycle:
    """Create a spell casting animation."""
    cycle = AnimationCycle('cast_spell', loop=False, fps=12)

    # Prepare
    cycle.frames.append(FrameData(
        bone_rotations={
            'torso': -5.0,
            'head': 5.0,
            'left_arm': -30.0,
            'right_arm': -30.0,
        },
        root_offset=(0.0, 1.0),
        duration=2.0
    ))

    # Gather energy
    cycle.frames.append(FrameData(
        bone_rotations={
            'torso': -10.0,
            'head': 10.0,
            'left_arm': -60.0,
            'right_arm': -60.0,
        },
        root_offset=(0.0, 2.0),
        duration=3.0
    ))

    # Cast (thrust forward)
    cycle.frames.append(FrameData(
        bone_rotations={
            'torso': 15.0,
            'head': -5.0,
            'left_arm': 30.0,
            'right_arm': 30.0,
        },
        root_offset=(0.0, -1.0),
        duration=1.0
    ))

    # Hold
    cycle.frames.append(FrameData(
        bone_rotations={
            'torso': 15.0,
            'head': -5.0,
            'left_arm': 35.0,
            'right_arm': 35.0,
        },
        root_offset=(0.0, -1.0),
        duration=3.0
    ))

    # Return
    cycle.frames.append(FrameData(
        bone_rotations={
            'torso': 0.0,
            'head': 0.0,
            'left_arm': 0.0,
            'right_arm': 0.0,
        },
        root_offset=(0.0, 0.0),
        duration=3.0
    ))

    return cycle


# =============================================================================
# Chibi-Specific Cycles
# =============================================================================

def create_chibi_walk_cycle() -> AnimationCycle:
    """Create a cute chibi walk cycle (simplified, bouncy)."""
    cycle = AnimationCycle('chibi_walk', loop=True, fps=8)

    # Chibi characters have minimal limb movement, more bounce
    phases = [
        {'bounce': 0, 'sway': 5, 'arm': 10},
        {'bounce': -2, 'sway': 0, 'arm': 0},
        {'bounce': 0, 'sway': -5, 'arm': -10},
        {'bounce': -2, 'sway': 0, 'arm': 0},
    ]

    for phase in phases:
        cycle.frames.append(FrameData(
            bone_rotations={
                'torso': phase['sway'],
                'left_arm': phase['arm'],
                'right_arm': -phase['arm'],
            },
            root_offset=(0.0, phase['bounce']),
            duration=2.0
        ))

    return cycle


def create_chibi_run_cycle() -> AnimationCycle:
    """Create a cute chibi run cycle (exaggerated bounce)."""
    cycle = AnimationCycle('chibi_run', loop=True, fps=12)

    phases = [
        {'bounce': 0, 'sway': 8, 'arm': 20},
        {'bounce': -4, 'sway': 0, 'arm': 0},
        {'bounce': 0, 'sway': -8, 'arm': -20},
        {'bounce': -4, 'sway': 0, 'arm': 0},
    ]

    for phase in phases:
        cycle.frames.append(FrameData(
            bone_rotations={
                'torso': phase['sway'],
                'head': -phase['sway'] * 0.3,
                'left_arm': phase['arm'],
                'right_arm': -phase['arm'],
            },
            root_offset=(0.0, phase['bounce']),
            duration=1.0
        ))

    return cycle


# =============================================================================
# Animation Cycle Registry
# =============================================================================

ANIMATION_CYCLES = {
    # Walk cycles
    'walk_4': create_walk_cycle_4frame,
    'walk_6': create_walk_cycle_6frame,
    'walk_8': create_walk_cycle_8frame,
    'walk': create_walk_cycle_6frame,  # Default

    # Run cycles
    'run_6': create_run_cycle_6frame,
    'run_8': create_run_cycle_8frame,
    'run': create_run_cycle_6frame,  # Default

    # Attack cycles
    'attack_slash': create_attack_slash,
    'attack_stab': create_attack_stab,
    'attack_overhead': create_attack_overhead,
    'attack': create_attack_slash,  # Default

    # Jump/fall
    'jump': create_jump_cycle,
    'fall': create_fall_cycle,

    # Hurt/death
    'hurt': create_hurt_cycle,
    'death': create_death_cycle,

    # Special
    'dodge_roll': create_dodge_roll,
    'cast_spell': create_cast_spell,

    # Chibi-specific
    'chibi_walk': create_chibi_walk_cycle,
    'chibi_run': create_chibi_run_cycle,
}


def create_cycle(name: str) -> AnimationCycle:
    """Create an animation cycle by name.

    Args:
        name: Cycle name (see ANIMATION_CYCLES for available names)

    Returns:
        AnimationCycle instance

    Raises:
        ValueError: If cycle name not found
    """
    if name not in ANIMATION_CYCLES:
        available = ', '.join(sorted(ANIMATION_CYCLES.keys()))
        raise ValueError(f"Unknown animation cycle '{name}'. Available: {available}")

    return ANIMATION_CYCLES[name]()


def list_cycles() -> List[str]:
    """Get list of available animation cycle names."""
    return sorted(ANIMATION_CYCLES.keys())

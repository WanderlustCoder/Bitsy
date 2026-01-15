"""
Bitsy Animation - Comprehensive animation system.

This module provides:
- Easing functions for smooth interpolation
- Timeline and Track-based keyframe animation
- Procedural animations (breathing, blinking, idle, etc.)
- Pre-built animation cycles (walk, run, attack, etc.)

Example usage:

    # Create a breathing animation
    from bitsy.animation import create_breathing_animation
    timeline = create_breathing_animation(duration=2.0, amplitude=0.05)

    # Get animated values at a specific time
    values = timeline.get_values_at(0.5)

    # Create a walk cycle
    from bitsy.animation import create_cycle
    walk = create_cycle('walk_6')
    timeline = walk.to_timeline()

    # Use easing functions
    from bitsy.animation import apply_easing
    eased_value = apply_easing(0.5, 'ease_out_bounce')
"""

# Easing functions
from .easing import (
    # Core functions
    apply_easing,
    get_easing,
    list_easings,
    # Individual easing functions (commonly used)
    linear,
    ease_in_quad,
    ease_out_quad,
    ease_in_out_quad,
    ease_in_cubic,
    ease_out_cubic,
    ease_in_out_cubic,
    ease_in_sine,
    ease_out_sine,
    ease_in_out_sine,
    ease_out_bounce,
    ease_out_elastic,
    smooth_step,
    # Registry
    EASING_FUNCTIONS,
)

# Timeline and Track system
from .timeline import (
    Keyframe,
    Track,
    Timeline,
    # Utilities
    create_simple_animation,
    create_oscillation,
    create_pulse,
    combine_timelines,
)

# Procedural animations
from .procedural import (
    # Animation creators
    create_breathing_animation,
    create_blinking_animation,
    create_double_blink_animation,
    create_bobbing_animation,
    create_hovering_animation,
    create_squash_stretch_animation,
    create_shake_animation,
    create_pulse_animation,
    create_spin_animation,
    create_idle_animation,
    # Factory function
    create_procedural_animation,
    list_procedural_animations,
    # Registry
    PROCEDURAL_ANIMATIONS,
)

# Animation cycles
from .cycles import (
    # Data classes
    FrameData,
    AnimationCycle,
    # Walk cycles
    create_walk_cycle_4frame,
    create_walk_cycle_6frame,
    create_walk_cycle_8frame,
    # Run cycles
    create_run_cycle_6frame,
    create_run_cycle_8frame,
    # Attack cycles
    create_attack_slash,
    create_attack_stab,
    create_attack_overhead,
    # Jump/Fall
    create_jump_cycle,
    create_fall_cycle,
    # Hurt/Death
    create_hurt_cycle,
    create_death_cycle,
    # Special
    create_dodge_roll,
    create_cast_spell,
    # Chibi-specific
    create_chibi_walk_cycle,
    create_chibi_run_cycle,
    # Factory function
    create_cycle,
    list_cycles,
    # Registry
    ANIMATION_CYCLES,
)

# Animation polish and enhancement
from .polish import (
    # Smear frames
    create_smear_frame,
    add_motion_blur,
    # Anticipation & Follow-through
    add_anticipation,
    add_follow_through,
    add_overshoot,
    add_holds,
    # Timing
    optimize_timing,
    adjust_fps,
    # Convenience
    polish_animation,
    # Secondary motion
    SecondaryMotionSimulator,
    simulate_secondary_motion,
    # Data classes and enums
    MotionData,
    SmearType,
    SecondaryType,
    list_smear_types,
    list_secondary_types,
)

__all__ = [
    # Easing
    'apply_easing',
    'get_easing',
    'list_easings',
    'linear',
    'ease_in_quad',
    'ease_out_quad',
    'ease_in_out_quad',
    'ease_in_cubic',
    'ease_out_cubic',
    'ease_in_out_cubic',
    'ease_in_sine',
    'ease_out_sine',
    'ease_in_out_sine',
    'ease_out_bounce',
    'ease_out_elastic',
    'smooth_step',
    'EASING_FUNCTIONS',

    # Timeline
    'Keyframe',
    'Track',
    'Timeline',
    'create_simple_animation',
    'create_oscillation',
    'create_pulse',
    'combine_timelines',

    # Procedural
    'create_breathing_animation',
    'create_blinking_animation',
    'create_double_blink_animation',
    'create_bobbing_animation',
    'create_hovering_animation',
    'create_squash_stretch_animation',
    'create_shake_animation',
    'create_pulse_animation',
    'create_spin_animation',
    'create_idle_animation',
    'create_procedural_animation',
    'list_procedural_animations',
    'PROCEDURAL_ANIMATIONS',

    # Cycles
    'FrameData',
    'AnimationCycle',
    'create_walk_cycle_4frame',
    'create_walk_cycle_6frame',
    'create_walk_cycle_8frame',
    'create_run_cycle_6frame',
    'create_run_cycle_8frame',
    'create_attack_slash',
    'create_attack_stab',
    'create_attack_overhead',
    'create_jump_cycle',
    'create_fall_cycle',
    'create_hurt_cycle',
    'create_death_cycle',
    'create_dodge_roll',
    'create_cast_spell',
    'create_chibi_walk_cycle',
    'create_chibi_run_cycle',
    'create_cycle',
    'list_cycles',
    'ANIMATION_CYCLES',

    # Polish
    'create_smear_frame',
    'add_motion_blur',
    'add_anticipation',
    'add_follow_through',
    'add_overshoot',
    'add_holds',
    'optimize_timing',
    'adjust_fps',
    'polish_animation',
    'SecondaryMotionSimulator',
    'simulate_secondary_motion',
    'MotionData',
    'SmearType',
    'SecondaryType',
    'list_smear_types',
    'list_secondary_types',
]

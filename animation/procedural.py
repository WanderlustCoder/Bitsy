"""
Procedural - Procedurally generated animations.

Provides functions to generate common animations procedurally:
- Breathing/idle
- Blinking
- Bobbing/floating
- Squash and stretch
"""

import math
import random
from typing import List, Tuple, Optional, Dict, Any

from .timeline import Timeline, Track, create_oscillation, create_pulse


def create_breathing_animation(duration: float = 2.0, amplitude: float = 0.05,
                               fps: int = 12) -> Timeline:
    """Create a subtle breathing animation.

    Animates scale and vertical position for a gentle breathing effect.

    Args:
        duration: Time for one breath cycle (in/out)
        amplitude: Scale change amount (0.05 = 5%)
        fps: Frames per second

    Returns:
        Timeline with breathing animation
    """
    timeline = Timeline('breathing', fps)
    timeline.loop = True

    # Vertical offset (moves up slightly when inhaling)
    y_track = Track('offset_y')
    y_track.add_keyframe(0, 0.0, 'ease_in_out_sine')
    y_track.add_keyframe(duration * 0.5, -amplitude * 10, 'ease_in_out_sine')
    y_track.add_keyframe(duration, 0.0, 'ease_in_out_sine')
    timeline.add_track(y_track)

    # Scale (expands when inhaling)
    scale_x = Track('scale_x')
    scale_x.add_keyframe(0, 1.0, 'ease_in_out_sine')
    scale_x.add_keyframe(duration * 0.5, 1.0 + amplitude * 0.5, 'ease_in_out_sine')
    scale_x.add_keyframe(duration, 1.0, 'ease_in_out_sine')
    timeline.add_track(scale_x)

    scale_y = Track('scale_y')
    scale_y.add_keyframe(0, 1.0, 'ease_in_out_sine')
    scale_y.add_keyframe(duration * 0.5, 1.0 + amplitude, 'ease_in_out_sine')
    scale_y.add_keyframe(duration, 1.0, 'ease_in_out_sine')
    timeline.add_track(scale_y)

    return timeline


def create_blinking_animation(blink_duration: float = 0.15,
                              interval: float = 3.0,
                              fps: int = 12) -> Timeline:
    """Create a blinking animation.

    Args:
        blink_duration: How long the blink takes
        interval: Time between blinks
        fps: Frames per second

    Returns:
        Timeline with blink animation
    """
    timeline = Timeline('blink', fps)
    timeline.loop = True

    eye_track = Track('eye_openness')

    # Eyes open for most of the interval
    eye_track.add_keyframe(0, 1.0, 'linear')

    # Start closing
    eye_track.add_keyframe(interval - blink_duration, 1.0, 'ease_in')

    # Fully closed
    eye_track.add_keyframe(interval - blink_duration / 2, 0.0, 'ease_out')

    # Open again
    eye_track.add_keyframe(interval, 1.0, 'ease_out')

    timeline.add_track(eye_track)

    return timeline


def create_double_blink_animation(blink_duration: float = 0.1,
                                  pause: float = 0.1,
                                  interval: float = 4.0,
                                  fps: int = 12) -> Timeline:
    """Create a double-blink animation (more expressive).

    Args:
        blink_duration: Duration of each blink
        pause: Pause between double blinks
        interval: Time between blink pairs
        fps: Frames per second

    Returns:
        Timeline with double blink
    """
    timeline = Timeline('double_blink', fps)
    timeline.loop = True

    eye_track = Track('eye_openness')

    # Open
    eye_track.add_keyframe(0, 1.0, 'linear')

    # First blink
    t = interval - blink_duration * 2 - pause
    eye_track.add_keyframe(t, 1.0, 'ease_in')
    eye_track.add_keyframe(t + blink_duration * 0.4, 0.0, 'ease_out')
    eye_track.add_keyframe(t + blink_duration, 1.0, 'ease_out')

    # Second blink
    t = t + blink_duration + pause
    eye_track.add_keyframe(t, 1.0, 'ease_in')
    eye_track.add_keyframe(t + blink_duration * 0.4, 0.0, 'ease_out')
    eye_track.add_keyframe(t + blink_duration, 1.0, 'ease_out')

    timeline.add_track(eye_track)

    return timeline


def create_bobbing_animation(amplitude: float = 2.0, period: float = 1.0,
                             fps: int = 12) -> Timeline:
    """Create a floating/bobbing animation.

    Good for floating items, ghosts, etc.

    Args:
        amplitude: Vertical movement amount in pixels
        period: Time for one bob cycle
        fps: Frames per second

    Returns:
        Timeline with bobbing animation
    """
    timeline = Timeline('bobbing', fps)
    timeline.loop = True

    y_track = Track('offset_y')
    y_track.add_keyframe(0, 0.0, 'ease_in_out_sine')
    y_track.add_keyframe(period * 0.5, -amplitude, 'ease_in_out_sine')
    y_track.add_keyframe(period, 0.0, 'ease_in_out_sine')
    timeline.add_track(y_track)

    return timeline


def create_hovering_animation(amplitude: float = 2.0, period: float = 2.0,
                              rotation_amount: float = 3.0,
                              fps: int = 12) -> Timeline:
    """Create a hovering animation with slight rotation.

    More complex than bobbing - includes subtle rotation.

    Args:
        amplitude: Vertical movement in pixels
        period: Time for one cycle
        rotation_amount: Rotation in degrees
        fps: Frames per second

    Returns:
        Timeline with hovering animation
    """
    timeline = Timeline('hovering', fps)
    timeline.loop = True

    # Vertical bob
    y_track = Track('offset_y')
    y_track.add_keyframe(0, 0.0, 'ease_in_out_sine')
    y_track.add_keyframe(period * 0.5, -amplitude, 'ease_in_out_sine')
    y_track.add_keyframe(period, 0.0, 'ease_in_out_sine')
    timeline.add_track(y_track)

    # Slight rotation
    rot_track = Track('rotation')
    rot_track.add_keyframe(0, 0.0, 'ease_in_out_sine')
    rot_track.add_keyframe(period * 0.25, rotation_amount, 'ease_in_out_sine')
    rot_track.add_keyframe(period * 0.75, -rotation_amount, 'ease_in_out_sine')
    rot_track.add_keyframe(period, 0.0, 'ease_in_out_sine')
    timeline.add_track(rot_track)

    return timeline


def create_squash_stretch_animation(squash_amount: float = 0.2,
                                    stretch_amount: float = 0.15,
                                    duration: float = 0.3,
                                    fps: int = 12) -> Timeline:
    """Create a squash and stretch animation.

    Good for jumps, impacts, bounces.

    Args:
        squash_amount: How much to squash (0.2 = 20% shorter)
        stretch_amount: How much to stretch (0.15 = 15% taller)
        duration: Total animation duration
        fps: Frames per second

    Returns:
        Timeline with squash/stretch
    """
    timeline = Timeline('squash_stretch', fps)

    # Vertical scale (stretch up, then squash down)
    scale_y = Track('scale_y')
    scale_y.add_keyframe(0, 1.0, 'ease_out')
    scale_y.add_keyframe(duration * 0.3, 1.0 + stretch_amount, 'ease_in')
    scale_y.add_keyframe(duration * 0.6, 1.0 - squash_amount, 'ease_out_bounce')
    scale_y.add_keyframe(duration, 1.0, 'ease_out')
    timeline.add_track(scale_y)

    # Horizontal scale (inverse - squash when stretched)
    scale_x = Track('scale_x')
    scale_x.add_keyframe(0, 1.0, 'ease_out')
    scale_x.add_keyframe(duration * 0.3, 1.0 - stretch_amount * 0.5, 'ease_in')
    scale_x.add_keyframe(duration * 0.6, 1.0 + squash_amount * 0.5, 'ease_out_bounce')
    scale_x.add_keyframe(duration, 1.0, 'ease_out')
    timeline.add_track(scale_x)

    return timeline


def create_shake_animation(intensity: float = 3.0, duration: float = 0.3,
                           frequency: int = 8, fps: int = 24) -> Timeline:
    """Create a shaking/trembling animation.

    Good for hit reactions, screen shake, etc.

    Args:
        intensity: Maximum shake offset in pixels
        duration: Total shake duration
        frequency: Number of shakes
        fps: Frames per second

    Returns:
        Timeline with shake animation
    """
    timeline = Timeline('shake', fps)

    rng = random.Random(42)  # Deterministic

    x_track = Track('offset_x')
    y_track = Track('offset_y')

    step = duration / frequency
    for i in range(frequency + 1):
        t = i * step
        # Decay intensity over time
        decay = 1.0 - (i / frequency)
        current_intensity = intensity * decay

        # Random offset
        ox = rng.uniform(-current_intensity, current_intensity)
        oy = rng.uniform(-current_intensity, current_intensity)

        x_track.add_keyframe(t, ox, 'linear')
        y_track.add_keyframe(t, oy, 'linear')

    # Return to center
    x_track.add_keyframe(duration, 0.0, 'ease_out')
    y_track.add_keyframe(duration, 0.0, 'ease_out')

    timeline.add_track(x_track)
    timeline.add_track(y_track)

    return timeline


def create_pulse_animation(scale_amount: float = 0.1, duration: float = 0.5,
                           fps: int = 12) -> Timeline:
    """Create a pulsing/heartbeat animation.

    Args:
        scale_amount: Scale change (0.1 = 10% larger)
        duration: Time for one pulse
        fps: Frames per second

    Returns:
        Timeline with pulse animation
    """
    timeline = Timeline('pulse', fps)
    timeline.loop = True

    scale_track = Track('scale')
    scale_track.add_keyframe(0, 1.0, 'ease_out')
    scale_track.add_keyframe(duration * 0.15, 1.0 + scale_amount, 'ease_in')
    scale_track.add_keyframe(duration * 0.3, 1.0 + scale_amount * 0.5, 'ease_out')
    scale_track.add_keyframe(duration * 0.45, 1.0 + scale_amount * 0.8, 'ease_in')
    scale_track.add_keyframe(duration, 1.0, 'ease_out')

    timeline.add_track(scale_track)

    return timeline


def create_spin_animation(rotations: float = 1.0, duration: float = 1.0,
                          easing: str = 'linear', fps: int = 12) -> Timeline:
    """Create a spinning animation.

    Args:
        rotations: Number of full rotations
        duration: Total duration
        easing: Easing function
        fps: Frames per second

    Returns:
        Timeline with spin animation
    """
    timeline = Timeline('spin', fps)

    rot_track = Track('rotation')
    rot_track.add_keyframe(0, 0.0, easing)
    rot_track.add_keyframe(duration, 360.0 * rotations, easing)

    timeline.add_track(rot_track)

    return timeline


def create_idle_animation(breathing: bool = True, blinking: bool = True,
                          subtle_sway: bool = True,
                          duration: float = 4.0, fps: int = 12) -> Timeline:
    """Create a comprehensive idle animation.

    Combines breathing, blinking, and subtle movement.

    Args:
        breathing: Include breathing
        blinking: Include blinking
        subtle_sway: Include slight side-to-side movement
        duration: Base loop duration
        fps: Frames per second

    Returns:
        Combined idle animation
    """
    timeline = Timeline('idle', fps)
    timeline.loop = True

    if breathing:
        # Breathing - scale and position
        breath_period = 2.5

        y_track = Track('breath_y')
        y_track.add_keyframe(0, 0.0, 'ease_in_out_sine')
        y_track.add_keyframe(breath_period * 0.5, -1.0, 'ease_in_out_sine')
        y_track.add_keyframe(breath_period, 0.0, 'ease_in_out_sine')
        # Loop within duration
        t = breath_period
        while t < duration:
            y_track.add_keyframe(t + breath_period * 0.5, -1.0, 'ease_in_out_sine')
            y_track.add_keyframe(t + breath_period, 0.0, 'ease_in_out_sine')
            t += breath_period
        timeline.add_track(y_track)

        scale_track = Track('breath_scale')
        scale_track.add_keyframe(0, 1.0, 'ease_in_out_sine')
        scale_track.add_keyframe(breath_period * 0.5, 1.02, 'ease_in_out_sine')
        scale_track.add_keyframe(breath_period, 1.0, 'ease_in_out_sine')
        t = breath_period
        while t < duration:
            scale_track.add_keyframe(t + breath_period * 0.5, 1.02, 'ease_in_out_sine')
            scale_track.add_keyframe(t + breath_period, 1.0, 'ease_in_out_sine')
            t += breath_period
        timeline.add_track(scale_track)

    if blinking:
        # Blink at a specific point in the loop
        blink_time = duration * 0.6
        blink_duration = 0.15

        eye_track = Track('eye_openness')
        eye_track.add_keyframe(0, 1.0, 'linear')
        eye_track.add_keyframe(blink_time, 1.0, 'ease_in')
        eye_track.add_keyframe(blink_time + blink_duration * 0.4, 0.0, 'ease_out')
        eye_track.add_keyframe(blink_time + blink_duration, 1.0, 'ease_out')
        eye_track.add_keyframe(duration, 1.0, 'linear')
        timeline.add_track(eye_track)

    if subtle_sway:
        # Gentle side-to-side movement
        sway_period = 3.0
        sway_amount = 0.5

        x_track = Track('sway_x')
        x_track.add_keyframe(0, 0.0, 'ease_in_out_sine')
        x_track.add_keyframe(sway_period * 0.25, sway_amount, 'ease_in_out_sine')
        x_track.add_keyframe(sway_period * 0.75, -sway_amount, 'ease_in_out_sine')
        x_track.add_keyframe(sway_period, 0.0, 'ease_in_out_sine')
        t = sway_period
        while t < duration:
            x_track.add_keyframe(t + sway_period * 0.25, sway_amount, 'ease_in_out_sine')
            x_track.add_keyframe(t + sway_period * 0.75, -sway_amount, 'ease_in_out_sine')
            x_track.add_keyframe(t + sway_period, 0.0, 'ease_in_out_sine')
            t += sway_period
        timeline.add_track(x_track)

    return timeline


# =============================================================================
# Preset Animations Registry
# =============================================================================

PROCEDURAL_ANIMATIONS = {
    'breathing': create_breathing_animation,
    'blink': create_blinking_animation,
    'double_blink': create_double_blink_animation,
    'bobbing': create_bobbing_animation,
    'hovering': create_hovering_animation,
    'squash_stretch': create_squash_stretch_animation,
    'shake': create_shake_animation,
    'pulse': create_pulse_animation,
    'spin': create_spin_animation,
    'idle': create_idle_animation,
}


def create_procedural_animation(name: str, **kwargs) -> Timeline:
    """Create a procedural animation by name.

    Args:
        name: Animation name
        **kwargs: Parameters for the animation

    Returns:
        Timeline with the animation
    """
    if name not in PROCEDURAL_ANIMATIONS:
        available = ', '.join(PROCEDURAL_ANIMATIONS.keys())
        raise ValueError(f"Unknown procedural animation '{name}'. Available: {available}")

    return PROCEDURAL_ANIMATIONS[name](**kwargs)


def list_procedural_animations() -> List[str]:
    """Get list of available procedural animations."""
    return list(PROCEDURAL_ANIMATIONS.keys())

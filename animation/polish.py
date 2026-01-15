"""
Animation Polish - Enhancement tools for professional animation quality.

Provides:
- Smear frames for fast motion
- Motion blur effects
- Anticipation frames (wind-up before action)
- Follow-through/overshoot (settling after action)
- Secondary motion (hair, cloth, tail physics)
- Hold frames (pause on key poses)
- Timing optimization
"""

import math
import random
from typing import List, Tuple, Optional, Dict, Any, Callable
from dataclasses import dataclass, field
from enum import Enum

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Canvas
from core.animation import Animation, Keyframe
from core.color import lerp_color


class SmearType(Enum):
    """Types of smear frame effects."""
    STRETCH = 'stretch'      # Stretch in motion direction
    MULTIPLE = 'multiple'    # Multiple ghost images
    DIRECTIONAL = 'directional'  # Motion lines
    BLEND = 'blend'          # Alpha blend between frames


class SecondaryType(Enum):
    """Types of secondary motion."""
    HAIR = 'hair'
    CLOTH = 'cloth'
    TAIL = 'tail'
    CHAIN = 'chain'
    RIBBON = 'ribbon'


@dataclass
class MotionData:
    """Motion information between frames."""
    dx: float = 0.0  # Horizontal movement
    dy: float = 0.0  # Vertical movement
    rotation: float = 0.0  # Rotation change
    scale_change: float = 0.0  # Scale change

    @property
    def speed(self) -> float:
        """Calculate speed from dx/dy."""
        return math.sqrt(self.dx * self.dx + self.dy * self.dy)

    @property
    def direction(self) -> float:
        """Calculate direction angle in radians."""
        return math.atan2(self.dy, self.dx)


@dataclass
class SecondaryPoint:
    """A point in a secondary motion chain (hair strand, cloth corner, etc.)."""
    x: float
    y: float
    vx: float = 0.0  # Velocity x
    vy: float = 0.0  # Velocity y
    damping: float = 0.8  # Velocity damping factor
    stiffness: float = 0.5  # Spring stiffness to rest position
    rest_x: float = 0.0  # Rest position x
    rest_y: float = 0.0  # Rest position y


# ==================== Smear Frames ====================

def create_smear_frame(frame1: Canvas, frame2: Canvas,
                       intensity: float = 0.5,
                       smear_type: str = 'blend') -> Canvas:
    """Create a smear frame between two animation frames.

    Args:
        frame1: First frame (previous)
        frame2: Second frame (next)
        intensity: Smear strength 0.0-1.0
        smear_type: Type of smear ('blend', 'stretch', 'multiple')

    Returns:
        New Canvas with smear effect
    """
    if smear_type == 'stretch':
        return _create_stretch_smear(frame1, frame2, intensity)
    elif smear_type == 'multiple':
        return _create_multiple_smear(frame1, frame2, intensity)
    else:  # Default to blend
        return _create_blend_smear(frame1, frame2, intensity)


def _create_blend_smear(frame1: Canvas, frame2: Canvas, intensity: float) -> Canvas:
    """Create smear by blending frames with trails."""
    result = Canvas(frame1.width, frame1.height)

    # Detect motion by comparing frames
    motion = _detect_motion(frame1, frame2)

    # Create multiple blended copies offset by motion
    num_copies = max(2, int(3 + intensity * 5))

    for i in range(num_copies):
        t = i / (num_copies - 1)
        alpha = int(255 * (1 - t * intensity * 0.7))

        # Offset based on motion
        offset_x = int(motion.dx * t * intensity)
        offset_y = int(motion.dy * t * intensity)

        # Blend frame at offset
        _blend_frame_at_offset(result, frame1, offset_x, offset_y, alpha)

    # Add the destination frame on top
    result.blit(frame2, 0, 0)

    return result


def _create_stretch_smear(frame1: Canvas, frame2: Canvas, intensity: float) -> Canvas:
    """Create smear by stretching pixels in motion direction."""
    result = Canvas(frame1.width, frame1.height)
    motion = _detect_motion(frame1, frame2)

    stretch_amount = int(motion.speed * intensity * 0.5)

    for y in range(frame1.height):
        for x in range(frame1.width):
            pixel1 = frame1.get_pixel(x, y)
            pixel2 = frame2.get_pixel(x, y)

            if pixel1[3] > 0 or pixel2[3] > 0:
                # Stretch from pixel1 towards pixel2
                for s in range(stretch_amount + 1):
                    t = s / max(1, stretch_amount)
                    sx = x + int(motion.dx * t * intensity * 0.3)
                    sy = y + int(motion.dy * t * intensity * 0.3)

                    if 0 <= sx < result.width and 0 <= sy < result.height:
                        color = lerp_color(pixel1, pixel2, t)
                        alpha = int(color[3] * (1 - t * 0.5))
                        color = (color[0], color[1], color[2], alpha)
                        if alpha > result.get_pixel(sx, sy)[3]:
                            result.set_pixel_solid(sx, sy, color)

    # Final frame on top
    result.blit(frame2, 0, 0)
    return result


def _create_multiple_smear(frame1: Canvas, frame2: Canvas, intensity: float) -> Canvas:
    """Create smear with multiple ghost images."""
    result = Canvas(frame1.width, frame1.height)
    motion = _detect_motion(frame1, frame2)

    num_ghosts = max(2, int(3 + intensity * 4))

    for i in range(num_ghosts):
        t = i / num_ghosts
        alpha = int(100 * (1 - t))

        offset_x = int(-motion.dx * t * 0.5)
        offset_y = int(-motion.dy * t * 0.5)

        _blend_frame_at_offset(result, frame1, offset_x, offset_y, alpha)

    result.blit(frame2, 0, 0)
    return result


def _detect_motion(frame1: Canvas, frame2: Canvas) -> MotionData:
    """Detect motion between two frames by comparing pixel positions."""
    # Find center of mass for non-transparent pixels in each frame
    cx1, cy1, count1 = _get_center_of_mass(frame1)
    cx2, cy2, count2 = _get_center_of_mass(frame2)

    if count1 == 0 or count2 == 0:
        return MotionData()

    return MotionData(
        dx=cx2 - cx1,
        dy=cy2 - cy1
    )


def _get_center_of_mass(canvas: Canvas) -> Tuple[float, float, int]:
    """Get center of mass of non-transparent pixels."""
    total_x, total_y, count = 0.0, 0.0, 0

    for y in range(canvas.height):
        for x in range(canvas.width):
            if canvas.get_pixel(x, y)[3] > 128:
                total_x += x
                total_y += y
                count += 1

    if count == 0:
        return canvas.width / 2, canvas.height / 2, 0

    return total_x / count, total_y / count, count


def _blend_frame_at_offset(dest: Canvas, src: Canvas,
                           offset_x: int, offset_y: int, alpha: int):
    """Blend source frame onto destination at offset with alpha."""
    for y in range(src.height):
        for x in range(src.width):
            dx = x + offset_x
            dy = y + offset_y

            if 0 <= dx < dest.width and 0 <= dy < dest.height:
                pixel = src.get_pixel(x, y)
                if pixel[3] > 0:
                    new_alpha = int(pixel[3] * alpha / 255)
                    if new_alpha > 0:
                        color = (pixel[0], pixel[1], pixel[2], new_alpha)
                        existing = dest.get_pixel(dx, dy)
                        if new_alpha > existing[3]:
                            dest.set_pixel_solid(dx, dy, color)


def add_motion_blur(animation: Animation, blur_frames: int = 1) -> Animation:
    """Add motion blur between frames in an animation.

    Args:
        animation: Source animation
        blur_frames: Number of blur frames to insert between keyframes

    Returns:
        New Animation with motion blur frames inserted
    """
    if animation.frame_count < 2:
        return animation

    result = Animation(animation.name + "_blurred", animation.fps)
    result.loop = animation.loop

    for i in range(animation.frame_count):
        # Add original frame
        kf = animation.keyframes[i]
        result.add_frame(kf.frame.copy(), kf.duration * 0.5, kf.name)

        # Add blur frames to next frame
        if i < animation.frame_count - 1 or animation.loop:
            next_idx = (i + 1) % animation.frame_count
            next_frame = animation.keyframes[next_idx].frame

            for b in range(blur_frames):
                t = (b + 1) / (blur_frames + 1)
                blur_frame = create_smear_frame(
                    kf.frame, next_frame,
                    intensity=0.3 + t * 0.4,
                    smear_type='blend'
                )
                result.add_frame(blur_frame, kf.duration * 0.5 / blur_frames,
                               f"{kf.name}_blur_{b}")

    return result


# ==================== Anticipation & Follow-through ====================

def add_anticipation(animation: Animation, frames: int = 2,
                     scale_factor: float = 0.9,
                     offset_direction: Tuple[float, float] = (0, 1)) -> Animation:
    """Add anticipation frames before the first frame.

    Anticipation is a small "wind-up" motion before the main action.

    Args:
        animation: Source animation
        frames: Number of anticipation frames to add
        scale_factor: Scale multiplier for squash effect
        offset_direction: Direction of anticipation movement (x, y normalized)

    Returns:
        New Animation with anticipation frames prepended
    """
    if animation.frame_count == 0:
        return animation

    result = Animation(animation.name + "_antic", animation.fps)
    result.loop = animation.loop

    first_frame = animation.keyframes[0].frame
    first_duration = animation.keyframes[0].duration

    # Create anticipation frames
    for i in range(frames):
        t = (i + 1) / (frames + 1)
        # Ease in for smooth anticipation
        eased_t = t * t  # Quadratic ease in

        antic_frame = _create_transform_frame(
            first_frame,
            scale_x=1 + (scale_factor - 1) * eased_t,
            scale_y=1 + (1 / scale_factor - 1) * eased_t,  # Inverse for squash
            offset_x=int(offset_direction[0] * eased_t * 2),
            offset_y=int(offset_direction[1] * eased_t * 2)
        )
        result.add_frame(antic_frame, first_duration / frames, f"antic_{i}")

    # Add all original frames
    for kf in animation.keyframes:
        result.add_frame(kf.frame.copy(), kf.duration, kf.name)

    return result


def add_follow_through(animation: Animation, frames: int = 2,
                       overshoot: float = 0.1) -> Animation:
    """Add follow-through frames after the last frame.

    Follow-through shows the character settling after action with overshoot.

    Args:
        animation: Source animation
        frames: Number of follow-through frames to add
        overshoot: Amount of overshoot (0.0-1.0)

    Returns:
        New Animation with follow-through frames appended
    """
    if animation.frame_count == 0:
        return animation

    result = Animation(animation.name + "_follow", animation.fps)
    result.loop = False  # Follow-through usually ends the animation

    # Add all original frames
    for kf in animation.keyframes:
        result.add_frame(kf.frame.copy(), kf.duration, kf.name)

    last_frame = animation.keyframes[-1].frame
    last_duration = animation.keyframes[-1].duration

    # Detect motion direction from last two frames
    if animation.frame_count >= 2:
        motion = _detect_motion(
            animation.keyframes[-2].frame,
            animation.keyframes[-1].frame
        )
    else:
        motion = MotionData()

    # Create follow-through frames with decreasing overshoot
    for i in range(frames):
        t = (i + 1) / (frames + 1)
        # Bounce/settle easing
        bounce = math.sin(t * math.pi) * (1 - t) * overshoot

        follow_frame = _create_transform_frame(
            last_frame,
            offset_x=int(motion.dx * bounce * 3),
            offset_y=int(motion.dy * bounce * 3),
            scale_x=1 + bounce * 0.2,
            scale_y=1 - bounce * 0.1
        )
        result.add_frame(follow_frame, last_duration / frames, f"follow_{i}")

    return result


def add_overshoot(animation: Animation, amount: float = 0.15,
                  settle_frames: int = 3) -> Animation:
    """Add overshoot and settle to the end of an animation.

    The character goes slightly past the end pose then settles back.

    Args:
        animation: Source animation
        amount: Overshoot amount (0.0-1.0)
        settle_frames: Number of frames to settle

    Returns:
        New Animation with overshoot settling
    """
    if animation.frame_count < 2:
        return animation

    result = Animation(animation.name + "_overshoot", animation.fps)
    result.loop = False

    # Add all original frames
    for kf in animation.keyframes:
        result.add_frame(kf.frame.copy(), kf.duration, kf.name)

    # Get motion from last two frames
    second_last = animation.keyframes[-2].frame
    last = animation.keyframes[-1].frame
    motion = _detect_motion(second_last, last)

    # Create overshoot frame
    overshoot_frame = _create_transform_frame(
        last,
        offset_x=int(motion.dx * amount * 5),
        offset_y=int(motion.dy * amount * 5)
    )
    result.add_frame(overshoot_frame, 0.5, "overshoot")

    # Settle back frames
    for i in range(settle_frames):
        t = (i + 1) / settle_frames
        settle_amount = 1 - t
        settle_frame = _create_transform_frame(
            last,
            offset_x=int(motion.dx * amount * 5 * settle_amount),
            offset_y=int(motion.dy * amount * 5 * settle_amount)
        )
        result.add_frame(settle_frame, 0.3, f"settle_{i}")

    return result


def _create_transform_frame(source: Canvas,
                            scale_x: float = 1.0, scale_y: float = 1.0,
                            offset_x: int = 0, offset_y: int = 0) -> Canvas:
    """Create a transformed copy of a frame."""
    result = Canvas(source.width, source.height)

    cx = source.width / 2
    cy = source.height / 2

    for y in range(source.height):
        for x in range(source.width):
            # Apply inverse transform to find source pixel
            src_x = int((x - cx - offset_x) / scale_x + cx)
            src_y = int((y - cy - offset_y) / scale_y + cy)

            if 0 <= src_x < source.width and 0 <= src_y < source.height:
                pixel = source.get_pixel(src_x, src_y)
                if pixel[3] > 0:
                    result.set_pixel_solid(x, y, pixel)

    return result


# ==================== Hold Frames ====================

def add_holds(animation: Animation, key_frame_indices: List[int],
              hold_duration: float = 2.0) -> Animation:
    """Add hold frames at key poses.

    Holds create pauses on important poses for emphasis.

    Args:
        animation: Source animation
        key_frame_indices: Indices of frames to hold
        hold_duration: Duration multiplier for held frames

    Returns:
        New Animation with holds added
    """
    result = Animation(animation.name + "_holds", animation.fps)
    result.loop = animation.loop

    for i, kf in enumerate(animation.keyframes):
        if i in key_frame_indices:
            # Extended hold duration
            result.add_frame(kf.frame.copy(), kf.duration * hold_duration,
                           kf.name + "_hold")
        else:
            result.add_frame(kf.frame.copy(), kf.duration, kf.name)

    return result


# ==================== Secondary Motion ====================

class SecondaryMotionSimulator:
    """Simulates physics-lite secondary motion for hair, cloth, etc."""

    def __init__(self, num_points: int = 5,
                 damping: float = 0.7,
                 stiffness: float = 0.4,
                 gravity: float = 0.5):
        """Initialize secondary motion simulator.

        Args:
            num_points: Number of points in the chain
            damping: Velocity damping (0-1, higher = more damping)
            stiffness: Spring stiffness (0-1, higher = snappier)
            gravity: Downward gravity force
        """
        self.num_points = num_points
        self.damping = damping
        self.stiffness = stiffness
        self.gravity = gravity
        self.points: List[SecondaryPoint] = []
        self._initialized = False

    def initialize(self, start_x: float, start_y: float,
                   direction: Tuple[float, float] = (0, 1),
                   spacing: float = 3.0):
        """Initialize the point chain.

        Args:
            start_x: Anchor point x
            start_y: Anchor point y
            direction: Direction the chain extends (normalized)
            spacing: Distance between points
        """
        self.points = []

        for i in range(self.num_points):
            x = start_x + direction[0] * spacing * i
            y = start_y + direction[1] * spacing * i

            point = SecondaryPoint(
                x=x, y=y,
                rest_x=x, rest_y=y,
                damping=self.damping,
                stiffness=self.stiffness
            )
            self.points.append(point)

        self._initialized = True

    def update(self, anchor_x: float, anchor_y: float,
               velocity_x: float = 0, velocity_y: float = 0):
        """Update the simulation for one frame.

        Args:
            anchor_x: New anchor position x
            anchor_y: New anchor position y
            velocity_x: Anchor velocity x (for inertia)
            velocity_y: Anchor velocity y
        """
        if not self._initialized or not self.points:
            return

        # First point follows anchor
        self.points[0].x = anchor_x
        self.points[0].y = anchor_y

        # Update rest positions relative to anchor
        dx = anchor_x - self.points[0].rest_x
        dy = anchor_y - self.points[0].rest_y

        for point in self.points:
            point.rest_x += dx
            point.rest_y += dy

        # Simulate each subsequent point
        for i in range(1, len(self.points)):
            point = self.points[i]
            prev = self.points[i - 1]

            # Spring force toward rest position relative to previous point
            spring_x = (prev.x + (point.rest_x - prev.rest_x) - point.x) * point.stiffness
            spring_y = (prev.y + (point.rest_y - prev.rest_y) - point.y) * point.stiffness

            # Add inherited velocity with delay
            inherited_vx = -velocity_x * 0.3 * (i / len(self.points))
            inherited_vy = -velocity_y * 0.3 * (i / len(self.points))

            # Update velocity
            point.vx = (point.vx + spring_x + inherited_vx) * point.damping
            point.vy = (point.vy + spring_y + inherited_vy + self.gravity) * point.damping

            # Update position
            point.x += point.vx
            point.y += point.vy

    def get_positions(self) -> List[Tuple[float, float]]:
        """Get current positions of all points."""
        return [(p.x, p.y) for p in self.points]

    def render_to_canvas(self, canvas: Canvas, color: Tuple[int, int, int, int],
                         thickness: int = 1):
        """Render the chain to a canvas.

        Args:
            canvas: Target canvas
            color: Line color
            thickness: Line thickness
        """
        positions = self.get_positions()

        for i in range(len(positions) - 1):
            x1, y1 = int(positions[i][0]), int(positions[i][1])
            x2, y2 = int(positions[i + 1][0]), int(positions[i + 1][1])

            # Draw line between points
            _draw_thick_line(canvas, x1, y1, x2, y2, color, thickness)


def _draw_thick_line(canvas: Canvas, x1: int, y1: int, x2: int, y2: int,
                     color: Tuple[int, int, int, int], thickness: int):
    """Draw a line with thickness."""
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    steps = max(dx, dy, 1)

    for i in range(steps + 1):
        t = i / steps if steps > 0 else 0
        x = int(x1 + (x2 - x1) * t)
        y = int(y1 + (y2 - y1) * t)

        # Draw thickness
        for tx in range(-thickness // 2, thickness // 2 + 1):
            for ty in range(-thickness // 2, thickness // 2 + 1):
                px, py = x + tx, y + ty
                if 0 <= px < canvas.width and 0 <= py < canvas.height:
                    canvas.set_pixel_solid(px, py, color)


def simulate_secondary_motion(animation: Animation,
                              anchor_track: List[Tuple[float, float]],
                              motion_type: str = 'hair',
                              num_points: int = 5,
                              color: Tuple[int, int, int, int] = (100, 80, 60, 255)) -> Animation:
    """Add secondary motion overlay to an animation.

    Args:
        animation: Source animation
        anchor_track: List of (x, y) anchor positions per frame
        motion_type: Type of secondary motion ('hair', 'cloth', 'tail')
        num_points: Number of simulation points
        color: Color for the secondary element

    Returns:
        New Animation with secondary motion rendered
    """
    if len(anchor_track) != animation.frame_count:
        raise ValueError("anchor_track must have same length as animation frames")

    result = Animation(animation.name + f"_{motion_type}", animation.fps)
    result.loop = animation.loop

    # Configure simulator based on type
    configs = {
        'hair': {'damping': 0.7, 'stiffness': 0.3, 'gravity': 0.3},
        'cloth': {'damping': 0.6, 'stiffness': 0.2, 'gravity': 0.5},
        'tail': {'damping': 0.75, 'stiffness': 0.4, 'gravity': 0.2},
        'chain': {'damping': 0.5, 'stiffness': 0.1, 'gravity': 0.8},
        'ribbon': {'damping': 0.8, 'stiffness': 0.15, 'gravity': 0.1},
    }
    config = configs.get(motion_type, configs['hair'])

    sim = SecondaryMotionSimulator(num_points, **config)

    # Initialize at first anchor position
    ax, ay = anchor_track[0]
    sim.initialize(ax, ay, direction=(0, 1), spacing=2.0)

    prev_x, prev_y = ax, ay

    for i, kf in enumerate(animation.keyframes):
        ax, ay = anchor_track[i]

        # Calculate velocity
        vx = ax - prev_x
        vy = ay - prev_y

        # Update simulation
        sim.update(ax, ay, vx, vy)

        # Create frame with secondary motion
        frame = kf.frame.copy()
        sim.render_to_canvas(frame, color, thickness=1)

        result.add_frame(frame, kf.duration, kf.name)

        prev_x, prev_y = ax, ay

    return result


# ==================== Timing Optimization ====================

def optimize_timing(animation: Animation,
                    min_duration: float = 0.5,
                    max_duration: float = 3.0) -> Animation:
    """Optimize animation timing for smoother motion.

    Adjusts frame durations based on motion amount between frames.
    Faster motion = shorter frames, slower motion = longer frames.

    Args:
        animation: Source animation
        min_duration: Minimum frame duration
        max_duration: Maximum frame duration

    Returns:
        New Animation with optimized timing
    """
    if animation.frame_count < 2:
        return animation

    result = Animation(animation.name + "_optimized", animation.fps)
    result.loop = animation.loop

    # Calculate motion for each frame transition
    motions = []
    for i in range(animation.frame_count):
        next_i = (i + 1) % animation.frame_count
        motion = _detect_motion(
            animation.keyframes[i].frame,
            animation.keyframes[next_i].frame
        )
        motions.append(motion.speed)

    max_motion = max(motions) if motions else 1
    if max_motion == 0:
        max_motion = 1

    # Adjust timing based on motion
    for i, kf in enumerate(animation.keyframes):
        motion_ratio = motions[i] / max_motion

        # More motion = shorter duration (faster movement)
        # Less motion = longer duration (hold poses)
        duration = max_duration - (max_duration - min_duration) * motion_ratio
        duration = max(min_duration, min(max_duration, duration))

        result.add_frame(kf.frame.copy(), duration, kf.name)

    return result


def adjust_fps(animation: Animation, target_fps: int) -> Animation:
    """Adjust animation to a new FPS by scaling durations.

    Args:
        animation: Source animation
        target_fps: Target frames per second

    Returns:
        New Animation with adjusted FPS
    """
    result = Animation(animation.name, target_fps)
    result.loop = animation.loop

    scale = animation.fps / target_fps

    for kf in animation.keyframes:
        result.add_frame(kf.frame.copy(), kf.duration * scale, kf.name)

    return result


# ==================== Convenience Functions ====================

def polish_animation(animation: Animation,
                     add_blur: bool = False,
                     add_antic: bool = False,
                     add_follow: bool = False,
                     optimize: bool = True) -> Animation:
    """Apply multiple polish effects to an animation.

    Args:
        animation: Source animation
        add_blur: Add motion blur frames
        add_antic: Add anticipation frames
        add_follow: Add follow-through frames
        optimize: Optimize timing

    Returns:
        Polished Animation
    """
    result = animation

    if add_antic:
        result = add_anticipation(result, frames=2)

    if add_blur:
        result = add_motion_blur(result, blur_frames=1)

    if add_follow:
        result = add_follow_through(result, frames=2)

    if optimize:
        result = optimize_timing(result)

    result.name = animation.name + "_polished"
    return result


def list_smear_types() -> List[str]:
    """List available smear frame types."""
    return [s.value for s in SmearType]


def list_secondary_types() -> List[str]:
    """List available secondary motion types."""
    return [s.value for s in SecondaryType]

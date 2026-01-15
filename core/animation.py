"""
Animation - Keyframe and timing system for sprite animation.

Supports frame sequences, timing, looping, and sprite sheet export.
Also provides integration with track-based animation system for
procedural and pose-driven animation rendering.
"""

from typing import List, Dict, Any, Optional, Callable, TYPE_CHECKING
from .canvas import Canvas

if TYPE_CHECKING:
    from ..animation.timeline import Timeline
    from ..animation.cycles import AnimationCycle


class Keyframe:
    """A single keyframe in an animation."""

    def __init__(self, frame: Canvas, duration: float = 1.0, name: str = ""):
        """
        Create a keyframe.

        Args:
            frame: The canvas/sprite for this frame
            duration: Duration in animation time units (typically frames at target FPS)
            name: Optional name for this keyframe
        """
        self.frame = frame
        self.duration = duration
        self.name = name

    def copy(self) -> 'Keyframe':
        """Create a copy of this keyframe."""
        return Keyframe(self.frame.copy(), self.duration, self.name)


class Animation:
    """A sequence of keyframes forming an animation."""

    def __init__(self, name: str = "Untitled", fps: int = 12):
        """
        Create an animation.

        Args:
            name: Name of the animation (e.g., "walk", "idle", "attack")
            fps: Target frames per second
        """
        self.name = name
        self.fps = fps
        self.keyframes: List[Keyframe] = []
        self.loop = True

    def add_frame(self, frame: Canvas, duration: float = 1.0, name: str = "") -> 'Animation':
        """Add a keyframe to the animation."""
        self.keyframes.append(Keyframe(frame, duration, name))
        return self

    def add_frames(self, frames: List[Canvas], duration: float = 1.0) -> 'Animation':
        """Add multiple frames with the same duration."""
        for i, frame in enumerate(frames):
            self.keyframes.append(Keyframe(frame, duration, f"frame_{i}"))
        return self

    @property
    def total_duration(self) -> float:
        """Total duration of the animation in time units."""
        return sum(kf.duration for kf in self.keyframes)

    @property
    def frame_count(self) -> int:
        """Number of keyframes."""
        return len(self.keyframes)

    def get_frame_at_time(self, time: float) -> Optional[Canvas]:
        """Get the frame at a given time."""
        if not self.keyframes:
            return None

        if self.loop:
            time = time % self.total_duration

        elapsed = 0.0
        for kf in self.keyframes:
            if elapsed + kf.duration > time:
                return kf.frame
            elapsed += kf.duration

        return self.keyframes[-1].frame if self.keyframes else None

    def get_frame_at_index(self, index: int) -> Optional[Canvas]:
        """Get frame by index."""
        if not self.keyframes:
            return None
        return self.keyframes[index % len(self.keyframes)].frame

    # === Export Methods ===

    def to_spritesheet(self, columns: int = 0) -> Canvas:
        """
        Export animation as a sprite sheet.

        Args:
            columns: Number of columns (0 = all in one row)

        Returns:
            Canvas containing the sprite sheet
        """
        if not self.keyframes:
            return Canvas(1, 1)

        frame_w = self.keyframes[0].frame.width
        frame_h = self.keyframes[0].frame.height
        count = len(self.keyframes)

        if columns <= 0:
            columns = count

        rows = (count + columns - 1) // columns

        sheet = Canvas(frame_w * columns, frame_h * rows)

        for i, kf in enumerate(self.keyframes):
            col = i % columns
            row = i // columns
            sheet.blit(kf.frame, col * frame_w, row * frame_h)

        return sheet

    def to_frames(self) -> List[Canvas]:
        """Export as list of frame canvases."""
        return [kf.frame for kf in self.keyframes]

    def save_spritesheet(self, filepath: str, columns: int = 0) -> None:
        """Save animation as sprite sheet PNG."""
        sheet = self.to_spritesheet(columns)
        sheet.save(filepath)

    def save_frames(self, filepath_pattern: str) -> None:
        """
        Save individual frames.

        Args:
            filepath_pattern: Pattern with {n} for frame number, e.g., "frame_{n}.png"
        """
        for i, kf in enumerate(self.keyframes):
            path = filepath_pattern.format(n=i)
            kf.frame.save(path)

    # === Animation Operations ===

    def reverse(self) -> 'Animation':
        """Return a reversed copy of the animation."""
        anim = Animation(f"{self.name}_reverse", self.fps)
        anim.loop = self.loop
        for kf in reversed(self.keyframes):
            anim.keyframes.append(kf.copy())
        return anim

    def pingpong(self) -> 'Animation':
        """Return a ping-pong version (forward then backward)."""
        anim = Animation(f"{self.name}_pingpong", self.fps)
        anim.loop = self.loop

        # Forward
        for kf in self.keyframes:
            anim.keyframes.append(kf.copy())

        # Backward (skip first and last to avoid duplicate)
        for kf in reversed(self.keyframes[1:-1]):
            anim.keyframes.append(kf.copy())

        return anim

    def scale(self, factor: int) -> 'Animation':
        """Return a scaled version of all frames."""
        anim = Animation(f"{self.name}_{factor}x", self.fps)
        anim.loop = self.loop
        for kf in self.keyframes:
            scaled_frame = kf.frame.scale(factor)
            anim.keyframes.append(Keyframe(scaled_frame, kf.duration, kf.name))
        return anim

    def apply(self, func: Callable[[Canvas], Canvas]) -> 'Animation':
        """Apply a function to all frames."""
        anim = Animation(f"{self.name}_modified", self.fps)
        anim.loop = self.loop
        for kf in self.keyframes:
            modified = func(kf.frame)
            anim.keyframes.append(Keyframe(modified, kf.duration, kf.name))
        return anim


class AnimationSet:
    """A collection of animations for a character/sprite."""

    def __init__(self, name: str = ""):
        self.name = name
        self.animations: Dict[str, Animation] = {}

    def add(self, animation: Animation) -> 'AnimationSet':
        """Add an animation to the set."""
        self.animations[animation.name] = animation
        return self

    def get(self, name: str) -> Optional[Animation]:
        """Get an animation by name."""
        return self.animations.get(name)

    def save_all_spritesheets(self, directory: str, columns: int = 0) -> None:
        """Save all animations as sprite sheets."""
        import os
        os.makedirs(directory, exist_ok=True)
        for name, anim in self.animations.items():
            path = os.path.join(directory, f"{name}.png")
            anim.save_spritesheet(path, columns)

    def __iter__(self):
        return iter(self.animations.values())

    def __len__(self):
        return len(self.animations)


# =============================================================================
# Track-Based Animation Integration
# =============================================================================

class TrackAnimationRenderer:
    """Renders track-based animations (Timelines) to frame sequences.

    This class bridges the procedural animation system with the
    canvas-based frame rendering, allowing Timeline data to drive
    character or object rendering.
    """

    def __init__(self, width: int, height: int, fps: int = 12):
        """
        Initialize the renderer.

        Args:
            width: Output frame width
            height: Output frame height
            fps: Frames per second for rendering
        """
        self.width = width
        self.height = height
        self.fps = fps
        self._render_callback: Optional[Callable[[Dict[str, Any]], Canvas]] = None

    def set_render_callback(self, callback: Callable[[Dict[str, Any]], Canvas]) -> None:
        """Set the callback function that renders a frame from track values.

        The callback receives a dictionary of track name -> value pairs
        and should return a Canvas with the rendered frame.

        Args:
            callback: Function (track_values: Dict) -> Canvas
        """
        self._render_callback = callback

    def render_timeline(self, timeline: 'Timeline', duration: Optional[float] = None) -> Animation:
        """Render a Timeline to an Animation.

        Args:
            timeline: The Timeline to render
            duration: Override duration (uses timeline duration if None)

        Returns:
            Animation with rendered frames

        Raises:
            ValueError: If no render callback is set
        """
        if self._render_callback is None:
            raise ValueError("No render callback set. Call set_render_callback first.")

        anim = Animation(timeline.name, self.fps)
        anim.loop = timeline.loop

        actual_duration = duration or timeline.get_duration()
        frame_count = max(1, int(actual_duration * self.fps))
        frame_duration = actual_duration / frame_count

        for i in range(frame_count):
            time = i * frame_duration
            values = timeline.get_values_at(time)
            frame = self._render_callback(values)
            anim.add_frame(frame, 1.0, f"frame_{i}")

        return anim

    def render_cycle(self, cycle: 'AnimationCycle') -> Animation:
        """Render an AnimationCycle to an Animation.

        Args:
            cycle: The AnimationCycle to render

        Returns:
            Animation with rendered frames
        """
        timeline = cycle.to_timeline()
        return self.render_timeline(timeline)


class AnimationBlender:
    """Blends between multiple animations for smooth transitions."""

    def __init__(self):
        self._animations: Dict[str, Animation] = {}
        self._current: Optional[str] = None
        self._target: Optional[str] = None
        self._blend_progress: float = 0.0
        self._blend_duration: float = 0.0
        self._current_time: float = 0.0

    def add_animation(self, name: str, animation: Animation) -> None:
        """Add an animation to the blender."""
        self._animations[name] = animation
        if self._current is None:
            self._current = name

    def play(self, name: str, blend_time: float = 0.0) -> None:
        """Play an animation, optionally blending from current.

        Args:
            name: Animation name to play
            blend_time: Time to blend between animations (0 = instant)
        """
        if name not in self._animations:
            raise ValueError(f"Unknown animation: {name}")

        if blend_time <= 0 or self._current is None:
            self._current = name
            self._target = None
            self._blend_progress = 0.0
            self._current_time = 0.0
        else:
            self._target = name
            self._blend_duration = blend_time
            self._blend_progress = 0.0

    def update(self, delta_time: float) -> None:
        """Update animation state.

        Args:
            delta_time: Time elapsed since last update
        """
        self._current_time += delta_time

        if self._target is not None and self._blend_duration > 0:
            self._blend_progress += delta_time / self._blend_duration
            if self._blend_progress >= 1.0:
                self._current = self._target
                self._target = None
                self._blend_progress = 0.0

    def get_frame(self) -> Optional[Canvas]:
        """Get the current animation frame.

        Returns:
            Current frame canvas, or blended frame if transitioning
        """
        if self._current is None:
            return None

        current_anim = self._animations[self._current]
        current_frame = current_anim.get_frame_at_time(self._current_time)

        if self._target is None or current_frame is None:
            return current_frame

        # Blend between animations
        target_anim = self._animations[self._target]
        target_frame = target_anim.get_frame_at_time(self._current_time)

        if target_frame is None:
            return current_frame

        return self._blend_frames(current_frame, target_frame, self._blend_progress)

    def _blend_frames(self, frame_a: Canvas, frame_b: Canvas,
                      t: float) -> Canvas:
        """Blend two frames together using alpha blending.

        Args:
            frame_a: First frame
            frame_b: Second frame
            t: Blend factor (0 = frame_a, 1 = frame_b)

        Returns:
            Blended frame
        """
        # Create result canvas
        result = Canvas(frame_a.width, frame_a.height)

        # Simple cross-fade blending
        for y in range(frame_a.height):
            for x in range(frame_a.width):
                if x < frame_b.width and y < frame_b.height:
                    # Get pixels
                    px_a = frame_a.pixels[y][x]
                    px_b = frame_b.pixels[y][x]

                    # Blend RGBA
                    r = int(px_a[0] * (1 - t) + px_b[0] * t)
                    g = int(px_a[1] * (1 - t) + px_b[1] * t)
                    b = int(px_a[2] * (1 - t) + px_b[2] * t)
                    a = int(px_a[3] * (1 - t) + px_b[3] * t)

                    result.set_pixel(x, y, (r, g, b, a))
                else:
                    result.set_pixel(x, y, frame_a.pixels[y][x])

        return result

    @property
    def current_animation(self) -> Optional[str]:
        """Get the name of the current (or transitioning to) animation."""
        return self._target if self._target else self._current

    @property
    def is_blending(self) -> bool:
        """Check if currently blending between animations."""
        return self._target is not None


class AnimationState:
    """Manages animation state for a character/entity.

    Provides a higher-level interface for animation playback
    with state management, events, and callbacks.
    """

    def __init__(self):
        self._blender = AnimationBlender()
        self._callbacks: Dict[str, List[Callable]] = {}
        self._playing = False
        self._speed = 1.0

    def add_animation(self, name: str, animation: Animation) -> 'AnimationState':
        """Add an animation."""
        self._blender.add_animation(name, animation)
        return self

    def play(self, name: str, blend_time: float = 0.0) -> 'AnimationState':
        """Play an animation."""
        self._blender.play(name, blend_time)
        self._playing = True
        self._fire_callback('on_animation_start', name)
        return self

    def stop(self) -> 'AnimationState':
        """Stop playback."""
        self._playing = False
        return self

    def pause(self) -> 'AnimationState':
        """Pause playback."""
        self._playing = False
        return self

    def resume(self) -> 'AnimationState':
        """Resume playback."""
        self._playing = True
        return self

    def update(self, delta_time: float) -> None:
        """Update animation state."""
        if self._playing:
            self._blender.update(delta_time * self._speed)

    def get_frame(self) -> Optional[Canvas]:
        """Get current frame."""
        return self._blender.get_frame()

    def set_speed(self, speed: float) -> 'AnimationState':
        """Set playback speed multiplier."""
        self._speed = max(0.0, speed)
        return self

    def on(self, event: str, callback: Callable) -> 'AnimationState':
        """Register an event callback.

        Events:
            - on_animation_start: Called when animation starts
            - on_animation_end: Called when non-looping animation ends
            - on_loop: Called each time a looping animation loops

        Args:
            event: Event name
            callback: Callback function
        """
        if event not in self._callbacks:
            self._callbacks[event] = []
        self._callbacks[event].append(callback)
        return self

    def _fire_callback(self, event: str, *args) -> None:
        """Fire callbacks for an event."""
        for callback in self._callbacks.get(event, []):
            callback(*args)

    @property
    def is_playing(self) -> bool:
        """Check if animation is playing."""
        return self._playing

    @property
    def current_animation(self) -> Optional[str]:
        """Get current animation name."""
        return self._blender.current_animation

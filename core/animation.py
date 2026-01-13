"""
Animation - Keyframe and timing system for sprite animation.

Supports frame sequences, timing, looping, and sprite sheet export.
"""

from typing import List, Dict, Any, Optional, Callable
from .canvas import Canvas


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

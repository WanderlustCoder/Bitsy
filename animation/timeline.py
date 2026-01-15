"""
Timeline - Keyframe sequencing and track-based animation.

Provides a flexible animation system with multiple tracks that can
animate different properties (position, rotation, scale, color, etc.).
"""

import math
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field

from .easing import apply_easing, get_easing


@dataclass
class Keyframe:
    """A single keyframe in an animation track.

    Attributes:
        time: Time in seconds when this keyframe occurs
        value: The value at this keyframe (any type)
        easing: Easing function name for interpolation TO this keyframe
    """

    time: float
    value: Any
    easing: str = 'linear'

    def __lt__(self, other: 'Keyframe') -> bool:
        return self.time < other.time


class Track:
    """An animation track controlling a single property.

    Tracks contain keyframes and interpolate between them based on time.
    """

    def __init__(self, name: str, property_path: str = ''):
        """Initialize track.

        Args:
            name: Track name for identification
            property_path: Dot-separated path to property (e.g., 'position.x')
        """
        self.name = name
        self.property_path = property_path
        self.keyframes: List[Keyframe] = []
        self._sorted = True

    def add_keyframe(self, time: float, value: Any, easing: str = 'linear') -> 'Track':
        """Add a keyframe to the track.

        Args:
            time: Time in seconds
            value: Value at this keyframe
            easing: Easing function name

        Returns:
            Self for chaining
        """
        self.keyframes.append(Keyframe(time, value, easing))
        self._sorted = False
        return self

    def add_keyframes(self, keyframes: List[Tuple[float, Any]],
                      easing: str = 'linear') -> 'Track':
        """Add multiple keyframes at once.

        Args:
            keyframes: List of (time, value) tuples
            easing: Default easing for all keyframes

        Returns:
            Self for chaining
        """
        for time, value in keyframes:
            self.add_keyframe(time, value, easing)
        return self

    def _ensure_sorted(self) -> None:
        """Ensure keyframes are sorted by time."""
        if not self._sorted:
            self.keyframes.sort(key=lambda k: k.time)
            self._sorted = True

    def get_value_at(self, time: float) -> Any:
        """Get interpolated value at a given time.

        Args:
            time: Time in seconds

        Returns:
            Interpolated value
        """
        if not self.keyframes:
            return None

        self._ensure_sorted()

        # Before first keyframe
        if time <= self.keyframes[0].time:
            return self.keyframes[0].value

        # After last keyframe
        if time >= self.keyframes[-1].time:
            return self.keyframes[-1].value

        # Find surrounding keyframes
        for i in range(len(self.keyframes) - 1):
            k1 = self.keyframes[i]
            k2 = self.keyframes[i + 1]

            if k1.time <= time < k2.time:
                # Calculate interpolation factor
                duration = k2.time - k1.time
                if duration <= 0:
                    return k2.value

                t = (time - k1.time) / duration
                t = apply_easing(t, k2.easing)

                return self._interpolate(k1.value, k2.value, t)

        return self.keyframes[-1].value

    def _interpolate(self, a: Any, b: Any, t: float) -> Any:
        """Interpolate between two values.

        Handles different types automatically.
        """
        # Numeric
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            return a + (b - a) * t

        # Tuple/list (for positions, colors, etc.)
        if isinstance(a, (tuple, list)) and isinstance(b, (tuple, list)):
            result = []
            for i in range(min(len(a), len(b))):
                if isinstance(a[i], (int, float)) and isinstance(b[i], (int, float)):
                    result.append(a[i] + (b[i] - a[i]) * t)
                else:
                    result.append(b[i] if t > 0.5 else a[i])
            return tuple(result) if isinstance(a, tuple) else result

        # For non-interpolatable types, use step
        return b if t > 0.5 else a

    def get_duration(self) -> float:
        """Get total duration of this track."""
        if not self.keyframes:
            return 0.0
        self._ensure_sorted()
        return self.keyframes[-1].time

    def shift_time(self, offset: float) -> 'Track':
        """Shift all keyframes by time offset.

        Args:
            offset: Time offset in seconds

        Returns:
            Self for chaining
        """
        for kf in self.keyframes:
            kf.time += offset
        return self

    def scale_time(self, factor: float) -> 'Track':
        """Scale all keyframe times.

        Args:
            factor: Scale factor (2.0 = twice as slow)

        Returns:
            Self for chaining
        """
        for kf in self.keyframes:
            kf.time *= factor
        return self

    def reverse(self) -> 'Track':
        """Reverse the track (flip time).

        Returns:
            Self for chaining
        """
        duration = self.get_duration()
        for kf in self.keyframes:
            kf.time = duration - kf.time
        self._sorted = False
        return self

    def copy(self) -> 'Track':
        """Create a copy of this track."""
        new_track = Track(self.name, self.property_path)
        for kf in self.keyframes:
            new_track.add_keyframe(kf.time, kf.value, kf.easing)
        return new_track


class Timeline:
    """Multi-track animation timeline.

    Contains multiple tracks that can be played together,
    controlling different properties of an object.
    """

    def __init__(self, name: str = 'animation', fps: int = 12):
        """Initialize timeline.

        Args:
            name: Animation name
            fps: Frames per second for rendering
        """
        self.name = name
        self.fps = fps
        self.tracks: Dict[str, Track] = {}
        self.loop = False
        self.ping_pong = False

    def add_track(self, track: Track) -> 'Timeline':
        """Add a track to the timeline.

        Args:
            track: Track to add

        Returns:
            Self for chaining
        """
        self.tracks[track.name] = track
        return self

    def create_track(self, name: str, property_path: str = '') -> Track:
        """Create and add a new track.

        Args:
            name: Track name
            property_path: Property path

        Returns:
            The created track
        """
        track = Track(name, property_path)
        self.tracks[name] = track
        return track

    def get_track(self, name: str) -> Optional[Track]:
        """Get track by name."""
        return self.tracks.get(name)

    def remove_track(self, name: str) -> bool:
        """Remove track by name."""
        if name in self.tracks:
            del self.tracks[name]
            return True
        return False

    def get_duration(self) -> float:
        """Get total duration across all tracks."""
        if not self.tracks:
            return 0.0
        return max(track.get_duration() for track in self.tracks.values())

    def get_frame_count(self) -> int:
        """Get total number of frames."""
        return int(self.get_duration() * self.fps) + 1

    def get_values_at(self, time: float) -> Dict[str, Any]:
        """Get all track values at a given time.

        Args:
            time: Time in seconds

        Returns:
            Dictionary mapping track names to values
        """
        duration = self.get_duration()

        # Handle looping
        if self.loop and duration > 0:
            if self.ping_pong:
                # Ping-pong: 0->1->0->1->...
                cycle = int(time / duration)
                t = time % duration
                if cycle % 2 == 1:
                    time = duration - t
                else:
                    time = t
            else:
                time = time % duration

        return {
            name: track.get_value_at(time)
            for name, track in self.tracks.items()
        }

    def get_frame_values(self, frame: int) -> Dict[str, Any]:
        """Get all track values at a given frame number.

        Args:
            frame: Frame number (0-indexed)

        Returns:
            Dictionary mapping track names to values
        """
        time = frame / self.fps
        return self.get_values_at(time)

    def copy(self) -> 'Timeline':
        """Create a copy of this timeline."""
        new_timeline = Timeline(self.name, self.fps)
        new_timeline.loop = self.loop
        new_timeline.ping_pong = self.ping_pong
        for name, track in self.tracks.items():
            new_timeline.tracks[name] = track.copy()
        return new_timeline

    def to_dict(self) -> Dict[str, Any]:
        """Serialize timeline to dictionary."""
        return {
            'name': self.name,
            'fps': self.fps,
            'loop': self.loop,
            'ping_pong': self.ping_pong,
            'tracks': {
                name: {
                    'property_path': track.property_path,
                    'keyframes': [
                        {'time': kf.time, 'value': kf.value, 'easing': kf.easing}
                        for kf in track.keyframes
                    ]
                }
                for name, track in self.tracks.items()
            }
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Timeline':
        """Create timeline from dictionary."""
        timeline = cls(data.get('name', 'animation'), data.get('fps', 12))
        timeline.loop = data.get('loop', False)
        timeline.ping_pong = data.get('ping_pong', False)

        for track_name, track_data in data.get('tracks', {}).items():
            track = timeline.create_track(
                track_name,
                track_data.get('property_path', '')
            )
            for kf_data in track_data.get('keyframes', []):
                track.add_keyframe(
                    kf_data['time'],
                    kf_data['value'],
                    kf_data.get('easing', 'linear')
                )

        return timeline


# =============================================================================
# Animation Utilities
# =============================================================================

def create_simple_animation(values: List[Any], duration: float,
                            easing: str = 'linear') -> Track:
    """Create a track that animates through a list of values.

    Args:
        values: List of values to animate through
        duration: Total duration in seconds
        easing: Easing function for transitions

    Returns:
        Track with evenly-spaced keyframes
    """
    track = Track('values')
    if not values:
        return track

    if len(values) == 1:
        track.add_keyframe(0, values[0])
        return track

    for i, value in enumerate(values):
        time = (i / (len(values) - 1)) * duration
        track.add_keyframe(time, value, easing)

    return track


def create_oscillation(min_val: float, max_val: float, period: float,
                       cycles: int = 1, easing: str = 'ease_in_out_sine') -> Track:
    """Create a track that oscillates between two values.

    Args:
        min_val: Minimum value
        max_val: Maximum value
        period: Time for one complete oscillation
        cycles: Number of oscillations
        easing: Easing function

    Returns:
        Track with oscillating values
    """
    track = Track('oscillation')
    total_duration = period * cycles

    for i in range(cycles * 2 + 1):
        time = (i / 2) * period
        value = min_val if i % 2 == 0 else max_val
        track.add_keyframe(time, value, easing)

    return track


def create_pulse(base_val: float, peak_val: float, attack: float,
                 hold: float, release: float) -> Track:
    """Create a pulse/envelope track (attack-hold-release).

    Args:
        base_val: Base/resting value
        peak_val: Peak value during hold
        attack: Time to reach peak
        hold: Time at peak
        release: Time to return to base

    Returns:
        Track with pulse envelope
    """
    track = Track('pulse')
    track.add_keyframe(0, base_val, 'linear')
    track.add_keyframe(attack, peak_val, 'ease_out')
    track.add_keyframe(attack + hold, peak_val, 'linear')
    track.add_keyframe(attack + hold + release, base_val, 'ease_in')
    return track


def combine_timelines(timelines: List[Timeline], sequential: bool = True) -> Timeline:
    """Combine multiple timelines into one.

    Args:
        timelines: List of timelines to combine
        sequential: If True, play one after another; if False, play simultaneously

    Returns:
        Combined timeline
    """
    if not timelines:
        return Timeline()

    result = Timeline('combined', timelines[0].fps)

    if sequential:
        # Play one after another
        time_offset = 0.0
        for i, timeline in enumerate(timelines):
            for track_name, track in timeline.tracks.items():
                # Create unique track name
                unique_name = f"{track_name}_{i}"
                new_track = track.copy()
                new_track.name = unique_name
                new_track.shift_time(time_offset)
                result.add_track(new_track)
            time_offset += timeline.get_duration()
    else:
        # Play simultaneously - merge tracks
        for timeline in timelines:
            for track_name, track in timeline.tracks.items():
                if track_name in result.tracks:
                    # Append keyframes to existing track
                    for kf in track.keyframes:
                        result.tracks[track_name].add_keyframe(
                            kf.time, kf.value, kf.easing
                        )
                else:
                    result.add_track(track.copy())

    return result

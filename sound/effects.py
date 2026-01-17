"""
Effects - Sound effect generation and preset sounds.

Combines oscillators, envelopes, and modulation to create game sounds.
"""

import math
from typing import List, Optional, Tuple, Union
from dataclasses import dataclass, field
from pathlib import Path

from .oscillators import (
    OscillatorConfig,
    generate_waveform,
    mix_samples,
    list_oscillator_types,
)
from .envelope import (
    Envelope,
    EnvelopeAR,
    EnvelopeDecay,
    apply_envelope,
)
from .wav import save_wav, get_wav_bytes


@dataclass
class FrequencySweep:
    """Frequency sweep configuration.

    Attributes:
        start_freq: Starting frequency in Hz
        end_freq: Ending frequency in Hz
        curve: Sweep curve ('linear', 'exponential', 'logarithmic')
    """
    start_freq: float
    end_freq: float
    curve: str = 'linear'

    def get_frequency_at(self, t: float) -> float:
        """Get frequency at time t (0.0 to 1.0).

        Args:
            t: Normalized time (0.0 = start, 1.0 = end)

        Returns:
            Frequency in Hz at time t
        """
        t = max(0.0, min(1.0, t))

        if self.curve == 'linear':
            return self.start_freq + (self.end_freq - self.start_freq) * t
        elif self.curve == 'exponential':
            # Exponential interpolation (sounds more natural for pitch)
            if self.start_freq <= 0 or self.end_freq <= 0:
                return self.start_freq + (self.end_freq - self.start_freq) * t
            log_start = math.log(self.start_freq)
            log_end = math.log(self.end_freq)
            return math.exp(log_start + (log_end - log_start) * t)
        elif self.curve == 'logarithmic':
            # Logarithmic (fast change at start, slow at end)
            t_log = math.log(1.0 + t * (math.e - 1.0))
            return self.start_freq + (self.end_freq - self.start_freq) * t_log
        else:
            return self.start_freq + (self.end_freq - self.start_freq) * t


@dataclass
class Vibrato:
    """Vibrato (pitch wobble) configuration.

    Attributes:
        rate: Vibrato rate in Hz
        depth: Vibrato depth (frequency multiplier, e.g., 0.05 = 5%)
    """
    rate: float = 5.0
    depth: float = 0.02


@dataclass
class Arpeggio:
    """Arpeggio configuration.

    Attributes:
        notes: List of note offsets in semitones
        speed: Notes per second
    """
    notes: List[int] = field(default_factory=lambda: [0, 4, 7])  # Major chord
    speed: float = 15.0


@dataclass
class SoundEffect:
    """A complete sound effect definition.

    Attributes:
        duration: Total duration in seconds
        sample_rate: Sample rate in Hz
        bit_depth: Bits per sample (8 or 16)
    """
    duration: float = 0.5
    sample_rate: int = 22050
    bit_depth: int = 8

    # Internal state
    _oscillator_type: str = field(default='square', repr=False)
    _base_frequency: float = field(default=440.0, repr=False)
    _volume: float = field(default=1.0, repr=False)
    _envelope: Optional[Union[Envelope, EnvelopeAR, EnvelopeDecay]] = field(default=None, repr=False)
    _sweep: Optional[FrequencySweep] = field(default=None, repr=False)
    _vibrato: Optional[Vibrato] = field(default=None, repr=False)
    _arpeggio: Optional[Arpeggio] = field(default=None, repr=False)
    _noise_seed: Optional[int] = field(default=None, repr=False)

    def set_oscillator(
        self,
        osc_type: str,
        frequency: float = 440.0,
        volume: float = 1.0
    ) -> 'SoundEffect':
        """Set the oscillator type and frequency.

        Args:
            osc_type: Oscillator type ('square', 'triangle', 'saw', 'sine', 'noise')
            frequency: Base frequency in Hz
            volume: Volume level 0.0 to 1.0

        Returns:
            Self for chaining
        """
        self._oscillator_type = osc_type
        self._base_frequency = frequency
        self._volume = volume
        return self

    def set_envelope(
        self,
        attack: float = 0.01,
        decay: float = 0.1,
        sustain: float = 0.5,
        release: float = 0.1
    ) -> 'SoundEffect':
        """Set an ADSR envelope.

        Args:
            attack: Attack time in seconds
            decay: Decay time in seconds
            sustain: Sustain level 0.0 to 1.0
            release: Release time in seconds

        Returns:
            Self for chaining
        """
        self._envelope = Envelope(attack, decay, sustain, release)
        return self

    def set_decay_envelope(
        self,
        decay_time: float = 0.5,
        curve: str = 'exponential'
    ) -> 'SoundEffect':
        """Set a simple decay envelope.

        Args:
            decay_time: Time to fade out
            curve: Decay curve ('linear', 'exponential', 'logarithmic')

        Returns:
            Self for chaining
        """
        self._envelope = EnvelopeDecay(decay_time, curve)
        return self

    def set_sweep(
        self,
        start_freq: float,
        end_freq: float,
        curve: str = 'exponential'
    ) -> 'SoundEffect':
        """Set a frequency sweep.

        Args:
            start_freq: Starting frequency in Hz
            end_freq: Ending frequency in Hz
            curve: Sweep curve type

        Returns:
            Self for chaining
        """
        self._sweep = FrequencySweep(start_freq, end_freq, curve)
        return self

    def set_vibrato(
        self,
        rate: float = 5.0,
        depth: float = 0.02
    ) -> 'SoundEffect':
        """Set vibrato (pitch wobble).

        Args:
            rate: Vibrato rate in Hz
            depth: Depth as frequency multiplier

        Returns:
            Self for chaining
        """
        self._vibrato = Vibrato(rate, depth)
        return self

    def set_arpeggio(
        self,
        notes: List[int],
        speed: float = 15.0
    ) -> 'SoundEffect':
        """Set an arpeggio pattern.

        Args:
            notes: Note offsets in semitones (0 = base note)
            speed: Notes per second

        Returns:
            Self for chaining
        """
        self._arpeggio = Arpeggio(notes, speed)
        return self

    def set_noise_seed(self, seed: int) -> 'SoundEffect':
        """Set random seed for noise oscillator.

        Args:
            seed: Random seed

        Returns:
            Self for chaining
        """
        self._noise_seed = seed
        return self

    def render(self) -> List[float]:
        """Render the sound effect to samples.

        Returns:
            List of audio samples in range -1.0 to 1.0
        """
        num_samples = int(self.duration * self.sample_rate)
        samples = []

        for i in range(num_samples):
            t = i / num_samples  # Normalized time 0.0 to 1.0
            time_seconds = i / self.sample_rate

            # Calculate frequency
            if self._sweep:
                freq = self._sweep.get_frequency_at(t)
            else:
                freq = self._base_frequency

            # Apply vibrato
            if self._vibrato:
                vibrato_offset = math.sin(2.0 * math.pi * self._vibrato.rate * time_seconds)
                freq *= (1.0 + self._vibrato.depth * vibrato_offset)

            # Apply arpeggio
            if self._arpeggio:
                note_index = int(time_seconds * self._arpeggio.speed) % len(self._arpeggio.notes)
                semitone_offset = self._arpeggio.notes[note_index]
                freq *= 2.0 ** (semitone_offset / 12.0)

            # Generate sample
            config = OscillatorConfig(frequency=freq, volume=self._volume)

            if self._oscillator_type in ('noise', 'noise_periodic'):
                # For noise, we need to generate sample-by-sample with consistent randomness
                import random
                if self._noise_seed is not None:
                    random.seed(self._noise_seed + i)
                sample = random.uniform(-1.0, 1.0) * self._volume
            else:
                # Generate a tiny segment to get the sample at this point
                # This is inefficient but correct for modulated frequencies
                phase = 0.0
                for j in range(i):
                    # Recalculate frequency for proper phase accumulation
                    tj = j / num_samples
                    fj = self._sweep.get_frequency_at(tj) if self._sweep else self._base_frequency
                    if self._vibrato:
                        time_j = j / self.sample_rate
                        vib = math.sin(2.0 * math.pi * self._vibrato.rate * time_j)
                        fj *= (1.0 + self._vibrato.depth * vib)
                    if self._arpeggio:
                        time_j = j / self.sample_rate
                        note_idx = int(time_j * self._arpeggio.speed) % len(self._arpeggio.notes)
                        fj *= 2.0 ** (self._arpeggio.notes[note_idx] / 12.0)
                    phase += fj / self.sample_rate

                # Generate sample based on phase
                p = phase % 1.0
                if self._oscillator_type == 'square':
                    sample = (1.0 if p < 0.5 else -1.0) * self._volume
                elif self._oscillator_type == 'triangle':
                    sample = (4.0 * p - 1.0 if p < 0.5 else 3.0 - 4.0 * p) * self._volume
                elif self._oscillator_type in ('sawtooth', 'saw'):
                    sample = (2.0 * p - 1.0) * self._volume
                elif self._oscillator_type == 'sine':
                    sample = math.sin(2.0 * math.pi * phase) * self._volume
                else:
                    sample = (1.0 if p < 0.5 else -1.0) * self._volume

            samples.append(sample)

        # Apply envelope
        if self._envelope:
            envelope_values = self._envelope.generate(num_samples, self.sample_rate)
            samples = apply_envelope(samples, envelope_values)

        return samples

    def save_wav(self, filename: Union[str, Path]) -> None:
        """Save the sound effect to a WAV file.

        Args:
            filename: Output file path
        """
        samples = self.render()
        save_wav(filename, samples, self.sample_rate, self.bit_depth)

    def get_wav_bytes(self) -> bytes:
        """Get the sound effect as WAV bytes.

        Returns:
            WAV file as bytes
        """
        samples = self.render()
        return get_wav_bytes(samples, self.sample_rate, self.bit_depth)


# Optimized render for performance (pre-compute phase)
def _render_optimized(effect: SoundEffect) -> List[float]:
    """Optimized render that pre-computes phase accumulation."""
    num_samples = int(effect.duration * effect.sample_rate)
    samples = []
    phase = 0.0

    for i in range(num_samples):
        t = i / num_samples
        time_seconds = i / effect.sample_rate

        # Calculate frequency
        if effect._sweep:
            freq = effect._sweep.get_frequency_at(t)
        else:
            freq = effect._base_frequency

        # Apply vibrato
        if effect._vibrato:
            vibrato_offset = math.sin(2.0 * math.pi * effect._vibrato.rate * time_seconds)
            freq *= (1.0 + effect._vibrato.depth * vibrato_offset)

        # Apply arpeggio
        if effect._arpeggio:
            note_index = int(time_seconds * effect._arpeggio.speed) % len(effect._arpeggio.notes)
            semitone_offset = effect._arpeggio.notes[note_index]
            freq *= 2.0 ** (semitone_offset / 12.0)

        # Accumulate phase
        phase += freq / effect.sample_rate

        # Generate sample based on oscillator type
        p = phase % 1.0
        osc = effect._oscillator_type

        if osc == 'square':
            sample = (1.0 if p < 0.5 else -1.0) * effect._volume
        elif osc == 'triangle':
            sample = (4.0 * p - 1.0 if p < 0.5 else 3.0 - 4.0 * p) * effect._volume
        elif osc in ('sawtooth', 'saw'):
            sample = (2.0 * p - 1.0) * effect._volume
        elif osc == 'sine':
            sample = math.sin(2.0 * math.pi * phase) * effect._volume
        elif osc in ('noise', 'noise_periodic'):
            import random
            if effect._noise_seed is not None:
                random.seed(effect._noise_seed + i)
            sample = random.uniform(-1.0, 1.0) * effect._volume
        else:
            sample = (1.0 if p < 0.5 else -1.0) * effect._volume

        samples.append(sample)

    # Apply envelope
    if effect._envelope:
        envelope_values = effect._envelope.generate(num_samples, effect.sample_rate)
        samples = apply_envelope(samples, envelope_values)

    return samples


# Replace the slow render with optimized version
SoundEffect.render = lambda self: _render_optimized(self)


# =============================================================================
# Preset Sound Effects
# =============================================================================

def create_jump_sound(
    duration: float = 0.15,
    start_freq: float = 200,
    end_freq: float = 600,
    sample_rate: int = 22050
) -> SoundEffect:
    """Create a classic jump sound (rising pitch).

    Args:
        duration: Sound duration in seconds
        start_freq: Starting frequency
        end_freq: Ending frequency
        sample_rate: Sample rate

    Returns:
        Configured SoundEffect
    """
    effect = SoundEffect(duration=duration, sample_rate=sample_rate)
    effect.set_oscillator('square', start_freq)
    effect.set_sweep(start_freq, end_freq, 'exponential')
    effect.set_decay_envelope(duration * 0.9, 'linear')
    return effect


def create_coin_sound(
    duration: float = 0.1,
    base_freq: float = 800,
    sample_rate: int = 22050
) -> SoundEffect:
    """Create a coin/collect sound (quick high arpeggio).

    Args:
        duration: Sound duration
        base_freq: Base frequency
        sample_rate: Sample rate

    Returns:
        Configured SoundEffect
    """
    effect = SoundEffect(duration=duration, sample_rate=sample_rate)
    effect.set_oscillator('square', base_freq)
    effect.set_arpeggio([0, 12], speed=30.0)  # Octave jump
    effect.set_decay_envelope(duration * 0.8, 'exponential')
    return effect


def create_hit_sound(
    duration: float = 0.1,
    sample_rate: int = 22050,
    seed: int = 42
) -> SoundEffect:
    """Create a hit/damage sound (noise burst).

    Args:
        duration: Sound duration
        sample_rate: Sample rate
        seed: Random seed for reproducibility

    Returns:
        Configured SoundEffect
    """
    effect = SoundEffect(duration=duration, sample_rate=sample_rate)
    effect.set_oscillator('noise', 100, volume=0.8)
    effect.set_noise_seed(seed)
    effect.set_decay_envelope(duration * 0.7, 'exponential')
    return effect


def create_explosion_sound(
    duration: float = 0.5,
    start_freq: float = 150,
    end_freq: float = 50,
    sample_rate: int = 22050,
    seed: int = 42
) -> SoundEffect:
    """Create an explosion sound (noise with pitch drop).

    Args:
        duration: Sound duration
        start_freq: Starting pitch for noise modulation
        end_freq: Ending pitch
        sample_rate: Sample rate
        seed: Random seed

    Returns:
        Configured SoundEffect
    """
    effect = SoundEffect(duration=duration, sample_rate=sample_rate)
    effect.set_oscillator('noise', start_freq, volume=1.0)
    effect.set_noise_seed(seed)
    effect.set_sweep(start_freq, end_freq, 'exponential')
    effect.set_decay_envelope(duration * 0.9, 'exponential')
    return effect


def create_powerup_sound(
    duration: float = 0.4,
    base_freq: float = 300,
    sample_rate: int = 22050
) -> SoundEffect:
    """Create a powerup sound (ascending arpeggio).

    Args:
        duration: Sound duration
        base_freq: Base frequency
        sample_rate: Sample rate

    Returns:
        Configured SoundEffect
    """
    effect = SoundEffect(duration=duration, sample_rate=sample_rate)
    effect.set_oscillator('square', base_freq)
    effect.set_arpeggio([0, 4, 7, 12, 16, 19], speed=20.0)  # Major arpeggio up
    effect.set_sweep(base_freq, base_freq * 2, 'linear')
    effect.set_envelope(attack=0.01, decay=0.1, sustain=0.7, release=0.15)
    return effect


def create_laser_sound(
    duration: float = 0.2,
    start_freq: float = 1000,
    end_freq: float = 200,
    sample_rate: int = 22050
) -> SoundEffect:
    """Create a laser/shoot sound (descending pitch).

    Args:
        duration: Sound duration
        start_freq: Starting frequency
        end_freq: Ending frequency
        sample_rate: Sample rate

    Returns:
        Configured SoundEffect
    """
    effect = SoundEffect(duration=duration, sample_rate=sample_rate)
    effect.set_oscillator('square', start_freq)
    effect.set_sweep(start_freq, end_freq, 'exponential')
    effect.set_decay_envelope(duration * 0.8, 'linear')
    return effect


def create_blip_sound(
    duration: float = 0.05,
    frequency: float = 600,
    sample_rate: int = 22050
) -> SoundEffect:
    """Create a short blip/click sound (menu select).

    Args:
        duration: Sound duration
        frequency: Tone frequency
        sample_rate: Sample rate

    Returns:
        Configured SoundEffect
    """
    effect = SoundEffect(duration=duration, sample_rate=sample_rate)
    effect.set_oscillator('square', frequency)
    effect.set_decay_envelope(duration * 0.9, 'exponential')
    return effect


def create_death_sound(
    duration: float = 0.6,
    start_freq: float = 400,
    end_freq: float = 80,
    sample_rate: int = 22050,
    seed: int = 42
) -> SoundEffect:
    """Create a death/game-over sound (descending with noise).

    Args:
        duration: Sound duration
        start_freq: Starting frequency
        end_freq: Ending frequency
        sample_rate: Sample rate
        seed: Random seed

    Returns:
        Configured SoundEffect
    """
    effect = SoundEffect(duration=duration, sample_rate=sample_rate)
    effect.set_oscillator('square', start_freq, volume=0.7)
    effect.set_sweep(start_freq, end_freq, 'exponential')
    effect.set_envelope(attack=0.01, decay=0.2, sustain=0.5, release=0.3)
    return effect


def create_select_sound(
    duration: float = 0.08,
    frequency: float = 500,
    sample_rate: int = 22050
) -> SoundEffect:
    """Create a menu select sound.

    Args:
        duration: Sound duration
        frequency: Tone frequency
        sample_rate: Sample rate

    Returns:
        Configured SoundEffect
    """
    effect = SoundEffect(duration=duration, sample_rate=sample_rate)
    effect.set_oscillator('triangle', frequency)
    effect.set_decay_envelope(duration * 0.9, 'exponential')
    return effect


def create_hurt_sound(
    duration: float = 0.15,
    start_freq: float = 300,
    end_freq: float = 150,
    sample_rate: int = 22050
) -> SoundEffect:
    """Create a hurt/damage taken sound.

    Args:
        duration: Sound duration
        start_freq: Starting frequency
        end_freq: Ending frequency
        sample_rate: Sample rate

    Returns:
        Configured SoundEffect
    """
    effect = SoundEffect(duration=duration, sample_rate=sample_rate)
    effect.set_oscillator('square', start_freq, volume=0.8)
    effect.set_sweep(start_freq, end_freq, 'linear')
    effect.set_decay_envelope(duration * 0.8, 'exponential')
    return effect


# Registry of presets
SOUND_PRESETS = {
    'jump': create_jump_sound,
    'coin': create_coin_sound,
    'hit': create_hit_sound,
    'explosion': create_explosion_sound,
    'powerup': create_powerup_sound,
    'laser': create_laser_sound,
    'blip': create_blip_sound,
    'death': create_death_sound,
    'select': create_select_sound,
    'hurt': create_hurt_sound,
}


def create_sound(preset: str, **kwargs) -> SoundEffect:
    """Create a sound effect from a preset.

    Args:
        preset: Preset name
        **kwargs: Override default parameters

    Returns:
        Configured SoundEffect

    Raises:
        ValueError: If preset is unknown
    """
    if preset not in SOUND_PRESETS:
        raise ValueError(
            f"Unknown preset: {preset}. "
            f"Available: {list(SOUND_PRESETS.keys())}"
        )

    return SOUND_PRESETS[preset](**kwargs)


def list_presets() -> List[str]:
    """List available sound presets.

    Returns:
        List of preset names
    """
    return list(SOUND_PRESETS.keys())

"""
Envelope - ADSR amplitude envelopes for sound shaping.

Controls how volume changes over time: Attack, Decay, Sustain, Release.
"""

from typing import List, Optional
from dataclasses import dataclass
import math


@dataclass
class Envelope:
    """ADSR envelope configuration.

    Attributes:
        attack: Time in seconds to reach full volume
        decay: Time in seconds to fall to sustain level
        sustain: Volume level during sustain (0.0 to 1.0)
        release: Time in seconds to fade to zero
    """
    attack: float = 0.01
    decay: float = 0.1
    sustain: float = 0.5
    release: float = 0.1

    def generate(
        self,
        num_samples: int,
        sample_rate: int,
        note_duration: Optional[float] = None
    ) -> List[float]:
        """Generate envelope values for given number of samples.

        Args:
            num_samples: Number of samples to generate
            sample_rate: Sample rate in Hz
            note_duration: Optional note-on duration (defaults to attack+decay+sustain time)

        Returns:
            List of amplitude multipliers (0.0 to 1.0)
        """
        envelope = []

        # Convert times to sample counts
        attack_samples = int(self.attack * sample_rate)
        decay_samples = int(self.decay * sample_rate)
        release_samples = int(self.release * sample_rate)

        # Calculate sustain duration
        if note_duration is not None:
            note_samples = int(note_duration * sample_rate)
            sustain_samples = max(0, note_samples - attack_samples - decay_samples)
        else:
            # Fill remaining time with sustain
            sustain_samples = max(0, num_samples - attack_samples - decay_samples - release_samples)

        for i in range(num_samples):
            if i < attack_samples:
                # Attack phase: ramp up from 0 to 1
                if attack_samples > 0:
                    value = i / attack_samples
                else:
                    value = 1.0
            elif i < attack_samples + decay_samples:
                # Decay phase: ramp down from 1 to sustain level
                decay_pos = i - attack_samples
                if decay_samples > 0:
                    value = 1.0 - (1.0 - self.sustain) * (decay_pos / decay_samples)
                else:
                    value = self.sustain
            elif i < attack_samples + decay_samples + sustain_samples:
                # Sustain phase: hold at sustain level
                value = self.sustain
            else:
                # Release phase: ramp down from sustain to 0
                release_pos = i - attack_samples - decay_samples - sustain_samples
                if release_samples > 0 and release_pos < release_samples:
                    value = self.sustain * (1.0 - release_pos / release_samples)
                else:
                    value = 0.0

            envelope.append(max(0.0, min(1.0, value)))

        return envelope


@dataclass
class EnvelopeAR:
    """Simple Attack-Release envelope.

    Attributes:
        attack: Time in seconds to reach full volume
        release: Time in seconds to fade to zero
    """
    attack: float = 0.01
    release: float = 0.1

    def generate(self, num_samples: int, sample_rate: int) -> List[float]:
        """Generate envelope values.

        Args:
            num_samples: Number of samples to generate
            sample_rate: Sample rate in Hz

        Returns:
            List of amplitude multipliers (0.0 to 1.0)
        """
        envelope = []

        attack_samples = int(self.attack * sample_rate)
        release_samples = int(self.release * sample_rate)
        hold_samples = max(0, num_samples - attack_samples - release_samples)

        for i in range(num_samples):
            if i < attack_samples:
                # Attack
                value = i / attack_samples if attack_samples > 0 else 1.0
            elif i < attack_samples + hold_samples:
                # Hold at full volume
                value = 1.0
            else:
                # Release
                release_pos = i - attack_samples - hold_samples
                if release_samples > 0:
                    value = 1.0 - release_pos / release_samples
                else:
                    value = 0.0

            envelope.append(max(0.0, min(1.0, value)))

        return envelope


@dataclass
class EnvelopeDecay:
    """Simple decay envelope - starts at full volume and fades out.

    Attributes:
        decay_time: Time in seconds to fade to zero
        curve: Decay curve ('linear', 'exponential', 'logarithmic')
    """
    decay_time: float = 0.5
    curve: str = 'exponential'

    def generate(self, num_samples: int, sample_rate: int) -> List[float]:
        """Generate envelope values.

        Args:
            num_samples: Number of samples to generate
            sample_rate: Sample rate in Hz

        Returns:
            List of amplitude multipliers (0.0 to 1.0)
        """
        envelope = []
        decay_samples = int(self.decay_time * sample_rate)

        for i in range(num_samples):
            if decay_samples <= 0:
                value = 0.0
            else:
                t = min(1.0, i / decay_samples)

                if self.curve == 'linear':
                    value = 1.0 - t
                elif self.curve == 'exponential':
                    # Exponential decay (fast start, slow end)
                    value = math.exp(-5.0 * t)
                elif self.curve == 'logarithmic':
                    # Logarithmic decay (slow start, fast end)
                    value = 1.0 - math.log(1.0 + t * (math.e - 1.0))
                else:
                    value = 1.0 - t

            envelope.append(max(0.0, min(1.0, value)))

        return envelope


def apply_envelope(samples: List[float], envelope: List[float]) -> List[float]:
    """Apply an envelope to samples.

    Args:
        samples: Audio samples
        envelope: Envelope multipliers

    Returns:
        Samples with envelope applied
    """
    result = []
    for i, sample in enumerate(samples):
        if i < len(envelope):
            result.append(sample * envelope[i])
        else:
            result.append(0.0)  # After envelope ends, silence

    return result


def create_envelope(
    envelope_type: str = 'adsr',
    **kwargs
) -> 'Envelope | EnvelopeAR | EnvelopeDecay':
    """Create an envelope of the specified type.

    Args:
        envelope_type: 'adsr', 'ar', or 'decay'
        **kwargs: Parameters for the envelope

    Returns:
        Envelope object
    """
    if envelope_type == 'adsr':
        return Envelope(
            attack=kwargs.get('attack', 0.01),
            decay=kwargs.get('decay', 0.1),
            sustain=kwargs.get('sustain', 0.5),
            release=kwargs.get('release', 0.1)
        )
    elif envelope_type == 'ar':
        return EnvelopeAR(
            attack=kwargs.get('attack', 0.01),
            release=kwargs.get('release', 0.1)
        )
    elif envelope_type == 'decay':
        return EnvelopeDecay(
            decay_time=kwargs.get('decay_time', 0.5),
            curve=kwargs.get('curve', 'exponential')
        )
    else:
        raise ValueError(f"Unknown envelope type: {envelope_type}")

"""
Oscillators - Waveform generators for 8-bit sound synthesis.

Provides classic chiptune waveforms: square, triangle, sawtooth, noise, sine.
"""

import math
import random
from typing import List, Callable, Optional
from dataclasses import dataclass


@dataclass
class OscillatorConfig:
    """Configuration for an oscillator.

    Attributes:
        frequency: Base frequency in Hz
        volume: Volume level 0.0 to 1.0
        phase: Starting phase 0.0 to 1.0
        duty_cycle: For pulse wave, ratio of high to low (0.0-1.0)
    """
    frequency: float = 440.0
    volume: float = 1.0
    phase: float = 0.0
    duty_cycle: float = 0.5


def generate_square(
    num_samples: int,
    sample_rate: int,
    config: OscillatorConfig
) -> List[float]:
    """Generate a square wave.

    Classic 8-bit sound - alternates between +1 and -1.

    Args:
        num_samples: Number of samples to generate
        sample_rate: Sample rate in Hz
        config: Oscillator configuration

    Returns:
        List of samples in range -1.0 to 1.0
    """
    samples = []
    phase = config.phase
    phase_increment = config.frequency / sample_rate

    for _ in range(num_samples):
        # Square wave: +1 for first half of period, -1 for second half
        value = 1.0 if (phase % 1.0) < 0.5 else -1.0
        samples.append(value * config.volume)
        phase += phase_increment

    return samples


def generate_pulse(
    num_samples: int,
    sample_rate: int,
    config: OscillatorConfig
) -> List[float]:
    """Generate a pulse wave with configurable duty cycle.

    Like square but with variable duty cycle for different timbres.

    Args:
        num_samples: Number of samples to generate
        sample_rate: Sample rate in Hz
        config: Oscillator configuration (uses duty_cycle)

    Returns:
        List of samples in range -1.0 to 1.0
    """
    samples = []
    phase = config.phase
    phase_increment = config.frequency / sample_rate
    duty = config.duty_cycle

    for _ in range(num_samples):
        value = 1.0 if (phase % 1.0) < duty else -1.0
        samples.append(value * config.volume)
        phase += phase_increment

    return samples


def generate_triangle(
    num_samples: int,
    sample_rate: int,
    config: OscillatorConfig
) -> List[float]:
    """Generate a triangle wave.

    Softer than square, good for bass. Linear ramp up then down.

    Args:
        num_samples: Number of samples to generate
        sample_rate: Sample rate in Hz
        config: Oscillator configuration

    Returns:
        List of samples in range -1.0 to 1.0
    """
    samples = []
    phase = config.phase
    phase_increment = config.frequency / sample_rate

    for _ in range(num_samples):
        # Triangle: ramp from -1 to 1 in first half, 1 to -1 in second half
        p = phase % 1.0
        if p < 0.5:
            value = 4.0 * p - 1.0  # -1 to 1
        else:
            value = 3.0 - 4.0 * p  # 1 to -1
        samples.append(value * config.volume)
        phase += phase_increment

    return samples


def generate_sawtooth(
    num_samples: int,
    sample_rate: int,
    config: OscillatorConfig
) -> List[float]:
    """Generate a sawtooth wave.

    Buzzy, aggressive sound. Linear ramp with sharp drop.

    Args:
        num_samples: Number of samples to generate
        sample_rate: Sample rate in Hz
        config: Oscillator configuration

    Returns:
        List of samples in range -1.0 to 1.0
    """
    samples = []
    phase = config.phase
    phase_increment = config.frequency / sample_rate

    for _ in range(num_samples):
        # Sawtooth: linear ramp from -1 to 1
        value = 2.0 * (phase % 1.0) - 1.0
        samples.append(value * config.volume)
        phase += phase_increment

    return samples


def generate_sine(
    num_samples: int,
    sample_rate: int,
    config: OscillatorConfig
) -> List[float]:
    """Generate a sine wave.

    Pure tone, less 8-bit but useful for smooth sounds.

    Args:
        num_samples: Number of samples to generate
        sample_rate: Sample rate in Hz
        config: Oscillator configuration

    Returns:
        List of samples in range -1.0 to 1.0
    """
    samples = []
    phase = config.phase
    phase_increment = config.frequency / sample_rate

    for _ in range(num_samples):
        value = math.sin(2.0 * math.pi * phase)
        samples.append(value * config.volume)
        phase += phase_increment

    return samples


def generate_noise(
    num_samples: int,
    sample_rate: int,
    config: OscillatorConfig,
    seed: Optional[int] = None
) -> List[float]:
    """Generate white noise.

    Random values, good for percussion and explosions.

    Args:
        num_samples: Number of samples to generate
        sample_rate: Sample rate in Hz (not used, for API consistency)
        config: Oscillator configuration
        seed: Random seed for reproducibility

    Returns:
        List of samples in range -1.0 to 1.0
    """
    if seed is not None:
        random.seed(seed)

    samples = []
    for _ in range(num_samples):
        value = random.uniform(-1.0, 1.0)
        samples.append(value * config.volume)

    return samples


def generate_noise_periodic(
    num_samples: int,
    sample_rate: int,
    config: OscillatorConfig,
    seed: Optional[int] = None
) -> List[float]:
    """Generate periodic noise (NES-style).

    Noise that repeats at a frequency, creating tonal noise.

    Args:
        num_samples: Number of samples to generate
        sample_rate: Sample rate in Hz
        config: Oscillator configuration (frequency controls period)
        seed: Random seed for reproducibility

    Returns:
        List of samples in range -1.0 to 1.0
    """
    if seed is not None:
        random.seed(seed)

    # Generate one period of noise
    period_samples = max(1, int(sample_rate / config.frequency))
    noise_period = [random.uniform(-1.0, 1.0) for _ in range(period_samples)]

    samples = []
    for i in range(num_samples):
        value = noise_period[i % period_samples]
        samples.append(value * config.volume)

    return samples


# Oscillator type registry
OSCILLATOR_TYPES = {
    'square': generate_square,
    'pulse': generate_pulse,
    'triangle': generate_triangle,
    'sawtooth': generate_sawtooth,
    'saw': generate_sawtooth,  # Alias
    'sine': generate_sine,
    'noise': generate_noise,
    'noise_periodic': generate_noise_periodic,
}


def generate_waveform(
    osc_type: str,
    num_samples: int,
    sample_rate: int,
    config: Optional[OscillatorConfig] = None,
    **kwargs
) -> List[float]:
    """Generate a waveform of the specified type.

    Args:
        osc_type: Oscillator type ('square', 'triangle', 'sawtooth', 'sine', 'noise')
        num_samples: Number of samples to generate
        sample_rate: Sample rate in Hz
        config: Oscillator configuration (optional)
        **kwargs: Additional arguments passed to oscillator

    Returns:
        List of samples in range -1.0 to 1.0

    Raises:
        ValueError: If oscillator type is unknown
    """
    if osc_type not in OSCILLATOR_TYPES:
        raise ValueError(
            f"Unknown oscillator type: {osc_type}. "
            f"Available: {list(OSCILLATOR_TYPES.keys())}"
        )

    config = config or OscillatorConfig()
    generator = OSCILLATOR_TYPES[osc_type]

    # Handle noise seed separately
    if osc_type in ('noise', 'noise_periodic') and 'seed' in kwargs:
        return generator(num_samples, sample_rate, config, seed=kwargs['seed'])

    return generator(num_samples, sample_rate, config)


def list_oscillator_types() -> List[str]:
    """List available oscillator types.

    Returns:
        List of oscillator type names
    """
    return list(OSCILLATOR_TYPES.keys())


def mix_samples(sample_lists: List[List[float]], weights: Optional[List[float]] = None) -> List[float]:
    """Mix multiple sample lists together.

    Args:
        sample_lists: List of sample lists to mix
        weights: Optional weights for each list (defaults to equal)

    Returns:
        Mixed samples, normalized to -1.0 to 1.0
    """
    if not sample_lists:
        return []

    if weights is None:
        weights = [1.0 / len(sample_lists)] * len(sample_lists)

    # Normalize weights
    total_weight = sum(weights)
    weights = [w / total_weight for w in weights]

    # Find longest list
    max_len = max(len(s) for s in sample_lists)

    # Mix samples
    result = []
    for i in range(max_len):
        mixed = 0.0
        for samples, weight in zip(sample_lists, weights):
            if i < len(samples):
                mixed += samples[i] * weight
        result.append(mixed)

    return result

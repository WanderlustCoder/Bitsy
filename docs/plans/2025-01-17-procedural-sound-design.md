# Procedural Sound Design

## Overview

Generate 8-bit chiptune sound effects programmatically in pure Python. No external dependencies - uses the built-in `wave` module for WAV file output.

## Architecture

### Three-Layer Design

1. **Oscillators** - Generate raw waveforms at specified frequencies
2. **Envelopes** - Shape amplitude over time (ADSR)
3. **Effects** - Modify frequency/amplitude over time (sweeps, vibrato, arpeggio)

### Core Classes

```python
@dataclass
class SoundEffect:
    duration: float = 0.5
    sample_rate: int = 22050
    bit_depth: int = 8

    def add_oscillator(type, frequency, volume)
    def add_envelope(attack, decay, sustain, release)
    def add_sweep(start_freq, end_freq, curve)
    def add_vibrato(rate, depth)
    def add_arpeggio(notes, speed)
    def render() -> List[int]
    def save_wav(filename)
```

## Oscillator Types

| Type | Description | Use Case |
|------|-------------|----------|
| Square | +1/-1 alternation | Classic NES, leads |
| Triangle | Linear ramp up/down | Bass, soft tones |
| Sawtooth | Linear ramp, sharp drop | Buzzy, aggressive |
| Noise | Random values | Percussion, explosions |
| Sine | Smooth wave | Pure tones |
| Pulse | Square with duty cycle | Varied timbres |

## Envelope (ADSR)

- **Attack**: Time to reach full volume
- **Decay**: Time to fall to sustain level
- **Sustain**: Level held during note
- **Release**: Time to fade to zero

## Sound Presets

| Preset | Technique |
|--------|-----------|
| Jump | Square wave, rising frequency sweep |
| Coin | High square, quick arpeggio (C-E-G) |
| Hit | Noise burst, fast decay |
| Explosion | Noise, slow decay, slight pitch drop |
| Powerup | Ascending arpeggio, sustain |
| Laser | Square, descending sweep |
| Blip | Single short square tone |
| Death | Descending tone with noise mix |

## Module Structure

```
sound/
├── __init__.py      # Public API exports
├── oscillators.py   # Waveform generators
├── envelope.py      # ADSR envelope
├── effects.py       # SoundEffect class
├── presets.py       # Ready-to-use sounds
└── wav.py           # WAV file writing
```

## Public API

```python
from sound import (
    # Core classes
    SoundEffect,
    Oscillator,
    Envelope,

    # Preset sounds
    create_jump_sound,
    create_coin_sound,
    create_hit_sound,
    create_explosion_sound,
    create_powerup_sound,
    create_laser_sound,
    create_blip_sound,
    create_death_sound,

    # Utilities
    list_oscillator_types,
    list_presets,
)

# Quick usage
jump = create_jump_sound()
jump.save_wav('jump.wav')

# Custom sound
effect = SoundEffect(duration=0.3)
effect.add_oscillator('square', 440)
effect.add_envelope(attack=0.01, decay=0.2)
effect.add_sweep(440, 880)
effect.save_wav('custom.wav')
```

## WAV Format

- Sample rate: 22050 Hz (default, configurable)
- Bit depth: 8-bit unsigned (authentic retro)
- Channels: Mono
- Format: Standard PCM WAV

## Design Decisions

1. **8-bit samples** - Authentic retro sound, smaller files
2. **22050 Hz sample rate** - Good quality, reasonable file size
3. **Mono output** - Simpler, matches retro games
4. **Built-in wave module** - No dependencies
5. **Preset-first API** - Easy to use, customizable when needed

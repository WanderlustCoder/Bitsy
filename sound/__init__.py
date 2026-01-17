"""
Bitsy Sound - Procedural 8-bit sound effect generation.

Generate chiptune-style sound effects programmatically.
No external dependencies - uses Python's built-in wave module.

Example usage:

    # Quick preset sounds
    from sound import create_jump_sound, create_coin_sound

    jump = create_jump_sound()
    jump.save_wav('jump.wav')

    coin = create_coin_sound()
    coin.save_wav('coin.wav')

    # Custom sound effect
    from sound import SoundEffect

    effect = SoundEffect(duration=0.3)
    effect.set_oscillator('square', 440)
    effect.set_sweep(440, 880)
    effect.set_decay_envelope(0.25)
    effect.save_wav('custom.wav')

    # List available presets
    from sound import list_presets
    print(list_presets())
"""

from .oscillators import (
    OscillatorConfig,
    generate_waveform,
    generate_square,
    generate_triangle,
    generate_sawtooth,
    generate_sine,
    generate_noise,
    generate_pulse,
    mix_samples,
    list_oscillator_types,
    OSCILLATOR_TYPES,
)

from .envelope import (
    Envelope,
    EnvelopeAR,
    EnvelopeDecay,
    apply_envelope,
    create_envelope,
)

from .effects import (
    SoundEffect,
    FrequencySweep,
    Vibrato,
    Arpeggio,
    create_sound,
    list_presets,
    SOUND_PRESETS,
    # Preset functions
    create_jump_sound,
    create_coin_sound,
    create_hit_sound,
    create_explosion_sound,
    create_powerup_sound,
    create_laser_sound,
    create_blip_sound,
    create_death_sound,
    create_select_sound,
    create_hurt_sound,
)

from .wav import (
    save_wav,
    load_wav,
    get_wav_bytes,
    samples_to_bytes,
)

__all__ = [
    # Oscillators
    'OscillatorConfig',
    'generate_waveform',
    'generate_square',
    'generate_triangle',
    'generate_sawtooth',
    'generate_sine',
    'generate_noise',
    'generate_pulse',
    'mix_samples',
    'list_oscillator_types',
    'OSCILLATOR_TYPES',

    # Envelopes
    'Envelope',
    'EnvelopeAR',
    'EnvelopeDecay',
    'apply_envelope',
    'create_envelope',

    # Sound Effects
    'SoundEffect',
    'FrequencySweep',
    'Vibrato',
    'Arpeggio',
    'create_sound',
    'list_presets',
    'SOUND_PRESETS',

    # Preset sounds
    'create_jump_sound',
    'create_coin_sound',
    'create_hit_sound',
    'create_explosion_sound',
    'create_powerup_sound',
    'create_laser_sound',
    'create_blip_sound',
    'create_death_sound',
    'create_select_sound',
    'create_hurt_sound',

    # WAV export
    'save_wav',
    'load_wav',
    'get_wav_bytes',
    'samples_to_bytes',
]

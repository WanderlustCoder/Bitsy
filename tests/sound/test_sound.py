"""Tests for procedural sound generation."""

import sys
import os
import math
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sound import (
    # Oscillators
    OscillatorConfig,
    generate_waveform,
    generate_square,
    generate_triangle,
    generate_sawtooth,
    generate_sine,
    generate_noise,
    mix_samples,
    list_oscillator_types,

    # Envelopes
    Envelope,
    EnvelopeAR,
    EnvelopeDecay,
    apply_envelope,
    create_envelope,

    # Effects
    SoundEffect,
    FrequencySweep,
    Vibrato,
    Arpeggio,
    create_sound,
    list_presets,

    # Presets
    create_jump_sound,
    create_coin_sound,
    create_hit_sound,
    create_explosion_sound,
    create_powerup_sound,
    create_laser_sound,
    create_blip_sound,
    create_death_sound,

    # WAV
    save_wav,
    load_wav,
    get_wav_bytes,
    samples_to_bytes,
)


class TestOscillators:
    """Tests for oscillator functions."""

    def test_list_oscillator_types(self):
        """Test listing oscillator types."""
        types = list_oscillator_types()
        assert 'square' in types
        assert 'triangle' in types
        assert 'sawtooth' in types
        assert 'sine' in types
        assert 'noise' in types

    def test_generate_square(self):
        """Test square wave generation."""
        config = OscillatorConfig(frequency=440, volume=1.0)
        samples = generate_square(1000, 22050, config)

        assert len(samples) == 1000
        # Square wave should only have +1 and -1 values
        for s in samples:
            assert abs(s) == 1.0 or abs(s) < 0.001

    def test_generate_triangle(self):
        """Test triangle wave generation."""
        config = OscillatorConfig(frequency=440, volume=1.0)
        samples = generate_triangle(1000, 22050, config)

        assert len(samples) == 1000
        # Triangle wave values should be in -1 to 1 range
        for s in samples:
            assert -1.0 <= s <= 1.0

    def test_generate_sawtooth(self):
        """Test sawtooth wave generation."""
        config = OscillatorConfig(frequency=440, volume=1.0)
        samples = generate_sawtooth(1000, 22050, config)

        assert len(samples) == 1000
        for s in samples:
            assert -1.0 <= s <= 1.0

    def test_generate_sine(self):
        """Test sine wave generation."""
        config = OscillatorConfig(frequency=440, volume=1.0)
        samples = generate_sine(1000, 22050, config)

        assert len(samples) == 1000
        for s in samples:
            assert -1.0 <= s <= 1.0

    def test_generate_noise(self):
        """Test noise generation."""
        config = OscillatorConfig(volume=1.0)
        samples = generate_noise(1000, 22050, config, seed=42)

        assert len(samples) == 1000
        for s in samples:
            assert -1.0 <= s <= 1.0

        # With same seed, should get same result
        samples2 = generate_noise(1000, 22050, config, seed=42)
        assert samples == samples2

    def test_generate_waveform_factory(self):
        """Test waveform factory function."""
        config = OscillatorConfig(frequency=440)
        samples = generate_waveform('square', 1000, 22050, config)
        assert len(samples) == 1000

    def test_generate_waveform_invalid(self):
        """Test invalid oscillator type."""
        try:
            generate_waveform('invalid', 1000, 22050)
            assert False, "Should raise ValueError"
        except ValueError as e:
            assert 'Unknown oscillator' in str(e)

    def test_volume_scaling(self):
        """Test volume scaling."""
        config = OscillatorConfig(frequency=440, volume=0.5)
        samples = generate_square(1000, 22050, config)

        for s in samples:
            assert abs(s) <= 0.5

    def test_mix_samples(self):
        """Test mixing multiple sample lists."""
        samples1 = [1.0, 1.0, 1.0]
        samples2 = [-1.0, -1.0, -1.0]

        mixed = mix_samples([samples1, samples2])
        # Equal weights should give 0
        for s in mixed:
            assert abs(s) < 0.001

    def test_mix_samples_weighted(self):
        """Test weighted mixing."""
        samples1 = [1.0, 1.0, 1.0]
        samples2 = [0.0, 0.0, 0.0]

        mixed = mix_samples([samples1, samples2], [1.0, 0.0])
        for s in mixed:
            assert abs(s - 1.0) < 0.001


class TestEnvelopes:
    """Tests for envelope functions."""

    def test_envelope_adsr(self):
        """Test ADSR envelope."""
        env = Envelope(attack=0.1, decay=0.1, sustain=0.5, release=0.1)
        values = env.generate(1000, 10000)

        assert len(values) == 1000
        # All values should be 0-1
        for v in values:
            assert 0.0 <= v <= 1.0

        # Attack should start at 0 and rise
        assert values[0] < 0.1
        # Should reach peak around attack time
        attack_end = int(0.1 * 10000)
        assert values[attack_end - 1] > 0.9

    def test_envelope_ar(self):
        """Test Attack-Release envelope."""
        env = EnvelopeAR(attack=0.1, release=0.1)
        values = env.generate(1000, 10000)

        assert len(values) == 1000
        for v in values:
            assert 0.0 <= v <= 1.0

    def test_envelope_decay(self):
        """Test decay envelope."""
        env = EnvelopeDecay(decay_time=0.5, curve='exponential')
        values = env.generate(1000, 2000)

        assert len(values) == 1000
        # Should start high and decay
        assert values[0] > 0.9
        assert values[-1] < 0.1

    def test_envelope_decay_linear(self):
        """Test linear decay."""
        env = EnvelopeDecay(decay_time=1.0, curve='linear')
        values = env.generate(100, 100)

        # Linear decay should be predictable
        assert abs(values[0] - 1.0) < 0.1
        assert abs(values[50] - 0.5) < 0.1
        assert values[-1] < 0.1

    def test_apply_envelope(self):
        """Test applying envelope to samples."""
        samples = [1.0, 1.0, 1.0, 1.0]
        envelope = [1.0, 0.5, 0.25, 0.0]

        result = apply_envelope(samples, envelope)

        assert result[0] == 1.0
        assert result[1] == 0.5
        assert result[2] == 0.25
        assert result[3] == 0.0

    def test_create_envelope_factory(self):
        """Test envelope factory."""
        env = create_envelope('adsr', attack=0.1, decay=0.1)
        assert isinstance(env, Envelope)

        env = create_envelope('ar', attack=0.1, release=0.1)
        assert isinstance(env, EnvelopeAR)

        env = create_envelope('decay', decay_time=0.5)
        assert isinstance(env, EnvelopeDecay)


class TestFrequencySweep:
    """Tests for frequency sweep."""

    def test_linear_sweep(self):
        """Test linear frequency sweep."""
        sweep = FrequencySweep(100, 200, 'linear')

        assert sweep.get_frequency_at(0.0) == 100
        assert sweep.get_frequency_at(0.5) == 150
        assert sweep.get_frequency_at(1.0) == 200

    def test_exponential_sweep(self):
        """Test exponential frequency sweep."""
        sweep = FrequencySweep(100, 200, 'exponential')

        # Use approximate comparison for floating-point
        assert abs(sweep.get_frequency_at(0.0) - 100) < 0.01
        assert abs(sweep.get_frequency_at(1.0) - 200) < 0.01
        # Middle should be geometric mean
        mid = sweep.get_frequency_at(0.5)
        expected = math.sqrt(100 * 200)
        assert abs(mid - expected) < 1.0


class TestSoundEffect:
    """Tests for SoundEffect class."""

    def test_create_sound_effect(self):
        """Test creating a sound effect."""
        effect = SoundEffect(duration=0.5, sample_rate=22050)
        assert effect.duration == 0.5
        assert effect.sample_rate == 22050

    def test_set_oscillator(self):
        """Test setting oscillator."""
        effect = SoundEffect(duration=0.1)
        effect.set_oscillator('square', 440, 0.8)

        samples = effect.render()
        assert len(samples) > 0

    def test_set_envelope(self):
        """Test setting envelope."""
        effect = SoundEffect(duration=0.1)
        effect.set_oscillator('square', 440)
        effect.set_envelope(attack=0.01, decay=0.05, sustain=0.5, release=0.02)

        samples = effect.render()
        # First sample should be near 0 (attack)
        assert abs(samples[0]) < 0.1
        # Last samples should be near 0 (release)
        assert abs(samples[-1]) < 0.1

    def test_set_sweep(self):
        """Test setting frequency sweep."""
        effect = SoundEffect(duration=0.2)
        effect.set_oscillator('square', 200)
        effect.set_sweep(200, 400)

        samples = effect.render()
        assert len(samples) > 0

    def test_render(self):
        """Test rendering sound effect."""
        effect = SoundEffect(duration=0.1, sample_rate=22050)
        effect.set_oscillator('square', 440)

        samples = effect.render()
        expected_samples = int(0.1 * 22050)
        assert len(samples) == expected_samples

    def test_chaining(self):
        """Test method chaining."""
        effect = (SoundEffect(duration=0.1)
                  .set_oscillator('square', 440)
                  .set_envelope(attack=0.01)
                  .set_sweep(440, 880))

        samples = effect.render()
        assert len(samples) > 0


class TestPresets:
    """Tests for preset sounds."""

    def test_list_presets(self):
        """Test listing presets."""
        presets = list_presets()
        assert 'jump' in presets
        assert 'coin' in presets
        assert 'hit' in presets
        assert 'explosion' in presets

    def test_create_jump_sound(self):
        """Test jump sound preset."""
        sound = create_jump_sound()
        samples = sound.render()
        assert len(samples) > 0

    def test_create_coin_sound(self):
        """Test coin sound preset."""
        sound = create_coin_sound()
        samples = sound.render()
        assert len(samples) > 0

    def test_create_hit_sound(self):
        """Test hit sound preset."""
        sound = create_hit_sound()
        samples = sound.render()
        assert len(samples) > 0

    def test_create_explosion_sound(self):
        """Test explosion sound preset."""
        sound = create_explosion_sound()
        samples = sound.render()
        assert len(samples) > 0

    def test_create_powerup_sound(self):
        """Test powerup sound preset."""
        sound = create_powerup_sound()
        samples = sound.render()
        assert len(samples) > 0

    def test_create_laser_sound(self):
        """Test laser sound preset."""
        sound = create_laser_sound()
        samples = sound.render()
        assert len(samples) > 0

    def test_create_blip_sound(self):
        """Test blip sound preset."""
        sound = create_blip_sound()
        samples = sound.render()
        assert len(samples) > 0

    def test_create_death_sound(self):
        """Test death sound preset."""
        sound = create_death_sound()
        samples = sound.render()
        assert len(samples) > 0

    def test_create_sound_factory(self):
        """Test create_sound factory."""
        sound = create_sound('jump')
        samples = sound.render()
        assert len(samples) > 0

    def test_create_sound_invalid(self):
        """Test invalid preset."""
        try:
            create_sound('invalid_preset')
            assert False, "Should raise ValueError"
        except ValueError as e:
            assert 'Unknown preset' in str(e)

    def test_preset_custom_params(self):
        """Test preset with custom parameters."""
        sound = create_jump_sound(duration=0.3, start_freq=100, end_freq=400)
        samples = sound.render()
        expected = int(0.3 * 22050)
        assert len(samples) == expected


class TestWAV:
    """Tests for WAV file operations."""

    def test_samples_to_bytes_8bit(self):
        """Test converting samples to 8-bit bytes."""
        samples = [0.0, 1.0, -1.0, 0.5, -0.5]
        data = samples_to_bytes(samples, bit_depth=8)

        assert len(data) == 5
        # Allow +-1 for center value due to int truncation
        assert 127 <= data[0] <= 128  # 0.0 -> ~128 (center)
        assert data[1] == 255  # 1.0 -> 255 (max)
        assert data[2] == 0    # -1.0 -> 0 (min)

    def test_samples_to_bytes_16bit(self):
        """Test converting samples to 16-bit bytes."""
        samples = [0.0, 1.0, -1.0]
        data = samples_to_bytes(samples, bit_depth=16)

        assert len(data) == 6  # 3 samples * 2 bytes

    def test_save_and_load_wav(self):
        """Test saving and loading WAV file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / 'test.wav'

            # Create simple samples
            original_samples = [0.0, 0.5, 1.0, 0.5, 0.0, -0.5, -1.0, -0.5]

            # Save
            save_wav(filepath, original_samples, sample_rate=22050, bit_depth=8)
            assert filepath.exists()

            # Load
            loaded_samples, sr, bits, channels = load_wav(filepath)

            assert sr == 22050
            assert bits == 8
            assert channels == 1
            assert len(loaded_samples) == len(original_samples)

    def test_get_wav_bytes(self):
        """Test getting WAV as bytes."""
        samples = [0.0, 0.5, -0.5, 0.0]
        data = get_wav_bytes(samples, sample_rate=22050, bit_depth=8)

        # Should be valid WAV file (starts with RIFF header)
        assert data[:4] == b'RIFF'
        assert b'WAVE' in data[:20]

    def test_save_wav_creates_directory(self):
        """Test that save_wav creates parent directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / 'subdir' / 'test.wav'

            save_wav(filepath, [0.0, 0.5], sample_rate=22050)

            assert filepath.exists()


class TestSoundEffectWAV:
    """Tests for SoundEffect WAV export."""

    def test_sound_effect_save_wav(self):
        """Test saving sound effect to WAV."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / 'jump.wav'

            sound = create_jump_sound()
            sound.save_wav(filepath)

            assert filepath.exists()
            assert filepath.stat().st_size > 0

    def test_sound_effect_get_wav_bytes(self):
        """Test getting sound effect as WAV bytes."""
        sound = create_coin_sound()
        data = sound.get_wav_bytes()

        assert data[:4] == b'RIFF'
        assert len(data) > 100


class TestDeterminism:
    """Tests for deterministic output."""

    def test_noise_determinism(self):
        """Test that noise with same seed produces same result."""
        sound1 = create_hit_sound(seed=42)
        sound2 = create_hit_sound(seed=42)

        samples1 = sound1.render()
        samples2 = sound2.render()

        assert samples1 == samples2

    def test_noise_different_seeds(self):
        """Test that different seeds produce different results."""
        sound1 = create_hit_sound(seed=42)
        sound2 = create_hit_sound(seed=123)

        samples1 = sound1.render()
        samples2 = sound2.render()

        assert samples1 != samples2


class TestEdgeCases:
    """Tests for edge cases."""

    def test_zero_duration(self):
        """Test zero duration sound."""
        effect = SoundEffect(duration=0.0)
        samples = effect.render()
        assert len(samples) == 0

    def test_very_short_duration(self):
        """Test very short duration."""
        effect = SoundEffect(duration=0.001, sample_rate=22050)
        effect.set_oscillator('square', 440)
        samples = effect.render()
        # 0.001 * 22050 = 22 samples
        assert len(samples) == 22

    def test_high_frequency(self):
        """Test high frequency (near Nyquist)."""
        effect = SoundEffect(duration=0.01, sample_rate=22050)
        effect.set_oscillator('square', 10000)  # High but below Nyquist
        samples = effect.render()
        assert len(samples) > 0

    def test_very_low_frequency(self):
        """Test very low frequency."""
        effect = SoundEffect(duration=0.1, sample_rate=22050)
        effect.set_oscillator('square', 20)
        samples = effect.render()
        assert len(samples) > 0


if __name__ == '__main__':
    # Simple test runner
    import traceback

    test_classes = [
        TestOscillators,
        TestEnvelopes,
        TestFrequencySweep,
        TestSoundEffect,
        TestPresets,
        TestWAV,
        TestSoundEffectWAV,
        TestDeterminism,
        TestEdgeCases,
    ]

    passed = 0
    failed = 0
    errors = []

    for test_class in test_classes:
        instance = test_class()
        for name in dir(instance):
            if name.startswith('test_'):
                try:
                    getattr(instance, name)()
                    passed += 1
                    print(f"  ✓ {test_class.__name__}.{name}")
                except Exception as e:
                    failed += 1
                    errors.append((test_class.__name__, name, e, traceback.format_exc()))
                    print(f"  ✗ {test_class.__name__}.{name}: {e}")

    print(f"\n{'='*60}")
    print(f"Results: {passed} passed, {failed} failed")

    if errors:
        print(f"\nFailed tests:")
        for cls_name, test_name, error, tb in errors:
            print(f"\n{cls_name}.{test_name}:")
            print(tb)

    exit(0 if failed == 0 else 1)

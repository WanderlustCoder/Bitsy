"""
WAV - Write audio samples to WAV files.

Uses Python's built-in wave module for zero dependencies.
"""

import wave
import struct
from typing import List, Union
from pathlib import Path


def samples_to_bytes(
    samples: List[float],
    bit_depth: int = 8
) -> bytes:
    """Convert float samples (-1.0 to 1.0) to bytes.

    Args:
        samples: Audio samples in range -1.0 to 1.0
        bit_depth: 8 or 16 bits per sample

    Returns:
        Bytes suitable for WAV file
    """
    if bit_depth == 8:
        # 8-bit WAV is unsigned (0-255, with 128 as center)
        byte_data = bytearray()
        for sample in samples:
            # Clamp to -1.0 to 1.0
            clamped = max(-1.0, min(1.0, sample))
            # Convert to 0-255 range
            value = int((clamped + 1.0) * 127.5)
            byte_data.append(max(0, min(255, value)))
        return bytes(byte_data)

    elif bit_depth == 16:
        # 16-bit WAV is signed (-32768 to 32767)
        byte_data = bytearray()
        for sample in samples:
            clamped = max(-1.0, min(1.0, sample))
            value = int(clamped * 32767)
            # Little-endian signed short
            byte_data.extend(struct.pack('<h', max(-32768, min(32767, value))))
        return bytes(byte_data)

    else:
        raise ValueError(f"Unsupported bit depth: {bit_depth}. Use 8 or 16.")


def save_wav(
    filename: Union[str, Path],
    samples: List[float],
    sample_rate: int = 22050,
    bit_depth: int = 8,
    channels: int = 1
) -> None:
    """Save samples to a WAV file.

    Args:
        filename: Output file path
        samples: Audio samples in range -1.0 to 1.0
        sample_rate: Sample rate in Hz (default 22050)
        bit_depth: Bits per sample, 8 or 16 (default 8)
        channels: Number of channels (default 1 for mono)
    """
    filename = Path(filename)

    # Ensure parent directory exists
    filename.parent.mkdir(parents=True, exist_ok=True)

    # Convert samples to bytes
    audio_bytes = samples_to_bytes(samples, bit_depth)

    # Write WAV file
    with wave.open(str(filename), 'wb') as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(bit_depth // 8)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_bytes)


def save_wav_stereo(
    filename: Union[str, Path],
    left_samples: List[float],
    right_samples: List[float],
    sample_rate: int = 22050,
    bit_depth: int = 8
) -> None:
    """Save stereo samples to a WAV file.

    Args:
        filename: Output file path
        left_samples: Left channel samples
        right_samples: Right channel samples
        sample_rate: Sample rate in Hz
        bit_depth: Bits per sample, 8 or 16
    """
    # Interleave left and right channels
    max_len = max(len(left_samples), len(right_samples))
    interleaved = []

    for i in range(max_len):
        left = left_samples[i] if i < len(left_samples) else 0.0
        right = right_samples[i] if i < len(right_samples) else 0.0
        interleaved.append(left)
        interleaved.append(right)

    save_wav(filename, interleaved, sample_rate, bit_depth, channels=2)


def get_wav_bytes(
    samples: List[float],
    sample_rate: int = 22050,
    bit_depth: int = 8,
    channels: int = 1
) -> bytes:
    """Get WAV file as bytes (for embedding or streaming).

    Args:
        samples: Audio samples in range -1.0 to 1.0
        sample_rate: Sample rate in Hz
        bit_depth: Bits per sample, 8 or 16
        channels: Number of channels

    Returns:
        Complete WAV file as bytes
    """
    import io

    audio_bytes = samples_to_bytes(samples, bit_depth)

    buffer = io.BytesIO()
    with wave.open(buffer, 'wb') as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(bit_depth // 8)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_bytes)

    return buffer.getvalue()


def load_wav(filename: Union[str, Path]) -> tuple:
    """Load samples from a WAV file.

    Args:
        filename: Input file path

    Returns:
        Tuple of (samples, sample_rate, bit_depth, channels)
    """
    filename = Path(filename)

    with wave.open(str(filename), 'rb') as wav_file:
        channels = wav_file.getnchannels()
        sample_width = wav_file.getsampwidth()
        sample_rate = wav_file.getframerate()
        num_frames = wav_file.getnframes()
        audio_bytes = wav_file.readframes(num_frames)

    bit_depth = sample_width * 8

    # Convert bytes to float samples
    samples = []

    if bit_depth == 8:
        # 8-bit unsigned
        for byte in audio_bytes:
            samples.append((byte - 128) / 127.0)

    elif bit_depth == 16:
        # 16-bit signed little-endian
        for i in range(0, len(audio_bytes), 2):
            value = struct.unpack('<h', audio_bytes[i:i+2])[0]
            samples.append(value / 32767.0)

    return samples, sample_rate, bit_depth, channels

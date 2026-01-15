"""
APNG Export - Pure Python animated PNG generation.

Supports:
- Full RGBA color (no palette limitations)
- Per-frame transparency
- Configurable frame delays
- Loop control
"""

import zlib
import struct
from typing import List, Tuple, Optional, BinaryIO

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Canvas


def _crc32(data: bytes) -> int:
    """Calculate CRC32 for PNG chunk."""
    return zlib.crc32(data) & 0xFFFFFFFF


def _write_chunk(f: BinaryIO, chunk_type: bytes, data: bytes) -> None:
    """Write a PNG chunk with CRC."""
    f.write(struct.pack('>I', len(data)))
    f.write(chunk_type)
    f.write(data)
    crc = _crc32(chunk_type + data)
    f.write(struct.pack('>I', crc))


def _compress_frame(canvas: Canvas) -> bytes:
    """Compress frame data for PNG."""
    raw_data = bytearray()

    for y in range(canvas.height):
        raw_data.append(0)  # Filter type: None
        for x in range(canvas.width):
            pixel = canvas.pixels[y][x]
            raw_data.extend([pixel[0], pixel[1], pixel[2], pixel[3]])

    return zlib.compress(bytes(raw_data), 9)


def save_apng(filepath: str, frames: List[Canvas],
              delays: Optional[List[Tuple[int, int]]] = None,
              loop: int = 0) -> None:
    """Save frames as animated PNG.

    Args:
        filepath: Output file path
        frames: List of frame canvases
        delays: Frame delays as (numerator, denominator) for seconds.
                Default (1, 10) = 0.1 seconds = 100ms
        loop: Number of times to loop (0 = infinite)
    """
    if not frames:
        raise ValueError("No frames to save")

    if delays is None:
        delays = [(1, 10)] * len(frames)  # Default 100ms
    elif len(delays) != len(frames):
        raise ValueError("Number of delays must match number of frames")

    width = frames[0].width
    height = frames[0].height
    num_frames = len(frames)

    with open(filepath, 'wb') as f:
        # PNG signature
        f.write(b'\x89PNG\r\n\x1a\n')

        # IHDR chunk
        ihdr_data = struct.pack('>IIBBBBB',
                                width, height,
                                8,  # bit depth
                                6,  # color type (RGBA)
                                0,  # compression
                                0,  # filter
                                0)  # interlace
        _write_chunk(f, b'IHDR', ihdr_data)

        # acTL chunk (animation control)
        actl_data = struct.pack('>II', num_frames, loop)
        _write_chunk(f, b'acTL', actl_data)

        sequence_number = 0

        for frame_idx, (frame, delay) in enumerate(zip(frames, delays)):
            delay_num, delay_den = delay

            # Ensure frame matches dimensions
            if frame.width != width or frame.height != height:
                # Create padded/cropped version
                adjusted = Canvas(width, height, (0, 0, 0, 0))
                adjusted.blit(frame, 0, 0)
                frame = adjusted

            # fcTL chunk (frame control)
            fctl_data = struct.pack('>IIIIIHHBB',
                                    sequence_number,
                                    width,
                                    height,
                                    0,  # x offset
                                    0,  # y offset
                                    delay_num,
                                    delay_den,
                                    0,  # dispose op (none)
                                    0)  # blend op (source)
            _write_chunk(f, b'fcTL', fctl_data)
            sequence_number += 1

            # Compress frame data
            compressed = _compress_frame(frame)

            if frame_idx == 0:
                # First frame uses IDAT
                _write_chunk(f, b'IDAT', compressed)
            else:
                # Subsequent frames use fdAT
                fdat_data = struct.pack('>I', sequence_number) + compressed
                _write_chunk(f, b'fdAT', fdat_data)
                sequence_number += 1

        # IEND chunk
        _write_chunk(f, b'IEND', b'')


def save_apng_simple(filepath: str, frames: List[Canvas],
                     fps: int = 10, loop: int = 0) -> None:
    """Save frames as animated PNG with simple FPS-based timing.

    Args:
        filepath: Output file path
        frames: List of frame canvases
        fps: Frames per second
        loop: Number of loops (0 = infinite)
    """
    # Convert FPS to delay fractions
    delays = [(1, fps)] * len(frames)
    save_apng(filepath, frames, delays, loop)


def save_apng_from_animation(filepath: str, animation, loop: int = 0) -> None:
    """Save an Animation object as APNG.

    Args:
        filepath: Output file path
        animation: Animation object with frames
        loop: Loop count
    """
    frames = []
    delays = []

    fps = animation.fps

    for frame_data in animation.frames:
        frames.append(frame_data['canvas'])
        duration = frame_data.get('duration', 1)
        # Convert frame duration to delay
        delays.append((int(duration), fps))

    save_apng(filepath, frames, delays, loop)


class APNGExporter:
    """APNG export with configuration options."""

    def __init__(self, compression: int = 9):
        """Initialize APNG exporter.

        Args:
            compression: Compression level (0-9)
        """
        self.compression = compression

    def export(self, filepath: str, frames: List[Canvas],
               fps: int = 10, loop: int = 0) -> None:
        """Export frames as APNG.

        Args:
            filepath: Output path
            frames: Frame canvases
            fps: Frames per second
            loop: Loop count
        """
        save_apng_simple(filepath, frames, fps, loop)

    def export_animation(self, filepath: str, animation, loop: int = 0) -> None:
        """Export Animation object as APNG."""
        save_apng_from_animation(filepath, animation, loop)


def frames_to_apng_bytes(frames: List[Canvas],
                         fps: int = 10, loop: int = 0) -> bytes:
    """Convert frames to APNG bytes in memory.

    Args:
        frames: Frame canvases
        fps: Frames per second
        loop: Loop count

    Returns:
        APNG file as bytes
    """
    from io import BytesIO

    buffer = BytesIO()

    if not frames:
        raise ValueError("No frames")

    width = frames[0].width
    height = frames[0].height
    num_frames = len(frames)
    delays = [(1, fps)] * num_frames

    # PNG signature
    buffer.write(b'\x89PNG\r\n\x1a\n')

    # IHDR
    ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)
    _write_chunk(buffer, b'IHDR', ihdr_data)

    # acTL
    actl_data = struct.pack('>II', num_frames, loop)
    _write_chunk(buffer, b'acTL', actl_data)

    sequence_number = 0

    for frame_idx, (frame, delay) in enumerate(zip(frames, delays)):
        delay_num, delay_den = delay

        if frame.width != width or frame.height != height:
            adjusted = Canvas(width, height, (0, 0, 0, 0))
            adjusted.blit(frame, 0, 0)
            frame = adjusted

        # fcTL
        fctl_data = struct.pack('>IIIIIHHBB',
                                sequence_number, width, height,
                                0, 0, delay_num, delay_den, 0, 0)
        _write_chunk(buffer, b'fcTL', fctl_data)
        sequence_number += 1

        compressed = _compress_frame(frame)

        if frame_idx == 0:
            _write_chunk(buffer, b'IDAT', compressed)
        else:
            fdat_data = struct.pack('>I', sequence_number) + compressed
            _write_chunk(buffer, b'fdAT', fdat_data)
            sequence_number += 1

    _write_chunk(buffer, b'IEND', b'')

    return buffer.getvalue()

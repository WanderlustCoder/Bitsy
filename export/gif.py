"""
GIF Export - Pure Python animated GIF generation.

Supports:
- Animated GIFs with frame delays
- Automatic palette quantization (max 256 colors)
- Transparency support
- Loop control
"""

import struct
from typing import List, Tuple, Optional, BinaryIO
from io import BytesIO

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Canvas


def _quantize_to_256(canvas: Canvas) -> Tuple[List[Tuple[int, int, int]], List[List[int]], int]:
    """Quantize canvas to 256 colors for GIF.

    Args:
        canvas: Source canvas

    Returns:
        (palette, indexed_pixels, transparent_index)
    """
    # Collect unique colors
    color_counts = {}
    has_transparency = False

    for row in canvas.pixels:
        for pixel in row:
            if pixel[3] < 128:  # Transparent
                has_transparency = True
            else:
                rgb = (pixel[0], pixel[1], pixel[2])
                color_counts[rgb] = color_counts.get(rgb, 0) + 1

    # Sort by frequency and limit to 255 (reserve 1 for transparency)
    max_colors = 255 if has_transparency else 256
    sorted_colors = sorted(color_counts.items(), key=lambda x: -x[1])
    palette_colors = [c[0] for c in sorted_colors[:max_colors]]

    # Build palette
    palette = list(palette_colors)

    # Add transparent color if needed
    transparent_index = -1
    if has_transparency:
        transparent_index = len(palette)
        palette.append((0, 0, 0))  # Transparent placeholder

    # Pad palette to power of 2
    palette_size = 2
    while palette_size < len(palette):
        palette_size *= 2
    while len(palette) < palette_size:
        palette.append((0, 0, 0))

    # Build color lookup
    color_to_index = {c: i for i, c in enumerate(palette_colors)}

    # Index pixels
    indexed = []
    for row in canvas.pixels:
        indexed_row = []
        for pixel in row:
            if pixel[3] < 128:
                indexed_row.append(transparent_index)
            else:
                rgb = (pixel[0], pixel[1], pixel[2])
                if rgb in color_to_index:
                    indexed_row.append(color_to_index[rgb])
                else:
                    # Find nearest color
                    nearest = _find_nearest(rgb, palette_colors)
                    indexed_row.append(nearest)
        indexed.append(indexed_row)

    return palette, indexed, transparent_index


def _find_nearest(color: Tuple[int, int, int],
                  palette: List[Tuple[int, int, int]]) -> int:
    """Find nearest color index in palette."""
    min_dist = float('inf')
    nearest = 0

    for i, p in enumerate(palette):
        dist = (color[0] - p[0])**2 + (color[1] - p[1])**2 + (color[2] - p[2])**2
        if dist < min_dist:
            min_dist = dist
            nearest = i

    return nearest


def _lzw_encode(data: List[int], min_code_size: int) -> bytes:
    """LZW compress data for GIF.

    Args:
        data: List of color indices
        min_code_size: Minimum code size (usually palette bits)

    Returns:
        LZW compressed bytes
    """
    clear_code = 1 << min_code_size
    eoi_code = clear_code + 1

    # Initialize code table
    code_table = {(i,): i for i in range(clear_code)}
    next_code = eoi_code + 1
    code_size = min_code_size + 1
    max_code = (1 << code_size) - 1

    # Output buffer
    output = []
    bit_buffer = 0
    bit_count = 0

    def emit_code(code: int) -> None:
        nonlocal bit_buffer, bit_count, output
        bit_buffer |= code << bit_count
        bit_count += code_size
        while bit_count >= 8:
            output.append(bit_buffer & 0xFF)
            bit_buffer >>= 8
            bit_count -= 8

    # Start with clear code
    emit_code(clear_code)

    if not data:
        emit_code(eoi_code)
        if bit_count > 0:
            output.append(bit_buffer & 0xFF)
        return bytes(output)

    # LZW encoding
    buffer = (data[0],)

    for pixel in data[1:]:
        new_buffer = buffer + (pixel,)

        if new_buffer in code_table:
            buffer = new_buffer
        else:
            emit_code(code_table[buffer])

            if next_code <= 4095:  # GIF max code
                code_table[new_buffer] = next_code
                next_code += 1

                # Increase code size if needed
                if next_code > max_code and code_size < 12:
                    code_size += 1
                    max_code = (1 << code_size) - 1

            buffer = (pixel,)

    # Output remaining buffer
    emit_code(code_table[buffer])
    emit_code(eoi_code)

    # Flush remaining bits
    if bit_count > 0:
        output.append(bit_buffer & 0xFF)

    return bytes(output)


def _write_gif_header(f: BinaryIO, width: int, height: int,
                      palette: List[Tuple[int, int, int]],
                      loop_count: int = 0) -> None:
    """Write GIF header and global color table."""
    # GIF signature
    f.write(b'GIF89a')

    # Logical screen descriptor
    palette_bits = 0
    size = len(palette)
    while (1 << (palette_bits + 1)) < size:
        palette_bits += 1

    packed = 0x80 | (palette_bits << 4) | palette_bits  # Global color table flag
    f.write(struct.pack('<HH', width, height))
    f.write(struct.pack('BBB', packed, 0, 0))  # packed, bg index, aspect

    # Global color table
    for r, g, b in palette:
        f.write(struct.pack('BBB', r, g, b))

    # Netscape extension for looping
    f.write(b'\x21\xFF\x0BNETSCAPE2.0')
    f.write(struct.pack('<BHB', 3, loop_count, 0))


def _write_frame(f: BinaryIO, canvas: Canvas, delay: int,
                 palette: List[Tuple[int, int, int]],
                 indexed: List[List[int]],
                 transparent_index: int) -> None:
    """Write a single GIF frame."""
    # Graphics control extension
    f.write(b'\x21\xF9\x04')
    if transparent_index >= 0:
        packed = 0x01  # Transparent flag
        f.write(struct.pack('<BHB', packed, delay, transparent_index))
    else:
        packed = 0x00
        f.write(struct.pack('<BHB', packed, delay, 0))
    f.write(b'\x00')

    # Image descriptor
    f.write(b'\x2C')
    f.write(struct.pack('<HHHH', 0, 0, canvas.width, canvas.height))
    f.write(b'\x00')  # No local color table

    # Image data
    # Calculate min code size based on palette size
    # min_code_size must be large enough to represent all palette indices
    palette_bits = 1
    size = len(palette)
    while (1 << palette_bits) < size:
        palette_bits += 1
    min_code_size = max(2, palette_bits)

    f.write(struct.pack('B', min_code_size))

    # Flatten indexed data
    flat_data = []
    for row in indexed:
        flat_data.extend(row)

    # LZW encode
    compressed = _lzw_encode(flat_data, min_code_size)

    # Write in sub-blocks
    pos = 0
    while pos < len(compressed):
        block_size = min(255, len(compressed) - pos)
        f.write(struct.pack('B', block_size))
        f.write(compressed[pos:pos + block_size])
        pos += block_size

    f.write(b'\x00')  # Block terminator


def save_gif(filepath: str, frames: List[Canvas],
             delays: Optional[List[int]] = None,
             loop: int = 0) -> None:
    """Save frames as animated GIF.

    Args:
        filepath: Output file path
        frames: List of frame canvases
        delays: Frame delays in centiseconds (100 = 1 second). Default 10.
        loop: Loop count (0 = infinite)
    """
    if not frames:
        raise ValueError("No frames to save")

    if delays is None:
        delays = [10] * len(frames)  # Default 100ms per frame
    elif len(delays) != len(frames):
        raise ValueError("Number of delays must match number of frames")

    # Use first frame dimensions
    width = frames[0].width
    height = frames[0].height

    # Build global palette from all frames
    all_colors = {}
    has_transparency = False

    for frame in frames:
        for row in frame.pixels:
            for pixel in row:
                if pixel[3] < 128:
                    has_transparency = True
                else:
                    rgb = (pixel[0], pixel[1], pixel[2])
                    all_colors[rgb] = all_colors.get(rgb, 0) + 1

    # Select most common colors
    max_colors = 255 if has_transparency else 256
    sorted_colors = sorted(all_colors.items(), key=lambda x: -x[1])
    palette_colors = [c[0] for c in sorted_colors[:max_colors]]

    # Build palette
    palette = list(palette_colors)
    transparent_index = -1
    if has_transparency:
        transparent_index = len(palette)
        palette.append((0, 0, 0))

    # Pad to power of 2
    palette_size = 2
    while palette_size < len(palette):
        palette_size *= 2
    while len(palette) < palette_size:
        palette.append((0, 0, 0))

    # Color lookup
    color_to_index = {c: i for i, c in enumerate(palette_colors)}

    with open(filepath, 'wb') as f:
        _write_gif_header(f, width, height, palette, loop)

        for frame, delay in zip(frames, delays):
            # Scale frame if different size
            if frame.width != width or frame.height != height:
                frame = frame.scale(1)  # Just copy for now

            # Index this frame's pixels
            indexed = []
            for row in frame.pixels:
                indexed_row = []
                for pixel in row:
                    if pixel[3] < 128:
                        indexed_row.append(transparent_index)
                    else:
                        rgb = (pixel[0], pixel[1], pixel[2])
                        if rgb in color_to_index:
                            indexed_row.append(color_to_index[rgb])
                        else:
                            nearest = _find_nearest(rgb, palette_colors)
                            indexed_row.append(nearest)
                indexed.append(indexed_row)

            _write_frame(f, frame, delay, palette, indexed, transparent_index)

        # GIF trailer
        f.write(b'\x3B')


def save_gif_from_animation(filepath: str, animation, loop: int = 0) -> None:
    """Save an Animation object as GIF.

    Args:
        filepath: Output file path
        animation: Animation object with frames
        loop: Loop count
    """
    frames = []
    delays = []

    for frame_data in animation.frames:
        frames.append(frame_data['canvas'])
        # Convert duration to centiseconds
        delay = int(frame_data.get('duration', 1) * 100 / animation.fps)
        delays.append(max(1, delay))

    save_gif(filepath, frames, delays, loop)


class GIFExporter:
    """GIF export with configuration options."""

    def __init__(self, dither: bool = False, max_colors: int = 256):
        """Initialize GIF exporter.

        Args:
            dither: Apply dithering for color reduction
            max_colors: Maximum colors (2-256)
        """
        self.dither = dither
        self.max_colors = min(256, max(2, max_colors))

    def export(self, filepath: str, frames: List[Canvas],
               delays: Optional[List[int]] = None,
               loop: int = 0) -> None:
        """Export frames as GIF.

        Args:
            filepath: Output path
            frames: Frame canvases
            delays: Frame delays in centiseconds
            loop: Loop count
        """
        save_gif(filepath, frames, delays, loop)

    def export_animation(self, filepath: str, animation, loop: int = 0) -> None:
        """Export Animation object as GIF."""
        save_gif_from_animation(filepath, animation, loop)

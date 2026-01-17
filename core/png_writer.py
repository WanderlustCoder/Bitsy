"""
Pure Python PNG Writer - No Dependencies Required

Creates valid PNG files using only Python standard library.
Supports RGBA images with alpha blending.
"""

import struct
import zlib
from typing import List, Tuple

# Type aliases
Color = Tuple[int, int, int, int]  # RGBA


def create_png(width: int, height: int, pixels: List[List[Color]]) -> bytes:
    """
    Create a PNG file from pixel data.

    Args:
        width: Image width in pixels
        height: Image height in pixels
        pixels: 2D list of RGBA tuples, pixels[y][x] = (r, g, b, a)

    Returns:
        PNG file as bytes
    """
    def make_chunk(chunk_type: bytes, data: bytes) -> bytes:
        """Create a PNG chunk with CRC."""
        chunk = chunk_type + data
        crc = zlib.crc32(chunk) & 0xffffffff
        return struct.pack('>I', len(data)) + chunk + struct.pack('>I', crc)

    # PNG signature
    png_data = b'\x89PNG\r\n\x1a\n'

    # IHDR chunk (image header)
    ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)
    png_data += make_chunk(b'IHDR', ihdr_data)

    # IDAT chunk (image data)
    raw_data = b''
    for y in range(height):
        raw_data += b'\x00'  # Filter type: None
        for x in range(width):
            r, g, b, a = pixels[y][x]
            raw_data += struct.pack('BBBB', r, g, b, a)

    compressed = zlib.compress(raw_data, 9)
    png_data += make_chunk(b'IDAT', compressed)

    # IEND chunk (image end)
    png_data += make_chunk(b'IEND', b'')

    return png_data


def save_png(filepath: str, width: int, height: int, pixels: List[List[Color]]) -> None:
    """Save pixel data as a PNG file."""
    png_bytes = create_png(width, height, pixels)
    with open(filepath, 'wb') as f:
        f.write(png_bytes)


def create_blank_canvas(width: int, height: int, color: Color = (0, 0, 0, 0)) -> List[List[Color]]:
    """Create a blank canvas filled with a single color."""
    return [[color for _ in range(width)] for _ in range(height)]


def blend_colors(base: Color, overlay: Color) -> Color:
    """Alpha blend overlay color onto base color.

    Uses integer math for performance (called 60k+ times per character).
    """
    br, bg, bb, ba = base
    or_, og, ob, oa = overlay

    if oa == 0:
        return base
    if oa == 255:
        return overlay

    # Integer alpha blending: (overlay * alpha + base * (255 - alpha)) / 255
    # Use (x + 127) // 255 for proper rounding
    inv_alpha = 255 - oa
    nr = (or_ * oa + br * inv_alpha + 127) // 255
    ng = (og * oa + bg * inv_alpha + 127) // 255
    nb = (ob * oa + bb * inv_alpha + 127) // 255
    na = ba if ba > oa else oa

    return (nr, ng, nb, na)


if __name__ == "__main__":
    # Test: create a simple gradient
    from .canvas import Canvas
    canvas = Canvas(64, 64, (24, 24, 48, 255))
    canvas.fill_circle(32, 32, 20, (200, 100, 150, 255))
    canvas.save("test_png.png")
    print("Created test_png.png")

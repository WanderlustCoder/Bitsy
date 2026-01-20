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


def load_png(filepath: str) -> List[List[Color]]:
    """
    Load a PNG file and return pixel data.

    Args:
        filepath: Path to PNG file

    Returns:
        2D list of RGBA tuples [y][x]
    """
    def unfilter_scanline(filter_type: int, scanline: bytes, prev: bytes, bpp: int) -> bytes:
        """Apply PNG unfiltering to a scanline."""
        result = bytearray(len(scanline))
        if filter_type == 0:
            return scanline
        if filter_type == 1:
            for i, value in enumerate(scanline):
                left = result[i - bpp] if i >= bpp else 0
                result[i] = (value + left) & 0xff
            return bytes(result)
        if filter_type == 2:
            for i, value in enumerate(scanline):
                up = prev[i] if prev else 0
                result[i] = (value + up) & 0xff
            return bytes(result)
        if filter_type == 3:
            for i, value in enumerate(scanline):
                left = result[i - bpp] if i >= bpp else 0
                up = prev[i] if prev else 0
                result[i] = (value + ((left + up) // 2)) & 0xff
            return bytes(result)
        if filter_type == 4:
            for i, value in enumerate(scanline):
                left = result[i - bpp] if i >= bpp else 0
                up = prev[i] if prev else 0
                up_left = prev[i - bpp] if (prev and i >= bpp) else 0
                p = left + up - up_left
                pa = abs(p - left)
                pb = abs(p - up)
                pc = abs(p - up_left)
                if pa <= pb and pa <= pc:
                    predictor = left
                elif pb <= pc:
                    predictor = up
                else:
                    predictor = up_left
                result[i] = (value + predictor) & 0xff
            return bytes(result)
        raise ValueError(f"Unsupported PNG filter type: {filter_type}")

    with open(filepath, 'rb') as f:
        signature = f.read(8)
        if signature != b'\x89PNG\r\n\x1a\n':
            raise ValueError("Not a valid PNG file")

        width = height = 0
        bit_depth = color_type = 0
        compressed_data = b''

        while True:
            length_data = f.read(4)
            if len(length_data) != 4:
                raise ValueError("Unexpected end of PNG file")
            chunk_len = struct.unpack('>I', length_data)[0]
            chunk_type = f.read(4)
            chunk_data = f.read(chunk_len)
            f.read(4)  # CRC

            if chunk_type == b'IHDR':
                width, height, bit_depth, color_type = struct.unpack('>IIBB', chunk_data[:10])
            elif chunk_type == b'IDAT':
                compressed_data += chunk_data
            elif chunk_type == b'IEND':
                break

        if bit_depth != 8 or color_type not in (2, 6):
            raise ValueError("Only 8-bit RGB/RGBA PNGs are supported")

        raw_data = zlib.decompress(compressed_data)
        bytes_per_pixel = 4 if color_type == 6 else 3
        row_bytes = width * bytes_per_pixel

        pixels: List[List[Color]] = []
        offset = 0
        prev_row = b''
        for _y in range(height):
            filter_type = raw_data[offset]
            offset += 1
            scanline = raw_data[offset:offset + row_bytes]
            offset += row_bytes
            recon = unfilter_scanline(filter_type, scanline, prev_row, bytes_per_pixel)
            row: List[Color] = []
            for x in range(width):
                idx = x * bytes_per_pixel
                r = recon[idx]
                g = recon[idx + 1]
                b = recon[idx + 2]
                a = recon[idx + 3] if bytes_per_pixel == 4 else 255
                row.append((r, g, b, a))
            pixels.append(row)
            prev_row = recon

        return pixels


if __name__ == "__main__":
    # Test: create a simple gradient
    from .canvas import Canvas
    canvas = Canvas(64, 64, (24, 24, 48, 255))
    canvas.fill_circle(32, 32, 20, (200, 100, 150, 255))
    canvas.save("test_png.png")
    print("Created test_png.png")

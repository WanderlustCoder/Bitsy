"""
PNG Loader - Pure Python PNG image loading.

Loads PNG files into Canvas objects for editing and manipulation.
Supports:
- 8-bit RGB and RGBA images
- Grayscale and grayscale+alpha
- Indexed color (palette-based) images
- All PNG filter types
"""

import zlib
import struct
from typing import Tuple, List, Optional, BinaryIO
from dataclasses import dataclass
from enum import IntEnum

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Canvas


# PNG signature
PNG_SIGNATURE = b'\x89PNG\r\n\x1a\n'


class ColorType(IntEnum):
    """PNG color types."""
    GRAYSCALE = 0
    RGB = 2
    INDEXED = 3
    GRAYSCALE_ALPHA = 4
    RGBA = 6


class FilterType(IntEnum):
    """PNG filter types."""
    NONE = 0
    SUB = 1
    UP = 2
    AVERAGE = 3
    PAETH = 4


@dataclass
class PNGInfo:
    """PNG image metadata."""
    width: int
    height: int
    bit_depth: int
    color_type: ColorType
    compression: int
    filter_method: int
    interlace: int
    palette: Optional[List[Tuple[int, int, int, int]]] = None


class PNGDecodeError(Exception):
    """Error during PNG decoding."""
    pass


def _read_chunk(f: BinaryIO) -> Tuple[str, bytes]:
    """Read a PNG chunk.

    Args:
        f: File handle

    Returns:
        (chunk_type, chunk_data) tuple
    """
    length_bytes = f.read(4)
    if len(length_bytes) < 4:
        raise PNGDecodeError("Unexpected end of file reading chunk length")

    length = struct.unpack('>I', length_bytes)[0]
    chunk_type = f.read(4).decode('ascii')
    chunk_data = f.read(length)
    crc = f.read(4)  # CRC (we could verify this)

    if len(chunk_data) < length:
        raise PNGDecodeError(f"Unexpected end of file reading {chunk_type} chunk")

    return chunk_type, chunk_data


def _parse_ihdr(data: bytes) -> PNGInfo:
    """Parse IHDR chunk.

    Args:
        data: IHDR chunk data

    Returns:
        PNGInfo with image metadata
    """
    if len(data) < 13:
        raise PNGDecodeError("IHDR chunk too short")

    width, height, bit_depth, color_type, compression, filter_method, interlace = \
        struct.unpack('>IIBBBBB', data[:13])

    return PNGInfo(
        width=width,
        height=height,
        bit_depth=bit_depth,
        color_type=ColorType(color_type),
        compression=compression,
        filter_method=filter_method,
        interlace=interlace
    )


def _parse_plte(data: bytes) -> List[Tuple[int, int, int, int]]:
    """Parse PLTE (palette) chunk.

    Args:
        data: PLTE chunk data

    Returns:
        List of RGBA colors
    """
    if len(data) % 3 != 0:
        raise PNGDecodeError("Invalid PLTE chunk length")

    palette = []
    for i in range(0, len(data), 3):
        r, g, b = data[i], data[i + 1], data[i + 2]
        palette.append((r, g, b, 255))

    return palette


def _parse_trns(data: bytes, info: PNGInfo) -> None:
    """Parse tRNS (transparency) chunk.

    Args:
        data: tRNS chunk data
        info: PNG info (modified in place)
    """
    if info.color_type == ColorType.INDEXED and info.palette:
        # Alpha values for palette entries
        for i, alpha in enumerate(data):
            if i < len(info.palette):
                r, g, b, _ = info.palette[i]
                info.palette[i] = (r, g, b, alpha)


def _paeth_predictor(a: int, b: int, c: int) -> int:
    """Paeth predictor function.

    Args:
        a: Left pixel
        b: Above pixel
        c: Upper-left pixel

    Returns:
        Predicted value
    """
    p = a + b - c
    pa = abs(p - a)
    pb = abs(p - b)
    pc = abs(p - c)

    if pa <= pb and pa <= pc:
        return a
    elif pb <= pc:
        return b
    else:
        return c


def _reconstruct_scanline(filter_type: int, scanline: bytes,
                          prev_scanline: Optional[bytes],
                          bytes_per_pixel: int) -> bytes:
    """Reconstruct a filtered scanline.

    Args:
        filter_type: PNG filter type
        scanline: Filtered scanline data
        prev_scanline: Previous reconstructed scanline (or None)
        bytes_per_pixel: Bytes per pixel

    Returns:
        Reconstructed scanline
    """
    result = bytearray(len(scanline))
    bpp = bytes_per_pixel

    for i in range(len(scanline)):
        x = scanline[i]

        # Get neighboring pixels
        a = result[i - bpp] if i >= bpp else 0  # Left
        b = prev_scanline[i] if prev_scanline else 0  # Above
        c = prev_scanline[i - bpp] if prev_scanline and i >= bpp else 0  # Upper-left

        if filter_type == FilterType.NONE:
            result[i] = x
        elif filter_type == FilterType.SUB:
            result[i] = (x + a) & 0xFF
        elif filter_type == FilterType.UP:
            result[i] = (x + b) & 0xFF
        elif filter_type == FilterType.AVERAGE:
            result[i] = (x + (a + b) // 2) & 0xFF
        elif filter_type == FilterType.PAETH:
            result[i] = (x + _paeth_predictor(a, b, c)) & 0xFF
        else:
            raise PNGDecodeError(f"Unknown filter type: {filter_type}")

    return bytes(result)


def _get_bytes_per_pixel(info: PNGInfo) -> int:
    """Calculate bytes per pixel for a given color type.

    Args:
        info: PNG info

    Returns:
        Bytes per pixel
    """
    if info.color_type == ColorType.GRAYSCALE:
        return 1
    elif info.color_type == ColorType.RGB:
        return 3
    elif info.color_type == ColorType.INDEXED:
        return 1
    elif info.color_type == ColorType.GRAYSCALE_ALPHA:
        return 2
    elif info.color_type == ColorType.RGBA:
        return 4
    else:
        raise PNGDecodeError(f"Unsupported color type: {info.color_type}")


def _decode_pixels(raw_data: bytes, info: PNGInfo) -> List[List[Tuple[int, int, int, int]]]:
    """Decode raw pixel data into RGBA pixels.

    Args:
        raw_data: Decompressed and unfiltered pixel data
        info: PNG info

    Returns:
        2D list of RGBA pixel tuples
    """
    pixels = []
    bpp = _get_bytes_per_pixel(info)
    scanline_width = info.width * bpp

    for y in range(info.height):
        row = []
        offset = y * scanline_width

        for x in range(info.width):
            pixel_offset = offset + x * bpp

            if info.color_type == ColorType.GRAYSCALE:
                v = raw_data[pixel_offset]
                row.append((v, v, v, 255))

            elif info.color_type == ColorType.RGB:
                r = raw_data[pixel_offset]
                g = raw_data[pixel_offset + 1]
                b = raw_data[pixel_offset + 2]
                row.append((r, g, b, 255))

            elif info.color_type == ColorType.INDEXED:
                idx = raw_data[pixel_offset]
                if info.palette and idx < len(info.palette):
                    row.append(info.palette[idx])
                else:
                    row.append((0, 0, 0, 255))

            elif info.color_type == ColorType.GRAYSCALE_ALPHA:
                v = raw_data[pixel_offset]
                a = raw_data[pixel_offset + 1]
                row.append((v, v, v, a))

            elif info.color_type == ColorType.RGBA:
                r = raw_data[pixel_offset]
                g = raw_data[pixel_offset + 1]
                b = raw_data[pixel_offset + 2]
                a = raw_data[pixel_offset + 3]
                row.append((r, g, b, a))

        pixels.append(row)

    return pixels


def load_png(filepath: str) -> Canvas:
    """Load a PNG file into a Canvas.

    Args:
        filepath: Path to PNG file

    Returns:
        Canvas with loaded image

    Raises:
        PNGDecodeError: If the file is not a valid PNG or uses unsupported features
        FileNotFoundError: If file doesn't exist
    """
    with open(filepath, 'rb') as f:
        return load_png_from_file(f)


def load_png_from_file(f: BinaryIO) -> Canvas:
    """Load a PNG from a file handle.

    Args:
        f: File handle opened in binary mode

    Returns:
        Canvas with loaded image
    """
    # Verify signature
    signature = f.read(8)
    if signature != PNG_SIGNATURE:
        raise PNGDecodeError("Not a valid PNG file (invalid signature)")

    info: Optional[PNGInfo] = None
    idat_chunks: List[bytes] = []

    # Read chunks
    while True:
        try:
            chunk_type, chunk_data = _read_chunk(f)
        except PNGDecodeError:
            break

        if chunk_type == 'IHDR':
            info = _parse_ihdr(chunk_data)
        elif chunk_type == 'PLTE':
            if info:
                info.palette = _parse_plte(chunk_data)
        elif chunk_type == 'tRNS':
            if info:
                _parse_trns(chunk_data, info)
        elif chunk_type == 'IDAT':
            idat_chunks.append(chunk_data)
        elif chunk_type == 'IEND':
            break

    if info is None:
        raise PNGDecodeError("No IHDR chunk found")

    if not idat_chunks:
        raise PNGDecodeError("No IDAT chunks found")

    # Check for unsupported features
    if info.bit_depth != 8:
        raise PNGDecodeError(f"Unsupported bit depth: {info.bit_depth} (only 8-bit supported)")

    if info.interlace != 0:
        raise PNGDecodeError("Interlaced PNGs not supported")

    # Decompress IDAT data
    compressed_data = b''.join(idat_chunks)
    try:
        decompressed = zlib.decompress(compressed_data)
    except zlib.error as e:
        raise PNGDecodeError(f"Failed to decompress image data: {e}")

    # Reconstruct scanlines
    bpp = _get_bytes_per_pixel(info)
    scanline_width = info.width * bpp
    expected_size = info.height * (1 + scanline_width)  # 1 byte filter + pixel data

    if len(decompressed) < expected_size:
        raise PNGDecodeError(
            f"Decompressed data too short: {len(decompressed)} < {expected_size}"
        )

    # Unfilter scanlines
    raw_pixels = bytearray()
    prev_scanline: Optional[bytes] = None

    for y in range(info.height):
        offset = y * (1 + scanline_width)
        filter_type = decompressed[offset]
        scanline = decompressed[offset + 1:offset + 1 + scanline_width]

        reconstructed = _reconstruct_scanline(
            filter_type, scanline, prev_scanline, bpp
        )
        raw_pixels.extend(reconstructed)
        prev_scanline = reconstructed

    # Decode to RGBA pixels
    pixels = _decode_pixels(bytes(raw_pixels), info)

    # Create canvas
    canvas = Canvas(info.width, info.height)
    canvas.pixels = pixels

    return canvas


def load_png_from_bytes(data: bytes) -> Canvas:
    """Load a PNG from bytes.

    Args:
        data: PNG file data as bytes

    Returns:
        Canvas with loaded image
    """
    import io
    return load_png_from_file(io.BytesIO(data))


def get_png_info(filepath: str) -> PNGInfo:
    """Get information about a PNG file without fully loading it.

    Args:
        filepath: Path to PNG file

    Returns:
        PNGInfo with image metadata
    """
    with open(filepath, 'rb') as f:
        signature = f.read(8)
        if signature != PNG_SIGNATURE:
            raise PNGDecodeError("Not a valid PNG file")

        chunk_type, chunk_data = _read_chunk(f)
        if chunk_type != 'IHDR':
            raise PNGDecodeError("First chunk is not IHDR")

        return _parse_ihdr(chunk_data)


class ImageLoader:
    """High-level image loading utilities."""

    @staticmethod
    def load(filepath: str) -> Canvas:
        """Load an image file.

        Currently supports PNG format.

        Args:
            filepath: Path to image file

        Returns:
            Canvas with loaded image
        """
        ext = os.path.splitext(filepath)[1].lower()

        if ext == '.png':
            return load_png(filepath)
        else:
            raise ValueError(f"Unsupported image format: {ext}")

    @staticmethod
    def can_load(filepath: str) -> bool:
        """Check if a file format is supported.

        Args:
            filepath: Path to image file

        Returns:
            True if format is supported
        """
        ext = os.path.splitext(filepath)[1].lower()
        return ext in ('.png',)


def extract_palette(canvas: Canvas, max_colors: int = 256) -> List[Tuple[int, int, int, int]]:
    """Extract unique colors from a canvas.

    Args:
        canvas: Source canvas
        max_colors: Maximum colors to extract

    Returns:
        List of unique RGBA colors
    """
    colors = set()

    for row in canvas.pixels:
        for pixel in row:
            colors.add(pixel)
            if len(colors) >= max_colors:
                break
        if len(colors) >= max_colors:
            break

    return sorted(list(colors))


def count_colors(canvas: Canvas) -> int:
    """Count unique colors in a canvas.

    Args:
        canvas: Source canvas

    Returns:
        Number of unique colors
    """
    colors = set()
    for row in canvas.pixels:
        for pixel in row:
            colors.add(pixel)
    return len(colors)


def has_transparency(canvas: Canvas) -> bool:
    """Check if canvas has any transparent pixels.

    Args:
        canvas: Source canvas

    Returns:
        True if any pixel has alpha < 255
    """
    for row in canvas.pixels:
        for pixel in row:
            if pixel[3] < 255:
                return True
    return False


def get_bounding_box(canvas: Canvas) -> Optional[Tuple[int, int, int, int]]:
    """Get the bounding box of non-transparent pixels.

    Args:
        canvas: Source canvas

    Returns:
        (x, y, width, height) or None if all transparent
    """
    min_x = canvas.width
    min_y = canvas.height
    max_x = -1
    max_y = -1

    for y in range(canvas.height):
        for x in range(canvas.width):
            if canvas.pixels[y][x][3] > 0:
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)

    if max_x < 0:
        return None

    return (min_x, min_y, max_x - min_x + 1, max_y - min_y + 1)


def trim_canvas(canvas: Canvas) -> Canvas:
    """Trim transparent edges from canvas.

    Args:
        canvas: Source canvas

    Returns:
        New canvas with transparent edges removed
    """
    bbox = get_bounding_box(canvas)
    if bbox is None:
        return Canvas(1, 1, (0, 0, 0, 0))

    x, y, w, h = bbox
    result = Canvas(w, h, (0, 0, 0, 0))

    for dy in range(h):
        for dx in range(w):
            result.pixels[dy][dx] = canvas.pixels[y + dy][x + dx]

    return result

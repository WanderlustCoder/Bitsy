"""Aseprite file reader (.ase/.aseprite format).

Based on the Aseprite file format specification:
https://github.com/aseprite/aseprite/blob/main/docs/ase-file-specs.md
"""

from dataclasses import dataclass, field
from enum import IntEnum
from typing import List, Tuple, Optional, Dict, BinaryIO
import struct
import zlib

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Canvas
from core.palette import Palette

Color = Tuple[int, int, int, int]


class ColorDepth(IntEnum):
    """Aseprite color depth modes."""
    INDEXED = 8
    GRAYSCALE = 16
    RGBA = 32


class BlendMode(IntEnum):
    """Aseprite layer blend modes."""
    NORMAL = 0
    MULTIPLY = 1
    SCREEN = 2
    OVERLAY = 3
    DARKEN = 4
    LIGHTEN = 5
    COLOR_DODGE = 6
    COLOR_BURN = 7
    HARD_LIGHT = 8
    SOFT_LIGHT = 9
    DIFFERENCE = 10
    EXCLUSION = 11
    HUE = 12
    SATURATION = 13
    COLOR = 14
    LUMINOSITY = 15
    ADDITION = 16
    SUBTRACT = 17
    DIVIDE = 18


class ChunkType(IntEnum):
    """Aseprite chunk types."""
    OLD_PALETTE_1 = 0x0004
    OLD_PALETTE_2 = 0x0011
    LAYER = 0x2004
    CEL = 0x2005
    CEL_EXTRA = 0x2006
    COLOR_PROFILE = 0x2007
    EXTERNAL_FILES = 0x2008
    MASK = 0x2016
    PATH = 0x2017
    TAGS = 0x2018
    PALETTE = 0x2019
    USER_DATA = 0x2020
    SLICE = 0x2022
    TILESET = 0x2023


class CelType(IntEnum):
    """Aseprite cel types."""
    RAW = 0
    LINKED = 1
    COMPRESSED = 2
    COMPRESSED_TILEMAP = 3


@dataclass
class AsepriteLayer:
    """An Aseprite layer."""
    name: str
    visible: bool
    opacity: int
    blend_mode: int
    layer_type: int  # 0=normal, 1=group
    child_level: int
    flags: int

    def is_visible(self) -> bool:
        return self.visible and (self.flags & 1) != 0


@dataclass
class AsepriteCel:
    """A cel (image on a layer in a frame)."""
    layer_index: int
    x: int
    y: int
    opacity: int
    cel_type: int
    width: int = 0
    height: int = 0
    pixels: Optional[List[List[Color]]] = None
    linked_frame: int = -1


@dataclass
class AsepriteFrame:
    """A frame in the animation."""
    duration: int  # milliseconds
    cels: Dict[int, AsepriteCel] = field(default_factory=dict)  # layer_index -> cel


@dataclass
class AsepriteTag:
    """An animation tag."""
    name: str
    from_frame: int
    to_frame: int
    direction: int  # 0=forward, 1=reverse, 2=ping-pong
    repeat: int
    color: Color


@dataclass
class AsepriteFile:
    """A loaded Aseprite file."""
    width: int
    height: int
    color_depth: int
    frames: List[AsepriteFrame]
    layers: List[AsepriteLayer]
    palette: Optional[Palette]
    tags: List[AsepriteTag]
    transparent_index: int = 0

    def get_frame(self, index: int, flatten: bool = True) -> Canvas:
        """Get a frame as a canvas.

        Args:
            index: Frame index
            flatten: If True, composite all visible layers

        Returns:
            Canvas with frame content
        """
        if index < 0 or index >= len(self.frames):
            return Canvas(self.width, self.height)

        frame = self.frames[index]
        result = Canvas(self.width, self.height)

        if flatten:
            # Composite all visible layers from bottom to top
            for layer_idx in range(len(self.layers)):
                layer = self.layers[layer_idx]
                if not layer.is_visible():
                    continue

                if layer_idx in frame.cels:
                    cel = frame.cels[layer_idx]
                    self._composite_cel(result, cel, layer)
        else:
            # Just return the first cel found
            for cel in frame.cels.values():
                if cel.pixels:
                    self._blit_cel(result, cel)
                    break

        return result

    def get_animation(self, tag: Optional[str] = None) -> List[Canvas]:
        """Get animation frames.

        Args:
            tag: Animation tag name (None for all frames)

        Returns:
            List of canvases
        """
        if tag is None:
            return [self.get_frame(i) for i in range(len(self.frames))]

        # Find tag
        for t in self.tags:
            if t.name == tag:
                frames = []
                for i in range(t.from_frame, t.to_frame + 1):
                    frames.append(self.get_frame(i))

                if t.direction == 1:  # Reverse
                    frames.reverse()
                elif t.direction == 2:  # Ping-pong
                    frames = frames + frames[-2:0:-1]

                return frames

        return []

    def get_layer(self, name: str) -> List[Canvas]:
        """Get all frames for a specific layer.

        Args:
            name: Layer name

        Returns:
            List of canvases (one per frame)
        """
        layer_idx = None
        for i, layer in enumerate(self.layers):
            if layer.name == name:
                layer_idx = i
                break

        if layer_idx is None:
            return []

        frames = []
        for frame in self.frames:
            canvas = Canvas(self.width, self.height)
            if layer_idx in frame.cels:
                cel = frame.cels[layer_idx]
                self._blit_cel(canvas, cel)
            frames.append(canvas)

        return frames

    def get_frame_durations(self) -> List[int]:
        """Get duration of each frame in milliseconds."""
        return [f.duration for f in self.frames]

    def list_layers(self) -> List[str]:
        """Get list of layer names."""
        return [l.name for l in self.layers]

    def list_tags(self) -> List[str]:
        """Get list of tag names."""
        return [t.name for t in self.tags]

    def _composite_cel(self, canvas: Canvas, cel: AsepriteCel, layer: AsepriteLayer):
        """Composite a cel onto a canvas."""
        if cel.pixels is None:
            return

        opacity = (cel.opacity * layer.opacity) // 255

        for y, row in enumerate(cel.pixels):
            canvas_y = cel.y + y
            if canvas_y < 0 or canvas_y >= canvas.height:
                continue

            for x, color in enumerate(row):
                canvas_x = cel.x + x
                if canvas_x < 0 or canvas_x >= canvas.width:
                    continue

                if color[3] == 0:
                    continue

                # Apply opacity
                alpha = (color[3] * opacity) // 255
                if alpha == 0:
                    continue

                src = (color[0], color[1], color[2], alpha)
                dst = canvas.get_pixel(canvas_x, canvas_y)

                # Normal blend
                blended = self._blend_normal(src, dst)
                canvas.set_pixel(canvas_x, canvas_y, blended)

    def _blit_cel(self, canvas: Canvas, cel: AsepriteCel):
        """Blit a cel onto a canvas without blending."""
        if cel.pixels is None:
            return

        for y, row in enumerate(cel.pixels):
            canvas_y = cel.y + y
            if canvas_y < 0 or canvas_y >= canvas.height:
                continue

            for x, color in enumerate(row):
                canvas_x = cel.x + x
                if canvas_x < 0 or canvas_x >= canvas.width:
                    continue

                if color[3] > 0:
                    canvas.set_pixel(canvas_x, canvas_y, color)

    def _blend_normal(self, src: Color, dst: Color) -> Color:
        """Normal alpha blending."""
        sa = src[3] / 255.0
        da = dst[3] / 255.0
        oa = sa + da * (1 - sa)

        if oa == 0:
            return (0, 0, 0, 0)

        r = int((src[0] * sa + dst[0] * da * (1 - sa)) / oa)
        g = int((src[1] * sa + dst[1] * da * (1 - sa)) / oa)
        b = int((src[2] * sa + dst[2] * da * (1 - sa)) / oa)
        a = int(oa * 255)

        return (r, g, b, a)


class AsepriteReader:
    """Reads Aseprite files."""

    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0
        self.width = 0
        self.height = 0
        self.color_depth = 0
        self.transparent_index = 0
        self.num_frames = 0
        self.frames: List[AsepriteFrame] = []
        self.layers: List[AsepriteLayer] = []
        self.palette_colors: List[Color] = []
        self.tags: List[AsepriteTag] = []

    def read(self) -> AsepriteFile:
        """Read and parse the file."""
        self._read_header()
        self._read_frames()

        palette = None
        if self.palette_colors:
            palette = Palette(self.palette_colors, "Aseprite")

        return AsepriteFile(
            width=self.width,
            height=self.height,
            color_depth=self.color_depth,
            frames=self.frames,
            layers=self.layers,
            palette=palette,
            tags=self.tags,
            transparent_index=self.transparent_index
        )

    def _read_header(self):
        """Read file header."""
        # File size
        file_size = self._read_dword()

        # Magic number
        magic = self._read_word()
        if magic != 0xA5E0:
            raise ValueError(f"Invalid Aseprite magic number: {magic:#x}")

        # Frame count
        self.num_frames = self._read_word()

        # Dimensions
        self.width = self._read_word()
        self.height = self._read_word()

        # Color depth
        self.color_depth = self._read_word()

        # Flags
        flags = self._read_dword()

        # Speed (deprecated)
        speed = self._read_word()

        # Reserved
        self._skip(8)

        # Transparent color index
        self.transparent_index = self._read_byte()

        # Reserved
        self._skip(3)

        # Number of colors
        num_colors = self._read_word()

        # Pixel dimensions
        pixel_width = self._read_byte()
        pixel_height = self._read_byte()

        # Grid position and size
        self._skip(8)

        # Reserved
        self._skip(84)

    def _read_frames(self):
        """Read all frames."""
        for frame_idx in range(self.num_frames):
            frame = self._read_frame(frame_idx)
            self.frames.append(frame)

    def _read_frame(self, frame_idx: int) -> AsepriteFrame:
        """Read a single frame."""
        frame_start = self.pos

        # Frame size
        frame_size = self._read_dword()

        # Magic
        magic = self._read_word()
        if magic != 0xF1FA:
            raise ValueError(f"Invalid frame magic: {magic:#x}")

        # Old chunk count (for compat)
        old_chunk_count = self._read_word()

        # Duration
        duration = self._read_word()

        # Reserved
        self._skip(2)

        # New chunk count
        new_chunk_count = self._read_dword()

        # Use new count if available
        num_chunks = new_chunk_count if new_chunk_count != 0 else old_chunk_count

        frame = AsepriteFrame(duration=duration)

        # Read chunks
        for _ in range(num_chunks):
            self._read_chunk(frame, frame_idx)

        return frame

    def _read_chunk(self, frame: AsepriteFrame, frame_idx: int):
        """Read a chunk within a frame."""
        chunk_start = self.pos

        chunk_size = self._read_dword()
        chunk_type = self._read_word()

        if chunk_type == ChunkType.LAYER:
            self._read_layer_chunk()
        elif chunk_type == ChunkType.CEL:
            cel = self._read_cel_chunk(frame_idx)
            if cel:
                frame.cels[cel.layer_index] = cel
        elif chunk_type == ChunkType.PALETTE:
            self._read_palette_chunk()
        elif chunk_type == ChunkType.OLD_PALETTE_1 or chunk_type == ChunkType.OLD_PALETTE_2:
            self._read_old_palette_chunk(chunk_type)
        elif chunk_type == ChunkType.TAGS:
            self._read_tags_chunk()

        # Skip to end of chunk
        self.pos = chunk_start + chunk_size

    def _read_layer_chunk(self):
        """Read a layer chunk."""
        flags = self._read_word()
        layer_type = self._read_word()
        child_level = self._read_word()
        default_width = self._read_word()
        default_height = self._read_word()
        blend_mode = self._read_word()
        opacity = self._read_byte()
        self._skip(3)
        name = self._read_string()

        layer = AsepriteLayer(
            name=name,
            visible=(flags & 1) != 0,
            opacity=opacity,
            blend_mode=blend_mode,
            layer_type=layer_type,
            child_level=child_level,
            flags=flags
        )
        self.layers.append(layer)

    def _read_cel_chunk(self, frame_idx: int) -> Optional[AsepriteCel]:
        """Read a cel chunk."""
        layer_index = self._read_word()
        x = self._read_short()
        y = self._read_short()
        opacity = self._read_byte()
        cel_type = self._read_word()
        z_index = self._read_short()
        self._skip(5)

        cel = AsepriteCel(
            layer_index=layer_index,
            x=x,
            y=y,
            opacity=opacity,
            cel_type=cel_type
        )

        if cel_type == CelType.RAW:
            cel.width = self._read_word()
            cel.height = self._read_word()
            cel.pixels = self._read_pixels(cel.width, cel.height)
        elif cel_type == CelType.LINKED:
            cel.linked_frame = self._read_word()
            # Copy pixels from linked frame
            if cel.linked_frame < len(self.frames):
                linked_frame = self.frames[cel.linked_frame]
                if layer_index in linked_frame.cels:
                    linked_cel = linked_frame.cels[layer_index]
                    cel.width = linked_cel.width
                    cel.height = linked_cel.height
                    cel.pixels = linked_cel.pixels
        elif cel_type == CelType.COMPRESSED:
            cel.width = self._read_word()
            cel.height = self._read_word()
            cel.pixels = self._read_compressed_pixels(cel.width, cel.height)

        return cel

    def _read_pixels(self, width: int, height: int) -> List[List[Color]]:
        """Read raw pixel data."""
        pixels = []
        for y in range(height):
            row = []
            for x in range(width):
                color = self._read_pixel()
                row.append(color)
            pixels.append(row)
        return pixels

    def _read_compressed_pixels(self, width: int, height: int) -> List[List[Color]]:
        """Read zlib-compressed pixel data."""
        # Find remaining data in chunk
        # Read all remaining bytes as compressed data
        compressed_start = self.pos

        # Decompress
        try:
            # Read until we have enough decompressed data
            bytes_per_pixel = self.color_depth // 8
            expected_size = width * height * bytes_per_pixel

            # Try to decompress with increasing amounts of input
            decompressed = None
            for try_size in [expected_size * 2, expected_size * 4, len(self.data) - self.pos]:
                try:
                    compressed = self.data[compressed_start:compressed_start + try_size]
                    decompressed = zlib.decompress(compressed)
                    if len(decompressed) >= expected_size:
                        break
                except zlib.error:
                    continue

            if decompressed is None:
                return [[]] * height

            # Parse decompressed pixel data
            pixels = []
            offset = 0
            for y in range(height):
                row = []
                for x in range(width):
                    color = self._parse_pixel(decompressed, offset)
                    offset += bytes_per_pixel
                    row.append(color)
                pixels.append(row)

            return pixels

        except Exception:
            return [[]] * height

    def _read_pixel(self) -> Color:
        """Read a single pixel based on color depth."""
        if self.color_depth == ColorDepth.RGBA:
            r = self._read_byte()
            g = self._read_byte()
            b = self._read_byte()
            a = self._read_byte()
            return (r, g, b, a)
        elif self.color_depth == ColorDepth.GRAYSCALE:
            v = self._read_byte()
            a = self._read_byte()
            return (v, v, v, a)
        else:  # INDEXED
            idx = self._read_byte()
            if idx == self.transparent_index:
                return (0, 0, 0, 0)
            if idx < len(self.palette_colors):
                return self.palette_colors[idx]
            return (idx, idx, idx, 255)

    def _parse_pixel(self, data: bytes, offset: int) -> Color:
        """Parse a pixel from decompressed data."""
        if self.color_depth == ColorDepth.RGBA:
            r = data[offset]
            g = data[offset + 1]
            b = data[offset + 2]
            a = data[offset + 3]
            return (r, g, b, a)
        elif self.color_depth == ColorDepth.GRAYSCALE:
            v = data[offset]
            a = data[offset + 1]
            return (v, v, v, a)
        else:  # INDEXED
            idx = data[offset]
            if idx == self.transparent_index:
                return (0, 0, 0, 0)
            if idx < len(self.palette_colors):
                return self.palette_colors[idx]
            return (idx, idx, idx, 255)

    def _read_palette_chunk(self):
        """Read a palette chunk."""
        size = self._read_dword()
        first = self._read_dword()
        last = self._read_dword()
        self._skip(8)

        # Ensure palette is big enough
        while len(self.palette_colors) < last + 1:
            self.palette_colors.append((0, 0, 0, 255))

        for i in range(first, last + 1):
            flags = self._read_word()
            r = self._read_byte()
            g = self._read_byte()
            b = self._read_byte()
            a = self._read_byte()

            self.palette_colors[i] = (r, g, b, a)

            if flags & 1:  # Has name
                name = self._read_string()

    def _read_old_palette_chunk(self, chunk_type: int):
        """Read old-style palette chunk."""
        num_packets = self._read_word()

        for _ in range(num_packets):
            skip = self._read_byte()
            num_colors = self._read_byte()
            if num_colors == 0:
                num_colors = 256

            while len(self.palette_colors) < skip + num_colors:
                self.palette_colors.append((0, 0, 0, 255))

            for i in range(num_colors):
                r = self._read_byte()
                g = self._read_byte()
                b = self._read_byte()
                self.palette_colors[skip + i] = (r, g, b, 255)

    def _read_tags_chunk(self):
        """Read animation tags chunk."""
        num_tags = self._read_word()
        self._skip(8)

        for _ in range(num_tags):
            from_frame = self._read_word()
            to_frame = self._read_word()
            direction = self._read_byte()
            repeat = self._read_word()
            self._skip(6)

            # Tag color (RGB)
            r = self._read_byte()
            g = self._read_byte()
            b = self._read_byte()
            self._skip(1)

            name = self._read_string()

            tag = AsepriteTag(
                name=name,
                from_frame=from_frame,
                to_frame=to_frame,
                direction=direction,
                repeat=repeat,
                color=(r, g, b, 255)
            )
            self.tags.append(tag)

    def _read_string(self) -> str:
        """Read a length-prefixed string."""
        length = self._read_word()
        if length == 0:
            return ""
        data = self.data[self.pos:self.pos + length]
        self.pos += length
        return data.decode('utf-8', errors='replace')

    def _read_byte(self) -> int:
        """Read unsigned byte."""
        value = self.data[self.pos]
        self.pos += 1
        return value

    def _read_word(self) -> int:
        """Read unsigned 16-bit word (little-endian)."""
        value = struct.unpack_from('<H', self.data, self.pos)[0]
        self.pos += 2
        return value

    def _read_short(self) -> int:
        """Read signed 16-bit short (little-endian)."""
        value = struct.unpack_from('<h', self.data, self.pos)[0]
        self.pos += 2
        return value

    def _read_dword(self) -> int:
        """Read unsigned 32-bit dword (little-endian)."""
        value = struct.unpack_from('<I', self.data, self.pos)[0]
        self.pos += 4
        return value

    def _skip(self, count: int):
        """Skip bytes."""
        self.pos += count


# Public functions

def load_aseprite(path: str) -> AsepriteFile:
    """Load an Aseprite file.

    Args:
        path: Path to .ase or .aseprite file

    Returns:
        Loaded AsepriteFile
    """
    with open(path, 'rb') as f:
        data = f.read()
    return load_aseprite_from_bytes(data)


def load_aseprite_from_bytes(data: bytes) -> AsepriteFile:
    """Load an Aseprite file from bytes.

    Args:
        data: File contents as bytes

    Returns:
        Loaded AsepriteFile
    """
    reader = AsepriteReader(data)
    return reader.read()

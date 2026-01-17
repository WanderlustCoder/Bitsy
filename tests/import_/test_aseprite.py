"""Tests for Aseprite file reading."""

import pytest
import struct
import zlib
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core import Canvas
from import_.aseprite import (
    AsepriteLayer,
    AsepriteFrame,
    AsepriteCel,
    AsepriteTag,
    AsepriteFile,
    AsepriteReader,
    ColorDepth,
    ChunkType,
    load_aseprite_from_bytes,
)


def create_minimal_aseprite(width=16, height=16, color_depth=32, num_frames=1):
    """Create minimal valid Aseprite file bytes."""
    data = bytearray()

    # Header
    header_size = 128
    frame_size = 16 + 4  # Frame header + one empty chunk list

    file_size = header_size + num_frames * frame_size

    # File size (will update later)
    data.extend(struct.pack('<I', file_size))
    # Magic number
    data.extend(struct.pack('<H', 0xA5E0))
    # Frames
    data.extend(struct.pack('<H', num_frames))
    # Width, Height
    data.extend(struct.pack('<H', width))
    data.extend(struct.pack('<H', height))
    # Color depth
    data.extend(struct.pack('<H', color_depth))
    # Flags
    data.extend(struct.pack('<I', 1))  # Layer opacity has valid value
    # Speed (deprecated)
    data.extend(struct.pack('<H', 100))
    # Reserved
    data.extend(b'\x00' * 8)
    # Transparent index
    data.append(0)
    # Reserved
    data.extend(b'\x00' * 3)
    # Number of colors
    data.extend(struct.pack('<H', 256))
    # Pixel width/height
    data.append(1)
    data.append(1)
    # Grid position/size
    data.extend(b'\x00' * 8)
    # Reserved
    data.extend(b'\x00' * 84)

    # Frames
    for _ in range(num_frames):
        frame_start = len(data)

        # Frame size (placeholder)
        data.extend(struct.pack('<I', frame_size))
        # Magic
        data.extend(struct.pack('<H', 0xF1FA))
        # Old chunk count
        data.extend(struct.pack('<H', 0))
        # Duration
        data.extend(struct.pack('<H', 100))  # 100ms
        # Reserved
        data.extend(b'\x00' * 2)
        # New chunk count
        data.extend(struct.pack('<I', 0))

    return bytes(data)


def create_aseprite_with_layer(width=8, height=8):
    """Create Aseprite file with a layer."""
    data = bytearray()

    # Calculate sizes
    header_size = 128

    # Layer chunk
    layer_name = b"Layer 1"
    layer_chunk_size = 4 + 2 + 2 + 2 + 2 + 2 + 2 + 1 + 3 + 2 + len(layer_name)

    frame_size = 16 + layer_chunk_size

    file_size = header_size + frame_size

    # === Header ===
    data.extend(struct.pack('<I', file_size))
    data.extend(struct.pack('<H', 0xA5E0))
    data.extend(struct.pack('<H', 1))  # 1 frame
    data.extend(struct.pack('<H', width))
    data.extend(struct.pack('<H', height))
    data.extend(struct.pack('<H', 32))  # RGBA
    data.extend(struct.pack('<I', 1))
    data.extend(struct.pack('<H', 100))
    data.extend(b'\x00' * 8)
    data.append(0)
    data.extend(b'\x00' * 3)
    data.extend(struct.pack('<H', 256))
    data.append(1)
    data.append(1)
    data.extend(b'\x00' * 8)
    data.extend(b'\x00' * 84)

    # === Frame ===
    data.extend(struct.pack('<I', frame_size))
    data.extend(struct.pack('<H', 0xF1FA))
    data.extend(struct.pack('<H', 1))  # 1 chunk (old count)
    data.extend(struct.pack('<H', 100))
    data.extend(b'\x00' * 2)
    data.extend(struct.pack('<I', 1))  # 1 chunk (new count)

    # Layer chunk
    data.extend(struct.pack('<I', layer_chunk_size))
    data.extend(struct.pack('<H', ChunkType.LAYER))
    data.extend(struct.pack('<H', 1))  # Flags: visible
    data.extend(struct.pack('<H', 0))  # Layer type: normal
    data.extend(struct.pack('<H', 0))  # Child level
    data.extend(struct.pack('<H', 0))  # Default width
    data.extend(struct.pack('<H', 0))  # Default height
    data.extend(struct.pack('<H', 0))  # Blend mode: normal
    data.append(255)  # Opacity
    data.extend(b'\x00' * 3)  # Reserved
    data.extend(struct.pack('<H', len(layer_name)))
    data.extend(layer_name)

    return bytes(data)


def create_aseprite_with_cel(width=4, height=4):
    """Create Aseprite file with a layer and cel (raw pixels)."""
    data = bytearray()

    # Pixel data (RGBA)
    pixel_data = []
    for y in range(height):
        for x in range(width):
            pixel_data.extend([255, 0, 0, 255])  # Red pixels
    pixel_bytes = bytes(pixel_data)

    # Calculate sizes
    header_size = 128
    layer_name = b"Layer 1"
    layer_chunk_size = 4 + 2 + 2 + 2 + 2 + 2 + 2 + 2 + 1 + 3 + 2 + len(layer_name)
    cel_chunk_size = 4 + 2 + 2 + 2 + 2 + 1 + 2 + 2 + 5 + 2 + 2 + len(pixel_bytes)
    frame_size = 16 + layer_chunk_size + cel_chunk_size
    file_size = header_size + frame_size

    # === Header ===
    data.extend(struct.pack('<I', file_size))
    data.extend(struct.pack('<H', 0xA5E0))
    data.extend(struct.pack('<H', 1))
    data.extend(struct.pack('<H', width))
    data.extend(struct.pack('<H', height))
    data.extend(struct.pack('<H', 32))  # RGBA
    data.extend(struct.pack('<I', 1))
    data.extend(struct.pack('<H', 100))
    data.extend(b'\x00' * 8)
    data.append(0)
    data.extend(b'\x00' * 3)
    data.extend(struct.pack('<H', 256))
    data.append(1)
    data.append(1)
    data.extend(b'\x00' * 8)
    data.extend(b'\x00' * 84)

    # === Frame ===
    data.extend(struct.pack('<I', frame_size))
    data.extend(struct.pack('<H', 0xF1FA))
    data.extend(struct.pack('<H', 2))
    data.extend(struct.pack('<H', 100))
    data.extend(b'\x00' * 2)
    data.extend(struct.pack('<I', 2))

    # Layer chunk
    data.extend(struct.pack('<I', layer_chunk_size))
    data.extend(struct.pack('<H', ChunkType.LAYER))
    data.extend(struct.pack('<H', 1))
    data.extend(struct.pack('<H', 0))
    data.extend(struct.pack('<H', 0))
    data.extend(struct.pack('<H', 0))
    data.extend(struct.pack('<H', 0))
    data.extend(struct.pack('<H', 0))
    data.append(255)
    data.extend(b'\x00' * 3)
    data.extend(struct.pack('<H', len(layer_name)))
    data.extend(layer_name)

    # Cel chunk (raw)
    data.extend(struct.pack('<I', cel_chunk_size))
    data.extend(struct.pack('<H', ChunkType.CEL))
    data.extend(struct.pack('<H', 0))  # Layer index
    data.extend(struct.pack('<h', 0))  # X position
    data.extend(struct.pack('<h', 0))  # Y position
    data.append(255)  # Opacity
    data.extend(struct.pack('<H', 0))  # Cel type: raw
    data.extend(struct.pack('<h', 0))  # Z-index
    data.extend(b'\x00' * 5)  # Reserved
    data.extend(struct.pack('<H', width))  # Width
    data.extend(struct.pack('<H', height))  # Height
    data.extend(pixel_bytes)

    return bytes(data)


class TestAsepriteReader:
    """Tests for AsepriteReader."""

    def test_read_minimal(self):
        """Test reading minimal Aseprite file."""
        data = create_minimal_aseprite()
        result = load_aseprite_from_bytes(data)

        assert result.width == 16
        assert result.height == 16
        assert result.color_depth == 32
        assert len(result.frames) == 1

    def test_read_dimensions(self):
        """Test reading different dimensions."""
        for w, h in [(8, 8), (32, 16), (64, 64)]:
            data = create_minimal_aseprite(width=w, height=h)
            result = load_aseprite_from_bytes(data)
            assert result.width == w
            assert result.height == h

    def test_read_multiple_frames(self):
        """Test reading multiple frames."""
        data = create_minimal_aseprite(num_frames=4)
        result = load_aseprite_from_bytes(data)

        assert len(result.frames) == 4

    def test_read_with_layer(self):
        """Test reading file with layer."""
        data = create_aseprite_with_layer()
        result = load_aseprite_from_bytes(data)

        assert len(result.layers) == 1
        assert result.layers[0].name == "Layer 1"
        assert result.layers[0].visible is True

    def test_read_with_cel(self):
        """Test reading file with cel (pixel data)."""
        data = create_aseprite_with_cel(4, 4)
        result = load_aseprite_from_bytes(data)

        assert len(result.layers) == 1
        assert len(result.frames) == 1
        assert 0 in result.frames[0].cels

        cel = result.frames[0].cels[0]
        assert cel.width == 4
        assert cel.height == 4
        assert cel.pixels is not None

    def test_invalid_magic(self):
        """Test error on invalid magic number."""
        data = bytearray(create_minimal_aseprite())
        # Corrupt magic number
        data[4] = 0x00
        data[5] = 0x00

        with pytest.raises(ValueError, match="Invalid Aseprite magic"):
            load_aseprite_from_bytes(bytes(data))


class TestAsepriteFile:
    """Tests for AsepriteFile class."""

    def test_get_frame(self):
        """Test getting frame as canvas."""
        data = create_aseprite_with_cel(4, 4)
        ase = load_aseprite_from_bytes(data)

        frame = ase.get_frame(0)
        assert frame.width == 4
        assert frame.height == 4

        # Check pixel is red
        pixel = frame.get_pixel(0, 0)
        assert pixel == (255, 0, 0, 255)

    def test_get_frame_out_of_bounds(self):
        """Test getting frame with invalid index."""
        data = create_minimal_aseprite(num_frames=2)
        ase = load_aseprite_from_bytes(data)

        # Should return empty canvas for invalid index
        frame = ase.get_frame(10)
        assert frame.width == 16
        assert frame.height == 16

    def test_get_animation(self):
        """Test getting all animation frames."""
        data = create_minimal_aseprite(num_frames=4)
        ase = load_aseprite_from_bytes(data)

        frames = ase.get_animation()
        assert len(frames) == 4

    def test_get_frame_durations(self):
        """Test getting frame durations."""
        data = create_minimal_aseprite(num_frames=3)
        ase = load_aseprite_from_bytes(data)

        durations = ase.get_frame_durations()
        assert len(durations) == 3
        assert all(d == 100 for d in durations)  # Default 100ms

    def test_list_layers(self):
        """Test listing layer names."""
        data = create_aseprite_with_layer()
        ase = load_aseprite_from_bytes(data)

        layers = ase.list_layers()
        assert "Layer 1" in layers

    def test_list_tags(self):
        """Test listing tag names."""
        data = create_minimal_aseprite()
        ase = load_aseprite_from_bytes(data)

        tags = ase.list_tags()
        assert tags == []  # No tags in minimal file


class TestAsepriteLayer:
    """Tests for AsepriteLayer."""

    def test_is_visible(self):
        """Test layer visibility check."""
        layer = AsepriteLayer(
            name="Test",
            visible=True,
            opacity=255,
            blend_mode=0,
            layer_type=0,
            child_level=0,
            flags=1  # Visible flag
        )
        assert layer.is_visible() is True

        layer.visible = False
        assert layer.is_visible() is False


class TestAsepriteCel:
    """Tests for AsepriteCel."""

    def test_cel_attributes(self):
        """Test cel attribute access."""
        cel = AsepriteCel(
            layer_index=0,
            x=10,
            y=20,
            opacity=200,
            cel_type=0,
            width=8,
            height=8
        )

        assert cel.layer_index == 0
        assert cel.x == 10
        assert cel.y == 20
        assert cel.opacity == 200


class TestAsepriteTag:
    """Tests for AsepriteTag."""

    def test_tag_attributes(self):
        """Test tag attribute access."""
        tag = AsepriteTag(
            name="Walk",
            from_frame=0,
            to_frame=7,
            direction=0,  # Forward
            repeat=0,
            color=(255, 200, 100, 255)
        )

        assert tag.name == "Walk"
        assert tag.from_frame == 0
        assert tag.to_frame == 7


class TestColorDepths:
    """Tests for different color depths."""

    def test_rgba_depth(self):
        """Test RGBA color depth."""
        data = create_minimal_aseprite(color_depth=32)
        ase = load_aseprite_from_bytes(data)
        assert ase.color_depth == 32

    def test_grayscale_depth(self):
        """Test grayscale color depth."""
        data = create_minimal_aseprite(color_depth=16)
        ase = load_aseprite_from_bytes(data)
        assert ase.color_depth == 16

    def test_indexed_depth(self):
        """Test indexed color depth."""
        data = create_minimal_aseprite(color_depth=8)
        ase = load_aseprite_from_bytes(data)
        assert ase.color_depth == 8


class TestEdgeCases:
    """Tests for edge cases."""

    def test_empty_layer_name(self):
        """Test handling empty layer name."""
        data = create_aseprite_with_layer()
        # This test just verifies no crash occurs
        ase = load_aseprite_from_bytes(data)
        assert ase is not None

    def test_get_nonexistent_layer(self):
        """Test getting frames for non-existent layer."""
        data = create_aseprite_with_layer()
        ase = load_aseprite_from_bytes(data)

        frames = ase.get_layer("NonExistent")
        assert frames == []

    def test_get_nonexistent_tag(self):
        """Test getting animation for non-existent tag."""
        data = create_minimal_aseprite()
        ase = load_aseprite_from_bytes(data)

        frames = ase.get_animation("NonExistent")
        assert frames == []

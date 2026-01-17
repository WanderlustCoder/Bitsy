"""
Animation Export Formats - Export animations for game engines.

Provides:
- Aseprite format export
- Spine JSON export
- Custom format with animation events
- Animation preview data
"""

from typing import List, Tuple, Optional, Dict, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import struct
import zlib

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Canvas
from animation.cycles import AnimationCycle, FrameData


class AnimationEventType(Enum):
    """Types of animation events."""
    TRIGGER = "trigger"      # Simple trigger (e.g., "hit")
    SOUND = "sound"          # Play sound
    SPAWN = "spawn"          # Spawn particle/effect
    HITBOX = "hitbox"        # Enable/disable hitbox
    CUSTOM = "custom"        # Custom event


@dataclass
class AnimationEvent:
    """An event triggered at a specific frame."""
    frame: int
    event_type: AnimationEventType
    name: str
    data: Optional[Dict[str, Any]] = None


@dataclass
class AnimationExport:
    """Complete animation export data."""
    name: str
    frames: List[Canvas]
    fps: int = 12
    loop: bool = True
    events: List[AnimationEvent] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)


# =============================================================================
# Aseprite Format Export
# =============================================================================

def export_aseprite(
    animation: AnimationExport,
    path: str,
    palette: Optional[List[Tuple[int, int, int, int]]] = None
) -> str:
    """Export animation as Aseprite file (.ase/.aseprite).

    Args:
        animation: Animation to export
        path: Output file path
        palette: Optional palette (extracts from frames if None)

    Returns:
        Path to saved file
    """
    if not animation.frames:
        raise ValueError("Animation has no frames")

    # Extract palette if not provided
    if palette is None:
        palette = _extract_palette(animation.frames)

    width = animation.frames[0].width
    height = animation.frames[0].height

    # Build Aseprite file structure
    ase_data = _build_aseprite_data(animation, palette, width, height)

    # Write file
    if not path.endswith(('.ase', '.aseprite')):
        path += '.aseprite'

    with open(path, 'wb') as f:
        f.write(ase_data)

    return path


def _extract_palette(frames: List[Canvas]) -> List[Tuple[int, int, int, int]]:
    """Extract unique colors from frames."""
    colors = set()
    for frame in frames:
        for y in range(frame.height):
            for x in range(frame.width):
                pixel = frame.get_pixel(x, y)
                if pixel and pixel[3] > 0:
                    colors.add(pixel)

    # Sort by luminance for consistent ordering
    palette = sorted(colors, key=lambda c: c[0] * 0.299 + c[1] * 0.587 + c[2] * 0.114)
    return palette[:256]  # Max 256 colors


def _build_aseprite_data(
    animation: AnimationExport,
    palette: List[Tuple[int, int, int, int]],
    width: int,
    height: int
) -> bytes:
    """Build Aseprite file binary data."""
    # Simplified ASE format - just the header and frames
    # Full ASE format is complex, this creates a basic valid file

    chunks = []

    # Palette chunk (0x2019)
    palette_data = _build_palette_chunk(palette)
    chunks.append(palette_data)

    # Frame chunks
    for i, frame in enumerate(animation.frames):
        cel_data = _build_cel_chunk(frame, palette, i)
        chunks.append(cel_data)

    # Calculate total size
    frame_data = b''.join(chunks)

    # Build header
    header = bytearray(128)

    # File size (updated later)
    # Magic number
    struct.pack_into('<H', header, 4, 0xA5E0)
    # Frames
    struct.pack_into('<H', header, 6, len(animation.frames))
    # Width/height
    struct.pack_into('<H', header, 8, width)
    struct.pack_into('<H', header, 10, height)
    # Color depth (32-bit RGBA)
    struct.pack_into('<H', header, 12, 32)
    # Flags
    struct.pack_into('<I', header, 14, 1)  # Has opacity
    # Speed (ms per frame)
    struct.pack_into('<H', header, 18, 1000 // animation.fps)
    # Palette entry count
    struct.pack_into('<B', header, 34, len(palette) if len(palette) < 256 else 0)

    # Combine header + frame data
    file_data = bytes(header) + frame_data

    # Update file size
    file_data = struct.pack('<I', len(file_data)) + file_data[4:]

    return file_data


def _build_palette_chunk(palette: List[Tuple[int, int, int, int]]) -> bytes:
    """Build palette chunk for Aseprite."""
    data = bytearray()

    # Chunk header
    chunk_type = 0x2019  # New palette chunk
    entries = len(palette)

    # Palette data
    palette_bytes = bytearray()
    palette_bytes.extend(struct.pack('<I', entries))  # Entry count
    palette_bytes.extend(struct.pack('<I', 0))  # First color index
    palette_bytes.extend(struct.pack('<I', entries - 1))  # Last color index

    for r, g, b, a in palette:
        palette_bytes.extend([r, g, b, a])

    # Chunk size
    chunk_size = len(palette_bytes) + 6  # +6 for chunk header
    data.extend(struct.pack('<I', chunk_size))
    data.extend(struct.pack('<H', chunk_type))
    data.extend(palette_bytes)

    return bytes(data)


def _build_cel_chunk(
    frame: Canvas,
    palette: List[Tuple[int, int, int, int]],
    layer_index: int
) -> bytes:
    """Build cel chunk for a frame."""
    data = bytearray()

    chunk_type = 0x2005  # Cel chunk

    # Cel data
    cel_bytes = bytearray()
    cel_bytes.extend(struct.pack('<H', layer_index))  # Layer index
    cel_bytes.extend(struct.pack('<h', 0))  # X position
    cel_bytes.extend(struct.pack('<h', 0))  # Y position
    cel_bytes.extend([255])  # Opacity

    # Cel type: 2 = compressed image
    cel_bytes.extend(struct.pack('<H', 2))
    cel_bytes.extend(struct.pack('<H', frame.width))
    cel_bytes.extend(struct.pack('<H', frame.height))

    # Pixel data (RGBA)
    pixels = bytearray()
    for y in range(frame.height):
        for x in range(frame.width):
            pixel = frame.get_pixel(x, y)
            if pixel:
                pixels.extend(pixel)
            else:
                pixels.extend([0, 0, 0, 0])

    # Compress pixel data
    compressed = zlib.compress(bytes(pixels))
    cel_bytes.extend(compressed)

    # Chunk size
    chunk_size = len(cel_bytes) + 6
    data.extend(struct.pack('<I', chunk_size))
    data.extend(struct.pack('<H', chunk_type))
    data.extend(cel_bytes)

    return bytes(data)


# =============================================================================
# Spine JSON Export
# =============================================================================

def export_spine_json(
    animation: AnimationExport,
    path: str,
    skeleton_name: str = "character"
) -> str:
    """Export animation as Spine JSON format.

    Args:
        animation: Animation to export
        path: Output file path
        skeleton_name: Name for the skeleton

    Returns:
        Path to saved file
    """
    if not animation.frames:
        raise ValueError("Animation has no frames")

    width = animation.frames[0].width
    height = animation.frames[0].height

    spine_data = {
        "skeleton": {
            "hash": f"{hash(animation.name) % 0xFFFFFFFF:08x}",
            "spine": "4.0",
            "width": width,
            "height": height,
            "images": "./images/"
        },
        "bones": [
            {"name": "root"}
        ],
        "slots": [
            {
                "name": "main",
                "bone": "root",
                "attachment": f"{animation.name}_0"
            }
        ],
        "skins": {
            "default": {
                "main": {}
            }
        },
        "animations": {}
    }

    # Add attachments for each frame
    for i, frame in enumerate(animation.frames):
        attachment_name = f"{animation.name}_{i}"
        spine_data["skins"]["default"]["main"][attachment_name] = {
            "x": width // 2,
            "y": height // 2,
            "width": width,
            "height": height
        }

    # Build animation timeline
    frame_duration = 1.0 / animation.fps
    timeline = []

    for i in range(len(animation.frames)):
        timeline.append({
            "time": i * frame_duration,
            "name": f"{animation.name}_{i}"
        })

    spine_data["animations"][animation.name] = {
        "slots": {
            "main": {
                "attachment": timeline
            }
        }
    }

    # Add events if present
    if animation.events:
        event_timeline = []
        for event in animation.events:
            event_data = {
                "time": event.frame * frame_duration,
                "name": event.name
            }
            if event.data:
                event_data.update(event.data)
            event_timeline.append(event_data)

        spine_data["animations"][animation.name]["events"] = event_timeline

        # Define events
        spine_data["events"] = {}
        for event in animation.events:
            spine_data["events"][event.name] = {}

    # Write file
    if not path.endswith('.json'):
        path += '.json'

    with open(path, 'w') as f:
        json.dump(spine_data, f, indent=2)

    return path


# =============================================================================
# Custom Format with Events
# =============================================================================

def export_bitsy_animation(
    animation: AnimationExport,
    path: str,
    include_frames: bool = False
) -> str:
    """Export animation in Bitsy's custom format with events.

    Args:
        animation: Animation to export
        path: Output file path
        include_frames: Include frame data in JSON

    Returns:
        Path to saved file
    """
    width = animation.frames[0].width if animation.frames else 0
    height = animation.frames[0].height if animation.frames else 0

    data = {
        "format": "bitsy-animation",
        "version": "1.0",
        "name": animation.name,
        "frameCount": len(animation.frames),
        "fps": animation.fps,
        "loop": animation.loop,
        "width": width,
        "height": height,
        "tags": animation.tags,
        "events": [],
        "frames": []
    }

    # Add events
    for event in animation.events:
        event_data = {
            "frame": event.frame,
            "type": event.event_type.value,
            "name": event.name
        }
        if event.data:
            event_data["data"] = event.data
        data["events"].append(event_data)

    # Add frame references or data
    for i, frame in enumerate(animation.frames):
        frame_info = {
            "index": i,
            "image": f"{animation.name}_{i}.png"
        }
        if include_frames:
            # Include pixel data as base64 or raw
            pixels = []
            for y in range(frame.height):
                row = []
                for x in range(frame.width):
                    pixel = frame.get_pixel(x, y)
                    row.append(list(pixel) if pixel else [0, 0, 0, 0])
                pixels.append(row)
            frame_info["pixels"] = pixels

        data["frames"].append(frame_info)

    if not path.endswith('.json'):
        path += '.json'

    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

    return path


# =============================================================================
# Conversion Functions
# =============================================================================

def cycle_to_export(
    cycle: AnimationCycle,
    events: Optional[List[AnimationEvent]] = None
) -> AnimationExport:
    """Convert AnimationCycle to AnimationExport.

    Args:
        cycle: Animation cycle to convert
        events: Optional events to attach

    Returns:
        AnimationExport ready for export
    """
    frames = []
    for frame_data in cycle.frames:
        if hasattr(frame_data, 'canvas'):
            frames.append(frame_data.canvas)
        elif hasattr(frame_data, 'sprite'):
            frames.append(frame_data.sprite)

    return AnimationExport(
        name=cycle.name,
        frames=frames,
        fps=cycle.fps,
        loop=cycle.loop,
        events=events or [],
        tags=[cycle.name.split('_')[0]] if '_' in cycle.name else []
    )


def export_animation_set(
    animations: Dict[str, AnimationExport],
    base_path: str,
    format: str = "json"
) -> List[str]:
    """Export multiple animations.

    Args:
        animations: Dict of name -> AnimationExport
        base_path: Base path for output
        format: Export format (json, spine, aseprite)

    Returns:
        List of saved file paths
    """
    saved = []

    for name, anim in animations.items():
        path = f"{base_path}_{name}"

        if format == "spine":
            saved.append(export_spine_json(anim, path, name))
        elif format == "aseprite":
            saved.append(export_aseprite(anim, path))
        else:
            saved.append(export_bitsy_animation(anim, path))

    return saved


def list_animation_formats() -> List[str]:
    """List available animation export formats."""
    return ["json", "spine", "aseprite", "bitsy"]

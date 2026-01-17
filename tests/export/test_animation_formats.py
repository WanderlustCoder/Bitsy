"""
Test Animation Formats - Tests for animation export formats.

Tests:
- AnimationExport defaults
- Aseprite export
- Spine JSON export
- Bitsy animation JSON export
- Available format listing
"""

import sys
import os
import json
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests.framework import TestCase, CanvasFixtures
from export.animation_formats import (
    AnimationExport,
    AnimationEvent,
    AnimationEventType,
    export_aseprite,
    export_spine_json,
    export_bitsy_animation,
    list_animation_formats,
)


class TestAnimationExport(TestCase):
    """Tests for AnimationExport dataclass."""

    def test_defaults(self):
        """AnimationExport has expected default values."""
        frames = [CanvasFixtures.solid((255, 0, 0, 255), width=8, height=8)]
        animation = AnimationExport(name="idle", frames=frames)

        self.assertEqual(animation.name, "idle")
        self.assertEqual(animation.frames, frames)
        self.assertEqual(animation.fps, 12)
        self.assertTrue(animation.loop)
        self.assertEqual(animation.events, [])
        self.assertEqual(animation.tags, [])


class TestExportAseprite(TestCase):
    """Tests for export_aseprite."""

    def test_export_aseprite_creates_file(self):
        """export_aseprite writes a file with Aseprite magic bytes."""
        frames = [
            CanvasFixtures.solid((255, 0, 0, 255), width=4, height=4),
            CanvasFixtures.solid((0, 255, 0, 255), width=4, height=4),
        ]
        animation = AnimationExport(name="run", frames=frames, fps=8)

        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = os.path.join(tmpdir, "run")
            filepath = export_aseprite(animation, base_path)

            self.assertTrue(filepath.endswith(".aseprite"))
            self.assertTrue(os.path.exists(filepath))

            with open(filepath, "rb") as f:
                header = f.read(6)

            self.assertEqual(header[4:6], b"\xe0\xa5")

    def test_export_aseprite_empty_raises(self):
        """export_aseprite raises for animations without frames."""
        animation = AnimationExport(name="empty", frames=[])
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = os.path.join(tmpdir, "empty")
            with self.assertRaises(ValueError):
                export_aseprite(animation, base_path)


class TestExportSpineJson(TestCase):
    """Tests for export_spine_json."""

    def test_export_spine_json_with_events(self):
        """export_spine_json writes expected structure and events."""
        frames = [
            CanvasFixtures.solid((255, 0, 0, 255), width=6, height=6),
            CanvasFixtures.solid((0, 0, 255, 255), width=6, height=6),
        ]
        events = [
            AnimationEvent(
                frame=1,
                event_type=AnimationEventType.TRIGGER,
                name="hit",
                data={"int": 5},
            )
        ]
        animation = AnimationExport(name="attack", frames=frames, fps=10, events=events)

        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = os.path.join(tmpdir, "attack")
            filepath = export_spine_json(animation, base_path, skeleton_name="hero")

            self.assertTrue(filepath.endswith(".json"))
            self.assertTrue(os.path.exists(filepath))

            with open(filepath, "r") as f:
                data = json.load(f)

            self.assertIn("skeleton", data)
            self.assertEqual(data["skeleton"]["width"], 6)
            self.assertEqual(data["skeleton"]["height"], 6)
            self.assertIn("animations", data)
            self.assertIn("attack", data["animations"])
            self.assertIn("events", data["animations"]["attack"])
            self.assertEqual(data["animations"]["attack"]["events"][0]["name"], "hit")
            self.assertEqual(data["animations"]["attack"]["events"][0]["int"], 5)
            self.assertIn("events", data)
            self.assertIn("hit", data["events"])

    def test_export_spine_json_empty_raises(self):
        """export_spine_json raises for animations without frames."""
        animation = AnimationExport(name="empty", frames=[])
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = os.path.join(tmpdir, "empty")
            with self.assertRaises(ValueError):
                export_spine_json(animation, base_path)


class TestExportBitsyAnimation(TestCase):
    """Tests for export_bitsy_animation."""

    def test_export_bitsy_animation_includes_events_and_frames(self):
        """export_bitsy_animation writes events and pixel data."""
        frames = [
            CanvasFixtures.solid((255, 255, 0, 255), width=3, height=3),
            CanvasFixtures.solid((0, 255, 255, 255), width=3, height=3),
        ]
        events = [
            AnimationEvent(
                frame=0,
                event_type=AnimationEventType.SOUND,
                name="whoosh",
                data={"volume": 0.5},
            )
        ]
        animation = AnimationExport(name="spin", frames=frames, fps=12, events=events, loop=False)

        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = os.path.join(tmpdir, "spin")
            filepath = export_bitsy_animation(animation, base_path, include_frames=True)

            self.assertTrue(filepath.endswith(".json"))
            self.assertTrue(os.path.exists(filepath))

            with open(filepath, "r") as f:
                data = json.load(f)

            self.assertEqual(data["format"], "bitsy-animation")
            self.assertEqual(data["frameCount"], 2)
            self.assertFalse(data["loop"])
            self.assertEqual(data["events"][0]["type"], "sound")
            self.assertIn("frames", data)
            self.assertIn("pixels", data["frames"][0])

    def test_export_bitsy_animation_without_frames_data(self):
        """export_bitsy_animation omits pixel data by default."""
        frames = [CanvasFixtures.solid((10, 20, 30, 255), width=2, height=2)]
        animation = AnimationExport(name="idle", frames=frames)

        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = os.path.join(tmpdir, "idle")
            filepath = export_bitsy_animation(animation, base_path)

            with open(filepath, "r") as f:
                data = json.load(f)

            self.assertIn("frames", data)
            self.assertNotIn("pixels", data["frames"][0])


class TestListAnimationFormats(TestCase):
    """Tests for list_animation_formats."""

    def test_list_animation_formats(self):
        """list_animation_formats returns expected formats."""
        formats = list_animation_formats()
        self.assertEqual(formats, ["json", "spine", "aseprite", "bitsy"])

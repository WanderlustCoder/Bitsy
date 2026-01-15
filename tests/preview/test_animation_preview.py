"""
Test Animation Preview - Tests for animation preview generation.

Tests:
- Frame strip creation
- HTML animation preview
- Animation preview options
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests.framework import TestCase
from core import Canvas
from preview.animation_preview import (
    create_frame_strip,
    generate_animation_preview,
    create_animation_html,
    AnimationPreviewOptions,
)


class TestCreateFrameStrip(TestCase):
    """Tests for frame strip creation."""

    def test_returns_canvas(self):
        """create_frame_strip returns Canvas."""
        frames = [Canvas(8, 8, (i * 50, 0, 0, 255)) for i in range(4)]
        result = create_frame_strip(frames)

        self.assertIsInstance(result, Canvas)

    def test_empty_frames(self):
        """Handles empty frame list."""
        result = create_frame_strip([])

        self.assertIsInstance(result, Canvas)

    def test_horizontal_layout(self):
        """Frames are arranged horizontally."""
        frames = [Canvas(10, 10, (i * 50, 0, 0, 255)) for i in range(4)]
        result = create_frame_strip(frames, padding=2)

        # Width should be: 4 frames * 10px + 3 gaps * 2px padding
        min_width = 4 * 10 + 3 * 2
        self.assertGreaterEqual(result.width, min_width)

    def test_max_height(self):
        """Strip height is max of all frames."""
        frames = [
            Canvas(8, 10, (255, 0, 0, 255)),
            Canvas(8, 16, (0, 255, 0, 255)),  # Tallest
            Canvas(8, 12, (0, 0, 255, 255)),
        ]
        result = create_frame_strip(frames)

        self.assertEqual(result.height, 16)

    def test_max_frames_limit(self):
        """max_frames parameter limits output."""
        frames = [Canvas(8, 8, (i * 10, 0, 0, 255)) for i in range(20)]

        result_limited = create_frame_strip(frames, max_frames=5)
        result_all = create_frame_strip(frames, max_frames=20)

        # Limited version should be narrower
        self.assertLess(result_limited.width, result_all.width)

    def test_padding_affects_width(self):
        """Padding affects total width."""
        frames = [Canvas(8, 8, (255, 0, 0, 255)) for _ in range(4)]

        small_pad = create_frame_strip(frames, padding=1)
        large_pad = create_frame_strip(frames, padding=10)

        self.assertLess(small_pad.width, large_pad.width)


class TestGenerateAnimationPreview(TestCase):
    """Tests for animation HTML preview generation."""

    def test_returns_html_string(self):
        """generate_animation_preview returns HTML string."""
        # Create simple animation object
        class SimpleAnim:
            def __init__(self):
                self.frames = [Canvas(8, 8, (i * 50, 0, 0, 255)) for i in range(4)]
                self.fps = 8

        animation = SimpleAnim()
        html = generate_animation_preview(animation)

        self.assertIsInstance(html, str)
        self.assertIn("<!DOCTYPE html>", html)

    def test_contains_frame_data(self):
        """HTML contains embedded frame data."""
        class SimpleAnim:
            def __init__(self):
                self.frames = [Canvas(8, 8, (255, 0, 0, 255)) for _ in range(2)]
                self.fps = 8

        animation = SimpleAnim()
        html = generate_animation_preview(animation)

        # Should contain data URIs
        self.assertIn("data:image/png;base64,", html)

    def test_contains_playback_controls(self):
        """HTML contains playback controls."""
        class SimpleAnim:
            def __init__(self):
                self.frames = [Canvas(8, 8, (255, 0, 0, 255)) for _ in range(4)]
                self.fps = 8

        animation = SimpleAnim()
        html = generate_animation_preview(animation)

        # Check for control elements
        self.assertIn("play-pause", html)
        self.assertIn("prev-frame", html)
        self.assertIn("next-frame", html)

    def test_contains_speed_controls(self):
        """HTML contains speed control buttons."""
        class SimpleAnim:
            def __init__(self):
                self.frames = [Canvas(8, 8, (255, 0, 0, 255)) for _ in range(4)]
                self.fps = 8

        animation = SimpleAnim()
        options = AnimationPreviewOptions(speeds=[0.5, 1.0, 2.0])
        html = generate_animation_preview(animation, options)

        self.assertIn("0.5x", html)
        self.assertIn("1.0x", html)
        self.assertIn("2.0x", html)

    def test_empty_animation(self):
        """Handles animation with no frames."""
        class EmptyAnim:
            def __init__(self):
                self.frames = []
                self.fps = 8

        animation = EmptyAnim()
        html = generate_animation_preview(animation)

        self.assertIsInstance(html, str)
        self.assertIn("No frames", html)


class TestCreateAnimationHtml(TestCase):
    """Tests for creating animation HTML from frames."""

    def test_returns_html(self):
        """create_animation_html returns HTML string."""
        frames = [Canvas(8, 8, (i * 50, 0, 0, 255)) for i in range(4)]
        html = create_animation_html(frames, fps=8)

        self.assertIsInstance(html, str)
        self.assertIn("<!DOCTYPE html>", html)

    def test_saves_to_file(self):
        """Saves HTML to file when path provided."""
        import tempfile

        frames = [Canvas(8, 8, (255, 0, 0, 255)) for _ in range(4)]

        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as f:
            output_path = f.name

        try:
            html = create_animation_html(frames, fps=8, output_path=output_path)

            self.assertTrue(os.path.exists(output_path))
            with open(output_path, 'r') as f:
                content = f.read()
            self.assertIn("<!DOCTYPE html>", content)
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)

    def test_respects_fps(self):
        """FPS value appears in output."""
        frames = [Canvas(8, 8, (255, 0, 0, 255)) for _ in range(4)]

        html_8fps = create_animation_html(frames, fps=8)
        html_24fps = create_animation_html(frames, fps=24)

        # Different FPS should result in different frame durations
        self.assertIn("8 FPS", html_8fps)
        self.assertIn("24 FPS", html_24fps)


class TestAnimationPreviewOptions(TestCase):
    """Tests for AnimationPreviewOptions dataclass."""

    def test_default_values(self):
        """Options have sensible defaults."""
        options = AnimationPreviewOptions()

        self.assertEqual(options.scales, [1, 2, 4])
        self.assertEqual(options.speeds, [0.5, 1.0, 2.0])
        self.assertTrue(options.show_frame_strip)
        self.assertTrue(options.dark_background)
        self.assertTrue(options.loop)

    def test_custom_values(self):
        """Custom values are accepted."""
        options = AnimationPreviewOptions(
            scales=[1, 8],
            speeds=[1.0],
            show_frame_strip=False,
            dark_background=False,
            title="Custom Animation",
            loop=False
        )

        self.assertEqual(options.scales, [1, 8])
        self.assertEqual(options.speeds, [1.0])
        self.assertFalse(options.show_frame_strip)
        self.assertFalse(options.dark_background)
        self.assertEqual(options.title, "Custom Animation")
        self.assertFalse(options.loop)

    def test_frame_strip_option(self):
        """show_frame_strip option affects output."""
        class SimpleAnim:
            def __init__(self):
                self.frames = [Canvas(8, 8, (255, 0, 0, 255)) for _ in range(4)]
                self.fps = 8

        animation = SimpleAnim()

        with_strip = generate_animation_preview(
            animation, AnimationPreviewOptions(show_frame_strip=True))
        without_strip = generate_animation_preview(
            animation, AnimationPreviewOptions(show_frame_strip=False))

        # With strip should have more occurrences (CSS + actual div)
        # Without strip only has CSS definitions
        with_count = with_strip.count("frame-strip-container")
        without_count = without_strip.count("frame-strip-container")
        self.assertGreater(with_count, without_count)

    def test_dark_background_option(self):
        """dark_background option affects output."""
        class SimpleAnim:
            def __init__(self):
                self.frames = [Canvas(8, 8, (255, 0, 0, 255)) for _ in range(4)]
                self.fps = 8

        animation = SimpleAnim()

        dark = generate_animation_preview(
            animation, AnimationPreviewOptions(dark_background=True))
        light = generate_animation_preview(
            animation, AnimationPreviewOptions(dark_background=False))

        self.assertIn('class="dark"', dark)
        self.assertIn('class="light"', light)

"""
Test GIF Export - Tests for animated GIF generation.

Tests:
- GIF file creation
- Animation frame handling
- Palette quantization
- LZW compression
"""

import sys
import os
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests.framework import TestCase, CanvasFixtures
from export import save_gif, GIFExporter
from core import Canvas


class TestSaveGif(TestCase):
    """Tests for save_gif function."""

    def test_save_gif_creates_file(self):
        """save_gif creates a GIF file."""
        frames = [
            Canvas(8, 8, (255, 0, 0, 255)),
            Canvas(8, 8, (0, 255, 0, 255)),
        ]

        with tempfile.NamedTemporaryFile(suffix='.gif', delete=False) as f:
            filepath = f.name

        try:
            save_gif(filepath, frames)
            self.assertTrue(os.path.exists(filepath))
            self.assertGreater(os.path.getsize(filepath), 0)
        finally:
            if os.path.exists(filepath):
                os.unlink(filepath)

    def test_save_gif_magic_bytes(self):
        """save_gif creates valid GIF header."""
        frames = [Canvas(4, 4, (255, 0, 0, 255))]

        with tempfile.NamedTemporaryFile(suffix='.gif', delete=False) as f:
            filepath = f.name

        try:
            save_gif(filepath, frames)

            with open(filepath, 'rb') as f:
                header = f.read(6)

            self.assertEqual(header, b'GIF89a')
        finally:
            if os.path.exists(filepath):
                os.unlink(filepath)

    def test_save_gif_with_delays(self):
        """save_gif accepts frame delays."""
        frames = [
            Canvas(4, 4, (255, 0, 0, 255)),
            Canvas(4, 4, (0, 255, 0, 255)),
            Canvas(4, 4, (0, 0, 255, 255)),
        ]
        delays = [10, 20, 30]

        with tempfile.NamedTemporaryFile(suffix='.gif', delete=False) as f:
            filepath = f.name

        try:
            save_gif(filepath, frames, delays=delays)
            self.assertTrue(os.path.exists(filepath))
        finally:
            if os.path.exists(filepath):
                os.unlink(filepath)

    def test_save_gif_transparency(self):
        """save_gif handles transparent pixels."""
        # Frame with some transparent pixels
        frame = Canvas(8, 8)
        frame.fill_rect(2, 2, 4, 4, (255, 0, 0, 255))
        frames = [frame]

        with tempfile.NamedTemporaryFile(suffix='.gif', delete=False) as f:
            filepath = f.name

        try:
            save_gif(filepath, frames)
            self.assertTrue(os.path.exists(filepath))
        finally:
            if os.path.exists(filepath):
                os.unlink(filepath)

    def test_save_gif_empty_raises(self):
        """save_gif raises for empty frame list."""
        with tempfile.NamedTemporaryFile(suffix='.gif', delete=False) as f:
            filepath = f.name

        try:
            with self.assertRaises(ValueError):
                save_gif(filepath, [])
        finally:
            if os.path.exists(filepath):
                os.unlink(filepath)


class TestGifExporter(TestCase):
    """Tests for GIFExporter class."""

    def test_gif_exporter_basic(self):
        """GIFExporter can be instantiated."""
        exporter = GIFExporter()
        self.assertIsNotNone(exporter)

    def test_gif_exporter_with_options(self):
        """GIFExporter accepts configuration options."""
        exporter = GIFExporter(dither=True, max_colors=16)
        self.assertTrue(exporter.dither)
        self.assertEqual(exporter.max_colors, 16)

    def test_gif_exporter_export(self):
        """GIFExporter.export creates GIF file."""
        exporter = GIFExporter()
        frames = [Canvas(4, 4, (255, 0, 0, 255))]

        with tempfile.NamedTemporaryFile(suffix='.gif', delete=False) as f:
            filepath = f.name

        try:
            exporter.export(filepath, frames)
            self.assertTrue(os.path.exists(filepath))
        finally:
            if os.path.exists(filepath):
                os.unlink(filepath)


class TestGifColorHandling(TestCase):
    """Tests for GIF color quantization."""

    def test_handles_many_colors(self):
        """GIF export handles images with many colors."""
        # Create gradient with many colors
        frame = CanvasFixtures.gradient_h(
            (0, 0, 0, 255), (255, 255, 255, 255),
            width=64, height=64
        )

        with tempfile.NamedTemporaryFile(suffix='.gif', delete=False) as f:
            filepath = f.name

        try:
            save_gif(filepath, [frame])
            self.assertTrue(os.path.exists(filepath))
        finally:
            if os.path.exists(filepath):
                os.unlink(filepath)

    def test_handles_256_color_limit(self):
        """GIF export respects 256 color limit."""
        # Create canvas with exactly 256 distinct colors
        frame = Canvas(16, 16)
        for y in range(16):
            for x in range(16):
                val = y * 16 + x
                frame.set_pixel_solid(x, y, (val, val, val, 255))

        with tempfile.NamedTemporaryFile(suffix='.gif', delete=False) as f:
            filepath = f.name

        try:
            save_gif(filepath, [frame])
            self.assertTrue(os.path.exists(filepath))
        finally:
            if os.path.exists(filepath):
                os.unlink(filepath)

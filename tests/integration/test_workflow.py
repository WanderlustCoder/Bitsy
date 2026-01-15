"""
Test Workflow - Integration tests for complete workflows.

Tests:
- Generate -> Edit -> Export pipeline
- Multiple module interactions
- End-to-end scenarios
"""

import sys
import os
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests.framework import TestCase
from core import Canvas, Palette
from generators import generate_item, ItemPalette
from ui import create_icon
from editor import adjust_brightness, outline, grayscale
from export import create_grid_sheet, save_gif, pack_sprites


class TestGenerateEditExportWorkflow(TestCase):
    """Tests for generation -> editing -> export workflow."""

    def test_generate_and_edit_item(self):
        """Generate item, apply effects, verify output."""
        # Generate
        sword = generate_item('sword', width=16, height=24)
        self.assertCanvasNotEmpty(sword)

        # Edit
        bright_sword = adjust_brightness(sword, 0.3)
        outlined_sword = outline(bright_sword, (0, 0, 0, 255))

        # Verify
        self.assertCanvasNotEmpty(outlined_sword)
        self.assertEqual(outlined_sword.width, 16)

    def test_create_icon_sheet(self):
        """Create multiple icons and pack into sheet."""
        icons = []
        for name in ['heart', 'star', 'gear', 'checkmark']:
            icon = create_icon(name, size=16)
            icons.append(icon)

        # Create sheet
        sheet = create_grid_sheet(icons, columns=2)

        self.assertEqual(sheet.width, 32)  # 2 * 16
        self.assertEqual(sheet.height, 32)  # 2 * 16

    def test_generate_item_variations(self):
        """Generate multiple item variations with different palettes."""
        palettes = [
            ItemPalette.iron(),
            ItemPalette.gold(),
            ItemPalette.wood(),
        ]

        items = []
        for palette in palettes:
            item = generate_item('sword', palette=palette)
            items.append(('sword', item))

        # Pack into atlas
        atlas, packed = pack_sprites(items)

        self.assertEqual(len(packed), 3)
        self.assertCanvasNotEmpty(atlas)


class TestAnimationWorkflow(TestCase):
    """Tests for animation generation workflow."""

    def test_create_animation_frames(self):
        """Create animation frames and export as GIF."""
        # Generate base
        base = generate_item('sword', width=16, height=24)

        # Create brightness variations for glow effect
        frames = []
        for brightness in [0, 0.1, 0.2, 0.1, 0, -0.1, -0.2, -0.1]:
            frame = adjust_brightness(base, brightness)
            frames.append(frame)

        # Export GIF
        with tempfile.NamedTemporaryFile(suffix='.gif', delete=False) as f:
            filepath = f.name

        try:
            save_gif(filepath, frames, delays=[10] * len(frames))
            self.assertTrue(os.path.exists(filepath))
            self.assertGreater(os.path.getsize(filepath), 100)
        finally:
            if os.path.exists(filepath):
                os.unlink(filepath)


class TestDeterminismAcrossModules(TestCase):
    """Tests that determinism is preserved across modules."""

    def test_same_seed_same_results(self):
        """Same seed produces identical results across runs."""
        result1 = generate_item('axe', seed=12345, width=16, height=16)
        result2 = generate_item('axe', seed=12345, width=16, height=16)

        self.assertCanvasEqual(result1, result2)

    def test_edit_operations_deterministic(self):
        """Edit operations produce consistent results."""
        base = generate_item('sword', seed=42)

        edit1 = outline(adjust_brightness(base, 0.2), (0, 0, 0, 255))
        edit2 = outline(adjust_brightness(base, 0.2), (0, 0, 0, 255))

        self.assertCanvasEqual(edit1, edit2)


class TestPNGRoundtrip(TestCase):
    """Tests for PNG save/load roundtrip."""

    def test_canvas_png_roundtrip(self):
        """Canvas survives PNG save/load cycle."""
        from editor import load_png

        original = generate_item('potion_health', width=12, height=16)

        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            filepath = f.name

        try:
            # Save
            original.save(filepath)

            # Load
            loaded = load_png(filepath)

            # Compare
            self.assertCanvasEqual(original, loaded)
        finally:
            if os.path.exists(filepath):
                os.unlink(filepath)

    def test_transparency_preserved(self):
        """Transparency is preserved through PNG roundtrip."""
        from editor import load_png

        # Canvas with transparent background
        canvas = Canvas(8, 8)
        canvas.fill_circle(4, 4, 3, (255, 0, 0, 255))

        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            filepath = f.name

        try:
            canvas.save(filepath)
            loaded = load_png(filepath)

            # Check transparent corner
            self.assertPixelColor(loaded, 0, 0, (0, 0, 0, 0))
            # Check opaque center
            center = loaded.pixels[4][4]
            self.assertEqual(center[3], 255)
        finally:
            if os.path.exists(filepath):
                os.unlink(filepath)


class TestEdgeCases(TestCase):
    """Tests for edge cases in module integration."""

    def test_1x1_canvas_through_pipeline(self):
        """1x1 canvas survives full pipeline."""
        canvas = Canvas(1, 1, (255, 0, 0, 255))
        bright = adjust_brightness(canvas, 0.5)
        gray = grayscale(bright)

        self.assertEqual(gray.width, 1)
        self.assertEqual(gray.height, 1)

    def test_large_canvas_operations(self):
        """Large canvases work correctly."""
        canvas = Canvas(256, 256, (100, 100, 100, 255))
        result = adjust_brightness(canvas, 0.2)

        self.assertEqual(result.width, 256)
        self.assertCanvasNotEmpty(result)

    def test_empty_operations_safe(self):
        """Empty/transparent canvases handled safely."""
        empty = Canvas(16, 16)  # All transparent
        outlined = outline(empty, (255, 0, 0, 255))

        # Should not crash, result should also be empty
        # (no pixels to outline)

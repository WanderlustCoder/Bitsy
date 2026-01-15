"""
Test Spritesheet - Tests for sprite sheet and atlas generation.

Tests:
- Grid sheet creation
- Bin packing
- Atlas metadata
- Sheet splitting
"""

import sys
import os
import tempfile
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests.framework import TestCase, CanvasFixtures
from export import (
    create_grid_sheet, create_animation_sheet, pack_sprites,
    SpriteAtlas, export_atlas_json, load_atlas_json,
    split_sheet, BinPacker, Rect
)
from core import Canvas


class TestGridSheet(TestCase):
    """Tests for grid-based sprite sheet creation."""

    def test_create_grid_sheet_basic(self):
        """create_grid_sheet creates correct dimensions."""
        sprites = [
            Canvas(8, 8, (255, 0, 0, 255)),
            Canvas(8, 8, (0, 255, 0, 255)),
            Canvas(8, 8, (0, 0, 255, 255)),
            Canvas(8, 8, (255, 255, 0, 255)),
        ]

        result = create_grid_sheet(sprites, columns=2, padding=0)

        self.assertEqual(result.width, 16)  # 2 columns * 8
        self.assertEqual(result.height, 16)  # 2 rows * 8

    def test_create_grid_sheet_with_padding(self):
        """create_grid_sheet respects padding."""
        sprites = [
            Canvas(8, 8, (255, 0, 0, 255)),
            Canvas(8, 8, (0, 255, 0, 255)),
        ]

        result = create_grid_sheet(sprites, columns=2, padding=2)

        # (8 + 2*2) * 2 = 24
        self.assertEqual(result.width, 24)

    def test_create_grid_sheet_centers_smaller_sprites(self):
        """create_grid_sheet centers sprites of different sizes."""
        sprites = [
            Canvas(8, 8, (255, 0, 0, 255)),
            Canvas(4, 4, (0, 255, 0, 255)),  # Smaller
        ]

        result = create_grid_sheet(sprites, columns=2, padding=0)

        # Both cells should be 8x8 (max size)
        self.assertEqual(result.width, 16)

    def test_create_grid_sheet_empty(self):
        """create_grid_sheet handles empty list."""
        result = create_grid_sheet([], columns=4)
        self.assertEqual(result.width, 1)
        self.assertEqual(result.height, 1)


class TestAnimationSheet(TestCase):
    """Tests for animation sprite sheet creation."""

    def test_create_animation_sheet_basic(self):
        """create_animation_sheet creates sheet with metadata."""
        animations = {
            'idle': [Canvas(8, 8, (255, 0, 0, 255)) for _ in range(4)],
            'walk': [Canvas(8, 8, (0, 255, 0, 255)) for _ in range(6)],
        }

        sheet, metadata = create_animation_sheet(animations, columns=4)

        self.assertIsInstance(sheet, Canvas)
        self.assertIn('animations', metadata)
        self.assertIn('idle', metadata['animations'])
        self.assertIn('walk', metadata['animations'])

    def test_create_animation_sheet_metadata_correct(self):
        """create_animation_sheet metadata has correct frame counts."""
        animations = {
            'run': [Canvas(8, 8) for _ in range(3)],
        }

        sheet, metadata = create_animation_sheet(animations, columns=4)

        self.assertEqual(metadata['animations']['run']['frame_count'], 3)


class TestBinPacker(TestCase):
    """Tests for bin packing algorithm."""

    def test_bin_packer_single_item(self):
        """BinPacker packs single item."""
        packer = BinPacker(64, 64)
        rect = packer.insert(16, 16)

        self.assertIsNotNone(rect)
        self.assertEqual(rect.x, 0)
        self.assertEqual(rect.y, 0)
        self.assertEqual(rect.width, 16)
        self.assertEqual(rect.height, 16)

    def test_bin_packer_multiple_items(self):
        """BinPacker packs multiple items."""
        packer = BinPacker(64, 64)

        rects = []
        for i in range(4):
            rect = packer.insert(16, 16)
            self.assertIsNotNone(rect)
            rects.append(rect)

        # Check no overlaps
        for i, r1 in enumerate(rects):
            for j, r2 in enumerate(rects):
                if i < j:
                    overlap = (
                        r1.x < r2.x + r2.width and
                        r1.x + r1.width > r2.x and
                        r1.y < r2.y + r2.height and
                        r1.y + r1.height > r2.y
                    )
                    self.assertFalse(overlap, f"Rects {i} and {j} overlap")

    def test_bin_packer_overflow(self):
        """BinPacker returns None when full."""
        packer = BinPacker(16, 16)
        rect1 = packer.insert(16, 16)  # Fill it
        rect2 = packer.insert(8, 8)  # Should fail

        self.assertIsNotNone(rect1)
        self.assertIsNone(rect2)

    def test_bin_packer_with_padding(self):
        """BinPacker respects padding."""
        packer = BinPacker(32, 32, padding=2)
        rect1 = packer.insert(10, 10)
        rect2 = packer.insert(10, 10)

        self.assertIsNotNone(rect1)
        self.assertIsNotNone(rect2)

        # With padding, they shouldn't touch
        min_distance = 2
        h_gap = abs(rect2.x - (rect1.x + rect1.width))
        v_gap = abs(rect2.y - (rect1.y + rect1.height))

        # At least one gap should exist
        self.assertTrue(h_gap >= min_distance or v_gap >= min_distance)


class TestPackSprites(TestCase):
    """Tests for pack_sprites function."""

    def test_pack_sprites_basic(self):
        """pack_sprites creates atlas and packed list."""
        sprites = [
            ('red', Canvas(8, 8, (255, 0, 0, 255))),
            ('green', Canvas(8, 8, (0, 255, 0, 255))),
            ('blue', Canvas(8, 8, (0, 0, 255, 255))),
        ]

        atlas, packed = pack_sprites(sprites)

        self.assertIsInstance(atlas, Canvas)
        self.assertEqual(len(packed), 3)

    def test_pack_sprites_assigns_positions(self):
        """pack_sprites assigns valid positions to sprites."""
        sprites = [
            ('s1', Canvas(8, 8, (255, 0, 0, 255))),
            ('s2', Canvas(8, 8, (0, 255, 0, 255))),
        ]

        atlas, packed = pack_sprites(sprites)

        for p in packed:
            self.assertGreaterEqual(p.x, 0)
            self.assertGreaterEqual(p.y, 0)
            self.assertLess(p.x + p.width, atlas.width + 1)
            self.assertLess(p.y + p.height, atlas.height + 1)


class TestSpriteAtlas(TestCase):
    """Tests for SpriteAtlas class."""

    def test_sprite_atlas_add(self):
        """SpriteAtlas.add adds sprite."""
        atlas = SpriteAtlas()
        atlas.add('test', Canvas(8, 8, (255, 0, 0, 255)))

        self.assertEqual(len(atlas.sprites), 1)

    def test_sprite_atlas_add_multiple(self):
        """SpriteAtlas.add_multiple adds dict of sprites."""
        atlas = SpriteAtlas()
        sprites = {
            'red': Canvas(8, 8, (255, 0, 0, 255)),
            'green': Canvas(8, 8, (0, 255, 0, 255)),
        }
        atlas.add_multiple(sprites)

        self.assertEqual(len(atlas.sprites), 2)

    def test_sprite_atlas_build(self):
        """SpriteAtlas.build creates atlas."""
        atlas = SpriteAtlas()
        atlas.add('test', Canvas(8, 8, (255, 0, 0, 255)))

        result, packed = atlas.build()

        self.assertIsInstance(result, Canvas)
        self.assertEqual(len(packed), 1)

    def test_sprite_atlas_clear(self):
        """SpriteAtlas.clear removes all sprites."""
        atlas = SpriteAtlas()
        atlas.add('test', Canvas(8, 8))
        atlas.clear()

        self.assertEqual(len(atlas.sprites), 0)


class TestAtlasJson(TestCase):
    """Tests for atlas JSON export/import."""

    def test_export_atlas_json(self):
        """export_atlas_json creates valid JSON file."""
        from export.spritesheet import PackedSprite

        packed = [
            PackedSprite(name='sprite1', canvas=Canvas(8, 8), x=0, y=0),
            PackedSprite(name='sprite2', canvas=Canvas(8, 8), x=8, y=0),
        ]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            filepath = f.name

        try:
            export_atlas_json(packed, 64, 64, filepath)

            with open(filepath, 'r') as f:
                data = json.load(f)

            self.assertIn('atlas', data)
            self.assertIn('sprites', data)
            self.assertEqual(data['atlas']['width'], 64)
            self.assertEqual(len(data['sprites']), 2)
        finally:
            os.unlink(filepath)

    def test_load_atlas_json(self):
        """load_atlas_json reads JSON file."""
        data = {
            'atlas': {'width': 32, 'height': 32},
            'sprites': {'test': {'x': 0, 'y': 0, 'width': 8, 'height': 8}}
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(data, f)
            filepath = f.name

        try:
            result = load_atlas_json(filepath)
            self.assertEqual(result['atlas']['width'], 32)
            self.assertIn('test', result['sprites'])
        finally:
            os.unlink(filepath)


class TestSplitSheet(TestCase):
    """Tests for split_sheet function."""

    def test_split_sheet_basic(self):
        """split_sheet splits sheet into frames."""
        # Create 4x4 grid of 8x8 sprites
        sheet = Canvas(32, 32, (255, 0, 0, 255))

        frames = split_sheet(sheet, 8, 8)

        self.assertEqual(len(frames), 16)  # 4x4
        for frame in frames:
            self.assertEqual(frame.width, 8)
            self.assertEqual(frame.height, 8)

    def test_split_sheet_with_count(self):
        """split_sheet respects count parameter."""
        sheet = Canvas(32, 8)  # 4 frames in a row

        frames = split_sheet(sheet, 8, 8, count=3)

        self.assertEqual(len(frames), 3)

    def test_split_sheet_roundtrip(self):
        """split_sheet reverses create_grid_sheet."""
        original_sprites = [
            Canvas(8, 8, (255, 0, 0, 255)),
            Canvas(8, 8, (0, 255, 0, 255)),
            Canvas(8, 8, (0, 0, 255, 255)),
            Canvas(8, 8, (255, 255, 0, 255)),
        ]

        sheet = create_grid_sheet(original_sprites, columns=2, padding=0)
        recovered = split_sheet(sheet, 8, 8, count=4)

        self.assertEqual(len(recovered), 4)
        # First frame should be red
        self.assertPixelColor(recovered[0], 0, 0, (255, 0, 0, 255))

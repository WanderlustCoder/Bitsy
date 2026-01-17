"""
Test Atlas Export - Tests for export/atlas.py.

Tests:
- SpriteAtlas packing and trimming
- create_atlas convenience function
- pack_animations naming
- Export metadata formats
"""

import sys
import os
import json
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests.framework import TestCase
from export.atlas import (
    SpriteAtlas,
    PackingAlgorithm,
    AtlasFormat,
    create_atlas,
    pack_animations,
)
from core import Canvas


class TestSpriteAtlas(TestCase):
    """Tests for SpriteAtlas packing and metadata."""

    def test_add_sprite_and_lookup(self):
        """SpriteAtlas.add_sprite adds and tracks sprites."""
        atlas = SpriteAtlas(max_width=32, max_height=32, padding=1, power_of_two=False,
                            algorithm=PackingAlgorithm.SHELF)
        canvas = Canvas(8, 8, (255, 0, 0, 255))

        added = atlas.add_sprite("hero", canvas, trim=False)
        duplicate = atlas.add_sprite("hero", canvas, trim=False)

        self.assertTrue(added)
        self.assertFalse(duplicate)
        result = atlas.get_sprite("hero")
        self.assertIsNotNone(result)
        page, sprite = result
        self.assertEqual(page.index, 0)
        self.assertEqual(sprite.width, 8)
        self.assertEqual(sprite.height, 8)

    def test_add_sprites_packs_within_bounds(self):
        """SpriteAtlas.add_sprites packs all sprites within page bounds."""
        atlas = SpriteAtlas(max_width=64, max_height=64, padding=1, power_of_two=False,
                            algorithm=PackingAlgorithm.MAXRECTS)
        sprites = [
            ("tall", Canvas(6, 12, (0, 255, 0, 255))),
            ("wide", Canvas(12, 6, (0, 0, 255, 255))),
            ("square", Canvas(8, 8, (255, 0, 0, 255))),
        ]

        added = atlas.add_sprites(sprites, trim=False)

        self.assertEqual(added, 3)
        for name, _ in sprites:
            page, sprite = atlas.get_sprite(name)
            self.assertGreaterEqual(sprite.x, 0)
            self.assertGreaterEqual(sprite.y, 0)
            self.assertLessEqual(sprite.x + sprite.width, page.canvas.width)
            self.assertLessEqual(sprite.y + sprite.height, page.canvas.height)

    def test_trimmed_sprite_metadata(self):
        """SpriteAtlas records trim metadata when trimming is enabled."""
        atlas = SpriteAtlas(max_width=32, max_height=32, padding=1, power_of_two=False,
                            algorithm=PackingAlgorithm.SHELF)
        canvas = Canvas(8, 8)  # Transparent by default
        canvas.fill_rect(2, 2, 4, 4, (255, 0, 0, 255))

        added = atlas.add_sprite("trim_me", canvas, trim=True)

        self.assertTrue(added)
        _, sprite = atlas.get_sprite("trim_me")
        self.assertTrue(sprite.trimmed)
        self.assertEqual(sprite.trim_x, 2)
        self.assertEqual(sprite.trim_y, 2)
        self.assertEqual(sprite.width, 4)
        self.assertEqual(sprite.height, 4)
        self.assertEqual(sprite.original_width, 8)
        self.assertEqual(sprite.original_height, 8)

    def test_power_of_two_page_dimensions(self):
        """SpriteAtlas respects power-of-two sizing for pages."""
        atlas = SpriteAtlas(max_width=30, max_height=30, padding=1, power_of_two=True,
                            algorithm=PackingAlgorithm.SHELF)
        atlas.add_sprite("sprite", Canvas(4, 4, (255, 0, 0, 255)))

        self.assertEqual(atlas.pages[0].canvas.width, 32)
        self.assertEqual(atlas.pages[0].canvas.height, 32)


class TestAtlasConvenience(TestCase):
    """Tests for create_atlas and pack_animations."""

    def test_create_atlas_uses_algorithm(self):
        """create_atlas returns a packed SpriteAtlas."""
        sprites = [
            ("a", Canvas(8, 8, (255, 0, 0, 255))),
            ("b", Canvas(8, 8, (0, 255, 0, 255))),
        ]

        atlas = create_atlas(sprites, max_size=64, padding=2, algorithm="shelf")

        self.assertIsInstance(atlas, SpriteAtlas)
        self.assertEqual(atlas.algorithm, PackingAlgorithm.SHELF)
        self.assertEqual(len(atlas.sprites), 2)

    def test_pack_animations_names_frames(self):
        """pack_animations names frames using animation and index."""
        animations = {
            "walk": [Canvas(4, 4, (255, 0, 0, 255)) for _ in range(2)],
            "idle": [Canvas(4, 4, (0, 255, 0, 255))],
        }

        atlas = pack_animations(animations, max_size=32)

        self.assertIn("walk_0", atlas.sprites)
        self.assertIn("walk_1", atlas.sprites)
        self.assertIn("idle_0", atlas.sprites)


class TestAtlasExportFormats(TestCase):
    """Tests for atlas export formats."""

    def _build_atlas(self) -> SpriteAtlas:
        atlas = SpriteAtlas(max_width=64, max_height=64, padding=1, power_of_two=False,
                            algorithm=PackingAlgorithm.SHELF)
        atlas.add_sprite("red", Canvas(8, 8, (255, 0, 0, 255)))
        atlas.add_sprite("green", Canvas(6, 6, (0, 255, 0, 255)))
        return atlas

    def test_export_json_format(self):
        """AtlasFormat.JSON writes metadata and png."""
        atlas = self._build_atlas()

        with tempfile.TemporaryDirectory() as tmpdir:
            base = os.path.join(tmpdir, "atlas")
            saved = atlas.save(base, format=AtlasFormat.JSON)

            json_path = f"{base}.json"
            png_path = f"{base}.png"
            self.assertIn(json_path, saved)
            self.assertIn(png_path, saved)
            self.assertTrue(os.path.exists(json_path))
            self.assertTrue(os.path.exists(png_path))

            with open(json_path, "r") as f:
                data = json.load(f)

            self.assertIn("sprites", data)
            self.assertIn("red", data["sprites"])

    def test_export_unity_format(self):
        """AtlasFormat.UNITY writes JSON metadata."""
        atlas = self._build_atlas()

        with tempfile.TemporaryDirectory() as tmpdir:
            base = os.path.join(tmpdir, "atlas")
            atlas.save(base, format=AtlasFormat.UNITY)

            json_path = f"{base}.json"
            self.assertTrue(os.path.exists(json_path))
            with open(json_path, "r") as f:
                data = json.load(f)
            self.assertIn("green", data["sprites"])

    def test_export_godot_format(self):
        """AtlasFormat.GODOT writes .tres metadata."""
        atlas = self._build_atlas()

        with tempfile.TemporaryDirectory() as tmpdir:
            base = os.path.join(tmpdir, "atlas")
            atlas.save(base, format=AtlasFormat.GODOT)

            tres_path = f"{base}.tres"
            self.assertTrue(os.path.exists(tres_path))
            with open(tres_path, "r") as f:
                content = f.read()
            self.assertIn("AtlasTexture", content)
            self.assertIn("Rect2", content)

    def test_export_gamemaker_format(self):
        """AtlasFormat.GAMEMAKER writes .yy metadata."""
        atlas = self._build_atlas()

        with tempfile.TemporaryDirectory() as tmpdir:
            base = os.path.join(tmpdir, "atlas")
            atlas.save(base, format=AtlasFormat.GAMEMAKER)

            yy_path = f"{base}.yy"
            self.assertTrue(os.path.exists(yy_path))
            with open(yy_path, "r") as f:
                data = json.load(f)
            frame_names = [frame["name"] for frame in data["frames"]]
            self.assertIn("red", frame_names)

    def test_export_phaser_format(self):
        """AtlasFormat.PHASER writes Phaser JSON metadata."""
        atlas = self._build_atlas()

        with tempfile.TemporaryDirectory() as tmpdir:
            base = os.path.join(tmpdir, "atlas")
            atlas.save(base, format=AtlasFormat.PHASER)

            phaser_path = f"{base}_phaser.json"
            self.assertTrue(os.path.exists(phaser_path))
            with open(phaser_path, "r") as f:
                data = json.load(f)
            self.assertIn("frames", data)
            self.assertIn("red", data["frames"])
            self.assertEqual(data["meta"]["image"], "atlas.png")

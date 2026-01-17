"""Tests for sprite detection."""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core import Canvas
from import_.sprite_detect import (
    DetectedSprite,
    DetectionConfig,
    SpriteDetector,
    Region,
    detect_sprites,
    detect_background,
    find_sprite_bounds,
    split_by_color,
)


def create_sprite_sheet():
    """Create a simple sprite sheet with 4 sprites."""
    canvas = Canvas(32, 32)

    # Clear to transparent background
    canvas.clear((0, 0, 0, 0))

    # Sprite 1: top-left (8x8 red square)
    for y in range(2, 10):
        for x in range(2, 10):
            canvas.set_pixel(x, y, (255, 0, 0, 255))

    # Sprite 2: top-right (8x8 green square)
    for y in range(2, 10):
        for x in range(18, 26):
            canvas.set_pixel(x, y, (0, 255, 0, 255))

    # Sprite 3: bottom-left (8x8 blue square)
    for y in range(18, 26):
        for x in range(2, 10):
            canvas.set_pixel(x, y, (0, 0, 255, 255))

    # Sprite 4: bottom-right (8x8 yellow square)
    for y in range(18, 26):
        for x in range(18, 26):
            canvas.set_pixel(x, y, (255, 255, 0, 255))

    return canvas


def create_sheet_with_background():
    """Create a sprite sheet with solid background."""
    canvas = Canvas(32, 32)

    # Clear to pink background
    canvas.clear((255, 0, 255, 255))

    # Add a sprite in the center
    for y in range(10, 22):
        for x in range(10, 22):
            canvas.set_pixel(x, y, (100, 100, 100, 255))

    return canvas


def create_complex_sprite():
    """Create a complex sprite with gaps."""
    canvas = Canvas(16, 16)
    canvas.clear((0, 0, 0, 0))

    # Draw a ring shape (has internal gap)
    for y in range(16):
        for x in range(16):
            dx = x - 7.5
            dy = y - 7.5
            dist = (dx * dx + dy * dy) ** 0.5
            if 4 <= dist <= 7:
                canvas.set_pixel(x, y, (200, 100, 50, 255))

    return canvas


class TestRegion:
    """Tests for Region class."""

    def test_region_add_pixel(self):
        """Test adding pixels to a region."""
        region = Region()
        region.add_pixel(5, 10)
        region.add_pixel(6, 11)

        assert (5, 10) in region.pixels
        assert (6, 11) in region.pixels
        assert region.min_x == 5
        assert region.max_x == 6
        assert region.min_y == 10
        assert region.max_y == 11

    def test_region_bounds(self):
        """Test region bounding box."""
        region = Region()
        region.add_pixel(0, 0)
        region.add_pixel(10, 20)

        bounds = region.bounds
        assert bounds == (0, 0, 11, 21)

    def test_region_merge(self):
        """Test merging regions."""
        r1 = Region()
        r1.add_pixel(0, 0)
        r1.add_pixel(1, 1)

        r2 = Region()
        r2.add_pixel(10, 10)
        r2.add_pixel(11, 11)

        r1.merge(r2)

        assert len(r1.pixels) == 4
        assert r1.max_x == 11
        assert r1.max_y == 11

    def test_overlaps_with_margin(self):
        """Test overlap detection with margin."""
        r1 = Region()
        r1.add_pixel(0, 0)
        r1.add_pixel(5, 5)

        r2 = Region()
        r2.add_pixel(8, 0)
        r2.add_pixel(12, 5)

        # No overlap without margin
        assert not r1.overlaps_with_margin(r2, 0)

        # Overlaps with margin of 3
        assert r1.overlaps_with_margin(r2, 3)


class TestSpriteDetector:
    """Tests for SpriteDetector."""

    def test_detect_basic(self):
        """Test basic sprite detection."""
        canvas = create_sprite_sheet()
        detector = SpriteDetector()
        sprites = detector.detect(canvas)

        assert len(sprites) == 4

    def test_detect_with_config(self):
        """Test detection with custom config."""
        canvas = create_sprite_sheet()
        config = DetectionConfig(min_size=4, max_size=16)
        detector = SpriteDetector(config)
        sprites = detector.detect(canvas)

        assert len(sprites) == 4
        for sprite in sprites:
            assert sprite.width >= 4
            assert sprite.height >= 4

    def test_detect_background(self):
        """Test background color detection."""
        canvas = create_sheet_with_background()
        detector = SpriteDetector()
        bg = detector.detect_background(canvas)

        # Should detect pink as background
        assert bg == (255, 0, 255, 255)

    def test_detect_transparent_background(self):
        """Test detecting transparent background."""
        canvas = create_sprite_sheet()
        detector = SpriteDetector()
        bg = detector.detect_background(canvas)

        # Should detect transparent
        assert bg[3] == 0

    def test_find_connected_regions(self):
        """Test connected region finding."""
        canvas = create_sprite_sheet()
        detector = SpriteDetector()
        bg = detector.detect_background(canvas)
        regions = detector.find_connected_regions(canvas, bg)

        assert len(regions) == 4

    def test_merge_nearby_sprites(self):
        """Test merging nearby sprites."""
        canvas = Canvas(16, 16)
        canvas.clear((0, 0, 0, 0))

        # Two sprites 2 pixels apart
        for y in range(4):
            for x in range(4):
                canvas.set_pixel(x, y, (255, 0, 0, 255))
                canvas.set_pixel(x + 6, y, (0, 255, 0, 255))

        # Without merging
        config = DetectionConfig(merge_nearby=False)
        detector = SpriteDetector(config)
        sprites = detector.detect(canvas)
        assert len(sprites) == 2

        # With merging (threshold 3)
        config = DetectionConfig(merge_nearby=True, merge_threshold=3)
        detector = SpriteDetector(config)
        sprites = detector.detect(canvas)
        assert len(sprites) == 1

    def test_margin(self):
        """Test sprite extraction with margin."""
        canvas = Canvas(16, 16)
        canvas.clear((0, 0, 0, 0))

        # 4x4 sprite in center
        for y in range(6, 10):
            for x in range(6, 10):
                canvas.set_pixel(x, y, (255, 0, 0, 255))

        config = DetectionConfig(margin=2)
        detector = SpriteDetector(config)
        sprites = detector.detect(canvas)

        assert len(sprites) == 1
        # Should be larger due to margin
        assert sprites[0].width >= 8
        assert sprites[0].height >= 8

    def test_size_filter(self):
        """Test filtering by size."""
        canvas = Canvas(32, 32)
        canvas.clear((0, 0, 0, 0))

        # Small sprite (2x2)
        for y in range(2):
            for x in range(2):
                canvas.set_pixel(x, y, (255, 0, 0, 255))

        # Large sprite (10x10)
        for y in range(10, 20):
            for x in range(10, 20):
                canvas.set_pixel(x, y, (0, 255, 0, 255))

        # Filter to only get large sprite
        config = DetectionConfig(min_size=5)
        detector = SpriteDetector(config)
        sprites = detector.detect(canvas)

        assert len(sprites) == 1
        assert sprites[0].width >= 10


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_detect_sprites(self):
        """Test detect_sprites function."""
        canvas = create_sprite_sheet()
        sprites = detect_sprites(canvas)

        assert len(sprites) == 4
        for sprite in sprites:
            assert isinstance(sprite, DetectedSprite)
            assert sprite.canvas is not None

    def test_detect_sprites_with_kwargs(self):
        """Test detect_sprites with keyword arguments."""
        canvas = create_sprite_sheet()
        sprites = detect_sprites(canvas, min_size=4, merge_nearby=False)

        assert len(sprites) == 4

    def test_detect_background_function(self):
        """Test detect_background function."""
        canvas = create_sheet_with_background()
        bg = detect_background(canvas)

        assert bg == (255, 0, 255, 255)

    def test_find_sprite_bounds(self):
        """Test find_sprite_bounds function."""
        canvas = Canvas(32, 32)
        canvas.clear((0, 0, 0, 0))

        # Sprite at (10, 10) with size 8x8
        for y in range(10, 18):
            for x in range(10, 18):
                canvas.set_pixel(x, y, (255, 0, 0, 255))

        bounds = find_sprite_bounds(canvas)
        x, y, w, h = bounds

        assert x == 10
        assert y == 10
        assert w == 8
        assert h == 8

    def test_split_by_color(self):
        """Test split_by_color function."""
        canvas = Canvas(16, 8)

        # Two sprites separated by magenta
        for y in range(8):
            for x in range(7):
                canvas.set_pixel(x, y, (255, 0, 0, 255))
            canvas.set_pixel(7, y, (255, 0, 255, 255))  # Separator
            canvas.set_pixel(8, y, (255, 0, 255, 255))  # Separator
            for x in range(9, 16):
                canvas.set_pixel(x, y, (0, 255, 0, 255))

        parts = split_by_color(canvas, (255, 0, 255, 255))
        assert len(parts) == 2


class TestDetectedSprite:
    """Tests for DetectedSprite dataclass."""

    def test_detected_sprite_properties(self):
        """Test DetectedSprite property access."""
        sprite_canvas = Canvas(8, 8)
        sprite = DetectedSprite(
            bounds=(10, 20, 8, 8),
            canvas=sprite_canvas,
            label="test"
        )

        assert sprite.x == 10
        assert sprite.y == 20
        assert sprite.width == 8
        assert sprite.height == 8
        assert sprite.label == "test"


class TestEdgeCases:
    """Tests for edge cases."""

    def test_empty_canvas(self):
        """Test detection on empty canvas."""
        canvas = Canvas(16, 16)
        canvas.clear((0, 0, 0, 0))

        sprites = detect_sprites(canvas)
        assert len(sprites) == 0

    def test_full_canvas(self):
        """Test detection on fully filled canvas."""
        canvas = Canvas(16, 16)
        canvas.clear((255, 0, 0, 255))

        # Should detect one large sprite
        sprites = detect_sprites(canvas)
        assert len(sprites) == 1
        assert sprites[0].width == 16

    def test_single_pixel(self):
        """Test ignoring single pixels."""
        canvas = Canvas(16, 16)
        canvas.clear((0, 0, 0, 0))
        canvas.set_pixel(8, 8, (255, 0, 0, 255))

        # With ignore_single_pixels=True (default)
        sprites = detect_sprites(canvas, ignore_single_pixels=True)
        assert len(sprites) == 0

        # With ignore_single_pixels=False
        sprites = detect_sprites(canvas, ignore_single_pixels=False, min_size=1)
        assert len(sprites) == 1

    def test_complex_shape(self):
        """Test detection of complex shapes."""
        canvas = create_complex_sprite()
        sprites = detect_sprites(canvas, min_size=1)

        # Ring should be detected as one sprite
        assert len(sprites) == 1

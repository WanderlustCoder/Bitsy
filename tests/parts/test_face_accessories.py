"""
Test Face Accessories - Tests for glasses and other face accessories.

Tests:
- Glasses creation and configuration
- Lens and frame rendering
- Face accessory factory
- Different glasses styles
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests.framework import TestCase
from core import Canvas
from parts.face_accessories import (
    FaceAccessory,
    Glasses,
    RoundGlasses,
    SquareGlasses,
    Goggles,
    EyePatch,
    GlassesConfig,
    create_face_accessory,
    list_face_accessory_types,
    FACE_ACCESSORY_TYPES
)
from parts.equipment import EquipmentSlot, DrawLayer


class TestFaceAccessoryBase(TestCase):
    """Tests for FaceAccessory base class."""

    def test_face_accessory_slot(self):
        """FaceAccessory uses HEAD equipment slot."""
        glasses = Glasses()
        self.assertEqual(glasses.config.slot, EquipmentSlot.HEAD)

    def test_face_accessory_layer(self):
        """FaceAccessory renders in front layer."""
        glasses = Glasses()
        self.assertEqual(glasses.config.layer, DrawLayer.FRONT)


class TestGlasses(TestCase):
    """Tests for Glasses class."""

    def test_glasses_creation(self):
        """Glasses can be created with default config."""
        glasses = Glasses()
        self.assertEqual(glasses.name, 'glasses')

    def test_glasses_with_config(self):
        """Glasses can be created with custom config."""
        config = GlassesConfig(
            frame_color=(100, 50, 50, 255),
            lens_color=(200, 220, 255, 100),
            lens_opacity=80
        )
        glasses = Glasses(config)

        self.assertEqual(glasses.frame_color, (100, 50, 50, 255))

    def test_glasses_draw(self):
        """Glasses can draw to canvas."""
        canvas = Canvas(32, 32)
        glasses = Glasses()

        # Draw at center with face dimensions
        glasses.draw(canvas, 16, 16, 24, 20)

        self.assertCanvasNotEmpty(canvas)

    def test_glasses_frame_thickness(self):
        """Glasses respects frame thickness config."""
        config = GlassesConfig(frame_thickness=2)
        glasses = Glasses(config)
        self.assertEqual(glasses.glasses_config.frame_thickness, 2)

    def test_glasses_bridge_styles(self):
        """Glasses supports different bridge styles."""
        for style in ['bar', 'double', 'rimless']:
            config = GlassesConfig(bridge_style=style)
            glasses = Glasses(config)
            self.assertEqual(glasses.glasses_config.bridge_style, style)


class TestRoundGlasses(TestCase):
    """Tests for RoundGlasses variant."""

    def test_round_glasses_creation(self):
        """RoundGlasses can be created."""
        glasses = RoundGlasses()
        self.assertEqual(glasses.name, 'round_glasses')

    def test_round_glasses_draw(self):
        """RoundGlasses can draw to canvas."""
        canvas = Canvas(32, 32)
        glasses = RoundGlasses()
        glasses.draw(canvas, 16, 16, 24, 20)
        self.assertCanvasNotEmpty(canvas)


class TestSquareGlasses(TestCase):
    """Tests for SquareGlasses variant."""

    def test_square_glasses_creation(self):
        """SquareGlasses can be created."""
        glasses = SquareGlasses()
        self.assertEqual(glasses.name, 'square_glasses')

    def test_square_glasses_draw(self):
        """SquareGlasses can draw rectangular lenses."""
        canvas = Canvas(32, 32)
        glasses = SquareGlasses()
        glasses.draw(canvas, 16, 16, 24, 20)
        self.assertCanvasNotEmpty(canvas)


class TestGoggles(TestCase):
    """Tests for Goggles class."""

    def test_goggles_creation(self):
        """Goggles can be created."""
        goggles = Goggles()
        self.assertEqual(goggles.name, 'goggles')

    def test_goggles_draw(self):
        """Goggles can draw to canvas."""
        canvas = Canvas(32, 32)
        goggles = Goggles()
        goggles.draw(canvas, 16, 16, 24, 20)
        self.assertCanvasNotEmpty(canvas)


class TestEyePatch(TestCase):
    """Tests for EyePatch class."""

    def test_eye_patch_creation(self):
        """EyePatch can be created."""
        patch = EyePatch()
        self.assertEqual(patch.name, 'eye_patch')

    def test_eye_patch_sides(self):
        """EyePatch can be configured for left or right eye."""
        left_patch = EyePatch(side='left')
        right_patch = EyePatch(side='right')

        self.assertEqual(left_patch.side, 'left')
        self.assertEqual(right_patch.side, 'right')

    def test_eye_patch_draw(self):
        """EyePatch can draw to canvas."""
        canvas = Canvas(32, 32)
        patch = EyePatch()
        patch.draw(canvas, 16, 16, 24, 20)
        self.assertCanvasNotEmpty(canvas)


class TestFaceAccessoryFactory(TestCase):
    """Tests for face accessory factory functions."""

    def test_create_face_accessory_glasses(self):
        """create_face_accessory creates glasses."""
        glasses = create_face_accessory('glasses')
        self.assertIsInstance(glasses, Glasses)

    def test_create_face_accessory_goggles(self):
        """create_face_accessory creates goggles."""
        goggles = create_face_accessory('goggles')
        self.assertIsInstance(goggles, Goggles)

    def test_create_face_accessory_eye_patch(self):
        """create_face_accessory creates eye patch."""
        patch = create_face_accessory('eye_patch')
        self.assertIsInstance(patch, EyePatch)

    def test_create_face_accessory_invalid(self):
        """create_face_accessory raises for unknown type."""
        with self.assertRaises(ValueError):
            create_face_accessory('unknown_accessory')

    def test_list_face_accessory_types(self):
        """list_face_accessory_types returns all types."""
        types = list_face_accessory_types()

        self.assertIn('glasses', types)
        self.assertIn('round_glasses', types)
        self.assertIn('square_glasses', types)
        self.assertIn('goggles', types)
        self.assertIn('eye_patch', types)

    def test_face_accessory_types_dict(self):
        """FACE_ACCESSORY_TYPES contains all accessory classes."""
        self.assertEqual(len(FACE_ACCESSORY_TYPES), 5)
        self.assertIn('glasses', FACE_ACCESSORY_TYPES)

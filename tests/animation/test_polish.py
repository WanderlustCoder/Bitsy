"""
Test Animation Polish - Tests for animation enhancement module.

Tests:
- Smear frames (blend, stretch, multiple)
- Motion blur
- Anticipation frames
- Follow-through and overshoot
- Secondary motion simulation
- Hold frames
- Timing optimization
"""

import sys
import os
import math

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests.framework import TestCase, CanvasFixtures
from core import Canvas
from core.animation import Animation


# Import polish module
try:
    from animation.polish import (
        SmearType,
        SecondaryType,
        MotionData,
        SecondaryPoint,
        SecondaryMotionSimulator,
        create_smear_frame,
        add_motion_blur,
        add_anticipation,
        add_follow_through,
        add_overshoot,
        add_holds,
        optimize_timing,
        adjust_fps,
        polish_animation,
        list_smear_types,
        list_secondary_types,
    )
    POLISH_AVAILABLE = True
except ImportError as e:
    POLISH_AVAILABLE = False
    IMPORT_ERROR = str(e)


def create_test_animation(frame_count: int = 4, width: int = 16, height: int = 16) -> Animation:
    """Create a test animation with moving content."""
    anim = Animation("test", fps=8)

    for i in range(frame_count):
        canvas = Canvas(width, height)
        # Draw a moving square
        x = 2 + i * 3
        y = 4 + i * 2
        for dy in range(4):
            for dx in range(4):
                if x + dx < width and y + dy < height:
                    canvas.set_pixel_solid(x + dx, y + dy, (255, 100, 50, 255))
        anim.add_frame(canvas, 1.0, f"frame_{i}")

    return anim


class TestSmearTypes(TestCase):
    """Tests for SmearType enum."""

    def test_smear_types_defined(self):
        """SmearType enum has expected values."""
        self.skipUnless(POLISH_AVAILABLE, "Polish module not available")

        self.assertEqual(SmearType.STRETCH.value, 'stretch')
        self.assertEqual(SmearType.MULTIPLE.value, 'multiple')
        self.assertEqual(SmearType.DIRECTIONAL.value, 'directional')
        self.assertEqual(SmearType.BLEND.value, 'blend')

    def test_list_smear_types(self):
        """list_smear_types returns all types."""
        self.skipUnless(POLISH_AVAILABLE, "Polish module not available")

        types = list_smear_types()
        self.assertIn('stretch', types)
        self.assertIn('multiple', types)
        self.assertIn('directional', types)
        self.assertIn('blend', types)
        self.assertEqual(len(types), 4)


class TestSecondaryTypes(TestCase):
    """Tests for SecondaryType enum."""

    def test_secondary_types_defined(self):
        """SecondaryType enum has expected values."""
        self.skipUnless(POLISH_AVAILABLE, "Polish module not available")

        self.assertEqual(SecondaryType.HAIR.value, 'hair')
        self.assertEqual(SecondaryType.CLOTH.value, 'cloth')
        self.assertEqual(SecondaryType.TAIL.value, 'tail')
        self.assertEqual(SecondaryType.CHAIN.value, 'chain')
        self.assertEqual(SecondaryType.RIBBON.value, 'ribbon')

    def test_list_secondary_types(self):
        """list_secondary_types returns all types."""
        self.skipUnless(POLISH_AVAILABLE, "Polish module not available")

        types = list_secondary_types()
        self.assertIn('hair', types)
        self.assertIn('cloth', types)
        self.assertIn('tail', types)
        self.assertIn('chain', types)
        self.assertIn('ribbon', types)
        self.assertEqual(len(types), 5)


class TestMotionData(TestCase):
    """Tests for MotionData dataclass."""

    def test_motion_data_creation(self):
        """MotionData can be created with defaults."""
        self.skipUnless(POLISH_AVAILABLE, "Polish module not available")

        motion = MotionData()
        self.assertEqual(motion.dx, 0.0)
        self.assertEqual(motion.dy, 0.0)
        self.assertEqual(motion.rotation, 0.0)
        self.assertEqual(motion.scale_change, 0.0)

    def test_motion_data_with_values(self):
        """MotionData can be created with custom values."""
        self.skipUnless(POLISH_AVAILABLE, "Polish module not available")

        motion = MotionData(dx=10.0, dy=5.0, rotation=0.5, scale_change=0.1)
        self.assertEqual(motion.dx, 10.0)
        self.assertEqual(motion.dy, 5.0)
        self.assertEqual(motion.rotation, 0.5)
        self.assertEqual(motion.scale_change, 0.1)

    def test_motion_speed_calculation(self):
        """MotionData.speed calculates correctly."""
        self.skipUnless(POLISH_AVAILABLE, "Polish module not available")

        motion = MotionData(dx=3.0, dy=4.0)
        self.assertAlmostEqual(motion.speed, 5.0, places=5)

        motion2 = MotionData(dx=0.0, dy=0.0)
        self.assertEqual(motion2.speed, 0.0)

    def test_motion_direction_calculation(self):
        """MotionData.direction calculates correctly."""
        self.skipUnless(POLISH_AVAILABLE, "Polish module not available")

        # Moving right
        motion = MotionData(dx=1.0, dy=0.0)
        self.assertAlmostEqual(motion.direction, 0.0, places=5)

        # Moving down
        motion2 = MotionData(dx=0.0, dy=1.0)
        self.assertAlmostEqual(motion2.direction, math.pi / 2, places=5)

        # Moving left
        motion3 = MotionData(dx=-1.0, dy=0.0)
        self.assertAlmostEqual(motion3.direction, math.pi, places=5)


class TestSmearFrames(TestCase):
    """Tests for smear frame creation."""

    def test_create_smear_frame_blend(self):
        """create_smear_frame creates blend smear."""
        self.skipUnless(POLISH_AVAILABLE, "Polish module not available")

        frame1 = CanvasFixtures.circle((255, 0, 0, 255), size=16)
        frame2 = CanvasFixtures.circle((0, 255, 0, 255), size=16)

        result = create_smear_frame(frame1, frame2, intensity=0.5, smear_type='blend')

        self.assertCanvasSize(result, 16, 16)
        self.assertCanvasNotEmpty(result)

    def test_create_smear_frame_stretch(self):
        """create_smear_frame creates stretch smear."""
        self.skipUnless(POLISH_AVAILABLE, "Polish module not available")

        frame1 = Canvas(16, 16)
        frame2 = Canvas(16, 16)

        # Draw content in different positions
        frame1.fill_rect(2, 2, 4, 4, (255, 0, 0, 255))
        frame2.fill_rect(10, 10, 4, 4, (255, 0, 0, 255))

        result = create_smear_frame(frame1, frame2, intensity=0.8, smear_type='stretch')

        self.assertCanvasSize(result, 16, 16)
        self.assertCanvasNotEmpty(result)

    def test_create_smear_frame_multiple(self):
        """create_smear_frame creates multiple ghost smear."""
        self.skipUnless(POLISH_AVAILABLE, "Polish module not available")

        frame1 = Canvas(16, 16)
        frame2 = Canvas(16, 16)

        frame1.fill_rect(2, 2, 4, 4, (255, 0, 0, 255))
        frame2.fill_rect(8, 8, 4, 4, (255, 0, 0, 255))

        result = create_smear_frame(frame1, frame2, intensity=0.7, smear_type='multiple')

        self.assertCanvasSize(result, 16, 16)
        self.assertCanvasNotEmpty(result)

    def test_create_smear_frame_default_type(self):
        """create_smear_frame defaults to blend type."""
        self.skipUnless(POLISH_AVAILABLE, "Polish module not available")

        frame1 = CanvasFixtures.circle((255, 0, 0, 255), size=16)
        frame2 = CanvasFixtures.circle((0, 255, 0, 255), size=16)

        result = create_smear_frame(frame1, frame2, intensity=0.5)

        self.assertCanvasNotEmpty(result)

    def test_create_smear_frame_intensity_range(self):
        """create_smear_frame works with various intensities."""
        self.skipUnless(POLISH_AVAILABLE, "Polish module not available")

        frame1 = CanvasFixtures.circle((255, 0, 0, 255), size=16)
        frame2 = CanvasFixtures.circle((0, 255, 0, 255), size=16)

        for intensity in [0.0, 0.25, 0.5, 0.75, 1.0]:
            result = create_smear_frame(frame1, frame2, intensity=intensity)
            self.assertCanvasNotEmpty(result)


class TestMotionBlur(TestCase):
    """Tests for motion blur functionality."""

    def test_add_motion_blur_basic(self):
        """add_motion_blur adds blur frames to animation."""
        self.skipUnless(POLISH_AVAILABLE, "Polish module not available")

        anim = create_test_animation(frame_count=3)
        original_count = anim.frame_count

        result = add_motion_blur(anim, blur_frames=1)

        # Should have more frames due to blur insertions
        self.assertGreater(result.frame_count, original_count)
        self.assertIn("_blurred", result.name)

    def test_add_motion_blur_preserves_loop(self):
        """add_motion_blur preserves loop setting."""
        self.skipUnless(POLISH_AVAILABLE, "Polish module not available")

        anim = create_test_animation(frame_count=3)
        anim.loop = True

        result = add_motion_blur(anim, blur_frames=1)

        self.assertTrue(result.loop)

    def test_add_motion_blur_single_frame(self):
        """add_motion_blur handles single-frame animation."""
        self.skipUnless(POLISH_AVAILABLE, "Polish module not available")

        anim = create_test_animation(frame_count=1)

        result = add_motion_blur(anim, blur_frames=1)

        # Should return unchanged for single frame
        self.assertEqual(result.frame_count, 1)

    def test_add_motion_blur_multiple_blur_frames(self):
        """add_motion_blur with multiple blur frames."""
        self.skipUnless(POLISH_AVAILABLE, "Polish module not available")

        anim = create_test_animation(frame_count=3)

        result = add_motion_blur(anim, blur_frames=2)

        self.assertGreater(result.frame_count, anim.frame_count)


class TestAnticipation(TestCase):
    """Tests for anticipation frame functionality."""

    def test_add_anticipation_basic(self):
        """add_anticipation adds anticipation frames."""
        self.skipUnless(POLISH_AVAILABLE, "Polish module not available")

        anim = create_test_animation(frame_count=3)
        original_count = anim.frame_count

        result = add_anticipation(anim, frames=2)

        self.assertEqual(result.frame_count, original_count + 2)
        self.assertIn("_antic", result.name)

    def test_add_anticipation_custom_scale(self):
        """add_anticipation with custom scale factor."""
        self.skipUnless(POLISH_AVAILABLE, "Polish module not available")

        anim = create_test_animation(frame_count=3)

        result = add_anticipation(anim, frames=2, scale_factor=0.8)

        self.assertEqual(result.frame_count, anim.frame_count + 2)

    def test_add_anticipation_custom_direction(self):
        """add_anticipation with custom offset direction."""
        self.skipUnless(POLISH_AVAILABLE, "Polish module not available")

        anim = create_test_animation(frame_count=3)

        result = add_anticipation(anim, frames=3, offset_direction=(1, 0))

        self.assertEqual(result.frame_count, anim.frame_count + 3)

    def test_add_anticipation_empty_animation(self):
        """add_anticipation handles empty animation."""
        self.skipUnless(POLISH_AVAILABLE, "Polish module not available")

        anim = Animation("empty", fps=8)

        result = add_anticipation(anim, frames=2)

        self.assertEqual(result.frame_count, 0)


class TestFollowThrough(TestCase):
    """Tests for follow-through functionality."""

    def test_add_follow_through_basic(self):
        """add_follow_through adds follow-through frames."""
        self.skipUnless(POLISH_AVAILABLE, "Polish module not available")

        anim = create_test_animation(frame_count=3)
        original_count = anim.frame_count

        result = add_follow_through(anim, frames=2)

        self.assertEqual(result.frame_count, original_count + 2)
        self.assertIn("_follow", result.name)
        self.assertFalse(result.loop)  # Follow-through ends animation

    def test_add_follow_through_custom_overshoot(self):
        """add_follow_through with custom overshoot."""
        self.skipUnless(POLISH_AVAILABLE, "Polish module not available")

        anim = create_test_animation(frame_count=3)

        result = add_follow_through(anim, frames=3, overshoot=0.2)

        self.assertEqual(result.frame_count, anim.frame_count + 3)

    def test_add_follow_through_empty_animation(self):
        """add_follow_through handles empty animation."""
        self.skipUnless(POLISH_AVAILABLE, "Polish module not available")

        anim = Animation("empty", fps=8)

        result = add_follow_through(anim, frames=2)

        self.assertEqual(result.frame_count, 0)


class TestOvershoot(TestCase):
    """Tests for overshoot functionality."""

    def test_add_overshoot_basic(self):
        """add_overshoot adds overshoot and settle frames."""
        self.skipUnless(POLISH_AVAILABLE, "Polish module not available")

        anim = create_test_animation(frame_count=3)
        original_count = anim.frame_count

        result = add_overshoot(anim, amount=0.15)

        # Adds overshoot frame + settle frames
        self.assertGreater(result.frame_count, original_count)
        self.assertIn("_overshoot", result.name)

    def test_add_overshoot_custom_settle(self):
        """add_overshoot with custom settle frames."""
        self.skipUnless(POLISH_AVAILABLE, "Polish module not available")

        anim = create_test_animation(frame_count=3)
        original_count = anim.frame_count

        result = add_overshoot(anim, amount=0.2, settle_frames=5)

        # Original + overshoot + settle frames
        self.assertEqual(result.frame_count, original_count + 1 + 5)

    def test_add_overshoot_single_frame(self):
        """add_overshoot handles animation with single frame."""
        self.skipUnless(POLISH_AVAILABLE, "Polish module not available")

        anim = create_test_animation(frame_count=1)

        result = add_overshoot(anim, amount=0.1)

        # Returns unchanged for single frame
        self.assertEqual(result.frame_count, 1)


class TestHoldFrames(TestCase):
    """Tests for hold frames functionality."""

    def test_add_holds_basic(self):
        """add_holds extends duration of key frames."""
        self.skipUnless(POLISH_AVAILABLE, "Polish module not available")

        anim = create_test_animation(frame_count=4)

        result = add_holds(anim, key_frame_indices=[0, 2], hold_duration=2.0)

        self.assertEqual(result.frame_count, 4)
        self.assertIn("_holds", result.name)

        # Check that held frames have extended duration
        self.assertEqual(result.keyframes[0].duration, 2.0)  # Held
        self.assertEqual(result.keyframes[1].duration, 1.0)  # Not held
        self.assertEqual(result.keyframes[2].duration, 2.0)  # Held

    def test_add_holds_preserves_loop(self):
        """add_holds preserves loop setting."""
        self.skipUnless(POLISH_AVAILABLE, "Polish module not available")

        anim = create_test_animation(frame_count=4)
        anim.loop = True

        result = add_holds(anim, key_frame_indices=[1], hold_duration=3.0)

        self.assertTrue(result.loop)

    def test_add_holds_empty_indices(self):
        """add_holds with empty indices list."""
        self.skipUnless(POLISH_AVAILABLE, "Polish module not available")

        anim = create_test_animation(frame_count=3)

        result = add_holds(anim, key_frame_indices=[], hold_duration=2.0)

        # All frames should have original duration
        for kf in result.keyframes:
            self.assertEqual(kf.duration, 1.0)


class TestSecondaryMotionSimulator(TestCase):
    """Tests for SecondaryMotionSimulator class."""

    def test_simulator_creation(self):
        """SecondaryMotionSimulator can be created."""
        self.skipUnless(POLISH_AVAILABLE, "Polish module not available")

        sim = SecondaryMotionSimulator(num_points=5, damping=0.7, stiffness=0.4, gravity=0.5)

        self.assertEqual(sim.num_points, 5)
        self.assertEqual(sim.damping, 0.7)
        self.assertEqual(sim.stiffness, 0.4)
        self.assertEqual(sim.gravity, 0.5)

    def test_simulator_initialize(self):
        """SecondaryMotionSimulator can be initialized."""
        self.skipUnless(POLISH_AVAILABLE, "Polish module not available")

        sim = SecondaryMotionSimulator(num_points=5)
        sim.initialize(10.0, 10.0, direction=(0, 1), spacing=3.0)

        self.assertEqual(len(sim.points), 5)
        self.assertTrue(sim._initialized)

    def test_simulator_update(self):
        """SecondaryMotionSimulator can be updated."""
        self.skipUnless(POLISH_AVAILABLE, "Polish module not available")

        sim = SecondaryMotionSimulator(num_points=5)
        sim.initialize(10.0, 10.0, direction=(0, 1), spacing=3.0)

        # Update with movement
        sim.update(12.0, 10.0, velocity_x=2.0, velocity_y=0.0)

        # First point should follow anchor
        self.assertEqual(sim.points[0].x, 12.0)

    def test_simulator_get_positions(self):
        """SecondaryMotionSimulator returns positions."""
        self.skipUnless(POLISH_AVAILABLE, "Polish module not available")

        sim = SecondaryMotionSimulator(num_points=4)
        sim.initialize(10.0, 10.0, direction=(0, 1), spacing=3.0)

        positions = sim.get_positions()

        self.assertEqual(len(positions), 4)
        for pos in positions:
            self.assertEqual(len(pos), 2)

    def test_simulator_render_to_canvas(self):
        """SecondaryMotionSimulator can render to canvas."""
        self.skipUnless(POLISH_AVAILABLE, "Polish module not available")

        sim = SecondaryMotionSimulator(num_points=4)
        sim.initialize(8.0, 4.0, direction=(0, 1), spacing=3.0)

        canvas = Canvas(16, 16)
        sim.render_to_canvas(canvas, (255, 100, 50, 255), thickness=1)

        self.assertCanvasNotEmpty(canvas)

    def test_simulator_uninitialized_update(self):
        """SecondaryMotionSimulator handles update when not initialized."""
        self.skipUnless(POLISH_AVAILABLE, "Polish module not available")

        sim = SecondaryMotionSimulator(num_points=4)
        # Should not raise error
        sim.update(10.0, 10.0)


class TestTimingOptimization(TestCase):
    """Tests for timing optimization functionality."""

    def test_optimize_timing_basic(self):
        """optimize_timing adjusts frame durations."""
        self.skipUnless(POLISH_AVAILABLE, "Polish module not available")

        anim = create_test_animation(frame_count=4)

        result = optimize_timing(anim)

        self.assertEqual(result.frame_count, 4)
        self.assertIn("_optimized", result.name)

    def test_optimize_timing_preserves_loop(self):
        """optimize_timing preserves loop setting."""
        self.skipUnless(POLISH_AVAILABLE, "Polish module not available")

        anim = create_test_animation(frame_count=4)
        anim.loop = True

        result = optimize_timing(anim)

        self.assertTrue(result.loop)

    def test_optimize_timing_custom_duration_range(self):
        """optimize_timing with custom min/max duration."""
        self.skipUnless(POLISH_AVAILABLE, "Polish module not available")

        anim = create_test_animation(frame_count=4)

        result = optimize_timing(anim, min_duration=0.3, max_duration=2.0)

        # All durations should be within range
        for kf in result.keyframes:
            self.assertGreaterEqual(kf.duration, 0.3)
            self.assertLessEqual(kf.duration, 2.0)

    def test_optimize_timing_single_frame(self):
        """optimize_timing handles single-frame animation."""
        self.skipUnless(POLISH_AVAILABLE, "Polish module not available")

        anim = create_test_animation(frame_count=1)

        result = optimize_timing(anim)

        self.assertEqual(result.frame_count, 1)


class TestAdjustFPS(TestCase):
    """Tests for FPS adjustment functionality."""

    def test_adjust_fps_increase(self):
        """adjust_fps can increase FPS."""
        self.skipUnless(POLISH_AVAILABLE, "Polish module not available")

        anim = create_test_animation(frame_count=4)
        anim_fps = anim.fps  # 8

        result = adjust_fps(anim, target_fps=16)

        self.assertEqual(result.fps, 16)

    def test_adjust_fps_decrease(self):
        """adjust_fps can decrease FPS."""
        self.skipUnless(POLISH_AVAILABLE, "Polish module not available")

        anim = create_test_animation(frame_count=4)

        result = adjust_fps(anim, target_fps=4)

        self.assertEqual(result.fps, 4)

    def test_adjust_fps_scales_duration(self):
        """adjust_fps scales frame durations."""
        self.skipUnless(POLISH_AVAILABLE, "Polish module not available")

        anim = create_test_animation(frame_count=2)
        original_duration = anim.keyframes[0].duration

        result = adjust_fps(anim, target_fps=16)  # Double FPS

        # Duration should be scaled
        self.assertAlmostEqual(result.keyframes[0].duration, original_duration * 0.5, places=3)

    def test_adjust_fps_preserves_loop(self):
        """adjust_fps preserves loop setting."""
        self.skipUnless(POLISH_AVAILABLE, "Polish module not available")

        anim = create_test_animation(frame_count=3)
        anim.loop = True

        result = adjust_fps(anim, target_fps=12)

        self.assertTrue(result.loop)


class TestPolishAnimation(TestCase):
    """Tests for polish_animation convenience function."""

    def test_polish_animation_default(self):
        """polish_animation with default options."""
        self.skipUnless(POLISH_AVAILABLE, "Polish module not available")

        anim = create_test_animation(frame_count=4)

        result = polish_animation(anim)

        self.assertIn("_polished", result.name)

    def test_polish_animation_with_blur(self):
        """polish_animation with motion blur."""
        self.skipUnless(POLISH_AVAILABLE, "Polish module not available")

        anim = create_test_animation(frame_count=3)
        original_count = anim.frame_count

        result = polish_animation(anim, add_blur=True)

        self.assertGreater(result.frame_count, original_count)

    def test_polish_animation_with_anticipation(self):
        """polish_animation with anticipation."""
        self.skipUnless(POLISH_AVAILABLE, "Polish module not available")

        anim = create_test_animation(frame_count=3)
        original_count = anim.frame_count

        result = polish_animation(anim, add_antic=True)

        self.assertGreater(result.frame_count, original_count)

    def test_polish_animation_with_follow_through(self):
        """polish_animation with follow-through."""
        self.skipUnless(POLISH_AVAILABLE, "Polish module not available")

        anim = create_test_animation(frame_count=3)
        original_count = anim.frame_count

        result = polish_animation(anim, add_follow=True)

        self.assertGreater(result.frame_count, original_count)

    def test_polish_animation_all_options(self):
        """polish_animation with all options enabled."""
        self.skipUnless(POLISH_AVAILABLE, "Polish module not available")

        anim = create_test_animation(frame_count=4)

        result = polish_animation(anim, add_blur=True, add_antic=True,
                                  add_follow=True, optimize=True)

        self.assertIsNotNone(result)
        self.assertGreater(result.frame_count, 0)

    def test_polish_animation_no_optimize(self):
        """polish_animation without optimization."""
        self.skipUnless(POLISH_AVAILABLE, "Polish module not available")

        anim = create_test_animation(frame_count=3)

        result = polish_animation(anim, optimize=False)

        self.assertIsNotNone(result)


class TestDeterminism(TestCase):
    """Tests for deterministic output."""

    def test_smear_frame_deterministic(self):
        """Smear frame creation is deterministic."""
        self.skipUnless(POLISH_AVAILABLE, "Polish module not available")

        frame1 = Canvas(16, 16)
        frame2 = Canvas(16, 16)
        frame1.fill_rect(2, 2, 4, 4, (255, 0, 0, 255))
        frame2.fill_rect(10, 10, 4, 4, (255, 0, 0, 255))

        result1 = create_smear_frame(frame1, frame2, intensity=0.5)
        result2 = create_smear_frame(frame1, frame2, intensity=0.5)

        self.assertCanvasEqual(result1, result2)

    def test_motion_blur_deterministic(self):
        """Motion blur is deterministic."""
        self.skipUnless(POLISH_AVAILABLE, "Polish module not available")

        anim = create_test_animation(frame_count=3)

        result1 = add_motion_blur(anim, blur_frames=1)
        result2 = add_motion_blur(anim, blur_frames=1)

        self.assertEqual(result1.frame_count, result2.frame_count)

        for i in range(result1.frame_count):
            self.assertCanvasEqual(result1.keyframes[i].frame, result2.keyframes[i].frame)

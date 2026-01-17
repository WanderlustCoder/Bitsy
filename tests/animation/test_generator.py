"""Tests for animation generator."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests.framework import TestCase
from animation.generator import (
    AnimationType,
    IdleStyle,
    AnimationConfig,
    AnimationSet,
    generate_idle,
    generate_idle_blink,
    generate_transition,
    generate_animation_set,
    list_animation_types,
    list_idle_styles,
    get_animation,
)
from animation.cycles import AnimationCycle


class TestAnimationType(TestCase):
    """Tests for AnimationType enum."""

    def test_generator_animation_types_exist(self):
        """All expected animation types exist."""
        expected = [
            "idle",
            "idle_breathe",
            "idle_blink",
            "idle_look",
            "walk",
            "run",
            "attack_slash",
            "attack_stab",
            "attack_overhead",
            "jump",
            "fall",
            "land",
            "hurt",
            "death",
            "transition",
        ]
        self.assertEqual([anim.value for anim in AnimationType], expected)


class TestIdleStyle(TestCase):
    """Tests for IdleStyle enum."""

    def test_generator_idle_styles_exist(self):
        """All expected idle styles exist."""
        expected = ["subtle", "relaxed", "alert", "tired", "excited"]
        self.assertEqual([style.value for style in IdleStyle], expected)


class TestAnimationConfig(TestCase):
    """Tests for AnimationConfig."""

    def test_generator_config_defaults(self):
        """AnimationConfig has sensible defaults."""
        config = AnimationConfig()
        self.assertEqual(config.fps, 12)
        self.assertEqual(config.frame_count, 8)
        self.assertEqual(config.movement_scale, 1.0)
        self.assertEqual(config.rotation_scale, 1.0)
        self.assertEqual(config.weight, 1.0)
        self.assertEqual(config.energy, 1.0)
        self.assertEqual(config.age_factor, 1.0)
        self.assertIsNone(config.seed)

    def test_generator_config_custom(self):
        """AnimationConfig accepts custom values."""
        config = AnimationConfig(
            fps=24,
            frame_count=16,
            movement_scale=2.0,
            rotation_scale=0.5,
            weight=1.2,
            energy=0.8,
            age_factor=0.9,
            seed=7,
        )
        self.assertEqual(config.fps, 24)
        self.assertEqual(config.frame_count, 16)
        self.assertEqual(config.movement_scale, 2.0)
        self.assertEqual(config.rotation_scale, 0.5)
        self.assertEqual(config.weight, 1.2)
        self.assertEqual(config.energy, 0.8)
        self.assertEqual(config.age_factor, 0.9)
        self.assertEqual(config.seed, 7)


class TestGenerateIdle(TestCase):
    """Tests for generate_idle function."""

    def test_generator_idle_default(self):
        """generate_idle creates animation cycle."""
        cycle = generate_idle()
        self.assertIsInstance(cycle, AnimationCycle)
        self.assertTrue(cycle.loop)
        self.assertGreater(len(cycle.frames), 0)

    def test_generator_idle_styles(self):
        """generate_idle works with all styles."""
        for style in IdleStyle:
            cycle = generate_idle(style=style, config=AnimationConfig(seed=1))
            self.assertIsInstance(cycle, AnimationCycle)
            self.assertIn(style.value, cycle.name)

    def test_generator_idle_config(self):
        """generate_idle respects config."""
        config = AnimationConfig(frame_count=4, fps=8)
        cycle = generate_idle(config=config)
        self.assertEqual(len(cycle.frames), 4)
        self.assertEqual(cycle.fps, 8)

    def test_generator_idle_config_scales(self):
        """generate_idle applies movement and rotation scaling."""
        base_config = AnimationConfig(seed=3)
        scaled_config = AnimationConfig(seed=3, movement_scale=2.0, rotation_scale=0.5)
        base_cycle = generate_idle(config=base_config)
        scaled_cycle = generate_idle(config=scaled_config)
        self.assertEqual(len(base_cycle.frames), len(scaled_cycle.frames))
        base_frame = base_cycle.frames[0]
        scaled_frame = scaled_cycle.frames[0]
        self.assertEqual(
            scaled_frame.root_offset[1],
            base_frame.root_offset[1] * scaled_config.movement_scale,
        )
        self.assertEqual(
            scaled_frame.bone_rotations['torso'],
            base_frame.bone_rotations['torso'] * scaled_config.rotation_scale,
        )

    def test_generator_idle_deterministic(self):
        """generate_idle is deterministic with seed."""
        config1 = AnimationConfig(seed=42)
        config2 = AnimationConfig(seed=42)
        cycle1 = generate_idle(config=config1)
        cycle2 = generate_idle(config=config2)
        self.assertEqual(len(cycle1.frames), len(cycle2.frames))
        self.assertEqual(cycle1.frames[0].bone_rotations, cycle2.frames[0].bone_rotations)
        self.assertEqual(cycle1.frames[0].root_offset, cycle2.frames[0].root_offset)


class TestGenerateIdleBlink(TestCase):
    """Tests for generate_idle_blink function."""

    def test_generator_idle_blink(self):
        """generate_idle_blink creates blink animation."""
        cycle = generate_idle_blink()
        self.assertIsInstance(cycle, AnimationCycle)
        self.assertFalse(cycle.loop)  # Blink doesn't loop
        self.assertEqual(cycle.name, "idle_blink")
        self.assertEqual(len(cycle.frames), 4)
        self.assertEqual(cycle.frames[0].bone_offsets['left_eye'], (0, 0))
        self.assertEqual(cycle.frames[1].bone_offsets['left_eye'], (0, 0.5))
        self.assertEqual(cycle.frames[2].bone_offsets['left_eye'], (0, 1))
        self.assertEqual(cycle.frames[3].bone_offsets['left_eye'], (0, 0))


class TestGenerateTransition(TestCase):
    """Tests for generate_transition function."""

    def test_generator_transition_idle_to_walk(self):
        """Transition from idle to walk."""
        config = AnimationConfig(frame_count=2, fps=10)
        cycle = generate_transition(AnimationType.IDLE, AnimationType.WALK, config)
        self.assertIsInstance(cycle, AnimationCycle)
        self.assertFalse(cycle.loop)
        self.assertIn("idle", cycle.name)
        self.assertIn("walk", cycle.name)
        self.assertEqual(len(cycle.frames), 2)
        self.assertEqual(cycle.frames[0].bone_rotations['left_arm'], 5)
        self.assertEqual(cycle.frames[1].bone_rotations['left_arm'], 15)
        self.assertEqual(cycle.frames[0].root_offset, (0, 0))

    def test_generator_transition_walk_to_run(self):
        """Transition from walk to run."""
        config = AnimationConfig(frame_count=3)
        cycle = generate_transition(AnimationType.WALK, AnimationType.RUN, config)
        self.assertIsInstance(cycle, AnimationCycle)
        self.assertEqual(len(cycle.frames), 3)
        self.assertEqual(cycle.frames[-1].bone_rotations['torso'], 5)


class TestGenerateAnimationSet(TestCase):
    """Tests for generate_animation_set function."""

    def test_generator_generate_set_default(self):
        """generate_animation_set creates complete set."""
        anim_set = generate_animation_set()
        self.assertIsInstance(anim_set, AnimationSet)
        self.assertIsInstance(anim_set.idle, AnimationCycle)
        self.assertIsInstance(anim_set.walk, AnimationCycle)
        self.assertIsInstance(anim_set.run, AnimationCycle)
        self.assertIsInstance(anim_set.attack, AnimationCycle)
        self.assertIsInstance(anim_set.jump, AnimationCycle)
        self.assertIsInstance(anim_set.hurt, AnimationCycle)
        self.assertIsInstance(anim_set.death, AnimationCycle)

    def test_generator_generate_set_with_transitions(self):
        """generate_animation_set includes transitions."""
        anim_set = generate_animation_set(include_transitions=True)
        self.assertIn('idle_to_walk', anim_set.transitions)
        self.assertIn('walk_to_run', anim_set.transitions)
        self.assertIn('idle_to_attack', anim_set.transitions)

    def test_generator_generate_set_without_transitions(self):
        """generate_animation_set can skip transitions."""
        anim_set = generate_animation_set(include_transitions=False)
        self.assertEqual(len(anim_set.transitions), 0)

    def test_generator_generate_set_scaling(self):
        """generate_animation_set applies config scaling."""
        default_set = generate_animation_set()
        config = AnimationConfig(rotation_scale=2.0, movement_scale=0.5)
        scaled_set = generate_animation_set(config=config)
        self.assertEqual(
            scaled_set.walk.frames[0].bone_rotations['torso'],
            default_set.walk.frames[0].bone_rotations['torso'] * config.rotation_scale,
        )
        self.assertEqual(
            scaled_set.walk.frames[1].root_offset[1],
            default_set.walk.frames[1].root_offset[1] * config.movement_scale,
        )

    def test_generator_get_all_returns_dict(self):
        """AnimationSet.get_all returns dictionary."""
        anim_set = generate_animation_set()
        all_anims = anim_set.get_all()
        self.assertIsInstance(all_anims, dict)
        self.assertIn('idle', all_anims)
        self.assertIn('walk', all_anims)
        self.assertIn('run', all_anims)
        self.assertIn('attack', all_anims)


class TestListFunctions(TestCase):
    """Tests for list functions."""

    def test_generator_list_animation_types(self):
        """list_animation_types returns list."""
        types = list_animation_types()
        self.assertIsInstance(types, list)
        self.assertEqual(types, [anim.value for anim in AnimationType])

    def test_generator_list_idle_styles(self):
        """list_idle_styles returns list."""
        styles = list_idle_styles()
        self.assertIsInstance(styles, list)
        self.assertEqual(styles, [style.value for style in IdleStyle])


class TestGetAnimation(TestCase):
    """Tests for get_animation function."""

    def test_generator_get_animation_by_string(self):
        """get_animation works with string type."""
        cycle = get_animation('walk')
        self.assertIsInstance(cycle, AnimationCycle)

    def test_generator_get_animation_by_enum(self):
        """get_animation works with enum type."""
        cycle = get_animation(AnimationType.RUN)
        self.assertIsInstance(cycle, AnimationCycle)

    def test_generator_get_animation_with_config(self):
        """get_animation applies config."""
        default_cycle = get_animation('walk')
        config = AnimationConfig(movement_scale=0.5, rotation_scale=2.0)
        cycle = get_animation('walk', config=config)
        self.assertIsInstance(cycle, AnimationCycle)
        self.assertEqual(
            cycle.frames[1].root_offset[1],
            default_cycle.frames[1].root_offset[1] * config.movement_scale,
        )

    def test_generator_get_animation_idle_breathe(self):
        """get_animation supports idle breathe variant."""
        cycle = get_animation(AnimationType.IDLE_BREATHE)
        self.assertIsInstance(cycle, AnimationCycle)
        self.assertIn("idle_relaxed", cycle.name)

    def test_generator_get_animation_invalid_type(self):
        """get_animation raises for invalid type."""
        with self.assertRaises(ValueError):
            get_animation('not_a_real_animation')

    def test_generator_get_animation_unsupported_type(self):
        """get_animation raises for unsupported enum types."""
        for anim_type in (AnimationType.IDLE_BLINK, AnimationType.IDLE_LOOK,
                          AnimationType.FALL, AnimationType.LAND,
                          AnimationType.TRANSITION):
            with self.assertRaises(ValueError):
                get_animation(anim_type)

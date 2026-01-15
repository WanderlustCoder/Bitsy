"""Tests for Character class and CharacterBuilder."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests.framework import TestCase
from core.canvas import Canvas
from core.style import Style
from characters import (
    Character,
    CharacterBuilder,
    CharacterParts,
    CharacterPalettes,
    CharacterLayout,
    build_character,
)


class TestCharacterBuilder(TestCase):
    """Tests for CharacterBuilder fluent API."""

    def test_create_default(self):
        """CharacterBuilder creates character with defaults."""
        char = CharacterBuilder().build()
        self.assertIsInstance(char, Character)

    def test_builder_returns_self(self):
        """All builder methods return self for chaining."""
        builder = CharacterBuilder()

        self.assertIs(builder.style('chibi'), builder)
        self.assertIs(builder.head('round'), builder)
        self.assertIs(builder.body('chibi'), builder)
        self.assertIs(builder.hair('spiky'), builder)
        self.assertIs(builder.eyes('large'), builder)
        self.assertIs(builder.skin('warm'), builder)
        self.assertIs(builder.outfit('blue'), builder)
        self.assertIs(builder.expression('happy'), builder)
        self.assertIs(builder.size(64, 64), builder)

    def test_method_chaining(self):
        """Builder supports full method chaining."""
        char = (CharacterBuilder()
            .style('chibi')
            .head('round')
            .body('simple')
            .hair('spiky', color='brown')
            .eyes('large', color='blue')
            .skin('warm')
            .outfit('red')
            .build())

        self.assertIsInstance(char, Character)

    def test_custom_size(self):
        """Builder respects custom size."""
        char = CharacterBuilder(width=64, height=64).build()
        self.assertEqual(char.width, 64)
        self.assertEqual(char.height, 64)

    def test_size_method(self):
        """size() method changes dimensions."""
        char = CharacterBuilder().size(48, 48).build()
        self.assertEqual(char.width, 48)
        self.assertEqual(char.height, 48)

    def test_head_types(self):
        """Builder accepts all head types."""
        head_types = ['round', 'oval', 'square', 'chibi', 'triangle', 'heart']
        for head_type in head_types:
            char = CharacterBuilder().head(head_type).build()
            self.assertIsInstance(char, Character)

    def test_body_types(self):
        """Builder accepts all body types."""
        body_types = ['chibi', 'simple', 'muscular', 'slim']
        for body_type in body_types:
            char = CharacterBuilder().body(body_type).build()
            self.assertIsInstance(char, Character)

    def test_hair_types(self):
        """Builder accepts all hair types."""
        hair_types = ['fluffy', 'spiky', 'long', 'short', 'bald', 'ponytail', 'twintails']
        for hair_type in hair_types:
            char = CharacterBuilder().hair(hair_type).build()
            self.assertIsInstance(char, Character)

    def test_hair_colors(self):
        """Builder accepts all hair colors."""
        colors = ['brown', 'lavender', 'pink', 'blue', 'red', 'blonde', 'black', 'white', 'green', 'purple']
        for color in colors:
            char = CharacterBuilder().hair('spiky', color=color).build()
            self.assertIsInstance(char, Character)

    def test_eye_types(self):
        """Builder accepts all eye types."""
        eye_types = ['simple', 'round', 'large', 'sparkle', 'closed', 'angry', 'sad']
        for eye_type in eye_types:
            char = CharacterBuilder().eyes(eye_type).build()
            self.assertIsInstance(char, Character)

    def test_eye_colors(self):
        """Builder accepts all eye colors."""
        colors = ['blue', 'green', 'brown', 'purple', 'red', 'gold']
        for color in colors:
            char = CharacterBuilder().eyes('large', color=color).build()
            self.assertIsInstance(char, Character)

    def test_expressions(self):
        """Builder accepts all expressions."""
        expressions = ['neutral', 'happy', 'sad', 'angry']
        for expr in expressions:
            char = CharacterBuilder().eyes('large', expression=expr).build()
            self.assertIsInstance(char, Character)

    def test_skin_palettes(self):
        """Builder accepts all skin palettes."""
        palettes = ['warm', 'cool', 'pale', 'tan', 'dark', 'olive']
        for palette in palettes:
            char = CharacterBuilder().skin(palette).build()
            self.assertIsInstance(char, Character)

    def test_outfit_colors(self):
        """Builder accepts all outfit colors."""
        colors = ['blue', 'red', 'green', 'purple', 'yellow', 'orange', 'pink', 'black', 'white', 'gold']
        for color in colors:
            char = CharacterBuilder().outfit(color).build()
            self.assertIsInstance(char, Character)

    def test_randomize(self):
        """randomize() creates varied characters."""
        builder = CharacterBuilder(seed=42)
        char1 = builder.randomize().build()

        builder2 = CharacterBuilder(seed=99)
        char2 = builder2.randomize().build()

        # Both should be valid characters
        self.assertIsInstance(char1, Character)
        self.assertIsInstance(char2, Character)

    def test_determinism_with_seed(self):
        """Same seed produces identical characters."""
        char1 = CharacterBuilder(seed=42).randomize().build()
        char2 = CharacterBuilder(seed=42).randomize().build()

        canvas1 = char1.render()
        canvas2 = char2.render()

        self.assertCanvasEqual(canvas1, canvas2)

    def test_different_seeds_differ(self):
        """Different seeds produce different characters."""
        char1 = CharacterBuilder(seed=42).randomize().build()
        char2 = CharacterBuilder(seed=99).randomize().build()

        canvas1 = char1.render()
        canvas2 = char2.render()

        # Canvases should be different
        pixels_differ = False
        for y in range(canvas1.height):
            for x in range(canvas1.width):
                if canvas1.get_pixel(x, y) != canvas2.get_pixel(x, y):
                    pixels_differ = True
                    break
            if pixels_differ:
                break

        self.assertTrue(pixels_differ)

    def test_render_shortcut(self):
        """render() method builds and renders in one call."""
        canvas = CharacterBuilder().render()
        self.assertIsInstance(canvas, Canvas)


class TestCharacter(TestCase):
    """Tests for Character class."""

    def test_render_returns_canvas(self):
        """render() returns a Canvas."""
        char = CharacterBuilder().build()
        canvas = char.render()
        self.assertIsInstance(canvas, Canvas)

    def test_render_correct_size(self):
        """render() produces correct size canvas."""
        char = CharacterBuilder(width=32, height=32).build()
        canvas = char.render()
        self.assertCanvasSize(canvas, 32, 32)

    def test_render_not_empty(self):
        """render() produces non-empty canvas."""
        char = CharacterBuilder().build()
        canvas = char.render()
        self.assertCanvasNotEmpty(canvas)

    def test_render_onto_existing_canvas(self):
        """render() can draw onto existing canvas."""
        char = CharacterBuilder(width=32, height=32).build()
        canvas = Canvas(64, 64, (0, 0, 0, 0))
        result = char.render(canvas)
        self.assertIs(result, canvas)

    def test_with_expression_returns_new_character(self):
        """with_expression() returns new Character instance."""
        char = CharacterBuilder().build()
        happy_char = char.with_expression('happy')

        self.assertIsInstance(happy_char, Character)
        self.assertIsNot(char, happy_char)

    def test_with_expression_changes_expression(self):
        """with_expression() changes the expression."""
        char = CharacterBuilder().eyes('large', expression='neutral').build()
        self.assertEqual(char.expression, 'neutral')

        happy_char = char.with_expression('happy')
        self.assertEqual(happy_char.expression, 'happy')

    def test_with_expression_original_unchanged(self):
        """with_expression() doesn't modify original."""
        char = CharacterBuilder().eyes('large', expression='neutral').build()
        happy_char = char.with_expression('happy')

        self.assertEqual(char.expression, 'neutral')

    def test_with_pose_returns_new_character(self):
        """with_pose() returns new Character instance."""
        char = CharacterBuilder().build()
        posed_char = char.with_pose('idle')

        self.assertIsInstance(posed_char, Character)
        self.assertIsNot(char, posed_char)

    def test_animate_returns_animation(self):
        """animate() returns an Animation."""
        from core.animation import Animation
        char = CharacterBuilder().build()
        anim = char.animate('idle')
        self.assertIsInstance(anim, Animation)

    def test_animate_idle(self):
        """animate('idle') creates idle animation."""
        char = CharacterBuilder().build()
        anim = char.animate('idle')
        self.assertGreater(anim.frame_count, 0)

    def test_animate_walk(self):
        """animate('walk') creates walk animation."""
        char = CharacterBuilder().build()
        anim = char.animate('walk')
        self.assertGreater(anim.frame_count, 0)

    def test_copy(self):
        """copy() creates independent copy."""
        char = CharacterBuilder().build()
        char_copy = char.copy()

        self.assertIsInstance(char_copy, Character)
        self.assertIsNot(char, char_copy)

    def test_repr(self):
        """__repr__ returns readable string."""
        char = CharacterBuilder().head('round').body('chibi').build()
        repr_str = repr(char)
        self.assertIn('Character', repr_str)

    def test_width_property(self):
        """width property returns correct value."""
        char = CharacterBuilder(width=48, height=32).build()
        self.assertEqual(char.width, 48)

    def test_height_property(self):
        """height property returns correct value."""
        char = CharacterBuilder(width=32, height=48).build()
        self.assertEqual(char.height, 48)

    def test_style_property(self):
        """style property returns Style object."""
        char = CharacterBuilder().style('chibi').build()
        self.assertIsInstance(char.style, Style)


class TestCharacterLayout(TestCase):
    """Tests for CharacterLayout positioning."""

    def test_default_layout(self):
        """Default layout has sensible values."""
        layout = CharacterLayout()
        self.assertEqual(layout.width, 32)
        self.assertEqual(layout.height, 32)

    def test_get_head_rect(self):
        """get_head_rect returns tuple of 4 values."""
        layout = CharacterLayout(width=32, height=32)
        rect = layout.get_head_rect()
        self.assertEqual(len(rect), 4)

    def test_get_body_rect(self):
        """get_body_rect returns tuple of 4 values."""
        layout = CharacterLayout(width=32, height=32)
        rect = layout.get_body_rect()
        self.assertEqual(len(rect), 4)

    def test_get_hair_rect(self):
        """get_hair_rect returns tuple of 4 values."""
        layout = CharacterLayout(width=32, height=32)
        rect = layout.get_hair_rect()
        self.assertEqual(len(rect), 4)

    def test_for_style_chibi(self):
        """for_style creates layout for chibi style."""
        style = Style.chibi()
        layout = CharacterLayout.for_style(style)
        self.assertIsInstance(layout, CharacterLayout)

    def test_for_style_custom_size(self):
        """for_style respects custom size."""
        style = Style.chibi()
        layout = CharacterLayout.for_style(style, width=64, height=64)
        self.assertEqual(layout.width, 64)
        self.assertEqual(layout.height, 64)


class TestBuildCharacterFunction(TestCase):
    """Tests for build_character convenience function."""

    def test_build_character_default(self):
        """build_character() creates character with defaults."""
        char = build_character()
        self.assertIsInstance(char, Character)

    def test_build_character_with_parts(self):
        """build_character() accepts part specifications."""
        char = build_character(
            head='round',
            body='chibi',
            hair='spiky',
            eyes='large'
        )
        self.assertIsInstance(char, Character)

    def test_build_character_with_colors(self):
        """build_character() accepts color specifications."""
        char = build_character(
            hair='spiky',
            hair_color='brown',
            eyes='large',
            eye_color='blue',
            outfit='red'
        )
        self.assertIsInstance(char, Character)

    def test_build_character_with_size(self):
        """build_character() accepts size."""
        char = build_character(width=64, height=64)
        self.assertEqual(char.width, 64)
        self.assertEqual(char.height, 64)

    def test_build_character_with_seed(self):
        """build_character() accepts seed for determinism."""
        char1 = build_character(seed=42)
        char2 = build_character(seed=42)

        canvas1 = char1.render()
        canvas2 = char2.render()

        self.assertCanvasEqual(canvas1, canvas2)

"""Tests for CharacterBuilder."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests.framework import TestCase
from core.canvas import Canvas
from characters import Character, CharacterBuilder


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

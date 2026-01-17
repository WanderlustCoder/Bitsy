"""Tests for ML style learning module."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core import Canvas
from ml import (
    SpriteFeatures,
    extract_features,
    color_distance,
    StyleModel,
    style_similarity,
    feature_similarity,
    color_palette_similarity,
    structural_similarity,
    batch_similarity,
    generate_variations,
    generate_diverse_set,
    StyleTransfer,
)


def create_test_sprite(pattern='solid', color=(255, 0, 0, 255)):
    """Create a simple test sprite."""
    canvas = Canvas(8, 8)

    if pattern == 'solid':
        for y in range(2, 6):
            for x in range(2, 6):
                canvas.set_pixel(x, y, color)

    elif pattern == 'symmetric':
        for y in range(8):
            for x in range(4):
                if (x + y) % 2 == 0:
                    canvas.set_pixel(x, y, color)
                    canvas.set_pixel(7 - x, y, color)

    elif pattern == 'random':
        import random
        random.seed(42)
        for y in range(8):
            for x in range(8):
                if random.random() < 0.3:
                    canvas.set_pixel(x, y, color)

    return canvas


class TestFeatures:
    """Tests for feature extraction."""

    def test_extract_features_basic(self):
        """Test basic feature extraction."""
        sprite = create_test_sprite('solid')
        features = extract_features(sprite)

        assert features.width == 8
        assert features.height == 8
        assert features.num_colors == 1
        assert features.pixel_density > 0

    def test_extract_features_colors(self):
        """Test color-related features."""
        sprite = create_test_sprite('solid', (255, 128, 0, 255))
        features = extract_features(sprite)

        assert features.avg_brightness > 0
        assert len(features.dominant_colors) > 0
        assert (255, 128, 0, 255) in features.dominant_colors

    def test_extract_features_symmetry(self):
        """Test symmetry detection."""
        symmetric = create_test_sprite('symmetric')
        features = extract_features(symmetric)

        # Should have high horizontal symmetry
        assert features.horizontal_symmetry > 0.8

    def test_feature_to_vector(self):
        """Test converting features to vector."""
        sprite = create_test_sprite('solid')
        features = extract_features(sprite)
        vector = features.to_vector()

        assert isinstance(vector, list)
        assert len(vector) > 0
        assert all(isinstance(v, float) for v in vector)

    def test_color_distance(self):
        """Test color distance calculation."""
        c1 = (255, 0, 0, 255)
        c2 = (255, 0, 0, 255)
        assert color_distance(c1, c2) == 0.0

        c3 = (0, 0, 0, 255)
        c4 = (255, 255, 255, 255)
        assert color_distance(c3, c4) == 1.0

    def test_quadrant_densities(self):
        """Test quadrant density calculation."""
        sprite = create_test_sprite('solid')
        features = extract_features(sprite)

        assert len(features.quadrant_densities) == 4
        # Center sprite should have density in all quadrants
        assert all(d > 0 for d in features.quadrant_densities)


class TestStyleModel:
    """Tests for StyleModel."""

    def test_create_model(self):
        """Test creating a style model."""
        model = StyleModel()
        assert model.num_examples() == 0
        assert not model.is_fitted()

    def test_add_example(self):
        """Test adding examples."""
        model = StyleModel()
        sprite = create_test_sprite('solid')
        model.add_example(sprite)

        assert model.num_examples() == 1

    def test_fit_model(self):
        """Test fitting the model."""
        model = StyleModel()
        model.add_example(create_test_sprite('solid'))
        model.add_example(create_test_sprite('symmetric'))
        model.fit()

        assert model.is_fitted()
        assert len(model.stats.feature_means) > 0
        assert len(model.stats.palette) > 0

    def test_fit_requires_examples(self):
        """Test that fit requires examples."""
        model = StyleModel()
        try:
            model.fit()
            assert False, "Should raise ValueError"
        except ValueError:
            pass

    def test_generate(self):
        """Test generating sprites."""
        model = StyleModel()
        model.add_example(create_test_sprite('solid'))
        model.add_example(create_test_sprite('symmetric'))
        model.fit()

        sprite = model.generate(8, 8, seed=42)

        assert isinstance(sprite, Canvas)
        assert sprite.width == 8
        assert sprite.height == 8

    def test_generate_requires_fit(self):
        """Test that generate requires fitting first."""
        model = StyleModel()
        model.add_example(create_test_sprite('solid'))

        try:
            model.generate(8, 8)
            assert False, "Should raise ValueError"
        except ValueError:
            pass

    def test_generate_deterministic(self):
        """Test deterministic generation with seed."""
        model = StyleModel()
        model.add_example(create_test_sprite('solid'))
        model.fit()

        s1 = model.generate(8, 8, seed=42)
        s2 = model.generate(8, 8, seed=42)

        # Same seed should produce same result
        for y in range(8):
            for x in range(8):
                assert s1.get_pixel(x, y) == s2.get_pixel(x, y)


class TestSimilarity:
    """Tests for similarity functions."""

    def test_style_similarity_identical(self):
        """Test similarity of identical sprites."""
        sprite = create_test_sprite('solid')
        sim = style_similarity(sprite, sprite)

        assert sim == 1.0

    def test_style_similarity_different(self):
        """Test similarity of different sprites."""
        s1 = create_test_sprite('solid', (255, 0, 0, 255))
        s2 = create_test_sprite('random', (0, 0, 255, 255))

        sim = style_similarity(s1, s2)

        assert 0.0 <= sim <= 1.0
        assert sim < 1.0  # Should not be identical

    def test_color_palette_similarity(self):
        """Test color palette similarity."""
        s1 = create_test_sprite('solid', (255, 0, 0, 255))
        s2 = create_test_sprite('solid', (255, 0, 0, 255))

        sim = color_palette_similarity(s1, s2)
        assert sim == 1.0

    def test_structural_similarity(self):
        """Test structural similarity."""
        s1 = create_test_sprite('solid')
        s2 = create_test_sprite('solid')

        sim = structural_similarity(s1, s2)
        assert sim == 1.0

    def test_batch_similarity(self):
        """Test batch similarity search."""
        target = create_test_sprite('solid', (255, 0, 0, 255))
        candidates = [
            create_test_sprite('solid', (255, 0, 0, 255)),
            create_test_sprite('random', (0, 255, 0, 255)),
            create_test_sprite('symmetric', (0, 0, 255, 255)),
        ]

        results = batch_similarity(target, candidates, top_k=2)

        assert len(results) == 2
        assert results[0][0] == 0  # First candidate should be most similar
        assert results[0][1] > results[1][1]  # Sorted by similarity


class TestGenerator:
    """Tests for generation utilities."""

    def test_generate_variations(self):
        """Test generating variations."""
        model = StyleModel()
        model.add_example(create_test_sprite('solid'))
        model.fit()

        variations = generate_variations(model, count=3, width=8, height=8)

        assert len(variations) == 3
        assert all(isinstance(v, Canvas) for v in variations)

    def test_generate_diverse_set(self):
        """Test generating diverse set."""
        model = StyleModel()
        model.add_example(create_test_sprite('solid'))
        model.add_example(create_test_sprite('random'))
        model.fit()

        sprites = generate_diverse_set(
            model, count=3, diversity_threshold=0.1,
            width=8, height=8, max_attempts=100
        )

        assert len(sprites) > 0
        assert len(sprites) <= 3

    def test_style_transfer(self):
        """Test style transfer."""
        source = create_test_sprite('solid', (255, 0, 0, 255))
        target = create_test_sprite('symmetric', (0, 255, 0, 255))

        transfer = StyleTransfer(source)
        result = transfer.transfer(target, strength=0.5)

        assert isinstance(result, Canvas)
        assert result.width == target.width


class TestEdgeCases:
    """Tests for edge cases."""

    def test_empty_sprite(self):
        """Test handling empty sprite."""
        empty = Canvas(8, 8)
        features = extract_features(empty)

        assert features.num_colors == 0
        assert features.pixel_density == 0.0

    def test_single_pixel(self):
        """Test handling single pixel sprite."""
        single = Canvas(8, 8)
        single.set_pixel(4, 4, (255, 0, 0, 255))

        features = extract_features(single)

        assert features.num_colors == 1
        assert features.pixel_density > 0


if __name__ == '__main__':
    import traceback

    test_classes = [
        TestFeatures,
        TestStyleModel,
        TestSimilarity,
        TestGenerator,
        TestEdgeCases,
    ]

    passed = 0
    failed = 0
    errors = []

    for test_class in test_classes:
        instance = test_class()
        for name in dir(instance):
            if name.startswith('test_'):
                try:
                    getattr(instance, name)()
                    passed += 1
                    print(f"  ✓ {test_class.__name__}.{name}")
                except Exception as e:
                    failed += 1
                    errors.append((test_class.__name__, name, e, traceback.format_exc()))
                    print(f"  ✗ {test_class.__name__}.{name}: {e}")

    print(f"\n{'='*60}")
    print(f"Results: {passed} passed, {failed} failed")

    if errors:
        print(f"\nFailed tests:")
        for cls_name, test_name, error, tb in errors:
            print(f"\n{cls_name}.{test_name}:")
            print(tb)

    exit(0 if failed == 0 else 1)

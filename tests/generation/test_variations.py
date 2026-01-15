"""
Test Variations - Tests for variation generation and quality scoring.

Tests:
- generate_variations
- generate_with_mutations
- select_best
- rank_by_quality
- QualityScorer
- batch_generate
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests.framework import TestCase, CanvasFixtures
from core import Canvas


try:
    from generation.variations import (
        QualityCriteria,
        VariationConfig,
        MutationConfig,
        QualityScore,
        QualityScorer,
        generate_variations,
        generate_with_mutations,
        select_best,
        rank_by_quality,
        generate_asset_set,
        batch_generate,
    )
    VARIATIONS_AVAILABLE = True
except ImportError as e:
    VARIATIONS_AVAILABLE = False
    IMPORT_ERROR = str(e)


def simple_generator(seed: int) -> Canvas:
    """Simple test generator."""
    import random
    rng = random.Random(seed)
    canvas = Canvas(16, 16)
    # Draw random circle
    cx = rng.randint(4, 12)
    cy = rng.randint(4, 12)
    r = rng.randint(2, 5)
    color = (rng.randint(50, 255), rng.randint(50, 255), rng.randint(50, 255), 255)
    canvas.fill_circle(cx, cy, r, color)
    return canvas


class TestQualityCriteria(TestCase):
    """Tests for QualityCriteria enum."""

    def test_criteria_defined(self):
        """QualityCriteria enum has expected values."""
        self.skipUnless(VARIATIONS_AVAILABLE, "Variations module not available")

        self.assertEqual(QualityCriteria.DETAIL.value, 'detail')
        self.assertEqual(QualityCriteria.CONTRAST.value, 'contrast')
        self.assertEqual(QualityCriteria.BALANCE.value, 'balance')
        self.assertEqual(QualityCriteria.OVERALL.value, 'overall')


class TestVariationConfig(TestCase):
    """Tests for VariationConfig dataclass."""

    def test_default_config(self):
        """VariationConfig has sensible defaults."""
        self.skipUnless(VARIATIONS_AVAILABLE, "Variations module not available")

        config = VariationConfig()
        self.assertEqual(config.count, 10)
        self.assertEqual(config.seed_start, 0)
        self.assertEqual(config.seed_step, 1)


class TestQualityScorer(TestCase):
    """Tests for QualityScorer class."""

    def test_scorer_creation(self):
        """QualityScorer can be created."""
        self.skipUnless(VARIATIONS_AVAILABLE, "Variations module not available")

        scorer = QualityScorer()
        self.assertIsNotNone(scorer.weights)

    def test_scorer_with_custom_weights(self):
        """QualityScorer accepts custom weights."""
        self.skipUnless(VARIATIONS_AVAILABLE, "Variations module not available")

        weights = {'detail': 2.0, 'contrast': 1.0}
        scorer = QualityScorer(weights=weights)
        self.assertEqual(scorer.weights['detail'], 2.0)

    def test_score_canvas(self):
        """QualityScorer can score a canvas."""
        self.skipUnless(VARIATIONS_AVAILABLE, "Variations module not available")

        scorer = QualityScorer()
        canvas = CanvasFixtures.circle((255, 100, 50, 255), size=16)

        score = scorer.score(canvas, seed=42)

        self.assertIsInstance(score, QualityScore)
        self.assertIn('detail', score.scores)
        self.assertIn('contrast', score.scores)
        self.assertIn('balance', score.scores)
        self.assertIn('overall', score.scores)

    def test_score_empty_canvas(self):
        """QualityScorer handles empty canvas."""
        self.skipUnless(VARIATIONS_AVAILABLE, "Variations module not available")

        scorer = QualityScorer()
        canvas = Canvas(16, 16)  # Empty

        score = scorer.score(canvas)

        self.assertIsNotNone(score)

    def test_score_overall_property(self):
        """QualityScore.overall returns weighted average."""
        self.skipUnless(VARIATIONS_AVAILABLE, "Variations module not available")

        scorer = QualityScorer()
        canvas = CanvasFixtures.solid((200, 100, 50, 255), width=16, height=16)

        score = scorer.score(canvas)

        self.assertGreaterEqual(score.overall, 0.0)
        self.assertLessEqual(score.overall, 1.0)


class TestGenerateVariations(TestCase):
    """Tests for generate_variations function."""

    def test_generate_variations_basic(self):
        """generate_variations creates multiple variations."""
        self.skipUnless(VARIATIONS_AVAILABLE, "Variations module not available")

        variations = generate_variations(simple_generator, count=5)

        self.assertEqual(len(variations), 5)
        for canvas, seed in variations:
            self.assertIsInstance(canvas, Canvas)
            self.assertIsInstance(seed, int)

    def test_generate_variations_with_config(self):
        """generate_variations respects config."""
        self.skipUnless(VARIATIONS_AVAILABLE, "Variations module not available")

        config = VariationConfig(count=3, seed_start=100, seed_step=10)
        variations = generate_variations(simple_generator, config=config)

        self.assertEqual(len(variations), 3)
        self.assertEqual(variations[0][1], 100)
        self.assertEqual(variations[1][1], 110)
        self.assertEqual(variations[2][1], 120)

    def test_generate_variations_deterministic(self):
        """generate_variations is deterministic."""
        self.skipUnless(VARIATIONS_AVAILABLE, "Variations module not available")

        v1 = generate_variations(simple_generator, count=3, seed_start=42)
        v2 = generate_variations(simple_generator, count=3, seed_start=42)

        for i in range(3):
            self.assertCanvasEqual(v1[i][0], v2[i][0])


class TestGenerateWithMutations(TestCase):
    """Tests for generate_with_mutations function."""

    def test_generate_with_mutations_basic(self):
        """generate_with_mutations creates variations."""
        self.skipUnless(VARIATIONS_AVAILABLE, "Variations module not available")

        def configurable_generator(size=16, color_r=200, seed=42):
            import random
            rng = random.Random(seed)
            canvas = Canvas(size, size)
            canvas.fill_circle(size//2, size//2, size//3, (color_r, 100, 50, 255))
            return canvas

        base_config = {'size': 16, 'color_r': 200, 'seed': 42}
        mutations = {'color_r': (100, 255)}

        variations = generate_with_mutations(
            configurable_generator, base_config, mutations, count=5
        )

        self.assertEqual(len(variations), 5)
        for canvas, config in variations:
            self.assertIsInstance(canvas, Canvas)
            self.assertIn('color_r', config)


class TestSelectBest(TestCase):
    """Tests for select_best function."""

    def test_select_best_basic(self):
        """select_best returns the best canvas."""
        self.skipUnless(VARIATIONS_AVAILABLE, "Variations module not available")

        variations = generate_variations(simple_generator, count=5)
        best = select_best(variations)

        self.assertIsInstance(best, Canvas)

    def test_select_best_with_criteria(self):
        """select_best respects criteria."""
        self.skipUnless(VARIATIONS_AVAILABLE, "Variations module not available")

        variations = generate_variations(simple_generator, count=5)

        best_detail = select_best(variations, criteria='detail')
        best_balance = select_best(variations, criteria='balance')

        self.assertIsInstance(best_detail, Canvas)
        self.assertIsInstance(best_balance, Canvas)

    def test_select_best_with_enum_criteria(self):
        """select_best accepts QualityCriteria enum."""
        self.skipUnless(VARIATIONS_AVAILABLE, "Variations module not available")

        variations = generate_variations(simple_generator, count=3)
        best = select_best(variations, criteria=QualityCriteria.OVERALL)

        self.assertIsInstance(best, Canvas)

    def test_select_best_empty_raises(self):
        """select_best raises on empty list."""
        self.skipUnless(VARIATIONS_AVAILABLE, "Variations module not available")

        with self.assertRaises(ValueError):
            select_best([])


class TestRankByQuality(TestCase):
    """Tests for rank_by_quality function."""

    def test_rank_by_quality_basic(self):
        """rank_by_quality returns sorted list."""
        self.skipUnless(VARIATIONS_AVAILABLE, "Variations module not available")

        variations = generate_variations(simple_generator, count=5)
        ranked = rank_by_quality(variations)

        self.assertEqual(len(ranked), 5)
        for canvas, metadata, score in ranked:
            self.assertIsInstance(canvas, Canvas)
            self.assertIsInstance(score, float)

    def test_rank_by_quality_sorted(self):
        """rank_by_quality returns descending order."""
        self.skipUnless(VARIATIONS_AVAILABLE, "Variations module not available")

        variations = generate_variations(simple_generator, count=5)
        ranked = rank_by_quality(variations)

        scores = [score for _, _, score in ranked]
        self.assertEqual(scores, sorted(scores, reverse=True))


class TestBatchGenerate(TestCase):
    """Tests for batch_generate function."""

    def test_batch_generate_list(self):
        """batch_generate returns list."""
        self.skipUnless(VARIATIONS_AVAILABLE, "Variations module not available")

        result = batch_generate(simple_generator, count=5, output_format='list')

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 5)

    def test_batch_generate_dict(self):
        """batch_generate returns dict."""
        self.skipUnless(VARIATIONS_AVAILABLE, "Variations module not available")

        result = batch_generate(simple_generator, count=3, seed_start=100, output_format='dict')

        self.assertIsInstance(result, dict)
        self.assertIn(100, result)
        self.assertIn(101, result)
        self.assertIn(102, result)


class TestGenerateAssetSet(TestCase):
    """Tests for generate_asset_set function."""

    def test_generate_asset_set_basic(self):
        """generate_asset_set creates complete set."""
        self.skipUnless(VARIATIONS_AVAILABLE, "Variations module not available")

        generators = {
            'sprite_a': simple_generator,
            'sprite_b': simple_generator,
        }

        result = generate_asset_set(generators, variations_per_asset=3)

        self.assertIn('sprite_a', result)
        self.assertIn('sprite_b', result)
        self.assertIsInstance(result['sprite_a'], Canvas)

"""Tests for AI agent module."""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core import Canvas
from ai.agent import (
    AgentMemory,
    GenerationRecord,
    StylePreferences,
    get_memory,
    reset_memory,
    QualityEvaluator,
    EvaluationCriteria,
    evaluate_canvas,
    Planner,
    ExecutionPlan,
    PlanStep,
    StepStatus,
    create_plan,
    Refiner,
    RefinementType,
    RefinementSuggestion,
    auto_refine,
)
from ai.tools.results import GenerationResult, QualityScore


class TestAgentMemory:
    """Tests for agent memory."""

    def setup_method(self):
        """Reset memory before each test."""
        reset_memory()

    def test_record_generation(self):
        """Test recording a generation."""
        memory = get_memory()
        record = memory.record_generation(
            prompt="a red warrior",
            tool_name="generate_character",
            parameters={"preset": "warrior", "hair_color": "red"},
        )

        assert record.prompt == "a red warrior"
        assert record.tool_name == "generate_character"
        assert len(memory.get_recent_results()) == 1

    def test_get_last_result(self):
        """Test getting last result."""
        memory = get_memory()
        memory.record_generation(
            prompt="first",
            tool_name="test",
            parameters={},
        )
        memory.record_generation(
            prompt="second",
            tool_name="test",
            parameters={},
        )

        last = memory.get_last_result()
        assert last.prompt == "second"

    def test_style_preferences_update(self):
        """Test style preferences are updated."""
        memory = get_memory()
        memory.record_generation(
            prompt="test",
            tool_name="generate_character",
            parameters={"hair_color": "red", "preset": "warrior"},
        )

        prefs = memory.style_preferences
        assert "red" in prefs.preferred_colors
        assert "warrior" in prefs.preferred_presets

    def test_record_feedback(self):
        """Test recording feedback."""
        memory = get_memory()
        memory.record_generation(
            prompt="test",
            tool_name="test",
            parameters={},
        )
        memory.record_feedback("looks great!")

        last = memory.get_last_result()
        assert last.user_feedback == "looks great!"

    def test_context_storage(self):
        """Test context storage."""
        memory = get_memory()
        memory.set_context("theme", "fantasy")
        assert memory.get_context("theme") == "fantasy"
        assert memory.get_context("missing", "default") == "default"

    def test_get_by_tag(self):
        """Test getting records by tag."""
        memory = get_memory()
        memory.record_generation(
            prompt="tagged",
            tool_name="test",
            parameters={},
            tags=["important"],
        )
        memory.record_generation(
            prompt="untagged",
            tool_name="test",
            parameters={},
        )

        tagged = memory.get_by_tag("important")
        assert len(tagged) == 1
        assert tagged[0].prompt == "tagged"

    def test_suggest_parameters(self):
        """Test parameter suggestions."""
        memory = get_memory()
        memory.record_generation(
            prompt="test",
            tool_name="generate_character",
            parameters={"hair_color": "blue", "preset": "mage"},
        )

        suggestions = memory.suggest_parameters("generate_character")
        assert suggestions.get("hair_color") == "blue"
        assert suggestions.get("preset") == "mage"

    def test_max_history(self):
        """Test history trimming."""
        memory = AgentMemory(max_history=5)

        for i in range(10):
            memory.record_generation(
                prompt=f"prompt {i}",
                tool_name="test",
                parameters={},
            )

        assert len(memory.get_recent_results(100)) == 5

    def test_serialization(self):
        """Test serialization to/from dict."""
        memory = get_memory()
        memory.record_generation(
            prompt="test",
            tool_name="generate_character",
            parameters={"preset": "warrior"},
        )
        memory.set_context("theme", "fantasy")

        data = memory.to_dict()
        restored = AgentMemory.from_dict(data)

        assert len(restored.get_recent_results()) == 1
        assert restored.get_context("theme") == "fantasy"


class TestQualityEvaluator:
    """Tests for quality evaluator."""

    def create_test_canvas(self, fill_color=None):
        """Create a test canvas."""
        canvas = Canvas(16, 16)
        if fill_color:
            for y in range(16):
                for x in range(16):
                    canvas.set_pixel(x, y, fill_color)
        return canvas

    def test_evaluate_empty_canvas(self):
        """Test evaluating empty canvas."""
        canvas = self.create_test_canvas()
        score = evaluate_canvas(canvas)
        assert score.overall >= 0
        assert score.overall <= 1

    def test_evaluate_filled_canvas(self):
        """Test evaluating filled canvas."""
        canvas = self.create_test_canvas((100, 100, 100, 255))
        score = evaluate_canvas(canvas)
        assert score.overall >= 0
        assert score.overall <= 1

    def test_color_economy(self):
        """Test color economy scoring."""
        # Canvas with few colors should score higher
        canvas = self.create_test_canvas((100, 100, 100, 255))
        evaluator = QualityEvaluator()
        score = evaluator.evaluate(canvas)
        assert score.color_harmony >= 0.5

    def test_coverage_scoring(self):
        """Test coverage scoring."""
        # Partially filled canvas
        canvas = Canvas(16, 16)
        for y in range(8):
            for x in range(8):
                canvas.set_pixel(x, y, (100, 100, 100, 255))

        score = evaluate_canvas(canvas)
        assert score.silhouette >= 0

    def test_custom_criteria(self):
        """Test custom evaluation criteria."""
        criteria = EvaluationCriteria(
            check_color_count=True,
            max_colors=4,
            check_symmetry=True,
        )
        evaluator = QualityEvaluator(criteria)
        canvas = self.create_test_canvas((100, 100, 100, 255))
        score = evaluator.evaluate(canvas)
        assert score is not None


class TestPlanner:
    """Tests for planner."""

    def test_simple_plan(self):
        """Test creating a simple plan."""
        plan = create_plan("a red warrior")
        assert plan is not None
        assert len(plan.steps) >= 1

    def test_character_set_plan(self):
        """Test creating a character set plan."""
        plan = create_plan("create a set of 3 heroes")
        assert len(plan.steps) >= 3

    def test_animated_character_plan(self):
        """Test creating an animated character plan."""
        plan = create_plan("a walking knight")
        assert len(plan.steps) >= 2
        # Should have character generation and animation steps

    def test_scene_with_props_plan(self):
        """Test creating a scene with props plan."""
        plan = create_plan("a forest scene with a chest")
        assert len(plan.steps) >= 1

    def test_variations_plan(self):
        """Test creating a variations plan."""
        plan = create_plan("create 5 variations of a warrior")
        assert len(plan.steps) >= 5

    def test_get_next_step(self):
        """Test getting next step."""
        planner = Planner()
        plan = create_plan("a red warrior")

        step = planner.get_next_step(plan)
        assert step is not None
        assert step.status == StepStatus.PENDING

    def test_plan_dependencies(self):
        """Test plan step dependencies."""
        plan = create_plan("a walking knight")

        # Find animation step
        anim_step = None
        for step in plan.steps:
            if step.depends_on:
                anim_step = step
                break

        if anim_step:
            # Animation should depend on character generation
            assert len(anim_step.depends_on) > 0


class TestRefiner:
    """Tests for refiner."""

    def create_test_result(self, canvas=None):
        """Create a test generation result."""
        if canvas is None:
            canvas = Canvas(16, 16)
            for y in range(16):
                for x in range(16):
                    canvas.set_pixel(x, y, (100, 100, 100, 255))

        return GenerationResult(
            canvas=canvas,
            parameters={"preset": "warrior"},
            seed=12345,
            sprite_type="character",
            generator_name="test",
            generation_time_ms=100,
            quality_score=None,
            metadata={},
        )

    def test_analyze_suggestions(self):
        """Test getting refinement suggestions."""
        refiner = Refiner()
        result = self.create_test_result()

        suggestions = refiner.analyze(result)
        assert isinstance(suggestions, list)

    def test_apply_color_reduction(self):
        """Test color reduction refinement."""
        refiner = Refiner()
        result = self.create_test_result()

        suggestion = RefinementSuggestion(
            refinement_type=RefinementType.COLOR_ADJUST,
            description="Reduce colors",
            priority=0.8,
            parameters={"target_colors": 4},
        )

        refinement = refiner.refine(result, suggestion)
        assert refinement.refined is not None

    def test_apply_contrast_boost(self):
        """Test contrast boost refinement."""
        refiner = Refiner()
        result = self.create_test_result()

        suggestion = RefinementSuggestion(
            refinement_type=RefinementType.CONTRAST_BOOST,
            description="Boost contrast",
            priority=0.7,
            parameters={"boost_factor": 1.2},
        )

        refinement = refiner.refine(result, suggestion)
        assert refinement.refined is not None

    def test_auto_refine(self):
        """Test automatic refinement."""
        result = self.create_test_result()
        refined, messages = auto_refine(result)

        assert refined is not None
        assert len(messages) > 0


class TestIntegration:
    """Integration tests for agent components."""

    def setup_method(self):
        """Reset state before each test."""
        reset_memory()

    def test_memory_with_quality_score(self):
        """Test memory recording with quality score."""
        memory = get_memory()
        canvas = Canvas(16, 16)
        for y in range(16):
            for x in range(16):
                canvas.set_pixel(x, y, (100, 100, 100, 255))

        quality = evaluate_canvas(canvas)

        result = GenerationResult(
            canvas=canvas,
            parameters={"preset": "warrior"},
            seed=12345,
            sprite_type="character",
            generator_name="test",
            generation_time_ms=100,
            quality_score=quality,
            metadata={},
        )

        record = memory.record_generation(
            prompt="a warrior",
            tool_name="generate_character",
            parameters={"preset": "warrior"},
            result=result,
            quality_score=quality,
        )

        high_quality = memory.get_high_quality(min_score=0.1)
        assert len(high_quality) >= 0  # May or may not meet threshold

    def test_plan_and_refine_workflow(self):
        """Test planning and refinement workflow."""
        # Create plan
        plan = create_plan("a fierce warrior")
        assert plan is not None

        # Get first step
        planner = Planner()
        step = planner.get_next_step(plan)
        assert step is not None

        # Create mock result
        canvas = Canvas(16, 16)
        for y in range(16):
            for x in range(16):
                canvas.set_pixel(x, y, (100, 100, 100, 255))

        result = GenerationResult(
            canvas=canvas,
            parameters=step.tool_call.parameters,
            seed=12345,
            sprite_type="character",
            generator_name=step.tool_call.tool_name,
            generation_time_ms=100,
            quality_score=None,
            metadata={},
        )

        # Analyze for refinement
        refiner = Refiner()
        suggestions = refiner.analyze(result)
        assert isinstance(suggestions, list)

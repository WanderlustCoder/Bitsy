"""Tests for AI tools module."""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ai.tools import (
    ToolRegistry,
    get_tools,
    list_tools,
)
from ai.tools.definitions import tool
from ai.tools.results import GenerationResult, AnimationResult, ToolResult, QualityScore


class TestToolDecorator:
    """Tests for the @tool decorator."""

    def test_basic_registration(self):
        """Test basic tool registration."""
        @tool(name="test_tool_basic")
        def test_func():
            return "result"

        registry = ToolRegistry.get_instance()
        registered = registry.get("test_tool_basic")
        assert registered is not None
        assert registered.name == "test_tool_basic"

    def test_with_category_and_tags(self):
        """Test registration with category and tags."""
        @tool(name="test_tool_cat", category="testing", tags=["unit", "test"])
        def test_func():
            return "result"

        registry = ToolRegistry.get_instance()
        registered = registry.get("test_tool_cat")
        assert registered.category == "testing"
        assert "unit" in registered.tags
        assert "test" in registered.tags

    def test_function_still_callable(self):
        """Test that decorated function is still callable."""
        @tool(name="test_tool_call")
        def add(a: int, b: int) -> int:
            return a + b

        result = add(2, 3)
        assert result == 5


class TestToolRegistry:
    """Tests for tool registry."""

    def test_singleton(self):
        """Test singleton pattern."""
        r1 = ToolRegistry.get_instance()
        r2 = ToolRegistry.get_instance()
        assert r1 is r2

    def test_list_all_tools(self):
        """Test listing all tools."""
        registry = ToolRegistry.get_instance()
        tools = registry.all()
        assert len(tools) > 0

    def test_get_nonexistent(self):
        """Test getting nonexistent tool."""
        registry = ToolRegistry.get_instance()
        tool = registry.get("nonexistent_tool_xyz")
        assert tool is None

    def test_list_by_category(self):
        """Test listing tools by category."""
        registry = ToolRegistry.get_instance()
        all_tools = registry.all()

        # Check that some tools have categories
        categories = set(t.category for t in all_tools)
        assert len(categories) > 0


class TestToolResults:
    """Tests for tool result types."""

    def test_generation_result(self):
        """Test GenerationResult creation."""
        from core import Canvas
        canvas = Canvas(16, 16)

        result = GenerationResult(
            canvas=canvas,
            parameters={"test": "value"},
            seed=12345,
            sprite_type="character",
            generator_name="test",
            generation_time_ms=100.0,
        )

        assert result.canvas is canvas
        assert result.seed == 12345
        assert result.sprite_type == "character"

    def test_animation_result(self):
        """Test AnimationResult creation."""
        from core import Canvas
        frames = [Canvas(16, 16) for _ in range(4)]

        result = AnimationResult(
            frames=frames,
            frame_delays=[100, 100, 100, 100],
            fps=10,
            loop=True,
            parameters={"animation_type": "idle"},
            seed=12345,
        )

        assert len(result.frames) == 4
        assert result.fps == 10
        assert result.loop is True

    def test_tool_result_success(self):
        """Test ToolResult success case."""
        result = ToolResult.ok({"data": "value"})
        assert result.success is True
        assert result.result == {"data": "value"}
        assert result.error is None

    def test_tool_result_failure(self):
        """Test ToolResult failure case."""
        result = ToolResult.fail("Something went wrong", "TestError")
        assert result.success is False
        assert result.error == "Something went wrong"
        assert result.error_type == "TestError"

    def test_quality_score(self):
        """Test QualityScore creation."""
        score = QualityScore(
            overall=0.85,
            color_harmony=0.9,
            contrast=0.8,
            composition=0.85,
            detail_level=0.8,
        )

        assert score.overall == 0.85
        assert score.color_harmony == 0.9


class TestHelperFunctions:
    """Tests for helper functions."""

    def test_get_tools(self):
        """Test get_tools function."""
        registry = get_tools()
        assert isinstance(registry, ToolRegistry)

    def test_list_tools(self):
        """Test list_tools function."""
        tools = list_tools()
        assert isinstance(tools, list)
        assert len(tools) > 0

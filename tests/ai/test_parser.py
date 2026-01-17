"""Tests for AI parser module."""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ai.parser import (
    parse_prompt,
    ParsedPrompt,
    ToolCall,
    ParserConfig,
    extract_keywords,
    match_templates,
    VocabularyRegistry,
    TemplateRegistry,
    get_vocabulary,
    get_templates,
)


class TestKeywordExtraction:
    """Tests for keyword extraction."""

    def test_extracts_sprite_type(self):
        """Test sprite type extraction."""
        result = extract_keywords("a fierce warrior")
        assert result.sprite_type == "character"

    def test_extracts_creature_type(self):
        """Test creature type extraction."""
        result = extract_keywords("a green slime")
        assert result.sprite_type == "creature"

    def test_extracts_colors(self):
        """Test color extraction."""
        result = extract_keywords("a red-haired knight")
        assert "red" in result.colors

    def test_extracts_preset(self):
        """Test preset extraction."""
        result = extract_keywords("make me a wizard")
        assert result.preset == "wizard"

    def test_extracts_species(self):
        """Test species extraction."""
        result = extract_keywords("an elf warrior")
        assert result.species == "elf"

    def test_extracts_modifiers(self):
        """Test modifier extraction."""
        result = extract_keywords("a fierce angry knight")
        assert "fierce" in result.modifiers
        assert "angry" in result.modifiers

    def test_tracks_unknown_words(self):
        """Test unknown word tracking."""
        result = extract_keywords("a xyzabc warrior")
        assert "xyzabc" in result.unknown

    def test_calculates_confidence(self):
        """Test confidence calculation."""
        result = extract_keywords("a red warrior")
        assert result.confidence > 0.5

        result_unknown = extract_keywords("xyzabc defghi")
        assert result_unknown.confidence < result.confidence


class TestTemplateMatching:
    """Tests for template matching."""

    def test_matches_color_class(self):
        """Test color + class template."""
        result = match_templates("a red warrior")
        assert result is not None
        assert result.tool_name == "generate_character"
        assert result.parameters.get("preset") == "warrior"

    def test_matches_species_class(self):
        """Test species + class template."""
        result = match_templates("an elf mage")
        assert result is not None
        assert result.parameters.get("species") == "elf"
        assert result.parameters.get("preset") == "mage"

    def test_matches_creature(self):
        """Test creature template."""
        result = match_templates("a green slime")
        assert result is not None
        assert result.tool_name == "generate_sprite"
        assert "slime" in result.parameters.get("description", "").lower()

    def test_matches_item(self):
        """Test item template."""
        result = match_templates("a golden sword")
        assert result is not None
        assert result.tool_name == "generate_item"

    def test_matches_scene(self):
        """Test scene template."""
        result = match_templates("a sunset forest")
        assert result is not None
        assert result.tool_name == "generate_scene"

    def test_matches_variations(self):
        """Test variation request template."""
        result = match_templates("make 5 variations")
        assert result is not None
        assert result.parameters.get("count") == 5

    def test_no_match_returns_none(self):
        """Test that non-matching text returns None."""
        result = match_templates("asdfgh jklmno")
        assert result is None


class TestPromptParsing:
    """Tests for main parser."""

    def test_parses_simple_character(self):
        """Test simple character parsing."""
        result = parse_prompt("a red warrior")
        assert result.tool_call is not None
        assert result.tool_call.tool_name == "generate_character"

    def test_parses_creature(self):
        """Test creature parsing."""
        result = parse_prompt("a blue slime monster")
        assert result.tool_call is not None
        assert "slime" in str(result.tool_call.parameters).lower()

    def test_parses_item(self):
        """Test item parsing."""
        result = parse_prompt("a magical sword")
        assert result.tool_call is not None
        assert result.tool_call.tool_name == "generate_item"

    def test_parses_scene(self):
        """Test scene parsing."""
        result = parse_prompt("a dark forest")
        assert result.tool_call is not None
        assert result.tool_call.tool_name == "generate_scene"

    def test_stores_keywords(self):
        """Test that keywords are stored."""
        result = parse_prompt("a fierce red knight")
        assert result.keywords is not None
        assert "red" in result.keywords.colors

    def test_stores_template_match(self):
        """Test that template match is stored."""
        result = parse_prompt("a red warrior")
        assert result.template_match is not None

    def test_needs_clarification_on_unknown(self):
        """Test clarification for unknown input."""
        result = parse_prompt("xyzabc defghi")
        assert result.needs_clarification is True
        assert len(result.clarification_options) > 0

    def test_warnings_on_low_confidence(self):
        """Test warnings for low confidence."""
        config = ParserConfig(min_confidence=0.9)
        result = parse_prompt("a xyzabc warrior", config)
        assert len(result.warnings) > 0

    def test_warnings_on_unknown_terms(self):
        """Test warnings for unknown terms."""
        result = parse_prompt("a xyzabc red warrior")
        if result.keywords and result.keywords.unknown:
            assert len(result.warnings) > 0


class TestVocabularyRegistry:
    """Tests for vocabulary registry."""

    def test_singleton_instance(self):
        """Test singleton pattern."""
        v1 = VocabularyRegistry.get_instance()
        v2 = VocabularyRegistry.get_instance()
        assert v1 is v2

    def test_lookup(self):
        """Test keyword lookup."""
        vocab = get_vocabulary()
        result = vocab.lookup("warrior", "sprite_type")
        assert result == "character"

    def test_find_category(self):
        """Test finding category for word."""
        vocab = get_vocabulary()
        result = vocab.find_category("red")
        assert result is not None
        assert result[0] == "color"
        assert result[1] == "red"

    def test_register_custom(self):
        """Test registering custom keywords."""
        vocab = get_vocabulary()
        vocab.register("custom", {"testword": "testvalue"})
        result = vocab.lookup("testword", "custom")
        assert result == "testvalue"

    def test_categories(self):
        """Test listing categories."""
        vocab = get_vocabulary()
        categories = vocab.categories()
        assert "sprite_type" in categories
        assert "color" in categories
        assert "preset" in categories


class TestTemplateRegistry:
    """Tests for template registry."""

    def test_singleton_instance(self):
        """Test singleton pattern."""
        t1 = TemplateRegistry.get_instance()
        t2 = TemplateRegistry.get_instance()
        assert t1 is t2

    def test_list_templates(self):
        """Test listing template names."""
        registry = get_templates()
        templates = registry.list_templates()
        assert len(templates) > 0
        assert "color_class" in templates

    def test_add_template(self):
        """Test adding custom template."""
        registry = get_templates()
        registry.add_template(
            name="test_template",
            pattern=r"test (\w+)",
            tool_name="test_tool",
            extractor=lambda m: {"value": m.group(1)},
            priority=1,
        )

        result = registry.match("test hello")
        assert result is not None
        assert result.parameters.get("value") == "hello"

        # Clean up
        registry.remove_template("test_template")

    def test_match_all(self):
        """Test matching all templates."""
        registry = get_templates()
        matches = registry.match_all("a red warrior")
        assert len(matches) >= 1


class TestParserConfig:
    """Tests for parser configuration."""

    def test_default_config(self):
        """Test default configuration."""
        config = ParserConfig()
        assert config.use_templates is True
        assert config.use_keywords is True
        assert config.use_llm_fallback is False
        assert config.min_confidence == 0.5

    def test_templates_disabled(self):
        """Test with templates disabled."""
        config = ParserConfig(use_templates=False)
        result = parse_prompt("a red warrior", config)
        assert result.template_match is None

    def test_keywords_disabled(self):
        """Test with keywords disabled."""
        config = ParserConfig(use_keywords=False)
        result = parse_prompt("a red warrior", config)
        assert result.keywords is None

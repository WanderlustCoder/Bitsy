"""
Main parser combining keywords and templates.

Provides the primary parsing interface that combines
keyword extraction and template matching.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from .keywords import extract_keywords, ExtractedKeywords, get_vocabulary
from .templates import match_templates, TemplateMatch, get_templates


@dataclass
class ToolCall:
    """A structured tool call."""
    tool_name: str
    parameters: Dict[str, Any]
    confidence: float = 0.0
    source: str = ""  # 'template', 'keywords', 'llm'


@dataclass
class ParsedPrompt:
    """Result of parsing a prompt."""
    original: str
    tool_call: Optional[ToolCall] = None
    keywords: Optional[ExtractedKeywords] = None
    template_match: Optional[TemplateMatch] = None
    warnings: List[str] = field(default_factory=list)
    needs_clarification: bool = False
    clarification_options: List[str] = field(default_factory=list)


@dataclass
class ParserConfig:
    """Configuration for the parser."""
    use_templates: bool = True
    use_keywords: bool = True
    use_llm_fallback: bool = False
    min_confidence: float = 0.5
    llm_provider: Optional[str] = None


def parse_prompt(
    prompt: str,
    config: Optional[ParserConfig] = None,
) -> ParsedPrompt:
    """Parse a natural language prompt into a tool call.

    This is the main entry point for parsing. It tries:
    1. Template matching (highest confidence)
    2. Keyword extraction
    3. LLM fallback (if enabled and low confidence)

    Args:
        prompt: Natural language prompt
        config: Parser configuration

    Returns:
        ParsedPrompt with tool call and metadata
    """
    config = config or ParserConfig()
    result = ParsedPrompt(original=prompt)

    # Try template matching first
    if config.use_templates:
        template_match = match_templates(prompt)
        if template_match:
            result.template_match = template_match
            result.tool_call = ToolCall(
                tool_name=template_match.tool_name,
                parameters=template_match.parameters,
                confidence=template_match.confidence,
                source='template',
            )

    # Extract keywords
    if config.use_keywords:
        keywords = extract_keywords(prompt)
        result.keywords = keywords

        # If no template match, build tool call from keywords
        if result.tool_call is None and keywords.sprite_type:
            params = _keywords_to_params(keywords)
            tool_name = _determine_tool(keywords)
            result.tool_call = ToolCall(
                tool_name=tool_name,
                parameters=params,
                confidence=keywords.confidence,
                source='keywords',
            )

    # Check confidence and add warnings
    if result.tool_call:
        if result.tool_call.confidence < config.min_confidence:
            result.warnings.append(
                f"Low confidence ({result.tool_call.confidence:.2f}). "
                "Result may not match intent."
            )

        # Check for unknown terms
        if result.keywords and result.keywords.unknown:
            result.warnings.append(
                f"Unrecognized terms: {', '.join(result.keywords.unknown)}"
            )
    else:
        # No tool call could be determined
        result.needs_clarification = True
        result.clarification_options = [
            "character - Generate a character sprite",
            "creature - Generate a creature/monster",
            "item - Generate an item",
            "prop - Generate a prop/object",
            "scene - Generate a scene/environment",
        ]

    # LLM fallback (not implemented - would require API)
    if (config.use_llm_fallback and
        result.tool_call and
        result.tool_call.confidence < config.min_confidence):
        # Would call LLM here
        pass

    return result


def _keywords_to_params(keywords: ExtractedKeywords) -> Dict[str, Any]:
    """Convert extracted keywords to tool parameters."""
    params = {}

    if keywords.preset:
        params['preset'] = keywords.preset
    if keywords.species:
        params['species'] = keywords.species
    if keywords.colors:
        # First color might be hair color
        params['hair_color'] = keywords.colors[0]
    if keywords.modifiers:
        params['modifiers'] = keywords.modifiers
    if keywords.features:
        params.update(keywords.features)

    return params


def _determine_tool(keywords: ExtractedKeywords) -> str:
    """Determine which tool to use based on keywords."""
    sprite_type = keywords.sprite_type or 'character'

    tool_map = {
        'character': 'generate_character',
        'creature': 'generate_sprite',
        'item': 'generate_item',
        'prop': 'generate_prop',
        'scene': 'generate_scene',
        'environment': 'generate_scene',
    }

    return tool_map.get(sprite_type, 'generate_sprite')


def parse_and_execute(prompt: str, config: Optional[ParserConfig] = None) -> Any:
    """Parse prompt and execute the resulting tool call.

    Args:
        prompt: Natural language prompt
        config: Parser configuration

    Returns:
        Result from tool execution
    """
    from ai.tools import ToolRegistry

    parsed = parse_prompt(prompt, config)

    if parsed.tool_call is None:
        raise ValueError(f"Could not parse prompt: {prompt}")

    registry = ToolRegistry.get_instance()
    tool = registry.get(parsed.tool_call.tool_name)

    if tool is None:
        raise ValueError(f"Unknown tool: {parsed.tool_call.tool_name}")

    return tool.function(**parsed.tool_call.parameters)

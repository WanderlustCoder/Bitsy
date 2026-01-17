"""
AI Parser - Natural language to tool call conversion.

Provides parsing capabilities to convert text descriptions
into structured tool calls.
"""

from .keywords import (
    VocabularyRegistry,
    get_vocabulary,
    extract_keywords,
)

from .templates import (
    TemplateRegistry,
    get_templates,
    match_templates,
)

from .parser import (
    parse_prompt,
    ParsedPrompt,
    ToolCall,
    ParserConfig,
)

__all__ = [
    # Vocabulary
    'VocabularyRegistry',
    'get_vocabulary',
    'extract_keywords',

    # Templates
    'TemplateRegistry',
    'get_templates',
    'match_templates',

    # Main parser
    'parse_prompt',
    'ParsedPrompt',
    'ToolCall',
    'ParserConfig',
]

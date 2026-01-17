"""
Template matching for natural language parsing.

Provides pattern-based parsing for common request formats.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any, Pattern
import re

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


@dataclass
class TemplateMatch:
    """Result of a template match."""
    template_name: str
    tool_name: str
    parameters: Dict[str, Any]
    confidence: float
    matched_text: str


@dataclass
class Template:
    """A pattern template for parsing."""
    name: str
    pattern: Pattern
    tool_name: str
    extractor: Callable[[re.Match], Dict[str, Any]]
    priority: int = 0


class TemplateRegistry:
    """Registry of parsing templates."""

    _instance: Optional['TemplateRegistry'] = None

    def __init__(self):
        self._templates: List[Template] = []
        self._load_defaults()

    @classmethod
    def get_instance(cls) -> 'TemplateRegistry':
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _load_defaults(self):
        """Load default templates."""
        # Character templates
        self.add_template(
            name="color_class",
            pattern=r"(?:a|an)\s+(\w+)\s+(warrior|mage|wizard|knight|rogue|hero)",
            tool_name="generate_character",
            extractor=lambda m: {
                "preset": m.group(2),
                "hair_color": m.group(1) if m.group(1) in _COLORS else None,
            },
            priority=10,
        )

        self.add_template(
            name="class_with_feature",
            pattern=r"(warrior|mage|wizard|knight|rogue|hero)\s+with\s+(.+)",
            tool_name="generate_character",
            extractor=lambda m: {
                "preset": m.group(1),
                "_features": m.group(2),
            },
            priority=9,
        )

        self.add_template(
            name="species_class",
            pattern=r"(?:a|an)\s+(elf|dwarf|orc|goblin|human)\s+(warrior|mage|wizard|knight|rogue)",
            tool_name="generate_character",
            extractor=lambda m: {
                "species": m.group(1),
                "preset": m.group(2),
            },
            priority=10,
        )

        # Creature templates
        self.add_template(
            name="color_creature",
            pattern=r"(?:a|an)\s+(\w+)\s+(slime|goblin|skeleton|dragon|monster|ghost)",
            tool_name="generate_sprite",
            extractor=lambda m: {
                "sprite_type": "creature",
                "description": f"{m.group(1)} {m.group(2)}",
            },
            priority=8,
        )

        self.add_template(
            name="simple_creature",
            pattern=r"(?:a|an)\s+(slime|goblin|skeleton|dragon|monster|ghost|zombie|spider)",
            tool_name="generate_sprite",
            extractor=lambda m: {
                "sprite_type": "creature",
                "description": m.group(1),
            },
            priority=5,
        )

        # Item templates
        self.add_template(
            name="color_item",
            pattern=r"(?:a|an)\s+(\w+)\s+(sword|potion|key|gem|staff|wand|shield|armor)",
            tool_name="generate_item",
            extractor=lambda m: {
                "item_type": m.group(2),
                "variant": m.group(1),
            },
            priority=8,
        )

        self.add_template(
            name="simple_item",
            pattern=r"(?:a|an)\s+(sword|potion|key|gem|staff|wand|shield|armor|weapon)",
            tool_name="generate_item",
            extractor=lambda m: {
                "item_type": m.group(1),
            },
            priority=5,
        )

        # Scene templates
        self.add_template(
            name="time_location",
            pattern=r"(morning|sunset|night|dawn|dusk|noon)\s+(forest|castle|dungeon|cave|village|beach)",
            tool_name="generate_scene",
            extractor=lambda m: {
                "time_of_day": m.group(1),
                "description": m.group(2),
            },
            priority=10,
        )

        self.add_template(
            name="weather_scene",
            pattern=r"(rainy|snowy|foggy|stormy)\s+(forest|castle|dungeon|cave|village|scene)",
            tool_name="generate_scene",
            extractor=lambda m: {
                "weather": m.group(1).replace('y', ''),
                "description": m.group(2),
            },
            priority=9,
        )

        self.add_template(
            name="simple_scene",
            pattern=r"(?:a|an)?\s*(forest|castle|dungeon|cave|village|mountain|beach|desert)\s*(?:scene)?",
            tool_name="generate_scene",
            extractor=lambda m: {
                "description": m.group(1),
            },
            priority=3,
        )

        # Variation request
        self.add_template(
            name="make_variations",
            pattern=r"(?:make|create|generate)\s+(\d+)\s+variations?",
            tool_name="_agent_variations",
            extractor=lambda m: {
                "count": int(m.group(1)),
            },
            priority=15,
        )

        # Modification request
        self.add_template(
            name="make_more",
            pattern=r"make\s+(?:it|that)\s+(?:more\s+)?(\w+)",
            tool_name="_agent_refine",
            extractor=lambda m: {
                "modifier": m.group(1),
            },
            priority=15,
        )

    def add_template(
        self,
        name: str,
        pattern: str,
        tool_name: str,
        extractor: Callable[[re.Match], Dict[str, Any]],
        priority: int = 0,
    ):
        """Add a template pattern.

        Args:
            name: Template identifier
            pattern: Regex pattern
            tool_name: Tool to call when matched
            extractor: Function to extract parameters from match
            priority: Higher priority templates match first
        """
        compiled = re.compile(pattern, re.IGNORECASE)
        template = Template(
            name=name,
            pattern=compiled,
            tool_name=tool_name,
            extractor=extractor,
            priority=priority,
        )
        self._templates.append(template)
        # Keep sorted by priority (descending)
        self._templates.sort(key=lambda t: -t.priority)

    def remove_template(self, name: str):
        """Remove a template by name."""
        self._templates = [t for t in self._templates if t.name != name]

    def match(self, text: str) -> Optional[TemplateMatch]:
        """Try to match text against templates.

        Args:
            text: Text to match

        Returns:
            TemplateMatch if found, None otherwise
        """
        for template in self._templates:
            match = template.pattern.search(text)
            if match:
                try:
                    params = template.extractor(match)
                    return TemplateMatch(
                        template_name=template.name,
                        tool_name=template.tool_name,
                        parameters=params,
                        confidence=0.8 + (template.priority / 100),
                        matched_text=match.group(0),
                    )
                except Exception:
                    continue
        return None

    def match_all(self, text: str) -> List[TemplateMatch]:
        """Match text against all templates.

        Args:
            text: Text to match

        Returns:
            List of all matches
        """
        matches = []
        for template in self._templates:
            match = template.pattern.search(text)
            if match:
                try:
                    params = template.extractor(match)
                    matches.append(TemplateMatch(
                        template_name=template.name,
                        tool_name=template.tool_name,
                        parameters=params,
                        confidence=0.8 + (template.priority / 100),
                        matched_text=match.group(0),
                    ))
                except Exception:
                    continue
        return matches

    def list_templates(self) -> List[str]:
        """List all template names."""
        return [t.name for t in self._templates]


def get_templates() -> TemplateRegistry:
    """Get the global template registry."""
    return TemplateRegistry.get_instance()


def match_templates(text: str) -> Optional[TemplateMatch]:
    """Match text against registered templates.

    Args:
        text: Text to match

    Returns:
        Best match if found
    """
    return get_templates().match(text)


# Color list for template extractors
_COLORS = {
    'red', 'blue', 'green', 'yellow', 'purple', 'orange', 'pink',
    'brown', 'black', 'white', 'gray', 'grey', 'golden', 'silver',
}

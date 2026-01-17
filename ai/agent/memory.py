"""
Agent memory for session context.

Provides persistent context across interactions within a session,
including generation history, style preferences, and recent results.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ai.tools.results import GenerationResult, QualityScore


@dataclass
class GenerationRecord:
    """Record of a generation attempt."""
    timestamp: datetime
    prompt: str
    tool_name: str
    parameters: Dict[str, Any]
    result: Optional[GenerationResult]
    quality_score: Optional[QualityScore]
    user_feedback: Optional[str] = None
    tags: List[str] = field(default_factory=list)


@dataclass
class StylePreferences:
    """User style preferences learned over session."""
    preferred_colors: List[str] = field(default_factory=list)
    preferred_presets: List[str] = field(default_factory=list)
    preferred_modifiers: List[str] = field(default_factory=list)
    palette_preferences: Dict[str, str] = field(default_factory=dict)
    avoided_features: List[str] = field(default_factory=list)


class AgentMemory:
    """Session memory for the agent.

    Tracks generation history, style preferences, and provides
    context for planning and refinement.
    """

    def __init__(self, max_history: int = 50):
        """Initialize agent memory.

        Args:
            max_history: Maximum number of generations to remember
        """
        self._history: List[GenerationRecord] = []
        self._max_history = max_history
        self._style_prefs = StylePreferences()
        self._context: Dict[str, Any] = {}
        self._session_start = datetime.now()

    def record_generation(
        self,
        prompt: str,
        tool_name: str,
        parameters: Dict[str, Any],
        result: Optional[GenerationResult] = None,
        quality_score: Optional[QualityScore] = None,
        tags: Optional[List[str]] = None,
    ) -> GenerationRecord:
        """Record a generation attempt.

        Args:
            prompt: Original user prompt
            tool_name: Tool that was called
            parameters: Parameters used
            result: Generation result if successful
            quality_score: Quality evaluation
            tags: Optional tags for categorization

        Returns:
            The created record
        """
        record = GenerationRecord(
            timestamp=datetime.now(),
            prompt=prompt,
            tool_name=tool_name,
            parameters=parameters,
            result=result,
            quality_score=quality_score,
            tags=tags or [],
        )

        self._history.append(record)

        # Trim history if needed
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]

        # Update style preferences from parameters
        self._update_preferences(parameters)

        return record

    def record_feedback(self, feedback: str, record_index: int = -1):
        """Record user feedback on a generation.

        Args:
            feedback: User's feedback
            record_index: Which record to update (-1 for most recent)
        """
        if self._history:
            self._history[record_index].user_feedback = feedback
            self._process_feedback(feedback)

    def _update_preferences(self, parameters: Dict[str, Any]):
        """Update style preferences from generation parameters."""
        if 'hair_color' in parameters:
            color = parameters['hair_color']
            if color and color not in self._style_prefs.preferred_colors:
                self._style_prefs.preferred_colors.append(color)
                # Keep top 10 colors
                self._style_prefs.preferred_colors = self._style_prefs.preferred_colors[-10:]

        if 'preset' in parameters:
            preset = parameters['preset']
            if preset and preset not in self._style_prefs.preferred_presets:
                self._style_prefs.preferred_presets.append(preset)
                self._style_prefs.preferred_presets = self._style_prefs.preferred_presets[-10:]

        if 'modifiers' in parameters:
            for mod in parameters.get('modifiers', []):
                if mod not in self._style_prefs.preferred_modifiers:
                    self._style_prefs.preferred_modifiers.append(mod)
                    self._style_prefs.preferred_modifiers = self._style_prefs.preferred_modifiers[-10:]

    def _process_feedback(self, feedback: str):
        """Process feedback to update preferences."""
        feedback_lower = feedback.lower()

        # Simple negative feedback detection
        negative_words = ['too', 'not', "don't", 'avoid', 'less', 'remove']
        is_negative = any(word in feedback_lower for word in negative_words)

        # If negative feedback about a recent generation, remember to avoid it
        if is_negative and self._history:
            recent = self._history[-1]
            # Could extract features from the feedback and add to avoided_features
            pass

    def get_recent_results(self, count: int = 5) -> List[GenerationRecord]:
        """Get recent generation records.

        Args:
            count: Number of records to return

        Returns:
            Most recent records
        """
        return self._history[-count:] if self._history else []

    def get_last_result(self) -> Optional[GenerationRecord]:
        """Get the most recent generation record."""
        return self._history[-1] if self._history else None

    def get_by_tag(self, tag: str) -> List[GenerationRecord]:
        """Get all records with a specific tag."""
        return [r for r in self._history if tag in r.tags]

    def get_successful(self) -> List[GenerationRecord]:
        """Get all successful generations."""
        return [r for r in self._history if r.result is not None]

    def get_high_quality(self, min_score: float = 0.8) -> List[GenerationRecord]:
        """Get generations above a quality threshold."""
        return [
            r for r in self._history
            if r.quality_score and r.quality_score.overall >= min_score
        ]

    @property
    def style_preferences(self) -> StylePreferences:
        """Get current style preferences."""
        return self._style_prefs

    def set_context(self, key: str, value: Any):
        """Set a context value.

        Args:
            key: Context key
            value: Value to store
        """
        self._context[key] = value

    def get_context(self, key: str, default: Any = None) -> Any:
        """Get a context value.

        Args:
            key: Context key
            default: Default if not found

        Returns:
            The context value
        """
        return self._context.get(key, default)

    def clear_context(self):
        """Clear all context values."""
        self._context.clear()

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the session.

        Returns:
            Session summary dict
        """
        successful = self.get_successful()
        high_quality = self.get_high_quality()

        return {
            "session_start": self._session_start.isoformat(),
            "total_generations": len(self._history),
            "successful_generations": len(successful),
            "high_quality_generations": len(high_quality),
            "style_preferences": {
                "colors": self._style_prefs.preferred_colors,
                "presets": self._style_prefs.preferred_presets,
                "modifiers": self._style_prefs.preferred_modifiers,
            },
            "context_keys": list(self._context.keys()),
        }

    def suggest_parameters(self, tool_name: str) -> Dict[str, Any]:
        """Suggest parameters based on session history.

        Args:
            tool_name: Tool to suggest parameters for

        Returns:
            Suggested parameters dict
        """
        suggestions = {}

        # Use most recent color preference
        if self._style_prefs.preferred_colors:
            suggestions['hair_color'] = self._style_prefs.preferred_colors[-1]

        # Use most recent preset preference
        if self._style_prefs.preferred_presets:
            suggestions['preset'] = self._style_prefs.preferred_presets[-1]

        # Include any frequently used modifiers
        if self._style_prefs.preferred_modifiers:
            suggestions['modifiers'] = self._style_prefs.preferred_modifiers[-3:]

        return suggestions

    def to_dict(self) -> Dict[str, Any]:
        """Serialize memory to dict for persistence."""
        return {
            "session_start": self._session_start.isoformat(),
            "history": [
                {
                    "timestamp": r.timestamp.isoformat(),
                    "prompt": r.prompt,
                    "tool_name": r.tool_name,
                    "parameters": r.parameters,
                    "user_feedback": r.user_feedback,
                    "tags": r.tags,
                }
                for r in self._history
            ],
            "style_preferences": {
                "preferred_colors": self._style_prefs.preferred_colors,
                "preferred_presets": self._style_prefs.preferred_presets,
                "preferred_modifiers": self._style_prefs.preferred_modifiers,
                "palette_preferences": self._style_prefs.palette_preferences,
                "avoided_features": self._style_prefs.avoided_features,
            },
            "context": self._context,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentMemory':
        """Deserialize memory from dict."""
        memory = cls()
        memory._session_start = datetime.fromisoformat(data.get("session_start", datetime.now().isoformat()))

        # Restore style preferences
        prefs = data.get("style_preferences", {})
        memory._style_prefs = StylePreferences(
            preferred_colors=prefs.get("preferred_colors", []),
            preferred_presets=prefs.get("preferred_presets", []),
            preferred_modifiers=prefs.get("preferred_modifiers", []),
            palette_preferences=prefs.get("palette_preferences", {}),
            avoided_features=prefs.get("avoided_features", []),
        )

        # Restore context
        memory._context = data.get("context", {})

        # Restore history (without full results - those can't be serialized)
        for h in data.get("history", []):
            record = GenerationRecord(
                timestamp=datetime.fromisoformat(h["timestamp"]),
                prompt=h["prompt"],
                tool_name=h["tool_name"],
                parameters=h["parameters"],
                result=None,
                quality_score=None,
                user_feedback=h.get("user_feedback"),
                tags=h.get("tags", []),
            )
            memory._history.append(record)

        return memory


# Global instance
_memory_instance: Optional[AgentMemory] = None


def get_memory() -> AgentMemory:
    """Get the global agent memory instance."""
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = AgentMemory()
    return _memory_instance


def reset_memory():
    """Reset the global memory instance."""
    global _memory_instance
    _memory_instance = AgentMemory()

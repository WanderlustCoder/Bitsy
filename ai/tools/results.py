"""
Result types for AI tools.

Provides structured result types that carry generated output
plus metadata for reproducibility and chaining.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core import Canvas


class SpriteType(Enum):
    """Types of sprites that can be generated."""
    AUTO = "auto"
    CHARACTER = "character"
    CREATURE = "creature"
    ITEM = "item"
    PROP = "prop"
    STRUCTURE = "structure"
    ENVIRONMENT = "environment"


@dataclass
class QualityScore:
    """Quality assessment of generated output."""
    silhouette: float = 0.0      # 0-1, clarity of shape
    color_harmony: float = 0.0   # 0-1, palette cohesion
    readability: float = 0.0     # 0-1, contrast and visibility
    detail: float = 0.0          # 0-1, appropriate detail level
    overall: float = 0.0         # 0-1, weighted average

    issues: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)

    def passes(self, threshold: float = 0.7) -> bool:
        """Check if quality meets threshold."""
        return self.overall >= threshold


@dataclass
class GenerationResult:
    """Result of a sprite generation operation."""
    canvas: Canvas
    parameters: Dict[str, Any]
    seed: int
    sprite_type: SpriteType = SpriteType.AUTO

    # Metadata
    generator_name: str = ""
    generation_time_ms: float = 0.0
    quality_score: Optional[QualityScore] = None

    # For chaining
    metadata: Dict[str, Any] = field(default_factory=dict)

    def save(self, path: str) -> str:
        """Save to PNG file."""
        self.canvas.save(path)
        return path

    def with_metadata(self, **kwargs) -> 'GenerationResult':
        """Return copy with updated metadata."""
        new_meta = {**self.metadata, **kwargs}
        return GenerationResult(
            canvas=self.canvas,
            parameters=self.parameters,
            seed=self.seed,
            sprite_type=self.sprite_type,
            generator_name=self.generator_name,
            generation_time_ms=self.generation_time_ms,
            quality_score=self.quality_score,
            metadata=new_meta,
        )


@dataclass
class AnimationResult:
    """Result of an animation generation operation."""
    frames: List[Canvas]
    frame_delays: List[int]  # milliseconds per frame
    parameters: Dict[str, Any]
    seed: int

    # Metadata
    animation_type: str = ""
    fps: int = 12
    loop: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def frame_count(self) -> int:
        return len(self.frames)

    @property
    def duration_ms(self) -> int:
        return sum(self.frame_delays)

    def get_frame(self, index: int) -> Canvas:
        """Get frame by index (wraps for looping)."""
        if self.loop:
            return self.frames[index % len(self.frames)]
        return self.frames[min(index, len(self.frames) - 1)]


@dataclass
class ToolResult:
    """Wrapper for tool execution results with error handling."""
    success: bool
    result: Optional[GenerationResult] = None
    animation: Optional[AnimationResult] = None
    error: Optional[str] = None
    error_type: Optional[str] = None
    warnings: List[str] = field(default_factory=list)

    # For debugging
    tool_name: str = ""
    parameters_used: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def ok(cls, result: GenerationResult, warnings: List[str] = None) -> 'ToolResult':
        """Create successful result."""
        return cls(
            success=True,
            result=result,
            warnings=warnings or [],
        )

    @classmethod
    def ok_animation(cls, animation: AnimationResult, warnings: List[str] = None) -> 'ToolResult':
        """Create successful animation result."""
        return cls(
            success=True,
            animation=animation,
            warnings=warnings or [],
        )

    @classmethod
    def fail(cls, error: str, error_type: str = "GenerationError") -> 'ToolResult':
        """Create failed result."""
        return cls(
            success=False,
            error=error,
            error_type=error_type,
        )

"""
Iterative refinement for sprite generation.

Provides mechanisms to refine generated sprites based on
feedback, quality scores, and style matching.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core import Canvas
from ai.tools.results import GenerationResult, QualityScore, ToolResult
from ai.agent.evaluator import QualityEvaluator, evaluate_canvas


class RefinementType(Enum):
    """Types of refinement operations."""
    COLOR_ADJUST = "color_adjust"
    CONTRAST_BOOST = "contrast_boost"
    OUTLINE_ENHANCE = "outline_enhance"
    DETAIL_ADD = "detail_add"
    SIMPLIFY = "simplify"
    REGENERATE = "regenerate"


@dataclass
class RefinementSuggestion:
    """A suggested refinement."""
    refinement_type: RefinementType
    description: str
    priority: float  # 0-1, higher = more important
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RefinementResult:
    """Result of a refinement operation."""
    success: bool
    original: GenerationResult
    refined: Optional[GenerationResult]
    improvements: Dict[str, float]  # Score improvements by category
    message: str


class Refiner:
    """Refines generated sprites iteratively."""

    def __init__(self, max_iterations: int = 3, quality_threshold: float = 0.8):
        """Initialize the refiner.

        Args:
            max_iterations: Maximum refinement iterations
            quality_threshold: Quality score to aim for
        """
        self.max_iterations = max_iterations
        self.quality_threshold = quality_threshold
        self._evaluator = QualityEvaluator()

    def analyze(self, result: GenerationResult) -> List[RefinementSuggestion]:
        """Analyze a result and suggest refinements.

        Args:
            result: Generation result to analyze

        Returns:
            List of refinement suggestions
        """
        suggestions = []
        score = result.quality_score

        if not score:
            score = self._evaluator.evaluate(result.canvas)

        # Check each quality dimension
        if score.color_harmony < 0.6:
            suggestions.append(RefinementSuggestion(
                refinement_type=RefinementType.COLOR_ADJUST,
                description="Improve color harmony by reducing palette",
                priority=0.8,
                parameters={"target_colors": 8},
            ))

        if score.readability < 0.5:
            suggestions.append(RefinementSuggestion(
                refinement_type=RefinementType.CONTRAST_BOOST,
                description="Increase contrast between elements",
                priority=0.7,
                parameters={"boost_factor": 1.3},
            ))

        if score.detail < 0.5:
            suggestions.append(RefinementSuggestion(
                refinement_type=RefinementType.OUTLINE_ENHANCE,
                description="Enhance outlines for better definition",
                priority=0.6,
                parameters={"outline_strength": 1.2},
            ))

        if score.silhouette < 0.5:
            suggestions.append(RefinementSuggestion(
                refinement_type=RefinementType.DETAIL_ADD,
                description="Add more detail to fill composition",
                priority=0.5,
            ))

        # Check for over-complexity
        if score.color_harmony < 0.4 and score.overall < 0.5:
            suggestions.append(RefinementSuggestion(
                refinement_type=RefinementType.SIMPLIFY,
                description="Simplify design - too many colors/details",
                priority=0.9,
            ))

        # Sort by priority
        suggestions.sort(key=lambda s: -s.priority)

        return suggestions

    def refine(
        self,
        result: GenerationResult,
        suggestion: RefinementSuggestion,
    ) -> RefinementResult:
        """Apply a refinement to a result.

        Args:
            result: Original generation result
            suggestion: Refinement to apply

        Returns:
            RefinementResult
        """
        original_score = result.quality_score or self._evaluator.evaluate(result.canvas)

        # Apply refinement based on type
        refined_canvas = self._apply_refinement(
            result.canvas,
            suggestion.refinement_type,
            suggestion.parameters,
        )

        if refined_canvas is None:
            return RefinementResult(
                success=False,
                original=result,
                refined=None,
                improvements={},
                message=f"Failed to apply {suggestion.refinement_type.value}",
            )

        # Evaluate refined result
        new_score = self._evaluator.evaluate(refined_canvas)

        # Calculate improvements
        improvements = {
            "overall": new_score.overall - original_score.overall,
            "color_harmony": new_score.color_harmony - original_score.color_harmony,
            "contrast": new_score.contrast - original_score.contrast,
            "composition": new_score.composition - original_score.composition,
            "detail_level": new_score.detail_level - original_score.detail_level,
        }

        # Create refined result
        refined_result = GenerationResult(
            canvas=refined_canvas,
            parameters={**result.parameters, "refined": True},
            seed=result.seed,
            sprite_type=result.sprite_type,
            generator_name=f"{result.generator_name}_refined",
            generation_time_ms=result.generation_time_ms,
            quality_score=new_score,
            metadata={
                **result.metadata,
                "refinement_type": suggestion.refinement_type.value,
                "original_score": original_score.overall,
                "refined_score": new_score.overall,
            },
        )

        success = new_score.overall > original_score.overall
        return RefinementResult(
            success=success,
            original=result,
            refined=refined_result,
            improvements=improvements,
            message=f"Refinement {'improved' if success else 'did not improve'} quality "
                    f"({original_score.overall:.2f} -> {new_score.overall:.2f})",
        )

    def _apply_refinement(
        self,
        canvas: Canvas,
        refinement_type: RefinementType,
        parameters: Dict[str, Any],
    ) -> Optional[Canvas]:
        """Apply a specific refinement to a canvas."""
        try:
            if refinement_type == RefinementType.COLOR_ADJUST:
                return self._reduce_colors(canvas, parameters.get('target_colors', 8))

            elif refinement_type == RefinementType.CONTRAST_BOOST:
                return self._boost_contrast(canvas, parameters.get('boost_factor', 1.2))

            elif refinement_type == RefinementType.OUTLINE_ENHANCE:
                return self._enhance_outlines(canvas, parameters.get('outline_strength', 1.0))

            elif refinement_type == RefinementType.SIMPLIFY:
                return self._simplify(canvas)

            elif refinement_type == RefinementType.DETAIL_ADD:
                # This would require regeneration with different params
                return canvas  # No-op for now

            elif refinement_type == RefinementType.REGENERATE:
                # Signals need for regeneration
                return None

        except Exception as e:
            return None

        return canvas

    def _reduce_colors(self, canvas: Canvas, target_colors: int) -> Canvas:
        """Reduce the color palette of a canvas."""
        from core import Color

        # Collect all colors and their frequencies
        color_freq = {}
        for y in range(canvas.height):
            for x in range(canvas.width):
                pixel = canvas.get_pixel(x, y)
                if pixel and pixel[3] > 0:
                    key = (pixel[0], pixel[1], pixel[2])
                    color_freq[key] = color_freq.get(key, 0) + 1

        # Keep top N colors
        sorted_colors = sorted(color_freq.items(), key=lambda x: -x[1])
        palette = [c[0] for c in sorted_colors[:target_colors]]

        # Create new canvas with reduced palette
        new_canvas = Canvas(canvas.width, canvas.height)

        for y in range(canvas.height):
            for x in range(canvas.width):
                pixel = canvas.get_pixel(x, y)
                if pixel and pixel[3] > 0:
                    # Find closest color in palette
                    closest = self._find_closest_color(
                        (pixel[0], pixel[1], pixel[2]),
                        palette,
                    )
                    new_canvas.set_pixel(x, y, (closest[0], closest[1], closest[2], pixel[3]))

        return new_canvas

    def _find_closest_color(
        self,
        color: Tuple[int, int, int],
        palette: List[Tuple[int, int, int]],
    ) -> Tuple[int, int, int]:
        """Find the closest color in a palette."""
        if not palette:
            return color

        min_dist = float('inf')
        closest = palette[0]

        for p in palette:
            dist = sum((a - b) ** 2 for a, b in zip(color, p))
            if dist < min_dist:
                min_dist = dist
                closest = p

        return closest

    def _boost_contrast(self, canvas: Canvas, factor: float) -> Canvas:
        """Boost contrast of a canvas."""
        from core import Color

        new_canvas = Canvas(canvas.width, canvas.height)

        for y in range(canvas.height):
            for x in range(canvas.width):
                pixel = canvas.get_pixel(x, y)
                if pixel and pixel[3] > 0:
                    # Apply contrast boost
                    r = self._apply_contrast(pixel[0], factor)
                    g = self._apply_contrast(pixel[1], factor)
                    b = self._apply_contrast(pixel[2], factor)
                    new_canvas.set_pixel(x, y, (r, g, b, pixel[3]))

        return new_canvas

    def _apply_contrast(self, value: int, factor: float) -> int:
        """Apply contrast adjustment to a single channel."""
        adjusted = 128 + (value - 128) * factor
        return max(0, min(255, int(adjusted)))

    def _enhance_outlines(self, canvas: Canvas, strength: float) -> Canvas:
        """Enhance outlines of a canvas."""
        from core import Color

        new_canvas = Canvas(canvas.width, canvas.height)

        # Copy original
        for y in range(canvas.height):
            for x in range(canvas.width):
                pixel = canvas.get_pixel(x, y)
                if pixel:
                    new_canvas.set_pixel(x, y, pixel)

        # Darken edge pixels
        for y in range(canvas.height):
            for x in range(canvas.width):
                pixel = canvas.get_pixel(x, y)
                if pixel and pixel[3] > 0:
                    if self._is_edge(canvas, x, y):
                        # Darken the pixel
                        factor = 1.0 - (0.3 * strength)
                        r = int(pixel[0] * factor)
                        g = int(pixel[1] * factor)
                        b = int(pixel[2] * factor)
                        new_canvas.set_pixel(x, y, (r, g, b, pixel[3]))

        return new_canvas

    def _is_edge(self, canvas: Canvas, x: int, y: int) -> bool:
        """Check if a pixel is on the edge."""
        pixel = canvas.get_pixel(x, y)
        if not pixel or pixel[3] == 0:
            return False

        neighbors = [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]
        for nx, ny in neighbors:
            if nx < 0 or nx >= canvas.width or ny < 0 or ny >= canvas.height:
                return True
            neighbor = canvas.get_pixel(nx, ny)
            if not neighbor or neighbor[3] == 0:
                return True

        return False

    def _simplify(self, canvas: Canvas) -> Canvas:
        """Simplify a canvas by reducing colors and removing noise."""
        # First reduce colors
        reduced = self._reduce_colors(canvas, 4)

        # Then remove isolated pixels (noise)
        from core import Color

        new_canvas = Canvas(canvas.width, canvas.height)

        for y in range(canvas.height):
            for x in range(canvas.width):
                pixel = reduced.get_pixel(x, y)
                if pixel and pixel[3] > 0:
                    # Count similar neighbors
                    similar = self._count_similar_neighbors(reduced, x, y, pixel)
                    if similar >= 1:  # Keep if at least 1 similar neighbor
                        new_canvas.set_pixel(x, y, pixel)

        return new_canvas

    def _count_similar_neighbors(
        self,
        canvas: Canvas,
        x: int,
        y: int,
        pixel,
        threshold: int = 30,
    ) -> int:
        """Count neighbors with similar colors."""
        count = 0
        neighbors = [
            (x-1, y), (x+1, y), (x, y-1), (x, y+1),
            (x-1, y-1), (x+1, y-1), (x-1, y+1), (x+1, y+1),
        ]

        for nx, ny in neighbors:
            if 0 <= nx < canvas.width and 0 <= ny < canvas.height:
                neighbor = canvas.get_pixel(nx, ny)
                if neighbor and neighbor[3] > 0:
                    if (abs(pixel[0] - neighbor[0]) <= threshold and
                        abs(pixel[1] - neighbor[1]) <= threshold and
                        abs(pixel[2] - neighbor[2]) <= threshold):
                        count += 1

        return count

    def auto_refine(
        self,
        result: GenerationResult,
    ) -> Tuple[GenerationResult, List[str]]:
        """Automatically refine a result until quality threshold is met.

        Args:
            result: Initial generation result

        Returns:
            Tuple of (final result, list of refinement messages)
        """
        messages = []
        current = result
        iterations = 0

        while iterations < self.max_iterations:
            # Evaluate current
            score = current.quality_score or self._evaluator.evaluate(current.canvas)

            if score.overall >= self.quality_threshold:
                messages.append(f"Quality threshold met: {score.overall:.2f}")
                break

            # Get suggestions
            suggestions = self.analyze(current)
            if not suggestions:
                messages.append("No further refinements available")
                break

            # Apply top suggestion
            top = suggestions[0]
            refinement = self.refine(current, top)
            messages.append(refinement.message)

            if refinement.success and refinement.refined:
                current = refinement.refined
            else:
                # Refinement didn't help, try next suggestion
                if len(suggestions) > 1:
                    refinement = self.refine(current, suggestions[1])
                    messages.append(refinement.message)
                    if refinement.success and refinement.refined:
                        current = refinement.refined

            iterations += 1

        return current, messages


def analyze_for_refinement(result: GenerationResult) -> List[RefinementSuggestion]:
    """Convenience function to analyze a result.

    Args:
        result: Generation result

    Returns:
        List of refinement suggestions
    """
    refiner = Refiner()
    return refiner.analyze(result)


def auto_refine(result: GenerationResult) -> Tuple[GenerationResult, List[str]]:
    """Convenience function for automatic refinement.

    Args:
        result: Initial result

    Returns:
        Refined result and messages
    """
    refiner = Refiner()
    return refiner.auto_refine(result)

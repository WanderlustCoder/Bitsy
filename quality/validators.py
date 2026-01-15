"""
Validators - Style compliance and constraint validation for pixel art.

Validates that pixel art meets specified style requirements:
- Palette constraints (max colors, specific palette)
- Outline style compliance
- Contrast requirements
- Animation smoothness
"""

import sys
import os
from typing import List, Tuple, Dict, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Canvas
from core.color import color_distance_weighted, rgb_to_hsv, grayscale
from core.style import Style


class ViolationType(Enum):
    """Types of style violations."""
    PALETTE_EXCEEDED = "palette_exceeded"
    COLOR_NOT_IN_PALETTE = "color_not_in_palette"
    MISSING_OUTLINE = "missing_outline"
    WRONG_OUTLINE_COLOR = "wrong_outline_color"
    LOW_CONTRAST = "low_contrast"
    ANIMATION_TIMING = "animation_timing"
    ANIMATION_JITTER = "animation_jitter"
    SIZE_VIOLATION = "size_violation"


class ViolationSeverity(Enum):
    """Severity of style violations."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class StyleViolation:
    """A style compliance violation."""
    violation_type: ViolationType
    severity: ViolationSeverity
    description: str
    details: Dict[str, Any] = field(default_factory=dict)
    suggestion: str = ""

    def __str__(self) -> str:
        return f"{self.severity.value.upper()}: {self.violation_type.value} - {self.description}"


@dataclass
class ValidationReport:
    """Complete validation report."""
    is_valid: bool
    violations: List[StyleViolation] = field(default_factory=list)
    style_name: str = ""
    checks_performed: List[str] = field(default_factory=list)

    @property
    def error_count(self) -> int:
        return sum(1 for v in self.violations if v.severity == ViolationSeverity.ERROR)

    @property
    def warning_count(self) -> int:
        return sum(1 for v in self.violations if v.severity == ViolationSeverity.WARNING)

    def __str__(self) -> str:
        status = "VALID" if self.is_valid else "INVALID"
        lines = [
            f"Validation Report: {status}",
            f"Style: {self.style_name or 'None'}",
            f"Checks: {', '.join(self.checks_performed)}",
            f"Violations: {len(self.violations)} ({self.error_count} errors, {self.warning_count} warnings)",
        ]
        if self.violations:
            lines.append("\nViolations:")
            for v in self.violations:
                lines.append(f"  - {v}")
        return "\n".join(lines)


def validate_palette(canvas: Canvas, max_colors: Optional[int] = None,
                     required_palette: Optional[List[Tuple[int, int, int, int]]] = None,
                     tolerance: int = 5) -> List[StyleViolation]:
    """
    Validate canvas against palette constraints.

    Args:
        canvas: Canvas to validate
        max_colors: Maximum allowed unique colors (None = unlimited)
        required_palette: If set, all colors must be in this palette
        tolerance: Color matching tolerance for required_palette

    Returns:
        List of violations found
    """
    violations = []

    # Count unique colors
    colors: Dict[Tuple[int, int, int, int], int] = {}
    for y in range(canvas.height):
        for x in range(canvas.width):
            pixel = tuple(canvas.pixels[y][x])
            if pixel[3] > 0:  # Only count opaque pixels
                color = (pixel[0], pixel[1], pixel[2], pixel[3])
                colors[color] = colors.get(color, 0) + 1

    unique_count = len(colors)

    # Check max colors
    if max_colors is not None and unique_count > max_colors:
        violations.append(StyleViolation(
            violation_type=ViolationType.PALETTE_EXCEEDED,
            severity=ViolationSeverity.ERROR,
            description=f"Canvas has {unique_count} colors, max allowed is {max_colors}",
            details={"unique_colors": unique_count, "max_allowed": max_colors},
            suggestion=f"Reduce palette by {unique_count - max_colors} colors"
        ))

    # Check required palette
    if required_palette is not None:
        off_palette_colors = []
        for color, count in colors.items():
            is_match = False
            for palette_color in required_palette:
                dist = color_distance_weighted(color, palette_color)
                if dist <= tolerance:
                    is_match = True
                    break
            if not is_match:
                off_palette_colors.append((color, count))

        if off_palette_colors:
            total_off = sum(c[1] for c in off_palette_colors)
            violations.append(StyleViolation(
                violation_type=ViolationType.COLOR_NOT_IN_PALETTE,
                severity=ViolationSeverity.WARNING,
                description=f"{len(off_palette_colors)} colors not in required palette ({total_off} pixels)",
                details={"off_palette_colors": off_palette_colors[:5]},  # First 5
                suggestion="Remap colors to nearest palette entries"
            ))

    return violations


def check_contrast(canvas: Canvas, min_contrast: float = 0.3,
                   check_adjacent: bool = True) -> List[StyleViolation]:
    """
    Check that the canvas has sufficient contrast.

    Args:
        canvas: Canvas to validate
        min_contrast: Minimum contrast ratio (0-1)
        check_adjacent: Also check contrast between adjacent colors

    Returns:
        List of violations found
    """
    violations = []

    # Calculate brightness range
    brightnesses = []
    for y in range(canvas.height):
        for x in range(canvas.width):
            pixel = canvas.pixels[y][x]
            if pixel[3] > 0:
                brightness = (pixel[0] + pixel[1] + pixel[2]) / 3 / 255
                brightnesses.append(brightness)

    if not brightnesses:
        return violations

    min_bright = min(brightnesses)
    max_bright = max(brightnesses)
    contrast_range = max_bright - min_bright

    if contrast_range < min_contrast:
        violations.append(StyleViolation(
            violation_type=ViolationType.LOW_CONTRAST,
            severity=ViolationSeverity.WARNING,
            description=f"Low overall contrast ({contrast_range:.2f}), minimum is {min_contrast}",
            details={"contrast": contrast_range, "min_brightness": min_bright, "max_brightness": max_bright},
            suggestion="Increase brightness difference between darkest and lightest colors"
        ))

    # Check adjacent pixel contrast
    if check_adjacent:
        low_contrast_pairs = 0
        checked_pairs = 0

        for y in range(canvas.height):
            for x in range(canvas.width - 1):
                p1 = canvas.pixels[y][x]
                p2 = canvas.pixels[y][x + 1]

                # Only check if both opaque and different
                if p1[3] > 0 and p2[3] > 0 and p1 != p2:
                    checked_pairs += 1
                    b1 = (p1[0] + p1[1] + p1[2]) / 3 / 255
                    b2 = (p2[0] + p2[1] + p2[2]) / 3 / 255

                    if abs(b1 - b2) < 0.1:  # Very similar brightness
                        # Check if hue difference makes up for it
                        h1, s1, v1 = rgb_to_hsv(p1[0], p1[1], p1[2])
                        h2, s2, v2 = rgb_to_hsv(p2[0], p2[1], p2[2])

                        hue_diff = min(abs(h1 - h2), 360 - abs(h1 - h2)) / 180
                        if hue_diff < 0.2 and s1 > 0.2 and s2 > 0.2:
                            low_contrast_pairs += 1

        if checked_pairs > 0:
            low_contrast_ratio = low_contrast_pairs / checked_pairs
            if low_contrast_ratio > 0.3:
                violations.append(StyleViolation(
                    violation_type=ViolationType.LOW_CONTRAST,
                    severity=ViolationSeverity.INFO,
                    description=f"{low_contrast_ratio:.1%} of adjacent color pairs have low contrast",
                    details={"low_contrast_pairs": low_contrast_pairs, "total_pairs": checked_pairs},
                    suggestion="Consider increasing contrast between similar adjacent colors"
                ))

    return violations


def check_readability(canvas: Canvas, target_scale: int = 1) -> List[StyleViolation]:
    """
    Check if the sprite is readable at target scale.

    Args:
        canvas: Canvas to validate
        target_scale: Scale at which sprite will be displayed

    Returns:
        List of violations found
    """
    violations = []

    # For very small sprites, check if details are too fine
    effective_size = min(canvas.width, canvas.height) * target_scale

    if effective_size < 16:
        # Count single-pixel details
        single_pixels = 0
        total_opaque = 0

        for y in range(canvas.height):
            for x in range(canvas.width):
                pixel = canvas.pixels[y][x]
                if pixel[3] == 0:
                    continue

                total_opaque += 1

                # Check if isolated
                neighbors = 0
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < canvas.width and 0 <= ny < canvas.height:
                        if canvas.pixels[ny][nx][3] > 0:
                            # Check if similar color
                            dist = color_distance_weighted(
                                tuple(pixel), tuple(canvas.pixels[ny][nx])
                            )
                            if dist < 50:
                                neighbors += 1

                if neighbors == 0:
                    single_pixels += 1

        if total_opaque > 0:
            single_ratio = single_pixels / total_opaque
            if single_ratio > 0.2:
                violations.append(StyleViolation(
                    violation_type=ViolationType.LOW_CONTRAST,
                    severity=ViolationSeverity.INFO,
                    description=f"{single_ratio:.1%} of pixels are isolated - may be hard to see at {target_scale}x",
                    details={"single_pixels": single_pixels, "total_pixels": total_opaque},
                    suggestion="Simplify details or increase sprite size"
                ))

    return violations


def validate_outline(canvas: Canvas, style: Style) -> List[StyleViolation]:
    """
    Validate that outline follows style requirements.

    Args:
        canvas: Canvas to validate
        style: Style configuration to validate against

    Returns:
        List of violations found
    """
    violations = []

    if not style.outline.enabled:
        return violations  # No outline required

    # Find edge pixels
    edge_pixels = []
    for y in range(canvas.height):
        for x in range(canvas.width):
            pixel = canvas.pixels[y][x]
            if pixel[3] == 0:
                continue

            # Check if edge (adjacent to transparent)
            is_edge = False
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if not (0 <= nx < canvas.width and 0 <= ny < canvas.height):
                    is_edge = True
                elif canvas.pixels[ny][nx][3] == 0:
                    is_edge = True

            if is_edge:
                edge_pixels.append((x, y, pixel))

    if not edge_pixels:
        return violations

    # Check if edges have outline color
    outline_color = style.outline.color
    if outline_color is None:
        # Auto outline - just check that edge is darker than interior
        # This is a simplified check
        pass
    else:
        # Check edge pixels match outline color
        matching = 0
        for x, y, pixel in edge_pixels:
            dist = color_distance_weighted(
                (pixel[0], pixel[1], pixel[2], pixel[3]),
                outline_color
            )
            if dist < 30:
                matching += 1

        match_ratio = matching / len(edge_pixels) if edge_pixels else 0

        if style.outline.mode == 'external' and match_ratio < 0.5:
            violations.append(StyleViolation(
                violation_type=ViolationType.MISSING_OUTLINE,
                severity=ViolationSeverity.WARNING,
                description=f"Only {match_ratio:.1%} of edge pixels match outline color",
                details={"matching": matching, "total_edges": len(edge_pixels)},
                suggestion="Apply outline to edge pixels"
            ))

    return violations


def validate_animation(frames: List[Canvas], fps: int = 12,
                       check_smoothness: bool = True) -> List[StyleViolation]:
    """
    Validate animation quality.

    Args:
        frames: List of animation frames
        fps: Target frames per second
        check_smoothness: Check for jerky motion

    Returns:
        List of violations found
    """
    violations = []

    if len(frames) < 2:
        return violations

    # Check frame consistency
    first_size = (frames[0].width, frames[0].height)
    for i, frame in enumerate(frames[1:], 1):
        if (frame.width, frame.height) != first_size:
            violations.append(StyleViolation(
                violation_type=ViolationType.SIZE_VIOLATION,
                severity=ViolationSeverity.ERROR,
                description=f"Frame {i} size {frame.width}x{frame.height} doesn't match first frame {first_size[0]}x{first_size[1]}",
                details={"frame": i, "expected": first_size, "actual": (frame.width, frame.height)},
                suggestion="Ensure all frames have same dimensions"
            ))

    if not check_smoothness:
        return violations

    # Check for jerky motion (large changes between frames)
    prev_center = _get_sprite_center(frames[0])
    large_jumps = 0

    for i, frame in enumerate(frames[1:], 1):
        center = _get_sprite_center(frame)
        if prev_center and center:
            dx = abs(center[0] - prev_center[0])
            dy = abs(center[1] - prev_center[1])

            # Large jump relative to frame size
            max_jump = max(frame.width, frame.height) * 0.3
            if dx > max_jump or dy > max_jump:
                large_jumps += 1

        prev_center = center

    if large_jumps > 0:
        violations.append(StyleViolation(
            violation_type=ViolationType.ANIMATION_JITTER,
            severity=ViolationSeverity.INFO,
            description=f"{large_jumps} frame(s) have large position jumps",
            details={"jumpy_frames": large_jumps, "total_frames": len(frames)},
            suggestion="Add intermediate frames or reduce motion distance"
        ))

    return violations


def _get_sprite_center(canvas: Canvas) -> Optional[Tuple[float, float]]:
    """Calculate center of mass of opaque pixels."""
    sum_x, sum_y = 0, 0
    count = 0

    for y in range(canvas.height):
        for x in range(canvas.width):
            if canvas.pixels[y][x][3] > 0:
                sum_x += x
                sum_y += y
                count += 1

    if count == 0:
        return None

    return (sum_x / count, sum_y / count)


def validate_style(canvas: Canvas, style: Style) -> ValidationReport:
    """
    Validate canvas against a complete style configuration.

    Args:
        canvas: Canvas to validate
        style: Style to validate against

    Returns:
        Complete ValidationReport
    """
    report = ValidationReport(
        is_valid=True,
        style_name=style.name,
        checks_performed=[]
    )

    # Palette validation
    report.checks_performed.append("palette")
    if style.palette.max_colors is not None:
        palette_violations = validate_palette(
            canvas,
            max_colors=style.palette.max_colors,
            required_palette=style.palette.global_palette
        )
        report.violations.extend(palette_violations)

    # Outline validation
    report.checks_performed.append("outline")
    outline_violations = validate_outline(canvas, style)
    report.violations.extend(outline_violations)

    # Contrast validation
    report.checks_performed.append("contrast")
    contrast_violations = check_contrast(canvas)
    report.violations.extend(contrast_violations)

    # Readability
    report.checks_performed.append("readability")
    readability_violations = check_readability(canvas)
    report.violations.extend(readability_violations)

    # Determine overall validity
    report.is_valid = report.error_count == 0

    return report

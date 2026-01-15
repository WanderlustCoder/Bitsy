"""
Analyzer - Canvas analysis tools for detecting pixel art quality issues.

Detects common pixel art problems:
- Orphan pixels: Single isolated pixels that look like noise
- Jaggies: Stair-step patterns that should be smoothed
- Banding: Unwanted uniform gradient steps
- Poor silhouettes: Shapes that are unclear at small sizes
"""

import sys
import os
from typing import List, Tuple, Dict, Set, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Canvas
from core.color import color_distance_weighted, rgb_to_hsv


class IssueType(Enum):
    """Types of pixel art quality issues."""
    ORPHAN_PIXEL = "orphan_pixel"
    JAGGY = "jaggy"
    BANDING = "banding"
    LOW_CONTRAST = "low_contrast"
    BROKEN_SILHOUETTE = "broken_silhouette"
    STRAY_COLOR = "stray_color"


class IssueSeverity(Enum):
    """Severity levels for issues."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class PixelIssue:
    """A detected pixel art quality issue."""
    issue_type: IssueType
    severity: IssueSeverity
    x: int
    y: int
    width: int = 1
    height: int = 1
    description: str = ""
    suggestion: str = ""

    def __str__(self) -> str:
        return f"{self.severity.value.upper()}: {self.issue_type.value} at ({self.x}, {self.y}): {self.description}"


@dataclass
class ColorStatistics:
    """Statistics about colors in a canvas."""
    total_pixels: int
    opaque_pixels: int
    transparent_pixels: int
    unique_colors: int
    color_counts: Dict[Tuple[int, int, int, int], int]
    dominant_colors: List[Tuple[Tuple[int, int, int, int], int]]
    avg_brightness: float
    avg_saturation: float
    has_alpha_gradient: bool


@dataclass
class QualityReport:
    """Complete quality analysis report for a canvas."""
    canvas_size: Tuple[int, int]
    issues: List[PixelIssue] = field(default_factory=list)
    color_stats: Optional[ColorStatistics] = None
    silhouette_score: float = 1.0  # 0-1, higher is better
    overall_score: float = 1.0  # 0-1, higher is better

    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == IssueSeverity.ERROR)

    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == IssueSeverity.WARNING)

    @property
    def has_issues(self) -> bool:
        return len(self.issues) > 0

    def __str__(self) -> str:
        lines = [
            f"Quality Report ({self.canvas_size[0]}x{self.canvas_size[1]})",
            f"Overall Score: {self.overall_score:.2f}",
            f"Issues: {len(self.issues)} ({self.error_count} errors, {self.warning_count} warnings)",
        ]
        if self.issues:
            lines.append("\nIssues:")
            for issue in self.issues[:10]:  # Show first 10
                lines.append(f"  - {issue}")
            if len(self.issues) > 10:
                lines.append(f"  ... and {len(self.issues) - 10} more")
        return "\n".join(lines)


def get_color_statistics(canvas: Canvas) -> ColorStatistics:
    """
    Analyze color distribution in a canvas.

    Args:
        canvas: Canvas to analyze

    Returns:
        ColorStatistics with detailed color information
    """
    color_counts: Dict[Tuple[int, int, int, int], int] = {}
    opaque_pixels = 0
    transparent_pixels = 0
    brightness_sum = 0.0
    saturation_sum = 0.0
    alpha_values: Set[int] = set()

    for y in range(canvas.height):
        for x in range(canvas.width):
            pixel = tuple(canvas.pixels[y][x])
            color = (pixel[0], pixel[1], pixel[2], pixel[3])
            color_counts[color] = color_counts.get(color, 0) + 1
            alpha_values.add(pixel[3])

            if pixel[3] > 0:
                opaque_pixels += 1
                # Calculate brightness (simple average)
                brightness = (pixel[0] + pixel[1] + pixel[2]) / 3 / 255
                brightness_sum += brightness

                # Calculate saturation
                h, s, v = rgb_to_hsv(pixel[0], pixel[1], pixel[2])
                saturation_sum += s
            else:
                transparent_pixels += 1

    total_pixels = canvas.width * canvas.height

    # Sort by frequency
    sorted_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)

    return ColorStatistics(
        total_pixels=total_pixels,
        opaque_pixels=opaque_pixels,
        transparent_pixels=transparent_pixels,
        unique_colors=len(color_counts),
        color_counts=color_counts,
        dominant_colors=sorted_colors[:10],
        avg_brightness=brightness_sum / opaque_pixels if opaque_pixels > 0 else 0,
        avg_saturation=saturation_sum / opaque_pixels if opaque_pixels > 0 else 0,
        has_alpha_gradient=len(alpha_values - {0, 255}) > 0,
    )


def find_orphan_pixels(canvas: Canvas, threshold: int = 1) -> List[PixelIssue]:
    """
    Find isolated single pixels that may be unintentional.

    An orphan pixel is an opaque pixel with few or no opaque neighbors.

    Args:
        canvas: Canvas to analyze
        threshold: Maximum number of opaque neighbors to be considered orphan

    Returns:
        List of PixelIssue for each orphan pixel found
    """
    issues = []

    # Neighbor offsets (8-directional)
    neighbors = [
        (-1, -1), (0, -1), (1, -1),
        (-1, 0),          (1, 0),
        (-1, 1),  (0, 1),  (1, 1),
    ]

    for y in range(canvas.height):
        for x in range(canvas.width):
            pixel = canvas.pixels[y][x]

            # Skip transparent pixels
            if pixel[3] == 0:
                continue

            # Count opaque neighbors with similar color
            opaque_neighbors = 0
            similar_neighbors = 0

            for dx, dy in neighbors:
                nx, ny = x + dx, y + dy
                if 0 <= nx < canvas.width and 0 <= ny < canvas.height:
                    neighbor = canvas.pixels[ny][nx]
                    if neighbor[3] > 0:
                        opaque_neighbors += 1
                        # Check color similarity
                        dist = color_distance_weighted(
                            (pixel[0], pixel[1], pixel[2], pixel[3]),
                            (neighbor[0], neighbor[1], neighbor[2], neighbor[3])
                        )
                        if dist < 50:  # Similar color threshold
                            similar_neighbors += 1

            # Orphan if very few opaque neighbors
            if opaque_neighbors <= threshold:
                severity = IssueSeverity.WARNING if opaque_neighbors == 0 else IssueSeverity.INFO
                issues.append(PixelIssue(
                    issue_type=IssueType.ORPHAN_PIXEL,
                    severity=severity,
                    x=x, y=y,
                    description=f"Isolated pixel with {opaque_neighbors} neighbor(s)",
                    suggestion="Remove or connect to nearby pixels"
                ))

    return issues


def find_jaggies(canvas: Canvas, min_length: int = 3) -> List[PixelIssue]:
    """
    Find stair-step patterns (jaggies) in the image.

    Jaggies are diagonal lines that appear as obvious stair-steps
    rather than smooth diagonals.

    Args:
        canvas: Canvas to analyze
        min_length: Minimum length of jaggy pattern to report

    Returns:
        List of PixelIssue for jaggy patterns found
    """
    issues = []
    visited: Set[Tuple[int, int]] = set()

    # Patterns that indicate jaggies (1-1 stair steps)
    # A smooth diagonal should have varying step lengths (1-2-1-2 or 2-1-2-1)
    jaggy_patterns = [
        [(0, 0), (1, 1), (2, 2), (3, 3)],  # Perfect diagonal = jaggy
        [(0, 0), (1, -1), (2, -2), (3, -3)],
    ]

    for y in range(canvas.height):
        for x in range(canvas.width):
            if (x, y) in visited:
                continue

            pixel = canvas.pixels[y][x]
            if pixel[3] == 0:
                continue

            # Check for jaggy pattern starting here
            for pattern in jaggy_patterns:
                jaggy_length = 0
                pattern_pixels = []

                for dx, dy in pattern:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < canvas.width and 0 <= ny < canvas.height:
                        neighbor = canvas.pixels[ny][nx]
                        if neighbor[3] > 0:
                            # Check if edge pixel (has transparent neighbor)
                            is_edge = False
                            for ddx, ddy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                                nnx, nny = nx + ddx, ny + ddy
                                if 0 <= nnx < canvas.width and 0 <= nny < canvas.height:
                                    if canvas.pixels[nny][nnx][3] == 0:
                                        is_edge = True
                                        break
                                else:
                                    is_edge = True
                                    break

                            if is_edge:
                                jaggy_length += 1
                                pattern_pixels.append((nx, ny))
                            else:
                                break
                        else:
                            break
                    else:
                        break

                if jaggy_length >= min_length:
                    # Mark as visited
                    for px, py in pattern_pixels:
                        visited.add((px, py))

                    issues.append(PixelIssue(
                        issue_type=IssueType.JAGGY,
                        severity=IssueSeverity.INFO,
                        x=x, y=y,
                        width=jaggy_length,
                        height=jaggy_length,
                        description=f"Stair-step pattern of length {jaggy_length}",
                        suggestion="Consider anti-aliasing or varying step lengths"
                    ))

    return issues


def detect_banding(canvas: Canvas, min_band_width: int = 3) -> List[PixelIssue]:
    """
    Detect color banding - uniform gradient steps that look artificial.

    Banding occurs when gradients have visible steps instead of smooth
    transitions, often from using too few colors.

    Args:
        canvas: Canvas to analyze
        min_band_width: Minimum width of color band to report

    Returns:
        List of PixelIssue for banding regions found
    """
    issues = []
    visited: Set[Tuple[int, int]] = set()

    for y in range(canvas.height):
        band_start = None
        band_color = None
        band_length = 0

        for x in range(canvas.width):
            if (x, y) in visited:
                continue

            pixel = tuple(canvas.pixels[y][x])

            if pixel[3] == 0:
                # End of any current band
                if band_length >= min_band_width:
                    # Check if this band is part of a gradient
                    _check_band_for_gradient(
                        canvas, band_start, y, band_length, band_color,
                        issues, visited
                    )
                band_start = None
                band_color = None
                band_length = 0
                continue

            color = (pixel[0], pixel[1], pixel[2])

            if band_color is None:
                band_start = x
                band_color = color
                band_length = 1
            elif color == band_color:
                band_length += 1
            else:
                # Different color - check previous band
                if band_length >= min_band_width:
                    _check_band_for_gradient(
                        canvas, band_start, y, band_length, band_color,
                        issues, visited
                    )
                band_start = x
                band_color = color
                band_length = 1

        # Check final band in row
        if band_length >= min_band_width:
            _check_band_for_gradient(
                canvas, band_start, y, band_length, band_color,
                issues, visited
            )

    return issues


def _check_band_for_gradient(
    canvas: Canvas,
    start_x: int,
    y: int,
    length: int,
    color: Tuple[int, int, int],
    issues: List[PixelIssue],
    visited: Set[Tuple[int, int]]
) -> None:
    """Check if a color band is part of a banding pattern."""
    if start_x is None or color is None:
        return

    # Check colors above and below
    colors_adjacent = []

    for check_y in [y - 1, y + 1]:
        if 0 <= check_y < canvas.height:
            mid_x = start_x + length // 2
            if 0 <= mid_x < canvas.width:
                adj_pixel = canvas.pixels[check_y][mid_x]
                if adj_pixel[3] > 0:
                    colors_adjacent.append((adj_pixel[0], adj_pixel[1], adj_pixel[2]))

    # If adjacent colors are different but similar (gradient), it's banding
    if len(colors_adjacent) >= 1:
        for adj_color in colors_adjacent:
            dist = sum(abs(a - b) for a, b in zip(color, adj_color))
            # Similar but not identical = likely gradient banding
            if 10 < dist < 80:
                for x in range(start_x, start_x + length):
                    visited.add((x, y))

                issues.append(PixelIssue(
                    issue_type=IssueType.BANDING,
                    severity=IssueSeverity.INFO,
                    x=start_x, y=y,
                    width=length, height=1,
                    description=f"Color band of width {length} in gradient",
                    suggestion="Add dithering or intermediate colors"
                ))
                break


def check_silhouette(canvas: Canvas, min_size: int = 1) -> Tuple[float, List[PixelIssue]]:
    """
    Analyze the silhouette clarity of a sprite.

    A good silhouette is recognizable even at small sizes or as a solid shape.

    Args:
        canvas: Canvas to analyze
        min_size: Minimum detail size to consider

    Returns:
        Tuple of (silhouette_score 0-1, list of issues)
    """
    issues = []

    # Create silhouette (all opaque pixels as one color)
    silhouette_pixels = 0
    boundary_pixels = 0
    holes = 0

    # Find opaque region bounds
    min_x, min_y = canvas.width, canvas.height
    max_x, max_y = 0, 0

    for y in range(canvas.height):
        for x in range(canvas.width):
            if canvas.pixels[y][x][3] > 0:
                silhouette_pixels += 1
                min_x = min(min_x, x)
                max_x = max(max_x, x)
                min_y = min(min_y, y)
                max_y = max(max_y, y)

                # Check if boundary pixel
                is_boundary = False
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nx, ny = x + dx, y + dy
                    if not (0 <= nx < canvas.width and 0 <= ny < canvas.height):
                        is_boundary = True
                    elif canvas.pixels[ny][nx][3] == 0:
                        is_boundary = True
                if is_boundary:
                    boundary_pixels += 1

    if silhouette_pixels == 0:
        return 0.0, [PixelIssue(
            issue_type=IssueType.BROKEN_SILHOUETTE,
            severity=IssueSeverity.ERROR,
            x=0, y=0,
            description="Canvas is completely transparent",
            suggestion="Add opaque pixels"
        )]

    # Calculate metrics
    width = max_x - min_x + 1
    height = max_y - min_y + 1
    bounding_area = width * height
    fill_ratio = silhouette_pixels / bounding_area if bounding_area > 0 else 0
    boundary_ratio = boundary_pixels / silhouette_pixels if silhouette_pixels > 0 else 0

    # Score based on:
    # - Fill ratio (higher = more solid, better silhouette)
    # - Boundary ratio (lower = smoother edges)
    score = min(1.0, fill_ratio * 1.2) * (1.0 - min(0.5, boundary_ratio * 0.5))

    if fill_ratio < 0.3:
        issues.append(PixelIssue(
            issue_type=IssueType.BROKEN_SILHOUETTE,
            severity=IssueSeverity.WARNING,
            x=min_x, y=min_y, width=width, height=height,
            description=f"Low fill ratio ({fill_ratio:.1%}) - silhouette may be unclear",
            suggestion="Consider filling gaps or simplifying shape"
        ))

    if boundary_ratio > 0.6:
        issues.append(PixelIssue(
            issue_type=IssueType.BROKEN_SILHOUETTE,
            severity=IssueSeverity.INFO,
            x=min_x, y=min_y, width=width, height=height,
            description=f"High boundary ratio ({boundary_ratio:.1%}) - very detailed edge",
            suggestion="May lose detail at small sizes"
        ))

    return score, issues


def analyze_canvas(canvas: Canvas, check_all: bool = True) -> QualityReport:
    """
    Perform comprehensive quality analysis on a canvas.

    Args:
        canvas: Canvas to analyze
        check_all: If True, run all checks. If False, only basic checks.

    Returns:
        QualityReport with all findings
    """
    report = QualityReport(
        canvas_size=(canvas.width, canvas.height)
    )

    # Get color statistics
    report.color_stats = get_color_statistics(canvas)

    # Find issues
    if check_all:
        # Orphan pixels
        orphans = find_orphan_pixels(canvas)
        report.issues.extend(orphans)

        # Jaggies
        jaggies = find_jaggies(canvas)
        report.issues.extend(jaggies)

        # Banding
        banding = detect_banding(canvas)
        report.issues.extend(banding)

    # Silhouette check
    silhouette_score, silhouette_issues = check_silhouette(canvas)
    report.silhouette_score = silhouette_score
    report.issues.extend(silhouette_issues)

    # Calculate overall score
    error_penalty = report.error_count * 0.2
    warning_penalty = report.warning_count * 0.05
    info_penalty = len([i for i in report.issues if i.severity == IssueSeverity.INFO]) * 0.01

    report.overall_score = max(0.0, min(1.0,
        report.silhouette_score - error_penalty - warning_penalty - info_penalty
    ))

    return report


def find_stray_colors(canvas: Canvas, expected_palette: List[Tuple[int, int, int, int]],
                      tolerance: int = 10) -> List[PixelIssue]:
    """
    Find pixels that don't match the expected palette.

    Args:
        canvas: Canvas to analyze
        expected_palette: List of expected RGBA colors
        tolerance: Maximum color distance to consider a match

    Returns:
        List of PixelIssue for stray colors
    """
    issues = []
    stray_colors: Dict[Tuple[int, int, int, int], List[Tuple[int, int]]] = {}

    for y in range(canvas.height):
        for x in range(canvas.width):
            pixel = tuple(canvas.pixels[y][x])

            if pixel[3] == 0:
                continue

            # Check against palette
            is_match = False
            for palette_color in expected_palette:
                dist = color_distance_weighted(pixel, palette_color)
                if dist <= tolerance:
                    is_match = True
                    break

            if not is_match:
                color = (pixel[0], pixel[1], pixel[2], pixel[3])
                if color not in stray_colors:
                    stray_colors[color] = []
                stray_colors[color].append((x, y))

    # Report each stray color
    for color, positions in stray_colors.items():
        # Report first occurrence
        x, y = positions[0]
        issues.append(PixelIssue(
            issue_type=IssueType.STRAY_COLOR,
            severity=IssueSeverity.WARNING,
            x=x, y=y,
            description=f"Color RGBA{color} not in palette ({len(positions)} pixels)",
            suggestion="Remap to nearest palette color"
        ))

    return issues

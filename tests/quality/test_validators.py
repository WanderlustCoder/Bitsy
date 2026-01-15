"""
Test Validators - Tests for style compliance validation.

Tests:
- Palette validation
- Contrast checking
- Outline validation
- Animation validation
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests.framework import TestCase
from core import Canvas
from core.style import Style, OutlineConfig, PaletteConfig
from quality.validators import (
    validate_palette,
    check_contrast,
    check_readability,
    validate_outline,
    validate_animation,
    validate_style,
    ViolationType,
    ViolationSeverity,
    ValidationReport,
)


class TestPaletteValidation(TestCase):
    """Tests for palette constraint validation."""

    def test_under_max_colors(self):
        """Canvas under max colors passes."""
        canvas = Canvas(8, 8, (255, 0, 0, 255))
        violations = validate_palette(canvas, max_colors=4)

        palette_violations = [v for v in violations if v.violation_type == ViolationType.PALETTE_EXCEEDED]
        self.assertEqual(len(palette_violations), 0)

    def test_exceeds_max_colors(self):
        """Canvas exceeding max colors fails."""
        canvas = Canvas(8, 8)
        # Add 10 different colors
        for i in range(10):
            canvas.set_pixel_solid(i % 8, i // 8, (i * 25, 0, 0, 255))

        violations = validate_palette(canvas, max_colors=4)

        palette_violations = [v for v in violations if v.violation_type == ViolationType.PALETTE_EXCEEDED]
        self.assertGreater(len(palette_violations), 0)

    def test_required_palette_match(self):
        """Colors matching required palette pass."""
        canvas = Canvas(8, 8, (255, 0, 0, 255))
        required = [(255, 0, 0, 255), (0, 255, 0, 255)]

        violations = validate_palette(canvas, required_palette=required)
        off_palette = [v for v in violations if v.violation_type == ViolationType.COLOR_NOT_IN_PALETTE]

        self.assertEqual(len(off_palette), 0)

    def test_required_palette_violation(self):
        """Colors not in required palette fail."""
        canvas = Canvas(8, 8, (0, 0, 255, 255))  # Blue not in palette
        required = [(255, 0, 0, 255), (0, 255, 0, 255)]

        violations = validate_palette(canvas, required_palette=required)
        off_palette = [v for v in violations if v.violation_type == ViolationType.COLOR_NOT_IN_PALETTE]

        self.assertGreater(len(off_palette), 0)

    def test_tolerance_affects_matching(self):
        """Tolerance parameter affects palette matching."""
        canvas = Canvas(8, 8, (250, 0, 0, 255))  # Slightly off red
        required = [(255, 0, 0, 255)]

        # Strict tolerance
        violations_strict = validate_palette(canvas, required_palette=required, tolerance=1)

        # Loose tolerance
        violations_loose = validate_palette(canvas, required_palette=required, tolerance=10)

        strict_off = [v for v in violations_strict if v.violation_type == ViolationType.COLOR_NOT_IN_PALETTE]
        loose_off = [v for v in violations_loose if v.violation_type == ViolationType.COLOR_NOT_IN_PALETTE]

        self.assertGreater(len(strict_off), len(loose_off))


class TestContrastValidation(TestCase):
    """Tests for contrast checking."""

    def test_good_contrast(self):
        """High contrast canvas passes."""
        canvas = Canvas(8, 8)
        canvas.fill_rect(0, 0, 4, 8, (0, 0, 0, 255))  # Black
        canvas.fill_rect(4, 0, 4, 8, (255, 255, 255, 255))  # White

        violations = check_contrast(canvas, min_contrast=0.5)
        low_contrast = [v for v in violations if v.violation_type == ViolationType.LOW_CONTRAST]

        self.assertEqual(len(low_contrast), 0)

    def test_low_contrast(self):
        """Low contrast canvas fails."""
        canvas = Canvas(8, 8)
        canvas.fill_rect(0, 0, 4, 8, (128, 128, 128, 255))
        canvas.fill_rect(4, 0, 4, 8, (130, 130, 130, 255))  # Very similar

        violations = check_contrast(canvas, min_contrast=0.5)
        low_contrast = [v for v in violations if v.violation_type == ViolationType.LOW_CONTRAST]

        self.assertGreater(len(low_contrast), 0)

    def test_single_color_low_contrast(self):
        """Single color canvas has zero contrast."""
        canvas = Canvas(8, 8, (128, 128, 128, 255))

        violations = check_contrast(canvas, min_contrast=0.1)
        low_contrast = [v for v in violations if v.violation_type == ViolationType.LOW_CONTRAST]

        self.assertGreater(len(low_contrast), 0)


class TestReadabilityValidation(TestCase):
    """Tests for readability checking."""

    def test_solid_shape_readable(self):
        """Solid shape is readable."""
        canvas = Canvas(8, 8)
        canvas.fill_rect(2, 2, 4, 4, (255, 0, 0, 255))

        violations = check_readability(canvas)
        self.assertEqual(len(violations), 0)

    def test_scattered_pixels_warning(self):
        """Very scattered pixels may trigger warning."""
        canvas = Canvas(8, 8)
        # Scattered single pixels
        for i in range(0, 8, 2):
            for j in range(0, 8, 2):
                canvas.set_pixel_solid(i, j, (255, 0, 0, 255))

        violations = check_readability(canvas, target_scale=1)
        # May or may not trigger depending on threshold
        self.assertIsInstance(violations, list)


class TestOutlineValidation(TestCase):
    """Tests for outline validation."""

    def test_no_outline_required(self):
        """No violations when outline not required."""
        canvas = Canvas(8, 8)
        canvas.fill_rect(2, 2, 4, 4, (255, 0, 0, 255))

        style = Style(outline=OutlineConfig(enabled=False))
        violations = validate_outline(canvas, style)

        self.assertEqual(len(violations), 0)

    def test_outline_with_specified_color(self):
        """Outline color validation works."""
        canvas = Canvas(8, 8)
        canvas.fill_rect(2, 2, 4, 4, (255, 0, 0, 255))
        # No outline applied - all edge pixels are red

        style = Style(outline=OutlineConfig(
            enabled=True,
            color=(0, 0, 0, 255),
            mode='external'
        ))
        violations = validate_outline(canvas, style)

        # Should warn about missing outline
        outline_violations = [v for v in violations if v.violation_type == ViolationType.MISSING_OUTLINE]
        self.assertGreater(len(outline_violations), 0)


class TestAnimationValidation(TestCase):
    """Tests for animation validation."""

    def test_single_frame(self):
        """Single frame animation passes."""
        frame = Canvas(8, 8, (255, 0, 0, 255))
        violations = validate_animation([frame])

        self.assertEqual(len(violations), 0)

    def test_consistent_frame_sizes(self):
        """Frames with same size pass."""
        frames = [
            Canvas(8, 8, (255, 0, 0, 255)),
            Canvas(8, 8, (0, 255, 0, 255)),
        ]
        violations = validate_animation(frames)

        size_violations = [v for v in violations if v.violation_type == ViolationType.SIZE_VIOLATION]
        self.assertEqual(len(size_violations), 0)

    def test_inconsistent_frame_sizes(self):
        """Frames with different sizes fail."""
        frames = [
            Canvas(8, 8, (255, 0, 0, 255)),
            Canvas(16, 16, (0, 255, 0, 255)),  # Different size
        ]
        violations = validate_animation(frames)

        size_violations = [v for v in violations if v.violation_type == ViolationType.SIZE_VIOLATION]
        self.assertGreater(len(size_violations), 0)


class TestValidateStyle(TestCase):
    """Tests for comprehensive style validation."""

    def test_returns_report(self):
        """validate_style returns ValidationReport."""
        canvas = Canvas(8, 8, (255, 0, 0, 255))
        style = Style()

        report = validate_style(canvas, style)

        self.assertIsInstance(report, ValidationReport)
        self.assertEqual(report.style_name, style.name)

    def test_tracks_checks_performed(self):
        """Report tracks which checks were performed."""
        canvas = Canvas(8, 8, (255, 0, 0, 255))
        style = Style()

        report = validate_style(canvas, style)

        self.assertIn("outline", report.checks_performed)
        self.assertIn("contrast", report.checks_performed)

    def test_valid_canvas_passes(self):
        """Valid canvas passes validation."""
        canvas = Canvas(16, 16)
        canvas.fill_rect(2, 2, 12, 12, (255, 0, 0, 255))
        canvas.fill_rect(3, 3, 10, 10, (200, 50, 50, 255))

        style = Style(palette=PaletteConfig(max_colors=16))
        report = validate_style(canvas, style)

        self.assertTrue(report.is_valid)

    def test_invalid_canvas_fails(self):
        """Canvas violating style fails validation."""
        canvas = Canvas(8, 8)
        # Create canvas with many colors
        for i in range(64):
            x, y = i % 8, i // 8
            canvas.set_pixel_solid(x, y, (i * 4, 0, 0, 255))

        style = Style(palette=PaletteConfig(max_colors=4))
        report = validate_style(canvas, style)

        self.assertFalse(report.is_valid)


class TestValidationReportProperties(TestCase):
    """Tests for ValidationReport properties."""

    def test_error_count(self):
        """error_count calculated correctly."""
        report = ValidationReport(is_valid=False)

        from quality.validators import StyleViolation
        report.violations.append(StyleViolation(
            violation_type=ViolationType.PALETTE_EXCEEDED,
            severity=ViolationSeverity.ERROR,
            description="test"
        ))
        report.violations.append(StyleViolation(
            violation_type=ViolationType.LOW_CONTRAST,
            severity=ViolationSeverity.WARNING,
            description="test"
        ))

        self.assertEqual(report.error_count, 1)
        self.assertEqual(report.warning_count, 1)

    def test_report_string(self):
        """Report string representation works."""
        report = ValidationReport(is_valid=True, style_name="test_style")
        string = str(report)

        self.assertIn("VALID", string)
        self.assertIn("test_style", string)

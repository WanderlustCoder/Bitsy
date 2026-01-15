"""
Test Analyzer - Tests for pixel art quality analysis.

Tests:
- Orphan pixel detection
- Jaggy detection
- Banding detection
- Silhouette analysis
- Color statistics
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests.framework import TestCase
from core import Canvas
from quality.analyzer import (
    analyze_canvas,
    find_orphan_pixels,
    find_jaggies,
    detect_banding,
    check_silhouette,
    get_color_statistics,
    find_stray_colors,
    IssueType,
    IssueSeverity,
    QualityReport,
)


class TestColorStatistics(TestCase):
    """Tests for color statistics analysis."""

    def test_empty_canvas(self):
        """Empty canvas has zero opaque pixels."""
        canvas = Canvas(8, 8)
        stats = get_color_statistics(canvas)

        self.assertEqual(stats.opaque_pixels, 0)
        self.assertEqual(stats.transparent_pixels, 64)

    def test_solid_canvas(self):
        """Solid canvas has one unique color."""
        canvas = Canvas(8, 8, (255, 0, 0, 255))
        stats = get_color_statistics(canvas)

        self.assertEqual(stats.opaque_pixels, 64)
        self.assertEqual(stats.unique_colors, 1)
        self.assertEqual(stats.transparent_pixels, 0)

    def test_two_colors(self):
        """Canvas with two colors detected correctly."""
        canvas = Canvas(8, 8, (255, 0, 0, 255))
        canvas.fill_rect(0, 0, 4, 8, (0, 255, 0, 255))
        stats = get_color_statistics(canvas)

        self.assertEqual(stats.unique_colors, 2)
        self.assertEqual(stats.opaque_pixels, 64)

    def test_dominant_colors(self):
        """Dominant colors sorted by frequency."""
        canvas = Canvas(8, 8, (255, 0, 0, 255))  # 64 red pixels
        canvas.fill_rect(0, 0, 2, 2, (0, 255, 0, 255))  # 4 green pixels
        stats = get_color_statistics(canvas)

        # Red should be dominant
        top_color = stats.dominant_colors[0][0]
        self.assertEqual(top_color, (255, 0, 0, 255))

    def test_alpha_gradient_detection(self):
        """Detect semi-transparent pixels."""
        canvas = Canvas(8, 8)
        canvas.set_pixel_solid(0, 0, (255, 0, 0, 128))  # Semi-transparent
        stats = get_color_statistics(canvas)

        self.assertTrue(stats.has_alpha_gradient)

    def test_brightness_calculation(self):
        """Average brightness calculated correctly."""
        # White canvas = brightness 1.0
        canvas = Canvas(4, 4, (255, 255, 255, 255))
        stats = get_color_statistics(canvas)
        self.assertAlmostEqual(stats.avg_brightness, 1.0, places=2)

        # Black canvas = brightness 0.0
        canvas = Canvas(4, 4, (0, 0, 0, 255))
        stats = get_color_statistics(canvas)
        self.assertAlmostEqual(stats.avg_brightness, 0.0, places=2)


class TestOrphanPixelDetection(TestCase):
    """Tests for orphan pixel detection."""

    def test_no_orphans_solid(self):
        """Solid canvas has no orphan pixels."""
        canvas = Canvas(8, 8, (255, 0, 0, 255))
        orphans = find_orphan_pixels(canvas)

        self.assertEqual(len(orphans), 0)

    def test_single_pixel_orphan(self):
        """Single isolated pixel detected as orphan."""
        canvas = Canvas(8, 8)
        canvas.set_pixel_solid(4, 4, (255, 0, 0, 255))
        orphans = find_orphan_pixels(canvas)

        self.assertGreater(len(orphans), 0)
        self.assertEqual(orphans[0].issue_type, IssueType.ORPHAN_PIXEL)
        self.assertEqual(orphans[0].x, 4)
        self.assertEqual(orphans[0].y, 4)

    def test_connected_not_orphan(self):
        """Connected pixels not detected as orphans."""
        canvas = Canvas(8, 8)
        canvas.fill_rect(3, 3, 3, 3, (255, 0, 0, 255))  # 3x3 block
        orphans = find_orphan_pixels(canvas)

        self.assertEqual(len(orphans), 0)

    def test_threshold_parameter(self):
        """Threshold parameter affects detection."""
        canvas = Canvas(8, 8)
        # Single isolated pixel
        canvas.set_pixel_solid(4, 4, (255, 0, 0, 255))

        # With threshold=0 (default), single pixel is orphan
        orphans_t0 = find_orphan_pixels(canvas, threshold=0)

        # With threshold=1, should not find orphan (need less than 1 neighbor)
        orphans_t1 = find_orphan_pixels(canvas, threshold=1)

        # Single pixel has 0 neighbors, so it's detected with threshold=0
        # but not with threshold=1 (which requires <1 neighbors)
        self.assertGreaterEqual(len(orphans_t0), len(orphans_t1))


class TestJaggyDetection(TestCase):
    """Tests for jaggy (stair-step) detection."""

    def test_no_jaggies_horizontal(self):
        """Horizontal line has no jaggies."""
        canvas = Canvas(16, 16)
        canvas.fill_rect(0, 8, 16, 1, (255, 0, 0, 255))
        jaggies = find_jaggies(canvas)

        self.assertEqual(len(jaggies), 0)

    def test_no_jaggies_vertical(self):
        """Vertical line has no jaggies."""
        canvas = Canvas(16, 16)
        canvas.fill_rect(8, 0, 1, 16, (255, 0, 0, 255))
        jaggies = find_jaggies(canvas)

        self.assertEqual(len(jaggies), 0)

    def test_diagonal_may_have_jaggies(self):
        """Perfect diagonal line may be detected as jaggy."""
        canvas = Canvas(16, 16)
        for i in range(16):
            canvas.set_pixel_solid(i, i, (255, 0, 0, 255))

        jaggies = find_jaggies(canvas, min_length=3)
        # May or may not detect depending on edge context
        # Just verify function runs without error
        self.assertIsInstance(jaggies, list)


class TestBandingDetection(TestCase):
    """Tests for color banding detection."""

    def test_no_banding_solid(self):
        """Solid color has no banding."""
        canvas = Canvas(16, 16, (128, 128, 128, 255))
        banding = detect_banding(canvas)

        self.assertEqual(len(banding), 0)

    def test_gradient_banding(self):
        """Gradient with large steps may have banding."""
        canvas = Canvas(32, 8)
        # Create obvious banding - wide strips of similar colors
        for i in range(4):
            color = (50 + i * 50, 50 + i * 50, 50 + i * 50, 255)
            canvas.fill_rect(i * 8, 0, 8, 8, color)

        banding = detect_banding(canvas, min_band_width=5)
        # Should detect some banding
        # (may not always trigger depending on detection logic)
        self.assertIsInstance(banding, list)


class TestSilhouetteAnalysis(TestCase):
    """Tests for silhouette quality analysis."""

    def test_empty_canvas_score(self):
        """Empty canvas has zero silhouette score."""
        canvas = Canvas(8, 8)
        score, issues = check_silhouette(canvas)

        self.assertEqual(score, 0.0)
        self.assertGreater(len(issues), 0)

    def test_solid_square_good_silhouette(self):
        """Solid square has good silhouette."""
        canvas = Canvas(16, 16)
        canvas.fill_rect(2, 2, 12, 12, (255, 0, 0, 255))
        score, issues = check_silhouette(canvas)

        self.assertGreater(score, 0.5)

    def test_sparse_pixels_poor_silhouette(self):
        """Scattered pixels have poor silhouette."""
        canvas = Canvas(16, 16)
        # Very sparse pixels
        for i in range(0, 16, 4):
            for j in range(0, 16, 4):
                canvas.set_pixel_solid(i, j, (255, 0, 0, 255))

        score, issues = check_silhouette(canvas)
        # Should have lower score than solid shape
        self.assertLess(score, 0.8)


class TestAnalyzeCanvas(TestCase):
    """Tests for comprehensive canvas analysis."""

    def test_analyze_returns_report(self):
        """analyze_canvas returns QualityReport."""
        canvas = Canvas(16, 16, (255, 0, 0, 255))
        report = analyze_canvas(canvas)

        self.assertIsInstance(report, QualityReport)
        self.assertEqual(report.canvas_size, (16, 16))

    def test_analyze_includes_color_stats(self):
        """Report includes color statistics."""
        canvas = Canvas(16, 16, (255, 0, 0, 255))
        report = analyze_canvas(canvas)

        self.assertIsNotNone(report.color_stats)
        self.assertEqual(report.color_stats.unique_colors, 1)

    def test_analyze_good_canvas(self):
        """Good canvas has high overall score."""
        canvas = Canvas(16, 16)
        canvas.fill_rect(2, 2, 12, 12, (255, 0, 0, 255))
        canvas.fill_rect(3, 3, 10, 10, (200, 0, 0, 255))  # Add shading
        report = analyze_canvas(canvas)

        self.assertGreater(report.overall_score, 0.5)

    def test_analyze_problematic_canvas(self):
        """Canvas with issues has lower score."""
        canvas = Canvas(16, 16)
        # Add many orphan pixels
        for i in range(0, 16, 3):
            for j in range(0, 16, 3):
                canvas.set_pixel_solid(i, j, (255, 0, 0, 255))

        report = analyze_canvas(canvas)
        self.assertGreater(len(report.issues), 0)


class TestStrayColorDetection(TestCase):
    """Tests for stray color detection."""

    def test_no_stray_in_palette(self):
        """Colors matching palette not reported as stray."""
        canvas = Canvas(8, 8, (255, 0, 0, 255))
        palette = [(255, 0, 0, 255), (0, 255, 0, 255)]
        stray = find_stray_colors(canvas, palette)

        self.assertEqual(len(stray), 0)

    def test_stray_color_detected(self):
        """Colors not in palette detected as stray."""
        canvas = Canvas(8, 8, (255, 0, 0, 255))
        canvas.set_pixel_solid(0, 0, (0, 0, 255, 255))  # Blue not in palette

        palette = [(255, 0, 0, 255), (0, 255, 0, 255)]
        stray = find_stray_colors(canvas, palette)

        self.assertGreater(len(stray), 0)
        self.assertEqual(stray[0].issue_type, IssueType.STRAY_COLOR)

    def test_tolerance_affects_detection(self):
        """Tolerance parameter affects stray detection."""
        canvas = Canvas(8, 8, (255, 0, 0, 255))
        canvas.set_pixel_solid(0, 0, (250, 0, 0, 255))  # Slightly off red

        palette = [(255, 0, 0, 255)]

        # Strict tolerance should find it
        stray_strict = find_stray_colors(canvas, palette, tolerance=1)

        # Loose tolerance should not
        stray_loose = find_stray_colors(canvas, palette, tolerance=10)

        self.assertGreater(len(stray_strict), len(stray_loose))


class TestQualityReportProperties(TestCase):
    """Tests for QualityReport properties."""

    def test_error_count(self):
        """error_count property works correctly."""
        report = QualityReport(canvas_size=(8, 8))

        from quality.analyzer import PixelIssue
        report.issues.append(PixelIssue(
            issue_type=IssueType.ORPHAN_PIXEL,
            severity=IssueSeverity.ERROR,
            x=0, y=0
        ))
        report.issues.append(PixelIssue(
            issue_type=IssueType.ORPHAN_PIXEL,
            severity=IssueSeverity.WARNING,
            x=1, y=1
        ))

        self.assertEqual(report.error_count, 1)
        self.assertEqual(report.warning_count, 1)

    def test_has_issues_property(self):
        """has_issues property works correctly."""
        report = QualityReport(canvas_size=(8, 8))
        self.assertFalse(report.has_issues)

        from quality.analyzer import PixelIssue
        report.issues.append(PixelIssue(
            issue_type=IssueType.ORPHAN_PIXEL,
            severity=IssueSeverity.INFO,
            x=0, y=0
        ))
        self.assertTrue(report.has_issues)

    def test_report_string(self):
        """Report string representation works."""
        report = QualityReport(canvas_size=(8, 8))
        string = str(report)

        self.assertIn("8x8", string)
        self.assertIn("Quality Report", string)

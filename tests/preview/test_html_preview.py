"""
Test HTML Preview - Tests for HTML preview generation.

Tests:
- Data URI generation
- HTML structure
- Preview options
- Multi-canvas preview
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests.framework import TestCase
from core import Canvas
from preview.html_preview import (
    canvas_to_data_uri,
    generate_preview_html,
    generate_preview_page,
    generate_multi_preview_html,
    PreviewOptions,
)


class TestCanvasToDataUri(TestCase):
    """Tests for data URI generation."""

    def test_returns_string(self):
        """canvas_to_data_uri returns a string."""
        canvas = Canvas(8, 8, (255, 0, 0, 255))
        uri = canvas_to_data_uri(canvas)

        self.assertIsInstance(uri, str)

    def test_starts_with_data_prefix(self):
        """Data URI has correct prefix."""
        canvas = Canvas(8, 8, (255, 0, 0, 255))
        uri = canvas_to_data_uri(canvas)

        self.assertTrue(uri.startswith("data:image/png;base64,"))

    def test_contains_base64_data(self):
        """Data URI contains base64 encoded content."""
        canvas = Canvas(8, 8, (255, 0, 0, 255))
        uri = canvas_to_data_uri(canvas)

        # Should have substantial base64 content after prefix
        base64_part = uri.split(",")[1]
        self.assertGreater(len(base64_part), 10)

    def test_different_canvases_different_uris(self):
        """Different canvases produce different URIs."""
        canvas1 = Canvas(8, 8, (255, 0, 0, 255))
        canvas2 = Canvas(8, 8, (0, 255, 0, 255))

        uri1 = canvas_to_data_uri(canvas1)
        uri2 = canvas_to_data_uri(canvas2)

        self.assertNotEqual(uri1, uri2)


class TestGeneratePreviewHtml(TestCase):
    """Tests for HTML preview generation."""

    def test_returns_html_string(self):
        """generate_preview_html returns HTML string."""
        canvas = Canvas(16, 16, (255, 0, 0, 255))
        html = generate_preview_html(canvas)

        self.assertIsInstance(html, str)
        self.assertTrue(html.startswith("<!DOCTYPE html>"))

    def test_contains_doctype(self):
        """HTML contains DOCTYPE declaration."""
        canvas = Canvas(16, 16, (255, 0, 0, 255))
        html = generate_preview_html(canvas)

        self.assertIn("<!DOCTYPE html>", html)

    def test_contains_data_uri(self):
        """HTML contains embedded data URI."""
        canvas = Canvas(16, 16, (255, 0, 0, 255))
        html = generate_preview_html(canvas)

        self.assertIn("data:image/png;base64,", html)

    def test_contains_image_tags(self):
        """HTML contains image tags."""
        canvas = Canvas(16, 16, (255, 0, 0, 255))
        html = generate_preview_html(canvas)

        self.assertIn("<img", html)

    def test_default_scales(self):
        """Default preview has multiple scale sections."""
        canvas = Canvas(16, 16, (255, 0, 0, 255))
        html = generate_preview_html(canvas)

        # Check for default scales
        self.assertIn("1x", html)
        self.assertIn("2x", html)
        self.assertIn("4x", html)

    def test_custom_title(self):
        """Custom title appears in HTML."""
        canvas = Canvas(16, 16, (255, 0, 0, 255))
        options = PreviewOptions(title="My Custom Title")
        html = generate_preview_html(canvas, options)

        self.assertIn("My Custom Title", html)

    def test_custom_scales(self):
        """Custom scales are used."""
        canvas = Canvas(16, 16, (255, 0, 0, 255))
        options = PreviewOptions(scales=[2, 6])
        html = generate_preview_html(canvas, options)

        self.assertIn("2x", html)
        self.assertIn("6x", html)

    def test_dark_background_class(self):
        """Dark background adds correct class."""
        canvas = Canvas(16, 16, (255, 0, 0, 255))

        dark_html = generate_preview_html(canvas, PreviewOptions(dark_background=True))
        light_html = generate_preview_html(canvas, PreviewOptions(dark_background=False))

        self.assertIn('class="dark"', dark_html)
        self.assertIn('class="light"', light_html)

    def test_show_info_option(self):
        """show_info option controls info section."""
        canvas = Canvas(16, 16, (255, 0, 0, 255))

        with_info = generate_preview_html(canvas, PreviewOptions(show_info=True))
        without_info = generate_preview_html(canvas, PreviewOptions(show_info=False))

        self.assertIn("Image Info", with_info)
        self.assertNotIn("Image Info", without_info)

    def test_download_option(self):
        """include_download option controls download section."""
        canvas = Canvas(16, 16, (255, 0, 0, 255))

        with_dl = generate_preview_html(canvas, PreviewOptions(include_download=True))
        without_dl = generate_preview_html(canvas, PreviewOptions(include_download=False))

        self.assertIn("Download", with_dl)
        self.assertNotIn("Download", without_dl)


class TestGeneratePreviewPage(TestCase):
    """Tests for saving preview pages."""

    def test_creates_file(self):
        """generate_preview_page creates a file."""
        import tempfile
        canvas = Canvas(16, 16, (255, 0, 0, 255))

        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as f:
            output_path = f.name

        try:
            result = generate_preview_page(canvas, output_path)
            self.assertEqual(result, output_path)
            self.assertTrue(os.path.exists(output_path))

            # Verify content
            with open(output_path, 'r') as f:
                content = f.read()
            self.assertIn("<!DOCTYPE html>", content)
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)

    def test_returns_path(self):
        """generate_preview_page returns the output path."""
        import tempfile
        canvas = Canvas(16, 16, (255, 0, 0, 255))

        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as f:
            output_path = f.name

        try:
            result = generate_preview_page(canvas, output_path)
            self.assertEqual(result, output_path)
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)


class TestGenerateMultiPreviewHtml(TestCase):
    """Tests for multi-canvas preview generation."""

    def test_returns_html(self):
        """generate_multi_preview_html returns HTML string."""
        canvases = [
            ("Red", Canvas(8, 8, (255, 0, 0, 255))),
            ("Green", Canvas(8, 8, (0, 255, 0, 255))),
        ]
        html = generate_multi_preview_html(canvases)

        self.assertIsInstance(html, str)
        self.assertTrue(html.startswith("<!DOCTYPE html>"))

    def test_contains_all_names(self):
        """HTML contains all canvas names."""
        canvases = [
            ("First Canvas", Canvas(8, 8, (255, 0, 0, 255))),
            ("Second Canvas", Canvas(8, 8, (0, 255, 0, 255))),
        ]
        html = generate_multi_preview_html(canvases)

        self.assertIn("First Canvas", html)
        self.assertIn("Second Canvas", html)

    def test_empty_list(self):
        """Handles empty canvas list."""
        html = generate_multi_preview_html([])

        self.assertIsInstance(html, str)


class TestPreviewOptions(TestCase):
    """Tests for PreviewOptions dataclass."""

    def test_default_values(self):
        """PreviewOptions has sensible defaults."""
        options = PreviewOptions()

        self.assertEqual(options.scales, [1, 2, 4, 8])
        self.assertEqual(options.title, "Pixel Art Preview")
        self.assertFalse(options.show_grid)
        self.assertTrue(options.dark_background)
        self.assertTrue(options.show_info)
        self.assertTrue(options.include_download)

    def test_custom_values(self):
        """PreviewOptions accepts custom values."""
        options = PreviewOptions(
            scales=[1, 3],
            title="Custom Preview",
            show_grid=True,
            dark_background=False
        )

        self.assertEqual(options.scales, [1, 3])
        self.assertEqual(options.title, "Custom Preview")
        self.assertTrue(options.show_grid)
        self.assertFalse(options.dark_background)

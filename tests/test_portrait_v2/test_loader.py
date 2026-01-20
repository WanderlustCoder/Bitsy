"""Tests for template loader."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from generators.portrait_v2.loader import TemplateLoader, Template
from core.canvas import Canvas


class TestTemplateLoader:
    def test_load_template_returns_template_object(self, tmp_path):
        """Loader returns a Template with pixel data."""
        canvas = Canvas(2, 2)
        canvas.set_pixel_solid(0, 0, (255, 0, 0, 255))
        canvas.set_pixel_solid(1, 0, (0, 255, 0, 255))
        canvas.set_pixel_solid(0, 1, (0, 0, 255, 255))
        canvas.set_pixel_solid(1, 1, (255, 255, 0, 255))

        png_path = tmp_path / "test.png"
        canvas.save(str(png_path))

        meta_path = tmp_path / "test.json"
        meta_path.write_text('{"name": "test", "anchor": [1, 1]}')

        loader = TemplateLoader(str(tmp_path))
        template = loader.load("test")

        assert isinstance(template, Template)
        assert template.name == "test"
        assert template.width == 2
        assert template.height == 2
        assert template.anchor == (1, 1)

    def test_load_template_without_metadata_uses_defaults(self, tmp_path):
        """Template without .json uses default anchor at center."""
        canvas = Canvas(4, 4)
        canvas.set_pixel_solid(0, 0, (255, 0, 0, 255))

        png_path = tmp_path / "nodata.png"
        canvas.save(str(png_path))

        loader = TemplateLoader(str(tmp_path))
        template = loader.load("nodata")

        assert template.anchor == (2, 2)

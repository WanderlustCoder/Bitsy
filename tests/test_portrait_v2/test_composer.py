"""Tests for template composer."""
import pytest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from generators.portrait_v2.composer import TemplatePortraitGenerator
from core.canvas import Canvas


class TestComposer:
    def test_composer_produces_canvas(self):
        """Composer generates a canvas with content."""
        generator = TemplatePortraitGenerator(
            style_path="templates/anime_standard",
            skin_color=(232, 190, 160),
            eye_color=(100, 80, 60),
        )

        canvas = generator.render()

        assert isinstance(canvas, Canvas)
        assert canvas.width == 80
        assert canvas.height == 128

        # Should have some non-transparent pixels
        has_content = False
        for y in range(canvas.height):
            for x in range(canvas.width):
                pixel = canvas.get_pixel(x, y)
                if pixel and pixel[3] > 0:
                    has_content = True
                    break
            if has_content:
                break

        assert has_content, "Canvas should have visible content"

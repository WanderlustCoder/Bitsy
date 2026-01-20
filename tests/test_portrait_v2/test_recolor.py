"""Tests for template recoloring."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from generators.portrait_v2.recolor import recolor_template


class TestRecolor:
    def test_recolor_swaps_placeholder_colors(self):
        """Recolor replaces placeholder red with target color."""
        pixels = [
            [(255, 0, 0, 255), (200, 0, 0, 255)],
            [(150, 0, 0, 255), (0, 0, 0, 0)],
        ]

        target_palette = [
            (232, 190, 160, 255),
            (200, 150, 130, 255),
            (170, 120, 100, 255),
        ]

        result = recolor_template(pixels, target_palette)

        assert result[0][0] == (232, 190, 160, 255)
        assert result[0][1] == (200, 150, 130, 255)
        assert result[1][0] == (170, 120, 100, 255)
        assert result[1][1] == (0, 0, 0, 0)

    def test_recolor_preserves_unknown_colors(self):
        """Colors not in placeholder palette are preserved."""
        pixels = [
            [(128, 128, 128, 255)],
        ]

        target_palette = [(255, 200, 150, 255)]
        result = recolor_template(pixels, target_palette)

        assert result[0][0] == (128, 128, 128, 255)

    def test_recolor_preserves_transparent_pixels(self):
        """Transparent pixels remain unchanged."""
        pixels = [
            [(255, 0, 0, 0)],
        ]

        target_palette = [(10, 20, 30, 255)]
        result = recolor_template(pixels, target_palette)

        assert result[0][0] == (255, 0, 0, 0)

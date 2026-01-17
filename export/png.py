"""
PNG Export - Provides convenient PNG saving and loading interface for export modules.

This module wraps the core PNG writing functionality with a Canvas-aware interface.
"""

from core.png_writer import save_png as _core_save_png
from editor.loader import load_png


def save_png(canvas, filepath: str) -> None:
    """Save a Canvas to a PNG file.

    Args:
        canvas: Canvas object to save
        filepath: Path to save the PNG file
    """
    _core_save_png(filepath, canvas.width, canvas.height, canvas.pixels)


__all__ = ['save_png', 'load_png']

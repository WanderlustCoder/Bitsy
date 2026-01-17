"""
Test History - Tests for editor undo/redo stack.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests.framework import TestCase
from editor.history import UndoStack
from core import Canvas


class TestUndoStack(TestCase):
    """Tests for undo/redo history behavior."""

    def test_push_undo_redo(self):
        """push stores snapshots and undo/redo restores them."""
        stack = UndoStack()
        canvas = Canvas(2, 2)
        canvas.set_pixel_solid(0, 0, (255, 0, 0, 255))
        stack.push(canvas)

        canvas.set_pixel_solid(1, 0, (0, 255, 0, 255))
        stack.push(canvas)

        undo_canvas = stack.undo()
        self.assertIsNotNone(undo_canvas)
        self.assertPixelColor(undo_canvas, 0, 0, (255, 0, 0, 255))
        self.assertPixelColor(undo_canvas, 1, 0, (0, 0, 0, 0))

        redo_canvas = stack.redo()
        self.assertIsNotNone(redo_canvas)
        self.assertPixelColor(redo_canvas, 1, 0, (0, 255, 0, 255))

    def test_push_clears_redo(self):
        """push after undo clears redo history."""
        stack = UndoStack()
        canvas = Canvas(2, 2)
        stack.push(canvas)

        canvas.set_pixel_solid(0, 1, (0, 0, 255, 255))
        stack.push(canvas)

        undo_canvas = stack.undo()
        self.assertIsNotNone(undo_canvas)

        undo_canvas.set_pixel_solid(1, 1, (255, 255, 0, 255))
        stack.push(undo_canvas)

        self.assertIsNone(stack.redo())

    def test_clear_resets_history(self):
        """clear removes undo and redo snapshots."""
        stack = UndoStack()
        canvas = Canvas(1, 1)
        stack.push(canvas)

        stack.clear()

        self.assertIsNone(stack.undo())
        self.assertIsNone(stack.redo())

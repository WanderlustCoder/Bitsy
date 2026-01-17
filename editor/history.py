"""
History - Undo/redo stack for editor canvas snapshots.

Provides:
- UndoStack class for managing canvas history
"""

import sys
import os
from typing import List, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Canvas


class UndoStack:
    """Track undo/redo history for canvas snapshots."""

    def __init__(self) -> None:
        self._undo_stack: List[Canvas] = []
        self._redo_stack: List[Canvas] = []

    def push(self, canvas: Canvas) -> None:
        """Push a snapshot and clear redo history."""
        self._undo_stack.append(canvas.copy())
        self._redo_stack.clear()

    def undo(self) -> Optional[Canvas]:
        """Undo to the previous snapshot and return it."""
        if len(self._undo_stack) <= 1:
            return None
        snapshot = self._undo_stack.pop()
        self._redo_stack.append(snapshot)
        return self._undo_stack[-1].copy()

    def redo(self) -> Optional[Canvas]:
        """Redo the last undone snapshot and return it."""
        if not self._redo_stack:
            return None
        snapshot = self._redo_stack.pop()
        self._undo_stack.append(snapshot)
        return snapshot.copy()

    def clear(self) -> None:
        """Clear all history."""
        self._undo_stack.clear()
        self._redo_stack.clear()

"""
Session management for collaborative editing.

Manages users, canvas state, and action history.
"""

import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
from collections import deque

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Canvas


Color = Tuple[int, int, int, int]


@dataclass
class User:
    """A user in a collaborative session."""
    username: str
    cursor_x: int = 0
    cursor_y: int = 0
    connected_at: float = field(default_factory=time.time)
    
    def __hash__(self):
        return hash(self.username)
    
    def __eq__(self, other):
        if isinstance(other, User):
            return self.username == other.username
        return False


@dataclass
class PixelAction:
    """A single pixel change action for history."""
    x: int
    y: int
    old_color: Optional[Color]
    new_color: Optional[Color]
    username: str
    timestamp: float = field(default_factory=time.time)


class ActionHistory:
    """Manages undo/redo history for a session."""
    
    def __init__(self, max_size: int = 1000):
        """Initialize history with max size."""
        self._undo_stack: deque = deque(maxlen=max_size)
        self._redo_stack: deque = deque(maxlen=max_size)
        self._max_size = max_size
    
    def push(self, action: PixelAction) -> None:
        """Add an action to history."""
        self._undo_stack.append(action)
        # Clear redo stack on new action
        self._redo_stack.clear()
    
    def undo(self) -> Optional[PixelAction]:
        """Pop and return the last action for undo."""
        if self._undo_stack:
            action = self._undo_stack.pop()
            self._redo_stack.append(action)
            return action
        return None
    
    def redo(self) -> Optional[PixelAction]:
        """Pop and return the last undone action for redo."""
        if self._redo_stack:
            action = self._redo_stack.pop()
            self._undo_stack.append(action)
            return action
        return None
    
    def can_undo(self) -> bool:
        """Check if undo is available."""
        return len(self._undo_stack) > 0
    
    def can_redo(self) -> bool:
        """Check if redo is available."""
        return len(self._redo_stack) > 0
    
    def clear(self) -> None:
        """Clear all history."""
        self._undo_stack.clear()
        self._redo_stack.clear()


class CollabSession:
    """A collaborative editing session.
    
    Manages canvas state, users, and synchronization.
    """
    
    def __init__(
        self,
        width: int = 32,
        height: int = 32,
        session_id: Optional[str] = None
    ):
        """Initialize a new session.
        
        Args:
            width: Canvas width
            height: Canvas height
            session_id: Optional session ID (generated if not provided)
        """
        self.session_id = session_id or str(uuid.uuid4())[:8]
        self.canvas = Canvas(width, height)
        self.users: Dict[str, User] = {}
        self.history = ActionHistory()
        self.chat_history: List[Tuple[str, str, float]] = []  # (user, text, time)
        self._created_at = time.time()
        
        # Callbacks
        self._on_pixel_change: Optional[Callable] = None
        self._on_user_join: Optional[Callable] = None
        self._on_user_leave: Optional[Callable] = None
        self._on_chat: Optional[Callable] = None
        self._on_cursor_move: Optional[Callable] = None
    
    # User management
    
    def add_user(self, username: str) -> User:
        """Add a user to the session."""
        if username in self.users:
            raise ValueError(f"User '{username}' already in session")
        
        user = User(username=username)
        self.users[username] = user
        
        if self._on_user_join:
            self._on_user_join(user)
        
        return user
    
    def remove_user(self, username: str) -> bool:
        """Remove a user from the session."""
        if username not in self.users:
            return False
        
        user = self.users.pop(username)
        
        if self._on_user_leave:
            self._on_user_leave(user)
        
        return True
    
    def get_user(self, username: str) -> Optional[User]:
        """Get a user by username."""
        return self.users.get(username)
    
    def get_users(self) -> List[str]:
        """Get list of connected usernames."""
        return list(self.users.keys())
    
    def user_count(self) -> int:
        """Get number of connected users."""
        return len(self.users)
    
    # Canvas operations
    
    def set_pixel(
        self,
        x: int, y: int,
        color: Color,
        username: str,
        record_history: bool = True
    ) -> bool:
        """Set a pixel and optionally record to history."""
        if not (0 <= x < self.canvas.width and 0 <= y < self.canvas.height):
            return False
        
        old_color = self.canvas.get_pixel(x, y)
        self.canvas.set_pixel(x, y, color)
        
        if record_history:
            action = PixelAction(
                x=x, y=y,
                old_color=old_color,
                new_color=color,
                username=username
            )
            self.history.push(action)
        
        if self._on_pixel_change:
            self._on_pixel_change(x, y, color, username)
        
        return True
    
    def clear_canvas(self, username: str) -> None:
        """Clear the entire canvas."""
        # Record all pixels for undo
        for y in range(self.canvas.height):
            for x in range(self.canvas.width):
                color = self.canvas.get_pixel(x, y)
                if color and color[3] > 0:
                    action = PixelAction(
                        x=x, y=y,
                        old_color=color,
                        new_color=None,
                        username=username
                    )
                    self.history.push(action)
        
        self.canvas = Canvas(self.canvas.width, self.canvas.height)
    
    def get_canvas_state(self) -> Dict[str, List[int]]:
        """Get full canvas state as dict for sync."""
        pixels = {}
        for y in range(self.canvas.height):
            for x in range(self.canvas.width):
                color = self.canvas.get_pixel(x, y)
                if color and color[3] > 0:
                    pixels[f"{x},{y}"] = list(color)
        return pixels
    
    def load_canvas_state(self, pixels: Dict[str, List[int]]) -> None:
        """Load canvas state from sync dict."""
        self.canvas = Canvas(self.canvas.width, self.canvas.height)
        for key, color in pixels.items():
            x, y = map(int, key.split(","))
            self.canvas.set_pixel(x, y, tuple(color))
    
    # History operations
    
    def undo(self, username: str) -> Optional[PixelAction]:
        """Undo the last action."""
        action = self.history.undo()
        if action:
            # Apply the reverse (use set_pixel_solid to bypass alpha blending)
            color = action.old_color or (0, 0, 0, 0)
            self.canvas.set_pixel_solid(action.x, action.y, color)
            
            if self._on_pixel_change:
                self._on_pixel_change(
                    action.x, action.y,
                    action.old_color or (0, 0, 0, 0),
                    username
                )
        return action
    
    def redo(self, username: str) -> Optional[PixelAction]:
        """Redo the last undone action."""
        action = self.history.redo()
        if action:
            # Use set_pixel_solid to bypass alpha blending
            color = action.new_color or (0, 0, 0, 0)
            self.canvas.set_pixel_solid(action.x, action.y, color)
            
            if self._on_pixel_change:
                self._on_pixel_change(
                    action.x, action.y,
                    action.new_color or (0, 0, 0, 0),
                    username
                )
        return action
    
    # Cursor tracking
    
    def update_cursor(self, username: str, x: int, y: int) -> None:
        """Update a user's cursor position."""
        user = self.users.get(username)
        if user:
            user.cursor_x = x
            user.cursor_y = y
            
            if self._on_cursor_move:
                self._on_cursor_move(username, x, y)
    
    def get_cursors(self) -> Dict[str, Tuple[int, int]]:
        """Get all user cursor positions."""
        return {
            name: (user.cursor_x, user.cursor_y)
            for name, user in self.users.items()
        }
    
    # Chat
    
    def add_chat(self, username: str, text: str) -> None:
        """Add a chat message."""
        entry = (username, text, time.time())
        self.chat_history.append(entry)
        
        # Keep last 100 messages
        if len(self.chat_history) > 100:
            self.chat_history = self.chat_history[-100:]
        
        if self._on_chat:
            self._on_chat(username, text)
    
    def get_chat_history(self, limit: int = 50) -> List[Tuple[str, str, float]]:
        """Get recent chat history."""
        return self.chat_history[-limit:]
    
    # Callbacks
    
    def on_pixel_change(self, callback: Callable) -> None:
        """Set callback for pixel changes."""
        self._on_pixel_change = callback
    
    def on_user_join(self, callback: Callable) -> None:
        """Set callback for user joins."""
        self._on_user_join = callback
    
    def on_user_leave(self, callback: Callable) -> None:
        """Set callback for user leaves."""
        self._on_user_leave = callback
    
    def on_chat(self, callback: Callable) -> None:
        """Set callback for chat messages."""
        self._on_chat = callback
    
    def on_cursor_move(self, callback: Callable) -> None:
        """Set callback for cursor movements."""
        self._on_cursor_move = callback

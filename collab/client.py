"""
Collaborative session client.

Connects to a server to participate in collaborative editing.
"""

import asyncio
import socket
import threading
import time
from typing import Callable, Dict, List, Optional, Tuple

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Canvas
from .protocol import (
    Message, MessageType,
    encode_message, decode_message,
    create_join_message, create_pixel_message,
    create_cursor_message, create_chat_message,
    create_undo_message, create_redo_message,
    create_clear_message,
)


Color = Tuple[int, int, int, int]


class CollabClient:
    """Client for joining collaborative sessions.
    
    Example:
        client = CollabClient("localhost", 8765, "Alice")
        client.connect()
        
        # Draw
        client.set_pixel(10, 10, (255, 0, 0, 255))
        
        # Chat
        client.send_chat("Hello!")
        
        # Get canvas
        canvas = client.get_canvas()
        
        client.disconnect()
    """
    
    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        width: int = 32,
        height: int = 32
    ):
        """Initialize client.
        
        Args:
            host: Server host address
            port: Server port
            username: Username for this client
            width: Expected canvas width
            height: Expected canvas height
        """
        self.host = host
        self.port = port
        self.username = username
        
        self.canvas = Canvas(width, height)
        self.session_id: Optional[str] = None
        self.users: List[str] = []
        self.cursors: Dict[str, Tuple[int, int]] = {}
        self.chat_history: List[Tuple[str, str]] = []
        
        self._socket: Optional[socket.socket] = None
        self._thread: Optional[threading.Thread] = None
        self._connected = False
        self._lock = threading.Lock()
        
        # Callbacks
        self.on_pixel_change: Optional[Callable] = None
        self.on_user_join: Optional[Callable] = None
        self.on_user_leave: Optional[Callable] = None
        self.on_chat: Optional[Callable] = None
        self.on_cursor_move: Optional[Callable] = None
        self.on_sync: Optional[Callable] = None
        self.on_error: Optional[Callable] = None
    
    def connect(self, timeout: float = 5.0) -> bool:
        """Connect to the server.
        
        Args:
            timeout: Connection timeout in seconds
            
        Returns:
            True if connected successfully
        """
        if self._connected:
            return True
        
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.settimeout(timeout)
            self._socket.connect((self.host, self.port))
            self._socket.settimeout(None)
            
            self._connected = True
            
            # Start receive thread
            self._thread = threading.Thread(target=self._receive_loop, daemon=True)
            self._thread.start()
            
            # Send join message
            self._send(create_join_message(self.username))
            
            # Wait for welcome
            time.sleep(0.2)
            
            return True
        
        except Exception as e:
            self._connected = False
            if self.on_error:
                self.on_error(str(e))
            return False
    
    def disconnect(self) -> None:
        """Disconnect from the server."""
        self._connected = False
        
        if self._socket:
            try:
                self._socket.close()
            except Exception:
                pass
            self._socket = None
        
        if self._thread:
            self._thread.join(timeout=1.0)
            self._thread = None
    
    def is_connected(self) -> bool:
        """Check if connected to server."""
        return self._connected
    
    def _receive_loop(self) -> None:
        """Background loop for receiving messages."""
        buffer = b""
        
        while self._connected and self._socket:
            try:
                data = self._socket.recv(4096)
                if not data:
                    break
                
                buffer += data
                
                # Process complete messages
                while len(buffer) >= 4:
                    length = int.from_bytes(buffer[:4], 'big')
                    if len(buffer) < 4 + length:
                        break
                    
                    msg_data = buffer[:4 + length]
                    buffer = buffer[4 + length:]
                    
                    msg = decode_message(msg_data)
                    if msg:
                        self._process_message(msg)
            
            except Exception:
                break
        
        self._connected = False
    
    def _process_message(self, msg: Message) -> None:
        """Process a received message."""
        msg_type = msg.type
        
        if msg_type == MessageType.WELCOME.value:
            self.session_id = msg.data.get("session_id")
            self.users = msg.data.get("users", [])
        
        elif msg_type == MessageType.USER_LIST.value:
            old_users = set(self.users)
            self.users = msg.data.get("users", [])
            new_users = set(self.users)
            
            # Detect joins and leaves
            for user in new_users - old_users:
                if user != self.username and self.on_user_join:
                    self.on_user_join(user)
            
            for user in old_users - new_users:
                if self.on_user_leave:
                    self.on_user_leave(user)
        
        elif msg_type == MessageType.SYNC.value:
            width = msg.data.get("width", self.canvas.width)
            height = msg.data.get("height", self.canvas.height)
            pixels = msg.data.get("pixels", {})
            
            with self._lock:
                self.canvas = Canvas(width, height)
                for key, color in pixels.items():
                    x, y = map(int, key.split(","))
                    self.canvas.set_pixel(x, y, tuple(color))
            
            if self.on_sync:
                self.on_sync()
        
        elif msg_type == MessageType.PIXEL.value:
            x = msg.data.get("x", 0)
            y = msg.data.get("y", 0)
            color = tuple(msg.data.get("color", [0, 0, 0, 255]))
            sender = msg.sender
            
            with self._lock:
                self.canvas.set_pixel(x, y, color)
            
            if self.on_pixel_change:
                self.on_pixel_change(x, y, color, sender)
        
        elif msg_type == MessageType.CURSOR.value:
            x = msg.data.get("x", 0)
            y = msg.data.get("y", 0)
            sender = msg.sender
            
            self.cursors[sender] = (x, y)
            
            if self.on_cursor_move:
                self.on_cursor_move(sender, x, y)
        
        elif msg_type == MessageType.CHAT.value:
            text = msg.data.get("text", "")
            sender = msg.sender
            
            self.chat_history.append((sender, text))
            
            if self.on_chat:
                self.on_chat(sender, text)
        
        elif msg_type == MessageType.ERROR.value:
            error = msg.data.get("error", "Unknown error")
            if self.on_error:
                self.on_error(error)
    
    def _send(self, msg: Message) -> bool:
        """Send a message to the server."""
        if not self._connected or not self._socket:
            return False
        
        try:
            data = encode_message(msg)
            self._socket.sendall(data)
            return True
        except Exception:
            return False
    
    # Canvas operations
    
    def set_pixel(self, x: int, y: int, color: Color) -> bool:
        """Set a pixel and broadcast to others."""
        with self._lock:
            self.canvas.set_pixel(x, y, color)
        
        return self._send(create_pixel_message(x, y, color, self.username))
    
    def get_pixel(self, x: int, y: int) -> Optional[Color]:
        """Get a pixel from the local canvas."""
        with self._lock:
            return self.canvas.get_pixel(x, y)
    
    def get_canvas(self) -> Canvas:
        """Get a copy of the current canvas."""
        with self._lock:
            copy = Canvas(self.canvas.width, self.canvas.height)
            for y in range(self.canvas.height):
                for x in range(self.canvas.width):
                    color = self.canvas.get_pixel(x, y)
                    if color:
                        copy.set_pixel(x, y, color)
            return copy
    
    def clear_canvas(self) -> bool:
        """Clear the canvas."""
        with self._lock:
            self.canvas = Canvas(self.canvas.width, self.canvas.height)
        return self._send(create_clear_message(self.username))
    
    # Cursor
    
    def update_cursor(self, x: int, y: int) -> bool:
        """Update cursor position."""
        return self._send(create_cursor_message(x, y, self.username))
    
    def get_cursors(self) -> Dict[str, Tuple[int, int]]:
        """Get all user cursor positions."""
        return dict(self.cursors)
    
    # Chat
    
    def send_chat(self, text: str) -> bool:
        """Send a chat message."""
        return self._send(create_chat_message(text, self.username))
    
    def get_chat_history(self) -> List[Tuple[str, str]]:
        """Get chat history."""
        return list(self.chat_history)
    
    # History
    
    def undo(self) -> bool:
        """Request undo."""
        return self._send(create_undo_message(self.username))
    
    def redo(self) -> bool:
        """Request redo."""
        return self._send(create_redo_message(self.username))
    
    # User info
    
    def get_users(self) -> List[str]:
        """Get list of connected users."""
        return list(self.users)
    
    def get_session_id(self) -> Optional[str]:
        """Get the session ID."""
        return self.session_id

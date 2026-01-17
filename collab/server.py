"""
Collaborative session server.

Hosts sessions that clients can connect to.
Uses asyncio for non-blocking networking.
"""

import asyncio
import logging
import socket
import threading
import time
from typing import Callable, Dict, List, Optional, Set

from .protocol import (
    Message, MessageType,
    encode_message, decode_message,
    create_welcome_message, create_user_list_message,
    create_pixel_message, create_sync_message,
    create_chat_message, create_cursor_message,
    create_error_message,
)
from .session import CollabSession

logger = logging.getLogger(__name__)


class ClientHandler:
    """Handles a single client connection."""
    
    def __init__(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
        session: CollabSession,
        server: 'CollabServer'
    ):
        self.reader = reader
        self.writer = writer
        self.session = session
        self.server = server
        self.username: Optional[str] = None
        self._running = False
    
    async def handle(self) -> None:
        """Main handler loop for this client."""
        self._running = True
        buffer = b""
        
        try:
            while self._running:
                data = await self.reader.read(4096)
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
                        await self._process_message(msg)
        
        except Exception as e:
            logger.debug(
                "Client handler loop error for %s: %s",
                self.username or "unknown",
                e,
                exc_info=True,
            )
        
        finally:
            await self._cleanup()
    
    async def _process_message(self, msg: Message) -> None:
        """Process a received message."""
        msg_type = msg.type
        
        if msg_type == MessageType.JOIN.value:
            await self._handle_join(msg)
        
        elif msg_type == MessageType.PIXEL.value:
            await self._handle_pixel(msg)
        
        elif msg_type == MessageType.CURSOR.value:
            await self._handle_cursor(msg)
        
        elif msg_type == MessageType.CHAT.value:
            await self._handle_chat(msg)
        
        elif msg_type == MessageType.UNDO.value:
            await self._handle_undo(msg)
        
        elif msg_type == MessageType.REDO.value:
            await self._handle_redo(msg)
        
        elif msg_type == MessageType.CLEAR.value:
            await self._handle_clear(msg)
    
    async def _handle_join(self, msg: Message) -> None:
        """Handle join request."""
        username = msg.data.get("username", "")
        
        if not username:
            await self.send(create_error_message("Username required"))
            return
        
        if username in self.session.users:
            await self.send(create_error_message("Username taken"))
            return
        
        self.username = username
        self.session.add_user(username)
        self.server._clients[username] = self
        
        # Send welcome with session info
        welcome = create_welcome_message(
            self.session.session_id,
            self.session.get_users()
        )
        await self.send(welcome)
        
        # Send full canvas state
        sync = create_sync_message(
            self.session.canvas.width,
            self.session.canvas.height,
            self.session.get_canvas_state()
        )
        await self.send(sync)
        
        # Broadcast user list to all
        await self.server.broadcast(
            create_user_list_message(self.session.get_users())
        )
    
    async def _handle_pixel(self, msg: Message) -> None:
        """Handle pixel change."""
        if not self.username:
            return
        
        x = msg.data.get("x", 0)
        y = msg.data.get("y", 0)
        color = tuple(msg.data.get("color", [0, 0, 0, 255]))
        
        self.session.set_pixel(x, y, color, self.username)
        
        # Broadcast to all other clients
        pixel_msg = create_pixel_message(x, y, color, self.username)
        await self.server.broadcast(pixel_msg, exclude=self.username)
    
    async def _handle_cursor(self, msg: Message) -> None:
        """Handle cursor update."""
        if not self.username:
            return
        
        x = msg.data.get("x", 0)
        y = msg.data.get("y", 0)
        
        self.session.update_cursor(self.username, x, y)
        
        cursor_msg = create_cursor_message(x, y, self.username)
        await self.server.broadcast(cursor_msg, exclude=self.username)
    
    async def _handle_chat(self, msg: Message) -> None:
        """Handle chat message."""
        if not self.username:
            return
        
        text = msg.data.get("text", "")
        if text:
            self.session.add_chat(self.username, text)
            chat_msg = create_chat_message(text, self.username)
            await self.server.broadcast(chat_msg)
    
    async def _handle_undo(self, msg: Message) -> None:
        """Handle undo request."""
        if not self.username:
            return
        
        action = self.session.undo(self.username)
        if action:
            color = action.old_color or (0, 0, 0, 0)
            pixel_msg = create_pixel_message(
                action.x, action.y, color, self.username
            )
            await self.server.broadcast(pixel_msg)
    
    async def _handle_redo(self, msg: Message) -> None:
        """Handle redo request."""
        if not self.username:
            return
        
        action = self.session.redo(self.username)
        if action:
            color = action.new_color or (0, 0, 0, 0)
            pixel_msg = create_pixel_message(
                action.x, action.y, color, self.username
            )
            await self.server.broadcast(pixel_msg)
    
    async def _handle_clear(self, msg: Message) -> None:
        """Handle canvas clear."""
        if not self.username:
            return
        
        self.session.clear_canvas(self.username)
        
        # Broadcast empty sync
        sync = create_sync_message(
            self.session.canvas.width,
            self.session.canvas.height,
            {}
        )
        await self.server.broadcast(sync)
    
    async def send(self, msg: Message) -> None:
        """Send a message to this client."""
        try:
            data = encode_message(msg)
            self.writer.write(data)
            await self.writer.drain()
        except Exception:
            logger.debug(
                "Failed to send message to %s",
                self.username or "unknown",
                exc_info=True,
            )
    
    async def _cleanup(self) -> None:
        """Clean up on disconnect."""
        self._running = False
        
        if self.username:
            self.session.remove_user(self.username)
            if self.username in self.server._clients:
                del self.server._clients[self.username]
            
            # Broadcast updated user list
            await self.server.broadcast(
                create_user_list_message(self.session.get_users())
            )
        
        try:
            self.writer.close()
            await self.writer.wait_closed()
        except Exception:
            logger.debug(
                "Error closing client writer for %s",
                self.username or "unknown",
                exc_info=True,
            )
    
    def disconnect(self) -> None:
        """Disconnect this client."""
        self._running = False


class CollabServer:
    """Server for hosting collaborative sessions.
    
    Example:
        server = CollabServer(port=8765)
        server.start()
        
        # ... server runs in background ...
        
        server.stop()
    """
    
    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 8765,
        width: int = 32,
        height: int = 32
    ):
        """Initialize server.
        
        Args:
            host: Host address to bind to
            port: Port to listen on
            width: Canvas width
            height: Canvas height
        """
        self.host = host
        self.port = port
        self.session = CollabSession(width=width, height=height)
        
        self._clients: Dict[str, ClientHandler] = {}
        self._server: Optional[asyncio.AbstractServer] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self._running = False
    
    def start(self) -> None:
        """Start the server in a background thread."""
        if self._running:
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._run_server, daemon=True)
        self._thread.start()
        
        # Wait for server to start
        time.sleep(0.1)
    
    def _run_server(self) -> None:
        """Run the server event loop."""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        
        try:
            self._loop.run_until_complete(self._serve())
        except Exception:
            logger.warning("Server event loop error", exc_info=True)
        finally:
            self._loop.close()
    
    async def _serve(self) -> None:
        """Main server coroutine."""
        self._server = await asyncio.start_server(
            self._handle_client,
            self.host,
            self.port
        )
        
        async with self._server:
            await self._server.serve_forever()
    
    async def _handle_client(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter
    ) -> None:
        """Handle a new client connection."""
        handler = ClientHandler(reader, writer, self.session, self)
        await handler.handle()
    
    async def broadcast(
        self,
        msg: Message,
        exclude: Optional[str] = None
    ) -> None:
        """Broadcast a message to all connected clients."""
        for username, client in list(self._clients.items()):
            if username != exclude:
                await client.send(msg)
    
    def stop(self) -> None:
        """Stop the server."""
        self._running = False
        
        if self._server:
            self._server.close()
        
        if self._loop:
            self._loop.call_soon_threadsafe(self._loop.stop)
        
        if self._thread:
            self._thread.join(timeout=1.0)
    
    def is_running(self) -> bool:
        """Check if server is running."""
        return self._running
    
    def get_session(self) -> CollabSession:
        """Get the session object."""
        return self.session
    
    def get_connected_users(self) -> List[str]:
        """Get list of connected usernames."""
        return list(self._clients.keys())

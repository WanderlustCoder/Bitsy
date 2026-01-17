"""
Bitsy Collab - Multi-user collaborative sprite editing.

Real-time collaboration for pixel art creation. Host sessions
and invite others to draw together.

Example - Host a session:

    from collab import CollabServer

    server = CollabServer(port=8765)
    server.start()
    print(f"Session: {server.session.session_id}")
    
    # Server runs in background...
    # When done:
    server.stop()

Example - Join a session:

    from collab import CollabClient

    client = CollabClient("localhost", 8765, username="Alice")
    client.connect()
    
    # Draw pixels
    client.set_pixel(10, 10, (255, 0, 0, 255))
    
    # Chat
    client.send_chat("Hello everyone!")
    
    # Get updates
    client.on_pixel_change = lambda x, y, c, u: print(f"{u} drew at {x},{y}")
    
    # When done:
    client.disconnect()
"""

from .protocol import (
    Message,
    MessageType,
    encode_message,
    decode_message,
    create_join_message,
    create_pixel_message,
    create_cursor_message,
    create_chat_message,
    create_sync_message,
)

from .session import (
    User,
    PixelAction,
    ActionHistory,
    CollabSession,
)

from .server import (
    CollabServer,
    ClientHandler,
)

from .client import (
    CollabClient,
)

__all__ = [
    # Protocol
    'Message',
    'MessageType',
    'encode_message',
    'decode_message',
    
    # Session
    'User',
    'PixelAction',
    'ActionHistory',
    'CollabSession',
    
    # Server
    'CollabServer',
    'ClientHandler',
    
    # Client
    'CollabClient',
]

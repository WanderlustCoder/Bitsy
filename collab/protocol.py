"""
Protocol definitions for collaborative sessions.

Defines message types and serialization for network communication.
"""

import json
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum


class MessageType(Enum):
    """Types of protocol messages."""
    # Connection
    JOIN = "join"
    LEAVE = "leave"
    WELCOME = "welcome"
    USER_LIST = "user_list"
    
    # Canvas
    PIXEL = "pixel"
    CLEAR = "clear"
    SYNC = "sync"
    
    # Cursor
    CURSOR = "cursor"
    
    # Chat
    CHAT = "chat"
    
    # History
    UNDO = "undo"
    REDO = "redo"
    
    # Errors
    ERROR = "error"


@dataclass
class Message:
    """Base protocol message."""
    type: str
    data: Dict[str, Any]
    sender: str = ""
    timestamp: float = 0.0

    def to_json(self) -> str:
        """Serialize message to JSON string."""
        return json.dumps({
            "type": self.type,
            "data": self.data,
            "sender": self.sender,
            "timestamp": self.timestamp
        })

    @classmethod
    def from_json(cls, json_str: str) -> 'Message':
        """Deserialize message from JSON string."""
        obj = json.loads(json_str)
        return cls(
            type=obj.get("type", ""),
            data=obj.get("data", {}),
            sender=obj.get("sender", ""),
            timestamp=obj.get("timestamp", 0.0)
        )


# Message factory functions

def create_join_message(username: str) -> Message:
    """Create a join message."""
    return Message(
        type=MessageType.JOIN.value,
        data={"username": username},
        sender=username
    )


def create_leave_message(username: str) -> Message:
    """Create a leave message."""
    return Message(
        type=MessageType.LEAVE.value,
        data={"username": username},
        sender=username
    )


def create_welcome_message(session_id: str, users: List[str]) -> Message:
    """Create a welcome message for new connections."""
    return Message(
        type=MessageType.WELCOME.value,
        data={"session_id": session_id, "users": users}
    )


def create_user_list_message(users: List[str]) -> Message:
    """Create a user list update message."""
    return Message(
        type=MessageType.USER_LIST.value,
        data={"users": users}
    )


def create_pixel_message(
    x: int, y: int, 
    color: Tuple[int, int, int, int],
    username: str
) -> Message:
    """Create a pixel change message."""
    return Message(
        type=MessageType.PIXEL.value,
        data={"x": x, "y": y, "color": list(color)},
        sender=username
    )


def create_clear_message(username: str) -> Message:
    """Create a canvas clear message."""
    return Message(
        type=MessageType.CLEAR.value,
        data={},
        sender=username
    )


def create_sync_message(
    width: int, 
    height: int, 
    pixels: Dict[str, List[int]]
) -> Message:
    """Create a full canvas sync message.
    
    pixels is a dict mapping "x,y" -> [r, g, b, a]
    """
    return Message(
        type=MessageType.SYNC.value,
        data={"width": width, "height": height, "pixels": pixels}
    )


def create_cursor_message(
    x: int, y: int, 
    username: str
) -> Message:
    """Create a cursor position message."""
    return Message(
        type=MessageType.CURSOR.value,
        data={"x": x, "y": y},
        sender=username
    )


def create_chat_message(text: str, username: str) -> Message:
    """Create a chat message."""
    return Message(
        type=MessageType.CHAT.value,
        data={"text": text},
        sender=username
    )


def create_undo_message(username: str) -> Message:
    """Create an undo request message."""
    return Message(
        type=MessageType.UNDO.value,
        data={},
        sender=username
    )


def create_redo_message(username: str) -> Message:
    """Create a redo request message."""
    return Message(
        type=MessageType.REDO.value,
        data={},
        sender=username
    )


def create_error_message(error: str) -> Message:
    """Create an error message."""
    return Message(
        type=MessageType.ERROR.value,
        data={"error": error}
    )


def encode_message(msg: Message) -> bytes:
    """Encode a message for network transmission."""
    json_str = msg.to_json()
    # Length-prefixed format: 4 bytes length + data
    data = json_str.encode('utf-8')
    length = len(data)
    return length.to_bytes(4, 'big') + data


def decode_message(data: bytes) -> Optional[Message]:
    """Decode a message from network data."""
    if len(data) < 4:
        return None
    
    length = int.from_bytes(data[:4], 'big')
    if len(data) < 4 + length:
        return None
    
    json_str = data[4:4+length].decode('utf-8')
    return Message.from_json(json_str)

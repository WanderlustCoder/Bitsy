"""Tests for collaborative editing module."""

import sys
import os
import time
import threading

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core import Canvas
from collab import (
    # Protocol
    Message, MessageType,
    encode_message, decode_message,
    create_join_message, create_pixel_message,
    create_chat_message, create_cursor_message,
    create_sync_message,
    
    # Session
    User, PixelAction, ActionHistory, CollabSession,
    
    # Server/Client
    CollabServer, CollabClient,
)


class TestProtocol:
    """Tests for protocol messages."""
    
    def test_message_creation(self):
        """Test creating a message."""
        msg = Message(type="test", data={"key": "value"})
        assert msg.type == "test"
        assert msg.data["key"] == "value"
    
    def test_message_json_roundtrip(self):
        """Test JSON serialization."""
        msg = Message(type="test", data={"x": 10}, sender="alice")
        json_str = msg.to_json()
        
        restored = Message.from_json(json_str)
        assert restored.type == msg.type
        assert restored.data == msg.data
        assert restored.sender == msg.sender
    
    def test_encode_decode_message(self):
        """Test binary encoding/decoding."""
        msg = Message(type="pixel", data={"x": 5, "y": 10})
        encoded = encode_message(msg)
        
        decoded = decode_message(encoded)
        assert decoded.type == msg.type
        assert decoded.data == msg.data
    
    def test_create_join_message(self):
        """Test join message factory."""
        msg = create_join_message("alice")
        assert msg.type == MessageType.JOIN.value
        assert msg.data["username"] == "alice"
    
    def test_create_pixel_message(self):
        """Test pixel message factory."""
        msg = create_pixel_message(10, 20, (255, 0, 0, 255), "bob")
        assert msg.type == MessageType.PIXEL.value
        assert msg.data["x"] == 10
        assert msg.data["y"] == 20
        assert msg.data["color"] == [255, 0, 0, 255]
    
    def test_create_chat_message(self):
        """Test chat message factory."""
        msg = create_chat_message("Hello!", "alice")
        assert msg.type == MessageType.CHAT.value
        assert msg.data["text"] == "Hello!"
    
    def test_create_sync_message(self):
        """Test sync message factory."""
        pixels = {"5,10": [255, 0, 0, 255]}
        msg = create_sync_message(32, 32, pixels)
        assert msg.type == MessageType.SYNC.value
        assert msg.data["width"] == 32
        assert msg.data["pixels"] == pixels


class TestActionHistory:
    """Tests for action history."""
    
    def test_create_history(self):
        """Test creating history."""
        history = ActionHistory()
        assert not history.can_undo()
        assert not history.can_redo()
    
    def test_push_and_undo(self):
        """Test pushing and undoing actions."""
        history = ActionHistory()
        
        action = PixelAction(x=5, y=10, old_color=None, new_color=(255, 0, 0, 255), username="alice")
        history.push(action)
        
        assert history.can_undo()
        
        undone = history.undo()
        assert undone == action
        assert not history.can_undo()
        assert history.can_redo()
    
    def test_redo(self):
        """Test redo functionality."""
        history = ActionHistory()
        
        action = PixelAction(x=5, y=10, old_color=None, new_color=(255, 0, 0, 255), username="alice")
        history.push(action)
        history.undo()
        
        redone = history.redo()
        assert redone == action
        assert history.can_undo()
        assert not history.can_redo()
    
    def test_new_action_clears_redo(self):
        """Test that new actions clear redo stack."""
        history = ActionHistory()
        
        action1 = PixelAction(x=5, y=10, old_color=None, new_color=(255, 0, 0, 255), username="alice")
        action2 = PixelAction(x=6, y=10, old_color=None, new_color=(0, 255, 0, 255), username="alice")
        
        history.push(action1)
        history.undo()
        history.push(action2)
        
        assert not history.can_redo()


class TestCollabSession:
    """Tests for collaborative session."""
    
    def test_create_session(self):
        """Test creating a session."""
        session = CollabSession(width=16, height=16)
        assert session.canvas.width == 16
        assert session.canvas.height == 16
        assert session.session_id is not None
    
    def test_add_user(self):
        """Test adding users."""
        session = CollabSession()
        user = session.add_user("alice")
        
        assert user.username == "alice"
        assert "alice" in session.get_users()
        assert session.user_count() == 1
    
    def test_remove_user(self):
        """Test removing users."""
        session = CollabSession()
        session.add_user("alice")
        
        result = session.remove_user("alice")
        assert result is True
        assert "alice" not in session.get_users()
    
    def test_duplicate_user(self):
        """Test adding duplicate username."""
        session = CollabSession()
        session.add_user("alice")
        
        try:
            session.add_user("alice")
            assert False, "Should raise ValueError"
        except ValueError:
            pass
    
    def test_set_pixel(self):
        """Test setting pixels."""
        session = CollabSession()
        session.add_user("alice")
        
        result = session.set_pixel(5, 5, (255, 0, 0, 255), "alice")
        assert result is True
        
        color = session.canvas.get_pixel(5, 5)
        assert color == (255, 0, 0, 255)
    
    def test_set_pixel_with_history(self):
        """Test that set_pixel records history."""
        session = CollabSession()
        session.add_user("alice")
        
        session.set_pixel(5, 5, (255, 0, 0, 255), "alice")
        
        assert session.history.can_undo()
    
    def test_undo_redo(self):
        """Test undo/redo in session."""
        session = CollabSession()
        session.add_user("alice")
        
        session.set_pixel(5, 5, (255, 0, 0, 255), "alice")
        session.undo("alice")
        
        # Pixel should be cleared
        color = session.canvas.get_pixel(5, 5)
        assert color[3] == 0  # Transparent
        
        session.redo("alice")
        color = session.canvas.get_pixel(5, 5)
        assert color == (255, 0, 0, 255)
    
    def test_cursor_tracking(self):
        """Test cursor position tracking."""
        session = CollabSession()
        session.add_user("alice")
        
        session.update_cursor("alice", 10, 20)
        
        cursors = session.get_cursors()
        assert cursors["alice"] == (10, 20)
    
    def test_chat(self):
        """Test chat functionality."""
        session = CollabSession()
        session.add_user("alice")
        
        session.add_chat("alice", "Hello!")
        
        history = session.get_chat_history()
        assert len(history) == 1
        assert history[0][0] == "alice"
        assert history[0][1] == "Hello!"
    
    def test_canvas_state(self):
        """Test getting/loading canvas state."""
        session = CollabSession(width=8, height=8)
        session.add_user("alice")
        
        session.set_pixel(2, 3, (255, 0, 0, 255), "alice")
        
        state = session.get_canvas_state()
        assert "2,3" in state
        assert state["2,3"] == [255, 0, 0, 255]
        
        # Load into new session
        session2 = CollabSession(width=8, height=8)
        session2.load_canvas_state(state)
        
        color = session2.canvas.get_pixel(2, 3)
        assert color == (255, 0, 0, 255)
    
    def test_callbacks(self):
        """Test session callbacks."""
        session = CollabSession()
        
        joined = []
        session.on_user_join(lambda u: joined.append(u.username))
        
        session.add_user("alice")
        assert "alice" in joined


class TestServerClient:
    """Tests for server/client (basic, no actual network)."""
    
    def test_create_server(self):
        """Test creating a server."""
        server = CollabServer(port=19999)
        assert server.session is not None
        assert not server.is_running()
    
    def test_create_client(self):
        """Test creating a client."""
        client = CollabClient("localhost", 19999, "alice")
        assert client.username == "alice"
        assert not client.is_connected()
    
    def test_server_session_access(self):
        """Test accessing server session."""
        server = CollabServer(port=19998, width=64, height=64)
        
        session = server.get_session()
        assert session.canvas.width == 64
        assert session.canvas.height == 64


class TestIntegration:
    """Integration tests with actual server/client connection."""
    
    def test_server_start_stop(self):
        """Test starting and stopping server."""
        server = CollabServer(port=19997)
        server.start()
        
        time.sleep(0.2)
        assert server.is_running()
        
        server.stop()
        time.sleep(0.2)
        # Note: is_running might still be True briefly
    
    def test_client_connect_disconnect(self):
        """Test client connection."""
        server = CollabServer(port=19996)
        server.start()
        time.sleep(0.2)
        
        try:
            client = CollabClient("localhost", 19996, "alice")
            connected = client.connect(timeout=2.0)
            
            assert connected
            assert client.is_connected()
            
            time.sleep(0.3)
            assert "alice" in client.get_users()
            
            client.disconnect()
        finally:
            server.stop()
    
    def test_two_clients(self):
        """Test two clients in same session."""
        server = CollabServer(port=19995)
        server.start()
        time.sleep(0.2)
        
        try:
            client1 = CollabClient("localhost", 19995, "alice")
            client2 = CollabClient("localhost", 19995, "bob")
            
            client1.connect(timeout=2.0)
            time.sleep(0.2)
            
            client2.connect(timeout=2.0)
            time.sleep(0.3)
            
            # Both should see each other
            users1 = client1.get_users()
            users2 = client2.get_users()
            
            assert "alice" in users1
            assert "bob" in users1
            assert "alice" in users2
            assert "bob" in users2
            
            client1.disconnect()
            client2.disconnect()
        finally:
            server.stop()
    
    def test_pixel_sync(self):
        """Test pixel synchronization between clients."""
        server = CollabServer(port=19994)
        server.start()
        time.sleep(0.2)
        
        received = []
        
        try:
            client1 = CollabClient("localhost", 19994, "alice")
            client2 = CollabClient("localhost", 19994, "bob")
            
            client2.on_pixel_change = lambda x, y, c, u: received.append((x, y, c, u))
            
            client1.connect(timeout=2.0)
            client2.connect(timeout=2.0)
            time.sleep(0.3)
            
            # Client 1 draws
            client1.set_pixel(5, 5, (255, 0, 0, 255))
            time.sleep(0.3)
            
            # Client 2 should receive
            assert len(received) > 0
            assert received[0][0] == 5
            assert received[0][1] == 5
            
            client1.disconnect()
            client2.disconnect()
        finally:
            server.stop()


if __name__ == '__main__':
    import traceback

    test_classes = [
        TestProtocol,
        TestActionHistory,
        TestCollabSession,
        TestServerClient,
        TestIntegration,
    ]

    passed = 0
    failed = 0
    errors = []

    for test_class in test_classes:
        instance = test_class()
        for name in dir(instance):
            if name.startswith('test_'):
                try:
                    getattr(instance, name)()
                    passed += 1
                    print(f"  ✓ {test_class.__name__}.{name}")
                except Exception as e:
                    failed += 1
                    errors.append((test_class.__name__, name, e, traceback.format_exc()))
                    print(f"  ✗ {test_class.__name__}.{name}: {e}")

    print(f"\n{'='*60}")
    print(f"Results: {passed} passed, {failed} failed")

    if errors:
        print(f"\nFailed tests:")
        for cls_name, test_name, error, tb in errors:
            print(f"\n{cls_name}.{test_name}:")
            print(tb)

    exit(0 if failed == 0 else 1)

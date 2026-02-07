"""WebSocket connection manager for real-time features"""
from typing import Dict, List, Set
from fastapi import WebSocket
from collections import defaultdict
import json
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and message broadcasting"""
    
    def __init__(self):
        # Store active connections by user_id
        self.active_connections: Dict[str, Set[WebSocket]] = defaultdict(set)
        # Store connections by room_id for chat rooms
        self.room_connections: Dict[str, Set[WebSocket]] = defaultdict(set)
        # Map WebSocket to user_id for cleanup
        self.websocket_users: Dict[WebSocket, str] = {}
        
    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept and register a new WebSocket connection"""
        await websocket.accept()
        self.active_connections[user_id].add(websocket)
        self.websocket_users[websocket] = user_id
        logger.info(f"User {user_id} connected. Total connections: {len(self.websocket_users)}")
        
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        user_id = self.websocket_users.get(websocket)
        if user_id:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
            del self.websocket_users[websocket]
            
            # Remove from all rooms
            for room_id in list(self.room_connections.keys()):
                if websocket in self.room_connections[room_id]:
                    self.room_connections[room_id].discard(websocket)
                    if not self.room_connections[room_id]:
                        del self.room_connections[room_id]
            
            logger.info(f"User {user_id} disconnected. Remaining connections: {len(self.websocket_users)}")
    
    async def join_room(self, websocket: WebSocket, room_id: str):
        """Add a connection to a chat room"""
        self.room_connections[room_id].add(websocket)
        logger.info(f"WebSocket joined room {room_id}. Room size: {len(self.room_connections[room_id])}")
        
    async def leave_room(self, websocket: WebSocket, room_id: str):
        """Remove a connection from a chat room"""
        if room_id in self.room_connections:
            self.room_connections[room_id].discard(websocket)
            if not self.room_connections[room_id]:
                del self.room_connections[room_id]
            logger.info(f"WebSocket left room {room_id}")
    
    async def send_personal_message(self, message: dict, user_id: str):
        """Send a message to a specific user (all their connections)"""
        if user_id in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending to user {user_id}: {e}")
                    disconnected.add(connection)
            
            # Clean up failed connections
            for connection in disconnected:
                self.disconnect(connection)
                
    async def broadcast_to_room(self, message: dict, room_id: str, exclude: WebSocket = None):
        """Broadcast message to all connections in a room"""
        if room_id in self.room_connections:
            disconnected = set()
            for connection in self.room_connections[room_id]:
                if connection != exclude:
                    try:
                        await connection.send_json(message)
                    except Exception as e:
                        logger.error(f"Error broadcasting to room {room_id}: {e}")
                        disconnected.add(connection)
            
            # Clean up failed connections
            for connection in disconnected:
                self.disconnect(connection)
    
    async def broadcast_to_all(self, message: dict):
        """Broadcast message to all connected users"""
        disconnected = []
        for websocket in self.websocket_users.keys():
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to all: {e}")
                disconnected.append(websocket)
        
        # Clean up failed connections
        for websocket in disconnected:
            self.disconnect(websocket)
    
    def get_room_users(self, room_id: str) -> Set[str]:
        """Get all user IDs in a specific room"""
        if room_id not in self.room_connections:
            return set()
        
        users = set()
        for websocket in self.room_connections[room_id]:
            user_id = self.websocket_users.get(websocket)
            if user_id:
                users.add(user_id)
        return users
    
    def get_online_status(self, user_id: str) -> bool:
        """Check if a user is currently online"""
        return user_id in self.active_connections and len(self.active_connections[user_id]) > 0


# Global connection manager instance
manager = ConnectionManager()

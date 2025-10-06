"""Session/room management for multiplayer games."""

import uuid
from typing import Dict, Optional
from web.multiplayer_game_engine import MultiplayerGameEngine


class SessionManager:
    """Manages multiple game sessions/rooms."""

    def __init__(self):
        """Initialize the session manager."""
        self.sessions: Dict[str, MultiplayerGameEngine] = {}
        self.player_sessions: Dict[str, str] = {}  # player_sid -> session_id

    def create_session(self) -> str:
        """Create a new game session and return its ID."""
        session_id = str(uuid.uuid4())[:8]  # Short ID like 'a3f2c9d1'
        self.sessions[session_id] = MultiplayerGameEngine()
        return session_id

    def get_session(self, session_id: str) -> Optional[MultiplayerGameEngine]:
        """Get a game session by ID."""
        return self.sessions.get(session_id)

    def join_session(self, session_id: str, player_sid: str) -> Optional[MultiplayerGameEngine]:
        """Join a player to a session."""
        if session_id not in self.sessions:
            return None

        self.player_sessions[player_sid] = session_id
        return self.sessions[session_id]

    def get_player_session(self, player_sid: str) -> Optional[str]:
        """Get the session ID for a player."""
        return self.player_sessions.get(player_sid)

    def remove_player(self, player_sid: str) -> None:
        """Remove a player from their session."""
        if player_sid in self.player_sessions:
            del self.player_sessions[player_sid]

    def session_exists(self, session_id: str) -> bool:
        """Check if a session exists."""
        return session_id in self.sessions

    def get_all_sessions(self) -> list:
        """Get list of all active sessions."""
        return [
            {
                'id': sid,
                'players': len([p for p, s in self.player_sessions.items() if s == sid])
            }
            for sid in self.sessions.keys()
        ]

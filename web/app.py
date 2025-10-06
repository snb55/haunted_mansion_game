"""Flask web server for the multiplayer Haunted Mansion game."""

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from web.multiplayer_game_engine import MultiplayerGameEngine

app = Flask(__name__)
app.config['SECRET_KEY'] = 'haunted-mansion-secret-key-2025'
socketio = SocketIO(app, cors_allowed_origins="*")

# Session-based game engines
game_sessions = {}  # session_code -> MultiplayerGameEngine
player_sessions = {}  # player_sid -> session_code


def get_or_create_session(session_code: str) -> MultiplayerGameEngine:
    """Get existing session or create a new one."""
    if session_code not in game_sessions:
        game_sessions[session_code] = MultiplayerGameEngine(session_id=session_code)
    return game_sessions[session_code]


@app.route('/')
def index():
    """Serve the main game page."""
    return render_template('index.html')


@socketio.on('connect')
def handle_connect():
    """Handle new client connection."""
    print(f"Client connected: {request.sid}")
    emit('connected', {'session_id': request.sid})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnect."""
    player_sid = request.sid
    print(f"Client disconnected: {player_sid}")

    # Get player's session
    if player_sid not in player_sessions:
        return

    session_code = player_sessions[player_sid]
    game_engine = game_sessions.get(session_code)

    if not game_engine:
        return

    # Get player's location before removing
    player = game_engine.get_player(player_sid)
    if player:
        location_id = player.current_location
        player_name = game_engine.player_names.get(player_sid, 'Someone')

        # Notify others in the same location
        emit('player_left', {
            'player_name': player_name
        }, room=f"{session_code}_{location_id}")

    # Remove player from game
    game_engine.remove_player(player_sid)
    del player_sessions[player_sid]


@socketio.on('join_game')
def handle_join_game(data):
    """Handle player joining the game."""
    player_sid = request.sid
    player_name = data.get('name', 'Adventurer')
    session_code = data.get('session_code', 'default')

    # Get or create game session
    game_engine = get_or_create_session(session_code)
    player_sessions[player_sid] = session_code

    # Add player to game
    player = game_engine.add_player(player_sid, player_name)

    # Join the room for their starting location (with session prefix)
    room_name = f"{session_code}_{player.current_location}"
    join_room(room_name)

    # Send initial game state
    result = game_engine.cmd_look(player_sid)

    emit('game_message', {
        'message': f"Welcome to the Haunted Mansion, {player_name}!",
        'type': 'system'
    })

    emit('game_message', {
        'message': result['message'],
        'type': 'look'
    })

    # Notify others in the same location
    emit('player_joined', {
        'player_name': player_name
    }, room=room_name, include_self=False)

    print(f"Player {player_name} joined session {session_code} with sid {player_sid}")


@socketio.on('command')
def handle_command(data):
    """Handle game command from player."""
    player_sid = request.sid
    command = data.get('command', '').strip()

    if not command:
        return

    # Get player's session
    if player_sid not in player_sessions:
        emit('game_message', {
            'message': "You haven't joined the game yet.",
            'type': 'error'
        })
        return

    session_code = player_sessions[player_sid]
    game_engine = game_sessions.get(session_code)

    if not game_engine:
        emit('game_message', {
            'message': "Game session not found.",
            'type': 'error'
        })
        return

    player = game_engine.get_player(player_sid)
    if not player:
        emit('game_message', {
            'message': "Player not found in session.",
            'type': 'error'
        })
        return

    # Execute command
    result = game_engine.execute_command(player_sid, command)

    # Send result to the player
    emit('game_message', {
        'message': result['message'],
        'type': 'success' if result.get('success') else 'error'
    })

    # Handle location changes (player moved)
    if result.get('location_changed'):
        old_location = result.get('old_location')
        new_location = result.get('new_location')

        old_room = f"{session_code}_{old_location}"
        new_room = f"{session_code}_{new_location}"

        # Leave old location room
        leave_room(old_room)

        # Join new location room
        join_room(new_room)

        # Notify players in old location
        if old_location and result.get('broadcast_message'):
            emit('game_message', {
                'message': result['broadcast_message'],
                'type': 'info'
            }, room=old_room)

        # Notify players in new location
        player_name = game_engine.player_names.get(player_sid, 'Someone')
        emit('player_arrived', {
            'player_name': player_name
        }, room=new_room, include_self=False)

    # Handle broadcasts (item taken, used, etc.)
    elif result.get('broadcast') and result.get('broadcast_message'):
        location_id = result.get('location_id')
        if location_id:
            room_name = f"{session_code}_{location_id}"
            emit('game_message', {
                'message': result['broadcast_message'],
                'type': 'info'
            }, room=room_name, include_self=False)

    # Handle win condition
    if result.get('game_won'):
        player_name = game_engine.player_names.get(player_sid, 'Someone')
        # Broadcast to entire session
        for sid, code in player_sessions.items():
            if code == session_code:
                emit('game_won', {
                    'player_name': player_name
                }, room=sid)


if __name__ == '__main__':
    print("Starting Haunted Mansion Web Server...")
    print("Visit http://localhost:5007 in your browser")
    socketio.run(app, host='0.0.0.0', port=5007, debug=True)

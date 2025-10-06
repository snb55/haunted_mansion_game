"""Firebase Cloud Functions for Haunted Mansion Game"""
import os
import sys
from firebase_functions import https_fn, options
from firebase_admin import initialize_app, firestore
import json

# Initialize Firebase Admin (but don't create client yet)
_app = None
_db = None

def get_db():
    """Lazy load Firestore client"""
    global _app, _db
    if _app is None:
        _app = initialize_app()
    if _db is None:
        _db = firestore.client()
    return _db

# Lazy import game modules to avoid cold start timeout
def get_game_engine():
    """Lazy load GameEngine to avoid initialization timeout"""
    sys.path.insert(0, os.path.dirname(__file__))
    from game.game_engine import GameEngine
    return GameEngine

def get_ascii_art():
    """Lazy load ascii art module"""
    sys.path.insert(0, os.path.dirname(__file__))
    from game import ascii_art
    return ascii_art


def get_image_for_location(game_state: dict, player_state: dict = None) -> str:
    """Get appropriate image path for current location based on game state."""
    location_id = game_state.get('current_location')
    locations_state = game_state.get('locations', {})

    if not location_id or location_id not in locations_state:
        return ""

    location = locations_state[location_id]
    state = location.get('state', {})

    # Determine if player is talking to NPC (passed from session/context)
    player_talking_to_npc = player_state.get('talking_to_npc') if player_state else False

    if location_id == 'entrance_hall':
        # Check if player has escaped (game won)
        if state.get('door_unlocked') and player_state and player_state.get('player_outside'):
            return 'images/entrance_hall/outside_of_mansion.png'
        # Door is unlocked
        elif state.get('door_unlocked'):
            return 'images/entrance_hall/entrance_hall_door_unlocked.png'
        # Eliza gave away candle
        elif state.get('eliza_gave_candle'):
            return 'images/entrance_hall/entrance_hall_eliza_gave_candle.png'
        # Player is talking to Eliza (and she still has candle)
        elif player_talking_to_npc:
            return 'images/entrance_hall/entrance_hall_eliza_speaking.png'
        # Default state
        else:
            return 'images/entrance_hall/entrance_hall_default.png'

    elif location_id == 'library':
        # Secret passage revealed
        if state.get('secret_passage_revealed'):
            return 'images/library/library_secret_revealed.png'
        # Edgar gave away amulet
        elif state.get('edgar_gave_amulet'):
            return 'images/library/library_edgar_gave_amulet.png'
        # Player is talking to Edgar
        elif player_talking_to_npc:
            return 'images/library/library_edgar_speaking.png'
        # Default state
        else:
            return 'images/library/library_default.png'

    elif location_id == 'basement':
        # Lights are on
        if state.get('lights_on'):
            # Check if key has been taken
            items_in_location = location.get('items', [])
            if 'rusty_key' not in items_in_location:
                return 'images/basement/basement_lit_key_taken.png'
            else:
                return 'images/basement/basement_lit_key_visible.png'
        # Pitch dark (no candle used)
        else:
            return 'images/basement/basement_pitch_dark.png'

    return ""


def get_ascii_art_for_location(game_state: dict) -> str:
    """Get appropriate ASCII art for current location."""
    ascii_art = get_ascii_art()
    location_id = game_state.get('current_location')
    locations_state = game_state.get('locations', {})

    if not location_id or location_id not in locations_state:
        return ""

    location = locations_state[location_id]

    if location_id == 'entrance_hall':
        if location.get('state', {}).get('door_unlocked'):
            return ascii_art.DOOR_UNLOCKED
        return ascii_art.ENTRANCE_HALL
    elif location_id == 'library':
        if location.get('state', {}).get('secret_passage_revealed'):
            return ascii_art.LIBRARY_SECRET
        return ascii_art.LIBRARY
    elif location_id == 'basement':
        if location.get('state', {}).get('lights_on'):
            return ascii_art.BASEMENT_LIT
        return ascii_art.BASEMENT_DARK

    return ""


def get_available_actions(engine) -> list:
    """Get all available actions based on current game state."""
    actions = []
    location = engine.get_current_location()

    if location is None:
        return []

    # Always available
    actions.append({'icon': '👁️', 'label': 'Look Around', 'command': 'look'})
    actions.append({'icon': '🎒', 'label': 'Check Inventory', 'command': 'inventory'})

    # NPCs to talk to
    npcs_here = [npc for npc in engine.npcs.values() if npc.location == location.id]
    for npc in npcs_here:
        actions.append({'icon': '💬', 'label': f'Chat with {npc.name}', 'command': f'start_chat_{npc.id}'})

    # Items to take
    if location.items:
        for item_id in location.items:
            if item_id in engine.items:
                # Special case: rusty_key in basement can only be taken if lights are on
                if location.id == 'basement' and item_id == 'rusty_key' and not location.get_state('lights_on'):
                    continue  # Don't show the key in darkness
                
                item = engine.items[item_id]
                actions.append({'icon': '📦', 'label': f'Take {item.name}', 'command': f'take {item.name}'})

    # Items to use (from inventory)
    if engine.player.inventory:
        for item_id in engine.player.inventory:
            if item_id in engine.items:
                item = engine.items[item_id]
                actions.append({'icon': '🔧', 'label': f'Use {item.name}', 'command': f'use {item.name}'})

    # Items to drop
    if engine.player.inventory:
        for item_id in engine.player.inventory:
            if item_id in engine.items:
                item = engine.items[item_id]
                actions.append({'icon': '⬇️', 'label': f'Drop {item.name}', 'command': f'drop {item.name}'})

    # Stationary objects to examine
    if location.stationary_objects:
        for obj_id in location.stationary_objects:
            if obj_id in engine.stationary_objects:
                obj = engine.stationary_objects[obj_id]
                actions.append({'icon': '🔍', 'label': f'Examine {obj.name}', 'command': f'examine {obj.name}'})

    # Movement options
    if location.exits:
        for direction in location.list_exits():
            actions.append({'icon': '🚶', 'label': f'Go {direction.upper()}', 'command': f'go {direction}'})

    # Special: secret passage
    if location.id == 'library' and location.get_state('secret_passage_revealed'):
        actions.append({'icon': '🚶', 'label': 'Go DOWN', 'command': 'go down'})

    # Special: Exit Mansion when door is unlocked - ONLY option!
    if location.id == 'entrance_hall' and location.get_state('door_unlocked'):
        return [{'icon': '🚪', 'label': '🌟 EXIT MANSION 🌟', 'command': 'exit_mansion', 'special': 'exit'}]

    return actions


def execute_action_with_art(engine, command: str) -> dict:
    """Execute command and return result."""
    result = {'message': '', 'art': '', 'image': '', 'game_won': False}

    if command == 'save':
        result['message'] = '✓ Game will be auto-saved!'
        return result

    output = engine.execute_command(command)
    result['message'] = output

    # Add images for specific actions (no ASCII art)
    verb, args = engine.parse_command(command)

    if verb in ['examine', 'x'] and args:
        target = ' '.join(args)
        target_id = target.lower().replace(' ', '_')
        if target_id == 'locked_door':
            location = engine.get_current_location()
            if location and location.get_state('door_unlocked'):
                result['image'] = 'images/entrance_hall/entrance_hall_door_unlocked.png'
            else:
                result['image'] = 'images/entrance_hall/entrance_hall_lock.png'

    if engine.game_won:
        result['game_won'] = True

    return result


@https_fn.on_request(
    cors=options.CorsOptions(
        cors_origins=["*"],
        cors_methods=["GET", "POST", "OPTIONS"],
    ),
    memory=options.MemoryOption.GB_1,
    timeout_sec=60
)
def api(req: https_fn.Request) -> https_fn.Response:
    """Main API endpoint for game commands."""

    # Handle preflight
    if req.method == 'OPTIONS':
        return https_fn.Response(status=204)

    # Get user ID from request
    user_id = req.headers.get('X-User-ID')
    if not user_id:
        return https_fn.Response(
            response=json.dumps({'success': False, 'message': 'User ID required'}),
            status=401,
            headers={'Content-Type': 'application/json'}
        )

    # Parse path - Cloud Functions path can be '/', '/api', '/api/new_game' etc
    # When called via hosting rewrite, path will be like '/api/new_game'
    path = req.path
    
    # Remove '/api' prefix if present and extract endpoint
    if path.startswith('/api/'):
        endpoint = path[5:]  # Remove '/api/' prefix
    elif path.startswith('/api'):
        endpoint = path[4:].lstrip('/')  # Remove '/api' prefix
    elif path == '/':
        endpoint = ''
    else:
        endpoint = path.lstrip('/')
    
    # Also check query parameter for backward compatibility
    if not endpoint:
        endpoint = req.args.get('endpoint', '')

    try:
        # Route handling
        if endpoint == 'new_game' and req.method == 'POST':
            return handle_new_game(user_id)

        elif endpoint == 'load_game' and req.method == 'POST':
            return handle_load_game(user_id)

        elif endpoint == 'check_save' and req.method == 'GET':
            return handle_check_save(user_id)

        elif endpoint == 'execute' and req.method == 'POST':
            data = req.get_json(silent=True) or {}
            command = data.get('command', '')
            room_code = data.get('room_code')
            return handle_execute(user_id, command, room_code)

        elif endpoint == 'create_room' and req.method == 'POST':
            return handle_create_room(user_id)

        elif endpoint == 'join_room' and req.method == 'POST':
            data = req.get_json(silent=True) or {}
            room_code = data.get('room_code', '')
            return handle_join_room(user_id, room_code)

        elif endpoint == 'leave_room' and req.method == 'POST':
            data = req.get_json(silent=True) or {}
            room_code = data.get('room_code', '')
            return handle_leave_room(user_id, room_code)

        else:
            return https_fn.Response(
                response=json.dumps({'success': False, 'message': 'Not found'}),
                status=404,
                headers={'Content-Type': 'application/json'}
            )

    except Exception as e:
        return https_fn.Response(
            response=json.dumps({'success': False, 'message': str(e)}),
            status=500,
            headers={'Content-Type': 'application/json'}
        )


def handle_new_game(user_id: str) -> https_fn.Response:
    """Start a new game."""
    try:
        GameEngine = get_game_engine()
        engine = GameEngine()
        engine.new_game()
    except Exception as e:
        import traceback
        print(f"Error in handle_new_game: {str(e)}")
        print(traceback.format_exc())
        return https_fn.Response(
            response=json.dumps({'success': False, 'message': f'Error initializing game: {str(e)}'}),
            status=500,
            headers={'Content-Type': 'application/json'}
        )

    # Get game state
    game_state = engine.to_dict()

    # Save to Firestore
    db = get_db()
    db.collection('saves').document(user_id).set({
        'gameState': game_state,
        'savedAt': firestore.SERVER_TIMESTAMP
    })

    location_art = get_ascii_art_for_location(game_state)
    location_image = get_image_for_location(game_state)
    location_desc = engine.cmd_look()
    actions = get_available_actions(engine)

    return https_fn.Response(
        response=json.dumps({
            'success': True,
            'art': location_art,
            'image': location_image,
            'message': location_desc,
            'actions': actions
        }),
        headers={'Content-Type': 'application/json'}
    )


def handle_load_game(user_id: str) -> https_fn.Response:
    """Load saved game."""
    db = get_db()
    doc = db.collection('saves').document(user_id).get()

    if not doc.exists:
        return https_fn.Response(
            response=json.dumps({'success': False, 'message': 'No saved game found'}),
            headers={'Content-Type': 'application/json'}
        )

    game_state = doc.to_dict().get('gameState', {})

    # Restore game engine
    GameEngine = get_game_engine()
    engine = GameEngine()
    engine.from_dict(game_state)

    location_art = get_ascii_art_for_location(game_state)
    location_image = get_image_for_location(game_state)
    location_desc = engine.cmd_look()
    actions = get_available_actions(engine)

    return https_fn.Response(
        response=json.dumps({
            'success': True,
            'art': location_art,
            'image': location_image,
            'message': location_desc,
            'actions': actions
        }),
        headers={'Content-Type': 'application/json'}
    )


def handle_check_save(user_id: str) -> https_fn.Response:
    """Check if a saved game exists."""
    db = get_db()
    doc = db.collection('saves').document(user_id).get()

    return https_fn.Response(
        response=json.dumps({'exists': doc.exists}),
        headers={'Content-Type': 'application/json'}
    )


def handle_execute(user_id: str, command: str, room_code: str = None) -> https_fn.Response:
    """Execute a game command."""
    if not command:
        return https_fn.Response(
            response=json.dumps({'success': False, 'message': 'No command provided'}),
            headers={'Content-Type': 'application/json'}
        )

    db = get_db()

    # Load game state (from room or single player save)
    if room_code:
        doc = db.collection('gameSessions').document(room_code).get()
        if not doc.exists:
            return https_fn.Response(
                response=json.dumps({'success': False, 'message': 'Room not found'}),
                headers={'Content-Type': 'application/json'}
            )
        game_state = doc.to_dict().get('gameState', {})
    else:
        doc = db.collection('saves').document(user_id).get()
        if not doc.exists:
            return https_fn.Response(
                response=json.dumps({'success': False, 'message': 'No active game'}),
                headers={'Content-Type': 'application/json'}
            )
        game_state = doc.to_dict().get('gameState', {})

    # Restore and execute
    GameEngine = get_game_engine()
    engine = GameEngine()
    engine.from_dict(game_state)

    result = execute_action_with_art(engine, command)

    # Update game state
    updated_state = engine.to_dict()

    # Save back
    if room_code:
        db.collection('gameSessions').document(room_code).update({
            'gameState': updated_state,
            'lastActivity': firestore.SERVER_TIMESTAMP
        })
    else:
        db.collection('saves').document(user_id).set({
            'gameState': updated_state,
            'savedAt': firestore.SERVER_TIMESTAMP
        })

    location_art = get_ascii_art_for_location(updated_state)
    location_image = get_image_for_location(updated_state, {'talking_to_npc': command.startswith('talk')})
    location_desc = engine.cmd_look()
    actions = get_available_actions(engine)

    # Use action-specific image if available, otherwise use location image
    display_image = result.get('image') if result.get('image') else location_image

    return https_fn.Response(
        response=json.dumps({
            'success': True,
            'message': result['message'],
            'art': result.get('art', ''),
            'image': display_image,
            'location_art': location_art,
            'location_desc': location_desc,
            'actions': actions,
            'game_won': result.get('game_won', False)
        }),
        headers={'Content-Type': 'application/json'}
    )


def handle_create_room(user_id: str) -> https_fn.Response:
    """Create a new multiplayer room."""
    import random
    import string

    # Generate 6-character room code
    room_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

    # Initialize new game
    GameEngine = get_game_engine()
    engine = GameEngine()
    engine.new_game()
    game_state = engine.to_dict()

    # Create room in Firestore
    db = get_db()
    db.collection('gameSessions').document(room_code).set({
        'ownerId': user_id,
        'roomCode': room_code,
        'players': {user_id: 'Player 1'},
        'gameState': game_state,
        'createdAt': firestore.SERVER_TIMESTAMP,
        'lastActivity': firestore.SERVER_TIMESTAMP,
        'isActive': True
    })

    return https_fn.Response(
        response=json.dumps({
            'success': True,
            'roomCode': room_code,
            'message': f'Room created: {room_code}'
        }),
        headers={'Content-Type': 'application/json'}
    )


def handle_join_room(user_id: str, room_code: str) -> https_fn.Response:
    """Join an existing multiplayer room."""
    db = get_db()
    doc_ref = db.collection('gameSessions').document(room_code)
    doc = doc_ref.get()

    if not doc.exists:
        return https_fn.Response(
            response=json.dumps({'success': False, 'message': 'Room not found'}),
            headers={'Content-Type': 'application/json'}
        )

    # Add player to room
    players = doc.to_dict().get('players', {})
    player_num = len(players) + 1
    players[user_id] = f'Player {player_num}'

    doc_ref.update({
        'players': players,
        'lastActivity': firestore.SERVER_TIMESTAMP
    })

    return https_fn.Response(
        response=json.dumps({
            'success': True,
            'message': f'Joined room {room_code}'
        }),
        headers={'Content-Type': 'application/json'}
    )


def handle_leave_room(user_id: str, room_code: str) -> https_fn.Response:
    """Leave a multiplayer room."""
    db = get_db()
    doc_ref = db.collection('gameSessions').document(room_code)
    doc = doc_ref.get()

    if not doc.exists:
        return https_fn.Response(
            response=json.dumps({'success': False, 'message': 'Room not found'}),
            headers={'Content-Type': 'application/json'}
        )

    data = doc.to_dict()
    players = data.get('players', {})
    owner_id = data.get('ownerId')

    # Remove player
    if user_id in players:
        del players[user_id]

    # If no players left
    if len(players) == 0:
        # If owner is leaving, save their game
        if owner_id == user_id:
            db.collection('saves').document(user_id).set({
                'gameState': data.get('gameState', {}),
                'savedAt': firestore.SERVER_TIMESTAMP
            })
        # Delete room
        doc_ref.delete()
    else:
        # Update room
        doc_ref.update({
            'players': players,
            'lastActivity': firestore.SERVER_TIMESTAMP
        })

    return https_fn.Response(
        response=json.dumps({'success': True, 'message': 'Left room'}),
        headers={'Content-Type': 'application/json'}
    )

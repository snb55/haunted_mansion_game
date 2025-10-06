#!/usr/bin/env python3
"""
Simple Flask web server for Haunted Mansion - Single Player
No websockets, just clean HTTP requests like the CLI version
"""

from flask import Flask, render_template, request, jsonify, session
import sys
import os
from datetime import timedelta

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Load from parent directory where .env is located
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    load_dotenv(env_path)
    if os.getenv('GEMINI_API_KEY'):
        print("✅ Gemini API key loaded from .env file!")
except ImportError:
    print("Note: python-dotenv not installed. Using system environment variables only.")
except Exception as e:
    print(f"Note: Could not load .env file: {e}")

# Add parent directory to path AND change working directory to project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
os.chdir(project_root)  # Change to project root so game data files can be found

from game.game_engine import GameEngine
from game import ascii_art

app = Flask(__name__)
app.secret_key = 'haunted-mansion-simple-2025'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# Session-based game engines (one per web session)
game_sessions = {}


def get_game_engine():
    """Get or create game engine for current session."""
    session_id = session.get('session_id')
    
    if not session_id:
        import uuid
        session_id = str(uuid.uuid4())
        session['session_id'] = session_id
        session.permanent = True
    
    if session_id not in game_sessions:
        game_sessions[session_id] = GameEngine()
    
    return game_sessions[session_id]


def get_ascii_art_for_location(engine: GameEngine) -> str:
    """Get appropriate ASCII art for current location."""
    location = engine.get_current_location()
    if not location:
        return ""

    if location.id == 'entrance_hall':
        if location.get_state('door_unlocked'):
            return ascii_art.DOOR_UNLOCKED
        return ascii_art.ENTRANCE_HALL
    elif location.id == 'library':
        if location.get_state('secret_passage_revealed'):
            return ascii_art.LIBRARY_SECRET
        return ascii_art.LIBRARY
    elif location.id == 'basement':
        if location.get_state('lights_on'):
            return ascii_art.BASEMENT_LIT
        return ascii_art.BASEMENT_DARK

    return ""


def get_available_actions(engine: GameEngine) -> list:
    """Get all available actions based on current game state."""
    actions = []
    location = engine.get_current_location()

    if location is None:
        return []

    # Always available
    actions.append({
        'icon': '👁️',
        'label': 'Look Around',
        'command': 'look'
    })
    
    actions.append({
        'icon': '🎒',
        'label': 'Check Inventory',
        'command': 'inventory'
    })

    # NPCs to talk to - start conversation mode
    npcs_here = [npc for npc in engine.npcs.values() if npc.location == location.id]
    for npc in npcs_here:
        actions.append({
            'icon': '💬',
            'label': f'Chat with {npc.name}',
            'command': f'start_chat_{npc.id}'
        })

    # Items to take
    if location.items:
        for item_id in location.items:
            if item_id in engine.items:
                # Special case: rusty_key in basement can only be taken if lights are on
                if location.id == 'basement' and item_id == 'rusty_key' and not location.get_state('lights_on'):
                    continue  # Don't show the key in darkness
                
                item = engine.items[item_id]
                actions.append({
                    'icon': '📦',
                    'label': f'Take {item.name}',
                    'command': f'take {item.name}'
                })

    # Items to use (from inventory)
    if engine.player.inventory:
        for item_id in engine.player.inventory:
            if item_id in engine.items:
                item = engine.items[item_id]
                actions.append({
                    'icon': '🔧',
                    'label': f'Use {item.name}',
                    'command': f'use {item.name}'
                })

    # Items to drop
    if engine.player.inventory:
        for item_id in engine.player.inventory:
            if item_id in engine.items:
                item = engine.items[item_id]
                actions.append({
                    'icon': '⬇️',
                    'label': f'Drop {item.name}',
                    'command': f'drop {item.name}'
                })

    # Stationary objects to examine
    if location.stationary_objects:
        for obj_id in location.stationary_objects:
            if obj_id in engine.stationary_objects:
                obj = engine.stationary_objects[obj_id]
                actions.append({
                    'icon': '🔍',
                    'label': f'Examine {obj.name}',
                    'command': f'examine {obj.name}'
                })

    # Movement options
    if location.exits:
        for direction in location.list_exits():
            actions.append({
                'icon': '🚶',
                'label': f'Go {direction.upper()}',
                'command': f'go {direction}'
            })

    # Special: secret passage
    if location.id == 'library' and location.get_state('secret_passage_revealed'):
        actions.append({
            'icon': '🚶',
            'label': 'Go DOWN',
            'command': 'go down'
        })

    # Special: Exit Mansion when door is unlocked - ONLY option!
    if location.id == 'entrance_hall' and location.get_state('door_unlocked'):
        return [{
            'icon': '🚪',
            'label': '🌟 EXIT MANSION 🌟',
            'command': 'exit_mansion',
            'special': 'exit'
        }]

    return actions


def execute_action_with_art(engine: GameEngine, command: str) -> dict:
    """Execute command and return result."""
    result = {
        'message': '',
        'art': '',
        'game_won': False,
        'game_over': False
    }
    
    # Handle special commands
    if command == 'save':
        engine.save_game()
        result['message'] = '✓ Game saved successfully!'
        return result
    
    # Execute the command
    output = engine.execute_command(command)
    result['message'] = output
    
    # Check for win condition
    if engine.game_won:
        result['game_won'] = True
    
    return result


@app.route('/')
def index():
    """Serve the main game page."""
    return render_template('simple.html')


@app.route('/api/new_game', methods=['POST'])
def new_game():
    """Start a new game."""
    engine = get_game_engine()
    engine.new_game()
    
    location_art = get_ascii_art_for_location(engine)
    location_desc = engine.cmd_look()
    actions = get_available_actions(engine)
    
    return jsonify({
        'success': True,
        'art': location_art,
        'message': location_desc,
        'actions': actions,
        'session_id': session.get('session_id', 'unknown')
    })


@app.route('/api/load_game', methods=['POST'])
def load_game():
    """Load saved game."""
    engine = get_game_engine()
    
    if not engine.persistence.save_exists():
        return jsonify({
            'success': False,
            'message': 'No saved game found.'
        })
    
    if engine.load_game():
        location_art = get_ascii_art_for_location(engine)
        location_desc = engine.cmd_look()
        actions = get_available_actions(engine)
        
        return jsonify({
            'success': True,
            'art': location_art,
            'message': location_desc,
            'actions': actions,
            'session_id': session.get('session_id', 'unknown')
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Failed to load game.'
        })


@app.route('/api/check_save', methods=['GET'])
def check_save():
    """Check if a saved game exists."""
    engine = get_game_engine()
    return jsonify({
        'exists': engine.persistence.save_exists()
    })


@app.route('/api/execute', methods=['POST'])
def execute():
    """Execute a game command."""
    data = request.get_json()
    command = data.get('command', '').strip()
    
    if not command:
        return jsonify({
            'success': False,
            'message': 'No command provided.'
        })
    
    engine = get_game_engine()
    
    # Execute command and get result with art
    result = execute_action_with_art(engine, command)
    
    # Get updated game state INCLUDING location description
    location_art = get_ascii_art_for_location(engine)
    location_desc = engine.cmd_look()  # Get updated location description
    actions = get_available_actions(engine)
    
    return jsonify({
        'success': True,
        'message': result['message'],
        'art': result.get('art', ''),
        'location_art': location_art,
        'location_desc': location_desc,  # Send updated location info
        'actions': actions,
        'game_won': result.get('game_won', False),
        'game_over': result.get('game_over', False)
    })


@app.route('/api/look', methods=['GET'])
def look():
    """Get current location view."""
    engine = get_game_engine()
    
    if engine.player is None:
        return jsonify({
            'success': False,
            'message': 'No active game. Please start a new game.'
        })
    
    location_art = get_ascii_art_for_location(engine)
    location_desc = engine.cmd_look()
    actions = get_available_actions(engine)
    
    return jsonify({
        'success': True,
        'art': location_art,
        'message': location_desc,
        'actions': actions
    })


if __name__ == '__main__':
    print("=" * 60)
    print("  Starting Haunted Mansion Web Server (Simple Version)")
    print("=" * 60)
    print("\n  🌐 Visit: http://localhost:5008")
    print("  📱 Or:    http://0.0.0.0:5008")
    print("\n  Press Ctrl+C to stop the server\n")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5008, debug=True)


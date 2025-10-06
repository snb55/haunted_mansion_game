"""Multiplayer game engine for the Haunted Mansion web game."""

import json
import os
from typing import Dict, Optional, List, Tuple
from datetime import datetime
import threading

from game.models.location import Location
from game.models.item import Item, StationaryObject
from game.models.player import Player


class MultiplayerGameEngine:
    """Game engine that supports multiple concurrent players in a shared world."""

    def __init__(self, session_id: str = 'default'):
        """Initialize the multiplayer game engine."""
        self.session_id = session_id
        self.locations: Dict[str, Location] = {}
        self.items: Dict[str, Item] = {}
        self.stationary_objects: Dict[str, StationaryObject] = {}
        self.players: Dict[str, Player] = {}  # player_sid -> Player
        self.player_names: Dict[str, str] = {}  # player_sid -> player name
        self.lock = threading.Lock()  # For thread-safe state management
        self.game_state_file = f'saves/session_{session_id}.json'

        # Load game data
        self._load_game_data()
        self._load_world_state()

    def _load_game_data(self) -> None:
        """Load locations and items from JSON files."""
        # Determine base directory (works from both /web and project root)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Load locations
        locations_path = os.path.join(base_dir, 'game', 'data', 'locations.json')
        with open(locations_path, 'r') as f:
            locations_data = json.load(f)

        for loc_id, loc_data in locations_data.items():
            location = Location(
                location_id=loc_id,
                name=loc_data['name'],
                description=loc_data['description'],
                initial_state=loc_data['initial_state'],
                exits=loc_data['exits'],
                initial_items=loc_data['initial_items'],
                stationary_objects=loc_data['stationary_objects']
            )
            self.locations[loc_id] = location

        # Load items
        items_path = os.path.join(base_dir, 'game', 'data', 'items.json')
        with open(items_path, 'r') as f:
            items_data = json.load(f)

        # Load mobile items
        for item_id, item_data in items_data['mobile_items'].items():
            item = Item(
                item_id=item_id,
                name=item_data['name'],
                description=item_data['description'],
                can_take=item_data['can_take'],
                use_targets=item_data.get('use_targets', [])
            )
            self.items[item_id] = item

        # Load stationary objects
        for obj_id, obj_data in items_data['stationary_objects'].items():
            obj = StationaryObject(
                object_id=obj_id,
                name=obj_data['name'],
                description=obj_data['description'],
                interaction_message=obj_data['interaction_message'],
                success_message=obj_data['success_message'],
                required_item=obj_data.get('required_item'),
                state_change=obj_data.get('state_change')
            )
            self.stationary_objects[obj_id] = obj

    def _load_world_state(self) -> None:
        """Load the shared world state if it exists."""
        if os.path.exists(self.game_state_file):
            try:
                with open(self.game_state_file, 'r') as f:
                    data = json.load(f)
                    world_state = data.get('world_state', {})

                    # Restore location states
                    for loc_id, loc_data in world_state.get('locations', {}).items():
                        if loc_id in self.locations:
                            self.locations[loc_id].from_dict(loc_data)
            except Exception as e:
                print(f"Error loading world state: {e}")

    def _save_world_state(self) -> None:
        """Save the shared world state."""
        try:
            world_state = {
                'locations': {
                    loc_id: loc.to_dict()
                    for loc_id, loc in self.locations.items()
                }
            }

            save_data = {
                'version': '1.0',
                'timestamp': datetime.now().isoformat(),
                'world_state': world_state
            }

            os.makedirs('saves', exist_ok=True)
            with open(self.game_state_file, 'w') as f:
                json.dump(save_data, f, indent=2)
        except Exception as e:
            print(f"Error saving world state: {e}")

    def add_player(self, session_id: str, player_name: str) -> Player:
        """Add a new player to the game."""
        with self.lock:
            if session_id not in self.players:
                self.players[session_id] = Player(current_location='entrance_hall')
                self.player_names[session_id] = player_name
            return self.players[session_id]

    def remove_player(self, session_id: str) -> None:
        """Remove a player from the game."""
        with self.lock:
            if session_id in self.players:
                del self.players[session_id]
            if session_id in self.player_names:
                del self.player_names[session_id]

    def get_player(self, session_id: str) -> Optional[Player]:
        """Get a player by session ID."""
        return self.players.get(session_id)

    def get_current_location(self, session_id: str) -> Optional[Location]:
        """Get a player's current location."""
        player = self.get_player(session_id)
        if player is None:
            return None
        return self.locations.get(player.current_location)

    def get_players_in_location(self, location_id: str) -> List[Tuple[str, str]]:
        """Get list of (session_id, name) for players in a specific location."""
        players_here = []
        with self.lock:
            for sid, player in self.players.items():
                if player.current_location == location_id:
                    players_here.append((sid, self.player_names.get(sid, 'Unknown')))
        return players_here

    def parse_command(self, command: str) -> tuple:
        """Parse a command string into verb and arguments."""
        parts = command.lower().strip().split()
        if not parts:
            return ('', [])
        verb = parts[0]
        args = parts[1:]
        return (verb, args)

    def execute_command(self, session_id: str, command: str) -> Dict:
        """
        Execute a command and return the result.

        Returns a dict with:
        - success: bool
        - message: str
        - broadcast: bool (whether to notify other players)
        - location_changed: bool
        - game_won: bool
        """
        verb, args = self.parse_command(command)

        if verb == 'look' or verb == 'l':
            return self.cmd_look(session_id)
        elif verb == 'go' or verb == 'move':
            if not args:
                return {'success': False, 'message': "Go where? Specify a direction.", 'broadcast': False}
            return self.cmd_go(session_id, args[0])
        elif verb == 'take' or verb == 'get' or verb == 'grab':
            if not args:
                return {'success': False, 'message': "Take what?", 'broadcast': False}
            return self.cmd_take(session_id, ' '.join(args))
        elif verb == 'drop':
            if not args:
                return {'success': False, 'message': "Drop what?", 'broadcast': False}
            return self.cmd_drop(session_id, ' '.join(args))
        elif verb == 'inventory' or verb == 'i':
            return self.cmd_inventory(session_id)
        elif verb == 'use':
            if not args:
                return {'success': False, 'message': "Use what?", 'broadcast': False}
            return self.cmd_use(session_id, ' '.join(args))
        elif verb == 'examine' or verb == 'x':
            if not args:
                return {'success': False, 'message': "Examine what?", 'broadcast': False}
            return self.cmd_examine(session_id, ' '.join(args))
        elif verb == 'help' or verb == 'h' or verb == '?':
            return self.cmd_help()
        else:
            return {'success': False, 'message': f"I don't understand '{verb}'. Type 'help' for commands.", 'broadcast': False}

    def cmd_look(self, session_id: str) -> Dict:
        """Look around the current location."""
        location = self.get_current_location(session_id)
        if location is None:
            return {'success': False, 'message': "You are nowhere.", 'broadcast': False}

        desc = location.describe()

        # Special case: basement darkness
        if location.id == 'basement' and not location.get_state('lights_on'):
            desc = f"\n{location.name}\n{'=' * len(location.name)}\n"
            desc += "It's pitch black. You can't see anything. You might want to light a candle.\n"

        # Special case: secret passage revealed
        if location.id == 'library' and location.get_state('secret_passage_revealed'):
            desc = desc.replace("Exits: south", "Exits: south, down")

        # Add other players in this location
        other_players = [name for sid, name in self.get_players_in_location(location.id) if sid != session_id]
        if other_players:
            desc += f"\nOther adventurers here: {', '.join(other_players)}\n"

        # Add helpful action hints
        desc += "\n💡 What to do:\n"

        # Show available items to take
        if location.items:
            for item_id in location.items:
                if item_id in self.items:
                    desc += f"  • 'take {self.items[item_id].name.lower()}' - Pick up the {self.items[item_id].name}\n"

        # Show stationary objects to examine/use
        if location.stationary_objects:
            for obj_id in location.stationary_objects:
                if obj_id in self.stationary_objects:
                    obj = self.stationary_objects[obj_id]
                    desc += f"  • 'examine {obj.name.lower()}' - Look at the {obj.name}\n"

        # Show exits
        if location.exits:
            for direction in location.list_exits():
                desc += f"  • 'go {direction}' - Go {direction}\n"

        # Special handling for secret passage
        if location.id == 'library' and location.get_state('secret_passage_revealed'):
            desc += f"  • 'go down' - Descend into the basement\n"

        desc += "  • 'inventory' - Check what you're carrying\n"
        desc += "  • 'help' - See all commands\n"

        return {'success': True, 'message': desc, 'broadcast': False}

    def cmd_go(self, session_id: str, direction: str) -> Dict:
        """Move in a direction."""
        with self.lock:
            player = self.get_player(session_id)
            location = self.get_current_location(session_id)

            if player is None or location is None:
                return {'success': False, 'message': "You are nowhere.", 'broadcast': False}

            # Basement darkness check
            if location.id == 'basement' and not location.get_state('lights_on'):
                return {'success': False, 'message': "It's too dark to see where you're going.", 'broadcast': False}

            # Secret passage handling
            if location.id == 'library' and direction == 'down':
                if location.get_state('secret_passage_revealed'):
                    old_location = player.current_location
                    player.move_to('basement')
                    player_name = self.player_names.get(session_id, 'Someone')
                    return {
                        'success': True,
                        'message': self.cmd_look(session_id)['message'],
                        'broadcast': True,
                        'broadcast_message': f"{player_name} descended into the basement.",
                        'old_location': old_location,
                        'new_location': 'basement',
                        'location_changed': True
                    }
                else:
                    return {'success': False, 'message': "You don't see a way down.", 'broadcast': False}

            # Normal movement
            next_location_id = location.get_exit(direction)
            if next_location_id is None:
                return {'success': False, 'message': f"You can't go {direction}.", 'broadcast': False}

            old_location = player.current_location
            player.move_to(next_location_id)
            player_name = self.player_names.get(session_id, 'Someone')

            return {
                'success': True,
                'message': self.cmd_look(session_id)['message'],
                'broadcast': True,
                'broadcast_message': f"{player_name} went {direction}.",
                'old_location': old_location,
                'new_location': next_location_id,
                'location_changed': True
            }

    def cmd_take(self, session_id: str, item_name: str) -> Dict:
        """Take an item."""
        with self.lock:
            player = self.get_player(session_id)
            location = self.get_current_location(session_id)

            if player is None or location is None:
                return {'success': False, 'message': "You are nowhere.", 'broadcast': False}

            item_id = item_name.lower().replace(' ', '_')

            if not location.has_item(item_id):
                return {'success': False, 'message': f"There's no {item_name} here.", 'broadcast': False}

            if item_id not in self.items:
                return {'success': False, 'message': f"You can't take the {item_name}.", 'broadcast': False}

            item = self.items[item_id]
            if not item.can_take:
                return {'success': False, 'message': f"You can't take the {item_name}.", 'broadcast': False}

            if player.is_inventory_full():
                return {'success': False, 'message': "Your inventory is full.", 'broadcast': False}

            location.remove_item(item_id)
            player.add_item(item_id)
            self._save_world_state()

            player_name = self.player_names.get(session_id, 'Someone')
            return {
                'success': True,
                'message': f"You take the {item.name}.",
                'broadcast': True,
                'broadcast_message': f"{player_name} took the {item.name}.",
                'location_id': location.id
            }

    def cmd_drop(self, session_id: str, item_name: str) -> Dict:
        """Drop an item."""
        with self.lock:
            player = self.get_player(session_id)
            location = self.get_current_location(session_id)

            if player is None or location is None:
                return {'success': False, 'message': "You are nowhere.", 'broadcast': False}

            item_id = item_name.lower().replace(' ', '_')

            if not player.has_item(item_id):
                return {'success': False, 'message': f"You don't have a {item_name}.", 'broadcast': False}

            if item_id not in self.items:
                return {'success': False, 'message': f"Unknown item: {item_name}.", 'broadcast': False}

            item = self.items[item_id]
            player.remove_item(item_id)
            location.add_item(item_id)
            self._save_world_state()

            player_name = self.player_names.get(session_id, 'Someone')
            return {
                'success': True,
                'message': f"You drop the {item.name}.",
                'broadcast': True,
                'broadcast_message': f"{player_name} dropped the {item.name}.",
                'location_id': location.id
            }

    def cmd_inventory(self, session_id: str) -> Dict:
        """Show inventory."""
        player = self.get_player(session_id)
        if player is None:
            return {'success': False, 'message': "You are nowhere.", 'broadcast': False}

        if not player.inventory:
            return {'success': True, 'message': "You're not carrying anything.", 'broadcast': False}

        inv_list = []
        for item_id in player.inventory:
            if item_id in self.items:
                inv_list.append(self.items[item_id].name)

        return {'success': True, 'message': "Carrying: " + ", ".join(inv_list), 'broadcast': False}

    def cmd_use(self, session_id: str, item_name: str) -> Dict:
        """Use an item."""
        with self.lock:
            player = self.get_player(session_id)
            location = self.get_current_location(session_id)

            if player is None or location is None:
                return {'success': False, 'message': "You are nowhere.", 'broadcast': False}

            item_id = item_name.lower().replace(' ', '_')

            # Candle in basement
            if item_id == 'candle' and location.id == 'basement':
                if player.has_item('candle'):
                    location.set_state('lights_on', True)
                    self._save_world_state()
                    player_name = self.player_names.get(session_id, 'Someone')
                    return {
                        'success': True,
                        'message': "You light the candle. The basement illuminates, revealing a rusty key!",
                        'broadcast': True,
                        'broadcast_message': f"{player_name} lit a candle. The basement is now illuminated!",
                        'location_id': location.id
                    }
                else:
                    return {'success': False, 'message': "You don't have a candle.", 'broadcast': False}

            if not player.has_item(item_id):
                return {'success': False, 'message': f"You don't have a {item_name}.", 'broadcast': False}

            if item_id not in self.items:
                return {'success': False, 'message': f"Unknown item: {item_name}.", 'broadcast': False}

            # Try using on stationary objects
            for obj_id in location.stationary_objects:
                if obj_id in self.stationary_objects:
                    obj = self.stationary_objects[obj_id]
                    if obj.required_item == item_id or (obj_id == 'bookshelf_lever' and item_id == 'ancient_amulet'):
                        result_msg = obj.success_message
                        game_won = False

                        if obj.state_change:
                            loc_id = obj.state_change['location']
                            state_key = obj.state_change['state_key']
                            new_value = obj.state_change['new_value']

                            if loc_id in self.locations:
                                self.locations[loc_id].set_state(state_key, new_value)
                                self._save_world_state()

                                if loc_id == 'entrance_hall' and state_key == 'door_unlocked':
                                    game_won = True
                                    result_msg += "\n\nThe door is unlocked! You can escape!\n*** YOU WIN! ***"

                        player_name = self.player_names.get(session_id, 'Someone')
                        return {
                            'success': True,
                            'message': result_msg,
                            'broadcast': True,
                            'broadcast_message': f"{player_name} used the {self.items[item_id].name}!",
                            'location_id': location.id,
                            'game_won': game_won
                        }

            return {'success': False, 'message': f"You can't use the {item_name} here.", 'broadcast': False}

    def cmd_examine(self, session_id: str, target: str) -> Dict:
        """Examine an item or object."""
        player = self.get_player(session_id)
        location = self.get_current_location(session_id)

        if player is None or location is None:
            return {'success': False, 'message': "You are nowhere.", 'broadcast': False}

        target_id = target.lower().replace(' ', '_')

        # Check inventory
        if player.has_item(target_id) and target_id in self.items:
            return {'success': True, 'message': self.items[target_id].description, 'broadcast': False}

        # Check location
        if location.has_item(target_id) and target_id in self.items:
            return {'success': True, 'message': self.items[target_id].description, 'broadcast': False}

        # Check stationary objects
        if target_id in location.stationary_objects and target_id in self.stationary_objects:
            return {'success': True, 'message': self.stationary_objects[target_id].description, 'broadcast': False}

        return {'success': False, 'message': f"You don't see a {target} here.", 'broadcast': False}

    def cmd_help(self) -> Dict:
        """Show help."""
        help_text = """Commands: look, go <dir>, take <item>, drop <item>, inventory, use <item>, examine <target>, help"""
        return {'success': True, 'message': help_text, 'broadcast': False}

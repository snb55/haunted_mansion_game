"""Main game engine for the Haunted Mansion game."""

import json
import os
from typing import Dict, Optional, List

from game.models.location import Location
from game.models.item import Item, StationaryObject
from game.models.player import Player
from game.utils.persistence import GameStatePersistence
from game.ai_npc import AINPC


class GameEngine:
    """Main game engine that manages game state and logic."""

    def __init__(self):
        """Initialize the game engine."""
        self.locations: Dict[str, Location] = {}
        self.items: Dict[str, Item] = {}
        self.stationary_objects: Dict[str, StationaryObject] = {}
        self.npcs: Dict[str, AINPC] = {}
        self.player: Optional[Player] = None
        self.persistence = GameStatePersistence()
        self.game_over = False
        self.game_won = False

        # Load game data
        self._load_game_data()

    def _load_game_data(self) -> None:
        """Load locations and items from JSON files."""
        # Get the directory where this file is located
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Load locations
        locations_path = os.path.join(base_dir, 'data', 'locations.json')
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
        items_path = os.path.join(base_dir, 'data', 'items.json')
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
        
        # Load NPCs
        npcs_path = os.path.join(base_dir, 'data', 'npcs.json')
        try:
            with open(npcs_path, 'r') as f:
                npcs_data = json.load(f)
            
            for npc_id, npc_data in npcs_data.items():
                npc = AINPC(
                    npc_id=npc_id,
                    name=npc_data['name'],
                    personality=npc_data['personality'],
                    role=npc_data['role'],
                    location=npc_data['location'],
                    guards_item=npc_data.get('guards_item'),
                    puzzle_solved=False
                )
                self.npcs[npc_id] = npc
        except FileNotFoundError:
            print("No NPCs file found - running without AI NPCs")

    def new_game(self) -> None:
        """Start a new game with default state."""
        self.player = Player(current_location='entrance_hall')
        self.game_over = False
        self.game_won = False

    def load_game(self) -> bool:
        """
        Load a saved game.

        Returns:
            True if load was successful, False otherwise
        """
        game_state = self.persistence.load_game()
        if game_state is None:
            return False

        # Load player
        self.player = Player.from_dict(game_state['player'])

        # Load location states
        for loc_id, loc_data in game_state['locations'].items():
            if loc_id in self.locations:
                self.locations[loc_id].from_dict(loc_data)

        self.game_over = False
        self.game_won = False
        return True

    def save_game(self) -> bool:
        """
        Save the current game state.

        Returns:
            True if save was successful, False otherwise
        """
        if self.player is None:
            return False

        game_state = {
            'player': self.player.to_dict(),
            'locations': {
                loc_id: loc.to_dict()
                for loc_id, loc in self.locations.items()
            }
        }

        return self.persistence.save_game(game_state)

    def get_current_location(self) -> Optional[Location]:
        """Get the player's current location."""
        if self.player is None:
            return None
        return self.locations.get(self.player.current_location)

    def parse_command(self, command: str) -> tuple[str, List[str]]:
        """
        Parse a command string into verb and arguments.

        Args:
            command: The command string to parse

        Returns:
            Tuple of (verb, arguments)
        """
        parts = command.lower().strip().split()
        if not parts:
            return ('', [])
        verb = parts[0]
        args = parts[1:]
        return (verb, args)

    def execute_command(self, command: str) -> str:
        """
        Execute a command and return the result message.

        Args:
            command: The command string to execute

        Returns:
            Message describing the result
        """
        verb, args = self.parse_command(command)

        if verb == 'look' or verb == 'l':
            return self.cmd_look()
        elif verb == 'go' or verb == 'move':
            if not args:
                return "Go where? Specify a direction."
            return self.cmd_go(args[0])
        elif verb == 'take' or verb == 'get' or verb == 'grab':
            if not args:
                return "Take what?"
            return self.cmd_take(' '.join(args))
        elif verb == 'drop':
            if not args:
                return "Drop what?"
            return self.cmd_drop(' '.join(args))
        elif verb == 'inventory' or verb == 'i':
            return self.cmd_inventory()
        elif verb == 'use':
            if not args:
                return "Use what?"
            return self.cmd_use(' '.join(args))
        elif verb == 'examine' or verb == 'x':
            if not args:
                return "Examine what?"
            return self.cmd_examine(' '.join(args))
        elif verb == 'help' or verb == 'h' or verb == '?':
            return self.cmd_help()
        elif verb == 'talk' or verb == 'speak' or verb == 'say':
            if not args:
                return "Say what?"
            return self.cmd_talk(' '.join(args))
        elif verb == 'exit_mansion':
            # Special command to exit the mansion (win the game)
            location = self.get_current_location()
            if location and location.id == 'entrance_hall' and location.get_state('door_unlocked'):
                self.game_won = True
                return "You step through the doorway into the cool night air. Freedom at last!"
            else:
                return "You can't leave yet."
        elif verb == 'quit' or verb == 'exit' or verb == 'q':
            self.save_game()
            self.game_over = True
            return "Game saved. Goodbye!"
        else:
            return f"I don't understand '{verb}'. Type 'help' for a list of commands."

    def cmd_look(self) -> str:
        """Look around the current location."""
        location = self.get_current_location()
        if location is None:
            return "You are nowhere."

        # Update description based on state
        desc = location.describe()

        # Special case: If in basement and lights are off
        if location.id == 'basement' and not location.get_state('lights_on'):
            desc = f"\n{location.name}\n{'=' * len(location.name)}\n"
            desc += "It's pitch black. You can't see anything. You might want to light a candle.\n"

        # Special case: If secret passage is revealed in library
        if location.id == 'library' and location.get_state('secret_passage_revealed'):
            desc = desc.replace("Exits: south", "Exits: south, down")
        
        # Add NPCs in this location
        npcs_here = [npc for npc in self.npcs.values() if npc.location == location.id]
        if npcs_here:
            desc += "\n\n👻 Present:\n"
            for npc in npcs_here:
                desc += f"  - {npc.name}"
                if npc.guards_item and not npc.puzzle_solved:
                    desc += " (guarding something...)"
                desc += "\n"

        return desc

    def cmd_go(self, direction: str) -> str:
        """Move in a direction."""
        location = self.get_current_location()
        if location is None:
            return "You are nowhere."

        # Special handling for basement darkness
        if location.id == 'basement' and not location.get_state('lights_on'):
            return "It's too dark to see where you're going. You need light."

        # Special handling for secret passage
        if location.id == 'library' and direction == 'down':
            if location.get_state('secret_passage_revealed'):
                self.player.move_to('basement')
                self.save_game()
                return self.cmd_look()
            else:
                return "You don't see a way down from here."

        # Special handling for going up from basement
        if location.id == 'basement' and direction == 'up':
            direction = 'up'  # Ensure it's lowercase

        # Normal exit handling
        next_location_id = location.get_exit(direction)
        if next_location_id is None:
            return f"You can't go {direction} from here."

        self.player.move_to(next_location_id)
        self.save_game()
        return self.cmd_look()

    def cmd_take(self, item_name: str) -> str:
        """Take an item."""
        location = self.get_current_location()
        if location is None:
            return "You are nowhere."

        # Convert item name to item ID
        item_id = item_name.lower().replace(' ', '_')

        # Special case: rusty_key in basement can only be taken if lights are on
        if location.id == 'basement' and item_id == 'rusty_key' and not location.get_state('lights_on'):
            return "It's too dark to see anything. You fumble around but can't find what you're looking for."

        # Check if item is in location
        if not location.has_item(item_id):
            return f"There's no {item_name} here."

        # Check if item exists and can be taken
        if item_id not in self.items:
            return f"You can't take the {item_name}."

        item = self.items[item_id]
        if not item.can_take:
            return f"You can't take the {item_name}."

        # Check inventory space
        if self.player.is_inventory_full():
            return "You're carrying too much. Drop something first."

        # Take the item
        location.remove_item(item_id)
        self.player.add_item(item_id)
        self.save_game()
        return f"You take the {item.name}."

    def cmd_drop(self, item_name: str) -> str:
        """Drop an item."""
        location = self.get_current_location()
        if location is None:
            return "You are nowhere."

        # Convert item name to item ID
        item_id = item_name.lower().replace(' ', '_')

        if not self.player.has_item(item_id):
            return f"You're not carrying a {item_name}."

        if item_id not in self.items:
            return f"Unknown item: {item_name}"

        item = self.items[item_id]
        self.player.remove_item(item_id)
        location.add_item(item_id)
        self.save_game()
        return f"You drop the {item.name}."

    def cmd_inventory(self) -> str:
        """Show inventory."""
        if not self.player.inventory:
            return "You're not carrying anything."

        inv_list = []
        for item_id in self.player.inventory:
            if item_id in self.items:
                inv_list.append(f"  - {self.items[item_id].name}")

        return "You are carrying:\n" + '\n'.join(inv_list)

    def cmd_use(self, item_name: str) -> str:
        """Use an item."""
        location = self.get_current_location()
        if location is None:
            return "You are nowhere."

        # Convert item name to item ID
        item_id = item_name.lower().replace(' ', '_')

        # Special case: using candle in basement
        if item_id == 'candle' and location.id == 'basement':
            if self.player.has_item('candle'):
                location.set_state('lights_on', True)
                self.save_game()
                return "You light the candle. The warm glow illuminates the basement, revealing a rusty key on the floor!"
            else:
                return "You don't have a candle."

        # Check if player has the item
        if not self.player.has_item(item_id):
            return f"You don't have a {item_name}."

        if item_id not in self.items:
            return f"Unknown item: {item_name}"

        item = self.items[item_id]

        # Try to use item on stationary objects in the room
        for obj_id in location.stationary_objects:
            if obj_id in self.stationary_objects:
                obj = self.stationary_objects[obj_id]
                if obj.required_item == item_id:
                    # Successfully use item on object
                    result = obj.success_message

                    # Apply state change
                    if obj.state_change:
                        loc_id = obj.state_change['location']
                        state_key = obj.state_change['state_key']
                        new_value = obj.state_change['new_value']

                        if loc_id in self.locations:
                            self.locations[loc_id].set_state(state_key, new_value)
                            self.save_game()

                    # Door unlocked - player can now exit
                    if loc_id == 'entrance_hall' and state_key == 'door_unlocked':
                        result += "\n\nThe front door swings open! The path to freedom lies before you..."

                    return result

        # Check if item can be used on bookshelf without requiring another item
        if 'bookshelf' in location.stationary_objects and item_id == 'ancient_amulet':
            obj = self.stationary_objects['bookshelf']
            result = obj.success_message

            if obj.state_change:
                loc_id = obj.state_change['location']
                state_key = obj.state_change['state_key']
                new_value = obj.state_change['new_value']

                if loc_id in self.locations:
                    self.locations[loc_id].set_state(state_key, new_value)
                    self.save_game()

            return result

        return f"You can't use the {item.name} here."

    def cmd_examine(self, target: str) -> str:
        """Examine an item or object."""
        location = self.get_current_location()
        if location is None:
            return "You are nowhere."

        target_id = target.lower().replace(' ', '_')

        # Check inventory
        if self.player.has_item(target_id) and target_id in self.items:
            return self.items[target_id].description

        # Check location items
        if location.has_item(target_id) and target_id in self.items:
            return self.items[target_id].description

        # Check stationary objects
        if target_id in location.stationary_objects and target_id in self.stationary_objects:
            obj = self.stationary_objects[target_id]
            return obj.description

        return f"You don't see a {target} here."

    def cmd_help(self) -> str:
        """Show help message."""
        return """
Available Commands:
  look (l)           - Look around the current location
  go <direction>     - Move in a direction (north, south, east, west, up, down)
  take <item>        - Pick up an item
  drop <item>        - Drop an item from your inventory
  inventory (i)      - Show what you're carrying
  use <item>         - Use an item
  examine <target>   - Examine an item or object closely
  talk <message>     - Chat with NPCs (e.g., 'talk hello' or 'talk I need help')
  help (h, ?)        - Show this help message
  quit (q, exit)     - Save and quit the game

Tips:
  - Explore all locations thoroughly
  - Have conversations with NPCs - they guard important items!
  - Be kind, clever, or brave in your words
  - Earn their trust through dialogue to get what they guard
  - Pick up items you find - they may be useful
  - Try using items in different locations
  - Examine objects carefully for clues
"""
    
    def cmd_talk(self, message: str) -> str:
        """Talk to an NPC with a message."""
        location = self.get_current_location()
        if location is None:
            return "You are nowhere."

        # Find NPC in current location
        npcs_here = [npc for npc in self.npcs.values() if npc.location == location.id]

        if not npcs_here:
            return "There's no one here to talk to."

        # Use the first NPC (could be enhanced to specify which one)
        target_npc = npcs_here[0]

        # Build game state for context
        game_state = {
            'inventory': [self.items[item_id].name for item_id in self.player.inventory if item_id in self.items],
            'location': location.name
        }

        # Get AI response
        npc_response, should_give_item = target_npc.talk(message, game_state)

        result = f"\n{target_npc.name} says:\n\"{npc_response}\"\n"

        # Check if NPC decided to give the item
        if should_give_item and target_npc.guards_item:
            # Add item to location so player can pick it up
            location.add_item(target_npc.guards_item)
            result += f"\n✨ {target_npc.name} has given you the {self.items[target_npc.guards_item].name}!"
            result += f"\n(Use 'take {self.items[target_npc.guards_item].name}' to pick it up)"

            # Track state for image selection
            if target_npc.id == 'phantom_child' and target_npc.guards_item == 'candle':
                location.set_state('eliza_gave_candle', True)
            elif target_npc.id == 'ghost_librarian' and target_npc.guards_item == 'ancient_amulet':
                location.set_state('edgar_gave_amulet', True)

            self.save_game()

        return result

    def to_dict(self) -> Dict:
        """
        Convert game state to dictionary for persistence.

        Returns:
            Dictionary containing the complete game state
        """
        return {
            'player': self.player.to_dict() if self.player else None,
            'locations': {
                loc_id: loc.to_dict()
                for loc_id, loc in self.locations.items()
            },
            'npcs': {
                npc_id: {
                    'location': npc.location,
                    'puzzle_solved': npc.puzzle_solved
                }
                for npc_id, npc in self.npcs.items()
            },
            'game_over': self.game_over,
            'game_won': self.game_won,
            'current_location': self.player.current_location if self.player else None
        }

    def from_dict(self, data: Dict) -> None:
        """
        Restore game state from dictionary.

        Args:
            data: Dictionary containing the game state
        """
        # Load player
        if data.get('player'):
            self.player = Player.from_dict(data['player'])

        # Load location states
        if data.get('locations'):
            for loc_id, loc_data in data['locations'].items():
                if loc_id in self.locations:
                    self.locations[loc_id].from_dict(loc_data)

        # Load NPC states
        if data.get('npcs'):
            for npc_id, npc_data in data['npcs'].items():
                if npc_id in self.npcs:
                    self.npcs[npc_id].location = npc_data.get('location', self.npcs[npc_id].location)
                    self.npcs[npc_id].puzzle_solved = npc_data.get('puzzle_solved', False)

        # Load game state flags
        self.game_over = data.get('game_over', False)
        self.game_won = data.get('game_won', False)


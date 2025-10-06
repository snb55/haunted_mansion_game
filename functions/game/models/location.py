"""Location model for the Haunted Mansion game."""

from typing import Dict, List, Optional


class Location:
    """Represents a location in the game world."""

    def __init__(
        self,
        location_id: str,
        name: str,
        description: str,
        initial_state: Dict[str, bool],
        exits: Dict[str, str],
        initial_items: List[str],
        stationary_objects: List[str]
    ):
        """
        Initialize a location.

        Args:
            location_id: Unique identifier for the location
            name: Display name of the location
            description: Descriptive text for the location
            initial_state: Dictionary of state keys and their initial boolean values
            exits: Dictionary mapping directions to location IDs
            initial_items: List of item IDs initially in this location
            stationary_objects: List of stationary object IDs in this location
        """
        self.id = location_id
        self.name = name
        self.description = description
        self.state = initial_state.copy()
        self.exits = exits.copy()
        self.items = initial_items.copy()
        self.stationary_objects = stationary_objects.copy()

    def get_state(self, key: str) -> bool:
        """Get the value of a state key."""
        return self.state.get(key, False)

    def set_state(self, key: str, value: bool) -> None:
        """Set the value of a state key."""
        self.state[key] = value

    def add_item(self, item_id: str) -> None:
        """Add an item to this location."""
        if item_id not in self.items:
            self.items.append(item_id)

    def remove_item(self, item_id: str) -> bool:
        """Remove an item from this location. Returns True if successful."""
        if item_id in self.items:
            self.items.remove(item_id)
            return True
        return False

    def has_item(self, item_id: str) -> bool:
        """Check if an item is in this location."""
        return item_id in self.items

    def get_exit(self, direction: str) -> Optional[str]:
        """Get the location ID for a given direction. Returns None if no exit."""
        return self.exits.get(direction.lower())

    def list_exits(self) -> List[str]:
        """Get a list of available exit directions."""
        return list(self.exits.keys())

    def describe(self) -> str:
        """Get the full description of the location including items and exits."""
        desc = f"\n{self.name}\n{'=' * len(self.name)}\n{self.description}\n"

        # Add items if any
        if self.items:
            desc += "\nYou can see:\n"
            for item_id in self.items:
                desc += f"  - {item_id.replace('_', ' ').title()}\n"

        # Add stationary objects if any
        if self.stationary_objects:
            desc += "\nYou notice:\n"
            for obj_id in self.stationary_objects:
                desc += f"  - {obj_id.replace('_', ' ').title()}\n"

        # Add available exits
        if self.exits:
            exit_list = ', '.join(self.list_exits())
            desc += f"\nExits: {exit_list}\n"

        return desc

    def to_dict(self) -> Dict:
        """Convert location to dictionary for persistence."""
        return {
            'state': self.state,
            'items': self.items
        }

    def from_dict(self, data: Dict) -> None:
        """Load location state from dictionary."""
        if 'state' in data:
            self.state = data['state']
        if 'items' in data:
            self.items = data['items']

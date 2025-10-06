"""Player model for the Haunted Mansion game."""

from typing import List, Optional, Dict


class Player:
    """Represents the player character."""

    def __init__(self, current_location: str = "entrance_hall", max_inventory: int = 10):
        """
        Initialize the player.

        Args:
            current_location: The location ID where the player starts
            max_inventory: Maximum number of items the player can carry
        """
        self.current_location = current_location
        self.inventory: List[str] = []
        self.max_inventory = max_inventory

    def add_item(self, item_id: str) -> bool:
        """
        Add an item to the player's inventory.

        Args:
            item_id: The ID of the item to add

        Returns:
            True if item was added, False if inventory is full
        """
        if len(self.inventory) >= self.max_inventory:
            return False
        if item_id not in self.inventory:
            self.inventory.append(item_id)
        return True

    def remove_item(self, item_id: str) -> bool:
        """
        Remove an item from the player's inventory.

        Args:
            item_id: The ID of the item to remove

        Returns:
            True if item was removed, False if item not in inventory
        """
        if item_id in self.inventory:
            self.inventory.remove(item_id)
            return True
        return False

    def has_item(self, item_id: str) -> bool:
        """
        Check if the player has a specific item.

        Args:
            item_id: The ID of the item to check

        Returns:
            True if player has the item
        """
        return item_id in self.inventory

    def list_inventory(self) -> List[str]:
        """Get a list of all items in the player's inventory."""
        return self.inventory.copy()

    def is_inventory_full(self) -> bool:
        """Check if the player's inventory is full."""
        return len(self.inventory) >= self.max_inventory

    def inventory_count(self) -> int:
        """Get the current number of items in inventory."""
        return len(self.inventory)

    def move_to(self, location_id: str) -> None:
        """
        Move the player to a new location.

        Args:
            location_id: The ID of the location to move to
        """
        self.current_location = location_id

    def to_dict(self) -> Dict:
        """Convert player to dictionary for persistence."""
        return {
            'current_location': self.current_location,
            'inventory': self.inventory,
            'max_inventory': self.max_inventory
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Player':
        """
        Create a Player instance from a dictionary.

        Args:
            data: Dictionary containing player data

        Returns:
            Player instance
        """
        player = cls(
            current_location=data.get('current_location', 'entrance_hall'),
            max_inventory=data.get('max_inventory', 10)
        )
        player.inventory = data.get('inventory', [])
        return player

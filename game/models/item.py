"""Item models for the Haunted Mansion game."""

from typing import Dict, Optional, List


class Item:
    """Represents a mobile item that can be picked up and carried."""

    def __init__(
        self,
        item_id: str,
        name: str,
        description: str,
        can_take: bool = True,
        use_targets: Optional[List[str]] = None
    ):
        """
        Initialize a mobile item.

        Args:
            item_id: Unique identifier for the item
            name: Display name of the item
            description: Descriptive text for the item
            can_take: Whether the item can be picked up
            use_targets: List of object/location IDs this item can be used on
        """
        self.id = item_id
        self.name = name
        self.description = description
        self.can_take = can_take
        self.use_targets = use_targets or []

    def can_use_on(self, target: str) -> bool:
        """Check if this item can be used on a specific target."""
        return target in self.use_targets

    def __str__(self) -> str:
        return self.name

    def to_dict(self) -> Dict:
        """Convert item to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'can_take': self.can_take,
            'use_targets': self.use_targets
        }


class StationaryObject:
    """Represents a stationary object that can be interacted with."""

    def __init__(
        self,
        object_id: str,
        name: str,
        description: str,
        interaction_message: str,
        success_message: str,
        required_item: Optional[str] = None,
        state_change: Optional[Dict] = None
    ):
        """
        Initialize a stationary object.

        Args:
            object_id: Unique identifier for the object
            name: Display name of the object
            description: Descriptive text for the object
            interaction_message: Message shown when examining/interacting
            success_message: Message shown when successfully used
            required_item: Item ID required to interact (None if no item needed)
            state_change: Dictionary describing state change on successful interaction
                         Format: {'location': str, 'state_key': str, 'new_value': bool}
        """
        self.id = object_id
        self.name = name
        self.description = description
        self.interaction_message = interaction_message
        self.success_message = success_message
        self.required_item = required_item
        self.state_change = state_change or {}

    def can_interact(self, player_has_item: bool = False) -> bool:
        """Check if the object can be interacted with."""
        if self.required_item is None:
            return True
        return player_has_item

    def get_state_change(self) -> Optional[Dict]:
        """Get the state change information for this object."""
        return self.state_change if self.state_change else None

    def __str__(self) -> str:
        return self.name

    def to_dict(self) -> Dict:
        """Convert stationary object to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'interaction_message': self.interaction_message,
            'success_message': self.success_message,
            'required_item': self.required_item,
            'state_change': self.state_change
        }

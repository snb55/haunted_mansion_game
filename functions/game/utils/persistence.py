"""Persistence utilities for saving and loading game state."""

import json
import os
from datetime import datetime
from typing import Dict, Optional


class GameStatePersistence:
    """Handles saving and loading game state to/from JSON files."""

    def __init__(self, save_dir: str = "saves", save_file: str = "game_state.json"):
        """
        Initialize the persistence handler.

        Args:
            save_dir: Directory where save files are stored
            save_file: Name of the save file
        """
        self.save_dir = save_dir
        self.save_file = save_file
        self.save_path = os.path.join(save_dir, save_file)

        # Create save directory if it doesn't exist
        os.makedirs(save_dir, exist_ok=True)

    def save_game(self, game_state: Dict) -> bool:
        """
        Save the current game state to a JSON file.

        Args:
            game_state: Dictionary containing the complete game state

        Returns:
            True if save was successful, False otherwise
        """
        try:
            # Add metadata
            save_data = {
                'version': '1.0',
                'timestamp': datetime.now().isoformat(),
                'game_state': game_state
            }

            with open(self.save_path, 'w') as f:
                json.dump(save_data, f, indent=2)

            return True
        except Exception as e:
            print(f"Error saving game: {e}")
            return False

    def load_game(self) -> Optional[Dict]:
        """
        Load game state from a JSON file.

        Returns:
            Dictionary containing game state, or None if no save file exists
        """
        if not os.path.exists(self.save_path):
            return None

        try:
            with open(self.save_path, 'r') as f:
                save_data = json.load(f)

            # Validate the save file has required structure
            if 'game_state' not in save_data:
                print("Invalid save file format")
                return None

            return save_data['game_state']
        except json.JSONDecodeError as e:
            print(f"Error parsing save file: {e}")
            return None
        except Exception as e:
            print(f"Error loading game: {e}")
            return None

    def save_exists(self) -> bool:
        """Check if a save file exists."""
        return os.path.exists(self.save_path)

    def delete_save(self) -> bool:
        """
        Delete the current save file.

        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            if os.path.exists(self.save_path):
                os.remove(self.save_path)
                return True
            return False
        except Exception as e:
            print(f"Error deleting save file: {e}")
            return False

    def get_save_info(self) -> Optional[Dict]:
        """
        Get metadata about the save file without loading the full game state.

        Returns:
            Dictionary with version and timestamp, or None if no save exists
        """
        if not os.path.exists(self.save_path):
            return None

        try:
            with open(self.save_path, 'r') as f:
                save_data = json.load(f)

            return {
                'version': save_data.get('version', 'unknown'),
                'timestamp': save_data.get('timestamp', 'unknown')
            }
        except Exception as e:
            print(f"Error reading save info: {e}")
            return None

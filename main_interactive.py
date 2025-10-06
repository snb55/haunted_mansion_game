#!/usr/bin/env python3
"""
Haunted Mansion Game - Interactive CLI Version
A text-based adventure game with arrow-key navigation and menu-based controls.
"""

import inquirer
from inquirer.themes import GreenPassion
from game.game_engine import GameEngine
from game import ascii_art
import os


def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_banner():
    """Print the game banner."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║           Welcome to the HAUNTED MANSION                     ║
║                                                              ║
║  You stand before a decrepit mansion on a foggy hillside.   ║
║  The windows are dark, and strange sounds echo from within.  ║
║  You push open the creaking door and step inside...          ║
║                                                              ║
║  Your goal: ESCAPE the mansion before it's too late!        ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")


def get_available_actions(engine: GameEngine) -> list:
    """Get all available actions based on current game state."""
    actions = []
    location = engine.get_current_location()

    if location is None:
        return ["Quit Game"]

    # Always available
    actions.append("👁️  Look Around")
    actions.append("🎒 Check Inventory")

    # Items to take
    if location.items:
        for item_id in location.items:
            if item_id in engine.items:
                item = engine.items[item_id]
                actions.append(f"📦 Take {item.name}")

    # Items to use (from inventory)
    if engine.player.inventory:
        for item_id in engine.player.inventory:
            if item_id in engine.items:
                item = engine.items[item_id]
                actions.append(f"🔧 Use {item.name}")

    # Items to drop
    if engine.player.inventory:
        for item_id in engine.player.inventory:
            if item_id in engine.items:
                item = engine.items[item_id]
                actions.append(f"⬇️  Drop {item.name}")

    # Stationary objects to examine
    if location.stationary_objects:
        for obj_id in location.stationary_objects:
            if obj_id in engine.stationary_objects:
                obj = engine.stationary_objects[obj_id]
                actions.append(f"🔍 Examine {obj.name}")

    # Movement options
    if location.exits:
        for direction in location.list_exits():
            actions.append(f"🚶 Go {direction.upper()}")

    # Special: secret passage
    if location.id == 'library' and location.get_state('secret_passage_revealed'):
        actions.append("🚶 Go DOWN")

    # Always available
    actions.append("❓ Help")
    actions.append("💾 Save & Quit")

    return actions


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


def execute_action(engine: GameEngine, action: str) -> str:
    """Execute the selected action and return result message."""
    if action.startswith("👁️"):
        return engine.cmd_look()
    elif action.startswith("🎒"):
        return engine.cmd_inventory()
    elif action.startswith("📦 Take"):
        item_name = action.replace("📦 Take ", "").strip()
        result = engine.cmd_take(item_name)
        # Show item art
        item_id = item_name.lower().replace(' ', '_')
        if item_id == 'candle':
            return result + "\n" + ascii_art.CANDLE
        elif item_id == 'rusty_key':
            return result + "\n" + ascii_art.RUSTY_KEY
        elif item_id == 'ancient_amulet':
            return result + "\n" + ascii_art.ANCIENT_AMULET
        return result
    elif action.startswith("🔧 Use"):
        item_name = action.replace("🔧 Use ", "").strip()
        return engine.cmd_use(item_name)
    elif action.startswith("⬇️  Drop"):
        item_name = action.replace("⬇️  Drop ", "").strip()
        return engine.cmd_drop(item_name)
    elif action.startswith("🔍 Examine"):
        target = action.replace("🔍 Examine ", "").strip()
        result = engine.cmd_examine(target)
        # Show art for examined objects
        target_id = target.lower().replace(' ', '_')
        if target_id == 'locked_door':
            location = engine.get_current_location()
            if location and location.get_state('door_unlocked'):
                return result + "\n" + ascii_art.DOOR_UNLOCKED
            return result + "\n" + ascii_art.LOCKED_DOOR_ART
        return result
    elif action.startswith("🚶 Go"):
        direction = action.replace("🚶 Go ", "").strip().lower()
        return engine.cmd_go(direction)
    elif action.startswith("❓"):
        return engine.cmd_help()
    elif action.startswith("💾"):
        engine.save_game()
        return "Game saved. Goodbye!"
    else:
        return "Unknown action."


def main():
    """Main interactive game loop."""
    engine = GameEngine()

    # Check for existing save
    if engine.persistence.save_exists():
        clear_screen()
        print_banner()
        print("\n🕯️  A saved game has been found.\n")

        questions = [
            inquirer.List('continue',
                         message="Would you like to continue your previous game?",
                         choices=['Yes, continue', 'No, start new game'],
                         ),
        ]

        answers = inquirer.prompt(questions, theme=GreenPassion())

        if answers and answers['continue'] == 'Yes, continue':
            if engine.load_game():
                print("\n✓ Game loaded successfully!\n")
            else:
                print("\n✗ Failed to load game. Starting a new game instead.\n")
                engine.new_game()
        else:
            print("\nStarting a new game...\n")
            engine.new_game()
    else:
        clear_screen()
        print_banner()
        engine.new_game()

    # Main game loop
    while not engine.game_over:
        try:
            # Get available actions
            actions = get_available_actions(engine)

            # Show current location first
            clear_screen()

            # Show ASCII art for location
            art = get_ascii_art_for_location(engine)
            if art:
                print(art)

            print("═" * 64)
            result = engine.cmd_look()
            print(result)
            print("═" * 64)

            # Show menu
            questions = [
                inquirer.List('action',
                             message="What do you want to do?",
                             choices=actions,
                             carousel=True,
                             ),
            ]

            answers = inquirer.prompt(questions, theme=GreenPassion())

            if not answers:
                # User pressed Ctrl+C or similar
                print("\n\nGame interrupted. Saving...")
                engine.save_game()
                print("Game saved. Goodbye!")
                break

            # Execute action
            action = answers['action']

            if action == "💾 Save & Quit":
                engine.save_game()
                clear_screen()
                print("\n✓ Game saved successfully!")
                print("\nThank you for playing Haunted Mansion!\n")
                break

            result = execute_action(engine, action)

            # Show result
            clear_screen()
            print("═" * 64)
            print(result)
            print("═" * 64)

            # Check for win condition
            if engine.game_won:
                clear_screen()
                print(ascii_art.WIN_BANNER)
                print("\nThanks for playing!\n")
                engine.save_game()

                # Ask to play again
                questions = [
                    inquirer.List('again',
                                 message="Play again?",
                                 choices=['Yes', 'No'],
                                 ),
                ]
                answers = inquirer.prompt(questions, theme=GreenPassion())

                if answers and answers['again'] == 'Yes':
                    engine.new_game()
                    engine.game_won = False
                else:
                    break
            else:
                # Wait for user to press enter
                input("\nPress ENTER to continue...")

        except KeyboardInterrupt:
            print("\n\nGame interrupted. Saving...")
            engine.save_game()
            print("Game saved. Goodbye!")
            break
        except Exception as e:
            print(f"\nAn error occurred: {e}")
            print("Press ENTER to continue...")
            input()

    clear_screen()
    print("\n" + "═" * 64)
    print("     Thank you for playing Haunted Mansion!")
    print("═" * 64 + "\n")


if __name__ == "__main__":
    main()

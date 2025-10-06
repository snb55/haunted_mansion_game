#!/usr/bin/env python3
"""
Haunted Mansion Game
A text-based adventure game with persistent state.
"""

from game.game_engine import GameEngine


def print_welcome() -> None:
    """Print the welcome message."""
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
║  Type 'help' for a list of commands.                         ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")


def print_divider() -> None:
    """Print a visual divider."""
    print("\n" + "─" * 64 + "\n")


def main():
    """Main game loop."""
    engine = GameEngine()

    # Check for existing save
    if engine.persistence.save_exists():
        print("\n🕯️  A saved game has been found.")
        choice = input("Would you like to continue your previous game? (y/n): ").lower().strip()
        print_divider()

        if choice in ['y', 'yes']:
            if engine.load_game():
                print("✓ Game loaded successfully!\n")
            else:
                print("✗ Failed to load game. Starting a new game instead.\n")
                engine.new_game()
        else:
            print("Starting a new game...\n")
            engine.new_game()
    else:
        print_welcome()
        engine.new_game()

    # Show initial location
    print(engine.cmd_look())

    # Main game loop
    while not engine.game_over:
        print_divider()

        try:
            command = input("→ ").strip()

            if not command:
                continue

            print()  # Blank line for readability
            result = engine.execute_command(command)
            print(result)

            # Check for game won condition
            if engine.game_won:
                print_divider()
                print("Congratulations! You've successfully escaped the haunted mansion!")
                print("Thanks for playing!\n")
                engine.save_game()
                break

        except KeyboardInterrupt:
            print("\n\nGame interrupted. Saving...")
            engine.save_game()
            print("Game saved. Goodbye!")
            break
        except Exception as e:
            print(f"\nAn error occurred: {e}")
            print("The game will try to continue...\n")

    print("\nThank you for playing Haunted Mansion!\n")


if __name__ == "__main__":
    main()

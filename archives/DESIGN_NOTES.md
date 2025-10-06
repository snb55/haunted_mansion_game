# Haunted Mansion Game - Design Notes & Architecture

## Architecture Overview

### Design Philosophy
- **Separation of Concerns:** Game logic, state management, and persistence are separate modules
- **Object-Oriented Design:** Locations, Items, and Player are distinct classes
- **Single Responsibility:** Each class handles one aspect of the game
- **Data-Driven:** Location and item definitions stored in JSON for easy modification

## Core Components

### 1. Game State Manager
**Responsibility:** Central controller for game state and persistence

```
GameState
├── current_location: str
├── locations: Dict[str, Location]
├── player: Player
└── methods:
    ├── save_game()
    ├── load_game()
    └── get_current_location()
```

### 2. Location Class
**Responsibility:** Represents a game location with state and connections

```
Location
├── id: str
├── name: str
├── description: str
├── state: Dict[str, bool]
├── items: List[Item]
├── exits: Dict[str, str]  # direction -> location_id
├── stationary_objects: List[StationaryObject]
└── methods:
    ├── describe()
    ├── get_state(key)
    ├── set_state(key, value)
    └── list_exits()
```

### 3. Item Classes

#### Mobile Item (Inventory)
```
Item
├── id: str
├── name: str
├── description: str
├── can_take: bool
└── methods:
    └── use(context)
```

#### Stationary Object
```
StationaryObject
├── id: str
├── name: str
├── description: str
├── interaction_result: str
└── methods:
    └── interact(player, location)
```

### 4. Player Class
**Responsibility:** Track player state and inventory

```
Player
├── inventory: List[Item]
├── max_inventory: int
└── methods:
    ├── add_item(item)
    ├── remove_item(item)
    ├── has_item(item_id)
    └── list_inventory()
```

## State Management

### Location States (Binary)
```json
{
  "entrance_hall": {
    "door_unlocked": false
  },
  "library": {
    "secret_passage_revealed": false
  },
  "basement": {
    "lights_on": false
  }
}
```

### State Transitions
1. **Entrance Hall Door:**
   - Trigger: Use "rusty_key" on "locked_door"
   - Effect: `door_unlocked: false → true`
   - Gameplay Impact: Can exit mansion (win condition)

2. **Library Secret Passage:**
   - Trigger: Pull "bookshelf_lever" OR use "ancient_amulet"
   - Effect: `secret_passage_revealed: false → true`
   - Gameplay Impact: Reveals exit to basement

3. **Basement Lights:**
   - Trigger: Use "candle" in basement
   - Effect: `lights_on: false → true`
   - Gameplay Impact: Can see and interact with objects

## Persistence Strategy

### File Format: JSON
**Rationale:**
- Human-readable for debugging
- Native Python support (json module)
- Easy to validate and modify
- Sufficient for single-player game

### Save File Structure
```json
{
  "version": "1.0",
  "timestamp": "2025-10-03T10:30:00",
  "player": {
    "current_location": "entrance_hall",
    "inventory": ["rusty_key"]
  },
  "locations": {
    "entrance_hall": {
      "state": {"door_unlocked": false},
      "items": []
    },
    "library": {
      "state": {"secret_passage_revealed": false},
      "items": ["ancient_amulet", "candle"]
    },
    "basement": {
      "state": {"lights_on": false},
      "items": []
    }
  }
}
```

### Save/Load Strategy
- **Auto-save:** After every state-changing action
- **Save location:** `./saves/game_state.json`
- **Load priority:** Check for existing save → Load defaults if missing
- **Validation:** Check JSON structure and required fields

## Game Flow

### Initialization
```
1. Check for existing save file
2. If exists → Load game state
3. If not → Initialize new game with defaults
4. Display welcome message and current location
```

### Main Game Loop
```
while not game_over:
    1. Display current location description
    2. Get player command
    3. Parse and validate command
    4. Execute command
    5. Update game state
    6. Auto-save
    7. Check win/lose conditions
```

### Win Condition (MVP)
- Player unlocks front door using rusty key
- Successfully exits the mansion

## Command Processing

### Command Parser
```python
def parse_command(input_str):
    parts = input_str.lower().split()
    verb = parts[0]
    args = parts[1:] if len(parts) > 1 else []
    return (verb, args)
```

### Command Handlers
- **look:** Display current location
- **go [direction]:** Move to connected location
- **take [item]:** Add item to inventory
- **drop [item]:** Remove item from inventory
- **use [item] [on target]:** Use item in context
- **inventory/i:** Show inventory
- **examine [object]:** Detailed description
- **quit:** Save and exit

## Data Files

### locations.json
```json
{
  "entrance_hall": {
    "name": "Entrance Hall",
    "description": "A grand entrance hall...",
    "initial_state": {"door_unlocked": false},
    "exits": {"north": "library"},
    "stationary_objects": ["locked_door"]
  }
}
```

### items.json
```json
{
  "rusty_key": {
    "name": "Rusty Key",
    "description": "An old, rusty key...",
    "can_take": true
  }
}
```

## Error Handling

### Invalid Commands
- Unknown verbs → "I don't understand that command"
- Missing arguments → "What do you want to [verb]?"
- Invalid targets → "You don't see that here"

### Edge Cases
- Taking item not in room → "That's not here"
- Full inventory → "You're carrying too much"
- Using wrong item → "That doesn't work"
- Locked exits → "You can't go that way"

## Testing Strategy

### Manual Test Cases
1. **New Game:** Start fresh, verify initial state
2. **Navigation:** Move between all locations
3. **Inventory:** Pick up, drop, use items
4. **State Changes:** Trigger all state transitions
5. **Persistence:** Save, quit, reload, verify state
6. **Win Condition:** Complete game objective

### Test Checklist
- [ ] All locations accessible
- [ ] All items can be picked up
- [ ] All stationary objects respond to interaction
- [ ] State persists across sessions
- [ ] Invalid commands handled gracefully
- [ ] Win condition triggers correctly

## Future Enhancements (Post-MVP)

### Potential Features
- **Enhanced UI:** ASCII art for locations
- **More locations:** Attic, dining room, cellar
- **Puzzles:** Multi-step challenges
- **NPCs:** Ghosts with dialogue
- **Time system:** Countdown to midnight
- **Multiple endings:** Different escape routes
- **Sound effects:** Atmospheric audio (text descriptions)

### Architecture Extensions
- **Event system:** Decouple state changes from actions
- **Plugin architecture:** Easy addition of new items/locations
- **Dialogue trees:** NPC conversation system
- **Achievement system:** Track player progress

# Haunted Mansion Game - Requirements Document

## Project Overview
A persistent, interactive adventure game set in a haunted mansion where players navigate through locations, interact with objects, and manage inventory to achieve objectives.

## Core Requirements (MVP)

### 1. Locations and State Management
**Requirement:** Minimum 3 distinct mansion locations with binary states

#### Proposed Locations:
- **Entrance Hall**
  - State: `door_unlocked` (boolean)
  - Initial: false
  - Description: Grand entrance with locked front door, dusty chandelier, cobwebs

- **Library**
  - State: `secret_passage_revealed` (boolean)
  - Initial: false
  - Description: Floor-to-ceiling bookshelves, ancient tomes, hidden passage behind bookshelf

- **Basement**
  - State: `lights_on` (boolean)
  - Initial: false
  - Description: Dark, damp underground chamber with mysterious shadows

#### Acceptance Criteria:
- [ ] Each location has at least one binary state property
- [ ] State can be altered through gameplay interactions
- [ ] State changes affect navigation or gameplay options

### 2. Objects and Interaction

#### Mobile Objects (Inventory - Minimum 3):
- **Rusty Key** - Opens the front door (Entrance Hall)
- **Candle** - Lights the basement
- **Ancient Amulet** - Reveals secret passage in Library

#### Stationary/Interactive Objects (Minimum 2):
- **Locked Door** (Entrance Hall) - Requires rusty key to unlock
- **Bookshelf Lever** (Library) - Reveals secret passage when pulled

#### Acceptance Criteria:
- [ ] Player can pick up, carry, and drop mobile objects
- [ ] Inventory system tracks player possessions
- [ ] Stationary objects respond to interactions
- [ ] Object interactions change location states
- [ ] Objects can be used across different locations

### 3. Game State Persistence

#### Data to Persist:
- Player's current location
- Player's inventory contents
- All location states (door_unlocked, secret_passage_revealed, lights_on)
- All stationary object states

#### Proposed Implementation:
- **Format:** JSON file storage
- **File:** `game_state.json`
- **Operations:** Save on state change, Load on game start

#### Acceptance Criteria:
- [ ] Game state saves automatically after each action
- [ ] Player can quit and resume without losing progress
- [ ] All critical data persists correctly
- [ ] Handle missing save file (new game scenario)

## Technical Requirements

### Technology Stack (Proposed)
- **Language:** Python 3.8+
- **Persistence:** JSON file storage
- **Interface:** Text-based CLI (MVP)

### Code Organization
```
/game
  /models
    - location.py
    - item.py
    - player.py
    - game_state.py
  /data
    - locations.json
    - items.json
  /utils
    - persistence.py
  - game_engine.py
  - main.py
```

### Quality Standards
- Clean, readable code with comments
- Logical class structure (OOP principles)
- Error handling for invalid inputs
- Clear separation of concerns

## User Interface (MVP)

### Command Structure:
- `look` - Describe current location
- `go [direction]` - Move to another location
- `take [item]` - Pick up an item
- `drop [item]` - Drop an item from inventory
- `use [item]` - Use/interact with an item
- `inventory` - Show current inventory
- `save` - Manually save game
- `quit` - Exit game

### Display Elements:
- Location name and description
- Available exits
- Visible objects
- Current inventory
- Interaction feedback messages

## Success Criteria (Definition of Done)

### Functional Requirements:
- [ ] 3+ locations implemented with binary states
- [ ] 3+ mobile objects in inventory system
- [ ] 2+ stationary interactive objects
- [ ] State persistence working correctly
- [ ] Player can complete basic gameplay loop

### Documentation Requirements:
- [ ] README.md with setup instructions
- [ ] Explanation of state architecture
- [ ] Description of persistence mechanism
- [ ] How to play the game

### Testing Requirements:
- [ ] All core features manually tested
- [ ] Edge cases handled (invalid commands, missing save file)
- [ ] Persistence verified across sessions

## Out of Scope (Post-MVP)

The following are NOT required for MVP but noted for future consideration:
- Multiplayer/concurrency
- LLM-generated NPC dialogue
- Visual/web UI
- Complex narrative branching
- Combat system
- Multiple save slots
- Achievements/scoring

## Timeline Estimate

- **Day 1-2:** Core architecture and models
- **Day 3-4:** Persistence and game engine
- **Day 5:** Polish, testing, documentation
- **Day 6-7:** Buffer for issues and refinement

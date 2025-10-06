# 👥 Multiplayer Design - Room Ownership System

## Architecture

### Anonymous Auth
Every player gets a unique Firebase UID automatically:
- No signup required
- UID persists across browser sessions
- Each UID has their own save games

### Room System

#### Room Creation
```javascript
Player A clicks "Create Multiplayer Game"
  ↓
1. Generate 6-char room code (e.g., "ABC123")
2. Create Firestore document:
   gameSessions/ABC123 {
     ownerId: "player-A-uid",     ← Owner!
     roomCode: "ABC123",
     players: {
       "player-A-uid": "PlayerName"
     },
     gameState: {...},
     locations: {...},
     npcs: {...},
     isActive: true
   }
3. Show: "Room ABC123 created! Share code with friends"
```

#### Room Joining
```javascript
Player B enters code "ABC123"
  ↓
1. Find gameSessions/ABC123
2. Add player to room:
   players: {
     "player-A-uid": "Player A",
     "player-B-uid": "Player B"  ← Joined!
   }
3. Both players now see same game state
4. Real-time updates via Firestore listeners
```

#### Gameplay (Synchronized)
```javascript
Player B types: "talk hello"
  ↓
1. Update gameSessions/ABC123/npcs/conversation
2. Firestore triggers update
3. Player A sees: "Player B talked to Little Eliza"
4. Both see NPC response in real-time
```

#### Room Exit Logic

**Scenario 1: Guest Leaves (Player B)**
```javascript
Player B clicks "Leave Room"
  ↓
1. Remove from players list
2. Owner (Player A) still has the room
3. Player B can rejoin with code
```

**Scenario 2: Owner Leaves (Player A)**
```javascript
Player A clicks "Leave Room"
  ↓
If Player B still in room:
  - Transfer ownership to Player B
  - Or: Mark room as "orphaned"
  
If room is empty:
  - Save game state to Player A's saves/{uid}
  - Delete room from gameSessions
```

**Scenario 3: Last Player Leaves**
```javascript
Only Player A in room, clicks "Leave"
  ↓
1. Check: ownerId === player-A-uid? YES
2. Save to saves/player-A-uid:
   {
     gameState: {...},
     locations: {...},
     npcs: {...},
     savedAt: timestamp
   }
3. Delete gameSessions/ABC123
4. Player A can load this save later!
```

#### Save Game Ownership

**Owner's Save**
```javascript
Room creator (ownerId) gets the save when:
- They leave and room is empty
- All players leave
- Room expires (inactive for X hours)

Why? They created it, they own the progress!
```

**Guest's Experience**
```javascript
Guests (non-owners) don't get saves from rooms:
- They're "visiting" someone else's game
- They can create their own rooms
- Or load their own single-player saves
```

## Firestore Listeners (Real-time)

```javascript
// Frontend listens for changes
db.collection('gameSessions')
  .doc(roomCode)
  .onSnapshot((doc) => {
    const data = doc.data();
    
    // Update game state
    updateLocations(data.locations);
    updateNPCs(data.npcs);
    updatePlayers(data.players);
    
    // Show other players' actions
    if (data.lastAction) {
      showNotification(data.lastAction);
    }
  });
```

## Security Rules Enforcement

```javascript
// Only owner can delete room
allow delete: if resource.data.ownerId == request.auth.uid;

// Owner and players can update
allow update: if request.auth.uid in resource.data.players.keys();

// Anyone can read to join
allow read: if request.auth != null;
```

## UI Flow

### Single Player
```
[Start Menu]
  ↓
"New Game" → Create solo save (saves/{uid})
"Load Game" → Load from saves/{uid}
```

### Multiplayer
```
[Start Menu]
  ↓
"Create Multiplayer" → Generate room code
  ↓
[In Room ABC123]
Player A: "Share code: ABC123"
  ↓
Player B: "Join Game" → Enter "ABC123"
  ↓
[Both Playing]
- See each other in location
- Share NPC conversations
- Synchronized game state
  ↓
[Leave]
Player B leaves → No save for them
Player A leaves last → Save to their account
```

## Example Game Session

```
1. Player A creates room "GHOST1"
   - ownerId: "uid-aaa"
   
2. Player B joins "GHOST1"
   - players: {uid-aaa: "Alice", uid-bbb: "Bob"}
   
3. They play together:
   - Alice talks to Eliza
   - Bob finds the key
   - Both solve puzzles
   
4. Bob leaves:
   - players: {uid-aaa: "Alice"}
   - Bob has no save
   
5. Alice leaves (last one):
   - Save gameState to saves/uid-aaa
   - Delete room "GHOST1"
   - Alice can continue later from her save
```

## Data Structure

```javascript
// Firestore
saves/
  uid-aaa/
    gameState: {...}
    savedAt: "2025-10-04..."
    
  uid-bbb/
    gameState: {...}
    savedAt: "2025-10-03..."

gameSessions/
  GHOST1/
    ownerId: "uid-aaa"
    roomCode: "GHOST1"
    players: {
      "uid-aaa": "Alice",
      "uid-bbb": "Bob"
    }
    gameState: {...}
    locations: {...}
    npcs: {...}
    createdAt: timestamp
    lastActivity: timestamp
    isActive: true
```

---

**Simple Rule: Creator owns the room and gets the save!**


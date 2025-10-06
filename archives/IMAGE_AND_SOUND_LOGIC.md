# 🎨🔊 IMAGE & SOUND LOADING LOGIC - Haunted Mansion

## Overview
This document defines EXACTLY when each image and sound should play based on game state and actions.
**Review and edit this before implementation!**

---

## 📁 Asset Inventory

### Images (12 files)
**Entrance Hall:**
- `entracnce_hall_default.png` (typo in filename - will use as-is)
- `entrance_hall_eliza_speaking.png`
- `entrance_hall_eliza_gave_candle.png`
- `entrance_hall_door_unlocked.png`
- `entrance_hall_lock.png`
- `outside_of_mansion.png`

**Library:**
- `library_default.png`
- `library_edgar_speaking.png`
- `library_edgar_gave_amulet.png`
- `library_secret_revealed.png`

**Basement:**
- `basement_pitch_dark.png`
- `basement_lit_key_visible.png`

**Videos:**
- `walking_out.mp4`

### Sounds (13 files)
**Ambient (Room Entry - Play Once):**
- `main_entrance_creepy.mp3`
- `library_ghost_noise.mp3`
- `basement_creepy.mp3`

**Menu/UI:**
- `main_menu_ghost_piano.mp3`
- `click.mp3` ← **PLAYS ON EVERY CLICK**
- `useless_selection.mp3`

**Movement:**
- `walking_between_rooms.mp3`

**Items:**
- `pick_up_item.mp3`
- `drop_item.mp3`

**Doors:**
- `locked_door.mp3`
- `unlock_and_open_door.mp3`

**Special:**
- `bookshelf_opens.mp3`

---

## 🎵 GLOBAL SOUND RULE

### **EVERY CLICK = CLICK SOUND**
```
ANY button clicked → play click.mp3 FIRST
Then play additional action-specific sound if applicable
```

Examples:
- Click action button → `click.mp3`
- Click "Chat with Eliza" → `click.mp3` 
- Click "Take key" → `click.mp3` + `pick_up_item.mp3`
- Click "Use door" → `click.mp3` + `locked_door.mp3` (if locked)
- Click "Inspect Door" → `click.mp3` + `locked_door.mp3` (if locked)

---

## 🚪 ENTRANCE HALL

### Image Selection Logic (Priority Order):

```
1. IF door_unlocked == True AND player_outside == True
   → IMAGE: outside_of_mansion.png
   REASON: Player has escaped, viewing mansion from outside
   NOTE THIS SHOULD ONLY BE SHOWN AFTER THE FINAL VIDEO IS played 
   Sequence is that once they key is used door is unlocked, video 
   is played and game is over then the outside image fades in and
   the piano music plays again.

2. ELSE IF door_unlocked == True
   → IMAGE: entrance_hall_door_unlocked.png
   REASON: Door is open, light streaming in

3. ELSE IF eliza_present AND eliza_has_candle == False
   → IMAGE: entrance_hall_eliza_gave_candle.png
   REASON: Eliza gave away the candle, she's satisfied


4. ELSE IF player_talking_to_eliza == True AND eliza_has_candle == TRUE
   → IMAGE: entrance_hall_eliza_speaking.png
   REASON: Active conversation with Eliza

5. ELSE IF player_talking_to_eliza == True AND eliza_has_candle == FALSO
   → IMAGE: entrance_hall_eliza_gave_candle.png
   REASON: Eliza gave away the candle, she's satisfied

6. ELSE (default)
   → IMAGE: entracnce_hall_default.png
   REASON: Initial state - Eliza with candle, door locked
```

### Sound Triggers:

| **Action** | **Sound File** | **When to Play** |
|------------|----------------|------------------|
| Enter room (first time only) | `main_entrance_creepy.mp3` | Player enters 'entrance_hall' for the first time in the game session |
| ANY button click | `click.mp3` | Every single button click |
| Chat with Little Eliza | `click.mp3` | Player initiates conversation |
| Eliza gives candle | `pick_up_item.mp3` | After successful conversation, candle added to inventory |
| Try to use door (locked) | `locked_door.mp3` | Player tries locked door without key (AFTER click sound) |
| Use key on door | `unlock_and_open_door.mp3` | Player successfully unlocks door (AFTER click sound) |
| Walk to library | `walking_between_rooms.mp3` | Player moves north to library |

---

## 📚 LIBRARY

### Image Selection Logic (Priority Order):

```
1. IF secret_passage_revealed == True
   → IMAGE: library_secret_revealed.png
   REASON: Bookshelf moved, basement entrance visible

2. ELSE IF edgar_present AND edgar_has_amulet == False
   → IMAGE: library_edgar_gave_amulet.png
   REASON: Edgar gave away the amulet

3. ELSE IF player_talking_to_edgar == True AND edgar_has_amulet == TRUE
   → IMAGE: library_edgar_speaking.png
   REASON: Active conversation with Edgar

4. ELSE IF player_talking_to_edgar == True AND edgar_has_amulet == FALSE
   → IMAGE: library_edgar_gave_amulet.png
   REASON: Edgar gave away the amulet

5. ELSE (default)
   → IMAGE: library_default.png
   REASON: Initial state - Edgar with amulet, normal bookshelf
```

### Sound Triggers:

| **Action** | **Sound File** | **When to Play** |
|------------|----------------|------------------|
| Enter room (first time only) | `library_ghost_noise.mp3` | Player enters 'library' for the first time in the game session |
| ANY button click | `click.mp3` | Every single button click |
| Chat with Edgar Blackwood | `click.mp3` | Player initiates conversation |
| Edgar gives amulet | `pick_up_item.mp3` | After successful conversation, amulet added to inventory |
| Use amulet on bookshelf | `bookshelf_opens.mp3` | Player activates secret passage (AFTER click sound) |
| Walk to entrance hall | `walking_between_rooms.mp3` | Player moves south |
| Walk to basement | `walking_between_rooms.mp3` | Player moves down (after secret revealed) |

---

## 🕯️ BASEMENT

### Image Selection Logic (Priority Order):

```
1. IF lights_on == False
   → IMAGE: basement_pitch_dark.png
   REASON: No candle used yet, complete darkness

2. ELSE IF lights_on == True
   → IMAGE: basement_lit_key_visible.png
   REASON: Candle lit, rusty key visible on floor (or taken)


3. ELSE IF lights_on == True AND key is taken
   → IMAGE: basement_lit_key_taken.png
   REASON: Candle lit, rusty key taken from floor
   
3. ELSE (fallback)
   → IMAGE: basement_pitch_dark.png
```

### Sound Triggers:

| **Action** | **Sound File** | **When to Play** |
|------------|----------------|------------------|
| Enter room (first time only) | `basement_creepy.mp3` | Player enters 'basement' for the first time in the game session |
| ANY button click | `click.mp3` | Every single button click |
| Use candle in basement | `click.mp3` only | Player lights the basement with candle |
| Take rusty key | `pick_up_item.mp3` | Player picks up the key (AFTER click sound) |
| Try to take key in darkness | `useless_selection.mp3` | Player tries to take key without light (AFTER click sound) | note this action should not even appear as one of the options
| Walk to library | `walking_between_rooms.mp3` | Player moves up |

---

## 🎮 GLOBAL UI SOUNDS

### Menu & Interaction Sounds:

| **Action** | **Sound File** | **When to Play** |
|------------|----------------|------------------|
| Game start (welcome screen) | `main_menu_ghost_piano.mp3` | When player first loads the game |
| **ANY button click** | `click.mp3` | **EVERY SINGLE BUTTON PRESS** |
| Invalid action | `useless_selection.mp3` | Player tries impossible action (AFTER click) |
| Drop item | `drop_item.mp3` | Player drops item from inventory (AFTER click) |

### Victory Sequence:

| **Action** | **Sound File** | **When to Play** |
|------------|----------------|------------------|
| Door unlocks | `unlock_and_open_door.mp3` | Key successfully used on door |
| Walk out door | `walking_out.mp3` | Player exits mansion |
| Victory video plays | (video has audio) | `walking_out.mp4` plays | then switches to mansion from the outside photo 
and main menu music plays

---

## 🔊 SOUND IMPLEMENTATION LOGIC

### Priority: Click Sound ALWAYS First
```javascript
function handleButtonClick(action) {
    // ALWAYS play click sound first
    playSound('sounds/click.mp3');
    
    // Then execute action and play additional sounds
    executeAction(action);
}
```

### Room Ambient Sounds (Play Once Per Session):
```javascript
// Track which rooms have been entered this session
const roomsVisited = new Set();

function onEnterRoom(roomName) {
    if (!roomsVisited.has(roomName)) {
        playSound(getRoomAmbientSound(roomName));
        roomsVisited.add(roomName);
    }
}

function getRoomAmbientSound(room) {
    const ambientSounds = {
        'entrance_hall': 'sounds/main_entrance_creepy.mp3',
        'library': 'sounds/library_ghost_noise.mp3',
        'basement': 'sounds/basement_creepy.mp3'
    };
    return ambientSounds[room];
}
```

### Action-Based Sounds (Every Time):
```javascript
function playActionSound(action, context) {
    const soundMap = {
        'pick_up_item': 'sounds/pick_up_item.mp3',
        'drop_item': 'sounds/drop_item.mp3',
        'locked_door': 'sounds/locked_door.mp3',
        'unlock_and_open': 'sounds/unlock_and_open_door.mp3',
        'bookshelf_opens': 'sounds/bookshelf_opens.mp3',
        'walking': 'sounds/walking_between_rooms.mp3',
        'walking_out': 'sounds/walking_out.mp3',
        'invalid': 'sounds/useless_selection.mp3'
    };
    
    // Click sound already played, now play action-specific sound
    if (soundMap[action]) {
        setTimeout(() => playSound(soundMap[action]), 100); // Slight delay after click
    }
}
```

---

## 📊 COMPLETE GAMEPLAY SEQUENCES

### Starting the Game:
```
ACTION: Player loads game
├─ SOUND: main_menu_ghost_piano.mp3
└─ IMAGE: (welcome screen)

ACTION: Player clicks "New Game"
├─ SOUND: click.mp3
├─ SOUND: main_entrance_creepy.mp3 (room ambient - first time)
└─ IMAGE: entracnce_hall_default.png
```

### Entrance Hall Sequence:
```
ACTION: Click "Chat with Little Eliza"
├─ SOUND: click.mp3
└─ IMAGE: entrance_hall_eliza_speaking.png

ACTION: Type message to Eliza
├─ SOUND: click.mp3 (on send button)
└─ IMAGE: entrance_hall_eliza_speaking.png (stays)

ACTION: Eliza gives candle after conversation
├─ SOUND: pick_up_item.mp3
└─ IMAGE: entrance_hall_eliza_gave_candle.png

ACTION: Click "Move to Library (north)"
├─ SOUND: click.mp3
├─ SOUND: walking_between_rooms.mp3
├─ SOUND: library_ghost_noise.mp3 (room ambient - first time)
└─ IMAGE: library_default.png
```

### Library Sequence:
```
ACTION: Click "Chat with Edgar Blackwood"
├─ SOUND: click.mp3
└─ IMAGE: library_edgar_speaking.png

ACTION: Edgar gives amulet after conversation
├─ SOUND: pick_up_item.mp3
└─ IMAGE: library_edgar_gave_amulet.png

ACTION: Click "Use amulet on bookshelf"
├─ SOUND: click.mp3
├─ SOUND: bookshelf_opens.mp3
└─ IMAGE: library_secret_revealed.png

ACTION: Click "Move to Basement (down)"
├─ SOUND: click.mp3
├─ SOUND: walking_between_rooms.mp3
├─ SOUND: basement_creepy.mp3 (room ambient - first time)
└─ IMAGE: basement_pitch_dark.png
```

### Basement Sequence:
```
ACTION: Click "Take key" (while dark)
├─ SOUND: click.mp3
├─ SOUND: useless_selection.mp3
└─ IMAGE: basement_pitch_dark.png (stays)

ACTION: Click "Use candle"
├─ SOUND: click.mp3
└─ IMAGE: basement_lit_key_visible.png

ACTION: Click "Take rusty key"
├─ SOUND: click.mp3
├─ SOUND: pick_up_item.mp3
└─ IMAGE: basement_lit_key_visible.png (same)

ACTION: Click "Move to Library (up)"
├─ SOUND: click.mp3
├─ SOUND: walking_between_rooms.mp3
└─ IMAGE: library_secret_revealed.png

ACTION: Click "Move to Entrance Hall (south)"
├─ SOUND: click.mp3
├─ SOUND: walking_between_rooms.mp3
└─ IMAGE: entrance_hall_eliza_gave_candle.png
```

### Victory Sequence:
```
ACTION: Click "Use locked door" (without key)
├─ SOUND: click.mp3
├─ SOUND: locked_door.mp3
└─ IMAGE: entracnce_hall_default.png (stays)

ACTION: Click "Use rusty key on door"
├─ SOUND: click.mp3
├─ SOUND: unlock_and_open_door.mp3
└─ IMAGE: entrance_hall_door_unlocked.png

ACTION: Click "Exit through door"
├─ SOUND: click.mp3
├─ SOUND: walking_out.mp3
├─ VIDEO: walking_out.mp4 (plays with audio)
└─ IMAGE: outside_of_mansion.png
```

---

## 🎯 SPECIAL CASES

### Invalid/Impossible Actions:
```
ACTION: Player tries impossible action
├─ SOUND: click.mp3 (button press)
├─ SOUND: useless_selection.mp3 (error indication)
└─ IMAGE: (stays same)

Examples:
- Try to take key without light
- Try to use item on wrong object
- Try to go direction that doesn't exist
- Try to use key without having it
```

### Inventory Management:
```
ACTION: Click inventory item to drop
├─ SOUND: click.mp3
├─ SOUND: drop_item.mp3
└─ IMAGE: (stays same)
```

### NPC Conversations:
```
ACTION: Click to start chat
├─ SOUND: click.mp3
└─ IMAGE: (switches to speaking variant)

ACTION: Type and send message
├─ SOUND: click.mp3 (on send)
└─ IMAGE: (stays speaking variant)

ACTION: End chat
├─ SOUND: click.mp3
└─ IMAGE: (updates to post-conversation state)
```

---

## 🐛 EDGE CASES & IMPLEMENTATION NOTES

### Sound Overlap Prevention:
```javascript
// Don't let sounds overlap/clash
let currentSound = null;

function playSound(src) {
    // Stop previous sound if still playing (optional)
    if (currentSound && !currentSound.ended) {
        // Either let it finish or cut it off
        // currentSound.pause();
    }
    
    currentSound = new Audio(src);
    currentSound.play();
}
```

### Multiple Quick Clicks:
- Click sound plays each time
- Action sounds queue or replace
- Images update immediately

### Room Revisiting:
- Ambient sounds: Only on FIRST visit per session
- Action sounds: Play every time
- Images: Always reflect current state

### Page Reload/Refresh:
- Reset `roomsVisited` set
- Menu music plays again
- Load saved game state for images

### Mobile/Touch:
- Touch = Click (same sound)
- Ensure sounds work on mobile (need user interaction first)

---

## ✅ TESTING CHECKLIST

### Sound Testing:
- [ ] Main menu music plays on game start
- [ ] Click sound plays on EVERY button press
- [ ] Entrance hall ambient plays on first entry only
- [ ] Library ambient plays on first entry only
- [ ] Basement ambient plays on first entry only
- [ ] Walking sounds play on room transitions
- [ ] Pick up sound plays when getting items from NPCs
- [ ] Pick up sound plays when taking key
- [ ] Locked door sound plays when trying without key
- [ ] Unlock sound plays when using key successfully
- [ ] Bookshelf sound plays when revealing secret
- [ ] Victory sounds play in correct sequence
- [ ] Invalid action sound plays for impossible actions
- [ ] Drop sound plays when dropping items
- [ ] No jarring sound overlaps
- [ ] Sounds work on mobile devices

### Image Testing:
- [ ] Entrance hall shows correct default image
- [ ] Entrance hall updates when Eliza speaks
- [ ] Entrance hall updates when Eliza gives candle
- [ ] Entrance hall updates when door unlocks
- [ ] Library shows correct default image
- [ ] Library updates when Edgar speaks
- [ ] Library updates when Edgar gives amulet
- [ ] Library updates when secret revealed
- [ ] Basement shows pitch dark initially
- [ ] Basement updates when candle used
- [ ] Victory sequence shows correct images/video
- [ ] No broken image links (check console)
- [ ] Images load quickly

### Integration Testing:
- [ ] Click sound + action sound don't clash
- [ ] Sound plays THEN image updates (feels responsive)
- [ ] Multiple rapid clicks don't break audio
- [ ] Refreshing page works correctly
- [ ] Loading saved game shows correct state
- [ ] Victory sequence is smooth and satisfying

---

## 📝 IMPLEMENTATION SUMMARY

### Backend (`web/simple_app.py`):
- Add `get_current_image(engine, session)` function
- Return image path in `/api/execute` response
- Track `talking_to_npc` in session

### Frontend (`web/templates/simple.html`):
- Replace ASCII art with `<img id="room-image">`
- Add `updateRoomImage(imagePath)` function
- Add sound player system
- Track `roomsVisited` set
- Play click sound on EVERY button press
- Play action-specific sounds based on response

### Sound System:
```javascript
const roomsVisited = new Set();

function playSound(src) {
    const audio = new Audio('/static/' + src);
    audio.play();
}

function handleButtonClick(command) {
    // ALWAYS play click first
    playSound('sounds/click.mp3');
    
    // Then execute command
    executeCommand(command);
}
```

---

## 🚀 READY FOR IMPLEMENTATION

**Once you approve this logic:**
1. I'll implement the backend image selection logic
2. I'll update the frontend to display images
3. I'll add the sound system
4. I'll wire everything together
5. We'll test each room and sequence

**Status:** ⏳ Awaiting your approval/edits

---

**Last Updated:** Ready for review
**Key Change:** Click sound plays on EVERY button press

# 🔥 Firebase Setup Plan - Haunted Mansion

## Architecture Overview

### Components
1. **Firebase Hosting** - Web app (HTML/JS/CSS)
2. **Cloud Functions** - Python backend (Flask converted to Functions)
3. **Firebase Authentication** - Anonymous auth for users
4. **Firestore Database** - Save games and multiplayer rooms
5. **Gemini API** - Already in your GCP project ✅

### Multiplayer Logic
- **Room Owner** = Creator of the game session
- **Room Join** = Others can join the room code
- **Save Ownership** = Room owner's save persists when all players leave
- **Anonymous Auth** = Each player gets unique Firebase UID

## Firebase Setup Steps

### 1. Initialize Firebase
```bash
firebase login
firebase init
```

Select:
- ✅ Hosting
- ✅ Functions (Python)
- ✅ Firestore
- ✅ Authentication (enable later in console)

### 2. Project Structure
```
haunted-mansion/
├── public/                    # Firebase Hosting
│   ├── index.html
│   ├── css/
│   └── js/
├── functions/                 # Cloud Functions (Python)
│   ├── main.py               # Flask app converted
│   ├── requirements.txt
│   └── game/                 # Game engine
├── firestore.rules           # Database security
└── firebase.json             # Firebase config
```

### 3. Firestore Database Schema

```javascript
// Collection: users
users/{userId}
  - savedGames: []            // Array of game state references
  - createdAt: timestamp
  - lastPlayed: timestamp

// Collection: gameSessions (for multiplayer)
gameSessions/{sessionId}
  - ownerId: string           // Creator's Firebase UID
  - roomCode: string          // 6-char code
  - players: map              // {uid: name}
  - gameState: object         // Full game state
  - locations: object         // Location states
  - npcs: object              // NPC conversation history
  - createdAt: timestamp
  - lastActivity: timestamp
  - isActive: boolean

// Collection: saves (for single player)
saves/{userId}
  - gameState: object
  - locations: object
  - npcs: object
  - savedAt: timestamp
```

### 4. Security Rules
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can read/write their own saves
    match /saves/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    // Game sessions
    match /gameSessions/{sessionId} {
      // Anyone can read to join
      allow read: if request.auth != null;
      
      // Only owner can create/delete
      allow create: if request.auth != null;
      allow delete: if request.auth != null && 
                      resource.data.ownerId == request.auth.uid;
      
      // Owner and players can update
      allow update: if request.auth != null && 
                      (resource.data.ownerId == request.auth.uid ||
                       request.auth.uid in resource.data.players);
    }
  }
}
```

### 5. Anonymous Auth Flow
```javascript
// On game start
firebase.auth().signInAnonymously()
  .then((userCredential) => {
    const uid = userCredential.user.uid;
    // Load saves for this UID
    loadUserSaves(uid);
  });

// Persist across sessions
firebase.auth().onAuthStateChanged((user) => {
  if (user) {
    // User is signed in (anonymous)
    currentUserId = user.uid;
  }
});
```

### 6. Multiplayer Room System

#### Create Room
```javascript
async function createRoom(playerName) {
  const user = firebase.auth().currentUser;
  const roomCode = generateRoomCode(); // 6 random chars
  
  const sessionData = {
    ownerId: user.uid,
    roomCode: roomCode,
    players: {
      [user.uid]: playerName
    },
    gameState: initialGameState(),
    createdAt: firebase.firestore.FieldValue.serverTimestamp(),
    isActive: true
  };
  
  await db.collection('gameSessions').doc(roomCode).set(sessionData);
  return roomCode;
}
```

#### Join Room
```javascript
async function joinRoom(roomCode, playerName) {
  const user = firebase.auth().currentUser;
  const sessionRef = db.collection('gameSessions').doc(roomCode);
  
  await sessionRef.update({
    [`players.${user.uid}`]: playerName,
    lastActivity: firebase.firestore.FieldValue.serverTimestamp()
  });
}
```

#### Leave Room / Save Logic
```javascript
async function leaveRoom(roomCode) {
  const user = firebase.auth().currentUser;
  const sessionDoc = await db.collection('gameSessions').doc(roomCode).get();
  const data = sessionDoc.data();
  
  // Remove player
  delete data.players[user.uid];
  
  if (Object.keys(data.players).length === 0) {
    // Last player leaving
    if (data.ownerId === user.uid) {
      // Owner - save to their personal saves
      await db.collection('saves').doc(user.uid).set({
        gameState: data.gameState,
        locations: data.locations,
        npcs: data.npcs,
        savedAt: firebase.firestore.FieldValue.serverTimestamp()
      });
    }
    // Delete room
    await sessionRef.delete();
  } else {
    // Update room
    await sessionRef.update({ players: data.players });
  }
}
```

## Implementation Steps

### Step 1: Firebase Init
```bash
cd "/Users/seanx/code/haunted mansion game /V1"
firebase login
firebase init
```

### Step 2: Convert Flask to Cloud Functions
Create `functions/main.py`:
```python
from firebase_functions import https_fn, options
from firebase_admin import initialize_app, firestore
import google.generativeai as genai
import os

initialize_app()
db = firestore.client()

@https_fn.on_request(
    cors=options.CorsOptions(
        cors_origins=["*"],
        cors_methods=["GET", "POST"],
    )
)
def api(req: https_fn.Request) -> https_fn.Response:
    # Your Flask routes here
    # Access Gemini API with the same key
    pass
```

### Step 3: Update Frontend
Add Firebase SDK to HTML:
```html
<script src="https://www.gstatic.com/firebasejs/10.x.x/firebase-app.js"></script>
<script src="https://www.gstatic.com/firebasejs/10.x.x/firebase-auth.js"></script>
<script src="https://www.gstatic.com/firebasejs/10.x.x/firebase-firestore.js"></script>
```

### Step 4: Enable Services in Console
1. Firebase Console → Authentication → Anonymous
2. Firestore Database → Create
3. Functions → Deploy

## Next Commands to Run

```bash
# 1. Login to Firebase
firebase login

# 2. Initialize project
firebase init

# 3. Deploy
firebase deploy
```

---

**Ready to start? Let's run `firebase login` first!**


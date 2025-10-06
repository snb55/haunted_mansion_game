# How to Play Multiplayer - Haunted Mansion

## 🎮 Quick Start Guide

### Step 1: Start the Server

Open your terminal and run:

```bash
cd "/Users/seanx/code/haunted mansion game /V1"
./start_web.sh
```

Or manually:
```bash
cd "/Users/seanx/code/haunted mansion game /V1/web"
python3 app.py
```

You should see:
```
Starting Haunted Mansion Web Server...
Visit http://localhost:5001 in your browser
```

### Step 2: Create a Game (Player 1)

1. Open your browser to: `http://localhost:5001`
2. Enter your name (e.g., "Alice")
3. Click **"🎮 Create New Game"**
4. You'll see a game code like **"abc123"**
5. **IMPORTANT:** Copy this code - you'll share it with friends!
6. Click **"Enter the Mansion"**

### Step 3: Join the Game (Player 2)

1. Open a NEW browser tab/window (or tell a friend to visit): `http://localhost:5001`
2. Enter your name (e.g., "Bob")
3. Type the game code in the box (e.g., "abc123")
4. Click **"🚪 Join Existing Game"**
5. Click **"Enter the Mansion"**

### Step 4: Play Together!

- Both players are now in the same haunted mansion!
- When Alice picks up an item, Bob sees it disappear
- When Bob moves to another room, Alice sees "Bob went north"
- You can see each other in the same locations
- Work together to escape!

## 🎯 Multiplayer Features

### What You'll See:

**When players join:**
```
"Bob has entered the area."
```

**When players move:**
```
"Alice went north."
"Bob has arrived."
```

**When players interact:**
```
"Alice took the Candle."
"Bob used the Rusty Key!"
```

**When someone wins:**
```
🎉 Alice has escaped the mansion! 🎉
```

### Shared World:
- ✅ Items are shared (if Alice takes it, Bob can't)
- ✅ Puzzles are shared (if Alice unlocks door, it's unlocked for Bob)
- ✅ Locations are shared (basement lit by one player, lit for all)
- ❌ Inventories are NOT shared (each player carries their own items)

## 🔧 Multiple Game Sessions

You can run multiple SEPARATE games at the same time:

**Game 1:**
- Alice creates game → Gets code "abc123"
- Bob joins "abc123" → They play together

**Game 2:**
- Charlie creates game → Gets code "xyz789"
- Diana joins "xyz789" → They play together

Alice/Bob and Charlie/Diana are in COMPLETELY DIFFERENT game worlds!

## 📱 Testing Locally

**Easy test (one computer):**
1. Open browser to `http://localhost:5001`
2. Create a game, note the code
3. Open a NEW PRIVATE/INCOGNITO window
4. Join with the same code
5. Play both players yourself!

**With friends (same network):**
1. Find your IP: `ifconfig | grep inet` (look for 192.168.x.x)
2. Share: `http://YOUR_IP:5001`
3. They join using your session code

## 💾 Persistence

Each session saves to its own file:
- Session "abc123" → `saves/session_abc123.json`
- Session "xyz789" → `saves/session_xyz789.json`

**To resume a game:**
- Just rejoin using the same session code!
- The world state (items, puzzles) is preserved
- Player inventories reset (limitation)

## 🐛 Troubleshooting

**Port already in use:**
```bash
pkill -f "python3 app.py"
cd web && python3 app.py
```

**Can't connect:**
- Make sure server is running
- Check you're using port 5001
- Try http://127.0.0.1:5001

**Players can't see each other:**
- Make sure using the SAME session code
- Both must have clicked "Enter the Mansion"

---

**Now go play!** 👻🏚️

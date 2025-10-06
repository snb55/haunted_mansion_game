# Haunted Mansion - Simple Web Version

## 🎉 What's New?

This is a **brand new web interface** that recreates the perfect CLI experience you love, but in a browser!

### ✅ What Makes It Better

- ✨ **No WebSockets** - Uses simple HTTP requests, no connection issues
- 🎮 **Same Perfect Interface** - Arrow keys + Enter navigation, just like the CLI
- 🏠 **Single Player** - Focused, stable, personal experience
- 🎨 **Beautiful ASCII Art** - All your location art displays perfectly
- 💾 **Save/Load** - Full save game support via sessions
- 🚀 **Fast & Reliable** - No multiplayer complexity, just works

### 🎯 Key Features

1. **Identical to CLI Experience**
   - Menu-based navigation with arrow keys (↑/↓)
   - Press ENTER to execute commands
   - Click commands with mouse if you prefer
   - Dynamic action menu based on game state

2. **All Game Features Work**
   - Take/drop/use items
   - Examine objects
   - Navigate rooms
   - Solve puzzles
   - Win the game!

3. **Visual Enhancements**
   - Location ASCII art displays
   - Item ASCII art when picking up items
   - Smooth animations and transitions
   - Beautiful dark theme with red accents

## 🚀 How to Start

### Option 1: Use the Startup Script (Recommended)

```bash
./start_web_simple.sh
```

### Option 2: Run Directly

```bash
cd web
python3 simple_app.py
```

Then open your browser to: **http://localhost:5008**

## 🎮 How to Play

1. **Start**: Choose "Start Adventure"
2. **Navigate**: Use ↑/↓ arrow keys or click on commands
3. **Execute**: Press ENTER or click to execute the selected command
4. **Continue**: After each action, press ENTER to continue
5. **Save**: The "Save Game" option is always available in the menu

### Controls

- **↑/↓ Arrow Keys** - Navigate through available commands
- **ENTER** - Execute selected command / Continue after results
- **Mouse Click** - Click any command to execute it directly

## 🔧 Technical Details

### Architecture

- **Backend**: Flask (Python)
- **Frontend**: Pure JavaScript (no frameworks)
- **Storage**: Session-based with file persistence
- **Communication**: Simple HTTP POST/GET (no WebSockets)

### File Structure

```
web/
├── simple_app.py          # New Flask app (no websockets)
├── templates/
│   └── simple.html        # New game interface
└── [old files...]         # Previous multiplayer version (kept for reference)
```

### Sessions

- Each browser session gets a unique game instance
- Game state is preserved in the session
- Save files work exactly like the CLI version
- No interference between different browser tabs/users

## 🆚 Differences from Old Web Version

| Feature | Old Web Version | New Simple Version |
|---------|----------------|-------------------|
| Connection | WebSockets | HTTP Requests |
| Players | Multiplayer | Single Player |
| Stability | Connection issues | Rock solid |
| Interface | Command parsing from text | Pre-built menu like CLI |
| Complexity | High | Low |
| Experience | Different from CLI | Identical to CLI |

## 🐛 Troubleshooting

### Port Already in Use

If port 5008 is already in use, edit `simple_app.py` and change the port:

```python
app.run(host='0.0.0.0', port=5009, debug=True)  # Change 5008 to 5009
```

### Game Not Loading

1. Make sure you're in the project root directory
2. Check that `game/` directory exists with all files
3. Try clearing browser cache and refreshing

### Keyboard Not Working

- Make sure the game screen is focused (click anywhere on the page)
- Try using mouse clicks instead
- Check browser console for JavaScript errors (F12)

## 🎯 What's Next?

This version is complete and ready to use! It matches your CLI experience perfectly. If you want to add features:

1. **Mobile support** - Add touch swipe gestures
2. **Sound effects** - Add spooky background music
3. **More ASCII art** - Expand art for more items/locations
4. **Themes** - Add different color schemes

## 📝 Notes

- The old web version (multiplayer) is still available at `web/app.py` (port 5007)
- This new version is completely independent and won't interfere
- All game data files are shared between CLI and web versions
- Save files from CLI and web are compatible!

---

**Enjoy escaping the mansion! 🏚️👻**



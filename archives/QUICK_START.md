# 🎮 Quick Start Guide - Haunted Mansion

## Ready to Play? Start Here!

### Step 1: Install Dependencies

```bash
cd "/Users/seanx/code/haunted mansion game /V1"
pip3 install -r requirements.txt
```

### Step 2: Choose Your Interface

## Option 1: Interactive CLI (Arrow Keys) ⭐ BEST EXPERIENCE

**No typing! Just arrow keys and Enter**

```bash
python3 main_interactive.py
```

**How it works:**
- Use ↑ and ↓ arrows to highlight an action
- Press Enter to execute
- Game shows you exactly what you can do

**Example:**
```
═══════════════════════════════════════
Entrance Hall
You stand in a grand entrance hall...

You notice:
  - Locked Door

Exits: north
═══════════════════════════════════════

[?] What do you want to do?:
 ❯ 👁️  Look Around
   🔍 Examine Locked Door
   🚶 Go NORTH
   🎒 Check Inventory
   ❓ Help
   💾 Save & Quit
```

## Option 2: Classic CLI (Type Commands)

**For traditionalists who like typing**

```bash
python3 main.py
```

**Commands to type:**
- `look` - Look around
- `go north` - Move north
- `take candle` - Pick up candle
- `use key` - Use an item
- `inventory` - Check inventory
- `examine door` - Look at something
- `quit` - Save and exit

## Option 3: Web Interface

**Browser-based (single player)**

```bash
cd web
python3 app.py
```

Then visit: `http://localhost:5001`

---

## 🎯 Goal

**Escape the haunted mansion before it's too late!**

### Quick Walkthrough (Spoilers!)

<details>
<summary>Click to see solution</summary>

1. Start in Entrance Hall
2. Go north to Library
3. Take the Candle
4. Take the Ancient Amulet
5. Use the Ancient Amulet (reveals secret passage)
6. Go down to Basement
7. Use the Candle (lights the basement)
8. Take the Rusty Key
9. Go up to Library
10. Go south to Entrance Hall
11. Use the Rusty Key
12. **YOU WIN!** 🎉

</details>

---

## 💡 Tips

**For Interactive CLI:**
- Just navigate the menus - everything you need is shown
- Actions disappear when no longer available
- New actions appear as you progress

**For Classic CLI:**
- Type `help` anytime for command list
- Game auto-saves after each action
- You can quit and resume anytime

**For Web:**
- Click buttons or type commands
- Same gameplay as CLI versions

---

## 🐛 Troubleshooting

**Interactive CLI not working?**
- Make sure you're in a real terminal (not remote session)
- Install inquirer: `pip3 install inquirer`

**Classic CLI - "command not found"?**
- Type `help` to see all commands
- Commands are case-insensitive

**Port already in use (web)?**
- Kill existing: `pkill -f "python3 app.py"`
- Or use different port in `web/app.py`

---

## 📚 More Info

- `README.md` - Full documentation
- `FUTURE_OPTIMIZATIONS.md` - Upcoming features
- `HOW_TO_PLAY_MULTIPLAYER.md` - Multiplayer guide (in development)

---

**Now go play and escape the mansion!** 👻🏚️

# 🤖 Quick Start: AI NPCs

## Setup (3 Steps)

```bash
# 1. Get API key
# Visit: https://makersuite.google.com/app/apikey

# 2. Install package
pip3 install google-generativeai

# 3. Run with your API key
GEMINI_API_KEY='your-api-key-here' ./start_with_ai.sh
```

Then open: **http://localhost:5008**

---

## Meet the NPCs

### 👧 **Little Eliza** (Entrance Hall)
- Guards the **Candle**
- Playful ghost child
- Loves riddles and games

### 📚 **Edgar Blackwood** (Library)
- Guards the **Ancient Amulet**
- Melancholic librarian
- Speaks in riddles

---

## How to Play

1. **Look around** - See who's in the room
2. **Talk to them** - Click "💬 Talk to [Name]"
3. **Get a puzzle** - They'll challenge you
4. **Answer it** - Click "💭 Answer Puzzle" and type
5. **Get the item** - If correct, they give you what they guard!

---

## Example

```
You see: Little Eliza (guarding something...)

→ Click "Talk to Little Eliza"

She says: "Solve my riddle for my candle!
         What has keys but no locks?"

→ Click "Answer Puzzle"
→ Type: "a piano"
→ Submit

She says: "CORRECT! Here's the candle!"

→ Click "Take Candle"
→ You got it! 🕯️
```

---

## Commands

**Web Interface:**
- Click commands in menu
- Type answers in text box

**CLI:**
- `talk Edgar` - Talk to NPC
- `answer your answer` - Answer puzzle

---

## No API Key?

Game works without it! NPCs give simple responses.
But with API = **unique puzzles every time!** 🎮

---

**Full guide:** `AI_NPC_SETUP_GUIDE.md`


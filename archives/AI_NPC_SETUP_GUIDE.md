# 🤖 AI NPC Setup Guide

## What's New?

Your haunted mansion now has **AI-powered NPCs** that use Google's Gemini API to:
- Have dynamic conversations
- Create unique puzzles each time
- Guard important items (candle and amulet)
- Remember your conversation history
- Adapt to your game state

## 🎭 The NPCs

### 1. **Little Eliza** (Entrance Hall)
- A mischievous ghost child
- Guards the **Candle**
- Loves games and puzzles
- Playful but eerie Victorian child personality

### 2. **Edgar Blackwood** (Library)
- The ghostly librarian
- Guards the **Ancient Amulet**
- Obsessed with riddles and wordplay
- Speaks in old-fashioned, poetic manner

## 🚀 Setup Instructions

### Step 1: Get Your Gemini API Key

1. Go to: **https://makersuite.google.com/app/apikey**
2. Click **"Get API Key"** or **"Create API Key"**
3. Copy your API key (looks like: `AIzaSy...`)

### Step 2: Install Dependencies

```bash
cd "/Users/seanx/code/haunted mansion game /V1"
pip3 install google-generativeai
```

Or install all requirements:
```bash
pip3 install -r requirements.txt
```

### Step 3: Set Your API Key

**Option A: Environment Variable (Recommended)**
```bash
export GEMINI_API_KEY='your-api-key-here'
./start_web_simple.sh
```

**Option B: Persistent (Add to your shell profile)**

Add to `~/.zshrc` or `~/.bashrc`:
```bash
export GEMINI_API_KEY='your-api-key-here'
```

Then reload:
```bash
source ~/.zshrc  # or source ~/.bashrc
```

**Option C: One-line start**
```bash
GEMINI_API_KEY='your-api-key-here' ./start_web_simple.sh
```

## 🎮 How to Play with NPCs

### 1. Talk to NPCs
When you see an NPC in a location:
```
👻 Present:
  - Little Eliza (guarding something...)
```

**Commands:**
- `talk Eliza` - Start a conversation
- `talk Edgar` - Talk to the librarian

### 2. Solve Their Puzzles
The AI will present you with a unique puzzle! Examples:
- Riddles
- Word puzzles
- Logic problems
- Haunted mansion trivia

### 3. Answer the Puzzle
After talking, they'll give you a puzzle. Type your answer:

**In Web Interface:**
- Click "💭 Answer Puzzle"
- Type your answer in the text box
- Click "Submit Answer"

**In CLI:**
```
answer your answer here
```

### 4. Get Your Reward!
If correct, the NPC will give you the item they're guarding:
```
✨ Little Eliza has placed the Candle before you!
(Use 'take Candle' to pick it up)
```

## 🎯 Gameplay Flow

**Before AI NPCs:**
```
1. Enter location → 2. Take item → 3. Use item
```

**With AI NPCs:**
```
1. Enter location
2. Talk to NPC → Get puzzle
3. Answer puzzle correctly
4. NPC gives you the item
5. Take item
6. Use item to progress
```

## 💡 Example Session

```
> look
Entrance Hall
=============
You stand in a grand entrance hall...

👻 Present:
  - Little Eliza (guarding something...)

> talk Eliza

Little Eliza says:
"Would you like to play with me? I've been so lonely... 
Answer my riddle and I'll share my precious candle with you!
What walks on four legs in the morning, two legs at noon, 
and three legs in the evening?"

(Type 'answer <your answer>' to respond)

> answer a human

Little Eliza responds:
"CORRECT: Oh clever one! Yes, it's a human! Here, take my 
candle, you've earned it..."

✨ Little Eliza has placed the Candle before you!
(Use 'take Candle' to pick it up)

> take candle

You take the Candle.
     🕯️
     ║║
    ╱  ╲
   │    │
   │ 🔥 │
   ╲____╱
```

## 🔧 Troubleshooting

### "Warning: google-generativeai not installed"
```bash
pip3 install google-generativeai
```

### "No API key found"
Make sure you set the environment variable:
```bash
export GEMINI_API_KEY='your-key-here'
```

### "API rate limit exceeded"
Gemini has usage limits on the free tier. Wait a few minutes and try again.

### NPCs give fallback responses
If the API isn't working, NPCs will use simple fallback responses. Check:
1. Is your API key set correctly?
2. Is google-generativeai installed?
3. Do you have internet connection?

## 📊 Technical Details

### How It Works

1. **NPC Data**: Stored in `game/data/npcs.json`
2. **AI Engine**: `game/ai_npc.py` manages Gemini API calls
3. **Personality Prompts**: Each NPC has a unique personality that guides AI responses
4. **Context-Aware**: AI knows your inventory, location, and conversation history
5. **Puzzle Validation**: AI judges if your answer is correct (even with typos/variations!)

### Files Changed
- ✅ `game/ai_npc.py` - NEW: AI NPC system
- ✅ `game/data/npcs.json` - NEW: NPC definitions
- ✅ `game/data/locations.json` - UPDATED: Removed items (NPCs guard them now)
- ✅ `game/game_engine.py` - UPDATED: Added talk/answer commands
- ✅ `web/simple_app.py` - UPDATED: Added NPC support
- ✅ `web/templates/simple.html` - UPDATED: Answer input UI
- ✅ `requirements.txt` - UPDATED: Added google-generativeai

## 🎨 Customization

Want to add more NPCs or change personalities? Edit `game/data/npcs.json`:

```json
{
  "your_npc_id": {
    "name": "Your NPC Name",
    "personality": "Describe their personality for the AI...",
    "role": "What do they do?",
    "location": "where_they_are",
    "guards_item": "item_id",
    "description": "How they look",
    "greeting": "First words they say"
  }
}
```

## 🌟 Benefits

**Dynamic Gameplay:**
- Different puzzles every playthrough
- Unique conversations
- More challenging and engaging

**Replayability:**
- AI generates new content each time
- Conversations feel natural
- Never the same puzzle twice

**Atmospheric:**
- NPCs add life to the mansion
- More immersive storytelling
- Victorian ghost aesthetics

---

**Ready to meet the ghosts? Get your API key and start playing! 👻🕯️**


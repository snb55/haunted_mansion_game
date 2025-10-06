"""AI-powered NPC system using Google Gemini API."""

import os
import json
from typing import Optional, Dict, List
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Warning: google-generativeai not installed. NPCs will use fallback responses.")


class AINPC:
    """AI-powered NPC that uses Gemini to generate contextual responses."""
    
    def __init__(self, npc_id: str, name: str, personality: str, role: str, 
                 location: str, guards_item: Optional[str] = None, 
                 puzzle_solved: bool = False):
        """
        Initialize an AI NPC.
        
        Args:
            npc_id: Unique identifier
            name: Display name
            personality: Personality description for AI prompting
            role: What they do in the game
            location: Where they are located
            guards_item: Item they guard (given after puzzle)
            puzzle_solved: Whether player solved their puzzle
        """
        self.id = npc_id
        self.name = name
        self.personality = personality
        self.role = role
        self.location = location
        self.guards_item = guards_item
        self.puzzle_solved = puzzle_solved
        self.conversation_history: List[Dict] = []
        self.current_puzzle: Optional[str] = None
        self.puzzle_answer: Optional[str] = None
        
        # Initialize Gemini if available
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.model = None
        
        if GEMINI_AVAILABLE and self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                # Use Gemini 2.0 Flash - fast and reliable
                self.model = genai.GenerativeModel('gemini-2.0-flash')
            except Exception as e:
                print(f"Failed to initialize Gemini for {name}: {e}")
    
    def generate_system_prompt(self, game_state: Dict) -> str:
        """Generate the system prompt for the AI based on NPC personality and game state."""
        prompt = f"""You are {self.name}, {self.personality}

YOUR ROLE: {self.role}

SETTING: You are in a haunted mansion. A player is trying to escape.

YOUR LOCATION: {self.location}

CURRENT GAME STATE:
- Player inventory: {', '.join(game_state.get('inventory', [])) or 'empty'}
- Player location: {game_state.get('location', 'unknown')}
"""
        
        if self.guards_item and not self.puzzle_solved:
            prompt += f"""
IMPORTANT: You are guarding the {self.guards_item}. The player needs this item to progress.

Have a NATURAL CONVERSATION with them. Don't just give them a single puzzle and demand an answer.
Instead:
- Greet them in character
- Engage in dialogue about the mansion, your past, their quest
- Challenge them with questions, riddles, or philosophical discussions
- React to what they say
- After 2-3 meaningful exchanges where they prove themselves (clever answers, kind words, good reasoning),
  decide they've earned your trust and give them the item

This should feel like talking to a real ghost, not a vending machine! Be mysterious, engaging, and dynamic.
"""
        elif self.guards_item and self.puzzle_solved:
            prompt += f"""
IMPORTANT: The player already solved your puzzle! You gave them the {self.guards_item}.
Be proud of them. Offer advice about using the item or other parts of the mansion.
"""
        else:
            prompt += """
You don't guard any items, but you have knowledge about the mansion.
Be helpful in a cryptic way. Give hints and atmosphere.
"""
        
        prompt += """

RULES:
- Stay in character at ALL times
- Keep responses to 2-4 sentences (brief but atmospheric)
- Be spooky, mysterious, or eccentric depending on your personality
- Don't break the fourth wall
- Don't mention being an AI
- If asked about the puzzle and it's not solved yet, remind them of the puzzle
- Use emojis sparingly (1-2 max) for atmosphere

Respond naturally to the player's message."""
        
        return prompt
    
    def talk(self, player_message: str, game_state: Dict) -> tuple[str, bool]:
        """
        Have a conversation with the NPC.
        
        Args:
            player_message: What the player said
            game_state: Current game state (inventory, location, etc.)
            
        Returns:
            Tuple of (NPC's response, should_give_item)
        """
        # Fallback if Gemini not available
        if not self.model:
            return self._fallback_response(player_message), False
        
        try:
            # Build full prompt with context
            system_prompt = self.generate_system_prompt(game_state)
            
            # Add conversation history context
            history_context = ""
            if self.conversation_history:
                history_context = "\n\nPREVIOUS CONVERSATION:\n"
                for msg in self.conversation_history[-5:]:  # Last 5 exchanges
                    history_context += f"Player: {msg['player']}\nYou: {msg['npc']}\n"
            
            # Add special instructions for puzzle completion detection
            give_item_instruction = ""
            if self.guards_item and not self.puzzle_solved:
                give_item_instruction = f"""

IMPORTANT: You are having a conversation with the player. After 2-3 good exchanges where they prove themselves 
worthy (through wit, kindness, or solving a challenge you give), you should decide to give them the {self.guards_item}.

When you decide they've earned it, include the EXACT phrase "[GIVE_ITEM]" somewhere in your response. 
This will trigger giving them the item. Only use this phrase ONCE when you truly feel they've proven themselves.

Be conversational and engaging. Don't just ask one puzzle - have a real dialogue!"""
            
            full_prompt = f"{system_prompt}{give_item_instruction}{history_context}\n\nPlayer says: \"{player_message}\"\n\nYour response:"
            
            # Generate response
            response = self.model.generate_content(full_prompt)
            npc_response = response.text.strip()
            
            # Check if NPC decided to give item
            should_give_item = False
            if "[GIVE_ITEM]" in npc_response:
                should_give_item = True
                self.puzzle_solved = True
                # Remove the trigger phrase from the response
                npc_response = npc_response.replace("[GIVE_ITEM]", "").strip()
            
            # Store in history
            self.conversation_history.append({
                'player': player_message,
                'npc': npc_response
            })
            
            return npc_response, should_give_item
            
        except Exception as e:
            print(f"Gemini API error for {self.name}: {e}")
            return self._fallback_response(player_message), False
    
    def check_puzzle_answer(self, answer: str, game_state: Dict) -> tuple[bool, str]:
        """
        Check if the puzzle answer is correct using AI.
        
        Args:
            answer: Player's answer
            game_state: Current game state
            
        Returns:
            (is_correct, response_message)
        """
        if not self.model or self.puzzle_solved:
            return False, "I have no puzzle for you."
        
        try:
            prompt = f"""You are {self.name}, {self.personality}

You previously asked the player a puzzle. They are now giving you their answer.

PUZZLE CONTEXT: You are guarding the {self.guards_item} and only give it after the puzzle is solved.

The player's answer is: "{answer}"

Evaluate their answer:
1. Is it correct or close enough to be correct?
2. If correct, respond with enthusiasm and tell them you'll give them the {self.guards_item}
3. If incorrect, respond in character explaining why it's wrong (be nice but stay mysterious)

Start your response with EXACTLY one of these:
- "CORRECT:" if their answer is right
- "INCORRECT:" if their answer is wrong

Then follow with 1-2 sentences in character.

Example correct: "CORRECT: Ah, you've solved it! The answer was indeed [answer]. Take the {self.guards_item}, you've earned it."
Example wrong: "INCORRECT: Not quite, brave soul. Think more carefully about the shadows..."

Your response:"""
            
            response = self.model.generate_content(prompt)
            full_response = response.text.strip()
            
            # Check if correct
            if full_response.upper().startswith("CORRECT:"):
                self.puzzle_solved = True
                message = full_response[8:].strip()  # Remove "CORRECT:"
                return True, message
            else:
                # Remove "INCORRECT:" prefix if present
                message = full_response.replace("INCORRECT:", "").strip()
                return False, message
                
        except Exception as e:
            print(f"Error checking puzzle answer: {e}")
            return False, "I... cannot judge your answer right now. Try again later."
    
    def _fallback_response(self, player_message: str) -> tuple[str, bool]:
        """Fallback responses when Gemini is not available."""
        if self.guards_item and not self.puzzle_solved:
            # Simple conversation counter for fallback
            if len(self.conversation_history) >= 2:
                self.puzzle_solved = True
                return f"You have proven yourself through our conversation. Take the {self.guards_item}.", True
            return f"Greetings... I am {self.name}. Speak with me, and I may share what I guard...", False
        elif self.guards_item and self.puzzle_solved:
            return f"You have already proven yourself worthy. The {self.guards_item} is yours.", False
        else:
            return f"I am {self.name}. I have seen many souls wander these halls...", False
    
    def to_dict(self) -> Dict:
        """Serialize NPC state."""
        return {
            'id': self.id,
            'name': self.name,
            'personality': self.personality,
            'role': self.role,
            'location': self.location,
            'guards_item': self.guards_item,
            'puzzle_solved': self.puzzle_solved,
            'conversation_history': self.conversation_history
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'AINPC':
        """Deserialize NPC state."""
        npc = AINPC(
            npc_id=data['id'],
            name=data['name'],
            personality=data['personality'],
            role=data['role'],
            location=data['location'],
            guards_item=data.get('guards_item'),
            puzzle_solved=data.get('puzzle_solved', False)
        )
        npc.conversation_history = data.get('conversation_history', [])
        return npc


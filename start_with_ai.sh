#!/bin/bash

# Haunted Mansion with AI NPCs - Startup Script

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║      HAUNTED MANSION - With AI-Powered NPCs! 🤖👻          ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check if GEMINI_API_KEY is set
if [ -z "$GEMINI_API_KEY" ]; then
    echo "⚠️  WARNING: GEMINI_API_KEY not set!"
    echo ""
    echo "NPCs will use fallback responses without an API key."
    echo ""
    echo "To enable AI-powered NPCs:"
    echo "  1. Get an API key from: https://makersuite.google.com/app/apikey"
    echo "  2. Run: export GEMINI_API_KEY='your-api-key-here'"
    echo "  3. Or run: GEMINI_API_KEY='your-key' ./start_with_ai.sh"
    echo ""
    read -p "Press ENTER to continue anyway, or Ctrl+C to cancel..."
else
    echo "✅ Gemini API key found!"
    echo ""
fi

# Check if google-generativeai is installed
python3 -c "import google.generativeai" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  WARNING: google-generativeai not installed!"
    echo ""
    echo "Installing now..."
    pip3 install google-generativeai
    echo ""
fi

echo "Starting the web server with AI NPCs..."
echo ""

cd web
python3 simple_app.py


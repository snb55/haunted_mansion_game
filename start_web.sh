#!/bin/bash
# Start the Haunted Mansion Web Server

echo "🏚️  Starting Haunted Mansion Web Server..."
echo ""
echo "Visit http://localhost:5000 in your browser"
echo "Open multiple browser tabs/windows to test multiplayer!"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

cd "$(dirname "$0")/web"
python3 app.py

#!/bin/bash

# Haunted Mansion - Simple Web Version Startup Script
# This starts the NEW web version without websockets - just like the CLI!

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║           HAUNTED MANSION - Simple Web Version              ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "Starting the web server..."
echo ""

cd web
python3 simple_app.py



// Haunted Mansion Game Client

let socket;
let playerName = '';
let sessionCode = '';
let availableCommands = [];
let selectedIndex = 0;
let isWaitingForResponse = false;

// DOM Elements
const loginScreen = document.getElementById('login-screen');
const gameScreen = document.getElementById('game-screen');
const playerNameInput = document.getElementById('player-name');
const startGameBtn = document.getElementById('start-game');
const createSessionBtn = document.getElementById('create-session');
const joinSessionBtn = document.getElementById('join-session');
const sessionCodeInput = document.getElementById('session-code');
const sessionInfo = document.getElementById('session-info');
const displaySessionCode = document.getElementById('display-session-code');
const playerNameDisplay = document.getElementById('player-name-display');
const outputArea = document.getElementById('output-area');
const commandMenu = document.getElementById('command-menu');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Focus on name input
    playerNameInput.focus();

    // Create session button
    createSessionBtn.addEventListener('click', createSession);

    // Join session button
    joinSessionBtn.addEventListener('click', joinSession);

    // Start game button
    startGameBtn.addEventListener('click', startGame);

    // Enter key on name input
    playerNameInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && sessionCode) {
            startGame();
        }
    });

    // Arrow key navigation
    document.addEventListener('keydown', (e) => {
        if (!gameScreen.classList.contains('active')) {
            return;
        }

        // Prevent input while waiting for response
        if (isWaitingForResponse && (e.key === 'Enter')) {
            e.preventDefault();
            console.log('Still waiting for previous command to complete');
            return;
        }

        if (e.key === 'ArrowUp') {
            e.preventDefault();
            navigateUp();
        } else if (e.key === 'ArrowDown') {
            e.preventDefault();
            navigateDown();
        } else if (e.key === 'Enter') {
            e.preventDefault();
            executeSelectedCommand();
        }
    });
});

function createSession() {
    const name = playerNameInput.value.trim();
    if (!name) {
        alert('Please enter your name first!');
        return;
    }

    // Generate random session code
    sessionCode = Math.random().toString(36).substring(2, 8);
    playerName = name;

    // Show session info
    displaySessionCode.textContent = sessionCode;
    sessionInfo.style.display = 'block';
    startGameBtn.style.display = 'block';
    createSessionBtn.style.display = 'none';
    joinSessionBtn.style.display = 'none';
    sessionCodeInput.style.display = 'none';
    document.querySelector('.or-divider').style.display = 'none';
}

function joinSession() {
    const name = playerNameInput.value.trim();
    const code = sessionCodeInput.value.trim();

    if (!name) {
        alert('Please enter your name first!');
        return;
    }

    if (!code) {
        alert('Please enter a game code!');
        return;
    }

    sessionCode = code.toLowerCase();
    playerName = name;

    // Show session info
    displaySessionCode.textContent = sessionCode;
    sessionInfo.style.display = 'block';
    startGameBtn.style.display = 'block';
    createSessionBtn.style.display = 'none';
    joinSessionBtn.style.display = 'none';
    sessionCodeInput.style.display = 'none';
    document.querySelector('.or-divider').style.display = 'none';
}

function startGame() {
    if (!playerName || !sessionCode) {
        alert('Please create or join a game first!');
        return;
    }

    // Connect to server
    socket = io();

    // Socket event handlers
    socket.on('connected', (data) => {
        console.log('Connected with session ID:', data.session_id);

        // Join the game with session code
        socket.emit('join_game', {
            name: playerName,
            session_code: sessionCode
        });

        // Switch to game screen
        loginScreen.classList.remove('active');
        gameScreen.classList.add('active');

        playerNameDisplay.textContent = `Playing as: ${playerName} | Room: ${sessionCode}`;
    });

    socket.on('game_message', (data) => {
        // Re-enable input FIRST
        isWaitingForResponse = false;

        addMessage(data.message, data.type || 'success');

        // Update command menu after look or success messages
        if (data.type === 'look' || data.type === 'success') {
            updateCommandMenu(data.message);
        }
    });

    socket.on('player_joined', (data) => {
        addMessage(`${data.player_name} has entered the area.`, 'info');
    });

    socket.on('player_left', (data) => {
        addMessage(`${data.player_name} has left the area.`, 'info');
    });

    socket.on('player_arrived', (data) => {
        addMessage(`${data.player_name} has arrived.`, 'info');
    });

    socket.on('game_won', (data) => {
        addMessage(`🎉 ${data.player_name} has escaped the mansion! 🎉`, 'win');
    });

    socket.on('disconnect', () => {
        addMessage('Disconnected from server.', 'error');
    });
}

function addMessage(text, type = 'success') {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.textContent = text;

    outputArea.appendChild(messageDiv);

    // Auto-scroll to bottom
    outputArea.scrollTop = outputArea.scrollHeight;
}

function updateCommandMenu(message) {
    // Parse the "What to do:" section from the message
    const whatToDoMatch = message.match(/💡 What to do:([\s\S]*?)$/);

    if (!whatToDoMatch) {
        return;
    }

    const actionsText = whatToDoMatch[1];
    const actionLines = actionsText.split('\n').filter(line => line.trim().startsWith('•'));

    // Extract commands
    availableCommands = [];
    actionLines.forEach(line => {
        const match = line.match(/'([^']+)'/);
        if (match) {
            availableCommands.push(match[1]);
        }
    });

    // Render command menu
    renderCommandMenu();
}

function renderCommandMenu() {
    commandMenu.innerHTML = '';
    selectedIndex = 0;

    availableCommands.forEach((command, index) => {
        const item = document.createElement('div');
        item.className = 'command-item';

        // Add icons based on command type
        if (command.startsWith('take')) {
            item.textContent = `📦 ${command}`;
        } else if (command.startsWith('go')) {
            item.textContent = `🚶 ${command}`;
        } else if (command.startsWith('examine')) {
            item.textContent = `🔍 ${command}`;
        } else if (command.startsWith('use')) {
            item.textContent = `🔧 ${command}`;
        } else if (command === 'inventory') {
            item.textContent = `🎒 ${command}`;
        } else if (command === 'look') {
            item.textContent = `👁️  ${command}`;
        } else if (command === 'help') {
            item.textContent = `❓ ${command}`;
        } else if (command.startsWith('drop')) {
            item.textContent = `⬇️  ${command}`;
        } else {
            item.textContent = command;
        }

        // Click handler
        item.addEventListener('click', () => {
            if (!isWaitingForResponse) {
                selectedIndex = index;
                // Update selection visually
                const items = commandMenu.querySelectorAll('.command-item');
                items.forEach(i => i.classList.remove('selected'));
                item.classList.add('selected');
                // Execute
                executeSelectedCommand();
            }
        });

        // Select first item by default
        if (index === 0) {
            item.classList.add('selected');
        }

        commandMenu.appendChild(item);
    });
}

function navigateUp() {
    if (availableCommands.length === 0) return;

    // Remove current selection
    const items = commandMenu.querySelectorAll('.command-item');
    if (items[selectedIndex]) {
        items[selectedIndex].classList.remove('selected');
    }

    // Move up (with wrap around)
    selectedIndex = (selectedIndex - 1 + availableCommands.length) % availableCommands.length;

    // Add new selection
    if (items[selectedIndex]) {
        items[selectedIndex].classList.add('selected');
        items[selectedIndex].scrollIntoView({ block: 'nearest', behavior: 'smooth' });
    }
}

function navigateDown() {
    if (availableCommands.length === 0) return;

    // Remove current selection
    const items = commandMenu.querySelectorAll('.command-item');
    if (items[selectedIndex]) {
        items[selectedIndex].classList.remove('selected');
    }

    // Move down (with wrap around)
    selectedIndex = (selectedIndex + 1) % availableCommands.length;

    // Add new selection
    if (items[selectedIndex]) {
        items[selectedIndex].classList.add('selected');
        items[selectedIndex].scrollIntoView({ block: 'nearest', behavior: 'smooth' });
    }
}

function executeSelectedCommand() {
    if (availableCommands.length === 0) {
        console.log('No commands available');
        return;
    }

    if (isWaitingForResponse) {
        console.log('Already waiting for response, ignoring');
        return;
    }

    const command = availableCommands[selectedIndex];
    console.log('Executing command:', command);

    // Set waiting flag
    isWaitingForResponse = true;

    // Send to server (don't display the command in output)
    if (socket && socket.connected) {
        socket.emit('command', { command: command });
    } else {
        console.error('Socket not connected');
        isWaitingForResponse = false;
    }
}

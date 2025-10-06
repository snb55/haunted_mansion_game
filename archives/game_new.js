// Haunted Mansion - Clean Terminal Version

let socket;
let playerName = '';
let sessionCode = '';
let commands = [];
let selectedIndex = 0;
let waiting = false;

// DOM elements
const loginScreen = document.getElementById('login-screen');
const gameScreen = document.getElementById('game-screen');
const playerNameInput = document.getElementById('player-name');
const startBtn = document.getElementById('start-btn');
const output = document.getElementById('output');
const menu = document.getElementById('menu');
const playerInfo = document.getElementById('player-info');

// Start game
startBtn.addEventListener('click', startGame);
playerNameInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') startGame();
});

function startGame() {
    playerName = playerNameInput.value.trim();
    if (!playerName) {
        alert('Please enter your name');
        return;
    }

    // Generate session code
    sessionCode = Math.random().toString(36).substring(2, 8);

    // Connect to server
    socket = io();

    socket.on('connect', () => {
        console.log('Connected to server');
        socket.emit('join_game', {
            name: playerName,
            session_code: sessionCode
        });
    });

    socket.on('game_message', handleMessage);
    socket.on('player_joined', (data) => addOutput(`${data.player_name} joined`, 'info'));
    socket.on('player_left', (data) => addOutput(`${data.player_name} left`, 'info'));
    socket.on('player_arrived', (data) => addOutput(`${data.player_name} arrived`, 'info'));
    socket.on('game_won', (data) => addOutput(`🎉 ${data.player_name} escaped! 🎉`, 'system'));
    socket.on('disconnect', () => addOutput('Disconnected from server', 'error'));

    // Show game screen
    loginScreen.classList.add('hidden');
    gameScreen.classList.remove('hidden');
    playerInfo.textContent = `${playerName} | Room: ${sessionCode}`;
}

function handleMessage(data) {
    // Always reset waiting flag when we get a response
    waiting = false;

    addOutput(data.message, data.type || 'system');

    // Update menu if it's a look or success message
    if (data.type === 'look' || data.type === 'success') {
        updateMenu(data.message);
    }
}

function addOutput(text, type = 'system') {
    const div = document.createElement('div');
    div.className = `message ${type}`;
    div.textContent = text;
    output.appendChild(div);
    output.scrollTop = output.scrollHeight;
}

function updateMenu(message) {
    // Extract commands from "What to do:" section
    const match = message.match(/💡 What to do:([\s\S]*?)$/);
    if (!match) return;

    const lines = match[1].split('\n').filter(line => line.trim().startsWith('•'));
    commands = lines.map(line => {
        const cmdMatch = line.match(/'([^']+)'/);
        return cmdMatch ? cmdMatch[1] : null;
    }).filter(Boolean);

    renderMenu();
}

function renderMenu() {
    menu.innerHTML = '';
    selectedIndex = 0;

    commands.forEach((cmd, i) => {
        const item = document.createElement('div');
        item.className = 'menu-item';
        if (i === 0) item.classList.add('selected');

        // Add emoji based on command
        let emoji = '';
        if (cmd.startsWith('take')) emoji = '📦';
        else if (cmd.startsWith('go')) emoji = '🚶';
        else if (cmd.startsWith('examine')) emoji = '🔍';
        else if (cmd.startsWith('use')) emoji = '🔧';
        else if (cmd === 'inventory') emoji = '🎒';
        else if (cmd === 'look') emoji = '👁️';
        else if (cmd === 'help') emoji = '❓';
        else if (cmd.startsWith('drop')) emoji = '⬇️';

        item.textContent = `${emoji} ${cmd}`;
        item.addEventListener('click', () => selectAndExecute(i));
        menu.appendChild(item);
    });
}

function selectAndExecute(index) {
    if (waiting) return;
    selectedIndex = index;
    updateSelection();
    executeCommand();
}

function updateSelection() {
    const items = menu.querySelectorAll('.menu-item');
    items.forEach((item, i) => {
        item.classList.toggle('selected', i === selectedIndex);
    });
}

function executeCommand() {
    if (waiting || commands.length === 0) return;

    waiting = true;
    const cmd = commands[selectedIndex];

    addOutput(`> ${cmd}`, 'user');

    if (socket && socket.connected) {
        socket.emit('command', { command: cmd });
    } else {
        addOutput('Not connected to server', 'error');
        waiting = false;
    }
}

// Keyboard navigation
document.addEventListener('keydown', (e) => {
    if (loginScreen.classList.contains('hidden') === false) return;
    if (waiting) return;

    if (e.key === 'ArrowUp') {
        e.preventDefault();
        selectedIndex = (selectedIndex - 1 + commands.length) % commands.length;
        updateSelection();
    } else if (e.key === 'ArrowDown') {
        e.preventDefault();
        selectedIndex = (selectedIndex + 1) % commands.length;
        updateSelection();
    } else if (e.key === 'Enter') {
        e.preventDefault();
        executeCommand();
    }
});

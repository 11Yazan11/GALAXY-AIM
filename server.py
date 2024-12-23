import json
import math
import threading
from flask import Flask, send_from_directory, request
from flask_socketio import SocketIO, emit
import time

# Constants
PORT = 3001
TICK_RATE = 60
SPEED = 5

# Game state
game_state = []
all_maps = {
    'default':[
        (-3000, -3000, 6000, 40),
        (-3000, -3000, 40, 6000),
        (-3000, 3000, 6000, 40),
        (3000, -3000, 40, 6000)
    ]
}


# Flask app and SocketIO setup
app = Flask(__name__, static_folder='public')
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")
current_map = 'default'

# Helper functions
def current_time_ms():
    return int(time.time() * 1000)

def add_player(x, y, w, h, color, angle, player_id, name, kills, level):
    game_state.append({
        "x": x, "y": y, "w": w, "h": h,
        "angle": angle, "id": player_id,
        "color": color,
        "name": name, "bullets": [], "kills": kills, 
        'level': level
    })

def remove_player(player_id):
    global game_state
    game_state = [player for player in game_state if player["id"] != player_id]

def send_kills(killer_id, killed_name, killer_name):
    socketio.emit('Kill', [killed_name, killer_name], to=killer_id)

def is_valid(player):
    return not (player["x"] < -2960 or player["x"] + player["w"] > 3000 or 
                player["y"] < -2960 or player["y"] + player["h"] > 3000)

def bullet_handle():
    for player in game_state:
        for bullet in player["bullets"]:
            angle = math.radians(bullet['vector']) 
            dx = math.cos(angle) * SPEED * 4
            dy = -(math.sin(angle) * SPEED * 4)
            bullet["x"] += dx
            bullet["y"] += dy

# Routes
@app.route('/game')
def serve_index():
    return send_from_directory(app.static_folder, 'client.py')

# Socket.IO events for /game namespace
@socketio.on('connect', namespace='/game')
def on_connect():
    player_id = request.sid
    print(f'A player joined the game: {player_id}')

@socketio.on('userdata', namespace='/game')
def on_user_data(data):
    add_player(100, 100, 80, 80, data['color'], 0, request.sid, data['name'], 0, 1)
    socketio.emit('mydata', next((p for p in game_state if p["id"] == request.sid), None), to=request.sid, namespace="/game")
    socketio.sleep(0.1)  # Short delay to ensure all clients are synced
    socketio.emit('gameStateUpdate', {"state": game_state, "timestamp": current_time_ms(), "walls": all_maps[current_map]}, namespace='/game')

@socketio.on('playerAngle', namespace='/game')
def on_player_angle(data):
    player_id = request.sid
    player = next((p for p in game_state if p["id"] == player_id), None)
    if player:
        player['angle'] = data


@socketio.on('playerInput', namespace='/game')
def on_player_input():
    player_id = request.sid
    player = next((p for p in game_state if p["id"] == player_id), None)
    if player:
        angle = math.radians(player['angle']) 
        dx = math.cos(angle) * SPEED
        dy = -(math.sin(angle) * SPEED)

        # Update the player's position
        player['x'] += dx
        player['y'] += dy

        # Ensure the player stays within bounds
        if not is_valid(player):
            player['x'] -= dx
            player['y'] -= dy
            return


@socketio.on('bullet', namespace='/game')
def on_bullet():
    player_id = request.sid  # Get the player ID from the bullet data
    player = next((p for p in game_state if p["id"] == player_id), None)
    if player and len(player["bullets"]) > -1:
        player["bullets"].append({
            "x": player["x"] + math.cos(math.radians(player["angle"])),
            "y": player["y"] - math.sin(math.radians(player["angle"])),
            "r": 10,
            "vector": player["angle"],
            "bounces": 0,
            "ownerId": player["id"]
})


@socketio.on('disconnect', namespace='/game')
def disconnect():
    player_id = request.sid  # Get the player ID from the disconnect data
    print(f'A player left the game: {player_id}')
    remove_player(player_id)



# Game loop
def game_loop():
    while True:
        current_time = current_time_ms()
        for player in game_state:
            socketio.emit('mydata', player, to=player['id'], namespace='/game')  # Send only their data to each player
        
        socketio.emit('gameStateUpdate', {"state": game_state, "timestamp": current_time, "walls": all_maps[current_map]}, namespace='/game')
        bullet_handle()
        socketio.sleep(1 / TICK_RATE)

# Start the server
if __name__ == '__main__':
    threading.Thread(target=game_loop, daemon=True).start()
    socketio.run(app, host='0.0.0.0', port=PORT)

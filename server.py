import json
import math
import threading
from flask import Flask, send_from_directory, request
from flask_socketio import SocketIO, emit

# Constants
PORT = 3001
TICK_RATE = 30
SPEED = 3

# Game state
game_state = []


# Flask app and SocketIO setup
app = Flask(__name__, static_folder='public')
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# Helper functions
def add_player(x, y, w, h, color, angle, player_id, name, kills):
    game_state.append({
        "x": x, "y": y, "w": w, "h": h,
        "angle": angle, "id": player_id,
        "color": color,
        "name": name, "bullets": [], "kills": kills
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
            angle = bullet["vector"]
            dx = math.cos(angle) * SPEED * 5
            dy = math.sin(angle) * SPEED * 5
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
    add_player(100, 100, 40, 40, data['color'], 0, request.sid, data['name'], 0)
    socketio.emit('mydata', next((p for p in game_state if p["id"] == request.sid), None), to=request.sid)



@socketio.on('playerInput', namespace='/game')
def on_player_input(data):
    player_id = request.sid
    player = next((p for p in game_state if p["id"] == player_id), None)
    if player:
        if data.get("left") and is_valid({"x": player["x"] - SPEED, "y": player["y"], "w": player["w"], "h": player["h"]}):
            player["x"] -= SPEED
        elif data.get("right") and is_valid({"x": player["x"] + SPEED, "y": player["y"], "w": player["w"], "h": player["h"]}):
            player["x"] += SPEED
        elif data.get("up") and is_valid({"x": player["x"], "y": player["y"] - SPEED, "w": player["w"], "h": player["h"]}):
            player["y"] -= SPEED
        elif data.get("down") and is_valid({"x": player["x"], "y": player["y"] + SPEED, "w": player["w"], "h": player["h"]}):
            player["y"] += SPEED

@socketio.on('bullet', namespace='/game')
def on_bullet(data):
    player_id = request.sid  # Get the player ID from the bullet data
    player = next((p for p in game_state if p["id"] == player_id), None)
    if player and len(player["bullets"]) < 10:
        player["bullets"].append({
            "x": player["x"] + player["w"] / 2,
            "y": player["y"] + player["h"] / 2,
            "vector": player["angle"],
            "bounces": 0,
            "ownerId": player["id"]
        })

@socketio.on('playerAngle', namespace='/game')
def on_player_angle(data):
    player_id = request.sid  # Get the player ID from the input data
    player = next((p for p in game_state if p["id"] == player_id), None)
    if player:
        player["angle"] = data['angle']

@socketio.on('disconnect', namespace='/game')
def disconnect():
    player_id = request.sid  # Get the player ID from the disconnect data
    print(f'A player left the game: {player_id}')
    remove_player(player_id)



# Game loop
def game_loop():
    while True:
        socketio.emit('gameStateUpdate', game_state, namespace='/game')
        bullet_handle()
        socketio.sleep(1 / TICK_RATE)

# Start the server
if __name__ == '__main__':
    threading.Thread(target=game_loop, daemon=True).start()
    socketio.run(app, host='0.0.0.0', port=PORT)


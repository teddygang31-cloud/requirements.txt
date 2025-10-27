    import websocket
import threading
import time
import json
import requests
from datetime import datetime

# Highrise credentials
HIGHRISE_API_TOKEN = '8ccb1f4f88a3169bde1b8eb5ac810403e53c9e683a30bf40a4a27c2cc9bfb92c'
ROOM_ID = '68fbed190c3d0cf6597a77e5

'

# Replace with actual Highrise WebSocket endpoint
WS_URL = f"wss://websocket.highrise.game/rooms/{ROOM_ID}?apiToken={HIGHRISE_API_TOKEN}"

visitors = {}
moderator_ids = ['YOUR_ID', 'MOD1_ID', 'MOD2_ID']  # Replace with your own and your moderators' IDs

def on_open(ws):
    print('Bot connected to Highrise room!')

    def tip_everyone():
        while True:
            time.sleep(5 * 60)
            for visitor_id in visitors:
                tip_user(visitor_id, 100)
    threading.Thread(target=tip_everyone, daemon=True).start()

def on_message(ws, message):
    try:
        msg = json.loads(message)
    except Exception as e:
        print(f"Failed to parse message: {e}")
        return

    # User joins
    if msg.get('type') == 'user_joined':
        user = msg['user']
        visitors[user['id']] = {'name': user['username'], 'joined': time.time()}
        greet_user(ws, user)

    # User leaves
    elif msg.get('type') == 'user_left':
        user = msg['user']
        if user['id'] in visitors:
            log_leave(ws, user)
            del visitors[user['id']]

    # Chat messages
    elif msg.get('type') == 'chat_message':
        text = msg['message']['text'].lower()
        sender_id = msg['user']['id']

        # Check for flame trigger
        if sender_id in moderator_ids and 'flame' in text:
            send_message(ws, 'Type "flame" in chat now!')
            for visitor_id in visitors:
                tip_user(visitor_id, 5)

        # Music selection
        if 'play music' in text:
            track = pick_music()
            send_message(ws, f'Now playing: {track}')
            # Integrate with music system if needed

def greet_user(ws, user):
    now = datetime.now().strftime("%H:%M:%S")
    send_message(ws, f"Welcome {user['username']} to the room! You joined at {now}.")

def log_leave(ws, user):
    now = datetime.now().strftime("%H:%M:%S")
    send_message(ws, f"{user['username']} left the room at {now}.")

def tip_user(user_id, amount):
    url = f'https://api.highrise.game/rooms/{ROOM_ID}/tip'
    payload = {
        'userId': user_id,
        'amount': amount
    }
    headers = {
        'Authorization': f'Bearer {HIGHRISE_API_TOKEN}'
    }
    try:
        r = requests.post(url, json=payload, headers=headers)
        if r.status_code == 200:
            print(f"Tipped {user_id} {amount} gold.")
        else:
            print(f"Failed to tip {user_id}: {r.text}")
    except Exception as e:
        print(f"Error tipping user: {e}")

def send_message(ws, text):
    payload = {
        'type': 'send_message',
        'text': text
    }
    ws.send(json.dumps(payload))

def pick_music():
    rap = ['Travis Scott', 'Drake', 'Kendrick Lamar']
    kpop = ['BTS', 'BLACKPINK', 'TWICE']
    all_artists = rap + kpop
    import random
    return random.choice(all_artists)

def on_error(ws, error):
    print(f"WebSocket error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("WebSocket closed")

if __name__ == "__main__":
    ws = websocket.WebSocketApp(
        WS_URL,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    try:
        ws.run_forever()
    except KeyboardInterrupt:
        print("Bot shutting down.")
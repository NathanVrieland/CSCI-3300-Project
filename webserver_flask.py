#this does the same thing as the other two webservers, but uses python flask library
import json
import mysql.connector
from flask import Flask, request, send_file
from flask_socketio import SocketIO, emit, send

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
host = "0.0.0.0" # 0.0.0.0 to host publically
port = 80 # 80 is default for http

@app.route('/')
def handle_root():
    with open("index.html", 'r') as index:
        return index.read()

@app.route('/content', methods=['GET'])
def handle_content():
    with open ("messages.txt", "r") as messagefile:
        return messagefile.read()

# websocket methods
@socketio.on('connect') # at the moment just for logging / debuging 
def handle_connect():
    print('websocket Client connected')

@socketio.on('disconnect') # at the moment just for logging / debuging
def handle_disconnect():
    print('websocket Client disconnected')

@socketio.on('message')
def handle_message(message):
    # websocket message will be formatted as arbitrary json strings, so use data["type"] to get type
    data = json.loads(message)
    if data["type"] == "chat":
        print(f"new chat from {data['name']}")
        with open("messages.txt", 'a') as messagefile:
            messagefile.write(f"{data['name']}: {data['message']}\n")
        # the emit's data field could potentially send back a checksum + the new message and the client could decide if it needs to get all the messages or not
        emit('update', {data['name']: data['message']}, broadcast=True) 

if __name__ == '__main__':
    socketio.run(app, port=port, host=host)

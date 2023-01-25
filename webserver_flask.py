#this does the same thing as the other two webservers, but uses python flask library
from flask import Flask, request
from flask_socketio import SocketIO, emit, send

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
host = ""
port = 80

@app.route('/')
def handle_root():
    with open("index.html", 'r') as index:
        return index.read()

@app.route('/message', methods=['POST'])
def handle_message():
    message = request.get_json()
    with open("messages.txt", 'a') as messagefile:
        messagefile.write(f"{message['name']}: {message['message']}\n")
    return "ok"
    emit('u', data, broadcast=True)

@app.route('/content', methods=['GET'])
def handle_content():
    with open ("messages.txt", "r") as messagefile:
        return messagefile.read()

@socketio.on('connect')
def handle_connect():
    print('websocket Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('websocket Client disconnected')

@socketio.on('message')
def handle_message(message):
    if message == 'update':
        print(f"Websocket message: {message}")
        emit('update', {'data': "nm"}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, port=80, host="0.0.0.0")
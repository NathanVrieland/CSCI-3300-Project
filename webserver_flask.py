from flask import Flask, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

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

@app.route('/content', methods=['GET'])
def handle_content():
    with open ("messages.txt", "r") as messagefile:
        return messagefile.read()

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    socketio.run(app)
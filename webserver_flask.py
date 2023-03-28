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

mydb = mysql.connector.connect(
  host="localhost",                              # Default host
  user="admin",                                   # Default user
  password="software_savants",                     # Replace with your password
  database="APP"                                   # If you want to connect to a specific database
)


@app.route('/')
def handle_root():
    with open("index.html", 'r') as index:
        return index.read()

@app.route('/content', methods=['GET'])
def handle_content():
    global mydb
    chat = "main_chat"
    content = [] # list to build into chat
    cursor = mydb.cursor()
    userlookup = mydb.cursor()
    cursor.execute(f"SELECT * FROM {chat}")
    for i in cursor.fetchall():
        userlookup.execute(f"SELECT Name FROM users where ID={i[3]}")
        content.append(f"{userlookup.fetchall()[0][0]} on {i[2]}: {i[1]}")
    return "".join(content)
    

# websocket methods
@socketio.on('connect') # at the moment just for logging / debuging 
def handle_connect():
    print('websocket Client connected')

@socketio.on('disconnect') # at the moment just for logging / debuging
def handle_disconnect():
    print('websocket Client disconnected')

@socketio.on('message')
def handle_message(message):
    global mydb
    # websocket message will be formatted as arbitrary json strings, so use data["type"] to get type
    data = json.loads(message)
    if data["type"] == "chat":
        userlookup = mydb.cursor()
        userlookup.execute(f"SELECT ID FROM users where Name='{data['name']}'")
        print(f"user {userlookup.fetchall()[0][0]} sent a message")
        print(f"new chat from {data['name']}")
        # with open("messages.txt", 'a') as messagefile:
        #     messagefile.write(f"{data['name']}: {data['message']}\n")
        # the emit's data field could potentially send back a checksum + the new message and the client could decide if it needs to get all the messages or not
        emit('update', {data['name']: data['message']}, broadcast=True) 

if __name__ == '__main__':
    socketio.run(app, port=port, host=host)

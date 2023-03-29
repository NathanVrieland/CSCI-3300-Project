#this does the same thing as the other two webservers, but uses python flask library
import json
import mysql.connector
from flask import Flask, request, send_file
from flask_socketio import SocketIO, emit, send
from auth import Login

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
host = "0.0.0.0" # 0.0.0.0 to host publically
port = 80 # 80 is default for http

mydb = mysql.connector.connect(
  host="localhost",                              # Default host
  user="APP",                                   # Default user
  password="password",                     # Replace with your password
  database="APP"                                   # If you want to connect to a specific database
)

print(type(mydb))

@app.route('/')
def handle_root():
    #TODO check if the client has username browser cookies, and serve login if they do not
    with open("index.html", 'r') as index:
        return index.read()

@app.route('/login')
def handle_root():
    with open("login.html", 'r') as index:
        return index.read()
      
@app.route('/authenticate', methods=['POST'])
def authenticate():
    # gets data from login.html
    json_data = request.get_json()
    username = json_data['username']
    password = json_data['password']
    mycursor = mydb.cursor()
    login_obj = Login(mycursor, username, password)
    if login_obj.is_user() and login_obj.get_match():
        pass
        '''
        calls handle_root() or whatever method we are using for the actual chat
        need some way to pass user account details
        '''

@app.route('/content', methods=['GET'])
def handle_content():
    global mydb
    chat = "main_chat"
    content = [] # list to build into chat
    cursor = mydb.cursor()
    userlookup = mydb.cursor()
    print(type(cursor))
    cursor.execute(f"SELECT * FROM {chat}")
    for i in cursor.fetchall():
        userlookup.execute(f"SELECT Name FROM users where ID={i[3]}")
        content.append(f"{userlookup.fetchall()[0][0]} on {i[2]}: {i[1]}\n")
    userlookup.close()
    cursor.close()
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
        message_adder = mydb.cursor()
        # lookup user 
        userlookup.execute(f"SELECT ID FROM users where Name='{data['name']}'")
        try: # make sure the user exists and return if not
            userID = userlookup.fetchall()[0][0] # fetchall() returns a list of tupeles, so we just need [0][0]
            print(f"user {userID} ({data['name']}) sent a message")
            userlookup.close()
        except IndexError:
            print(f"user {data['name']} not found")
            message_adder.close()
            userlookup.close()
            return
        
        message_adder.execute(f"INSERT INTO main_chat (message, userID) VALUES ('{data['message']}', {userID});")
        message_adder.close()
        mydb.commit() # this pushes changes to the database 
        emit('update', {data['name']: data['message']}, broadcast=True) 

if __name__ == '__main__':
    socketio.run(app, port=port, host=host)

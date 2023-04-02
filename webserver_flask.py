#this does the same thing as the other two webservers, but uses python flask library
import json
import mysql.connector
import random
from flask import Flask, request, send_file, make_response, abort
from flask_socketio import SocketIO, emit, send
from auth import Login, Signup


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


@app.route('/')
def handle_root():
    #TODO check if the client has username browser cookies, and serve login if they do not
    with open("index.html", 'r') as index:
        return index.read()

      
@app.route('/login', methods=["GET"])
def handle_login():
    with open("login.html", 'r') as index:
        return index.read()

      
  
@app.route('/signup', methods=['POST'])
def auth_signup():
    global mydb
    print("\033[92m###### got signup request ######\033[0m")
    json_data = request.get_json()
    username = json_data['username']
    password = json_data['password']
    print(f"\033[92m###### {username=} {password=} ######\033[0m")
    signup_obj = Signup(mydb, username, password)
    newcookie = signup_obj.signup()     # creates new user account
    resp = make_response("creating new user")
    resp.set_cookie('login', newcookie)

    cursor = mydb.cursor()
    cursor.execute(f"UPDATE users SET browser_cookie = {newcookie} WHERE name = '{username}'")
    cursor.commit()
    return resp


@app.route('/login', methods=['POST'])
def auth_login():
    global mydb
    print("\033[92m###### got login request ######\033[0m")
    # gets data from login.html
    json_data = request.get_json()
    username = json_data['username']
    password = json_data['password']
    print(f"\033[92m###### {username=} {password=} ######\033[0m")
    login_obj = Login(mydb, username, password)
    login_return = login_obj.login()
    if login_return:
        newcookie = str(random.randint(0, 99999999999999))
        resp = make_response("setting a cookie")
        resp.set_cookie('login', newcookie)
        cursor = mydb.cursor()
        cursor.execute(f"UPDATE users SET browser_cookie = {newcookie} WHERE ID = {login_return}")
        cursor.close()
        mydb.commit()
        return resp
    else:
        abort(403)
    return "ok"

    
@app.route('/content/', methods=['GET'])
def handle_content():
    global mydb
    groupchat = request.args.get("groupchat")
    content = [] # list to build into chat
    cursor = mydb.cursor()
    userlookup = mydb.cursor()
    cursor.execute(f"SELECT * FROM messages where groupchat={groupchat}")
    for i in cursor.fetchall():
        userlookup.execute(f"SELECT Name FROM users where ID={i[3]}")
        content.append(f"{userlookup.fetchall()[0][0]} on {i[2].strftime('%a, %b %d')}: {i[1]}\n")
        print(type(i[2]))
    userlookup.close()
    cursor.close()
    return "".join(content)
    
    
@app.route('/groups/', methods=['GET'])
def handle_groups():
    global mydb
    user_name = request.args.get("user")
    cursor = mydb.cursor()
    cursor.execute(f"select g.ID, g.Name from is_in join users u on is_in.user_ID = u.ID join groupchats g on g.ID = is_in.chat_ID where u.browser_cookie = '{request.cookies.get('login')}'")
    return cursor.fetchall()

  
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
        userlookup.execute(f"SELECT ID FROM users where browser_cookie='{request.cookies.get('login')}'")
        try: # make sure the user exists and return if not
            userID = userlookup.fetchall()[0][0] # fetchall() returns a list of tupeles, so we just need [0][0]
            print(f"user {userID} sent a message")
            userlookup.close()
        except IndexError:
            print(f"user not found")
            message_adder.close()
            userlookup.close()
            return
        
        message_adder.execute(f"INSERT INTO messages (message, userID, groupchat) VALUES ('{data['message']}', {userID}, {data['groupchat']});")
        message_adder.close()
        mydb.commit() # this pushes changes to the database 
        emit('update', {"user": data['message']}, broadcast=True) 

if __name__ == '__main__':
    socketio.run(app, port=port, host=host)

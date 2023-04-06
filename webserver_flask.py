#this does the same thing as the other two webservers, but uses python flask library
import json
import mysql.connector
import random
from lookups import cookieExists
from groupchat import Groupchat, Newchat
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
    '''
        handles requests at path '/' and serves index.html
    '''
    global mydb
    if cookieExists(mydb, sanitize(request.cookies.get('login'))):
        with open("index.html", 'r') as index:
            return index.read()
    else:
        with open("login.html", 'r') as index:
            return index.read()

      
@app.route('/login', methods=["GET"])
def handle_login():
    '''
        handles GET requests at path '/login' and serves login.html
    '''
    with open("login.html", 'r') as index:
        return index.read()

      
  
@app.route('/signup', methods=['POST'])
def auth_signup():
    '''
        handles requests at path '/signup'
        adds new user to database, calls signup class, and assigns browser cookies to user
    '''
    # parse JSON for username and password
    print("\033[92m###### got signup request ######\033[0m")
    json_data = request.get_json()
    username = sanitize(json_data['username'])
    password = sanitize(json_data['password'])
    print(f"\033[92m###### {username=} {password=} ######\033[0m")
    # create new user and return its browser cookie
    signup_obj = Signup(mydb, username, password)
    cookie = signup_obj.signup()     # creates new user account
    # create an HTML response that will tell the browser to store user cookie
    resp = make_response("creating new user")
    resp.set_cookie('login', cookie)
    return resp


@app.route('/login', methods=['POST'])
def auth_login():
    '''
        handles POST requests at path '/login' 
        calls login object to check if the user has entered correct username and password
        if so, gives client new browser cookie and saves it to the database 
    '''
    global mydb
    print("\033[92m###### got login request ######\033[0m")
    # gets data from login.html
    json_data = request.get_json()
    username = sanitize(json_data['username'])
    password = sanitize(json_data['password'])
    print(f"\033[92m###### {username=} {password=} ######\033[0m")
    login_obj = Login(mydb, username, password)
    cookie = login_obj.login()
    if cookie:
        resp = make_response("setting a cookie")
        resp.set_cookie('login', cookie)
        return resp
    else:
        abort(403)
    return "ok"

    
@app.route('/content/', methods=['GET'])
def handle_content():
    '''
        handles requests at path '/content/'
        queries the database for messages at the desired groupchat 
        builds the messages returned from the groupchat into a large string to be sent to the client
    '''
    global mydb
    groupchat = request.args.get("groupchat")
    if groupchat == '':
        abort(404)
    content = [] # list to build into chat
    cursor = mydb.cursor()
    userlookup = mydb.cursor()
    cursor.execute(f"SELECT * FROM messages where groupchat={groupchat}")
    for i in cursor.fetchall():
        userlookup.execute(f"SELECT Name FROM users where ID={i[3]}")
        content.append(f"{i[2].strftime('%m/%d/%Y, %H:%M:%S')} - {userlookup.fetchall()[0][0]}:\t{i[1]}\n")
    userlookup.close()
    cursor.close()
    return "".join(content)
    
    
@app.route('/groups/', methods=['GET'])
def handle_groups():
    '''
        handles requests at path '/groups/' 
        simply returns an an array of arrays that contain groupchat ID's followed by groupchat names
    '''
    global mydb
    # user_name = request.args.get("user")
    cursor = mydb.cursor()
    cursor.execute(f"select g.ID, g.Name from is_in join users u on is_in.user_ID = u.ID join groupchats g on g.ID = is_in.chat_ID where u.browser_cookie = '{request.cookies.get('login')}'")
    return cursor.fetchall()

@app.route('/adduser', methods=["POST"])
def handle_adduser():
    global mydb
    json_data = request.get_json()
    groupchat = sanitize(json_data["groupchat"])
    user = sanitize(json_data["user"])  
    mygroup = Groupchat(mydb, groupchat)
    mygroup.addUser(user)
    return "ok"

@app.route('/addgroup', methods=["POST"])
def handle_addgroup():
    print("\033[96m#### adding group ####\033[0m")
    global mydb
    json_data = request.get_json()
    groupname = sanitize(json_data["groupname"])
    mygroup = Newchat(mydb, groupname)
    mygroup.addCookie(request.cookies.get('login'))
    return "ok"

# websocket methods
@socketio.on('connect') # at the moment just for logging / debuging 
def handle_connect():
    print('websocket Client connected')

    
@socketio.on('disconnect') # at the moment just for logging / debuging
def handle_disconnect():
    print('websocket Client disconnected')

    
@socketio.on('message')
def handle_message(message):
    '''
    websocket method that is called whenever a user sends a message
    message is recieved from client as a JSON object, and is inserted into database 
    also calls emit() which pings all other connected websocket clients
    pinged clients then update their list of messages
    '''
    global mydb
    # websocket message will be formatted as arbitrary json strings, so use data["type"] to get type
    data = sanitize(json.loads(message))
    if data["type"] == "chat":
        userlookup = mydb.cursor()
        message_adder = mydb.cursor()
        # lookup user 
        cookie = sanitize(request.cookies.get('login'))
        userlookup.execute(f"SELECT ID FROM users where browser_cookie='{cookie}'")
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


# Basic input sanitization
def sanitize(input: str) -> str:
    escapes = ['--', ';', '=']
    for i in escapes:
        if i in input:
            input = input.replace(i, '')
    return input


if __name__ == '__main__':
    socketio.run(app, port=port, host=host)

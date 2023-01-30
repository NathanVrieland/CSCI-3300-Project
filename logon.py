"""
This is a very basic concept to show how we can log in by checking credentials with a json file
Later I will check out the html and look at how to integrate this with the server, which should be no big trouble
-Luke
"""

import json


# Called to append changes to json file
def write_json(data, filename='logon.json'):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)


def signup(username: str = None):
    if username is None:
        username = input('Enter a username: ')
    with open('logon.json') as json_file:
        data = json.load(json_file)
        temp = data['logins']
        for entry in temp:
            if username not in entry.values():
                password = input('Enter a password: ')
                y = {'username': username, 'password': password}
                temp.append(y)
                write_json(data)
                return
        choice = input('Username already exists, login with this username? (y/n ) ')
        if choice[0] == 'y':
            login(username)


def login(username: str = None):
    if username is None:
        username = input('Enter your username: ')
    with open('logon.json') as json_file:
        data = json.load(json_file)
        temp = data['logins']
        for entry in temp:
            if username in entry.values():
                password = input('Enter your password: ')
                if entry['password'] == password:
                    print(f'Logged in as {username}')
                    return
                else:
                    print('Wrong password, try again')
        choice = input('Username not found, create new account with this username? (y/n) ')
        if choice[0] == 'y':
            signup(username)


select = input('Log in or sign up? (l/s) ')
if select[0] == 's':
    signup()
else:
    login()

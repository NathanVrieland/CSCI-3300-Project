import os
import hashlib
import random
import datetime
import mysql.connector
from flask import redirect


# this is a comment
# parent class for authenticating
class Authenticator:

    def __init__(self, db, username: str, password: str):
        self.db = db
        self.cursor = self.db.cursor()
        self.username = username
        self.password = password

    # returns true if there is a name of username in the user table
    def is_user(self) -> bool:
        self.cursor.execute(f'SELECT name FROM users WHERE name = "{self.username}"')
        # checks if anything was fetched
        if len(self.cursor.fetchone()) != 0:
            return True
        else:
            return False


# parent class for getting information from existing users
class Existing_user:

    def __init__(self, db, username: str):
        self.db = db
        self.cursor = self.db.cursor()
        self.username = username
        self.id = self.get_id()

    # returns id from database as string
    def get_id(self) -> str:
        self.cursor.execute(f'SELECT ID from users WHERE name = "{self.username}"')
        id = self.cursor.fetchone()[0]
        return id

    def get_salt(self) -> str:
        self.cursor.execute(f'SELECT salt FROM users WHERE ID = {self.id}')
        salt = self.cursor.fetchone()[0]
        return salt


# signup handler
class Signup(Authenticator):
    def __init__(self, db, username: str, password: str):
        super().__init__(db, username, password)

    def signup(self):
        new_cookie = generate_cookie(self.cursor)
        salt = os.urandom(32).hex()
        key = generate_key(self.password, salt)
        print(f'\033[92m###### Signup.signup() key: {key}, salt: {salt} ######\033[0m')
        self.cursor.execute(f"INSERT INTO users (name, password, browser_cookie, salt) VALUES ('{self.username}', '{key}', '{new_cookie}', '{salt}')")
        self.db.commit()
        redirect('/login.html', code=302)
        return new_cookie


# login handler
class Login(Authenticator, Existing_user):

    def __init__(self, db, username: str, password: str):
        Authenticator.__init__(self, db, username, password)
        Existing_user.__init__(self, db, username)
        salt = self.get_salt()
        self.key = generate_key(self.password, salt)
        print(f'\033[92m###### Login.__init__() salt: {salt} ######\033[0m')

    # checks that key matches key in database
    def is_match(self) -> bool:
        self.cursor.execute(f'SELECT password FROM users WHERE name = "{self.username}"')
        password = self.cursor.fetchone()[0]
        print(f'\033[92m###### Login.is_match() self.key: {self.key}, password: {password} ######\033[0m')
        # compares key as a string to the password in database
        if self.key == password:
            return True
        else:
            return False

    def login(self) -> int | bool:
        if self.is_user():
            if self.is_match():
                print(f'\033[92m###### success ######\033[0m')
                # redirect(location='/index.html', code=302)
                # TODO: send request with user information
                return self.id
            else:
                print(f'\033[92m###### fail ######\033[0m')
                # redirect(location='/login.html', code=403)
                # TODO: send request that password was bad
                return False
        else:
            # redirect(location='/login.html', code=403)
            # TODO: send request that user does not exist
            return False


# a login object should be called and used before creating an Acc_change object
class Acc_change(Existing_user):

    def __init__(self, cursor, user_id: str, username: str, password: str):
        super().__init__(cursor, username)
        self.cursor = cursor
        self.user_id = user_id
        self.username = username
        self.password = password

    # changes username
    def change_username(self, new_username) -> None:
        self.cursor.execute(f'UPDATE user SET name = "{new_username}" WHERE ID = {self.user_id}')
        self.db.commit()

    # changes password
    def change_password(self, new_password) -> None:
        salt = generate_salt(self.cursor)
        key = generate_key(new_password, salt)
        self.cursor.execute(f'UPDATE user SET password = {key}, salt = {salt}, WHERE ID = {self.user_id}')
        self.db.commit()


# generates new salt
def generate_salt(cursor) -> str:
    salt = os.urandom(32).hex()
    cursor.execute(f'SELECT salt from users WHERE salt = {salt}')
    collision = cursor.fetchone()
    # fetchone() returns a NoneType if there is no match in the database
    if collision is None:
        return salt
    else:
        return generate_salt(cursor)

    
# generates new cookie
def generate_cookie(cursor) -> str:
    cookie = f'{random.randint(0, 1000000):06}'
    cursor.execute(f'SELECT browser_cookie from users WHERE browser_cookie = {cookie}')
    collision = cursor.fetchone()
    # fetchone() returns a NoneType if there is no match in the database
    if collision is None:
        return cookie
    else:
        return generate_cookie(cursor)


# generates new key
def generate_key(password: str, salt: str) -> str:
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return key.hex()

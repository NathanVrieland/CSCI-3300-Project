import os
import hashlib
import mysql.connector
from flask import redirect


# parent class for authenticating
class Authenticator:

    def __init__(self, db, username: str, password: str):
        self.db = db
        self.cursor = self.db.cursor()
        self.username = username
        self.password = password

    # returns true if there is a name of username in the user table
    def is_user(self) -> bool:
        self.cursor.execute(f'SELECT Name FROM users WHERE Name = "{self.username}"')
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
        self.cursor.execute(f'SELECT ID from users WHERE Name = "{self.username}"')
        id = self.cursor.fetchone()[0]
        return id

    def get_salt(self) -> bytes:
        self.cursor.execute(f'SELECT salt FROM users WHERE ID = "{self.id}"')
        salt = self.cursor.fetchone()[0]
        return salt.encode('utf-8')


# signup handler
class Signup(Authenticator):
    def __init__(self, db, username: str, password: str):
        super().__init__(db, username, password)

    def signup(self):
        salt = os.urandom(32)
        key = generate_key(self.password, salt)
        self.cursor.execute(f'INSERT INTO users VALUES ("{self.username}", "{key}", "{salt}")')
        self.db.commit()
        redirect('/login.html', code=302)


# login handler
class Login(Authenticator, Existing_user):

    def __init__(self, db, username: str, password: str):
        Authenticator.__init__(self, db, username, password)
        Existing_user.__init__(self, db, username)
        salt = self.get_salt()
        self.key = generate_key(self.password, salt)

    # checks that key matches key in database
    def is_match(self) -> bool:
        self.cursor.execute(f'SELECT password FROM users WHERE Name = "{self.username}"')
        password = self.cursor.fetchone()[0]
        print(f'Key: {self.key}\nPassword: {[password]}')
        self.cursor.execute(f'UPDATE users SET password = "{generate_key(password, self.get_salt())}", salt = "{generate_salt(self.cursor)}" WHERE Name = "{self.username}"')
        self.db.commit()
        # compares key as a string to the password in database
        if self.password == password:
            return True
        else:
            return False

    def login(self) -> None:
        if self.is_user():
            if self.is_match():
                print("********** success **********")
                # redirect(location='/index.html', code=302)
                # TODO: send request with user information
            else:
                print("********** fail **********")
                # redirect(location='/login.html', code=403)
                # TODO: send request that password was bad
        else:
            redirect(location='/login.html', code=403)
            # TODO: send request that user does not exist


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
        self.cursor.execute(f'UPDATE user SET Name = "{new_username}" WHERE ID = {self.user_id}')
        self.db.commit()

    # changes password
    def change_password(self, new_password) -> None:
        salt = generate_salt(self.cursor)
        key = generate_key(new_password, salt)
        self.cursor.execute(f'UPDATE user SET Password = {key}, Salt = {salt}, WHERE ID = {self.user_id}')
        self.db.commit()


# generates new salt
def generate_salt(cursor) -> bytes:
    salt = os.urandom(32)
    cursor.execute(f'SELECT Salt from users WHERE Salt = {salt}')
    collision = cursor.fetchone()
    if len(collision) == 0:
        return salt
    else:
        return generate_salt(cursor)


# generates new key
def generate_key(password: str, salt: bytes) -> str:
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return key.hex()

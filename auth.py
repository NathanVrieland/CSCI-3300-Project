import json
import hashlib
import mysql.connector


class Login:
    def __init__(self, cursor: mysql.connector.connect().cursor(), username: str, password: str):
        self.cursor = cursor
        self.username = username
        self.key = get_key(username, password)

    # checks if username is in the database
    def is_user(self) -> bool:
        self.cursor.execute(f'SELECT Name FROM users WHERE Name={self.username}')
        # checks if anything was fetched
        if len(self.cursor.fetchone()) != 0:
            return True
        else:
            return False

    # checks that key matches key in database
    def get_match(self):
        self.cursor.execute(f'SELECT password FROM users WHERE Name={self.username}')
        password = self.cursor.fetchone()[0]
        # compares key as a string to the password in database
        if self.key.decode() == password:
            return True
        else:
            return False


# returns a key, which is the password hashed with salt
def get_key(username: str, password: str) -> bytes:
    # finds appropriate salt
    with open('login.json') as json_file:
        data = json.load(json_file)['logins']
        for entry in data:
            if username == entry:
                salt = entry['salt']
                # uses password-based key derivation function 2 to derive a key
                key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
                return key

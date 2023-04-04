from lookups import userID_from_name, groupchatID_fom_name, groupchatName_from_ID, userID_from_cookie
import mysql.connector
class Groupchat():

    def __init__(self, database, ID):
        self.ID = ID
        self.database = database
        self.name = ""
        cursor = self.database.cursor()
        cursor.execute(f"SELECT name FROM groupchats WHERE ID={self.ID}")
        self.name = cursor.fetchone()[0]

    def addUser(self, username):
        cursor = self.database.cursor()
        userID = userID_from_name(self.database, username)
        cursor.execute(f"INSERT INTO is_in values ({userID}, {self.ID})")
        self.database.commit()
    
    def removeUser(self, username):
        cursor = self.database.cursor()
        userID = userID_from_name(self.database, username)
        cursor.execute(f"DELETE FROM is_in WHERE user_ID={userID} and chat_ID={self.ID}")
        self.database.commit()

    def addCookie(self, cookie):
        cursor = self.database.cursor()
        userID = userID_from_cookie(self.database, cookie)
        cursor.execute(f"INSERT INTO is_in values ({userID}, {self.ID})")
        self.database.commit()

class Newchat(Groupchat):
    
    def __init__(self, database, name):
        # add new groupchat to database 
        cursor = database.cursor()
        cursor.execute(f"INSERT INTO groupchats (name) VALUE ('{name}')")
        database.commit()
        super().__init__(database, groupchatID_fom_name(database, name))



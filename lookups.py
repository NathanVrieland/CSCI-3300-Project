import mysql.connector

# lookups for users 
def userID_from_name(database, name):
    userlookup = database.cursor()
    userlookup.execute(f"SELECT ID from users where name='{name}'")
    return userlookup.fetchone()[0]

def userID_from_cookie(database, cookie):
    userlookup = database.cursor()
    userlookup.execute(f"SELECT ID from users WHERE browser_cookie={cookie}")
    return userlookup.fetchone()[0]

def cookieExists(database, cookie):
    userlookup = database.cursor()
    userlookup.execute(f"SELECT ID from users WHERE browser_cookie={cookie}")
    if userlookup.fetchone() == None:
        return False
    return True
    
# lookups for groups 
def groupchatID_fom_name(database, name):
    grouplookup = database.cursor()
    grouplookup.execute(f"SELECT ID from groupchats WHERE name='{name}'")
    return grouplookup.fetchone()[0]

def groupchatName_from_ID(database, ID):
    grouplookup = database.cursor()
    grouplookup.execute(f"SELECT name from groupchats WHERE ID={ID}")
    return grouplookup.fetchone()[0]


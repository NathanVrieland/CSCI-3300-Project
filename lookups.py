import mysql.connector
def userID_from_name(database, name):
    userlookup = database.cursor()
    userlookup.execute(f"SELECT ID from users where name='{name}'")
    return userlookup.fetchone()[0]

def groupchatID_fom_name(database, name):
    grouplookup = database.cursor()
    grouplookup.execute(f"SELECT ID from groupchats WHERE name='{name}'")
    return grouplookup.fetchone()[0]

def groupchatName_from_ID(database, ID):
    grouplookup = database.cursor()
    grouplookup.execute(f"SELECT name from groupchats WHERE ID={ID}")
    return grouplookup.fetchone()[0]
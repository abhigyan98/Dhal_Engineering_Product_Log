import sqlite3

con = sqlite3.connect('list.db', check_same_thread=False)
db = con.cursor()

def createUser(uid,name,email,password,active):
    db.execute("INSERT INTO user VALUES (?,?,?,?,?)",(uid,name,email,password,active))
    con.commit()

def getPasswordForLogin(email):
    db.execute("SELECT uid,password,active FROM user WHERE email=(?)",(email,))
    data = db.fetchall()
    return data

def getUser(uid):
    db.execute("SELECT * FROM user WHERE uid=(?)",(uid,))
    user = db.fetchall()
    return user

def getAllUserEmail():
    db.execute("SELECT email FROM user")
    email = db.fetchall()
    return email

def updateUserActivation(uid,active):
    db.execute("UPDATE user SET active=(?) WHERE uid=(?)",(active,uid))
    con.commit()
#createTable()
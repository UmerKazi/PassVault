import sqlite3
from cryptography.fernet import Fernet

key = "Be1PA8snHgb1DS6oaWek62WLE9nxipFw3o3vB4uJ8ZI="
cipher_suite = Fernet(key)

def conectionDB(func):
    def wrapper(*args, **kwargs):
        global myConection
        global myCursor
        myConection = sqlite3.connect("PasswordsDB")
        myCursor = myConection.cursor()

        result = func(*args, **kwargs)

        myConection.commit()
        myConection.close()

        return result
    return wrapper


@conectionDB
def createDB():
    try:
        myCursor.execute('''
            CREATE TABLE USERS (
            USER VARCHAR(17) UNIQUE,
            PASSWORD VARCHAR(17))
            ''')

        myCursor.execute('''
            CREATE TABLE PASSWORDS_DATA (
            USER VARCHAR(17),
            NAME VARCHAR (17),
            PASSWORD VARCHAR(17),
            NOTES VARCHAR(100))
            ''')

    except sqlite3.OperationalError:
        pass

@conectionDB
def loginUser(user, password):
    myCursor.execute("SELECT PASSWORD FROM USERS WHERE USER='"+user+"'")
    passwordDB = myCursor.fetchall()

    try:
        passwordDB = cipher_suite.decrypt(passwordDB[0][0])
        passwordDB = passwordDB.decode("utf-8")
        if passwordDB == password:
            return "yes"
        else:
            return "no"

    except IndexError:
        return "error"


@conectionDB
def createUser(user, password):
    password = cipher_suite.encrypt(bytes(password, encoding='utf-8'))
    data = (user, password)
    myCursor.execute("INSERT INTO USERS VALUES(?,?)", data)


@conectionDB
def insertPasswordData(user, name, password, notes):
    password = cipher_suite.encrypt(bytes(password, encoding='utf-8'))
    data = (user, name, password, notes)
    myCursor.execute("INSERT INTO PASSWORDS_DATA VALUES(?,?,?,?)", data)


@conectionDB
def readPasswords(user):
    myCursor.execute("SELECT NAME,PASSWORD,NOTES FROM PASSWORDS_DATA WHERE USER='"+user+"'")
    passwords = myCursor.fetchall()
    return passwords


@conectionDB
def deletePassword(user, name):
    myCursor.execute("DELETE FROM PASSWORDS_DATA WHERE USER='"+user+"' AND NAME='"+name+"'")


@conectionDB
def readNotes(user, name):
    myCursor.execute("SELECT NOTES FROM PASSWORDS_DATA WHERE USER='"+user+"' AND NAME='"+name+"'")
    notes = myCursor.fetchall()

    return notes

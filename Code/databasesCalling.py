""" THIS IS FOR DATABASES"""
import urllib2
import json
import sqlite3, time
import urllib


def getLinkInformation(function,user, details):
    """most important function as it returns the response of a link opened"""

    database = sqlite3.connect('Information.db')
    cursor = database.cursor()
    cursor.execute("SELECT IP, PORT FROM USERS WHERE USERNAME= ?",
                    (user,))
    row = cursor.fetchone()
    url = 'http://' + str(row[0]) + ':' + str(row[1]) + function
    details = json.dumps(details)
    req = urllib2.Request(url,details,  {'Content-Type': 'application/json'})
    response = urllib2.urlopen(req, timeout=3)
    response = response.read()
    database.close()
    return response

def updateStatusInformation(status,user):
    """update status"""
    database = sqlite3.connect('Information.db')
    cursor = database.cursor()
    cursor.execute("UPDATE USERS SET ONLINE = ? WHERE USERNAME = ?", (status, user))
    database.commit()
    database.close()

def updateUserInformation(location,ip,port,lastlogin,online,username):
    """update users"""
    database = sqlite3.connect('Information.db')
    cursor = database.cursor()
    cursor.execute("UPDATE USERS  SET LOCATION = ?, IP = ?, PORT = ?, LASTLOGIN = ?, ONLINE = ? WHERE USERNAME = ? ",
                    (location, ip, port, lastlogin,online,username))
    database.commit()
    database.close()


def insertUsers(username):
    """insert into users"""
    database = sqlite3.connect('Information.db')
    cursor = database.cursor()
    cursor.execute("INSERT OR REPLACE INTO USERS (USERNAME) values (?) ",
                    (username,))
    database.commit()
    database.close()


def updateName(user):
    """update name in profile"""
    database = sqlite3.connect('Information.db')
    cursor = database.cursor()
    cursor.execute("INSERT OR REPLACE INTO PROFILE (FULLNAME, USERNAME) values (?,?)", (user,user))
    database.commit()
    database.close()

def updateUserCredentials(username,password, tfa): 
    """update credentials"""
    database = sqlite3.connect('Information.db')
    cursor = database.cursor()
    cursor.execute("INSERT into SERVER (USERNAME, PASSWORD, TFA) values (?,?, ?)", (username,password,tfa))
    database.commit()
    database.close()

def updateThreading(username, Thread): 
    """update threading details"""
    database = sqlite3.connect('Information.db')
    cursor = database.cursor()
    cursor.execute("UPDATE SERVER SET THREADING = ? WHERE USERNAME = ?", (Thread,username))
    database.commit()
    database.close()

def updateActiveUser(username, active): 
    """update the active user"""
    database = sqlite3.connect('Information.db')
    cursor = database.cursor()
    cursor.execute("UPDATE SERVER SET ACTIVEUSER = ? WHERE USERNAME = ?", (active,username))
    database.commit()
    database.close()
    
def checkifUserExists(username):
    """check for whether the client already exists in the server"""
    serverList = returnServer()
    for key in serverList:
        if (key == username):
            return True
        else:
            return False

def returnActiveUser(username): 
    """return active user """
    database = sqlite3.connect('Information.db')
    cursor = database.cursor()
    cursor.execute("SELECT ACTIVEUSER FROM SERVER WHERE USERNAME = ?", (username,))
    row = cursor.fetchone()
    activeUser = row[0]
    database.close()
    return activeUser 

def returnPassword(username): 
    """return password"""
    database = sqlite3.connect('Information.db')
    cursor = database.cursor()
    cursor.execute("SELECT PASSWORD FROM SERVER WHERE USERNAME = ?", (username,))
    row = cursor.fetchone()
    password = row[0]
    database.close()
    return password 

def returnTFA(username): 
    """return two factor authentication details"""
    database = sqlite3.connect('Information.db')
    cursor = database.cursor()
    cursor.execute("SELECT TFA FROM SERVER WHERE USERNAME = ?", (username,))
    row = cursor.fetchone()
    tfa = row[0]
    database.close()
    return tfa

def returnThread(username): 
    """return thread status"""
    database = sqlite3.connect('Information.db')
    cursor = database.cursor()
    try:
        cursor.execute("SELECT THREADING FROM SERVER WHERE USERNAME = ?", (username,))
        row = cursor.fetchone()
        thread = row[0]
    except:
        thread = False
    database.close()
    return thread


def logoutOfServer():
    """logout of the server"""
    database = sqlite3.connect('Information.db')
    cursor = database.cursor()
    cursor = database.execute("SELECT * from SERVER")
    for row in cursor:
        url = 'http://cs302.pythonanywhere.com/logoff'
        values = {'username' : row[0],'password' : row[1]}
        data = urllib.urlencode(values)
        full_url = url + '?' + data
        information = urllib2.urlopen(full_url)
        result = information.read()
        print result
    database.commit()
    database.close()

def deleteFromDatabase(user):
    """delete user from database"""
    database = sqlite3.connect('Information.db')
    cursor = database.cursor()
    cursor = database.execute("DELETE FROM SERVER WHERE USERNAME = ?", (user,))
    database.commit()
    database.close()

def returnProfile():
    """return profile as a dictionary"""
    database = sqlite3.connect('Information.db')
    cursor = database.cursor()
    cursor = database.execute("SELECT * from PROFILE")
    userDict = {}
    for row in cursor: 
        userDict[row[8]] = {'fullname' : row[0],
                            'position' : row[1],
                            'description' : row[2],
                            'location' : row[3],
                            'picture' : row[4]}
    database.close()
    return userDict     

def returnServer():
    """return server as a dictionary"""
    database = sqlite3.connect('Information.db')
    cursor = database.cursor()
    cursor = database.execute("SELECT * from SERVER")
    userDict = {}
    for row in cursor: 
        userDict[row[0]] = {'password' : row[1],
                            'threading' : row[2],
                            'active' : row[3],
                            'tfa' : row[4]}
    database.close()
    return userDict     

def returnEvent():
    """return event as a dictionary"""
    database = sqlite3.connect('Information.db')
    cursor = database.cursor()
    cursor = database.execute("SELECT * from EVENTS")
    userDict = {}
    for row in cursor: 
        userDict[row[1]] = {
                            'sender' : row[2],
                            'destination' : row[3],
                            'event_name' : row[4],
                            'event_description' : row[5],
                            'event_location' : row[6],
                            'event_picture' : row[7],
                            'start_time' : row[8],
                            'end_time' : row[9],
                            'attendee' : row[10],
                            'attendance' : row[11]}
    database.close()
    return userDict     


def returnUserList():
    """return user list as a dictionary"""
    database = sqlite3.connect('Information.db')
    cursor = database.cursor()
    cursor = database.execute("SELECT * from USERS")
    userDict = {}
    for row in cursor: 
        userDict[row[0]] = {'location' : row[1],
                            'ip' : row[2],
                            'port' : row[3],
                            'lastlogin' : time.strftime('%d/%b %H:%M:%S', time.localtime(row[4])),
                            'online' : row[5]}
    database.close()
    return userDict


def returnMessages():
    """return messages as a dictionary"""
    database = sqlite3.connect('Information.db')
    cursor = database.cursor()
    cursor = database.execute("SELECT * from MESSAGES")
    userDict = {}
    for row in cursor: 
        userDict[row[0]] = {'sender' : row[1],
                            'destination' : row[2],
                            'message' : row[3],
                            'stamp' : time.strftime('%d/%b %H:%M:%S', time.localtime(row[4])),
                            'filename' : row[5],
                            'content_type' : row[6]
                            }
    database.close()
    return userDict


def databaseFiles(file):
    """put files in database"""
    database = sqlite3.connect('Information.db') 
    cursor = database.cursor()
    cursor.execute("INSERT INTO MESSAGES (SENDER, DESTINATION, FILENAME,CONTENT_TYPE, STAMP) VALUES (?, ?,?,?,?)",
                (file.get('sender'), file.get('destination'), file.get('filename'),file.get('content_type'),file.get('stamp')))
    database.commit()
    database.close()       

def updateProfile(profile,username):
    """put profile details in database"""
    database = sqlite3.connect('Information.db')
    cursor = database.cursor()
    cursor.execute("UPDATE PROFILE SET FULLNAME = ?, POSITION=?, DESCRIPTION=?, LOCATION=?,PICTURE=? WHERE USERNAME=?",
            (profile.get('fullname'),profile.get('position'),profile.get('description'),profile.get('location'),profile.get('picture'),username))
    database.commit()
    database.close()

def updateAttendance(event, eventID):
    """update attendance in database"""
    database = sqlite3.connect('Information.db')
    cursor = database.cursor()
    cursor.execute("UPDATE EVENTS SET ATTENDANCE = ? , ATTENDEE = ? WHERE EVENTID = ?",
     (event.get('attendance'), event.get('sender'),eventID))
    database.commit()
    database.close()


def storeMessages(message):
    """store messages"""
    database = sqlite3.connect('Information.db')
    cursor = database.cursor()
    cursor.execute("INSERT INTO MESSAGES (SENDER, DESTINATION, MESSAGE, STAMP) VALUES (?, ?, ?, ?)",
     (message.get('sender'), message.get('destination'), message.get('message'), message.get('stamp')))
    database.commit()
    database.close()

def storeEvents(event, eventID):
    """store event details"""
    database = sqlite3.connect('Information.db')
    cursor = database.cursor()
    cursor.execute("INSERT INTO EVENTS (EVENTID, SENDER, DESTINATION, EVENT_NAME, EVENT_DESCRIPTION, EVENT_LOCATION, EVENT_PICTURE, START_TIME, END_TIME) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
     (eventID, event.get('sender'), event.get('destination'), event.get('event_name'), event.get('event_description'),event.get('event_location'),event.get('event_picture'),event.get('start_time'),event.get('end_time')))
    database.commit()
    database.close()


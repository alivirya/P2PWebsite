#!/usr/bin/python

import sqlite3

## THIS DOCUMENT CREATES ALL OF THE TABLES WITHIN THE DATABASE

def creating():
	conn = sqlite3.connect('Information.db')
	
	
	conn.execute('''CREATE TABLE IF NOT EXISTS USERS
	
	               (USERNAME TEXT PRIMARY KEY     NOT NULL,
	               LOCATION          TEXT,
	               IP                TEXT,
	               PORT              INT,
	               LASTLOGIN         INT,
	               ONLINE            INT);''')
	
	conn.execute('''CREATE TABLE IF NOT EXISTS MESSAGES
	               (
	               ID	INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
	               SENDER                TEXT     NOT NULL,
	               DESTINATION           TEXT     NOT NULL,
	               MESSAGE               TEXT,
	               STAMP                 INT      NOT NULL,
	               FILENAME              TEXT,
	               CONTENT_TYPE           TEXT);''')
	
	conn.execute('''CREATE TABLE IF NOT EXISTS PROFILE
	
	                (FULLNAME           TEXT NOT NULL,
	                POSITION           TEXT,
	                DESCRIPTION        TEXT,
	                LOCATION           TEXT,
	                PICTURE            TEXT,
	                ENCODING           TEXT,
	                ENCRYPTION         TEXT,
	                DECRYPTIONKEY      TEXT,
	                USERNAME	TEXT PRIMARY KEY NOT NULL);''')
	
	
	conn.execute('''CREATE TABLE IF NOT EXISTS EVENTS
	
	                (
	                ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
	                EVENTID TEXT   NOT NULL,
	                SENDER           TEXT NOT NULL,
	                DESTINATION           TEXT NOT NULL,
	                EVENT_NAME        TEXT  NOT NULL,
	                EVENT_DESCRIPTION   TEXT,
	                EVENT_LOCATION           TEXT,
	                EVENT_PICTURE            TEXT,
	                START_TIME           REAL NOT NULL,
	                END_TIME         REAL NOT NULL,
	                ATTENDEE    TEXT,
	                ATTENDANCE INTEGER);''')
	
	
	conn.execute('''CREATE TABLE IF NOT EXISTS SERVER
	
	               (USERNAME TEXT     NOT NULL,
	               PASSWORD          TEXT         NOT NULL,
	               THREADING         TEXT,
	               ACTIVEUSER              TEXT,
	               TFA	TEXT);''')
	conn.commit()
	
	conn.close()
	
	               
	
	

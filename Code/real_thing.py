#!/usr/bin/python
# Requires:  CherryPy 3.2.2  (www.cherrypy.org)
#            Python  (We use 2.7)



import sqlite3, cherrypy, hashlib, time, urllib2, urllib, urlparse, socket, json
import os, os.path, cgi, base64, threading, hmac, struct
import databasesCalling, creatingdatabase
from random import choice
from string import ascii_uppercase
from collections import OrderedDict

 
""" The address we listen for connections on"""
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
local_ip = s.getsockname()[0]
fptr = urllib2.urlopen("https://api.ipify.org")
public_ip = fptr.read()
fptr.close()

#set IP address according to location
if (local_ip[0:3] == '192'):
    listen_ip = public_ip
else:
    listen_ip = local_ip
if (listen_ip[0:6] == '10.103'):
    location = '0'
elif (listen_ip[0:6] == '172.23'):
    location = '1'
else:
    location = '2'
listen_port = 10007

# SECURITY

""" CODE FROM STACK OVERFLOW, GETTING GOOGLE AUTHENTICATION CODE"""
def getHOTP(secret, intervals_no):
    key = base64.b32decode(secret, True)
    msg = struct.pack(">Q", intervals_no)
    h = hmac.new(key, msg, hashlib.sha1).digest()
    o = ord(h[19]) & 15
    h = (struct.unpack(">I", h[o:o+4])[0] & 0x7fffffff) % 1000000
    return h

def getTOTP(secret):
    return getHOTP(secret, intervals_no=int(time.time())//30)



class MainApp(object):

    #CherryPy Configuration
    _cp_config = {'tools.encode.on': True, 
                  'tools.encode.encoding': 'utf-8',
                  'tools.sessions.on' : True,
                 }                 




    #THREADING THREADING THREADING
    def startThread(self):
        """start the thread"""
        updateThread = threading.Thread(target=self.getDetails, args=(cherrypy.session['username'],cherrypy.session['password']))
        updateThread.daemon = True
        updateThread.start()


    def updateUsers(self, username,password):
        """Updating users statuses and profiles"""

        values = {'username' : username,
                  'password' : password,
                  'enc' : '0',
                  'json' : '1'}
        result = json.loads(self.returnURLInformation('http://cs302.pythonanywhere.com/getList',values))
        allUsers = self.initiateUsers()
        onlineList = []
        for key in result:        
            if (result[key]['username'] in allUsers):
                databasesCalling.updateUserInformation(result[key]["location"], result[key]["ip"], result[key]["port"], result[key]["lastLogin"], '1', (result[key]["username"]))
                self.retrieveStatus(result[key]['username'])
                self.fetchProfile(result[key]['username'],username)
                onlineList.append(result[key]['username'])
        for word in allUsers:
            if (word not in onlineList):
                databasesCalling.updateStatusInformation(0,word)

    def report(self,username,password):    
        """Reporting to the server"""
        url = 'http://cs302.pythonanywhere.com/report'
        values = {'username' : username,
                  'password' : password,
                  'location' : location, 
                  'ip' : listen_ip,
                  'port' : listen_port }
        response = self.returnURLInformation(url, values)
        print response


    def getDetails(self,username,password):
        """ do all the above every 45 seconds"""    
        while(databasesCalling.returnThread(username)):
            print "THREADING"
            self.updateUsers(username,password)
            self.report(username,password)
            time.sleep(45)
        
    



    @cherrypy.expose
    def signin(self, username=None, password=None):
        """LOGGING IN"""
        if (self.authoriseUserLogin(username,password)):
            cherrypy.session['username'] = username
            #if user doesnt exist, update credentials in the server
            if (self.userExists() != 'True'):
                databasesCalling.updateUserCredentials(username,self.hash(2, password),self.secretGenerator())
                raise cherrypy.HTTPRedirect('/tfa')
            else: 
                raise cherrypy.HTTPRedirect('/tfaAuthenticated')

        raise cherrypy.HTTPRedirect('/')
        



    @cherrypy.expose
    def logout(self):
        """LOGGINGOUT
        logoff user and expire session"""
        url = 'http://cs302.pythonanywhere.com/logoff'
        #expiring session
        try: 
            databasesCalling.updateThreading(cherrypy.session['username'],False)
            values = {'username' : cherrypy.session['username'],'password' : cherrypy.session['password']}
            result = self.returnURLInformation(url,values)
            cherrypy.lib.sessions.expire()
            print result
            raise cherrypy.HTTPRedirect('/')            
        except: 
            raise cherrypy.HTTPRedirect('/')
 

    def initializingDatabases(self):
        """initializing databases"""
        creatingdatabase.creating()
        for key in self.initiateUsers():
            databasesCalling.insertUsers(key)
            databasesCalling.updateName(key)


    @cherrypy.expose
    def initiateUsers(self):
        """Get list of all users"""
        result = self.returnURLInformation('http://cs302.pythonanywhere.com/listUsers','')
        result = result.split(',')
        return result


    #PROCESSES

    def returnURLInformation(self, url, values):
        """Return a url based on string values"""
        data = urllib.urlencode(values)
        full_url = url + '?' + data
        information = urllib2.urlopen(full_url)
        information = information.read()
        return information
        
    def authoriseUserLogin(self, username=None, password=None):
        """Authorizing login"""
        values = {'username' : username,
                  'password' : self.hash(2,password),
                  'location' : location, 
                  'ip' : listen_ip,
                  'port' : listen_port }
        try:
            result = self.returnURLInformation('http://cs302.pythonanywhere.com/report', values)
            print result
            if (result[0] == '0'):
                return True
            else:
                return False
        except: 
            return False

    def storeDownloadedFiles(self,file):
        """store downloaded files"""
        decoded = base64.decodestring(file.get('file'))
        newFile = file.get('filename')
        newFile = open('./public/media/' + newFile, 'wb')
        newFile.write(decoded)
        databasesCalling.databaseFiles(file)


    # SECURITY

    @cherrypy.expose
    def secretGenerator(self):
        """Create a secret for tfa"""
        random = ''.join(choice(ascii_uppercase) for i in range(16))
        return base64.b32encode(random)[:16]
        
    

    @cherrypy.expose
    def tfaAuthenticator(self, code):
        """Checks if the authentication is right"""
        if (str(code) in str(getTOTP(databasesCalling.returnTFA(cherrypy.session['username'])))):
            databasesCalling.updateThreading(cherrypy.session['username'],True)
            cherrypy.session['password'] = databasesCalling.returnPassword(cherrypy.session['username'])
            self.startThread()
            raise cherrypy.HTTPRedirect('/')
        else: 
            cherrypy.lib.sessions.expire()
            raise cherrypy.HTTPRedirect('/')


    """ CODE not fully implemented for encryption and hashing"""
    def AESdecrypt(enc):
        enc = binascii.unhexlify(enc)
        iv = enc[:16]
        cipher = AES.new('41fb5b5ae4d57c5ee528adb078ac3b2e', AES.MODE_CBC, iv )
        return cipher.decrypt(enc[16:]).rstrip(' ')
        
    def hash(self,standard,text, salt='COMPSYS302-2017'):
        if (standard == 0):
            return text
        elif (standard == 1):
            hashed = hashlib.sha256(text)
            return hashed.hexdigest()
        elif (standard == 2):
            hashed = hashlib.sha256(text + salt) # This is not to be used for hashing messages/files, simply for the login server
            return hashed.hexdigest()
        elif (standard == 3):
            hashed = hashlib.sha512(text)
            return hashed.hexdigest()   
      
      
        
    """ PAGES THAT ARE DISPLAYED IN THE BROWSER"""
    @cherrypy.expose
    def index(self,upi=None):
        try:
            """main login/home page
            update users and report"""
            self.setActiveUser(upi)
            print "##########################################"
            print "Welcome   " + cherrypy.session['username']
            print "##########################################"
            cherrypy.session['password']
            print "##########################################"
            print "AUTHENTICATED"
            print "##########################################"

            homePage = urllib.urlopen('home.html')
            return homePage
        except KeyError:
            self.initializingDatabases()
            loginPage = urllib.urlopen('homepage.html')
            return loginPage   

    @cherrypy.expose
    def profile(self, user):
        """USERS profile page"""
        profile = databasesCalling.returnProfile()
        profile = open('profile.html').read().format(name=profile[user]['fullname'],position=profile[user]['position'],description=profile[user]['description'],location=profile[user]['location'])                 
        return profile

    @cherrypy.expose
    def event(self):
        """eventpage"""
        event = open('event.html').read()               
        return event


    @cherrypy.expose
    def default(self, *args, **kwargs):
        """404 page"""
        """The default page, given when we don't recognise where the request is for."""
        cherrypy.response.status = 404
        return open('fail.html').read().format(fail='404 Page not found :(')

    @cherrypy.expose
    def listAPI(self):
        """list all available APIS"""
        return "Available APIs: /listAPI /ping [sender]/receiveMessage [sender] [destination] [message] [stamp] [markdown] [encryption(opt)] [hashing(opt)] [hash(opt)] /getProfile [sender] /recieveFile [sender] [destination] [file] [filename] [content_type] [stamp] [encryption] [hash] /getStatus [profile_username] /receiveEvent [sender] [destination] [event_name] [event_description] [event_location] [event_picture] [start_time] [end_time] [markdown] [encryption] [decryptionKey] /acknowledgeEvent [sender] [event_name] [attendance] [start_time] Encryption: 0 Hashing: 0"
   
    @cherrypy.expose
    def ping(self, sender=None):
        """PING"""  
        return "0"

    @cherrypy.expose
    def tfa(self):
        """return qr code page"""
        tfa = open('tfa.html').read()               
        return tfa
        
    @cherrypy.expose
    def tfaAuthenticated(self):
        """return authentication page"""
        tfa = open('tfaAuthenticated.html').read()               
        return tfa


    # FORMS FORM FORMS
    """these are form datas sent to us from the html"""

    @cherrypy.expose
    def editProfile(self,user,fullname,position,description,location,picture): 
        """Edit profile given the details from the form"""
        data = {'fullname' : fullname,
                'position' : position,
                'description' : description,
                'location' : location,
                'picture' : picture}
        databasesCalling.updateProfile(data,user)
        url = '/profile?user='+user
        raise cherrypy.HTTPRedirect(url)

    @cherrypy.expose
    def upload(self, myFile, destination):
        """upload file"""
        size = 0
        file =  myFile.file.read()
        while True:
            data = myFile.file.read(8192)
            if not data:
                break
            size += len(data)
        file = base64.encodestring(file)
        filename =  myFile.filename
        content_type = myFile.content_type
        file_details = {'sender' : cherrypy.session['username'],
                        'destination' : destination,
                        'file' : file,
                        'filename' : str(filename),
                        'content_type' : str(content_type),
                        'stamp' : float(time.time())}
        return file_details

    @cherrypy.expose
    def search(self,searchID):
        """Search users and messages"""
        #get dictionary of userlist and messagelist
        userList = databasesCalling.returnUserList()
        messageList = databasesCalling.returnMessages()
        result = ''
        messageFound = False

        """if user is found, redirrect to its page"""
        for key in userList:
            if (key == searchID):
                self.setActiveUser(key)
                link = '/?upi=' + searchID
                raise cherrypy.HTTPRedirect(link)
        """otherwise search messages"""
        for key in messageList:
            if (messageList[key]['message'] != None and ((messageList[key]['sender'] == cherrypy.session['username']) or (messageList[key]['destination'] == cherrypy.session['username']))):
                if (searchID in messageList[key]['message']):
                    messageFound = True
                    result += messageList[key]['stamp'] +'      '+  messageList[key]['sender'] + '       :         ' + messageList[key]['message'] + '    to:    ' +  messageList[key]['destination']+  '</br>'

        """return html depending on result"""
        if (messageFound):
            return open('search.html').read().format(search=result)
        else:
            return open('search.html').read().format(search='NOT FOUND')

    @cherrypy.expose
    def updateStatus(self,status):
        """Update your status"""
        user = cherrypy.session['username']
        if (status == "Online"):
            databasesCalling.updateStatusInformation(1,user)
        if (status == 'Idle'):
            databasesCalling.updateStatusInformation(2,user)
        elif (status == 'Away'):
            databasesCalling.updateStatusInformation(3,user)
        elif (status == 'Do Not Disturb'):
            databasesCalling.updateStatusInformation(4,user)
        else: 
            databasesCalling.updateStatusInformation(0,word)
        raise cherrypy.HTTPRedirect('/profile?user=' + user)


    @cherrypy.expose
    def createEvent(self, destination, event_name, event_description, event_location, event_picture, start_time,end_time):
        """Create an event through the parameters given"""
        epochStart = float(time.mktime(time.strptime(start_time, '%d.%m.%Y %H:%M')))
        epochEnd =  float(time.mktime(time.strptime(end_time, '%d.%m.%Y %H:%M')))

        eventSent = False
        try:
            eventID = self.hash(2, event_name + str(epochStart))
            event = {'sender' : cherrypy.session['username'],
                     'destination' : destination,
                     'event_name' : event_name,
                     'event_description' : event_description,
                     'event_location' : event_location,
                     'event_picture' : event_picture,
                     'start_time' : epochStart,
                     'end_time' : epochEnd
                     }
            eventResult = databasesCalling.getLinkInformation('/receiveEvent', destination,event)
            if (eventResult[0] == '0'):
                databasesCalling.storeEvents(event, eventID)
                eventSent = True
        except: 
            return open('fail.html').read().format(fail='Event not sent :(')
        if (eventSent):
            raise cherrypy.HTTPRedirect('/event')


    # INTERNAL INTERNAL INTERNAL


    @cherrypy.expose
    @cherrypy.tools.json_in()
    def acknowledgeEvent(self):
        """acknowledgeEvent, receiveEvent, receiveFile and receiveMessage all retrieve a json object which is then updated to the database"""
 
        try:
            event = cherrypy.request.json
        except:
            return "1"
        try:
            eventID = self.hash(2, event.get('event_name') + str(event.get('start_time')))
            databasesCalling.updateAttendance(event, eventID)
            return "0"
        except: 
            return "4"




    @cherrypy.expose
    @cherrypy.tools.json_in()
    def receiveEvent(self):
        try: 
            event = cherrypy.request.json
        except: 
            return "1"

        try:
            eventID = self.hash(2, event.get('event_name') + str(event.get('start_time')))
            databasesCalling.storeEvents(event, eventID)
            return "0"
        except:
            return "4"


    @cherrypy.expose
    @cherrypy.tools.json_in()
    def receiveFile(self):
        try:
            file = cherrypy.request.json
        except:
            return "1"
        try:
            self.storeDownloadedFiles(file)
            return "0"
        except:
            return "4"



    @cherrypy.expose
    @cherrypy.tools.json_in()
    def receiveMessage(self):
        try:
            message = cherrypy.request.json
        except:
            return "1"
        try:
            databasesCalling.storeMessages(message)
            return "0"
        except: 
            return "4"


    def retrieveStatus(self,user):
        """Retrieve the statuses of other users"""
        try:
            details = {'profile_username' : user}
            response = json.loads(databasesCalling.getLinkInformation('/getStatus',user,details))
            if (response['status'] == 'Idle'):
                databasesCalling.updateStatusInformation(2,user)
            elif (response['status'] == 'Away'):
                databasesCalling.updateStatusInformation(3,user)
            elif (response['status'] == 'Do Not Disturb'):
                databasesCalling.updateStatusInformation(4,user)
            elif (response['status'] == 'Online'):
                databasesCalling.updateStatusInformation(1,user)
            else:
                databasesCalling.updateStatusInformation(0,user)
        except: 
            pass


    def fetchProfile(self, target, user):
        """receive the profiles of other users"""
        try:
            details = {'profile_username' : target,
                       'sender' : user}
            response = databasesCalling.getLinkInformation('/getProfile', target, details)
            response = json.loads(response)
            databasesCalling.updateProfile(response,target)
        except:
            pass             


    """ EXTERNAL EXTERNAL EXTERNAL
    EXTERNAL COMMUNICATIONS TO OTHER USERS"""

    @cherrypy.expose
    def sendMessage(self, message, destination,myFile,sender=None):
        """This applies to files and messages as they are both linked"""
        fileSent = False
        messageSent=False 
        """try send a file upload first"""
        if (myFile.filename != None):
            try:  
                file = self.upload(myFile,destination)
                fileResult = databasesCalling.getLinkInformation('/receiveFile',destination,file)
                if (fileResult[0] == '0'):
                    fileSent = True
                    self.storeDownloadedFiles(file)
            except:
                pass
        """try message sending"""
        if (message != ''):     
             try:
                 message = {'sender': cherrypy.session['username'],
                        'message': message,
                        'destination' :destination,
                        'stamp' : float(time.time())}
                 messageResult = databasesCalling.getLinkInformation('/receiveMessage', destination, message)
                 if (messageResult[0] == '0'):
                     databasesCalling.storeMessages(message)
                     messageSent = True
             except:
                 pass

        """only redirect if the message has been sent"""
        page = '/?upi=' + destination
        if (messageSent or fileSent):          
            raise cherrypy.HTTPRedirect(page)
        else:
            return open('fail.html').read().format(fail='Message not sent :(')
    
    
    @cherrypy.expose
    def respondToEvent(self, event_name, attendance, start_time, host):
        """give user a response to their event"""
        sender = cherrypy.session['username']
        startTime  = float(time.mktime(time.strptime(start_time, '%d/%b/%y %H:%M:%S')))
        eventID = self.hash(2, event_name + str(startTime))
        eventUpdated = False
        try: 
            attendanceDetails= {'event_name' : event_name,
                              'sender' : sender,
                               'attendance' : attendance,
                                'start_time' : startTime}
            attendanceResult = databasesCalling.getLinkInformation('/acknowledgeEvent',host, attendanceDetails)
            if (attendanceResult[0] == '0'):
                databasesCalling.updateAttendance(attendanceDetails, eventID)
            else:
                attendanceDetails = {'event_name' : event_name,
                              'sender' : sender,
                              'attendance' : 3,
                              'attendance_time' : start_time}    
                databasesCalling.updateAttendance(attendanceDetails, eventID)
            eventUpdated = True
        except: 
            return open('fail.html').read().format(fail='Unable to send update to Client :(')
        if (eventUpdated):
            raise cherrypy.HTTPRedirect(page)
            
            
    

    
    @cherrypy.tools.json_in()
    @cherrypy.expose
    def getStatus(self):
        """Send status of a user to other users who request it"""
        target = cherrypy.request.json
        target = target.get('profile_username')
        users = databasesCalling.returnUserList()
        if (users[target]['online'] == 0):
            status= "Offline"
        elif (users[target]['online'] == 1):
            status= "Online"
        elif (users[target]['online'] == 2):
            status= "Idle"
        elif (users[target]['online'] == 3):
            status= "Away"
        else:
            status ="Do Not Disturb"
        status = {'status': status}
        return json.dumps(status)



    @cherrypy.tools.json_in()
    @cherrypy.expose
    def getProfile(self):
        """Send profiles of users to other users who request it """
        profile = cherrypy.request.json
        username= profile.get('profile_username')
        profiles = databasesCalling.returnProfile()
        details = {'fullname' : profiles[username]['fullname'],
                    'position' : profiles[username]['position'],
                    'description' : profiles[username]['description'],
                    'picture' : profiles[username]['picture'],
                    'location' : profiles[username]['location']}
        return json.dumps(details)





        # JAVASCRIPT JAVASCRIPT JAVASCRIPT

        """THESE ARE ALL JAVASCRIPT FUNCTIONS WHICH ARE ONLY NECESSARY IN ORDER TO EDIT THE HTML DISPLAY"""
    @cherrypy.expose
    def returnProfile(self):  
        return json.dumps(databasesCalling.returnProfile())

    @cherrypy.expose
    def returnSecret(self):  
        return databasesCalling.returnTFA(cherrypy.session['username'])

    @cherrypy.expose
    def userExists(self):  
        return str(databasesCalling.checkifUserExists(cherrypy.session['username']))

    @cherrypy.expose
    def returnEvents(self):
        userDict = databasesCalling.returnEvent()
        userDict = OrderedDict(sorted(userDict.items(), key=lambda t:t[0]))
        userDict = OrderedDict(sorted(userDict.items(), key=lambda t:t[1]["start_time"], reverse = True))
        return json.dumps(userDict)



    @cherrypy.expose
    def setActiveUser(self,user):
        if (user != None):
            databasesCalling.updateActiveUser(cherrypy.session['username'],user)


    @cherrypy.expose
    def returnActiveUser(self):
        try:
            return databasesCalling.returnActiveUser(cherrypy.session['username'])
        except: pass


    @cherrypy.expose
    def returnSessionUser(self):
        try:
            return cherrypy.session['username']
        except: 
            raise cherrypy.HTTPRedirect('/')

    @cherrypy.expose
    def returnUserList(self):
        userDict = databasesCalling.returnUserList()
        userDict = OrderedDict(sorted(userDict.items(), key=lambda t:t[0]))
        userDict = OrderedDict(sorted(userDict.items(), key=lambda t:t[1]["online"], reverse = True))
        return json.dumps(userDict)

    @cherrypy.expose
    def returnMessages(self):
        return json.dumps(databasesCalling.returnMessages())

if __name__ == '__main__':
    conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './public'
        }
    }

    cherrypy.config.update({'server.socket_host': '0.0.0.0',
                            'server.socket_port': listen_port,
                            'engine.autoreload.on': True,
                            'tools.gzip.on' : True,
                            'tools.gzip.mime_types' : ['text/*'],
                           })
    cherrypy.quickstart(MainApp(), '/', conf)

    
if cherrypy.engine.state != cherrypy.engine.states.STARTED:
    print "shutting down"
    databasesCalling.logoutOfServer()

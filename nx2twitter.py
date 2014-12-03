#This software is provided AS-IS and without warranty. Use at your own risk.
#Written/Compiled by Adam Kemp (@atomkemp), 2014
#Licensed under GPLv3 or greater. See LICENSE file for more information.
#
#THIS BOT USES SENSITIVE INFORMATION ABOUT YOUR GMAIL AND TWITTER ACCOUNT. KEEP THIS INFORMATION PRIVATE!!!
#
#copy, move and delete components adapted from: http://stackoverflow.com/questions/3527933/move-an-email-in-gmail-with-python-and-imaplib
#parse and download components adapted from: http://stackoverflow.com/questions/348630/how-can-i-download-all-emails-with-attachments-from-gmail
#Twitter components adapted from: http://www.dototot.com/how-to-write-a-twitter-bot-with-python-and-tweepy/

import imaplib, re, email, os, tweepy, time, datetime

detach_dir = "./tweeted" #set the system folder name for downloaded images
delay = 0.5 #set time for mail check in minutes
tweeting = False #set to true to send tweets. good for testing your system and configuration

pattern_uid = re.compile('\d+ \(UID (?P<uid>\d+)\)')

def setupTwitter():
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
    api = tweepy.API(auth)
    
def connect():
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login(username, password)
    return imap

def disconnect(imap):
    imap.logout()

def parse_uid(data):
    match = pattern_uid.match(data)
    return match.group('uid')

if __name__ == '__main__':
    
    print "***************************************************"
    print "NX2Twitter"
    print "Tweeting pictures from your Samsung NX smart camera"
    print "Written/Compiled by Adam Kemp (@atomkemp), 2014"
    print "Software is provided AS-IS and without warranty."
    print "Use at your own risk."
    print "***************************************************"
    print ""
    time.sleep(2) #for dramatic effect

    if not os.path.isfile('config.n2t'):
        print "Configuration file not found. Let's make a new one!"
        time.sleep(2)
        username = raw_input('Enter your Gmail address: ')
        password = raw_input('Enter your Gmail password: ')
        accessPassword = raw_input('Enter your access password: ')
        mailDump = raw_input('Enter your desired Gmail folder: ')
        CONSUMER_KEY = raw_input('Enter your Twitter Consumer Key: ')
        CONSUMER_SECRET = raw_input('Enter your Twitter Consumer Secret: ')
        ACCESS_KEY = raw_input('Enter your Twitter Access Key: ')
        ACCESS_SECRET = raw_input('Enter your Twitter Access Secret: ')
        print "Writing to file..."
        config = open('config.n2t','w')
        config.write(username + '\n')
        config.write(password + '\n')
        config.write(accessPassword + '\n')
        config.write(mailDump + '\n')
        config.write(CONSUMER_KEY + '\n')
        config.write(CONSUMER_SECRET + '\n')
        config.write(ACCESS_KEY + '\n')
        config.write(ACCESS_SECRET + '\n')
        config.close()
        print "Done!"
    else:
        print "Previous configuration found. Reading file..."
        config = open('config.n2t','r')
        configLines = config.readlines()
        username = configLines[0].rstrip('\n')
        password = configLines[1].rstrip('\n')
        accessPassword = configLines[2].rstrip('\n')
        mailDump = configLines[3].rstrip('\n')
        CONSUMER_KEY = configLines[4].rstrip('\n')
        CONSUMER_SECRET = configLines[5].rstrip('\n')
        ACCESS_KEY = configLines[6].rstrip('\n')
        ACCESS_SECRET = configLines[7].rstrip('\n')
        config.close()
        print "Data read from existing config.n2t. If you would like"
        print "to create a new config file, delete the old one and"
        print "restart the program."
        time.sleep(2)
        print ""
        print "Username: " + username
        print "Password: " + password
        print "Access Password: " + accessPassword
        print "Mail Folder: " + mailDump
        print "Consumer Key: " + CONSUMER_KEY
        print "Consumer Secret: " + CONSUMER_SECRET
        print "Access Key: " + ACCESS_SECRET
        print "Access Secret: " + ACCESS_SECRET
    setupTwitter()
    print "Done! Starting up..."
    print ""
    
    while True:
        imap = connect()
        imap.select(mailbox = 'Inbox', readonly = False)
        resp, items = imap.search(None, '(SUBJECT "[Samsung Smart Camera] sent you files!")') #this is just what my camera uses as default. change to whatever 'subject' your camera/system uses

        email_ids  = items[0].split()
        now = datetime.datetime.now()

        #runs only if there are available messages
        if not email_ids:
            print str(now) + ": No new messages..."
            
        else:
            print str(now) + ": Message detected. Parsing..."
            latest_email_id = email_ids[-1] # Assuming that you are moving the latest email.

            resp, uid_data = imap.fetch(latest_email_id, "(UID)") #extract UID
            resp, data = imap.fetch(latest_email_id, "(RFC822)") #extract message

            mail = email.message_from_string(data[0][1])
            varFrom = mail['From']
            varPass = re.search(';(.+?);', varFrom).group(1)
            print "From: " + varFrom
            print "Password: "+ varPass
            if varPass == accessPassword:
                print "Access granted!"
                for part in mail.walk():
                    if part.get_content_maintype() == 'multipart':
                        continue
                    if part.get_content_type() == "text/html":
                        message_body = part.get_payload(decode=False)
                        print "Message body: " + message_body
                    if part.get('Content-Disposition') is None: 
                        continue
                    
                    filename = part.get_filename()
                    print "Found file: " + filename
                    counter = 1

                    if not filename:
                        filename = 'part-%03d%s' % (counter, 'bin')
                        counter += 1

                    att_path = os.path.join(detach_dir, filename)

                    if not os.path.isfile(att_path):
                        fp = open(att_path, 'wb')
                        fp.write(part.get_payload(decode=True))
                        fp.close()

                    #this seems like a good place to Tweet
                    if tweeting:
                        photo_path = './tweeted/' + filename
                        if not message_body:
                            api.update_with_media(photo_path,'')
                        else:
                            api.update_with_media(photo_path,message_body)
            else:
                print "Access DENIED!"

            #moves message to desired directory
            msg_uid = parse_uid(uid_data[0])

            result = imap.uid('COPY', msg_uid, 'NX2Twitter')

            if result[0] == 'OK':
                mov, data = imap.uid('STORE', msg_uid , '+FLAGS', '(\Deleted)')
                imap.expunge()
        time.sleep(delay*60) #sleep for desired time

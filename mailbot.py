"""
    Authur: Steven Wu

    How to use this class
    1. Subclass this class and fill needed parameter
    2. Add your function to the new class and append its name to MailBot.EnabledService
    3. Any string written in MailBot.ReplyMsg will be mailed out, add your reply message here


    This bot could search UNSEEN mail in specified mail/folder/title
    execute command in the mail and reply result
"""


import time
import sys
import getpass
import imaplib
import email
import smtplib
from email.mime.text import MIMEText




def GetInputLine():
    "Get line input from stdin and remove CR/LF"
    line = sys.stdin.readline()
    lines = line.split("\n")
    if len(lines) > 0:
        line = lines[0]
    else:
        line = ''
    return line


def GetPlainTextFromMail(mail_str):
    "Get plain text from RFC822 format"
    message = email.message_from_string(mail_str)
    for part in message.walk():
        if part.get_content_type() == "text/plain":
            return part.get_payload(decode=True)
    return ''



class MailBot:
    def __init__(self):
        self.IMAP_Server = ''
        self.SMTP_Server = ''
        self.user = ''
        self.__password = ''
        self.run = True
        self.IntervalSec = 900
        self.CommandMailTitle = ''
        self.ReplyMailTitle = ''
        self.MailFolder = ''
        self.RetryCount = 3
        self.RetryItvSec = 60

        self.ReplyMsg = ''
        self.DecodeCharset = ''

        self.EnabledService = ['SetIntervalMin']
        

    def Sleep(self,SlpSec):
        print 'Sleep %d secs' % (SlpSec)
        for a in range(0,SlpSec,1):
            if self.run:
                time.sleep(1)

    def SetPassword(self,password):
        "Set password for loggin"
        self.__password = password

    def InputPassword(self):
        "Let user input password manually"
        self.__password = getpass.getpass()        

    def InputLoginInfo(self):
        "Let user input login info manually"
        print 'email:'
        self.user = GetInputLine()
        self.InputPassword()

    def ReplyMail(self,mail):
        try:
            msg = MIMEText(mail)
            msg['From'] = self.user
            msg['To'] = self.user
            msg['Subject'] = self.ReplyMailTitle

            server = smtplib.SMTP() 
            server.connect(self.SMTP_Server)
            server.starttls()
            server.login(self.user, self.__password)
            server.sendmail(self.user, [self.user], msg.as_string())
            server.quit()
            return True
        except:
            pass
        return False


    def GetMail(self):
        """
            Get mail from server
            GetMail() => (ConnectSuccess,Mail)
        """
        text = ''
        try:
            imap = imaplib.IMAP4_SSL(self.IMAP_Server)
            print imap.login(self.user,self.__password)
            print imap.select(self.MailFolder)
            typ,rm=imap.search(None,'UNSEEN','SUBJECT',self.CommandMailTitle)
            print typ,rm
            mails = rm[0].split()
            print mails
            nMail = len(mails)
            if nMail > 0:
                typ,content=imap.fetch(int(mails[0]), '(RFC822)')
                imap.logout()
                print typ
                text = content[0][1]
        except Exception as e:
            print 'get mail failed: [%s] %s'%(type(e).__name__,e.message)
            return False,''

        return True,text


    def GetStringCommands(self,s):
        lines = s.splitlines()
        cmds = []
        for line in lines:
            s = line.split(' ',1)
            if len(s) == 1:
                s.append('')
            cmds.append((s[0],s[1]))

        return cmds

    def GetMailCommands(self):
        CnSuc,mail = self.GetMail()
        if not CnSuc:
            return False,[]
        mail_cont = GetPlainTextFromMail(mail)
        if len(mail_cont) == 0:
            return True,[]
        return True,self.GetStringCommands(mail_cont)

    def GetInputCommands(self):
        print 'input command'
        cmd = GetInputLine()
        return self.GetStringCommands(cmd)

    def SetIntervalMin(self,sIntervalMin):
        """
            Set mail check interval in minute
            max is 15 min
            This is default service function
        """
        self.IntervalSec = int(sIntervalMin)*60
        if self.IntervalSec > 900:
            self.IntervalSec = 900
        print "call SetIntervalMin",sIntervalMin

    def OnCommandNotFount(self):
        print 'command not found'

    def ExecuteCommand(self,cmd,param):
        "Execute a command"
        if (cmd != '') and (cmd in self.EnabledService):
            method = None
            try:
                method = getattr(self,cmd)
            except:
                self.OnCommandNotFount()

            if method != None:
                method(param)

    def TryLogin(self):
        "Try to login server to test password correct"
        try:
            imap = imaplib.IMAP4_SSL(self.IMAP_Server)
            typ,m = imap.login(self.user,self.__password)
            print typ,m
            if typ == 'OK':
                imap.logout()
                return True
        except:
            pass
        return False

    def ExtraWork(self):
        pass

    def Run(self):
        "Start the bot, all initialization must be done before this function"
        if self.TryLogin() == False:
            print "password invalid, failed"
            return

        print "login successed, enter loop"
        while self.run:
            self.ReplyMsg = ''

            for a in range(0,self.RetryCount):
                print '[%s] get command' % (time.ctime())
                CnSuc,cmds = self.GetMailCommands()
                if CnSuc:
                    break
                print 'GetMail failed, retry count', a
                self.Sleep(self.RetryItvSec)

            for cmd,param in cmds:
                self.ExecuteCommand(cmd,param)
            self.ExtraWork()

            if len(self.ReplyMsg) > 0:
                if len(self.DecodeCharset) > 0:
                    self.ReplyMsg = self.ReplyMsg.decode(self.DecodeCharset).encode('utf-8')
                self.ReplyMail(self.ReplyMsg)

            self.Sleep(self.IntervalSec)


# MailBot


example code
=========================================================
    from mailbot import MailBot

    class MyBot(MailBot):
        def __init__(self):
            MailBot.__init__(self)
            self.IntervalSec = 900
            self.IMAP_Server = 'imap-mail server'
            self.SMTP_Server = 'smtp-mail server'
            self.user = 'your email'
            self.CommandMailTitle = 'Receive mail title'
            self.ReplyMailTitle = 'Reply mail title'
            self.MailFolder = 'folder'
            self.EnabledService.append('MyFunc')

        def MyFunc(self,param):
            self.ReplyMsg += 'MyFunc() called'



    b=MyBot()
    b.InputPassword()
    b.Run()







Send mail like this to your email and move to MailFolder and set to UNSEEN
=========================================================
    From: 'your email' 
    To: 'your email' 
    Subject: 'Receive mail title' 

    MyFunc 




and bot will reply this mail to you
=========================================================
    From: 'your email'
    To: 'your email'
    Subject: 'Reply mail title'

    MyFunc() called



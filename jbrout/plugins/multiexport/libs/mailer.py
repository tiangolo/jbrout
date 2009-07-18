# -*- coding: utf-8 -*-
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders
import os

def sendMail(fro="", to="", subject="", text="", files=[],server="localhost",
                security="none",port=25,auth=False,username="",password="" ):
    assert type(to)==list
    assert type(files)==list
    #print "Server is:   ", server
    #print "Port is:     ", port
    #print "Security is: ", security
    #print "Auth is:     ", auth
    #print "Username is: ", username
    #print "Password is: ", password

    msg = MIMEMultipart()
    msg['From'] = fro
    msg['To'] = COMMASPACE.join(to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach( MIMEText(text) )

    for file in files:
        part = MIMEBase('application', "octet-stream")
        part.set_payload( open(file,"rb").read() )
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"'
                       % os.path.basename(file))
        msg.attach(part)

    if security == "ssl":
        smtp = smtplib.SMTP_SSL(server, port)
        #smtp.set_debuglevel(1)
        smtp.connect()
    else:
        smtp = smtplib.SMTP(server, port)
        #smtp.set_debuglevel(1)
    if security == 'start tls':
        smtp.starttls()
    if auth:
        smtp.login(username, password)
    smtp.sendmail(fro, to, msg.as_string() )
    smtp.close()



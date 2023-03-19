import smtplib
import traceback
import sys

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def sendEmail(params):
    response = {
        'message_action' : "SEND_EMAILL_SUCCESS",
        'message_data'   : {}
    }
    try:
        port     = '2525'
        host     = 'localhost'
        default_sender = 'jublia_test@test.com'
        
        reciver   = params["participants"]
        subject   = params["email_subject"]
        body      = params['email_body']
        sender    = default_sender
        

        if isinstance(reciver, str):
            reciver = reciver.split(",")
        #end if 

        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['To'     ] = ", ".join(reciver)
        msg['From'   ] = sender

        html_email = MIMEText(body, 'html')
        msg.attach( html_email )

        server = smtplib.SMTP(host,port)
        server.sendmail(sender,reciver,msg.as_string())
        server.quit()

    except:
        print(traceback.format_exc())
        response['message_action'] = "SEND_EMAIL_FAILED"
        response['message_data']   = {
            "reason" : str(sys.exc_info())
        }
    
    return response 
#end def 
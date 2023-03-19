import email_lib
import traceback
import sys

from flask import Flask
from datetime import datetime
from app import Emails, Participants, app, db

class auto_send_email :
    def auto_send_email() :
        response = {
            'message_action' : "SEND_EMAIL_SUCCESS",
            'message_data'   : {}
        }
        try : 
            now = datetime.now()
            #get email queue
            q_emails = Emails.query.filter_by(status='QUEUE')
            for email in q_emails :
                email_datetime = email.send_date_time
                #compare current time with email send time
                print('now', now)
                print('email_datetime', email_datetime)
                print('>', now >=email_datetime)
                if now >=email_datetime :
                    current_email = email.json()
                    email_subject = current_email['email_subject']
                    email_body = current_email['email_body']
                    event_id = current_email['event_id']
                
                    #get participants (on assumsion in every events can have more than 1 participants)
                    q_participants = Participants.query.filter_by(event_id=event_id)
                    participants = [participant.participant_email for participant in q_participants]
                
                    params = {
                        'participants' : participants,
                        'email_subject': email_subject,
                        'email_body': email_body,
                    }
                    result = email_lib.sendEmail(params)
            
                    send_status = result['message_action']
                    
                    if 'SUCCESS' in send_status :
                        email.status = 'SUCCESS'
                    else :
                        email.status = 'FAILED'
                        email.failed_reason = result['message_data']['reason']
                    db.session.commit()
            
        except :
            print(traceback.format_exc())
            response['message_action'] = "SEND_EMAIL_FAILED"
            response['message_data']   = {
                "reason" : str(sys.exc_info())
            }
        print('Response ======================', response)
        return response
    #end def
#end class

with app.app_context():
    auto_send_emaill = auto_send_email()
    auto_send_email.auto_send_email()
import traceback
import sys
import os
from flask import Flask, request, jsonify, make_response, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from os import environ

#app definition
app = Flask(__name__, template_folder='templates')
# app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DB_URL')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@localhost:5432/test_jublia'

#db instance
db = SQLAlchemy(app)

#========================== Models ========================#

class Events(db.Model) :
    __tablename__ = "events"
    event_id = db.Column(db.Integer, unique=True, primary_key=True)
    event_name = db.Column(db.String(255), nullable = False)
    participant_ids = db.relationship('Participants', backref="event_participants", lazy=True)
    
    def __repr__(self) :
        return self.event_name
    
    def json(self) :
        return {
            'event_id': self.event_id,
            'event_name' : self.event_name,
            'participant_ids' : self.participant_ids,
        }
    #end def
#end class

class Participants(db.Model) :
    __tablename__ = "participants"
    participant_id = db.Column(db.Integer, unique=True, primary_key=True)
    participant_name = db.Column(db.String(255), nullable=False)
    participant_email = db.Column(db.String(255), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.event_id'), nullable=False)
    
    def __repr__(self) :
        return self.participant_name + ' <' + self.participant_email + '>'
        
    def json(self) :
        return {
            'participant_id': self.participant_id,
            'participant_name' : self.participant_name,
            'participant_email' : self.participant_email,
            'event_id': self.event_id,
        }
    #end def
#end class

class Emails(db.Model) :
    __tablename__ = "emails"
    email_id = db.Column(db.Integer, unique=True, primary_key=True)
    email_subject = db.Column(db.String(255), nullable=False)
    email_body = db.Column(db.String(5000), nullable=False)
    send_date_time = db.Column(db.DateTime)
    event_id = db.relationship('Events', backref="email_events", lazy=True)
    status = db.Column(db.String(255), nullable=False)
    
    def __repr__(self) :
        return self.email_subject
    
    def json(self) :
        return {
            'email_id': self.email_id,
            'emaiil_subject' : self.emaiil_subject,
            'emaiil_body' : self.emaiil_body,
            'send_date_time': self.send_date_time,
            'status': self.status,
            'event_id': self.event_id,
        }
    #end def
#end class

with app.app_context():
    db.create_all()
    
#========================== End Models ========================#

#========================= Routes ============================#

@app.route('/')
def index():
    return render_template('index.html')
#end def

@app.route('/v1/events', methods=['POST'])
def create_event():
    response = {
        'message_action' : "CREATE_EVENT_SUCCESS",
        'message_data'   : {}
    }
    try :
        params = request.form.to_dict()
        new_event = Events(
            event_name=params['event_name'], 
        )
        db.session.add(new_event)
        db.session.commit()
        
        response = redirect('/v1/events')
    except :
        print(traceback.format_exc())
        response['message_action'] = "CREATE_EVENT_FAILED"
        response['message_data']   = {
            "reason" : str(sys.exc_info())
        }
                  
    return response
#end def

@app.route('/v1/events', methods=['GET'])
def get_events() :
    response = {
        'message_action' : "GET_EVENT_SUCCESS",
        'message_data'   : {}
    }
    try : 
        q_events = Events.query.all()
        events = [event.json() for event in q_events]
        response = render_template(
            'events.html', 
            events=events,
        )
    except :
        print(traceback.format_exc())
        response['message_action'] = "GET_EVENTS_FAILED"
        response['message_data']   = {
            "reason" : str(sys.exc_info())
        }
    return response
#end def

@app.route('/v1/events/<int:event_id>', methods=['GET'])
def get_event(event_id) :
    response = {
        'message_action' : "GET_EVENT_SUCCESS",
        'message_data'   : {}
    }
    try : 
        event = Events.query.filter_by(event_id=event_id).first()
        response['message_data'] = {
            'event': event.json()
        }
    except :
        print(traceback.format_exc())
        response['message_action'] = "GET_EVENT_FAILED"
        response['message_data']   = {
            "reason" : str(sys.exc_info())
        }
        
    return response
#end def

@app.route('/v1/events/<int:event_id>', methods=['POST'])
def update_event(event_id) :
    response = {
        'message_action' : "UPDATE_EVENT_SUCCESS",
        'message_data'   : {}
    }
    try : 
        data = request.form.to_dict()
        event = Events.query.filter_by(event_id=event_id).first()
        event.event_name = data['event_name']
        db.session.commit()
        response = redirect('/v1/events')
    except :
        print(traceback.format_exc())
        response['message_action'] = "UPDATE_EVENT_FAILED"
        response['message_data']   = {
            "reason" : str(sys.exc_info())
        }
        
    return response
#end def

@app.route('/v1/events/delete/<int:event_id>')
def delete_event(event_id) :
    response = {
        'message_action' : "REMOVE_EVENT_SUCCESS",
        'message_data'   : {}
    }
    try : 
        event = Events.query.filter_by(event_id=event_id).first()
        db.session.delete(event)
        db.session.commit()
        
        response = redirect('/v1/events')
    except :
        print(traceback.format_exc())
        response['message_action'] = "REMOVE_EVENT_FAILED"
        response['message_data']   = {
            "reason" : str(sys.exc_info())
        }
        
    return response
#end def

@app.route('/v1/participants', methods=['POST'])
def create_participant():
    response = {
        'message_action' : "CREATE_PARTICIPANT_SUCCESS",
        'message_data'   : {}
    }
    try :
        data = request.form.to_dict()
        print('========== data ==============', data)
        new_participant = Participants(
            participant_name=data['participant_name'], 
            participant_email=data['participant_email'], 
            event_id=data['event_id']
        )
        db.session.add(new_participant)
        db.session.commit()
        
        response = redirect('/v1/participants')
    except :
        print(traceback.format_exc())
        response['message_action'] = "CREATE_PARTICIPANT_FAILED"
        response['message_data']   = {
            "reason" : str(sys.exc_info())
        }
                  
    return response
#end def

@app.route('/v1/participants', methods=['GET'])
def get_participants() :
    response = {
        'message_action' : "GET_PARTICIPANTS_SUCCESS",
        'message_data'   : {}
    }
    try : 
        q_participants = Participants.query.all()
        participants = [participant.json() for participant in q_participants]
        q_events = Events.query.all()
        events = [event.json() for event in q_events]
        response = render_template(
            'participants.html', 
            participants=participants,
            events=events
        )
    except :
        print(traceback.format_exc())
        response['message_action'] = "GET_PARTICIPANTS_FAILED"
        response['message_data']   = {
            "reason" : str(sys.exc_info())
        }
    return response
#end def

@app.route('/v1/participants/<int:participant_id>', methods=['GET'])
def get_participant(participant_id) :
    response = {
        'message_action' : "GET_PARTICIPANT_SUCCESS",
        'message_data'   : {}
    }
    try : 
        participant = Participants.query.filter_by(participant_id=participant_id).first()
        response['message_data'] = {
            'participant': participant.json()
        }
    except :
        print(traceback.format_exc())
        response['message_action'] = "GET_PARTICIPANT_FAILED"
        response['message_data']   = {
            "reason" : str(sys.exc_info())
        }
        
    return response
#end def

@app.route('/v1/participants/<int:participant_id>', methods=['POST'])
def update_participant(participant_id) :
    response = {
        'message_action' : "UPDATE_PARTICIPANT_SUCCESS",
        'message_data'   : {}
    }
    try : 
        data = request.form.to_dict()
        participant = Participants.query.filter_by(participant_id=participant_id).first()
        participant.participant_name = data['participant_name']
        participant.participant_email = data['participant_email']
        db.session.commit()
        response = redirect('/v1/participants')
    except :
        print(traceback.format_exc())
        response['message_action'] = "UPDATE_PARTICIPANT_FAILED"
        response['message_data']   = {
            "reason" : str(sys.exc_info())
        }
        
    return response
#end def

@app.route('/v1/participants/delete/<int:participant_id>', methods=['DELETE'])
def delete_participant(participant_id) :
    response = {
        'message_action' : "REMOVE_PARTICIPANT_SUCCESS",
        'message_data'   : {}
    }
    try : 
        participant = Participants.query.filter_by(participant_id=participant_id).first()
        db.session.delete(participant)
        db.session.commit()
    except :
        print(traceback.format_exc())
        response['message_action'] = "REMOVE_PARTICIPANT_FAILED"
        response['message_data']   = {
            "reason" : str(sys.exc_info())
        }
        
    return response
#end def

@app.route('/v1/emails', methods=['GET'])
def get_emails() :
    response = {
        'message_action' : "GET_EMAILS_SUCCESS",
        'message_data'   : {}
    }
    try : 
        q_emails = Emails.query.all()
        emails = [email.json() for email in q_emails]
        q_events = Events.query.all()
        events = [event.json() for event in q_events]
        response = render_template(
            'emails.html', 
            emails=emails,
            events=events
        )
    except :
        print(traceback.format_exc())
        response['message_action'] = "GET_EMAILS_FAILED"
        response['message_data']   = {
            "reason" : str(sys.exc_info())
        }
    return response
#end de

@app.route('/save_emails', methods=["POST"])
def save_emails():
    response = {
        'message_action' : "SAVE_EMAIL_SUCCESS",
        'message_data'   : {}
    }
    try :
        data = request.form.to_dict()
        print('========== data ==============', data)
        new_emails = Emails(
            email_subject=data['email_subject'], 
            email_body=data['email_body'], 
            event_id=data['event_id'],
            send_datetime=data['datetime']
        )
        db.session.add(new_emails)
        db.session.commit()
        
        response = redirect('/v1/emails')
    except :
        print(traceback.format_exc())
        response['message_action'] = "CREATE_PARTICIPANT_FAILED"
        response['message_data']   = {
            "reason" : str(sys.exc_info())
        }
                  
    return response
#========================= End Routes ============================#


app.run(debug=True)


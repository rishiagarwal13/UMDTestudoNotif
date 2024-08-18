from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
import asyncio
import websockets
import requests
from bs4 import BeautifulSoup
from time import strftime, gmtime
from random import randint
import json
import threading

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///courses.db'
app.config['MAIL_SERVER'] = 'smtp.example.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your-email@example.com'
app.config['MAIL_PASSWORD'] = 'your-password'

db = SQLAlchemy(app)
mail = Mail(app)

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    course = db.Column(db.String(20), nullable=False)
    section_index = db.Column(db.Integer, nullable=False)

# Existing functions (getSemester, getSections, isOpen) remain the same

async def check_course(course, section_index):
    while True:
        sections = getSections(course)
        section = sections[section_index]
        is_open = isOpen(section)
        
        if is_open:
            # Notify subscribers
            subscribers = Subscription.query.filter_by(course=course, section_index=section_index).all()
            for subscriber in subscribers:
                send_notification_email(subscriber.email, course, section[2])
            break
        
        await asyncio.sleep(randint(35, 45))

def send_notification_email(email, course, section):
    msg = Message("Course Open Notification",
                  sender="noreply@example.com",
                  recipients=[email])
    msg.body = f"The course {course} section {section} is now open!"
    mail.send(msg)

def background_task():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    subscriptions = Subscription.query.all()
    for subscription in subscriptions:
        loop.create_task(check_course(subscription.course, subscription.section_index))
    
    loop.run_forever()

@app.route('/subscribe', methods=['POST'])
def subscribe():
    data = request.json
    email = data['email']
    course = data['course']
    section_index = data['section_index']
    
    subscription = Subscription(email=email, course=course, section_index=section_index)
    db.session.add(subscription)
    db.session.commit()
    
    # Start checking this course if it's not already being checked
    loop = asyncio.get_event_loop()
    loop.create_task(check_course(course, section_index))
    
    return jsonify({"message": "Subscription added successfully"}), 201

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    # Start the background task in a separate thread
    thread = threading.Thread(target=background_task)
    thread.start()
    
    app.run(debug=True)
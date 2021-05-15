from flask import render_template
from flask_mail import Message, Mail

class Email():
    def __init__(self, message, recipients):
        self.message = Message(message, recipients)
    
    def bootstrap(self, path, hospital, name, email, telephone):
        self.message.html = render_template(path, hospital=hospital, name=name, email=email, telephone=telephone)
        return self
    
    def bootstrapReset(self, path, email, emailLink, auxReset):
        self.message.html = render_template(path, email=email, emailLink=emailLink, auxReset=auxReset)
        return self
    
    def sendMail(self, mail):
        try:
            mail.send(self.message)
            return True
        except:
            return False
        
    



    
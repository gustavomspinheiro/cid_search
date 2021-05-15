from flask_login import UserMixin

from cidsystem.source.Core.model import db, datetime, Model
from cidsystem import loginManager
from cidsystem.source.Support.mail import Email

@loginManager.user_loader
def loadUser(userId):
    return User.query.get(int(userId))

#User Class
class User(db.Model, UserMixin):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    surname = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(60), unique=True, nullable=False)
    confirm = db.Column(db.Boolean, nullable=True, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.now)

    def __repr__(self):
        return f"Usuário: {self.name} {self.surname}: {self.email}"
    
    @classmethod
    def bootstrapResetPass(cls, email):
        user = cls.query.filter_by(email=email).first()
        if user:
            email = Email(f"Reset de senha para administrador {user.name} {user.surname}", recipients=[f"{user.email}"])
            return email
        return
        
    @classmethod
    def findByEmail(cls, email):
        user = cls.query.filter_by(email=email).first()
        if user:
            return user
        return

   

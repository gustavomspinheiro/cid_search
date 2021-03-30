from flask_login import UserMixin

from cidsystem.source.Core.model import db, datetime, Model
from cidsystem import loginManager

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

   

from cidsystem.source.Core.model import db, datetime,Model
from datetime import datetime

#Feedback Class
class Feedback(db.Model):
    __tablename__ = 'feedbacks'

    id = db.Column(db.Integer, primary_key=True)
    cid_id = db.Column(db.Integer, db.ForeignKey('cids.id'), nullable=False)
    search = db.Column(db.Text, nullable=False)
    helpfull = db.Column(db.Boolean, nullable=False)
    trained = db.Column(db.Boolean, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __init__(self, _id, search, helpfull):
        self.cid_id = _id
        self.search = search
        self.helpfull = helpfull
        self.trained = False

    def __repr__(self):
        return f"{self.cid_id}: {self.search} | Helpfull: {self.helpfull} | Created At: {self.created_at}"

    #*** CLASSMETHODS ***
    @classmethod
    def findAll(cls):
        return Model.findAll(cls)
    
    @classmethod
    def findHelpfull(cls):
        return cls.query.filter_by(helpfull=True).all()

    #*** METHODS ***
    def saveToDb(self):
        return Model.saveToDb(self)



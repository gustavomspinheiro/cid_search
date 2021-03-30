from cidsystem.source.Core.model import db, datetime,Model

#Feedback Class
class Feedback(db.Model):
    __tablename__ = 'feedbacks'

    id = db.Column(db.Integer, primary_key=True)
    cid_id = db.Column(db.Integer, db.ForeignKey('cids.id'), nullable=False)
    search = db.Column(db.Text, nullable=False)
    helpfull = db.Column(db.Boolean, nullable=False)

    def __init__(self, _id, search, helpfull):
        self.cid_id = _id
        self.search = search
        self.helpfull = helpfull

    def __repr__(self):
        return f"{self.cid_id}: {self.search} | Helpfull: {self.helpfull}"

    #*** METHODS ***
    def saveToDb(self):
        return Model.saveToDb(self)



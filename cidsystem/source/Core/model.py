from datetime import datetime
from cidsystem.db import db


class Model():
    def findAll(self):
        return self.query.all()
    
    def saveToDb(self):
        db.session.add(self)
        db.session.commit()
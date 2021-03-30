from cidsystem.source.Core.Api.model import *
from cidsystem.source.Boot.helpers import *

class Customer(db.Model):
    __tablename__='customers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    admin = db.Column(db.Boolean, nullable=False)

    def __init__(self, username, password, admin=False):
        self.name = username
        self.password = str(passHash(password))
        self.admin = admin
    
    def __str__(self):
        return f"Customer: {self.name}. Admin: {self.admin}"

    #*** CLASSMETHODS ***
    @classmethod
    def findAll(cls):
        return Model.findAll(cls)
    
    def findByName(self, username):
        customer = self.query.filter_by(name=username).first()
        if customer:
            return customer
        else:
            return

    def toJson(self):
        return {
            'username': self.name,
            'admin_approval': self.admin
        }

    def getCustomerData(self, _id):
        customer = self.query.get(_id).first()
        if customer:
            return ModelApi.apiCallback(jsonify(customer), 200, 'Cliente encontrado com sucesso')

        return ModelApi.apiCallback({}, 404, 'Cliente não encontrado')
    

    def saveToDb(self):
        return Model.saveToDb(self)
   

        
    

        
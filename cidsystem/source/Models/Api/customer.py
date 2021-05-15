from cidsystem.source.Support.mail import Email
from cidsystem.source.Core.Api.model import *
from cidsystem.source.Boot.helpers import *

class Customer(db.Model):
    __tablename__='customers'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(30), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    admin = db.Column(db.Boolean, nullable=False)

    def __init__(self, username, password, admin=False):
        self.email = username
        self.password = str(passHash(password))
        self.admin = admin
    
    def __str__(self):
        return f"Customer: {self.email}. Admin: {self.admin}"

    #*** CLASSMETHODS ***
    @classmethod
    def findAll(cls):
        return Model.findAll(cls)
    
    @classmethod
    def bootstrapResetPass(cls, email):
        customer = cls.query.filter_by(email=email).first()
        if customer:
            email = Email(f"Reset de senha para cliente {customer.email}", recipients=[f"{customer.email}"])
            return email
        else:
            return ModelApi.apiCallback({}, 404, 'Cliente não encontrado. Tente outro e-mail')
            
    @classmethod
    def findByName(cls, username):
        customer = cls.query.filter_by(email=username).first()
        if customer:
            return customer

    @classmethod
    def findCustomerToApprove(cls):
        customers = cls.query.filter_by(admin=False).all()
        if customers:
            return customers

    def toJson(self):
        return {
            'username': self.email,
            'admin_approval': self.admin
        }

    def getCustomerData(self, _id):
        customer = self.query.get(_id).first()
        if customer:
            return ModelApi.apiCallback(jsonify(customer), 200, 'Cliente encontrado com sucesso')

        return ModelApi.apiCallback({}, 404, 'Cliente não encontrado')

    def saveToDb(self):
        return Model.saveToDb(self)
   

        
    

        
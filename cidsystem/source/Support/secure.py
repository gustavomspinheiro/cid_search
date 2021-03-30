from cidsystem.source.Models.Api.customer import Customer
from cidsystem.source.Core.Api.model import *
from cidsystem.source.Boot.helpers import checkPass

def authenticate(username, password):
    user = Customer.query.filter_by(name=username).first()
    if user and checkPass(user.password, password):
        return user

def identity(payload):
    userId = payload['identity']
    return Customer.query.get(userId)


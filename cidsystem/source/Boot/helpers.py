from flask import Flask
from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)

#PASSWORD
def passHash(password):
    return bcrypt.generate_password_hash(password).decode('utf-8')

def checkPass(_hash, password):
    return bcrypt.check_password_hash(_hash, password)

def checkPassword(password):
        passwordSize = len(password)
        if passwordSize >= CONF_PASS_MIN_LENGTH and passwordSize <= CONF_PASS_MAX_LENGTH:
            return True
        else:
            return False


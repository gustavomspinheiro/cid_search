import sys

from flask import Flask
from flask_assets import Environment, Bundle
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_jwt import JWT, jwt_required, current_identity

#from cidsystem.source.Models.cid import Cid
#from cidsystem.source.Models.modeltrain import TrainModel
from cidsystem.source.Models.Api.customer import Customer
from cidsystem.source.Support.secure import authenticate, identity
from .db import db

#initialize the app
app = Flask(__name__)

#configurations of the app
app.config['SECRET_KEY'] = 'b\x16\xadA_\xc3\xd9\x06\xc9\xf7h\x99\xb8\xe5v{\x9f\xaeA\xfaR:\xc5\x0c?\x81\xe3\xd2\xb2\xf1x\xdd\x82Zc&\x1b\xaf~Kqo\xbc\xd4\x86\xa8!\xc4H\xf5\xa4\xebP[\xf6VNhfs0u\xb0\xd52'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'

#jwt configuration
jwt = JWT(app, authenticate, identity)

#initialize bcrypt configuration
bcrypt = Bcrypt(app)

#initialize database
db.init_app(app)

#create all tables
@app.before_first_request
def createTables():
    with app.app_context():
        # Customer.__table__.drop(db.engine)
        db.create_all()
       
        # cid1 = Cid('B00', '', 'Infecções Pelo Vírus do Herpes (herpes simples)')
        # cid2 = Cid('A25.0', 'A25', 'Espirilose')
        # train1 = TrainModel(11974, 'Paciente estava grávida e passou mal')
        # cid1.saveToDb()
        # cid2.saveToDb()
        # train1.saveToDb()

#initialize login manager
loginManager = LoginManager()
loginManager.init_app(app)
loginManager.login_view = 'login'

#config minified assets
assets = Environment(app)
minJS = Bundle('shared/scripts/jquery-3.5.1.min.js','shared/scripts/modal-plugin.js', 'shared/scripts/normalize-h.js', 'web/scripts/web_scripts.js', output='minified/jsmin.js')
minCSS = Bundle('shared/styles/styles.css','shared/styles/boot.css','web/styles/web_styles.css', output='minified/stylemin.css')
assets.register('minjs', minJS)
assets.register('mincss', minCSS)
assets.init_app(app)

#import controllers and routes.
from cidsystem.source.Controllers.web import *
from cidsystem.source.Controllers.admin import *
from cidsystem.source.Controllers.api import *
import sys

from flask import Flask
from flask_assets import Environment, Bundle
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_jwt import JWT, jwt_required, current_identity
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect, CSRFError


from cidsystem.source.Models.Api.customer import Customer
from cidsystem.source.Models.feedback import Feedback
from cidsystem.source.Models.modeltrain import TrainModel
from cidsystem.source.Support.secure import authenticate, identity
from cidsystem.source.Support.mail import Email
from cidsystem.source.Boot.config import *
from .db import db

#initialize the app
app = Flask(__name__)

#app settings
app.config['SECRET_KEY'] = 'b\x16\xadA_\xc3\xd9\x06\xc9\xf7h\x99\xb8\xe5v{\x9f\xaeA\xfaR:\xc5\x0c?\x81\xe3\xd2\xb2\xf1x\xdd\x82Zc&\x1b\xaf~Kqo\xbc\xd4\x86\xa8!\xc4H\xf5\xa4\xebP[\xf6VNhfs0u\xb0\xd52'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'

#cookies settings
# app.config.update(
#     SESSION_COOKIE_SECURE=True,
#     SESSION_COOKIE_HTTPONLY=True,
#     SESSION_COOKIE_SAMESITE='Lax'
# )

#initialize CSRF
csrf = CSRFProtect(app)

# Disable pre-request CSRF
app.config['WTF_CSRF_CHECK_DEFAULT'] = False

#configure flask limiter
limiter = Limiter(app, key_func=get_remote_address, default_limits=["2 per second"])

#jwt configuration
jwt = JWT(app, authenticate, identity)

#initialize bcrypt configuration
bcrypt = Bcrypt(app)

#initialize database
db.init_app(app)

#configure e-mail settings
app.config["MAIL_SERVER"] = 'smtp.sendgrid.net'
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config['MAIL_USERNAME'] = 'apikey'
app.config['MAIL_PASSWORD'] = CONF_SENDGRID_API_KEY
app.config['MAIL_DEFAULT_SENDER'] = CONF_SENDGRID_DEFAULT_SENDER
mail = Mail(app)

#create all tables
@app.before_first_request
def createTables():
    with app.app_context():        
        # Customer.__table__.drop(db.engine)
        # TrainModel.__table__.drop(db.engine)
        db.create_all()
        
        # cids = Feedback.findAll()
        # for cid in cids:
        #     print(cid)
        # trainTest = TrainModel.trainPredict(dataFrame, data)
        # feedbacks = Feedback.findAll()
        # for feedback in feedbacks:
        #     print(feedback)
        
        
        # cid1 = Cid('B00', '', 'Infecções Pelo Vírus do Herpes (herpes simples)')
        # cid1.saveToDb()

        # train1 = TrainModel(11974, 'Paciente queria ficar grávida mas teve complicações em procedimento', False)
        # train2 = TrainModel(11974, 'Paciente grávida teve passou mal durante procedimento de inseminação', False)
        # train3 = TrainModel(11974, 'Paciente queria engravidar por inseminação mas teve problemas', False)
        # train4 = TrainModel(11974, 'paciente ficou grávida após inseminação artificial mas apresentou complicações', False)
        # train5 = TrainModel(11781, 'Paciente sofreu com acidente de moto', False)
        # train6 = TrainModel(11781, 'Traumatismo craniano após acidente com veículo', False)
        # train7 = TrainModel(11781, 'Paciente apresentou complicações após acidente de carro', False)
        # train8 = TrainModel(11781, 'Paciente com hemorragia interna após cair de moto', False)

        # train1.saveToDb()
        # train2.saveToDb()
        # train3.saveToDb()
        # train4.saveToDb()
        # train5.saveToDb()
        # train6.saveToDb()
        # train7.saveToDb()
        # train8.saveToDb()

        # cids = TrainModel.findAll()
        # print("below cids")
        # print(cids)

#set functions performed after each request
@app.after_request
def add_security_headers(resp):
    resp.headers['Content-Security-Policy']='default-src \'self\'; font-src https://fonts.gstatic.com https://fonts.googleapis.com/ \'self\';style-src https://fonts.googleapis.com/ \'self\' \'unsafe-inline\'; script-src \'self\';img-src \'self\' data:'
    resp.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    resp.headers['X-Content-Type-Options'] = 'nosniff'
    resp.headers['X-Frame-Options'] = 'SAMEORIGIN'
    resp.headers['X-XSS-Protection'] = '1; mode-block'
    return resp

#customize CSRF Error response
@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return  jsonify({"redirect": url_for('renderError')}) 

#initialize login manager
loginManager = LoginManager()
loginManager.init_app(app)
loginManager.login_view = 'login'

#config minified assets
assets = Environment(app)
minJS = Bundle('shared/scripts/jquery-3.5.1.min.js','shared/scripts/modal-plugin.js', 'shared/scripts/reset-modal-plugin.js', 'shared/scripts/normalize-h.js', 'web/scripts/web_scripts.js', output='minified/jsmin.js')
minCSS = Bundle('shared/styles/styles.css','shared/styles/boot.css','web/styles/web_styles.css','admin/styles/admin_styles.css', output='minified/stylemin.css')
assets.register('minjs', minJS)
assets.register('mincss', minCSS)
assets.init_app(app)

#import controllers and routes.
from cidsystem.source.Controllers.web import *
from cidsystem.source.Controllers.admin import *
from cidsystem.source.Controllers.api import *
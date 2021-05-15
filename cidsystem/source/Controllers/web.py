import json, secrets, base64
from flask import flash, jsonify, request, render_template, url_for, redirect, session
from flask_login import login_user, current_user, logout_user, login_required
from joblib import load

import time

from cidsystem import app, db, mail
from cidsystem.source.Boot.helpers import passHash, checkPass
from cidsystem.source.Boot.config import *
from cidsystem.source.Support.message import Message
from cidsystem.source.Support.authforms import RegistrationForm, LoginForm
from cidsystem.source.Support.mail import Email
from cidsystem.source.Models.user import User
from cidsystem.source.Models.cid import Cid
from cidsystem.source.Models.modeltrain import TrainModel
from cidsystem.source.Models.Api.customer import Customer
from cidsystem.source.Models.feedback import Feedback


#***INDEX RENDER***#
@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('index.html', title=CONF_HOME_TITLE)

#***SEARCH ROUTES (TEXT)***#
@app.route('/busca-cid' , methods=['GET', 'POST'])
def searchText():
    if request.method == 'POST':
        search = request.form["search_text"]
        if search:
            return jsonify({'redirect': url_for('searchTextRes', search=search, page_num=1)})
        else:
            return jsonify({'message': Message('Oops! Favor incluir o texto para busca').alert().render()})
    return render_template('text-search.html', title='Busca de Cids') 

@app.route('/busca-cid-resultado/<search>/<page_num>', methods=['GET', 'POST'])
def searchTextRes(search, page_num):
    cidsSearched = Cid.searchByText(search, int(page_num))
    return render_template('text-search.html', title='Resultados da Busca', cids=cidsSearched, search=search) 

#***SEARCH ROUTES (RECOMMENDATION)***#
@app.route('/search-recom', methods = ['GET', 'POST'])
def searchRecom():
    data = request.form["case_desc"]
    if data:
        session["case_desc"] = data 
        start = time.time()

        dataFrame = TrainModel.generateDataframe()
        prediction = TrainModel.trainPredict(dataFrame, data)
        
        # classifier = load('cidsystem/persist/model.joblib')
        # vectorizer = load('cidsystem/persist/vector.joblib')
        # prediction = TrainModel.predictSentence([data], classifier, vectorizer)

        f1 = load('cidsystem/persist/f1-score.joblib')
        print("f1 Joblib: {}".format(f1))

        end = time.time()
        diff = end - start
        print("Time:")
        print(diff)

        if prediction:
            predictedCid = Cid.searchById(int(prediction[0]))
            session["predicted"] = predictedCid.serialize
            return jsonify({'redirect': url_for('result')})
    else:
        message = Message('Favor inserir a descrição para busca').info().render()
        return jsonify({'message': message})

@app.route('/result')
def result():
    cidRecommended = session.get("predicted")
    description = session.get("case_desc")
    resultTitle = "Cids Recomendados"
    f1Score = load('cidsystem/persist/f1-score.joblib')
    return render_template('result.html', title=resultTitle, cid=cidRecommended, case_desc=description, f1_score=f1Score, target_score=CONF_MODEL_F1_SCORE)

#***FEEDBACK ROUTES***#
@app.route('/collect-feedback', methods=["POST"])
def collectFeedback():
    form = request.form
    code = form["cid"]
    caseDescription = form["case_description"]
    helpfull = bool(form["aux_feedback"])

    cid = Cid.searchByCode(code)
    
    if not cid:
        return jsonify({'message': Message('Oops! Cid não encontrado').alert().render()})
    
    feedback = Feedback(cid.id, caseDescription, helpfull)
    try:
        feedback.saveToDb()
        return jsonify({'message': Message('Agradecemos seu feedback. Volte sempre :)').success().render()})
    except:
        return jsonify({'message': Message('Oops! Ocorreu um erro. Tente novamente mais tarde').error().render()})


#***ADMIN REGISTRATION ROUTES***#
@app.route('/cadastro-admin', methods=['GET', 'POST'])
def admin_register():
    regForm = RegistrationForm(request.form)
    if request.method == 'POST':
        if not regForm.validateByEmail(regForm.adminEmail.data):
            flash(f"Oops! O e-mail já foi cadastrado", 'alert');
            return jsonify({'reload': True});

        if regForm.validate_on_submit():
            pHash = passHash(regForm.adminPass.data)
            user = User(name=regForm.adminName.data, surname=regForm.adminSurname.data, email=regForm.adminEmail.data, password=pHash)
            db.session.add(user)
            db.session.commit()
            flash(f'Conta criada para {regForm.adminName.data} :)', 'success')
            return jsonify({'reload': True})
        else:
            for error in regForm.errors.items():
                flash(f"Oops! {error[1][0]} =/", 'alert')
                return jsonify({'reload': True})
    if current_user.is_authenticated:
        return render_template('admin/home.html')
    return render_template('admin-register.html', title=CONF_REGISTER_TITLE, form=regForm)    
    
@app.route('/login-admin')
def admin_login():
    loginForm = LoginForm()
    if current_user.is_authenticated:
        return render_template('admin/home.html')
    return render_template('admin-login.html', title=CONF_LOGIN_TITLE, form=loginForm)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        logForm = LoginForm(request.form)
        if logForm.validate_on_submit():
            user = User.query.filter_by(email=logForm.adminEmail.data).first()
            if user and checkPass(user.password, logForm.adminPass.data):
                login_user(user, remember=logForm.remember.data)
                flash(f'Login realizado com sucesso {user.name} :)', 'success')
                return jsonify({'redirect': url_for('adminHome')})   
            else:
                flash(f'Oops! E-mail ou senha incorretos', 'alert');
                return jsonify({'reload': True})

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

#***PASSWORD RESET ROUTES***#
@app.route('/admin/reset-senha', methods=['POST'])
def initAdminReset():
    email = request.form["admin_email"]
    emailBytes = email.encode('ascii')
    base64Bytes = base64.b64encode(emailBytes)
    link = base64Bytes.decode('ascii')

    bootstrap = User.bootstrapResetPass(email)
    checkClass = isinstance(bootstrap, Email)
    if checkClass:
        bootstrap.bootstrapReset('support/reset-password.html', email, link, "admin")
        if bootstrap.sendMail(mail):
            return jsonify({'message': Message("Um e-mail com as instruções para reset de senha foi enviado :)").success().render()}) 
        return jsonify({'message': Message("Erro ao enviar o e-mail. Tente mais tarde").error().render()})
    return jsonify({'message': Message("Oops! Cliente não foi encontrado. Digite outro e-mail").alert().render()})

@app.route('/confirmacao-reset-senha/<email>/<auxReset>', methods=['GET', 'POST'])
def resetPass(email, auxReset):
    base64Bytes = email.encode('ascii')
    emailBytes = base64.b64decode(base64Bytes)
    username = emailBytes.decode('ascii')

    if auxReset == "admin":
        checkUser = User.findByEmail(username)
    
    if auxReset == "customer":
        checkUser = Customer.findByName(username)

    if checkUser:
        return render_template('support/confirm-password-reset.html', title='Reset de Senha', user=checkUser.email)
    else:
        return render_template('error.html', title="Erro no sistema", reason="usuário não encontrado")

@app.route('/processar-reset-senha', methods=['POST'])
def processReset():
    username = request.form["pass_reset_email"]
    password = request.form["pass_reset_password"]
    confirmPass = request.form["pass_reset_confirm_password"]

    passSize = len(password)

    if not username:
        return jsonify({'message': Message('Oops! Usuário inexistente').alert().render()})
    
    if passSize < CONF_PASS_MIN_LENGTH or passSize > CONF_PASS_MAX_LENGTH:
        return jsonify({'message': Message(f"Oops! A senha precisa conter entre {CONF_PASS_MIN_LENGTH} e {CONF_PASS_MAX_LENGTH} caracteres").alert().render()})
    
    user = User.findByEmail(username)
    if user is None:
        user = Customer.findByName(username)

    if user:
        if password != confirmPass:
            return jsonify({'message': Message('Oops! A senha e confirmação de senha precisam ser iguais').alert().render()})
        try:
            user.password = passHash(password)
            db.session.commit()
            return jsonify({'message': Message('Senha redefinida com sucesso').success().render()})
        except:
            return jsonify({'message': Message('Oops! Erro ao processar os dados. Tente novamente mais tarde').error().render()})
    else:
        return jsonify({'message': Message('Oops! Usuário não encontrado').alert().render()})
    

#***API PAGE ROUTES***#
@app.route('/api-cid', methods=['GET'])
def renderApi():
    return render_template('api-cid.html')

@app.route('/api-integration-contact', methods=['POST'])
def postContact():
    hospitalName = request.form["contact_api_hospital"]
    prospectName = request.form["contact_api_name"]
    prospectEmail = request.form["contact_api_email"]
    prospectTel = request.form["contact_api_tel"]
    email = Email(f"Contato para Integração: {hospitalName}", recipients=['melhorcid@gmail.com'])
    checkMail = email.bootstrap('support/api-contact-email.html', hospitalName, prospectName, prospectEmail, prospectTel).sendMail(mail)
    if checkMail:
        return jsonify({'message': Message('Contato enviado com sucesso').success().render()})
    else:
        return jsonify({'message': Message('Oops! Não foi possível enviar o e-mail. Tente novamente mais tarde').error().render()})

#***ERROR ROUTES***#
@app.route('/error', methods=['GET'])
def renderError():
    return render_template('error.html', title="Erro no Sistema")
    
    


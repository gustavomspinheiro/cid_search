import json, secrets
from flask import flash, jsonify, request, render_template, url_for, redirect, session
from flask_login import login_user, current_user, logout_user, login_required

from cidsystem import app, db
from cidsystem.source.Boot.helpers import passHash, checkPass
from cidsystem.source.Boot.config import *
from cidsystem.source.Support.message import Message
from cidsystem.source.Support.authforms import RegistrationForm, LoginForm
from cidsystem.source.Models.user import User
from cidsystem.source.Models.cid import Cid
from cidsystem.source.Models.modeltrain import TrainModel
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
        dataFrame = TrainModel.generateDataframe()
        prediction = TrainModel.trainPredict(dataFrame, data)
        session["case_desc"] = data    

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
    return render_template('result.html', title=resultTitle, cid=cidRecommended, case_desc=description)

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


#***REGISTRATION ROUTES***#
@app.route('/cadastro-admin', methods=['GET', 'POST'])
def admin_register():
    regForm = RegistrationForm(request.form)
    if request.method == 'POST':
        if not regForm.validateByEmail(regForm.adminEmail.data):
            flash(f"Oops! O e-mail já foi cadastrado. Tente outro e-mail", 'message_error');
            return jsonify({'reload': True});

        if regForm.validate_on_submit():
            pHash = passHash(regForm.adminPass.data)
            user = User(name=regForm.adminName.data, surname=regForm.adminSurname.data, email=regForm.adminEmail.data, password=pHash)
            db.session.add(user)
            db.session.commit()
            flash(f'Conta criada para {regForm.adminName.data} :)', 'message_success')
            return jsonify({'reload': True})
        else:
            for error in regForm.errors.items():
                flash(f"Oops! {error[1][0]} =/", 'message_error')
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
    logForm = LoginForm(request.form)
    if logForm.validate_on_submit():
        user = User.query.filter_by(email=logForm.adminEmail.data).first()
        if user and checkPass(user.password, logForm.adminPass.data):
            login_user(user, remember=logForm.remember.data)
            flash(f'Login realizado com sucesso {user.name} :)', 'message_success')
            return jsonify({'redirect': url_for('adminHome')})   
        else:
            flash(f'Oops! E-mail ou senha incorretos', 'message_error');
            return jsonify({'reload': True})

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

#***API PAGE ROUTES***#
@app.route('/api-cid', methods=['GET'])
def renderApi():
    return render_template('api-cid.html')


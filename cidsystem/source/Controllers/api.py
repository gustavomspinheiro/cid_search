import base64
from flask import flash, jsonify, request, render_template, url_for, redirect, session
from flask_jwt import JWT, jwt_required, current_identity

from cidsystem import app, db, jwt, mail, csrf, limiter
from cidsystem.source.Boot.config import *
from cidsystem.source.Models.Api.customer import Customer
from cidsystem.source.Core.Api.model import ModelApi
from cidsystem.source.Models.cid import Cid
from cidsystem.source.Models.modeltrain import TrainModel
from cidsystem.source.Support.mail import Email


#create a user
@app.route('/api/registrar-cliente', methods=['POST'])
@limiter.limit("3 per day", error_message=ModelApi.requestLimitError("3", "dia"))
def createCustomer():
    data = request.get_json()
    passSize = len(str(data["password"]))
    customer = Customer(data['email'], str(data['password']), admin=False)

    if passSize < CONF_PASS_MIN_LENGTH or passSize > CONF_PASS_MAX_LENGTH:
        return ModelApi.apiCallback(customer.toJson(), 400, f"A senha precisa conter entre {CONF_PASS_MIN_LENGTH} e {CONF_PASS_MAX_LENGTH} caracteres")

    customerExists = customer.findByName(customer.email)
    if customerExists:
        return ModelApi.apiCallback(customer.toJson(), 400, 'Cliente já existe na base de dados :)')

    if customer:
        try:
            customer.saveToDb()
            return ModelApi.apiCallback(customer.toJson(), 200, 'Cliente salvo com sucesso!Aguarde o administrador do sistema te aprovar')
        except:
            return ModelApi.apiCallback({}, 500, 'Erro ao processar os dados. Tente novamente mais tarde')
    return ModelApi.apiCallback({}, 404, 'Erro ao processar. Verifique os dados')

#reset a user password
@app.route('/api/reset-senha', methods=['POST'])
@limiter.limit("20 per day", error_message=ModelApi.requestLimitError("2", "dia"))
def initReset():
    data = request.get_json()
    username = data["username"]      
    usernameBytes = username.encode('ascii')
    base64Bytes = base64.b64encode(usernameBytes)
    link = base64Bytes.decode('ascii')

    bootstrap = Customer.bootstrapResetPass(username)
    checkClass = isinstance(bootstrap, Email)
    if checkClass:
        bootstrap.bootstrapReset('support/reset-password.html', username, link, "customer")
        if bootstrap.sendMail(mail):
            return ModelApi.apiCallback({}, 200, 'Um e-mail com as instruções para redefinir sua senha foi enviado :)')
        return ModelApi.apiCallback({}, 500, 'Erro ao enviar o e-mail. Tente novamente mais tarde :/')
    return ModelApi.apiCallback({}, 400, 'Cliente não foi encontrado. Favor tentar outro e-mail :)') 

#get the recommended Cid
@app.route('/api/recomendar-cid', methods=['POST'])
@limiter.limit("1 per second", error_message=ModelApi.requestLimitError("1", "segundo"))
@jwt_required()
def recommedCid():
    if not current_identity.admin:
        return ModelApi.apiCallback({}, 404, 'Cliente ainda não foi autorizado. Aguarde mais um pouco ou entre em contato pelos canais de atendimento')
    
    data = request.get_json()
    caseToPredict = data["case_desc"]

    if not isinstance(caseToPredict, str):
        return ModelApi.apiCallback({}, 404, 'O formato da busca precisa ser um texto. Tente novamente :)')

    dataFrame = TrainModel.generateDataframe()
    prediction = TrainModel.trainPredict(dataFrame, caseToPredict)

    if prediction:
        predictedCid = Cid.searchById(int(prediction[0]))
        return ModelApi.apiCallback(predictedCid.serialize, 200, 'Cid recomendado com sucesso')
    return ModelApi.apiCallback({}, 200, 'Infelizmente não possuimos recomendações para esse caso')
        


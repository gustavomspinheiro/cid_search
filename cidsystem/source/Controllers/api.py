from flask import flash, jsonify, request, render_template, url_for, redirect, session
from flask_jwt import JWT, jwt_required, current_identity

from cidsystem import app, db, jwt
from cidsystem.source.Models.Api.customer import Customer
from cidsystem.source.Core.Api.model import ModelApi
from cidsystem.source.Models.cid import Cid
from cidsystem.source.Models.modeltrain import TrainModel


#create a user
@app.route('/api/registrar-cliente', methods=['POST'])
def createCustomer():
    data = request.get_json()
    customer = Customer(data['name'], str(data['password']), admin=True)

    customerExists = customer.findByName(customer.name)
    if customerExists:
        return ModelApi.apiCallback(customer.toJson(), 404, 'Cliente já existe na base de dados :)')

    if customer:
        try:
            customer.saveToDb()
            return ModelApi.apiCallback(customer.toJson(), 200, 'Cliente salvo com sucesso!')
        except:
            return ModelApi.apiCallback({}, 500, 'Erro ao processar os dados. Tente novamente mais tarde')
    return ModelApi.apiCallback({}, 404, 'Erro ao processar. Verifique os dados')
        
#get the recommended Cid
@app.route('/api/recomendar-cid', methods=['POST'])
@jwt_required()
def recommedCid():
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
        


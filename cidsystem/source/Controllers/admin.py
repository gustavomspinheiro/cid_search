import numpy as np
from flask import flash, jsonify, request, render_template, url_for, redirect
from flask_login import login_user, current_user, logout_user, login_required
from joblib import load, dump

from cidsystem import app, db, bcrypt, loginManager
from cidsystem.source.Models.feedback import Feedback
from cidsystem.source.Models.modeltrain import TrainModel
from cidsystem.source.Models.Api.customer import Customer
from cidsystem.source.Support.message import Message
from cidsystem.source.Models.cid import Cid

#***RENDER ADMIN HOME***#
@app.route('/admin/home', methods=['GET'])
@login_required
def adminHome():
    customersToBeApproved = Customer.findCustomerToApprove()
    return render_template('admin/home.html', customersToBeApproved=customersToBeApproved)

#***PARTIAL TRAIN MODEL***#
@app.route('/admin/feedback-modelo', methods=['GET', 'POST'])
@login_required
def retrainModel():
    #get positive feedbacks to populate number of cases to be retrained
    positiveFeedbacks = Feedback.findHelpfull()
    if positiveFeedbacks:
        for positiveFeedback in positiveFeedbacks:
            caseToInput = TrainModel(positiveFeedback.cid_id, positiveFeedback.search, True, False)
            if TrainModel.findByCase(positiveFeedback.search) is None:
                caseToInput.saveToDb()

    classifier = load('cidsystem/persist/model.joblib')
    vectorizer = load('cidsystem/persist/vector.joblib')
    
    classes = TrainModel.findCidIds()
    caseArray, answerArray = TrainModel.generateNewTestTrain()
    npAnswerArray = np.array(answerArray)
    caseTest = vectorizer.transform(caseArray)
    classifier.partial_fit(caseTest, npAnswerArray, classes=classes)
    dump(vectorizer, 'cidsystem/persist/vector.joblib')
    dump(classifier, 'cidsystem/persist/model.joblib')
    
    flash("Classificador atualizado :)", "success")
    return jsonify({'reload': True})
    
@app.route('/admin/atualizar-metricas', methods=['GET', 'POST'])
@login_required
def updateMetrics():
    dataFrame = TrainModel.generateDataframe()
    vectorizer = load('cidsystem/persist/vector.joblib')
    allFeatures, vectorizer = TrainModel.prepareVocabulary(dataFrame, vectorizer)
    trainResult = TrainModel.train(allFeatures, dataFrame.cid_id)
    classifier = load('cidsystem/persist/model.joblib')


    recallScore = TrainModel.recallScore(classifier, trainResult)
    precisionScore = TrainModel.precisionScore(classifier, trainResult)
    f1Score = TrainModel.f1Score(classifier, trainResult)

    print(f"Recall: {recallScore}")
    print(f"Precision: {precisionScore}")
    print(f"F1: {f1Score}")

    dump(f1Score, 'cidsystem/persist/f1-score.joblib')
    flash("Métricas atualizadas :)", "success")
    return jsonify({'reload': True})

@app.route('/admin/aprovar-cliente', methods=['POST'])
@login_required
def approveCustomer():
    data = request.form
    email = data['customer_email']
    customer = Customer.findByName(email)
    if customer:
        customer.admin = True
        customer.saveToDb()
        flash("Cliente aprovado :)", "success")
    else:
        flash("Oops! Ocorreu algum erro", "error")
    return jsonify({'reload': True})

@loginManager.unauthorized_handler
def unauthorizedLogin():
    flash(f'Favor realizar o login para acessar a área administrativa', 'info')
    return redirect(url_for('admin_login'))
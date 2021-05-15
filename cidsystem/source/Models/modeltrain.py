import pandas as pd
import numpy as np
from datetime import datetime

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import recall_score, precision_score, f1_score
from joblib import dump

from cidsystem.source.Core.model import db, datetime, Model

#Train Model Class
class TrainModel(db.Model, Model):

    __tablename__='model_train'

    id = db.Column(db.Integer, primary_key=True)
    cid_id = db.Column(db.Integer, db.ForeignKey('cids.id'), nullable=False)
    case = db.Column(db.Text, nullable=False)
    feedback_source = db.Column(db.Boolean, nullable=False, default=False)
    trained = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    #*** INIT AND REPRESENTATION ***
    def __init__(self, cid_id, case, feedback_source, trained=False):
        self.cid_id = cid_id
        self.case = case
        self.feedback_source = feedback_source
        self.trained = trained
    
    def __repr__(self):
        return f"{self.cid_id}: {self.case} | Trained? {self.trained}"
    
    #*** PROPERTIES ***
    @property
    def serialize(self):
        return {
            'id': self.id,
            'cid_id': self.cid_id,
            'case': self.case,
            'trained': self.trained
        }

    #*** CLASSMETHODS ***
    @classmethod
    def findAll(cls):
        return Model.findAll(cls)
    
    @classmethod
    def findCidIds(cls):
        testTrainData = cls.query.all()
        classificationArray = []
        for data in testTrainData:
            if data.cid_id not in classificationArray:
                classificationArray.append(data.cid_id)
        return classificationArray

    @classmethod
    def generateNewTestTrain(cls):
        caseArray = []
        answerArray = []
        testTrainData = cls.findNotTrained()
        for testTrain in testTrainData:
            caseArray.append(testTrain.case)
            answerArray.append(testTrain.cid_id)
        return caseArray, answerArray


    @classmethod
    def findByCase(cls, case):
        return cls.query.filter_by(case=case).first()
    
    @classmethod
    def findNotTrained(cls):
        return cls.query.filter_by(trained=False).all()
    
    @classmethod
    def generateDataframe(cls):
        cids = cls.findAll()
        if cids:
            jsonResults = []
            for cid in cids:
                jsonResults.append(cid.serialize)
            return pd.json_normalize(jsonResults)
        return
    
    @classmethod
    def generateDataframeNotTrained(cls):
        cids = cls.findNotTrained()
        if cids:
            jsonResults = []
            for cid in cids:
                jsonResults.append(cid.serialize)
            return pd.json_normalize(jsonResults)
        return
    
    @classmethod
    def updateTraining(cls):
        cids = cls.findAll()
        if cids:
            for cid in cids:
                cid.trained = True
                db.session.commit()
        return True
    
    @classmethod
    def trainPredict(cls, dataFrame, sentence):
        if not dataFrame.empty:
            vectorizer = cls.initVectorizer()
            allFeatures, vectorizer = cls.prepareVocabulary(dataFrame, vectorizer)
            trainResult = cls.train(allFeatures, dataFrame.cid_id)
            classification = cls.classify(trainResult)
            score = cls.score(classification, trainResult)
            recallScore = cls.recallScore(classification, trainResult)
            precisionScore = cls.precisionScore(classification, trainResult)
            f1Score = cls.f1Score(classification, trainResult)
            print(f"Score: {score}")
            print(f"Recall: {recallScore}")
            print(f"Precision: {precisionScore}")
            print(f"F1: {f1Score}")
            dump(vectorizer, 'cidsystem/persist/vector.joblib')
            dump(classification, 'cidsystem/persist/model.joblib')
            dump(f1Score, 'cidsystem/persist/f1-score.joblib')
            # updateTraining = cls.updateTraining()
            prediction = cls.predictSentence([sentence], classification, vectorizer)
            if prediction:
                return prediction
            return
        return
        
    #*** METHODS ***
    def saveToDb(self):
        return Model.saveToDb(self)

    #initiates the vectorizer and desconsider stop words.
    def initVectorizer():
        vectorizer = CountVectorizer(stop_words=["a", "A", "o", "O", ".", ",", "paciente", "Paciente", "de", "está", "esta", "com", "possui"])
        return vectorizer

    #fit_transform makes our vectorizer to learn the vocabulary. Generates the tokens (matrix: individual words vs cases )
    def prepareVocabulary(data, vectorizer):
        allFeatures = vectorizer.fit_transform(data.case)
        return allFeatures, vectorizer
    
    #split and shuffle training and testing data. Test size 33%. Means that part of the data will be for training and part testing data.
    def train(allFeatures, answer):
        X_train, X_test, y_train, y_test = train_test_split(allFeatures, answer, test_size=0.33, random_state=88)
        return [X_train, X_test, y_train, y_test]
    
    #fit will train our model with x_train (train data) and y_train (train label). Predict performs a classification into an array of test data.
    def classify(trainResult):
        classifier = MultinomialNB()
        classifier.fit(trainResult[0], trainResult[2])
        nrCorrect = (trainResult[3] == classifier.predict(trainResult[1])).sum()
        nrIncorrect = trainResult[3].size - nrCorrect
        percent = f"{(nrCorrect / (nrIncorrect + nrCorrect))*100}% of documents classified correctly"
        return classifier

    #transform is the method to process the sentence. Predict returns an array with the results of the prediction.
    def predictSentence(sentence, classifier, vectorizer):
        docTerm = vectorizer.transform(sentence)
        return classifier.predict(docTerm)
    
    #overall method accuracy. Good predictions divided by total number of predictions
    def score(classifier, trainResult):
        return classifier.score(trainResult[1], trainResult[3])
    
    #recall score: of all of my "cid1" data, how many did we classified as "cid1"? How many cid1 did we get versus we miss?
    #formula: TP/(TP + FN) - true positives and false negatives
    #definition by towardsdatascience.com: ability of classification model to identify all relevant instances
    def recallScore(classifier, trainResult):
        return recall_score(trainResult[3], classifier.predict(trainResult[1]), average="macro")

    #precision score: number of good cid1 predictions divided by total cid1 predictions (true positives and false positives)
    #formula: TP/(TP + FP) - true positives and false positives
    #definition by towardsdatascience.com: ability of classification model to return only relevant instances
    def precisionScore(classifier, trainResult):
        return precision_score(trainResult[3], classifier.predict(trainResult[1]), average="macro")
    
    #f1 score: single metric that combines recall and precision using harmonic mean
    def f1Score(classifier, trainResult):
        return f1_score(trainResult[3], classifier.predict(trainResult[1]), average="macro")
    

    

    
    

    





   
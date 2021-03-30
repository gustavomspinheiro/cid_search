import pandas as pd

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB

from cidsystem.source.Core.model import db, datetime, Model

#Train Model Class
class TrainModel(db.Model, Model):

    __tablename__='model_train'

    id = db.Column(db.Integer, primary_key=True)
    cid_id = db.Column(db.Integer, db.ForeignKey('cids.id'), nullable=False)
    case = db.Column(db.Text, nullable=False)

    #*** INIT AND REPRESENTATION ***
    def __init__(self, cid_id, case):
        self.cid_id = cid_id
        self.case = case
    
    def __repr__(self):
        return f"{self.cid_id}: {self.case}"
    
    #*** PROPERTIES ***
    @property
    def serialize(self):
        return {
            'id': self.id,
            'cid_id': self.cid_id,
            'case': self.case,
        }

    #*** CLASSMETHODS ***
    @classmethod
    def findAll(cls):
        return Model.findAll(cls)
    
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
    def trainPredict(cls, dataFrame, sentence):
        if not dataFrame.empty:
            vectorizer = cls.initVectorizer()
            allFeatures, vectorizer = cls.prepareVocabulary(dataFrame, vectorizer)
            trainResult = cls.train(allFeatures, dataFrame.cid_id)
            classification = cls.classify(trainResult)
            prediction = cls.predictSentence([sentence], classification, vectorizer)
            if prediction:
                return prediction
            return
        return
        
    
    #*** METHODS ***
    def saveToDb(self):
        return Model.saveToDb(self)

    def initVectorizer():
        vectorizer = CountVectorizer(stop_words=["a", "A", "o", "O", ".", ",", "paciente", "Paciente", "de", "está", "esta", "com", "possui"])
        return vectorizer

    def prepareVocabulary(data, vectorizer):
        allFeatures = vectorizer.fit_transform(data.case)
        return allFeatures, vectorizer
    
    def train(allFeatures, answer):
        X_train, X_test, y_train, y_test = train_test_split(allFeatures, answer, test_size=0.33, random_state=88)
        return [X_train, X_test, y_train, y_test]
    
    def classify(trainResult):
        classifier = MultinomialNB()
        classifier.fit(trainResult[0], trainResult[2])
        nrCorrect = (trainResult[3] == classifier.predict(trainResult[1])).sum()
        nrIncorrect = trainResult[3].size - nrCorrect
        percent = f"{(nrCorrect / (nrIncorrect + nrCorrect))*100}% of documents classified correctly"
        return classifier

    def predictSentence(sentence, classifier, vectorizer):
        docTerm = vectorizer.transform(sentence)
        return classifier.predict(docTerm)
    
    

    





   
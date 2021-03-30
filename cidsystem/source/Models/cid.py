from spellchecker import SpellChecker

from cidsystem.source.Core.model import db, datetime, Model
from cidsystem.source.Models.modeltrain import TrainModel

#Cid Class
class Cid(db.Model, Model):
    __tablename__='cids'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(15), nullable=False, unique=True)
    relation = db.Column(db.String(15), nullable=True)
    desc = db.Column(db.Text, nullable=False)
    trainings = db.relationship('TrainModel', backref='cid', lazy=True)
    # feedbacks = db.relationship('Feedback', backref='cid', lazy=True)

    #*** INIT AND REPRESENTATION ***
    def __init__(self, code, relation, desc):
        self.code = code
        self.relation = relation
        self.desc = desc
    
    def __repr__(self):
        return f"{self.code}: {self.desc}"

    #*** PROPERTIES ***
    @property
    def serialize(self):
        return {
            'id': self.id,
            'code': self.code,
            'relation': self.relation,
            'desc': self.desc
        }

    #*** CLASSMETHODS ***
    @classmethod
    def findAll(cls):
        return Model.findAll(cls)

    @classmethod
    def searchByText(cls, name, page_num):
        nameRevised = '%{}%'.format(name)
        result= cls.query.filter(cls.desc.ilike(nameRevised)).first()

        if result:
            resultRev = cls.query.filter(cls.desc.ilike(nameRevised)).paginate(per_page=4, page=page_num)
            return resultRev
        else:
            tokenized = name.split()
            spell = SpellChecker(language="pt")
            correctWord = ''
        
            for i in range(len(tokenized)):
                size = len(spell.known([tokenized[i]]))
                if size > 0:
                    correctWord += f"{tokenized[i]}"
                else:
                    correctWord += f"{spell.correction(tokenized[i])}"
            nameCorrected = '%{}%'.format(correctWord)
            result = cls.query.filter(cls.desc.ilike(nameCorrected)).paginate(per_page=3, page=page_num)
            return result
    
    @classmethod
    def searchByCode(cls, cid_code):
        result = cls.query.filter_by(code=cid_code).first()
        return result

    @classmethod
    def searchById(cls, id_):
        result = cls.query.get(id_)
        return result

    @classmethod
    def toJson(self):
        return jsonify(self.findAll())

    #*** METHODS ***
    def saveToDb(self):
        return Model.saveToDb(self)

   

    
    

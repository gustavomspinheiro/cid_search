from cidsystem.source.Core.model import db, datetime, Model

class ModelApi():
    def apiCallback(objectResponse, status, message):
        return {
            'response': objectResponse,
            'status': status,
            'message': message
        }

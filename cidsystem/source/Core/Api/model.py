from cidsystem.source.Core.model import db, datetime, Model

class ModelApi():
    def apiCallback(objectResponse, status, message):
        return {
            'response': objectResponse,
            'status': status,
            'message': message
        }

    def requestLimitError(limit = '1', time = 'segundo'):
        return f"Número de requisições atingido: {limit} por {time}"

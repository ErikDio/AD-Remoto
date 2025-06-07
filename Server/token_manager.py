from datetime import datetime

class TokenManager:
    token:dict = {}
    @classmethod
    def validate(cls, request_token):
        try:
            if cls.token[request_token]["expires"] < now:
                return "placeholder"
        except KeyError:
            return "error"

    @classmethod
    def add_token(cls, request_token, object_id):
        expiration = placeholder
        cls.token[request_token] = {"expires":expiration, "object":object_id}
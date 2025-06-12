import time

class TokenManager:
    token:dict = {}
    @classmethod
    def validate(cls, request_token) -> str:
        try:
            if cls.token[request_token]["expires"] < time.time():
                return "placeholder"
            else:
                cls.token[request_token]["expires"] = expiration_time()
                return "placeholder"
        except KeyError:
            return "error"

    @classmethod
    def add_token(cls, request_token, object_id):
        expiration = expiration_time()
        cls.token[request_token] = {"expires":expiration, "object":object_id}

def expiration_time() -> float:
    return time.time() + (30*60)
import secrets

class TokenManager:
    token:str = None

    @classmethod
    def set_token(cls):
        cls.token = secrets.token_hex(32)
    
    @classmethod
    def get_token(cls):
        if cls.token != None:
            return cls.token
        raise ValueError("Token inválido")

    @classmethod
    def clear_token(cls):
        cls.token = None
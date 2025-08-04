import secrets

class TokenManager:
    token:str = None

    @classmethod
    def set_token(cls) -> None:
        cls.token = secrets.token_hex(32)
    
    @classmethod
    def get_token(cls) -> str:
        if cls.token != None:
            return cls.token
        raise ValueError("Invalid Token")

    @classmethod
    def clear_token(cls) -> None:
        cls.token = None
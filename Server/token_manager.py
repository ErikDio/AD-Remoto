import time
from Shared.operations import *

class TokenManager:
    
    token:dict = {}

    @classmethod
    def validate(cls, request_token:str) -> str:
        try:
            if cls.token[request_token]["expires"] < time.time():
                return ErrorList.EXPIRED_TOKEN
            else:
                return ReturnList.OPERATION_OK
        except KeyError:
            return ErrorList.INVALID_TOKEN
        
    @classmethod
    def auth(cls, request_token:str) -> str:
        validation = cls.validate(request_token)
        if (validation == ReturnList.OPERATION_OK):
            cls.token[request_token]["expires"] = expiration_time()
        return validation
    
    @classmethod
    def add_token(cls, request_token:str):
        expiration:float = expiration_time()
        cls.token[request_token] = {"expires":expiration}

def expiration_time() -> float:
    return time.time() + (30*60)
import time
from typing import TypedDict
from Shared.operations import *
import ad_helper
import threading

class SessionDict(TypedDict):
        user: str
        expires: float
        session: ad_helper.Operation

class TokenManager:
    
    token:dict[str, SessionDict] = {} # Example: token{"token":{"user":"Erik Dio", "expires":123.123, "session":ad_helper_session}}
    def __init__(self):
        self.thread = threading.Thread(target=self.monitor_token, daemon=True)
        self.thread.run()

    def monitor_token(self):
        while True:
            time.sleep(1)
            for tokens in self.token.keys():
                self.validate(tokens)
                

    @classmethod
    def validate(cls, request_token:str) -> str:
        try:
            if cls.token[request_token]["expires"] < time.time():
                cls.token.pop(request_token)
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
            return cls.token[request_token]
        return validation
    
    @classmethod
    def add_token(cls, request_token:str, user:str, session):
        expiration:float = expiration_time()
        cls.token[request_token] = {"expires":expiration, "user":user, session:session}

def expiration_time() -> float:
    return time.time() + (30*60)
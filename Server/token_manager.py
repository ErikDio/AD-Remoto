class TokenManager:
    token:dict = {}
    @classmethod
    def validate(cls, request_token):
        if request_token in cls.token.keys():
            return "placeholder"
        else:
            return "error"

    @classmethod
    def get_token(cls):
        raise NotImplementedError("This method should be implemented by subclasses")
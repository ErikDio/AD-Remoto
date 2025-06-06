class TokenManager:
    token:dict = {}
    @classmethod

    def validate(cls, request_token): #Realiza validação do Token
        if request_token in cls.token.keys():
            return "placeholder"
        else:
            return "error"
    
    @classmethod
    def add_token(cls, token, instance): #Adiciona um novo token e o atribui a uma instância
        pass

    @classmethod
    def get_token(cls):
        raise NotImplementedError("This method should be implemented by subclasses")
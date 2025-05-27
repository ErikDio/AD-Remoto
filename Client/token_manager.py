import time

class TokenManager:
    def __init__(self):
        self._token = None
        self._issued_at = None
        self._expires_in = 3600  # seconds (1 hour)

    def set_token(self, token):
        self._token = token
        self._issued_at = time.time()

    def get_token(self):
        if self.is_token_valid():
            return self._token
        raise ValueError("Token is missing or expired")

    def is_token_valid(self):
        if self._token is None or self._issued_at is None:
            return False
        return (time.time() - self._issued_at) < self._expires_in

    def clear_token(self):
        self._token = None
        self._issued_at = None
from enum import Enum
class OperationList(Enum):
    AUTHENTICATE = "authenticate"
    CHANGE_ID = "changeID"
    CHANGE_PASSWORD ="changePassword"
    SEARCH_USER = "searchUser"
    UNLOCK_ACCOUNT = "unlockAccount"

class ErrorList(Enum):
    EXPIRED_TOKEN = "expired"
    INVALID_TOKEN = "invalid"

class ReturnList(Enum):
    OPERATION_OK = "ok"
    OPERATION_ERROR = "error"
    NOT_FOUND = "notFound"
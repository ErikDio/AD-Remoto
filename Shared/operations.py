from enum import Enum
class OperationList(Enum):
    AUTHENTICATE = "authenticate"
    CHANGE_ID = "changeID"
    CHANGE_PASSWORD ="changePassword"
    SEACHR_USER = "searchUser"
    UNLOCK_ACCOUNT = "unlockAccount"
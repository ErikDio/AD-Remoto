from enum import Enum
class OperationList(Enum):
    AUTHENTICATE = "authenticate"
    CHANGE_ID = "changeID"
    CHANGE_PASSWORD ="changePassword"
    SEARCH_USER = "searchUser"
    UNLOCK_ACCOUNT = "unlockAccount"
from ldap3 import Server, Connection, ALL, MODIFY_REPLACE, SIMPLE, Entry
import ldap3.core.exceptions
import sys
from . import log
import json
import os

from Shared.operations import *

from .token_manager import TokenManager

log = log.Log_Handler()

# Load configuration from config.json (support frozen apps)
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(__file__)
CONFIG_PATH = os.path.join(base_path, "config.json")
with open(CONFIG_PATH, "r") as f:
    config = json.load(f)

class Operation():
    fqdn = config.get("domain")
    search_base = config.get("search_base")
    operation = ""
    conn:Connection = None
    
    def __init__(self, user=None, password=None, op=None, target=None, det=None):
        bind_user = user
        bind_password = password
        self.target_username = target
        self.operation = op
        self.detail = det
        server = Server(self.fqdn, port=636, use_ssl=True, get_info=ALL)
        return_var = ""
        try:
            self.conn = Connection(server,
            user=bind_user,
            password=bind_password,
            authentication=SIMPLE,
            auto_bind=True)
            log.write("Connected")
            return_var = ReturnList.OPERATION_OK.value

        except ldap3.core.exceptions.LDAPBindError:
            log.write("Authentication error.")
            return_var = ReturnList.OPERATION_ERROR.value
            self.output = return_var
            return
        except Exception as e:
            log.write(f"Critical error when trying to authenticate: {e}")
            self.output = ErrorList.CRITICAL_ERROR.value
            return
        log.write(return_var)
        self.output = return_var
        
    def handleRequest(self, request_aray:list) -> str:
        # Request array:
        # 1 - Operation
        # 2 - Target user CN
        # 3 - Detail
        request, target_user, detail = (request_aray+[None]*3)[:3] # Completes with None if necessary

        match request:
            case OperationList.SEARCH_USER.value:
                return self.searchUser(target_username=target_user)
            case OperationList.UNLOCK_ACCOUNT.value:
                return self.unlockAccount(target_username=target_user)
            case OperationList.CHANGE_ID.value:
                return self.changeID(target_username=target_user, detail=detail)
            case OperationList.CHANGE_PASSWORD.value:
                return self.changePassword(target_username=target_user, detail=detail)
            case _:
                return ErrorList.INVALID_OPERATION.value

    def searchUser(self, target_username:str) -> str:
        self.conn.search(
            self.search_base,
            f'(&(objectClass=user)(sAMAccountName={target_username}))',
            attributes=['distinguishedName', 'sAMAccountName', 'cn']
        )

        if not self.conn.entries:
            log.write(f"User {target_username} not found.")
            return ReturnList.NOT_FOUND.value
        else:
            user_entry:Entry = self.conn.entries[0]
            user_dn = user_entry.entry_dn
            log.write(f"Found {target_username}: {user_dn}")
            return f"{ReturnList.OPERATION_OK.value}|{user_entry.cn}|{user_dn}"

    def unlockAccount(self, target_username:str) -> str:
        self.conn.extend.microsoft.unlock_account(target_username)
        if(self.conn.result['result'] == 0):
            log.write("Conta desbloqueada")
            return ReturnList.OPERATION_OK.value
        else:
            log.write(f"Error unlocking account: {self.conn.result}")
            return ReturnList.OPERATION_ERROR.value
        
    def changeID(self, target_username:str, detail:str) -> str:
        new_logon_id = detail
        domain = config.get("domain")
        self.conn.modify(target_username, {
            'sAMAccountName': [(MODIFY_REPLACE, [new_logon_id])],
            'userPrincipalName': [(MODIFY_REPLACE, [f"{new_logon_id}@{domain}"])]
        })
        if(self.conn.result['result'] == 0):
            log.write(f"ID alterado para {new_logon_id}")
            return ReturnList.OPERATION_OK.value
        else:
            log.write(f"Error changing ID: {self.conn.result}")
            return ReturnList.OPERATION_ERROR.value

    def changePassword(self, target_username:str, detail:str) -> str:
        new_password = detail
        self.conn.extend.microsoft.unlock_account(target_username)
        self.conn.extend.microsoft.modify_password(target_username, new_password)
        if(self.conn.result['result'] == 0):
            return ReturnList.OPERATION_OK.value
        else:
            log.write(f"Error changing password: {self.conn.result}")
            return ReturnList.OPERATION_ERROR.value
            
        
    def disconnect(self) -> None: #Finishes the session
        self.conn.unbind()
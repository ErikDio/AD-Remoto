from ldap3 import Server, Connection, ALL, MODIFY_REPLACE, SIMPLE, Entry
import ldap3.core.exceptions
import sys
import log
import json
import os

from Shared.operations import *

from token_manager import TokenManager

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
    
    def __init__(self, user, password, op, target, det):
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
            if (self.operation == OperationList.AUTHENTICATE):
                log.write("Conectado")
                self.conn.unbind()
                return_var = ReturnList.OPERATION_OK
                self.output = return_var

        except ldap3.core.exceptions.LDAPBindError:
            log.write("Erro ao autenticar.")
            return_var = ReturnList.OPERATION_ERROR
            self.output = return_var
            return
        except Exception as e:
            log.write(f"Erro crítico ao tentar autenticar: {e}")
            self.output = ErrorList.CRITICAL_ERROR
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
            case OperationList.SEARCH_USER:
                return self.searchUser()
            case OperationList.UNLOCK_ACCOUNT:
                return self.unlockAccount()
            case OperationList.CHANGE_ID:
                return self.changeID()
            case OperationList.CHANGE_PASSWORD:
                return self.changePassword()
            case _:
                return ErrorList.INVALID_OPERATION

    def searchUser(self, target_username:str) -> str:
        self.conn.search(
            self.search_base,
            f'(&(objectClass=user)(sAMAccountName={target_username}))',
            attributes=['distinguishedName', 'sAMAccountName', 'cn']
        )

        if not self.conn.entries:
            log.write(f"User {target_username} not found.")
            return ReturnList.NOT_FOUND
        else:
            user_entry:Entry = self.conn.entries[0]
            user_dn = user_entry.entry_dn
            return f"{ReturnList.OPERATION_OK}|{user_entry.cn}|{user_dn}"
                
    def unlockAccount(self, target_username:str) -> str:
        self.conn.extend.microsoft.unlock_account(target_username)
        if(self.conn.result['result'] == 0):
            log.write("Conta desbloqueada")
            return ReturnList.OPERATION_OK
        else:
            return ReturnList.OPERATION_ERROR
    def changeID(self, target_username:str, detail:str) -> str:
        new_logon_id = detail
        domain = config.get("domain")
        self.conn.modify(target_username, {
            'sAMAccountName': [(MODIFY_REPLACE, [new_logon_id])],
            'userPrincipalName': [(MODIFY_REPLACE, [f"{new_logon_id}@{domain}"])]
        })
        if(self.conn.result['result'] == 0):
            log.write(f"ID alterado para {new_logon_id}")
            return ReturnList.OPERATION_OK
        else:
            return ReturnList.OPERATION_ERROR

    def changePassword(self, target_username:str, detail:str) -> str:
        new_password = detail
        self.conn.extend.microsoft.unlock_account(target_username)
        self.conn.extend.microsoft.modify_password(target_username, new_password)
        if(self.conn.result['result'] == 0):
            return ReturnList.OPERATION_OK
        else:
            return ReturnList.OPERATION_ERROR
        
    def disconnect(self) -> None: #Encerra a sessão
        self.conn.unbind()
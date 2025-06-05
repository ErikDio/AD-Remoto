from ldap3 import Server, Connection, ALL, MODIFY_REPLACE, SIMPLE, Entry
import ldap3.core.exceptions
import sys
import log
import json
import os

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

# Configuration
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
            if (self.operation == "autenticar"):
                log.write("Conectado")
                self.conn.unbind()
                return_var = "ok"
                self.output = return_var

        except ldap3.core.exceptions.LDAPBindError:
            log.write("Erro ao autenticar.")
            return_var = "Fatal"
            self.output = return_var
            return
        match self.operation:
            case "pesquisarUsuario":
                return_var = self.pesquisarUsuario()
            case "desbloquearConta":
                return_var = self.desbloquearConta()
            case "alterarID":
                return_var = self.alterarID()
            case "alterarSenha":
                return_var = self.alterarSenha()
        log.write(return_var)
        self.conn.unbind()
        self.output = return_var

    # 1. Connect to the LDAP server
    def pesquisarUsuario(self):
        # 2. Search for the user
        self.conn.search(
            self.search_base,
            f'(&(objectClass=user)(sAMAccountName={self.target_username}))',
            attributes=['distinguishedName', 'sAMAccountName', 'cn']
        )

        if not self.conn.entries:
            log.write(f"User {self.target_username} not found.")
            return "Nan"
        else:
            user_entry:Entry = self.conn.entries[0]
            user_dn = user_entry.entry_dn
            return f"{user_entry.cn}|{user_dn}"
                
                
    def desbloquearConta(self):
        self.conn.extend.microsoft.unlock_account(self.target_username)
        if(self.conn.result['result'] == 0):
            log.write("Conta desbloqueada")
            return "ok"
        else:
            return "erro"
    def alterarID(self):
        new_logon_id = self.detail
        domain = config.get("domain")
        self.conn.modify(self.target_username, {
            'sAMAccountName': [(MODIFY_REPLACE, [new_logon_id])],
            'userPrincipalName': [(MODIFY_REPLACE, [f"{new_logon_id}@{domain}"])]
        })
        if(self.conn.result['result'] == 0):
            log.write(f"ID alterado para {new_logon_id}")
            return f"ok"
        else:
            return "erro"

    def alterarSenha(self):
        # 3. Reset password (Windows requires SSL or StartTLS for password changes)
        new_password = self.detail
        self.conn.extend.microsoft.unlock_account(self.target_username)
        self.conn.extend.microsoft.modify_password(self.target_username, new_password)
        if(self.conn.result['result'] == 0):
            return "Alterado"
        else:
            return "Erro"
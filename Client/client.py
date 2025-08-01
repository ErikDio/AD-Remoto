import socket
import sys, os
import tkinter as tk
from tkinter import simpledialog, messagebox
import json

from .token_manager import TokenManager
from Shared.operations import *

config:dict

if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(__file__)
CONFIG_PATH = os.path.join(base_path, "config.json")
with open(CONFIG_PATH, "r") as f:
    config = json.load(f)

TokenManager.set_token()

HOST = config.get("host")
PORT = config.get("port",7777)
DOMAIN = config.get("domain")
FILTER = config.get("ou_filter")

def request(pedido) -> str:
    msg:str = ""
    try:
        msg = f'{TokenManager.get_token()}|{pedido}'#token|operação|alvo|detalhe
    except ValueError as e:
        return str(e)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(msg.encode('utf-8'))
        data = s.recv(1024)
        resposta = data.decode('utf-8').strip()
        if pedido == "ping":
            return ReturnList.OPERATION_OK if data else ReturnList.OPERATION_ERROR
        else:
            return resposta

def run_gui():
    current_dn:str = None

    def authenticate() -> None:
        user = entry_user.get()
        password = entry_pass.get()
        if not user or not password:
            messagebox.showerror("Erro", "Usuário e senha são obrigatórios.")
            return
        usuario = f"{user}@{DOMAIN}"
        senha = password
        if request("ping") != ReturnList.OPERATION_OK:
            messagebox.showerror("Erro", "Falha na conexão com o servidor.")
            return
        msg = request(f"{usuario}|{senha}|{OperationList.AUTHENTICATE.value}")
        if msg != ReturnList.OPERATION_OK.value:
            messagebox.showerror("Erro", "Usuário ou senha inválidos.")
            return
        
        frame_login.pack_forget()
        frame_main.pack()

    def pesquisar_usuario() -> None:
        nonlocal current_dn
        user_id = entry_id.get()
        resposta = request(f"{OperationList.SEARCH_USER.value}|{user_id}")
        if resposta == "Nan":
            messagebox.showerror("Erro", "Usuário não encontrado.")
            return
        elif "|" not in resposta:
            messagebox.showerror("Falha", "Erro ao pesquisar o usuário, tente novamente.")
            return
        status, info, dn = resposta.split("|")
        if(FILTER != "Nan" and FILTER not in dn):
            messagebox.showerror("Erro", f"O usuário está fora da OU {FILTER}.")
            return
        label_info.config(text=f"Usuário: {info}")
        btn_unlock.config(state=tk.NORMAL)
        btn_pass.config(state=tk.NORMAL)
        btn_id.config(state=tk.NORMAL)
        current_dn = dn

    def desbloquear() -> None:
        dn = current_dn
        resposta = request(f"{OperationList.UNLOCK_ACCOUNT.value}|{dn}")
        messagebox.showinfo("Resultado", "Sucesso ao desbloquear a conta." if ReturnList.OPERATION_OK.value in resposta[0:3] else "Erro ao desbloquear a conta.")

    def alterar_senha() -> None:
        dn = current_dn
        nova = simpledialog.askstring("Nova Senha", "Digite a nova senha:", show='*')
        if not nova:
            return
        resposta = request(f"{OperationList.CHANGE_PASSWORD.value}|{dn}|{nova}")
        messagebox.showinfo("Resultado", "Sucesso ao alterar a senha." if ReturnList.OPERATION_OK.value in resposta[0:3] else "Erro ao alterar a senha.")

    def alterar_id() -> None:
        dn = current_dn
        novo = simpledialog.askstring("Novo ID", "Digite o novo ID:")
        if not novo:
            return
        resposta = request(f"{OperationList.CHANGE_ID.value}|{dn}|{novo}")
        messagebox.showinfo("Resultado", "Sucesso ao alterar o ID." if ReturnList.OPERATION_OK.value in resposta[0:3] else "Erro ao alterar o ID.")

    root = tk.Tk()
    root.title("Client GUI")
    root.geometry("800x600")

    frame_login = tk.Frame(root)
    tk.Label(frame_login, text="Usuário (adm):", font=("Arial", 16)).pack(pady=20)
    entry_user = tk.Entry(frame_login, font=("Arial", 16), width=30)
    entry_user.pack(pady=10)
    tk.Label(frame_login, text="Senha:", font=("Arial", 16)).pack(pady=10)
    entry_pass = tk.Entry(frame_login, show="*", font=("Arial", 16), width=30)
    entry_pass.pack(pady=10)
    tk.Button(frame_login, text="Entrar", font=("Arial", 16, "bold"), width=15, height=2, bg="#4CAF50", fg="white", command=authenticate).pack(pady=20)
    frame_login.pack(expand=True)

    frame_main = tk.Frame(root)
    tk.Label(frame_main, text="ID do usuário:", font=("Arial", 16)).pack(pady=20)
    entry_id = tk.Entry(frame_main, font=("Arial", 16), width=30)
    entry_id.pack(pady=10)
    tk.Button(frame_main, text="Pesquisar", font=("Arial", 16, "bold"), width=15, height=2, bg="#2196F3", fg="white", command=pesquisar_usuario).pack(pady=20)
    label_info = tk.Label(frame_main, text="Usuário: ", font=("Arial", 16))
    label_info.pack(pady=10)
    label_dn = tk.Label(frame_main, text="DN: ", font=("Arial", 14))
    label_dn.pack(pady=5)
    frame_actions = tk.Frame(frame_main)
    btn_unlock = tk.Button(frame_actions, text="Desbloquear Conta", font=("Arial", 14, "bold"), width=18, height=2, bg="#FF9800", fg="white", command=desbloquear, state=tk.DISABLED)
    btn_pass = tk.Button(frame_actions, text="Alterar Senha", font=("Arial", 14, "bold"), width=18, height=2, bg="#9C27B0", fg="white", command=alterar_senha, state=tk.DISABLED)
    btn_id = tk.Button(frame_actions, text="Alterar ID", font=("Arial", 14, "bold"), width=18, height=2, bg="#009688", fg="white", command=alterar_id, state=tk.DISABLED)
    btn_unlock.pack(side=tk.LEFT, padx=10, pady=20)
    btn_pass.pack(side=tk.LEFT, padx=10, pady=20)
    btn_id.pack(side=tk.LEFT, padx=10, pady=20)
    frame_actions.pack(pady=30)
    frame_main.pack_forget()

    root.mainloop()

if __name__ == "__main__":
    run_gui()
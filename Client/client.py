import socket
import getpass
import sys, os
import tkinter as tk
from tkinter import simpledialog, messagebox
import json
from token_manager import TokenManager
from Shared.operations import OperationList as oplist

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

def request(pedido):
    msg:str = ""
    try:
        msg = f'{TokenManager.get_token()}|{pedido}'#token|operação|alvo|detalhe
    except ValueError as e:
        return str(e)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(msg.encode('utf-8'))
        data = s.recv(1024)
        resposta = data.decode('utf-8')
        if pedido == "ping":
            return "ok" if data else "erro"
        else:
            return resposta

def run_gui():
    current_dn:str = None

    def authenticate():
        user = entry_user.get()
        password = entry_pass.get()
        if not user or not password:
            messagebox.showerror("Erro", "Usuário e senha são obrigatórios.")
            return
        usuario = f"{user}@{DOMAIN}"
        senha = password
        if request("ping") != "ok":
            messagebox.showerror("Erro", "Falha na conexão com o servidor.")
            return
        msg = request(f"{usuario}|{senha}|{oplist.AUTHENTICATE}|Nan")
        if msg != "ok":
            messagebox.showerror("Erro", "Usuário ou senha inválidos.")
            return
        
        frame_login.pack_forget()
        frame_main.pack()

    def pesquisar_usuario():
        user_id = entry_id.get()
        resposta = request(f"{oplist.SEACHR_USER}|{user_id}|Nan")
        if resposta == "Nan":
            messagebox.showerror("Erro", "Usuário não encontrado.")
            return
        info, dn = resposta.split("|")
        if(FILTER not in ("Nan", dn)):
            messagebox.showerror("Erro", "O usuário está fora da OU {FILTER}.")
            return
        label_info.config(text=f"Usuário: {info}")
        btn_unlock.config(state=tk.NORMAL)
        btn_pass.config(state=tk.NORMAL)
        btn_id.config(state=tk.NORMAL)
        current_dn = dn

    def desbloquear():
        dn = current_dn
        resposta = request(f"{oplist.UNLOCK_ACCOUNT}|{dn}|Nan")
        messagebox.showinfo("Resultado", "Sucesso ao desbloquear a conta." if resposta == "ok" else "Erro ao desbloquear a conta.")

    def alterar_senha():
        dn = current_dn
        nova = simpledialog.askstring("Nova Senha", "Digite a nova senha:", show='*')
        if not nova:
            return
        resposta = request(f"{oplist.CHANGE_PASSWORD}|{dn}|{nova}")
        messagebox.showinfo("Resultado", "Sucesso ao alterar a senha." if resposta == "ok" else "Erro ao alterar a senha.")

    def alterar_id():
        dn = current_dn
        novo = simpledialog.askstring("Novo ID", "Digite o novo ID:")
        if not novo:
            return
        resposta = request(f"{oplist.CHANGE_ID}|{dn}|{novo}")
        messagebox.showinfo("Resultado", "Sucesso ao alterar o ID." if resposta == "ok" else "Erro ao alterar o ID.")

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
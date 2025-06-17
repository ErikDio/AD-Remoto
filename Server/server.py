import socket
import threading
import log
import json
import os, sys
from typing import TypedDict

from Shared.operations import *
import ad_helper
from token_manager import TokenManager

class SessionDict(TypedDict):
    user: str
    session: ad_helper.Operation

config:dict
# Load configuration from config.json (support frozen apps)
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(__file__)
CONFIG_PATH = os.path.join(base_path, "config.json")
with open(CONFIG_PATH, "r") as f:
    config = json.load(f)

HOST = config.get("HOST", "0.0.0.0")
PORT = config.get("PORT", 7777)
TIMEOUT = 300  #Seconds
SESSION:dict[str, SessionDict] = {} #Example: SESSION{"token":{"user":"Erik Dio", "session":ad_helper_session}}
log = log.Log_Handler()

def handle_login(stripped_data: str) -> str:
    token, id, password = stripped_data
    if (token not in SESSION.keys()):
        t_SESSION = ad_helper.Operation(id=id, password=password)
        if (t_SESSION.output == ReturnList.OPERATION_OK):
            SESSION[token] = {"user":id, "session":t_SESSION}
            TokenManager.add_token(token)
            log.write(f"{id} logged in.")
            return ReturnList.OPERATION_OK
        else:
            log.write(f"Unsuccessful login attempt from {id}.")
            return ReturnList.OPERATION_ERROR
    else:
        log.write("Already logged in.")
        raise ValueError

def handle_request(data: str) -> str:
    try:
        stripped_data = data.strip().split("|")
        if len(stripped_data <= 2):
            log.write("Invalid request.")
            raise ValueError
        token = stripped_data[0]
        if(OperationList.AUTHENTICATE in stripped_data):
            return handle_login(stripped_data=stripped_data)
        else:
            auth = TokenManager.auth(token)
            if auth == ReturnList.OPERATION_OK:
                output = SESSION[token]["session"].handleRequest(stripped_data[1:]) #skips the first item, which should be the token
                return output
            else:
                return auth
        """user, password, operation, target, details = data.strip().split('|', 4)
        ad_return = ad_helper.Operation(
            user=user,
            password=password,
            target=target,
            op=operation,
            det=details
        )
        return ad_return.output
        """
    except ValueError:
        return ReturnList.OPERATION_ERROR
def validate_request(data: str) -> bool:
    if("|" in data):
        return True
    else:
        return False
    
def client_thread(conn, addr) -> None:
    conn.settimeout(TIMEOUT)
    log.write(f"Connection established with {addr}")
    with conn:
        while True:
            try:
                data = conn.recv(1024)
                if(not data):
                    log.write(f"No data from {addr}. Closing connection.")
                    break
                decoded_data = data.decode('utf-8').strip()
                if OperationList.AUTHENTICATE in decoded_data:
                    log.write(f"Received login request from {addr}")
                else:
                    log.write(f"Received from {addr}: {decoded_data}")
                if "ping" in decoded_data.lower():
                    conn.sendall("pong".encode('utf-8'))
                    continue
                if(validate_request(decoded_data) == True):
                    response = handle_request(decoded_data)
                    conn.sendall(response.encode('utf-8'))
            except socket.timeout:
                log.write(f"Connection with {addr} timed out after {TIMEOUT} seconds.")
                break
            except SyntaxError:
                log.write(f"")
            except Exception as e:
                log.write(f"Error with {addr}: {e}")
                try:
                    conn.sendall(f"Server error: {e}".encode('utf-8'))
                except:
                    log.write(f"Error sending \"{e}\" to {addr}")
                break

    log.write(f"Connection closed with {addr}")
    
def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        log.write(f"Server listening on port {PORT}...")

        while True:
            conn, addr = s.accept()
            thread = threading.Thread(target=client_thread, args=(conn, addr), daemon=True)
            thread.start()

if __name__ == "__main__":
    main()
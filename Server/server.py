import socket
import threading
import log
import ad_helper
import json
import os
import sys
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
TIMEOUT = 300  # 5 minutes
SESSION:ad_helper = []
log = log.Log_Handler()

def handle_request(data: str) -> str:
    try:
        user, password, operation, target, details = data.strip().split('|', 4)
        ad_return = ad_helper.Operation(
            user=user,
            password=password,
            target=target,
            op=operation,
            det=details
        )
        return ad_return.output
    except ValueError:
        return 'Erro'

def client_thread(conn, addr) -> None:
    conn.settimeout(TIMEOUT)
    log.write(f"Connection established with {addr}")
    with conn:
        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    log.write(f"No data from {addr}. Closing connection.")
                    break

                decoded_data = data.decode('utf-8').strip()
                if "autenticar" in decoded_data:
                    log.write(f"Received login request from {addr}")
                else:
                    log.write(f"Received from {addr}: {decoded_data}")
                if "ping" in decoded_data.lower():
                    conn.sendall("pong".encode('utf-8'))
                    continue

                response = handle_request(decoded_data)
                conn.sendall(response.encode('utf-8'))

            except socket.timeout:
                log.write(f"Connection with {addr} timed out after {TIMEOUT} seconds.")
                break

            except Exception as e:
                log.write(f"Error with {addr}: {e}")
                try:
                    conn.sendall(f"Server error: {e}".encode('utf-8'))
                except:
                    pass
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
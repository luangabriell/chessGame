import socket
import json
import threading

HOST = socket.gethostbyname(socket.gethostname())
PORT = 5050


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))

def listen():
    while True:
        print(sock.recv(2048).decode())
    
thread = threading.Thread(target = listen)
thread.start()

send = input("start game ? [s/n]: ")
if send == "s":
    sock.send(json.dumps({"code": "new_game"}).encode())

quit = input("quit game ? [s/n]: ")
if quit == "s":
    sock.send(json.dumps({"code": "quit_game"}).encode())
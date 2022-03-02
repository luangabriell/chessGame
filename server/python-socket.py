import socket
import threading
import json

class Server:
    def __init__(self):
        HOST = socket.gethostbyname(socket.gethostname())
        PORT = 5050

        self.games = []
        self.gamers = {}

        self.ADRESS = (HOST, PORT)
        
        self.SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.SOCKET.bind(self.ADRESS)

        print("[STARTING] server is starting...")
        self.start_server()  

    def new_game(self, conn):
        if len(self.games) == 0 or len(self.games[-1]) == 3:
            self.games.append([conn])
            conn.send(json.dumps({"code": "201"}).encode())
            self.gamers[conn] = None
        else:
            self.games[-1].append(conn)
            self.games[-1].append({})
            conn.send(json.dumps({"code": "200"}).encode())
            self.games[-1][0].send(json.dumps({"code": "200"}).encode())
            self.gamers[self.games[-1][0]] = len(self.games) - 1
            self.gamers[self.games[-1][1]] = len(self.games) - 1
    
    def quit_game(self, conn):

        self.games[self.gamers[conn]][1].send(json.dumps({"code": "400"}).encode())
        self.games[self.gamers[conn]][0].send(json.dumps({"code": "400"}).encode())

        self.gamers[self.games[self.gamers[conn]][0]] = None
        self.gamers[self.games[self.gamers[conn]][1]] = None
        self.games.pop(self.gamers[conn])

    def handle_client(self, conn, addr):
        print(f"[NEW CONNECTION] {addr} connected.")
        # print(self.gamers)
        # print(self.games)
        while True:
            try:
                data = conn.recv(1024).decode("utf-8")
                if data:
                    board_json = json.loads(data) 
                    if board_json["code"] == "new_game":
                        self.new_game(conn)
                    if board_json["code"] == "quit_game":
                        self.quit_game(conn)
            except:
                print(f"[DICONNECTED] {addr} disconnected")

                if self.gamers[conn] != None:
                    if conn == self.games[self.gamers[conn]][0]:
                        self.games[self.gamers[conn]][1].send(json.dumps({"code": "400"}).encode())
                        self.gamers[self.games[self.gamers[conn]][1]] = None
                    if conn == self.games[self.gamers[conn]][1]:
                        self.games[self.gamers[conn]][0].send(json.dumps({"code": "400"}).encode())
                        self.gamers[self.games[self.gamers[conn]][0]] = None


                try:
                    self.games.pop(self.gamers[conn])
                except:
                    pass
                try:
                    self.gamers.pop(conn)
                except:
                    pass
                break

    def start_server(self):
        self.SOCKET.listen()
        print(f"[LISTENING] server is listening on {self.ADRESS[0]}:{self.ADRESS[1]}")
        while True:
            conn, addr = self.SOCKET.accept()
            thread = threading.Thread(target = self.handle_client, args = (conn, addr))
            thread.start()

Server().start_server()
import socket
import threading
import json

class Server:
    def __init__(self):
        # config host and port to be used
        HOST = socket.gethostbyname(socket.gethostname())
        PORT = 5050
        # define atributes games and gamers
        self.games = []
        self.gamers = {}
        # define ADRESS as a tuple of host and port
        self.ADRESS = (HOST, PORT)
        # create socket 
        self.SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.SOCKET.bind(self.ADRESS)
        # log a message in console indicating that server is starting
        print("[STARTING] server is starting...")
        # starts server
        self.start_server()  

    # method to start a game (it's require the conn of the client)
    def new_game(self, conn):
        # if there aren't any gamer waiting
        if len(self.games) == 0 or len(self.games[-1]) == 3:
            # create a new game element
            self.games.append([conn])
            # send to the gamer code 201, that means that there aren't any gammer free to play
            conn.send(json.dumps({"code": "201"}).encode())
            # set the game that gamer is playing
            self.gamers[conn] = len(self.games) - 1
        # if there are a gamer waiting
        else:
            # append gamer to the last element of games
            self.games[-1].append(conn)
            # append board dictionary to the last element of games
            self.games[-1].append({})
            # send to the gamers that it's all ready to start the game
            conn.send(json.dumps({"code": "200"}).encode())
            self.games[-1][0].send(json.dumps({"code": "200"}).encode())
            # set the game that gamers are playing
            self.gamers[self.games[-1][0]] = len(self.games) - 1
            self.gamers[self.games[-1][1]] = len(self.games) - 1
    
    # method to quit a game (it's require the conn of the client)
    def quit_game(self, conn):
        # if there are a game beeing played
        if len(self.games[self.gamers[conn]]) > 1:
            # send to the gamers code 401, that means that the game has finished by quiting
            self.games[self.gamers[conn]][1].send(json.dumps({"code": "401"}).encode())
            self.games[self.gamers[conn]][0].send(json.dumps({"code": "401"}).encode())
            # remove game of the list
            self.gamers[self.games[self.gamers[conn]][0]] = None
            self.gamers[self.games[self.gamers[conn]][1]] = None
            
        # if there aren't a game beeing played  
        else:
            # send to the client code 401, that means the game has finished by quiting
            self.games[self.gamers[conn]][0].send(json.dumps({"code": "401"}).encode())
            # remove game of the list
            self.gamers[self.games[self.gamers[conn]][0]] = None

        self.games.pop(self.gamers[conn])
    # method to hand new client (it's require the conn and the addr of the new client)
    def handle_client(self, conn, addr):
        # log a message in console indicating that a new client has connected
        print(f"[NEW CONNECTION] {addr} connected.")
        # while client is connected
        while True:
            try:
                # try to recive data from client
                data = conn.recv(1024).decode("utf-8")
                # if data is not None
                if data:
                    # define data as the data translated to json
                    data = json.loads(data) 
                    # if data code equal new_game
                    if data["code"] == "new_game":
                        # call method to start a new game passing the conn
                        self.new_game(conn)
                    # if data code equal quit_game
                    if data["code"] == "quit_game":
                        # call method to start a new game passing the conn
                        self.quit_game(conn)
            except:
                # if the client is not connected break the while extructure

                # log a message indicating that client has disconnected
                print(f"[DICONNECTED] {addr} disconnected")
                # check if the client is playing a game
                if self.gamers[conn] != None:
                    # end the game and send to the oponent that the game has finished 
                    if conn == self.games[self.gamers[conn]][0]:
                        # send conde 400, that means that the game has finished by disconnection
                        self.games[self.gamers[conn]][1].send(json.dumps({"code": "400"}).encode())
                        self.gamers[self.games[self.gamers[conn]][1]] = None
                    if conn == self.games[self.gamers[conn]][1]:
                        # send conde 400, that means that the game has finished by disconnection
                        self.games[self.gamers[conn]][0].send(json.dumps({"code": "400"}).encode())
                        self.gamers[self.games[self.gamers[conn]][0]] = None

                # remove gamer for the list of gamers
                # remove game that the gamer is playing of the list of games

                # there are a try and except extructure because sometimes the game or the gamer has already been removed of the lists
                try:
                    self.games.pop(self.gamers[conn])
                except:
                    pass
                try:
                    self.gamers.pop(conn)
                except:
                    pass
                # break the while extructure
                break
    
    # method to start server and listen to new connections
    def start_server(self):
        # enable socket to listen new connections
        self.SOCKET.listen()
        # log a message in the console that the server is listening to new connections
        print(f"[LISTENING] server is listening on {self.ADRESS[0]}:{self.ADRESS[1]}")
        # while extructures
        while True:
            # accept a new connection and store the connection and the adress
            conn, addr = self.SOCKET.accept()
            # create a new thread to handle the new client connected
            thread = threading.Thread(target = self.handle_client, args = (conn, addr))
            # start thread
            thread.start()

Server().start_server()
from socket import *

import sys
import pickle
import select
import time

debug = False
buffer_size = 1024

def write(_socket, data):
    pickled = pickle.dumps(data)
    if debug:
        print("write: "+str(len(pickled)))
        print(data)
    _socket.send(pickled)


def read(_socket):
    if debug:
        print("read:")
    data = pickle.loads(_socket.recv(1024))
    if debug:
        print(data)
    return data


class ChatClient:
    
    def __init__(self, host, port):
        self.clients = ["ALL"]
        self.conn = socket(AF_INET, SOCK_STREAM)
        self.conn.connect((host, port)) 
    
    def run(self, name):
        self.name = name
        write(self.conn, [name])
        msg = read(self.conn)

        if(msg[0] == "WRONG_NAME"):
            print("Name not accepted\n")
            return
        
        self.clients += msg
        
        print("Welcome to the chat")
        self.print_clients()
        
        while True:
            #self.handle_stdin()
            self.handle_conn()
            
    def handle_stdin(self):
        msg = sys.stdin.readline()
        if(msg[:11] == "GET_CLIENTS"):
            write(self.conn, ["GET_CLIENTS"])
        else:
            msg = msg.split(':')
            if msg[0] in self.clients:
                write(self.conn, ["MESSAGE", self.name, msg[0], msg[1]])
            else:
                print("WRONG RECIEVER NAME")
                
    def handle_conn(self):
        msg = read(self.conn)
        if msg[0] == "CLOSE":
            if msg[1] in self.clients:
                self.clients.remove(msg[1])
        elif msg[0] == "NEW_CLIENT":
            if msg[1] not in self.clients:
                self.clients.append(msg[1])
        elif msg[0] == "MESSAGE":
            print(msg[1]+" -> "+msg[2]+": "+msg[3])
        else:
            self.clients = ["ALL"]+msg
            print_clients()
            
    def print_clients(self):
        string = "USERS: "
        for client in self.clients:
            string += client + ", "
        string = string[:-2]
        print(string)
     
client = ChatClient('localhost', 12345)
client.run(sys.argv[1])


import socket
import sys
import threading
import pickle

debug = False
unacceptable_names = ["WRONG_NAME", "CLOSE", "NEW_CLIENT", "MESSAGE", "GET_CLIENTS", "ALL"]
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



class ChatServer:
    def __init__(self, host, port):
        self.clients = []
        self.sockets = {}
        self.open_socket(host, port)
        self.client_lock = threading.RLock()
    
    
    def open_socket(self, host, port):
        """ 
        Metoda tworząca server, na hoscie: host i porcie: port
        """
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind( (host, port) ) 
        self.server.listen(5)


    def run(self):
        while True:         
            clientSocket, clientAddr = self.server.accept()
            if debug:
                print("SERVER LOG: Zgłoszenie klienta, adres: {0}".format(clientAddr))
            
            if debug:
                self.number_of_clients()

            Client(clientSocket, clientAddr, self).start()
    
    def number_of_clients(self):
        print("Liczba klientów: {0}".format(len(self.clients)))
    
    def add_client(self, client_name, client_socket):
        if client_name in self.clients or client_name in unacceptable_names:
            return False
        else:
            self.clients.append(client_name)
            self.sockets[client_name] = client_socket
            return True
    
    def clean_client(self, client):
        try:
            self.sockets[client].close()
            if debug:
                self.number_of_clients()
        except:
            if debug:
                print("Exception: usuwanie klienta")
        
        msg = ["CLOSE", client]
        err = []
        with self.client_lock:
            for client in self.clients:
                try:
                    write(self.sockets[client], msg)
                except:
                    err.append(client)
        server.clean_clients(err)

    def clean_clients(self, err):
        for client in err:
            with self.client_lock:
                if client in self.clients:
                    self.clients.remove(client)
                else:
                    err.remove(client)
        for client in err:
            self.clean_client(client)
            
        

class Client(threading.Thread):
    def __init__(self, client_socket, client_addr, server):
        threading.Thread.__init__(self, daemon=True)
        self.client_socket = client_socket;
        self.client_addr = client_addr;
        self.server = server
        
    def run(self):
        try:
            msg = read(self.client_socket)
            if msg:                             
                self.client_name = msg[0]
            else:
                return
        except:
            return
        
        with self.server.client_lock:
            result = server.add_client(self.client_name, self.client_socket)
        
        if(result == False):
            msg = ["WRONG_NAME"]
            write(self.client_socket, msg)
            return
        
        with self.server.client_lock:
            try:
                write(self.client_socket, self.server.clients)
            except:
                self.server.clean_client(self.client_name)
                if debug:
                    print("EXCEPT clasue: {0}".format(data))
                return

        msg = ["NEW_CLIENT", self.client_name]
        err = []
        with self.server.client_lock:
            for client in self.server.clients:
                if self.client_name != client:
                    try:
                        write(self.server.sockets[client], msg)                         
                    except:
                        err.append(client)                      
        self.server.clean_clients(err)  
                
            
        running = True
        while running:
            try:
                msg = read(self.client_socket)
                if msg:                             
                    msgType = msg[0];
                    
                    if(msgType == "MESSAGE"):
                        reciever = msg[2];
                        err = []
                        with self.server.client_lock:
                            for client in self.server.clients:
                                if self.client_name == client or reciever == client or reciever == "ALL":
                                    try:
                                        write(self.server.sockets[client], msg)                         
                                    except:
                                        err.append(client)                      
                        self.server.clean_clients(err)  
                    
                    elif(msgType == "GET_CLIENTS"):
                        try:
                            write(self.client_socket, self.server.clients)
                        except:
                            self.server.clean_client(self.client_name)
                            if debug:
                                print("CLOSE clause: {0}".format(msg))
                            return
                        
                    elif(msgType == "CLOSE"):
                        self.server.clean_client(self.client_name)
                        if debug:
                            print("CLOSE clause: {0}".format(msg))
                        return
                                    
                else:
                    running = False
                    self.server.clean_client(self.client_name)
                    if debug:
                        print("IF clause")
                    break
                    
            except:
                self.server.clean_client(self.client_name)
                running = False
                if debug:
                    print("EXCEPT clasue")
                break
    
    


server = ChatServer('',12345)
server.run()
        

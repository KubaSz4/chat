from socket import *

import tkinter as tk
import sys
import pickle
import select
import time
import threading
import os
import signal

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


class ChatClient(threading.Thread):
    
    def __init__(self, host, port, ui, name):
        threading.Thread.__init__(self, daemon=True)
        self.ui = ui
        self.name = name
        self.clients = ["ALL"]
        self.conn = socket(AF_INET, SOCK_STREAM)
        try:
            self.conn.connect((host, port)) 
        except:
            print("Server offline")
            exit(0)
            
    def run(self):
        try:
            write(self.conn, [self.name])
            msg = read(self.conn)

            if(msg[0] == "WRONG_NAME"):
                print("Name not accepted\n")
                os.kill(os.getpid(), signal.SIGUSR1)
            
            self.clients += msg
            self.ui.refresh_list(self.clients)
            
            while True:
                self.handle_conn()
        except:
            os.kill(os.getpid(), signal.SIGUSR1)
            
    def handle_stdin(self, text, reciever_id):
        if(text[:11] == "GET_CLIENTS"):
            write(self.conn, ["GET_CLIENTS"])
        else:
            write(self.conn, ["MESSAGE", self.name, 
            self.clients[reciever_id],
            text])
                
    def handle_conn(self):
        msg = read(self.conn)
        if msg[0] == "CLOSE":
            if msg[1] in self.clients:
                self.clients.remove(msg[1])
            self.ui.refresh_list(self.clients)
        elif msg[0] == "NEW_CLIENT":
            if msg[1] not in self.clients:
                self.clients.append(msg[1])
            self.ui.refresh_list(self.clients)
        elif msg[0] == "MESSAGE":
            self.ui.add_to_label(msg[1]+" -> "+msg[2]+": "+msg[3])
        else:
            self.clients = ["ALL"]+msg
            self.ui.refresh_list(self.clients)
        
    def print_clients(self):
        string = "USERS: "
        for client in self.clients:
            string += client + ", "
        string = string[:-2]
        print(string)
     
     
     
class MyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CHAT: "+sys.argv[1])
        self.root.minsize(600,400)
        self.mainFrame = tk.Frame(self.root)
        self.mainFrame.grid(row=0, column=0, sticky=tk.N + tk.S + tk.W + tk.E)
        self.mainFrame.myName = "MainFrame"
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        
        self.mainFrame.rowconfigure(0,weight=12)
        self.mainFrame.rowconfigure(1,weight=6)
        self.mainFrame.rowconfigure(2,weight=1)
        
        self.mainFrame.columnconfigure(0,weight=40)
        self.mainFrame.columnconfigure(1,weight=10)
        self.mainFrame.columnconfigure(2,weight=1)
        
        self.label_text = tk.StringVar()
        self.label = tk.Label(self.mainFrame, textvariable=self.label_text, anchor="nw", justify="left", width=50,wraplength=400, height=14, bg="white")
        self.label.grid(column=0, row=0, sticky=tk.N + tk.S + tk.W + tk.E)
        self.label.myName = "Label"
        
        
        self.scrollbar = tk.Scrollbar(self.mainFrame, orient=tk.VERTICAL)
        self.scrollbar.grid(row=0, column=2, rowspan = 2, sticky=tk.N+tk.S)
        self.listbox_list = tk.StringVar()
        self.listbox = tk.Listbox(self.mainFrame, listvariable = self.listbox_list, yscrollcommand=self.scrollbar.set)
        self.listbox.grid(column=1, row=0, rowspan=2, sticky=tk.N + tk.S + tk.W + tk.E)
        self.listbox.myName = "Listbox"
        self.scrollbar['command'] = self.listbox.yview

        self.entry = tk.Entry(self.mainFrame)
        self.entry.grid(column=0, row=1, sticky=tk.N + tk.S + tk.W + tk.E)
        self.entry.myName = "Entry"
        self.entry.bind('<Return>', lambda event: self.send())
        self.entry.focus_force()
        
        self.send_button = tk.Button(self.mainFrame, text="SEND MESSAGE", command=self.send)
        self.send_button.grid(column=0, row=2,sticky=tk.N + tk.S + tk.W + tk.E)
        self.send_button.myName="SEND MESSAGE"

        self.close_button = tk.Button(self.mainFrame, text="CLOSE", command=self.quit)
        self.close_button.grid(column=1, columnspan=2, row=2,sticky=tk.N + tk.S + tk.W + tk.E)
        self.close_button.myName = "CLOSE"
        
        
        self.send_button.bind('<Return>', lambda event: self.send())
        self.close_button.bind('<Return>', lambda event: self.quit())
        
        self.start_client()

    def start_client(self):
        self.client = ChatClient('localhost', 12345, self, sys.argv[1])
        self.client.start()

    def send(self):
        text = self.entry.get()
        reciever_id = 0
        try:
            reciever_id = self.listbox.curselection()[0]
        except:
            pass
        self.client.handle_stdin(text, reciever_id)
        self.entry.delete(0, len(text))
        
    def add_to_label(self, text):
        old_text = self.label_text.get()
        lines = []
        if len(old_text)>0:
            lines = old_text.split('\n')
        lines.append(text)
        new_text = ""
        for line in lines[-min(len(lines), 20):]:
            if len(line)<2: continue
            new_text+=line+'\n'
        self.label_text.set(new_text)
            
    def refresh_list(self, new_list):
        string = ""
        for item in new_list:
            string+=item+" "
        self.listbox_list.set(string)

    def quit(self):
        exit(0)


def handler(signum, frame):
    exit(0)


signal.signal(signal.SIGUSR1, handler)
root = tk.Tk()
myapp = MyApp(root)
root.mainloop()


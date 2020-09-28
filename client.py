import os
import sys
import tkinter as tk
from tkinter import filedialog
import socket as sc
from threading import Thread
from decouple import config
import base64


class Send(Thread):
    def __init__(self, conn, name):
        super(Send, self).__init__()
        self.conn = conn
        self.name = name

    def run(self):
        while 1:
            bw = ['fuck', 'dead', 'shit']
            sw = ['q', 'quit', 'close', 'exit', 'end']
            print('{}: '.format(self.name), end='')
            sys.stdout.flush()
            message = sys.stdin.readline()[:-1]
            if message.strip().lower() in sw:
                self.conn.sendall(f'#msg_Server: {self.name} has left the chat.'.encode('utf-8'))
                break
            else:
                self.conn.sendall(f'#msg_{self.name}: {message}'.encode('utf-8'))

        print('\nQuitting...')
        self.conn.close()
        os._exit(0)


class Receive(Thread):
    def __init__(self, conn, name):
        super(Receive, self).__init__()
        self.conn = conn
        self.name = name
        self.messages = None

    def run(self):
        while 1:
            try:
                bw = ['fuck', 'dead', 'shit']
                message = self.conn.recv(4096).decode('utf-8')
                if message:
                    if self.messages:
                        if message in bw:
                            self.messages.insert(tk.END, '****')
                        else:
                            self.messages.insert(tk.END, message)
                        print(f'\r{message}\n{self.name}:', end='')
                    else:
                        # Thread has started, but client GUI is not yet ready
                        print(f'\r{message}\n{self.name}: ', end='')

                else:
                    # Server has closed the socket, exit the program
                    print('\nOh no, we have lost connection to the server!')
                    print('\nQuitting...')
                    self.conn.close()
                    os._exit(0)
            except sc.error as e:
                print(e)
                break


class Client:
    def __init__(self):
        self.IP = config('IP')
        self.PORT = int(config('PORT'))
        # initialize address
        self.address = (self.IP, self.PORT)
        # create a TCP/IP socket
        self.socket = sc.socket(sc.AF_INET, sc.SOCK_STREAM)
        #
        self.name = None
        self.messages = None

    def start(self):
        print(f'Trying to connect to {self.IP}:{self.PORT}...')
        # waiting for connection to server
        self.socket.connect(self.address)
        print(f'Successfully connected to {self.IP}:{self.PORT}')
        print()
        self.name = input('Your name is: ')
        print()
        print(f'Welcome, {self.name}! getting ready to send and receive messages.')

        send = Send(self.socket, self.name)
        receive = Receive(self.socket, self.name)
        send.start()
        receive.start()

        self.socket.sendall(f'#msg_Server: {self.name} has joined the chat.'.encode('utf-8'))
        print(f'{self.name}: ', end='')
        return receive

    def send_text(self, text_input):
        message = text_input.get()
        text_input.delete(0, tk.END)
        if message.strip() != '' or message.strip() is not None:
            # self.messages.insert(tk.END, f'{self.name}: {message}')
            sw = ['q', 'quit', 'close', 'exit', 'end']
            bw = ['fuck', 'dead', 'shit']
            if message.strip().lower() in sw:
                try:
                    self.socket.sendall(f'#msg|Server: {self.name} has left the chat.'.encode('utf-8'))
                except sc.error as e:
                    print(e)
                print('\nQuitting...')
                self.socket.close()
                os._exit(0)
            else:
                if os.path.exists(message):
                    name, extension = os.path.splitext(message)
                    with open(message, 'rb') as f:
                        l = f.read(4096)
                        while l:
                            if extension == '.txt':
                                self.socket.send(f'#txt_file {l}'.encode('utf-8'))
                                self.socket.sendall(f'#msg_{self.name}: sent {name}{extension}'.encode('utf-8'))
                                l = f.read(4096)
                            elif extension == '.jpg':
                                str = base64.b64encode(f.read(4096))
                                self.socket.send('#img_file: '.encode('utf-8')+str.strip())
                                self.socket.sendall(f'#msg_{self.name}: sent {name}{extension}'.encode('utf-8'))

                else:
                    try:
                        last_str = ' '
                        ls_w = message.strip().lower().split(' ')
                        for w in ls_w:
                            if w in bw:
                                w = ' **** '
                            last_str += ' '+w
                        self.socket.sendall(f'#msg_{self.name}: {last_str.strip()}'.encode('utf-8'))
                    except sc.error as e:
                        print(e)


class GUI:
    def __init__(self):
        self.client = Client()
        self.receive = self.client.start()
        self.file_name = None

    def file_dialog(self, txt):
        file_name = filedialog.askopenfilename(initialdir="/", title="Select file", filetypes=(("jpeg files","*.jpg"), ("text files", "*.txt"), ("all files","*.*")))
        self.file_name = file_name
        txt.delete(0, tk.END)
        txt.insert(tk.END, file_name)

    def main(self):
        window = tk.Tk()
        window.title(f'Chat-room | {self.client.name}')

        frm_messages = tk.Frame(master=window)
        scrollbar = tk.Scrollbar(master=frm_messages)
        messages = tk.Listbox(
            master=frm_messages,
            yscrollcommand=scrollbar.set
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, expand=False)
        messages.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.client.messages = messages
        self.receive.messages = messages
        frm_messages.grid(row=0, column=0, columnspan=3, sticky="nsew")

        # frm_user = tk.Frame(master=window)
        # scrollbar_1 = tk.Scrollbar(master=frm_user)
        # display = tk.Listbox(
        #     master=frm_user,
        #     yscrollcommand=scrollbar_1.set
        # )
        #
        # scrollbar_1.pack(side=tk.RIGHT, fill=tk.Y, expand=False)
        # display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # frm_user.grid(row=0, column=0, columnspan=3, sticky="nsew")

        frm_entry = tk.Frame(master=window)
        text_input = tk.Entry(master=frm_entry)
        text_input.pack(fill=tk.BOTH, expand=True)
        text_input.bind("<Return>", lambda x: self.client.send_text(text_input))
        text_input.insert(0, "Your message here.")

        btn_file = tk.Button(
            master=window,
            text='File',
            command=lambda: self.file_dialog(text_input)
        )
        btn_send = tk.Button(
            master=window,
            text='Send',
            command=lambda: self.client.send_text(text_input)
        )

        frm_entry.grid(row=1, column=0, padx=10, sticky="ew")
        btn_file.grid(row=1, column=1, pady=10, sticky="ew")
        btn_send.grid(row=1, column=2, padx=10, pady=10, sticky="ew")

        window.rowconfigure(0, minsize=400, weight=1)
        window.rowconfigure(1, minsize=50, weight=0)
        window.columnconfigure(0, minsize=200, weight=1)
        window.columnconfigure(1, minsize=50, weight=0)

        window.mainloop()


if __name__ == '__main__':
    gui = GUI()
    gui.main()
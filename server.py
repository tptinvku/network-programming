import os
import tkinter as tk
import socket as sc
from decouple import config
from threading import Thread
import base64


class Server(Thread):
    def __init__(self):
        super(Server, self).__init__()
        self.connections = []
        self.IP = config('IP')
        self.PORT = int(config('PORT'))
        # initialize address
        self.address = (self.IP, self.PORT)
        self.display = None
        self.messages = None

    def run(self):
        # create a TCP/IP socket
        socket = sc.socket(sc.AF_INET, sc.SOCK_STREAM)
        # bind the socket to the PORT
        socket.bind(self.address)
        print(f'Listening at {self.address}')
        # listen for incoming connections
        socket.listen()

        while 1:
            # Accept new connection
            conn, client_address = socket.accept()
            print(f'Accept a new connection from {conn.getpeername()} to {conn.getsockname()}')
            # Create new thread
            communication = Communication(conn, client_address, self)
            # Start new thread
            communication.start()
            # Add thread to active connections
            self.connections.append(communication)
            print('Ready to receive messages from', conn.getpeername())

    def broadcast(self, message, address):
        self.messages.insert(tk.END, message)
        for connection in self.connections:
            try:
                connection.conn.sendall(message.encode('utf-8'))
            except sc.socket as e:
                print(e)

    def remove_connection(self, connection):
        for line in range(self.display.size()):
            item = self.display.get(line).split(':')[0]
            if str(item) == str(connection.address):
                self.display.delete(line)
                self.connections.remove(connection)


class Communication(Thread):
    def __init__(self, conn, address, server):
        super(Communication, self).__init__()
        self.conn = conn
        self.address = address
        self.server = server
        self.image_counter = 1
        self.txt_counter = 1
        self.img_name = 'image%s.jpg'
        self.txt_name = 'txt%s.txt'
        self.client_name = None

    def run(self):
        while 1:
            try:
                data = self.conn.recv(4096)
                message = data.decode('utf-8')
                if str(message).startswith('#msg'):
                    if data:
                        self.client_name = str(message).split('#msg_Server: ')
                        if len(self.client_name) > 1:
                            self.client_name = self.client_name[1].split(' ')[0]
                            self.server.display.insert(tk.END, f'{self.conn.getpeername()}: {self.client_name}')
                        print(f'{self.address} says {message}')
                        self.server.broadcast(message, self.address)

                elif message.startswith('#img_file'):
                    if data:
                        with open(self.img_name % self.image_counter, 'wb') as img:
                            base_image = base64.b64decode(message.split(':')[1].strip())
                            img.write(base_image)
                            self.server.broadcast('Got Image', self.address)
                            self.image_counter +=1

                elif message.startswith('#txt_file'):
                    if data:
                        with open(self.txt_name % self.txt_counter, 'wb') as txt:
                            txt.write(str(data).split(' ')[1].encode('utf-8'))
                            self.server.broadcast('Got Text', self.address)
                else:
                    # Client has closed the socket, exit the thread
                    print(f'{self.address} has closed the connection')
                    self.conn.close()
                    self.server.remove_connection(self)
                    return

            except sc.error as e:
                print(e)
                break
            except Exception as e:
                print(e)
                break


class GUI():
    def __init__(self):
        super(GUI, self).__init__()
        self.server = Server()
        self.server.start()
        th_close = Thread(target=self.close_server, args=(self.server,))
        th_close.start()

    def close_server(self, server):
        while 1:
            sw = ['q', 'quit', 'close', 'exit', 'end']
            stop = input('').lower().strip()
            if stop in sw:
                for connection in server.connections:
                    connection.conn.close()
                print('Shutting down the server...')
                os._exit(0)

    def remove_client(self, display):
        if display.size() > 0:
            selected = display.selection_get().split(':')[0]
            for line in range(display.size()):
                item = display.get(line).split(':')[0]
                if item == selected:
                    display.delete(line)
                    try:
                        self.server.connections[line].conn.close()
                        del self.server.connections[line]
                    except sc.error as e:
                        print(e)
                        break
                    finally:
                        break

    def destroy(self, window):
        window.destroy()

    def main(self):
        window = tk.Tk()
        window.title('Server')
        frm_user = tk.Frame(master=window)
        scrollbar = tk.Scrollbar(master=frm_user)
        display = tk.Listbox(
            master=frm_user,
            yscrollcommand=scrollbar.set
        )
        self.server.display = display

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, expand=False)
        display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        frm_user.grid(row=0, column=0, columnspan=3, sticky="nsew")
        frm_message = tk.Frame(master=window)
        scrollbar_1 = tk.Scrollbar(master=frm_message)
        messages = tk.Listbox(
            master=frm_message,
            yscrollcommand=scrollbar_1.set
        )
        self.server.messages = messages
        scrollbar_1.pack(side=tk.RIGHT, fill=tk.Y, expand=False)
        messages.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        frm_message.grid(row=0, column=1, columnspan=3, sticky="nsew")

        remove_user = tk.Button(
            master=window,
            text='Kick',
            command=lambda: self.remove_client(display)
        )

        destroy_server = tk.Button(
            master=window,
            text='Stop',
            command=lambda: self.destroy(window)
        )

        destroy_server.grid(row=1, column=1, padx=10, pady=10, sticky='ew')
        remove_user.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        window.rowconfigure(0, minsize=300, weight=1)
        window.rowconfigure(1, minsize=50, weight=1)
        window.columnconfigure(0, minsize=200, weight=1)
        window.columnconfigure(1, minsize=250, weight=1)

        window.mainloop()


if __name__ == '__main__':
    gui = GUI()
    gui.main()

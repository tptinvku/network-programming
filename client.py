import os
import time
import socket as sc
import tkinter as tk
from tkinter import ttk
from decouple import config
from threading import Thread


class Client(Thread):
    def __init__(self):
        super(Client, self).__init__()
        self.max_delay = 1
        self.default_msg = b'Exchange Rate'
        self.ip = config('IP')
        self.port = int(config('PORT'))
        self.address = (self.ip, self.port)
        self.socket = sc.socket(family=sc.AF_INET, type=sc.SOCK_DGRAM)
        self.listBox = None
        self.threads = []

    def run(self):
        send = Thread(target=self.send)
        send.start()
        for count in range(3):
            receive = Thread(target=self.receive, args=(count, ))
            self.threads.append(receive)
            receive.start()

        for thread in self.threads:
            thread.join()

    def stop(self):
        while True:
            key = input('').strip().lower()
            if key == 'q':
                self.socket.close()
                os._exit(0)

    def send(self):
        while True:
            try:
                self.socket.sendto(self.default_msg, self.address)
            except sc.error as e:
                print(e)
                self.socket.close()
                break
            except Exception as e:
                print(e)
                self.socket.close()
                break
            time.sleep(self.max_delay)

    def receive(self, count):
        while True:
            data, server = self.socket.recvfrom(4096)
            if data:
                message = data.decode()
                columns = message.split('|')
                print(columns, '\n')
                ls_child = self.listBox.get_children()
                index = len(ls_child)
                if index < 3:
                    self.listBox.insert("", tk.END, values=columns)
                else:
                    self.listBox.item(ls_child[count], values=columns)

                time.sleep(self.max_delay)


class GUI:
    def __init__(self):
        self.client = Client()
        stop = Thread(target=self.client.stop)
        stop.start()

    def main(self):
        window = tk.Tk()
        window.title('Client')
        window.resizable(width=0, height=0)

        columns = ('From', 'To', 'Exchange Rate', 'Time')
        list_box = ttk.Treeview(master=window, columns=columns, show='headings')
        for col in columns:
            list_box.heading(col, text=col)
        list_box.grid(row=0, column=0, columnspan=4, sticky='nsew')
        self.client.listBox = list_box
        self.client.start()
        window.mainloop()


if __name__ == '__main__':
    gui = GUI()
    gui.main()

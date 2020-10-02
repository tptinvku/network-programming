import os
import time
import socket as sc
import tkinter as tk
from decouple import config
from threading import Thread


class Client:
    def __init__(self):
        self.max_delay = 1
        self.default_msg = b'Hi'
        self.ip = config('IP')
        self.port = int(config('PORT'))
        self.address = (self.ip, self.port)
        self.socket = sc.socket(family=sc.AF_INET, type=sc.SOCK_DGRAM)
        stop = Thread(target=self.stop)
        stop.start()

    def start(self):
        while True:
            try:
                self.socket.sendto(self.default_msg, self.address)
                data, server = self.socket.recvfrom(4096)
                if data:
                    print(data)
                else:
                    self.socket.close()
                    os._exit(0)
                time.sleep(self.max_delay)

            except sc.error:
                self.socket.close()
                os._exit(0)
                break
            except Exception:
                self.socket.close()
                os._exit(0)
                break

    def stop(self):
        while True:
            key = input('').strip().lower()
            if key == 'q':
                self.socket.close()
                os._exit(0)


class GUI:
    def __init__(self):
        self.client = Client()
        self.client.start()

    def create_table(self, window):
        for i in range(3):
            for j in range(4):
                self.entry = tk.Entry(master=window, width=tk.X)
                self.entry.grid(row=i, column=j)
                # self.entry.insert(tk.END, )

    def main(self):
        window = tk.Tk()
        window.title('Client')

        self.create_table(window)


if __name__ == '__main__':
    # start = GUI()
    # start.main()
    client = Client()
    client.start()
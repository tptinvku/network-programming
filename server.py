import os
import socket as sc
import sys
from threading import Thread

from decouple import config


class Server:
    def __init__(self):
        self.IP = config("IP")
        self.PORT = int(config("PORT"))
        self.address = (self.IP, self.PORT)
        self.socket = sc.socket(family=sc.AF_INET, type=sc.SOCK_DGRAM)

    def start(self):
        self.socket.bind(self.address)
        print("Server: Created Socket!", end='\n')
        communication = Communication(self.socket)
        communication.start()
        stop = Thread(target=self.stop)
        stop.start()

    def stop(self):
        while True:
            key = input('')
            if key == 'q':
                self.socket.close()
                os._exit(0)


class Communication(Thread):
    def __init__(self, socket):
        super().__init__()
        self.socket = socket

    def run(self):
        while True:
            data, address = self.socket.recvfrom(4096)
            print(data.decode())
            if data:
                self.socket.sendto(
                    f'Server: received "{data.decode().split(":")[1].strip()}" from {data.decode().split(":")[0].strip()}'.encode(
                    ),
                    address)


if __name__ == "__main__":
    sv = Server()
    sv.start()

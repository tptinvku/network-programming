import os
import random
import socket as sc
from decouple import config
from threading import Thread
from datetime import datetime


class ExchangeRateFake(Thread):
    def __init__(self, server, address):
        super(ExchangeRateFake, self).__init__()
        self.server = server
        self.address = address
        self.threads = []
        self.unit = ['USD', 'JPY', 'HKD']
        self.from_currency = 'VND'
        self.to_currency = ''
        self.now = datetime.now()
        self.last_refreshed = self.now.strftime("%H:%M:%S - %d/%m/%Y")

    def by_unit(self, index):
        usd = random.random()
        jpy = random.random()
        hkd = random.random()
        exchange_rate = (usd, jpy, hkd)
        self.to_currency = self.unit[index]
        message = f'{self.from_currency}|{self.to_currency}|{exchange_rate[index]}|{self.last_refreshed}'.encode()
        self.server.socket.sendto(message, self.address)

    def run(self):
        while True:
            for index in range(len(self.unit)):
                thread = Thread(target=self.by_unit, args=(index, ))
                self.threads.append(thread)
                thread.start()


class Server:
    def __init__(self):
        self.ip = config('IP')
        self.port = int(config('PORT'))
        self.address = (self.ip, self.port)
        self.socket = sc.socket(family=sc.AF_INET, type=sc.SOCK_DGRAM)
        stop = Thread(target=self.stop)
        stop.start()

    def start(self):
        self.socket.bind(self.address)
        while True:
            try:
                data, address = self.socket.recvfrom(4096)
                if data:
                    exchange_rate_fake = ExchangeRateFake(self, address)
                    exchange_rate_fake.start()
                    message = data.decode()
                    print(message)
                else:
                    self.socket.close()
                    os._exit(0)
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


if __name__ == '__main__':
    sv = Server()
    sv.start()

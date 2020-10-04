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
        self.markets = ['USD', 'JPY', 'HKD']
        self.units = ['USD', 'JPY', 'HKD', 'VND', 'LAK', 'SGD', 'BRD']
        self.from_currency = ''
        self.message = ''

    def by_unit(self, index, to_currency, exchange_rate):
        if not to_currency == self.from_currency:
            now = datetime.now()
            last_refreshed = now.strftime("%H:%M:%S - %d/%m/%Y")
            self.message = f'{index}|{self.from_currency}|{to_currency}|{exchange_rate}|{last_refreshed}'.encode()
            self.server.socket.sendto(self.message, self.address)
            self.message = ''

    def run(self):
        while True:
            to_currency = self.units
            usd = random.random()
            jpy = random.random()
            hkd = random.random()
            vnd = random.random()
            lak = random.random()
            sgd = random.random()
            brd = random.random()
            exchange_rate = (usd, jpy, hkd, vnd, lak, sgd, brd)
            list_rate = list(exchange_rate)
            for index in range(len(self.units)):
                if self.from_currency == self.units[index]:
                    to_currency.remove(self.from_currency)
                    list_rate.pop(index)
                    break
            for index in range(len(to_currency)):
                thread = Thread(target=self.by_unit, args=(index, to_currency[index], list_rate[index]), daemon=True)
                self.threads.append(thread)
                thread.start()

            for thread in self.threads:
                thread.join()


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
                message = data.decode()
                exchange_rate_fake = ExchangeRateFake(self, address)
                if data:
                    # print(message)
                    if message in exchange_rate_fake.markets:
                        print(message)
                        exchange_rate_fake.from_currency = message
                        exchange_rate_fake.start()

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

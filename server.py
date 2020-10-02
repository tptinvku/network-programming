import os
import time
import requests
import socket as sc
from decouple import config
from threading import Thread


class ExchangeRate(Thread):
    def __init__(self, server, address):
        super(ExchangeRate, self).__init__()
        self.max_delay = 60
        self.list_rate = ['USD', 'JPY', 'HKD']
        self.function = 'CURRENCY_EXCHANGE_RATE'
        self.api_key = config('KEY')
        self.from_currency = 'VND'
        self.to_currency = ''
        self.server = server
        self.address = address
        self.exchange_rate = ''
        self.last_refreshed = ''
        self.threads = []

    def by_unit(self, index):
        self.to_currency = self.list_rate[index]
        main_url = f'https://www.alphavantage.co/query?function={self.function}&from_currency={self.from_currency}&to_currency={self.to_currency}&apikey={self.api_key}'
        response = requests.get(main_url)
        if response.status_code == 200:
            try:
                result = response.json()
                detail = result['Realtime Currency Exchange Rate']
                self.exchange_rate = detail['5. Exchange Rate']
                self.last_refreshed = detail['6. Last Refreshed']
            except Exception as e:
                print(e)
                # self.server.socket.sendto(self.exchange_rate.encode(), self.address)

        time.sleep(self.max_delay)

    def run(self):
        while True:
            for i in range(len(self.list_rate)):
                thread = Thread(target=self.by_unit, args=(i,))
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
                if message:
                    print(message)
                    exchange_rate = ExchangeRate(self, address)
                    exchange_rate.start()
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

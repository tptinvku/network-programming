from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QThread
from PyQt5 import QtCore
from threading import Thread
from sys import platform
import socket as sc
import random
import base64
import datetime
import os


class Controller:
    def __init__(self, ui):
        self.ui = ui
        self.friends = []
        self.conn_state = False
        self.address = ()

    def event_catch(self):
        self.ui.btn_file.clicked.connect(
            lambda: self.openFileDialog()
        )
        self.ui.btn_send.clicked.connect(
            lambda: self.send()
        )

        self.ui.btn_connect.clicked.connect(
            lambda: self.connect()
        )

    def send(self):
        if self.ui.txt_msg.text() and self.address:
            send = Send(self.ui, self.address, self.socket)
            send.start()

    def openFileDialog(self):
        window = QFileDialog.getOpenFileName(
            caption="Choose Files",
            filter="Text file (*.txt) ;;Image file (*.png, *.jpg)"
        )
        self.ui.txt_msg.setText(window[0])

    def connect(self):
        self.socket = sc.socket(sc.AF_INET, sc.SOCK_DGRAM)
        self.host = self.ui.txt_host.text()
        self.port = self.ui.txt_port.text()
        _translate = QtCore.QCoreApplication.translate
        if self.host and self.port:
            self.address = (self.host, int(self.port))
            if not self.conn_state:
                self.conn_state = True
                if (self.host, self.port) not in self.friends:
                    try:
                        self.ui.btn_connect.setText(_translate("Form", "Disconnect"))
                        self.friends.append((self.host, int(self.port)))
                        for friend in self.friends:
                            self.ui.txt_friends.append(f"{friend}\n")
                        print(self.friends)
                    except sc.error:
                        self.socket = sc.socket(sc.AF_INET, sc.SOCK_DGRAM)
            else:
                self.conn_state = False
                self.ui.btn_connect.setText(_translate("Form", "Connect"))
                self.friends.remove(self.address)
                self.ui.txt_friends.clear()
                for friend in self.friends:
                    self.ui.txt_friends.append(f"{friend}\n")
                self.ui.txt_chat.append(f"{self.address}: lose connect")
                self.socket.close()

            self.client = Client(self.ui, self.address, self.socket)
            self.client.start()


class Client(Thread):
    def __init__(self, ui, address, socket):
        super(Client, self).__init__()
        self.ui = ui
        self.address = address
        self.socket = socket

    def run(self):
        receive = Receive(self.socket, self.ui)
        receive.start()


class Send(Thread):
    def __init__(self, ui, address, socket):
        super(Send, self).__init__()
        self.ui = ui
        self.address = address
        self.socket = socket

    def file_type(self, filename, codecheck):
        with open(filename, 'rb') as file:
            if codecheck != 'file_txt':
                file_data = codecheck.encode('utf-8') + base64.b64encode(file.read(1024 * 25))
            else:
                file_send = codecheck.encode('utf-8') + file.read(1024 * 25)
                file_data = file_send
            self.socket.sendto(file_data, self.address)
            self.ui.txt_msg.append(f"{self.address}: 'Send file done'\n")
            self.ui.txt_msg.setText("")

    def run(self):
        try:
            if self.ui.txt_msg.text():
                message = self.ui.txt_msg.text()
                if message[-4:] == '.txt':
                    self.file_type(message, 'file_txt')
                elif message[-4:] == '.png':
                    self.file_type(message, 'file_png')
                elif message[-4:] == '.jpg':
                    self.file_type(message, 'file_jpg')
                else:
                    # send message
                    mgs = 'mgs' + message
                    self.socket.sendto(f"{self.address}: {mgs}".encode('utf-8'), self.address)
                self.ui.txt_chat.append(f"{self.address}: {message}\n")
                self.ui.txt_msg.setText("")
        except Exception as e:
            print(e)


class Receive(Thread):
    def __init__(self, socket, ui):
        super(Receive, self).__init__()
        self.ui = ui
        self.socket = socket
        self.buffer_size = 1024 * 25

    def save_file(self, type, data):
        filename = datetime.datetime.now().strftime('%d_%m_%Y_%H_%M_%S') + type
        if type != '.txt':
            file = open(filename, 'wb')
            data = base64.b64decode(data[8:])
            file.write(data)
        else:
            file = open(filename, 'w')
            file.write(data[8:])
        file.close()
        print('Done')

    def run(self):
        while 1:
            try:
                mess, addr = self.socket.recvfrom(self.buffer_size)
                data = mess.decode('utf_8')
                check = data[:8]
                if check == 'file_txt':
                    self.save_file('.txt', data)
                elif check == 'file_png':
                    self.save_file('.png', data)
                elif check == 'file_jpg':
                    self.save_file('.jpg', data)
                elif data[22:25] == 'mgs':
                    new_mgs = data[:21] + " " + data[25:]
                    self.ui.txt_chat.append(new_mgs)
            except Exception as e:
                print(e)
                break


class Server(QThread):
    def __init__(self, ui):
        super(Server, self).__init__()
        self.ui = ui
        self.host = "localhost"
        self.port = random.randint(6000, 6500)
        self.ui.txt_comp_name.setText(sc.gethostname())
        self.ui.txt_address.setText(f"{self.host}:{self.port}")
        self.address = (self.host, self.port)
        self.socket = sc.socket(sc.AF_INET, sc.SOCK_DGRAM)
        self.buffer_size = 1024 * 25

    def run(self):
        self.socket.bind(self.address)
        response = ServerResponse(self,self.ui)
        response.start()


class ServerResponse(Thread):
    def __init__(self, server, ui):
        super(ServerResponse, self).__init__()
        self.server = server
        self.ui = ui
        self.buffer_size = 1024 * 25

    def save_file(self, type, data):
        filename = datetime.datetime.now().strftime('%d_%m_%Y_%H_%M_%S') + type
        if type != '.txt':
            file = open(filename, 'wb')
            data = base64.b64decode(data[8:])
            file.write(data)
        else:
            file = open(filename, 'w')
            file.write(data[8:])
        file.close()
        self.ui.txt_chat.append('Save file done')

    def file_type(self, filename, codecheck):
        try:
            file = open(filename, 'rb')
            if codecheck != 'file_txt':
                file_data = codecheck.encode('utf-8') + base64.b64encode(file.read(1024 * 25))
            else:
                file_send = codecheck.encode('utf-8') + file.read(1024 * 25)
                file_data = file_send
            self.server.socket.sendto(file_data, self.server.address)
            self.ui.txt_chat.append('Send file done')
        except Exception as e:
            print(e)

    def run(self):
        while 1:
            try:
                mess, addr = self.server.socket.recvfrom(self.buffer_size)
                data = mess.decode('utf_8')
                check = data[:8]
                if check == 'file_txt':
                    self.save_file('.txt', data)
                elif check == 'file_png':
                    self.save_file('.png', data)
                elif check == 'file_jpg':
                    self.save_file('.jpg', data)
                elif data[22:25] == 'mgs':
                    new_mgs = data[:21] + " " + data[25:]
                    self.ui.txt_chat.append(new_mgs)
                if self.ui.txt_msg.text():
                    message = self.ui.txt_msg.text()
                    if message[-4:] == '.txt':
                        self.file_type(message, 'file_txt')
                    elif message[-4:] == '.png':
                        self.file_type(message, 'file_png')
                    elif message[-4:] == '.jpg':
                        self.file_type(message, 'file_jpg')
                    else:
                        # send message
                        mgs = 'mgs' + message
                        self.server.socket.sendto(f"{addr}: {mgs}".encode('utf-8'), addr)
                    self.ui.txt_msg.setText("")
            except Exception as e:
                # print(e)
                break


def clear_console():
    if platform.system().lower() == "windows":
        os.system("cls")
    else:
        os.system("clear")

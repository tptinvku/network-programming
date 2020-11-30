import sys
import rsa
import time
import socket as sc
from decouple import config

ip = config("IP")
port = int(config("PORT"))
server_address = (ip, port)

socket = sc.socket(family=sc.AF_INET, type=sc.SOCK_STREAM)
socket.connect(server_address)
client_name = input("Enter your name:")

public_key, private_key = rsa.newkeys(512)
save_pk = public_key.save_pkcs1(format="DER")
socket.sendall(save_pk)
time.sleep(2)
while 1:
    message = input(f"{client_name}: ")
    if message in list(("q", "quit", "exit", "close", "cancel")):
        sys.exit(0)
    else:
        socket.sendall(f"{client_name}: {message}".encode())
        data = socket.recv(1024)
        if data:
            print(rsa.decrypt(data, private_key).decode())

import sys
import rsa
import time
import socket as sc
from decouple import config

ip = config("IP")
port = int(config("PORT"))
server_address = (ip, port)

socket = sc.socket(family=sc.AF_INET, type=sc.SOCK_STREAM)
socket.bind(server_address)
socket.listen()

connection, address = socket.accept()

public_key, private_key = rsa.newkeys(512)
save_pk = public_key.save_pkcs1(format="DER")
connection.sendall(save_pk)
time.sleep(2)

client_save_pk = connection.recv(1024)
PublicKey = rsa.key.PublicKey.load_pkcs1(client_save_pk, format="DER")
print(f"Client: {PublicKey}")
while 1:
    data = connection.recv(1024)
    if data:
        print(f"{address}|{rsa.decrypt(data, private_key).decode()}")
        message = input("Server: ")
        if message in list(("q", "quit", "exit", "close", "cancel")):
            sys.exit(0)
        else:
            encrypted_message = rsa.encrypt(f"Server: {message}".encode(), PublicKey)
            connection.sendall(encrypted_message)

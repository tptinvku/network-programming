import sys
import rsa
import socket as sc
from decouple import config

ip = config("IP")
port = int(config("PORT"))
server_address = (ip, port)

socket = sc.socket(family=sc.AF_INET, type=sc.SOCK_STREAM)
socket.bind(server_address)
socket.listen()

connection, address = socket.accept()
save_pk = connection.recv(1024)
public_key = rsa.key.PublicKey.load_pkcs1(save_pk, format="DER")
print(public_key)
while 1:
    data = connection.recv(1024)
    if data:
        print(f"{address}|{data.decode()}")
        message = input("Server: ")
        if message in list(("q", "quit", "exit", "close", "cancel")):
            sys.exit(0)
        else:
            encrypted_message = rsa.encrypt(f"Server: {message}".encode(), public_key)
            connection.sendall(encrypted_message)

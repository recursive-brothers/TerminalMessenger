#!/usr/bin/env python3

import socket

#this came from https://realpython.com/python-sockets

HOST = '172.20.10.3'  # The server's hostname or IP address
PORT = 3333        # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    while True:
        message = input().encode()
        s.sendall(message)
        data = s.recv(1024)
        


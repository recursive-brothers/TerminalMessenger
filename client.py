#!/usr/bin/env python3

import socket
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('port')
args = parser.parse_args()

# This code is based on the simple client from https://realpython.com/python-sockets

HOST = '172.20.10.4'  # The server's hostname or IP address
PORT = int(args.port) # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    while True:
        message = input('> ').encode()
        s.sendall(message)
        data = s.recv(1024)


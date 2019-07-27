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
        print(data)

# async def async_input(server_socket):
#     while True:
#         message = await ainput("> ")
#         server_socket.sendall(message)

# async def get_messages(server_socket):
#     while True:
#         received_message = server_socket.recv(1024)
#         if received_message:
#             print(received_message)




# async def main(s):
#     get_input = asyncio.create_task(async_input(s))
#     get_output = asyncio.create_task(get_messages(s))
#     await get_input
#     await get_output

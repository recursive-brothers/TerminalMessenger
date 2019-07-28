#!/usr/bin/env python3

import socket
import argparse
import asyncio
from aioconsole import ainput

parser = argparse.ArgumentParser()
parser.add_argument('port')
args = parser.parse_args()


HOST = '18.222.230.158'  # The server's hostname or IP address
PORT = int(args.port) # The port used by the server


async def get_user_input(server_socket):
    while True:
        message = await ainput("> ")
        server_socket.sendall(message.encode())
        await asyncio.sleep(.1)

async def get_messages(server_socket):
    while True:
        received_message = None
        try:
            received_message = server_socket.recv(1024).decode()
        except:
            pass
        if received_message:
            print('\n' + received_message + '\n>', end='')
        await asyncio.sleep(.1)
          
async def main(s):
    get_input = asyncio.ensure_future(get_user_input(s))
    get_output = asyncio.ensure_future(get_messages(s))
    await get_output
    await get_input
    

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.setblocking(False)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(s))
    
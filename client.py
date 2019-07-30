#!/usr/bin/env python3

import socket
import argparse
import asyncio
from aioconsole import ainput
import curses
import logging

logging.basicConfig(filename='server.log',
                            filemode='a',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)



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
            print('\n' + received_message + '\n> ', end='')
        await asyncio.sleep(.1)
          
async def background_tasks(s):
    get_input = asyncio.ensure_future(get_user_input(s))
    get_output = asyncio.ensure_future(get_messages(s))
    await get_output
    await get_input
    

# with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#     s.connect((HOST, PORT))
#     s.setblocking(False)
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(background_tasks(s))
    


def main(stdscr):
    # curses.echo()
    num_rows, num_cols = stdscr.getmaxyx()
    

    received_messages_rows = int(.85 * num_rows)
    sending_message_rows = num_rows - received_messages_rows

    received_window = curses.newwin(received_messages_rows,num_cols,0,0)
    received_window.border('|', '|', '-', '-', '+', '+', '+', '+')
    received_window.refresh()

    input_window = curses.newwin(sending_message_rows,num_cols,received_messages_rows,0)
    input_window.border('|', '|', '-', '-', '+', '+', '+', '+')
    input_window.refresh()

    input_window.nodelay(True)
    received_window.nodelay(True)
    
    built_str = ''
    y_position = 1
    x_position = 1
    while True:

        ch = input_window.getch(y_position,x_position)

        if ch != curses.ERR:
            if ch == ord('\n'):
                input_window.erase()
                input_window.border('|', '|', '-', '-', '+', '+', '+', '+')
                input_window.refresh()
                received_window.addstr(1,1,built_str)
                received_window.refresh()
                x_position = y_position = 1
                built_str = ''

            elif ch == 127:
                input_window.addstr(y_position,x_position - 1,"  ")
                input_window.refresh()
                x_position -= 1
            
            else:
                built_str += chr(ch)
                input_window.addstr(y_position,x_position,chr(ch))
                x_position += 1 

        if x_position == num_cols - 1:
            y_position += 1
            x_position = 1
        if x_position == 0:
            if y_position != 1:
                y_position -= 1
                x_position = num_cols - 2
            else:
                x_position = 1    


curses.wrapper(main)
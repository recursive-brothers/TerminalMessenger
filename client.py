#!/usr/bin/env python3

import socket
import argparse
import asyncio
import curses
import logging
import json
import traceback
from client_modules import *


logging.basicConfig(filename='client.log',
                            filemode='a',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)

parser = argparse.ArgumentParser()
parser.add_argument('port')
parser.add_argument('--name', '-n', default='Anonymous')
args = parser.parse_args()

HOST    = 'terminalmessenger.com'
PORT    = int(args.port)


async def main(s: socket.socket) -> None:
    stdscr = setup_curses()

    num_rows, num_cols = stdscr.getmaxyx()
    received_window_rows = int(RECEIVED_WINDOW_RATIO * num_rows)
    input_window_rows = num_rows - received_window_rows
    
    received_window = ReceivedWindow(received_window_rows, num_cols, 0, 1)
    input_window = InputWindow(input_window_rows, num_cols, received_window_rows, 0, 1, 1)
    
    get_input = asyncio.ensure_future(get_user_input(s, input_window, received_window))
    get_output = asyncio.ensure_future(receive_server_messages(s, received_window))
    await get_output
    await get_input

def setup_curses(): # -> Window
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(SENDER.SELF.value, curses.COLOR_BLUE, -1)
    curses.init_pair(SENDER.TERMINAL.value, curses.COLOR_GREEN, -1)
    curses.init_pair(SENDER.OTHER.value, curses.COLOR_YELLOW, -1)
    return stdscr

def cleanup_curses() -> None:
    curses.nocbreak()
    curses.echo()
    curses.endwin()

def handshake(server_socket: socket.socket) -> None:
    ip_and_port = json.loads(server_socket.recv(BUFFER_SIZE).decode())
    utils.ADDRESS = [ip_and_port['address'], ip_and_port['port']]
    server_socket.sendall(args.name.encode())
    server_socket.setblocking(False)

if __name__ == "__main__":
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            handshake(s)
            loop = asyncio.get_event_loop()
            loop.run_until_complete(main(s))
    except KeyboardInterrupt:
        logging.debug("keyboard interrupt, shutting down client")
        cleanup_curses()
    except ConnectionRefusedError:
        logging.debug(traceback.format_exc())
        print("Can't connect to server. Try again later.")
    except socket.gaierror:
        logging.debug(traceback.format_exc())
        print("Can't find the server. Are you connected to the internet?")
    
""" 
Implement proper exception handling for asyncio as current errors are just
being swallowed and the client hangs

--> Right now, if you get the timeout error, our program just doesn't do anything except let you type. Very annoying.
    Probably related to asyncIO eating our exceptions.
"""

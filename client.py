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

async def main(s):
    stdscr = setup_curses()

    num_rows, num_cols = stdscr.getmaxyx()
    received_window_rows = int(RECEIVED_WINDOW_RATIO * num_rows)
    input_window_rows = num_rows - received_window_rows
    
    received_window = ReceivedWindow(received_window_rows, num_cols, 0, 1)
    input_window = InputWindow(input_window_rows, num_cols, received_window_rows, 0, 1, 1)
    
    get_input = asyncio.ensure_future(get_user_input(s, input_window, received_window, num_cols, received_window_rows))
    get_output = asyncio.ensure_future(receive_server_messages(s, received_window))
    await get_output
    await get_input

def setup_curses():
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(SENDER.SELF.value, curses.COLOR_BLUE, -1)
    curses.init_pair(SENDER.TERMINAL.value, curses.COLOR_GREEN, -1)
    curses.init_pair(SENDER.OTHER.value, curses.COLOR_YELLOW, -1)
    return stdscr

def cleanup_curses():
    curses.nocbreak()
    curses.echo()
    curses.endwin()

def handshake(server_socket):
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
    except:
        logging.debug(traceback.format_exc())
    finally:
        cleanup_curses()
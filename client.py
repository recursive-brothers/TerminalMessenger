#!/usr/bin/env python3

import socket
import argparse
import asyncio
import curses
import logging
import datetime
import json
import traceback
from enum import Enum

logging.basicConfig(filename='client.log',
                            filemode='a',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)



parser = argparse.ArgumentParser()
parser.add_argument('port')
parser.add_argument('--name', '-n', default='Anonymous')
args = parser.parse_args()



HOST    = '18.222.230.158'  # The server's hostname or IP address
PORT    = int(args.port) # The port used by the server
ADDRESS = None

BUFFER_SIZE = 1024
SLEEP_TIME  = .001

ENTER       = 10
BACKSPACE   = 127
SCROLL      = 27
SCROLL_UP   = 65
SCROLL_DOWN = 66

RECEIVED_WINDOW_RATIO = .85

class SENDER(Enum):
    SELF     = 1
    TERMINAL = 2
    OTHER    = 3




class StringBuilder:
    def __init__(self):
        self.ch_list = []

    def _append(self, seq):
        self.ch_list.append(seq)
    
    def delete(self, num):
        self.ch_list = self.ch_list[:num * -1]

    def build(self):
        built_str = ''.join(self.ch_list)
        self.ch_list.clear()
        return built_str

    def __iadd__(self, seq):
        self._append(seq)

    def __bool__(self):
        return bool(self.ch_list)


class CursorPosition:
    def __init__(self,startY,startX):
        self.y = startY
        self.x = startX

class ReceivedWindow:
    def __init__(self, num_rows, num_cols, startY, startX):
        self.cursor = CursorPosition(startY, startX)
        self.window = curses.newpad(num_rows, num_cols)
        self.width = num_cols
        self.height = num_rows

        self.display_width = num_cols
        self.display_height = num_rows

        self.top_left = CursorPosition(0, 0)

        self.window.scrollok(True)
        self.window.idlok(True)
        self.window.nodelay(True)
        self.refresh()

    def refresh(self):
        self.window.refresh(self.top_left.y, self.top_left.x, 0, 0, self.display_height - 1, self.display_width - 1) #refresh display_height -1 to avoid overlap

    def scroll(self, lines):
        if lines < 0 or (self.top_left.y + self.display_height < self.height):
            self.top_left.y = max(self.top_left.y + lines, 0)
            self.refresh()

    def _paint_str(self, string, color_fmt):
        width = self.width - 2
        while string:
            self.window.addstr(self.cursor.y, self.cursor.x, string[:width], color_fmt)
            self.cursor.y += 1
            string = string[width:]

    def paint_message(self, metadata, message, color):
        # we have a one character margin on both sides of the received window
        width = self.width - 2

        # calculation works as follows:
        # height of metadata is ceiling of metadata length over width of screen (1 + floor(len(metadata) / width))
        # height of message is ceiling of message length over width of screen (1 + floor(len(message) / width))
        # we cannot add the length of metadata and message and divide by width:
        #     if length of metadata and message are both slightly longer than width, then adding would give
        #     a height of 3 lines, when in reality it should be 4.
        message_line_height = 2 + int(len(metadata) / width) + int(len(message) / width)
        lines_to_scroll = message_line_height + self.cursor.y - self.height

        if lines_to_scroll > 0:
            self.height += lines_to_scroll
            self.scroll(lines_to_scroll)
            self.window.resize(self.height, self.width)

        self._paint_str(metadata, curses.color_pair(color) | curses.A_STANDOUT)
        self._paint_str(message, curses.color_pair(color))

        self.refresh()

class InputWindow:
    def __init__(self, num_rows, num_cols, startY, startX, cursorY, cursorX):
        self.height = num_rows
        self.width = num_cols
        self.window = curses.newwin(num_rows, num_cols,startY,startX)
        self.cursor = CursorPosition(cursorY, cursorX)
        self.window.nodelay(True)
        self.add_border()
        self.window.refresh()
    
    def clear_text(self):
        self.window.erase()
        self.window.border('|', '|', '-', '-', '+', '+', '+', '+')
        self.window.refresh()
        self.cursor.x = self.cursor.y = 1

    def add_char(self, ch):
        self.window.addstr(self.cursor.y,self.cursor.x,chr(ch))
        self.cursor.x += 1 

        if self.cursor.x == self.width - 1:
            self.cursor.y += 1
            self.cursor.x = 1
    
    def add_border(self):
        self.window.border('|', '|', '-', '-', '+', '+', '+', '+')
    
    def get_input(self):
        return self.window.getch(self.cursor.y, self.cursor.x)
    
    def backspace(self):
        if self.cursor.x <= 1 and self.cursor.y <=1:
            return
        self.window.addstr(self.cursor.y, self.cursor.x - 1, " ")
        self.window.refresh()
        self.cursor.x -= 1
    
        if self.cursor.x == 0:
            if self.cursor.y != 1:
                self.cursor.y -= 1
                self.cursor.x = self.width - 2
            else:
                self.cursor.x = 1

def handle_enter(server_socket, accumulated_input, input_window):
    if accumulated_input:
        input_window.clear_text()
        server_socket.sendall(accumulated_input.build().encode())

def handle_backspace(accumulated_input, input_window):
    accumulated_input.delete(1)
    input_window.backspace()

def handle_scroll(input_window, received_window):
    input_window.get_input()
    scroll_direction = input_window.get_input()
    if scroll_direction == SCROLL_UP:
        received_window.scroll(-1)
    elif scroll_direction == SCROLL_DOWN:
        received_window.scroll(1)

# this name is bad
def handle_normal_ch(ch, accumulated_input, input_window):
    accumulated_input += chr(ch)
    input_window.add_char(ch)


async def get_user_input(server_socket, input_window, received_window, num_rows, num_cols):
    accumulated_input = StringBuilder()
    while True:
        ch = input_window.get_input()
        if ch != curses.ERR:
            if ch == ENTER:
                handle_enter(server_socket, accumulated_input, input_window)
            elif ch == BACKSPACE: 
                handle_backspace(accumulated_input, input_window) 
            elif ch == SCROLL: 
                handle_scroll(input_window, received_window)
            else:
                handle_normal_ch(ch, accumulated_input, input_window)
                
        await asyncio.sleep(SLEEP_TIME)

def determine_sender(addr):
    sender = None
    if addr == ADDRESS:
        sender = SENDER.SELF
    elif addr == 0:
        sender = SENDER.TERMINAL
    else: 
        sender = SENDER.OTHER
    return sender.value

def format_metadata(received_message):
    messager = received_message["name"]
    curr_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    return f'{messager}     {curr_time}'


async def receive_server_messages(server_socket, received_window):
    while True:
        json_message = None
        try:
            json_message = server_socket.recv(BUFFER_SIZE).decode()
        except:
            pass
        if json_message:
            received_message = json.loads(json_message)
            logging.debug(received_message)

            message  = received_message["message"]
            color_num = determine_sender(received_message['address'])
            metadata = format_metadata(received_message)
            received_window.paint_message(metadata, message, color_num)


        await asyncio.sleep(SLEEP_TIME)

          
async def main(s):
    stdscr = setup_curses()

    num_rows, num_cols = stdscr.getmaxyx()
    received_window_rows = int(RECEIVED_WINDOW_RATIO * num_rows)
    input_window_rows = num_rows - received_window_rows
    
    # do we want documentation for what this means?
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
    global ADDRESS
    ip_and_port = json.loads(server_socket.recv(BUFFER_SIZE).decode())
    ADDRESS = [ip_and_port['address'], ip_and_port['port']]
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


"""
1. break things up into multiple files, e.g. key handlers, the different classes
2. add docs
"""
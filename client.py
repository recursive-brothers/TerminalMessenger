#!/usr/bin/env python3

import socket
import argparse
import asyncio
from aioconsole import ainput
import curses
import logging
import datetime

logging.basicConfig(filename='client.log',
                            filemode='a',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)



parser = argparse.ArgumentParser()
parser.add_argument('port')
args = parser.parse_args()


HOST = '18.222.230.158'  # The server's hostname or IP address
PORT = int(args.port) # The port used by the server


def init_input_window(rows,cols,startY,startX):
    input_window = curses.newwin(rows,cols,startY,startX)
    input_window.border('|', '|', '-', '-', '+', '+', '+', '+')
    input_window.refresh()
    return input_window
    
    
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
        self.window.refresh(0, 0, 0, 0, num_rows, num_cols)

    def refresh(self):
        self.window.refresh(self.top_left.y, self.top_left.x, 0, 0, self.display_height, self.display_width)

    def scroll(self, lines):
        self.top_left.y += lines
        self.refresh()

    def paint_message(self, built_str):
        message_height = int(2 + len(built_str) / (self.width - 2))
        lines_to_scroll = message_height + self.cursor.y - self.height

        if lines_to_scroll > 0:
            self.height += lines_to_scroll
            self.scroll(lines_to_scroll)
            self.window.resize(self.height, self.width)

        curr_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        self.window.addstr(self.cursor.y, self.cursor.x, f'> {curr_time}')
        self.cursor.y += 1

        while True:
            self.window.addstr(self.cursor.y, self.cursor.x, built_str[:self.width - 2])
            self.cursor.y += 1
            if len(built_str) > self.width - 2:
                built_str = built_str[self.width-2:]
            else:
                break

        self.refresh()


def send_message(input_window, received_window, input_window_cursor, num_cols, num_rows, built_str):
    input_window.erase()
    input_window.border('|', '|', '-', '-', '+', '+', '+', '+')
    input_window.refresh()
    input_window_cursor.x = input_window_cursor.y = 1
    received_window.paint_message("".join(built_str))
    built_str.clear()


def backspace(input_window, input_window_cursor, built_str, num_cols):
    if len(built_str) <= 0:
        return
    input_window.addstr(input_window_cursor.y, input_window_cursor.x - 1, "  ")
    input_window.refresh()
    built_str.pop()
    input_window_cursor.x -= 1

    if input_window_cursor.x == 0:
        if input_window_cursor.y != 1:
            input_window_cursor.y -= 1
            input_window_cursor.x = num_cols - 2
        else:
            input_window_cursor.x = 1

def build_message(input_window, input_window_cursor, built_str, num_cols, ch):
    built_str.append(chr(ch))
    input_window.addstr(input_window_cursor.y,input_window_cursor.x,chr(ch))
    input_window_cursor.x += 1 

    if input_window_cursor.x == num_cols - 1:
        input_window_cursor.y += 1
        input_window_cursor.x = 1

def received_window_scroll(ch,received_window, num_rows, num_cols):
    
    if ch == 65:
        received_window.scroll(-1)
    elif ch == 66:
        received_window.scroll(1)

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

    def add_char(self,ch):
        logging.debug("in add char")
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
        logging.debug("in backspace!")
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

async def get_user_input(server_socket, input_window, received_window, num_rows, num_cols):
    built_str = []
    

    while True:
        ch = input_window.get_input()
        if not ch == -1:
            logging.debug(ch)

        if ch != curses.ERR:
            if ch == ord('\n'):
                if built_str:
                    # input_window.erase()
                    # input_window.border('|', '|', '-', '-', '+', '+', '+', '+')
                    # input_window.refresh()
                    # input_window_cursor.x = input_window_cursor.y = 1
                    input_window.clear_text()
                    server_socket.sendall("".join(built_str).encode())
                    built_str.clear()

            elif ch == 127:
                if built_str:
                    built_str.pop()
                input_window.backspace()
                # backspace(input_window, input_window_cursor, built_str, num_cols)

            elif ch == 27:
                input_window.get_input()
                scroll_direction = input_window.get_input()
                if scroll_direction == 65:
                    received_window.scroll(-1)
                elif scroll_direction == 66:
                    received_window.scroll(1)

            else:
                built_str.append(chr(ch))
                input_window.add_char(ch)

        await asyncio.sleep(.001)

async def get_messages(server_socket, received_window):
    while True:
        received_message = None
        try:
            received_message = server_socket.recv(1024).decode()
        except:
            pass
        if received_message:
            received_window.paint_message(received_message)

        await asyncio.sleep(.001)

          
async def background_tasks(s):
    stdscr = curses.initscr()
    curses.noecho()
    
    num_rows, num_cols = stdscr.getmaxyx()
    
    received_messages_rows = int(.85 * num_rows)
    sending_message_rows = num_rows - received_messages_rows

    # might want to put these numbers into constants up top or somewhere so that it's easy to change and makes some goddamn sense
    received_window = ReceivedWindow(received_messages_rows, num_cols, 0, 1)
    
    input_window = InputWindow(sending_message_rows,num_cols,received_messages_rows,0,1,1)

    

    get_input = asyncio.ensure_future(get_user_input(s, input_window, received_window, num_cols, received_messages_rows))
    get_output = asyncio.ensure_future(get_messages(s, received_window))
    await get_output
    await get_input

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.setblocking(False)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(background_tasks(s))

"""
To keep in mind:
1. the 'keep track of total offset with scroll' functionality is the most gay thing ever created
2. Ideally, we encapsulate some of this scroll and redraw functionality in methods and encapsulate that in the class

Create a class for received window/pad, then do the same for input window, then, if there's enough similarity to justify it (and only if), then we can abstract that into another parent class
    If and ONLY IF (big Schnyder letters) we get to call it pee

Would also be nice to factor out num_rows and num_cols potentially into a screen class or something, and also create a string builder for built_str instead of doing it manually
We have to make a decision about what we choose to call received_window
"""

"""
TODO before moving to actual client

scroll messages when they fill page

after moving to client:
set a fixed number of lines for input and resize as necessary

EDGE CASES for scrolling
trying to scroll above all the messages that exist
trying to scroll past the messages that have been pasted
"""

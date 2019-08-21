#!/usr/bin/env python3

import socket
import argparse
import asyncio
import curses
import logging
import datetime
import json

logging.basicConfig(filename='client.log',
                            filemode='a',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)



parser = argparse.ArgumentParser()
parser.add_argument('port')
parser.add_argument('--name', '-n', default='Anonymous')
args = parser.parse_args()



HOST = '18.222.230.158'  # The server's hostname or IP address
PORT = int(args.port) # The port used by the server


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
        self.window.refresh(self.top_left.y, self.top_left.x, 0, 0, self.display_height-1, self.display_width-1) #refresh display_height -1 to avoid overlap

    def scroll(self, lines):
        if lines < 0 or (self.top_left.y + self.display_height < self.height):
            self.top_left.y = max(self.top_left.y + lines,0)
            self.refresh()
        
    def paint_message(self, received_message):
        message_height = int(2 + len(received_message) / (self.width - 2))
        lines_to_scroll = message_height + self.cursor.y - self.height

        if lines_to_scroll > 0:
            self.height += lines_to_scroll
            self.scroll(lines_to_scroll)
            self.window.resize(self.height, self.width)

        contents = json.loads(received_message)

        curr_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        self.window.addstr(self.cursor.y, self.cursor.x, f'{contents["name"]} {curr_time}')
        self.cursor.y += 1

        message = received_message["message"]

        while True:
            self.window.addstr(self.cursor.y, self.cursor.x, message[:self.width - 2])
            self.cursor.y += 1
            if len(message) > self.width - 2:
                message = message[self.width-2:]
            else:
                break

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

    def add_char(self,ch):
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


async def get_user_input(server_socket, input_window, received_window, num_rows, num_cols):
    built_str = []

    while True:
        ch = input_window.get_input()
        if ch != curses.ERR:
            if ch == ord('\n'):
                if built_str:
                    input_window.clear_text()
                    server_socket.sendall("".join(built_str).encode())
                    built_str.clear()

            elif ch == 127:
                if built_str:
                    built_str.pop()
                input_window.backspace()

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
    curses.cbreak()
    
    num_rows, num_cols = stdscr.getmaxyx()
    logging.debug(num_rows)
    logging.debug(num_cols)
    
    received_messages_rows = int(.85 * num_rows)
    sending_message_rows = num_rows - received_messages_rows
    logging.debug("peeeee")
    logging.debug(sending_message_rows)
    logging.debug(received_messages_rows)

    # might want to put these numbers into constants up top or somewhere so that it's easy to change and makes some goddamn sense
    received_window = ReceivedWindow(received_messages_rows, num_cols, 0, 1)
    logging.debug(received_window.window.getmaxyx())

    input_window = InputWindow(sending_message_rows,num_cols,received_messages_rows,0,1,1)
    logging.debug(input_window.window.getmaxyx())

    

    get_input = asyncio.ensure_future(get_user_input(s, input_window, received_window, num_cols, received_messages_rows))
    get_output = asyncio.ensure_future(get_messages(s, received_window))
    await get_output
    await get_input

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.setblocking(False)
    s.sendall(args.name.encode())
    loop = asyncio.get_event_loop()
    loop.run_until_complete(background_tasks(s))

"""
Bug list:
1. when you scroll up the top of input window border dissapears
2. when you scroll down past the last message, it just pastes the last message over and over again
"""

#!/usr/bin/env python3

import socket
import argparse
import asyncio
import curses
import logging
import datetime
import json
import traceback

logging.basicConfig(filename='client.log',
                            filemode='a',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)



parser = argparse.ArgumentParser()
parser.add_argument('port')
parser.add_argument('--name', '-n', default='Anonymous')
args = parser.parse_args()



HOST =    '18.222.230.158'  # The server's hostname or IP address
PORT =    int(args.port) # The port used by the server
ADDRESS = None

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

    def pick_color(self, addr):
        if addr == 0:
            return 3
        elif addr == ADDRESS:
            return 2
        else: 
            return 4
        
    def paint_message(self, json_message):
        received_message = json.loads(json_message)
        logging.debug(received_message)
        messager = received_message["name"]
        message  = received_message["message"]
        color_num = self.pick_color(received_message['address'])

        message_line_height = int(2 + len(message) / (self.width - 2))
        lines_to_scroll = message_line_height + self.cursor.y - self.height

        if lines_to_scroll > 0:
            self.height += lines_to_scroll
            self.scroll(lines_to_scroll)
            self.window.resize(self.height, self.width)


        curr_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

        self.window.addstr(self.cursor.y, self.cursor.x, f'{messager}     {curr_time}', curses.color_pair(color_num) | curses.A_STANDOUT)
        self.cursor.y += 1

        while True:
            self.window.addstr(self.cursor.y, self.cursor.x, message[:self.width - 2], curses.color_pair(color_num))
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

def handle_enter(server_socket, accumulated_input, input_window):
    if accumulated_input:
        input_window.clear_text()
        server_socket.sendall(accumulated_input.build().decode())

def handle_backspace(accumulated_input, input_window):
    accumulated_input.delete(1)
    input_window.backspace()

def handle_scroll(input_window, received_window):
    input_window.get_input()
    scroll_direction = input_window.get_input()
    if scroll_direction == 65:
        received_window.scroll(-1)
    elif scroll_direction == 66:
        received_window.scroll(1)

# this name is bad
def handle_normal_ch(ch, accumulated_input, input_window):
    accumulated_input += chr(ch)
    input_window.add_char(ch)


async def get_accumulated_input(server_socket, input_window, received_window, num_rows, num_cols):
    accumulated_input = StringBuilder()
    while True:
        ch = input_window.get_input()
        if ch != curses.ERR:
            if ch == ord('\n'):
                handle_enter(server_socket, accumulated_input, input_window)
            elif ch == 127:
                handle_backspace(accumulated_input, input_window)
            elif ch == 27:
                handle_scroll(input_window, received_window)
            else:
                handle_normal_ch(ch, accumulated_input, input_window)
                
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

          
async def main(s):
    stdscr = setup_curses()

    num_rows, num_cols = stdscr.getmaxyx()
    received_messages_rows = int(.85 * num_rows)
    sending_message_rows = num_rows - received_messages_rows
    
    # might want to put these numbers into constants up top or somewhere so that it's easy to change and makes some goddamn sense
    received_window = ReceivedWindow(received_messages_rows, num_cols, 0, 1)
    input_window = InputWindow(sending_message_rows,num_cols,received_messages_rows,0,1,1)
    
    get_input = asyncio.ensure_future(get_accumulated_input(s, input_window, received_window, num_cols, received_messages_rows))
    get_output = asyncio.ensure_future(get_messages(s, received_window))
    await get_output
    await get_input

def setup_curses():
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, -1, -1)
    curses.init_pair(2, curses.COLOR_BLUE, -1)
    curses.init_pair(3, curses.COLOR_GREEN, -1)
    curses.init_pair(4, curses.COLOR_YELLOW, -1)
    return stdscr


def cleanup_curses():
    curses.nocbreak()
    curses.echo()
    curses.endwin()

def handshake(server_socket):
    global ADDRESS
    ip_and_port = json.loads(server_socket.recv(1024).decode())
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
1. mitch wants a string builder class....
2. break paint_message into smaller peices (maybe)
3. handle json parsing outside of received (maybe something that is called in get_messages)
4. add constants for the math stuff
5. break things up into multiple files, e.g. key handlers, the different classes

ERROR_LIST:
1. log file getting polluted with information that seems irrelevant? Something about not receiving messages and not blocking
"""
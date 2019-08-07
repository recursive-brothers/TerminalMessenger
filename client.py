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
scroll = 0

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


def init_input_window(rows,cols,startY,startX):
    input_window = curses.newwin(rows,cols,startY,startX)
    input_window.border('|', '|', '-', '-', '+', '+', '+', '+')
    input_window.refresh()
    return input_window
    
    


def init_received_window(rows,cols,startY,startX):
    received_window = curses.newpad(rows,cols)
    received_window.scrollok(True)
    received_window.idlok(True)
    received_window.refresh(0,0,0,0,rows,cols)
    return received_window

class CursorPosition:
    def __init__(self,startY,startX):
        self.y = startY
        self.x = startX

class ReceivedWindow:
    def __init__(self, startY, startX):
        pass

def paint_message(received_window, received_window_cursor, num_cols, num_rows, built_str):
    global scroll
    message_height = int(2 + len(built_str)/(num_cols-2))
    lines_to_scroll = (message_height + received_window_cursor.y-scroll) - num_rows
    logging.debug(lines_to_scroll)

    if lines_to_scroll > 0:
        scroll += lines_to_scroll
        logging.debug(scroll)
        logging.debug(num_rows+scroll)
        received_window.resize(num_rows + scroll, num_cols)
        
        
        
    curr_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    received_window.addstr(received_window_cursor.y, received_window_cursor.x, f'> {curr_time}')
    received_window_cursor.y += 1

    str_to_paint = "".join(built_str)
    built_str.clear()
    while True:
        received_window.addstr(received_window_cursor.y, received_window_cursor.x, str_to_paint[:num_cols-2])
        received_window_cursor.y += 1
        if len(str_to_paint) > num_cols - 2:
            str_to_paint = str_to_paint[num_cols-2:]
        else:
            break
    
    received_window.refresh(scroll,0,0,0,num_rows,num_cols)
    
        
def send_message(input_window, received_window, input_window_cursor, received_window_cursor, num_cols, num_rows, built_str):
    input_window.erase()
    input_window.border('|', '|', '-', '-', '+', '+', '+', '+')
    input_window.refresh()
    input_window_cursor.x = input_window_cursor.y = 1
    paint_message(received_window, received_window_cursor, num_cols, num_rows, built_str)


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

def received_window_scroll(input_window,received_window,num_rows,num_cols):
    global scroll
    input_window.getch()
    ch = input_window.getch()
    if ch == 65:
        scroll -= 1 
    elif ch == 66:
        scroll += 1

    received_window.refresh(scroll,0,0,0,num_rows,num_cols)


def input_loop(input_window,received_window,num_cols, num_rows):
    global scroll
    built_str = []
    input_window_cursor = CursorPosition(1,1)
    received_window_cursor = CursorPosition(0,1)

    while True:
        ch = input_window.getch(input_window_cursor.y, input_window_cursor.x)

        if ch != curses.ERR:
            if ch == ord('\n'):
                send_message(input_window, received_window, input_window_cursor, received_window_cursor, num_cols, num_rows, built_str) if built_str else None
            elif ch == 127:
                backspace(input_window, input_window_cursor, built_str, num_cols)
            elif ch == 27:
                received_window_scroll(input_window,received_window,num_rows,num_cols) 
            else:
                build_message(input_window, input_window_cursor, built_str, num_cols, ch)
    

def main(stdscr):
    num_rows, num_cols = stdscr.getmaxyx()
    
    received_messages_rows = int(.85 * num_rows)
    sending_message_rows = num_rows - received_messages_rows

    received_window = init_received_window(received_messages_rows,num_cols,0,0)
    input_window = init_input_window(sending_message_rows,num_cols,received_messages_rows,0)

    input_window.nodelay(True)
    received_window.nodelay(True)


    input_loop(input_window,received_window,num_cols, received_messages_rows)

     


curses.wrapper(main)

"""
To keep in mind:
1. the 'keep track of total offset with scroll' functionality is the most gay thing ever created
2. Ideally, we encapsulate some of this scroll and redraw functionality in methods and encapsulate that in the class

Create a class for received window/pad, then do the same for input window, then, if there's enough similarity to justify it (and only if), then we can abstract that into another parent class
    If and ONLY IF (big Schnyder letters) we get to call it pee
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

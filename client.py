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
    



def draw_input_window(rows,cols,startY,startX):
    input_window = curses.newwin(rows,cols,startY,startX)
    input_window.border('|', '|', '-', '-', '+', '+', '+', '+')
    input_window.refresh()
    return input_window
    
    


def draw_received_window(rows,cols,startY,startX):
    received_window = curses.newwin(rows,cols,startY,startX)
    received_window.border('|', '|', '-', '-', '+', '+', '+', '+')
    received_window.refresh()
    return received_window

class CursorPosition:
    def __init__(self,startY,startX):
        self.y = startY
        self.x = startX
        
def send_message(input_window, received_window, input_window_cursor, received_window_cursor, num_cols, built_str):
    input_window.erase()
    input_window.border('|', '|', '-', '-', '+', '+', '+', '+')
    input_window.refresh()

    
    received_window.addstr(received_window_cursor.y, 1, "".join(built_str))
    received_window_cursor.y += int(1 + (len(built_str) / num_cols))
    received_window.refresh()
    input_window_cursor.x = input_window_cursor.y = 1
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



def input_loop(input_window,received_window,num_cols):
    built_str = []
    input_window_cursor = CursorPosition(1,1)
    received_window_cursor = CursorPosition(1,1)


    while True:
        ch = input_window.getch(input_window_cursor.y, input_window_cursor.x)

        if ch != curses.ERR:
            if ch == ord('\n'):
                send_message(input_window, received_window, input_window_cursor, received_window_cursor, num_cols, built_str)
            elif ch == 127:
                backspace(input_window, input_window_cursor, built_str, num_cols)
            else:
                build_message(input_window, input_window_cursor, built_str, num_cols, ch)

def main(stdscr):
    # curses.echo()
    num_rows, num_cols = stdscr.getmaxyx()
    
    received_messages_rows = int(.85 * num_rows)
    sending_message_rows = num_rows - received_messages_rows

    received_window = draw_received_window(received_messages_rows,num_cols,0,0)
    input_window = draw_input_window(sending_message_rows,num_cols,received_messages_rows,0)

    input_window.nodelay(True)
    received_window.nodelay(True)

    input_loop(input_window,received_window,num_cols)

     


curses.wrapper(main)

"""
TODO before moving to actual client

recieved window should put new messages on new line with some basic formatting

wrap long text in received window

scroll messages when they fill page

after moving to client:

set a fixed number of lines for input and resize as necessary

Formatting received window:
we have to keep track of received cursor pos. 


"""
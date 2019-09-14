import curses
import asyncio
import socket
import datetime
from .input_window import InputWindow
from .received_window import ReceivedWindow
from .utils import SCROLL, SCROLL_UP, SCROLL_DOWN, BACKSPACE, ENTER, SLEEP_TIME, StringBuilder, serialize_message

def handle_enter(server_socket: socket.socket, accumulated_input: StringBuilder, input_window: InputWindow) -> None:
    if accumulated_input:
        time = datetime.datetime.now()
        input_window.clear_text()
        server_socket.sendall(serialize_message(message=accumulated_input.build(), time=str(time)).encode())

def handle_backspace(accumulated_input: StringBuilder, input_window: InputWindow):
    accumulated_input.delete(1)
    input_window.backspace()

def handle_scroll(input_window: InputWindow, received_window: ReceivedWindow) -> None:
    input_window.get_input()
    scroll_direction = input_window.get_input()
    if scroll_direction == SCROLL_UP:
        received_window.scroll(-1)
    elif scroll_direction == SCROLL_DOWN:
        received_window.scroll(1)

# this name is bad
def handle_normal_ch(char_code: int, accumulated_input: StringBuilder, input_window: InputWindow) -> None:
    ch = chr(char_code)
    accumulated_input += ch
    input_window.add_str(ch)

async def get_user_input(server_socket: socket.socket, input_window: InputWindow, received_window: ReceivedWindow) -> None:
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

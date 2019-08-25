import curses
import asyncio
from .utils import SCROLL, SCROLL_UP, SCROLL_DOWN, BACKSPACE, ENTER, SLEEP_TIME, StringBuilder

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
import curses
from .utils import CursorPosition

class InputWindow:
    # curses window constructor takes 4 arguments:
    # - num_rows: height of window
    # - num_cols: width of window
    # - begin_y: y-coordinate of where top-left corner of window will be drawn on screen
    # - begin_x: x-coordinate of where top-left corner of window will be drawn on screen
    # this constructor takes the above 4 arguments plus the starting y,x coordinate of the cursor
    def __init__(self, num_rows: int, num_cols: int, startY: int, startX: int, cursorY: int, cursorX: int):
        self.height = num_rows
        self.width = num_cols
        self.window = curses.newwin(num_rows, num_cols, startY, startX)
        self.cursor = CursorPosition(cursorY, cursorX)
        self.window.nodelay(True)
        self._add_border()
        self.window.refresh()
    
    def clear_text(self) -> None:
        self.window.erase()
        self._add_border()
        self.window.refresh()
        self.cursor.x = self.cursor.y = 1

    # the width calculation here is **very** different than in received_window. 
    # explanation:
    #   CONTEXT: START COUNTING WIDTH AT 0
    #   cursor.x is always pointing at the space after where the last character was added.
    #   this means that cursor.x should move down one line exactly when it is at the right border,
    #   which is at width - 1.
    #   because cursor.x automatically starts at 1 when we move to the next line, there is no reason
    #   to try and 'factor it out' in the logic. It just works.
    # in received window, we do the scroll and other calculations in one batch: we determine the 
    # number of lines to scroll based on the number of columns excluding the border, and we always
    # add the string starting from cursor.x = 1 and never factor cursor.x into the equation.
    def add_str(self, msg: str) -> None:
        width = self.width - 1

        while msg:
            if len(msg) + self.cursor.x >= width:
                self.window.addstr(self.cursor.y, self.cursor.x, msg[:width - self.cursor.x])
                self.cursor.y += 1
                self.cursor.x = 1
                msg = msg[width - self.cursor.x:]
            else:
                self.window.addstr(self.cursor.y, self.cursor.x, msg)
                self.cursor.x += len(msg)
                break

    def _add_border(self) -> None:
        self.window.border('|', '|', '-', '-', '+', '+', '+', '+')
    
    def get_input(self): # -> int
        return self.window.getch(self.cursor.y, self.cursor.x)
    
    def backspace(self) -> None:
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

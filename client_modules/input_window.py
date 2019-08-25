import curses
from .utils import CursorPosition

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
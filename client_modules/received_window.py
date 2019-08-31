import curses
from .utils import CursorPosition

class ReceivedWindow:
    # the pad constructor only takes height and width
    # this constructor also provides initial cursor position
    def __init__(self, num_rows, num_cols, cursorY, cursorX):
        self.cursor = CursorPosition(cursorY, cursorX)
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
        # The refresh method on pads takes the following arguments:
        # - pminrow: the y-coordinate for the top-left corner of the contents in the pad to be displayed
        # - pmincol: the x-coordinate for the top-left corner of the contents in the pad to be displayed
        # - sminrow: the top row of the screen where the drawing begins
        # - smincol: the left-hand column of the screen where the drawing begins
        # - smaxrow: the bottom row of the screen where the drawing ends
        # - smaxcol: the right-hand column of the screen where the drawing ends
        # We subtract 1 from height and width for the same reason the last element of an array is at len - 1
        self.window.refresh(self.top_left.y, self.top_left.x, 0, 0, self.display_height - 1, self.display_width - 1) # refresh display_height -1 to avoid overlap

    def scroll(self, lines):
        # if scrolling up and there is still space to scroll OR scrolling down and there is still space to scroll
        if (lines < 0 and self.top_left.y > 0) or \
           (lines > 0 and self.top_left.y + self.display_height < self.height):
           # this works assuming we do one line at a time--problems if we don't
            self.top_left.y = self.top_left.y + lines
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
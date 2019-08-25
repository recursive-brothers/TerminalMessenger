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
from enum import Enum

ADDRESS = None

BUFFER_SIZE = 1024
SLEEP_TIME  = .001

ENTER       = 10
BACKSPACE   = 127
SCROLL      = 27
SCROLL_UP   = 65
SCROLL_DOWN = 66

RECEIVED_WINDOW_RATIO = .85

class SENDER(Enum):
    SELF     = 1
    TERMINAL = 2
    OTHER    = 3

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
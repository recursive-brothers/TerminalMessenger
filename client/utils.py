HOST    = '18.222.230.158'  # The server's hostname or IP address
PORT    = int(args.port) # The port used by the server
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
import json
import datetime
from enum import Enum
from typing import Any, List

ADDRESS: List[Any] = []

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
    def __init__(self, string: str = None):
        self.ch_list = list(string) if string else []
        
    def _append(self, seq: str) -> None:
        self.ch_list.extend(list(seq))
    
    def delete(self, num: int) -> None:
        if num <= 0:
            return
        self.ch_list = self.ch_list[:num * -1]

    def build(self) -> str:
        built_str = ''.join(self.ch_list)
        self.ch_list.clear()
        return built_str

    def __iadd__(self, seq: str) -> 'StringBuilder':
        self._append(seq)
        return self
        
    def __bool__(self) -> bool:
        return bool(self.ch_list)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, StringBuilder) and other.ch_list == self.ch_list

class CursorPosition:
    def __init__(self, startY: int, startX: int):
        self.y = startY
        self.x = startX

class Message:
    def __init__(self, msg: str, time: datetime.datetime, name: str = "", addr: str = ""):
        self.msg  = msg
        self.name = name
        self.time = time
        self.addr = addr

    def to_json(self) -> str:
        time_str = self.time.strftime("%Y-%m-%d %H:%M:%S.%f")
        return Message.serialize_json(message=self.msg, name=self.name, time=time_str, addr=self.addr)

    def generate_cql(self):
        pass

    @staticmethod
    def from_json(json_msg: str) -> Message:
        message = json.loads(json_msg)
        time = datetime.datetime.strptime(message["time"], '%Y-%m-%d %H:%M:%S.%f') 
        return Message(message["message"], time, message["name"], message.get("address", ""))

    @staticmethod
    def serialize_json(**kwargs: Any) -> str:
        return json.dumps(kwargs)
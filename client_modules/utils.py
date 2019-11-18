import json
import datetime
from uuid import uuid1
from enum import Enum
from typing import Any, List, Union, Tuple
from tzlocal import get_localzone

TIMEZONE: Any = get_localzone()

USERNAME: str = ""

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
    def __init__(self, msg: str, time: Any  = '', display_name: str = "", user: str = ""):
        self.msg  = msg
        self.display_name = display_name
        self.time = time
        self.user = user

    def to_json(self) -> str:
        time_str = self.fmt_time
        return Message.serialize_json(contents=self.msg, display_name=self.display_name, messaged_at=time_str, user=self.user)

    @property
    def fmt_time(self):
        return self.time.strftime("%Y-%m-%d %H:%M:%S.%f") if self.time else ''

    @classmethod
    def from_dict(cls, message):
        time = datetime.datetime.strptime(message["messaged_at"], '%Y-%m-%d %H:%M:%S.%f') if message['messaged_at'] else '' 
        return cls(message["contents"], time, message["display_name"], message.get("user", ""))

    @classmethod
    def from_json(cls, json_msg: str) -> 'Message':
        return cls.from_dict(json.loads(json_msg))

    @staticmethod
    def serialize_json(**kwargs: Any) -> str:
        return json.dumps(kwargs)

import datetime
import asyncio
import logging
import json
import re
import socket
from . import utils
from .utils import SENDER, SLEEP_TIME, BUFFER_SIZE, Message
from .received_window import ReceivedWindow
from typing import List, Union



def determine_sender(user: str) -> int:
    sender = None
    if user == utils.USERNAME:
        sender = SENDER.SELF
    elif user == "Terminal Messenger":
        sender = SENDER.TERMINAL
    else: 
        sender = SENDER.OTHER
    return sender.value

def format_metadata(name: str, time: datetime.datetime) -> str:
    curr_time = time.replace(tzinfo=datetime.timezone.utc).astimezone(utils.TIMEZONE).strftime("%Y-%m-%d %H:%M")
    return f'{name}     {curr_time}'

async def receive_server_messages(server_socket: socket.socket, received_window: ReceivedWindow) -> None:
    while True:
        raw_messages = None
        try:
            raw_messages = server_socket.recv(BUFFER_SIZE).decode()
            logging.debug(raw_messages)
        except:
            pass
        if raw_messages:
            json_messages  = re.findall(r'{.*?}', raw_messages)

            for json_msg in json_messages:
                received_message = Message.from_json(json_msg)
                message   = received_message.msg
                color_num = determine_sender(received_message.user)
                metadata  = format_metadata(received_message.name, received_message.time)
                received_window.paint_message(metadata, message, color_num)

        await asyncio.sleep(SLEEP_TIME)

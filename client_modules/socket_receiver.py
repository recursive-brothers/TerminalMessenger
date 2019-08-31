import datetime
import asyncio
import logging
import json
import re
from . import utils
from .utils import SENDER, SLEEP_TIME, BUFFER_SIZE

def determine_sender(addr):
    sender = None
    if addr == utils.ADDRESS:
        sender = SENDER.SELF
    elif addr == 0:
        sender = SENDER.TERMINAL
    else: 
        sender = SENDER.OTHER
    return sender.value

def format_metadata(name):
    curr_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    return f'{name}     {curr_time}'

async def receive_server_messages(server_socket, received_window):
    while True:
        raw_messages = None
        try:
            raw_messages = server_socket.recv(BUFFER_SIZE).decode()
            logging.debug(raw_messages)
        except:
            pass
        if raw_messages:
            message_format = r'{.*?}'
            json_messages  = re.findall(message_format, raw_messages)

            for json_msg in json_messages:
                received_message = json.loads(json_msg)
                message   = received_message["message"]
                color_num = determine_sender(received_message["address"])
                metadata  = format_metadata(received_message["name"])
                received_window.paint_message(metadata, message, color_num)

        await asyncio.sleep(SLEEP_TIME)
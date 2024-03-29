#!/usr/bin/python3

import os
import sys

BASE_DIR = os.path.dirname(__file__)
sys.path.append(BASE_DIR)

import selectors
import socket
import types
import argparse
import datetime
import traceback
import logging
import datetime
import json
import re
import uuid
from database_clients.dynamo_client import DynamoClient
from client_modules.utils import Message
from typing import Any, List, Tuple, Dict


HOST = "0.0.0.0"
SERVER_NAME = "Terminal Messenger"

CHATROOM_ID = 'c7532c20-e301-11e9-aaef-0800200c9a66'

db_client: DynamoClient = DynamoClient()

parser = argparse.ArgumentParser()
parser.add_argument('port')
args = parser.parse_args()

logger = logging.getLogger('tm_server_logger')
logging.basicConfig(filemode='a', datefmt='%H:%M:%S', format='%(asctime)s::%(funcName)s::%(lineno)d::%(message)s',level = logging.NOTSET)

critical_handler = logging.FileHandler('critical.log')
error_handler = logging.FileHandler('error.log')
warning_handler = logging.FileHandler('warning.log')
info_handler = logging.FileHandler('info.log')
debug_handler = logging.FileHandler('debug.log')

critical_handler.setLevel(logging.CRITICAL)
error_handler.setLevel(logging.ERROR)
warning_handler.setLevel(logging.WARNING)
info_handler.setLevel(logging.INFO)
debug_handler.setLevel(logging.DEBUG)

logger.addHandler(critical_handler)
logger.addHandler(error_handler)
logger.addHandler(warning_handler)
logger.addHandler(info_handler)
logger.addHandler(debug_handler)

list_of_sockets: List[socket.socket] = []
client_manager = selectors.DefaultSelector()

logging.getLogger('boto3').setLevel(1000)
logging.getLogger('botocore').setLevel(1000)
logging.getLogger('nose').setLevel(1000)

class ClientInformation:
    def __init__(self, addr: str):
        self.addr = addr
        self.handshake_complete = False
        self.name = None

def initialize_master_socket(port: int) -> None:
    master_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    master_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    master_socket.bind((HOST, port))
    master_socket.listen()
    master_socket.setblocking(False)
    client_manager.register(master_socket, selectors.EVENT_READ, data=None)
    logger.log(logging.DEBUG, "master socket initialized")

def setup() -> None:
    port = int(args.port)
    db_client.connect()
    initialize_master_socket(port)
    logger.log(logging.INFO, f'listening on {(HOST, port)}')

def accept_new_client(master_socket) -> None:
    client_socket, addr = master_socket.accept()
    client_socket.setblocking(False)
    client_manager.register(client_socket, selectors.EVENT_READ | selectors.EVENT_WRITE, data = ClientInformation(addr))
    list_of_sockets.append(client_socket)
    logger.log(logging.INFO, f'accepted client {addr}')

def close_client_connection(socket_wrapper) -> None:
    closed_client_name = socket_wrapper.data.name
    client_socket = socket_wrapper.fileobj
    client_manager.unregister(client_socket)
    client_socket.close()
    list_of_sockets.remove(client_socket)
    msg = Message(f'{closed_client_name} has left the chat!', datetime.datetime.utcnow(), SERVER_NAME, SERVER_NAME)
    route_message(msg)
    logger.log(logging.INFO, 'closed client connection {socket_wrapper.data.addr}')

def send_to_all(recv_data: bytes) -> None:
    for socket in list_of_sockets:
        logger.log(logging.DEBUG, f'sending message to {socket.getpeername()}')
        socket.send(recv_data)

def os_error_logging(socket_wrapper) -> None:
    logger.log(logging.WARNING, f'OSERROR OCCURRED: BEGIN LOGGING')
    logger.log(logging.WARNING, f'address is {socket_wrapper.data.addr}')
    logger.log(logging.WARNING,f'count of clients {len(list_of_sockets)}')
    logger.log(logging.WARNING, str(traceback.format_exc()))
    logger.log(logging.WARNING, "OSERROR OCCURRED: ENDING LOGGING")

def load_messages(socket_wrapper) -> None:
    results = db_client.get_chatroom_msgs(CHATROOM_ID, 50)
    results.reverse()
    json_messages = json.dumps(results)
    socket_wrapper.fileobj.send(json_messages.encode())
    logger.log(logging.DEBUG, f"loading message history for {socket_wrapper.data.addr}")

def route_message(msg: Message):
    db_client.insert_msg(msg, CHATROOM_ID)
    logger.log(logging.DEBUG, f'message {msg} inserted into database')
    send_to_all(msg.to_json().encode())

def handle_client(socket_wrapper, events: int) -> None:
    recv_data = None 
    client_socket = socket_wrapper.fileobj
    if events & selectors.EVENT_READ:
        try:
            recv_data = client_socket.recv(1024)
        except ConnectionResetError: # this is the connection reset by peer error.
            recv_data = None
            os_error_logging(socket_wrapper)
        except TimeoutError:
            recv_data = None
            logger.log(logging.ERROR, f"time out error, disconnecting: {socket_wrapper.data.addr}")

        if not recv_data:
            close_client_connection(socket_wrapper)
            return
        elif not socket_wrapper.data.handshake_complete:
            name = recv_data.decode()
            socket_wrapper.data.name = name
            socket_wrapper.data.handshake_complete = True
            load_messages(socket_wrapper)
            msg = Message(f'{name} has joined the chat!', datetime.datetime.utcnow(), SERVER_NAME, SERVER_NAME)
            route_message(msg)
            logger.log(logging.DEBUG, f"handshake completed for {socket_wrapper.data.addr}")
        else:
            raw_messages = recv_data.decode()
            logger.log(logging.DEBUG, f"sending message {raw_messages} from {socket_wrapper.data.addr}")

            json_messages = re.findall(r'{.*?"contents": ".*?[^\\]".*?}', raw_messages)
            logger.log(logging.DEBUG, f"matched message {json_messages}")
            for json_msg in json_messages:
                msg = Message.from_json(json_msg)
                msg.time = datetime.datetime.utcnow()
                logger.log(logging.INFO, f'sending message {msg} from {socket_wrapper.data.addr}')
                route_message(msg)

def event_loop() -> None:
    while True:
        ready_sockets = client_manager.select()
        for socket_wrapper, events in ready_sockets:
            if socket_wrapper.data is None:
                accept_new_client(socket_wrapper.fileobj)
            else:
                handle_client(socket_wrapper, events)


logger.log(logging.INFO, '----------------------STARTING SESSION----------------------')
try:
    setup()
    event_loop()
except Exception as e:
    logger.log(logging.CRITICAL, traceback.format_exc())

logger.log(logging.INFO, '----------------------ENDING SESSION-------------------------')

"""
ERROR LIST:
Errors we blindly handle:
1. connection reset by peer 

Broken:
2. non utf-8 characters being sent (not handled, can handle this easily by catching it)
3. Port is already occupied when we try to start server (prev process on port not killed?)
4. Really weird situation where we get an additional left the chat message long after the first left the chat message for the same leave event(?)
Relevant logs:
DEBUG:root:closing connection ('50.236.133.186', 58537) 2019-08-30 17:12:12.738614
DEBUG:root:client sent -> {"address": 0, "name": "Terminal Messenger", "message": "Mitch has left the chat!"} 2019-08-30 17:12:12.738865
DEBUG:root:accepted client ('50.236.133.186', 56246) 2019-08-30 17:12:24.880810
DEBUG:root:client sent -> {"address": 0, "name": "Terminal Messenger", "message": "MUD has joined the chat!"} 2019-08-30 17:12:24.921247
DEBUG:root:client sent -> {"address": ["50.236.133.186", 56246], "name": "MUD", "message": "yo"} 2019-08-30 17:12:28.399335
DEBUG:root:time out error, disconnecting:  ('50.236.133.186', 55474) 2019-08-30 17:28:22.762359
DEBUG:root:closing connection ('50.236.133.186', 55474) 2019-08-30 17:28:22.762534
DEBUG:root:client sent -> {"address": 0, "name": "Terminal Messenger", "message": "Mitch has left the chat!"} 2019-08-30 17:28:22.762652
"""

"""
Bug: people communicating between time zones get weird times for each other's messages, not ones
consistent with their time zone.
Solution: store milliseconds ('unix time') in mongo and convert to timezone on client
"""

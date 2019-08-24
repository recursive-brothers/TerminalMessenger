#!/usr/bin/python3

import selectors
import socket
import types
import argparse
import datetime
import traceback
import logging
import datetime
import json

HOST = '0.0.0.0' 
SERVER_NAME = "Terminal Messenger"

parser = argparse.ArgumentParser()
parser.add_argument('port')
args = parser.parse_args()

logging.basicConfig(filename='server.log',
                            filemode='a',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)

list_of_sockets = []
client_manager = selectors.DefaultSelector()


class ClientInformation:
	def __init__(self, addr):
		self.addr = addr
		self.handshake_complete = False
		self.name = None


def log_debug_info(*args):
	str_args = [str(arg) for arg in args]
	str_args.append(str(datetime.datetime.now()))
	logging.debug(' '.join(str_args))

def serialize_message(**kwargs):
	return json.dumps(kwargs)

def initialize_master_socket(port):
	master_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	master_socket.bind((HOST, port))
	master_socket.listen()
	master_socket.setblocking(False)
	client_manager.register(master_socket, selectors.EVENT_READ, data=None)

def setup():
	port = int(args.port)
	initialize_master_socket(port)
	log_debug_info('listening on', (HOST, port))

def accept_new_client(master_socket):
	client_socket, addr = master_socket.accept()
	client_socket.setblocking(False)
	client_socket.send(serialize_message(address=addr[0],port=addr[1]).encode())
	client_manager.register(client_socket, selectors.EVENT_READ | selectors.EVENT_WRITE, data = ClientInformation(addr))
	list_of_sockets.append(client_socket)
	log_debug_info('accepted client', addr)

def close_client_connection(socket_wrapper):
	log_debug_info('closing connection', socket_wrapper.data.addr)
	closed_client_name = socket_wrapper.data.name
	client_socket = socket_wrapper.fileobj
	client_manager.unregister(client_socket)
	client_socket.close()
	list_of_sockets.remove(client_socket)
	send_to_all(serialize_message(address=0, name=SERVER_NAME, message=f'{closed_client_name} has left the chat!').encode())

def send_to_all(recv_data):
	log_debug_info('client sent ->', recv_data.decode())
	for socket in list_of_sockets:
		socket.send(recv_data)

def os_error_logging(socket_wrapper):
	log_debug_info("OSERROR OCCURRED: BEGIN LOGGING")
	log_debug_info('address is', socket_wrapper.data.addr)
	log_debug_info('count of clients', len(list_of_sockets))
	log_debug_info(traceback.format_exc())
	log_debug_info("OSERROR OCCURRED: ENDING LOGGING")


def handle_client(socket_wrapper, events):
	recv_data = None 
	client_socket = socket_wrapper.fileobj
	if events & selectors.EVENT_READ:
		try:
			recv_data = client_socket.recv(1024)
		except ConnectionResetError:
			recv_data = None
			os_error_logging(socket_wrapper)

		if recv_data:
			if not socket_wrapper.data.handshake_complete:
				name = recv_data.decode()
				socket_wrapper.data.name = name
				socket_wrapper.data.handshake_complete = True

				send_to_all(serialize_message(address=0, name=SERVER_NAME, message=f'{name} has joined the chat!').encode())
			else:
				send_to_all(serialize_message(address=socket_wrapper.data.addr, name=socket_wrapper.data.name, message=recv_data.decode()).encode())
		else:
			close_client_connection(socket_wrapper)

def event_loop():
	while True:
		ready_sockets = client_manager.select()
		for socket_wrapper, events in ready_sockets:
			if socket_wrapper.data is None:
				accept_new_client(socket_wrapper.fileobj)
			else:
				handle_client(socket_wrapper, events)


log_debug_info('----------------------STARTING SESSION----------------------')
try:
	setup()
	event_loop()
except Exception as e:
	log_debug_info(traceback.format_exc())

log_debug_info('----------------------ENDING SESSION-------------------------')

"""
Figure out how to clean up handle_client

ERROR_LIST:
1. connection reset by peer when mitch's computer falls asleep (the server crashes), so this error isn't even handled
2. non utf-8 characters being sent (not handled, can handle this easily by catching it)
3. really really weird random unicorn error with json decodes error.
4. Port is already occupied when we try to start server (prev process on port not killed?)
"""
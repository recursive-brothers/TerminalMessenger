#!/usr/bin/python3

import selectors
import socket
import types
import argparse
import datetime
import traceback
import logging
import datetime

HOST = '0.0.0.0' 

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
		self.name_accepted = False
		self.name = None

def log_debug_info(*args):
	str_args = [str(arg) for arg in args]
	str_args.append(str(datetime.datetime.now()))
	logging.debug(' '.join(str_args))

def initialize_listening_socket(port):
	lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	lsock.bind((HOST, port))
	lsock.listen()
	lsock.setblocking(False)
	client_manager.register(lsock, selectors.EVENT_READ, data=None)

def setup():
	port = int(args.port)
	initialize_listening_socket(port)
	log_debug_info('listening on', (HOST, port))

# NEED TO RENAME MASTER SOCKET
def accept_new_client(master_socket):
	client_socket, addr = master_socket.accept()
	client_socket.setblocking(False)
	client_manager.register(client_socket, selectors.EVENT_READ | selectors.EVENT_WRITE, data = ClientInformation(addr))
	list_of_sockets.append(client_socket)
	log_debug_info('accepted client', addr)

def close_client_connection(client_socket, address):
	log_debug_info('closing connection', address)
	client_manager.unregister(client_socket)
	client_socket.close()
	list_of_sockets.remove(client_socket)

def send_to_all(recv_data):
	log_debug_info('client sent ->', recv_data.decode())
	for socket in list_of_sockets:
		socket.send(recv_data)

def handle_client(socket_wrapper, events):
	recv_data = None 
	client_socket = socket_wrapper.fileobj
	if events & selectors.EVENT_READ:
		try:
			recv_data = client_socket.recv(1024)
		except ConnectionResetError:
			recv_data = None
			log_debug_info("OSERROR OCCURRED: BEGIN LOGGING")
			log_debug_info('address is', socket_wrapper.data.addr)
			log_debug_info('count of clients', len(list_of_sockets))
			log_debug_info(traceback.format_exc())
			log_debug_info("OSERROR OCCURRED: ENDING LOGGING")
		if recv_data:
			if not socket_wrapper.data.name_accepted:
				socket_wrapper.data.name = recv_data
				send_to_all(f'{recv_data} has joined the chat!')
			else:
				send_to_all(recv_data)
		else:
			close_client_connection(client_socket, socket_wrapper.data.addr)

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
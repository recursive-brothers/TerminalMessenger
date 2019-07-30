#!/usr/bin/python3

import selectors
import socket
import types
import argparse
import datetime
import traceback
import logging
import datetime


logging.basicConfig(filename='server.log',
                            filemode='a',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)

parser = argparse.ArgumentParser()
parser.add_argument('port')
args = parser.parse_args()

# goal: get a server that connect with multiple clients and get it to send messages from one client to the others
sockets_container = selectors.DefaultSelector()
host = '0.0.0.0'
port = int(args.port)


lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((host, port))
lsock.listen()
logging.debug('listening on' + str((host, port)) + f' {str(datetime.datetime.now())}')
lsock.setblocking(False)
sockets_container.register(lsock, selectors.EVENT_READ, data=None)

list_of_sockets = []

def handle_client(client_socket, events):
	recv_data = None 
	socket_obj = client_socket.fileobj
	if events & selectors.EVENT_READ:
		recv_data = socket_obj.recv(1024)
		if not recv_data:
			logging.debug('closing connection ' + client_socket.data + f' {str(datetime.datetime.now())}')
			sockets_container.unregister(socket_obj)
			socket_obj.close()
			list_of_sockets.remove(socket_obj)
			return

		logging.debug("client sent -> " + recv_data.decode() + f' {str(datetime.datetime.now())}')
	
	if recv_data:
		for socket in list_of_sockets:
			if socket != socket_obj:
				logging.debug(f'sending to other clients {str(datetime.datetime.now())}')
				socket.send(recv_data)

def main():
	while True:
		ready_sockets = sockets_container.select()
		for socket_obj, events in ready_sockets:
			if socket_obj.data is None:
				client_socket, addr = socket_obj.fileobj.accept() 
				logging.debug('accepted client' + addr + f' {str(datetime.datetime.now())}') 
				client_socket.setblocking(False)
				sockets_container.register(client_socket, selectors.EVENT_READ | selectors.EVENT_WRITE, data = addr)
				list_of_sockets.append(client_socket)
			else:
				handle_client(socket_obj, events)


logging.debug(f'----------------------STARTING SESSION {str(datetime.datetime.now())}----------------------')
try:
	main()
except Exception as e:
	logging.debug(traceback.format_exc())

logging.debug(f'----------------------ENDING SESSION {str(datetime.datetime.now())}-------------------------')

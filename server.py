#!/usr/local/bin/python3

import selectors
import socket
import types
import argparse


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
print('listening on', (host, port))
lsock.setblocking(False)
sockets_container.register(lsock, selectors.EVENT_READ, data=None)

list_of_sockets = []





def handle_client(client_socket, events):
	recv_data = None 
	socket_obj = client_socket.fileobj
	if events & selectors.EVENT_READ:
		recv_data = socket_obj.recv(1024)
		if not recv_data:
			print('closing connection', client_socket.data)
			sockets_container.unregister(socket_obj)
			socket_obj.close()
			list_of_sockets.remove(socket_obj)
			return

		print("data just received")
		print("client sent -> ", recv_data)
	
	if recv_data:
		for socket in list_of_sockets:
			if socket != socket_obj:
				print("sending to other clients")
				socket.send(recv_data)

	

while True:
	ready_sockets = sockets_container.select()
	for socket_obj, events in ready_sockets:
		if socket_obj.data is None:
			client_socket, addr = socket_obj.fileobj.accept() 
			print('accepted client', addr) 
			client_socket.setblocking(False)
			sockets_container.register(client_socket, selectors.EVENT_READ | selectors.EVENT_WRITE, data = addr)
			list_of_sockets.append(client_socket)
		else:
			handle_client(socket_obj, events)


	





"""
1. send it to everybody except yourself
2. route to a specific IP address specified on the command line with an option
"""

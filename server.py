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
	if events & selectors.EVENT_READ:
		recv_data = client_socket.recv(1024)
		print("data just received")
		print("client sent -> ", recv_data)
		print(events & selectors.EVENT_WRITE)

	
	if recv_data:
		for socket in list_of_sockets:
			if socket != client_socket:
				print("sending to other clients")
				socket.send(recv_data)
	

while True:
	ready_sockets = sockets_container.select()
	for socket_obj, events in ready_sockets:
		if socket_obj.data is None:
			client_socket, addr = socket_obj.fileobj.accept() 
			print('accept09u8ham', addr) 
			client_socket.setblocking(False)
			sockets_container.register(client_socket, selectors.EVENT_READ | selectors.EVENT_WRITE, data = "Client socket")
			list_of_sockets.append(client_socket)
		else:
			handle_client(socket_obj.fileobj, events)


	





"""
1. send it to everybody except yourself
2. route to a specific IP address specified on the command line with an option



Current Problems:

1. when client terminates, server gets spammed with b''. Need to implement graceful termination.  
"""

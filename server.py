#!/usr/local/bin/python3

import selectors
import socket
import types


# goal: get a server that connect with multiple clients and get it to send messages from one client to the others
sockets_container = selectors.DefaultSelector()
host = '0.0.0.0'
port = 3333


lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((host, port))
lsock.listen()
print('listening on', (host, port))
lsock.setblocking(False)
sockets_container.register(lsock, selectors.EVENT_READ, data=None)

list_of_sockets = []

try:
	while True:
		ready_sockets = sockets_container.select()
		for socket_obj, events in ready_sockets:
			if socket_obj.data is None:
				conn, addr = socket_obj.fileobj.accept()  
				print('accepted connection from', addr)
				conn.setblocking(False)
				events = selectors.EVENT_READ | selectors.EVENT_WRITE
				sel.register(conn, events)
				"""
					client_socket, address = socket_obj.fileobj.accept()
					client_socket.setblocking(False)
					sockets_container.register(client_socket, selectors.EVENT_READ | selectors.EVENT_WRITE)
					list_of_sockets.append(client_socket)
				"""
			else:
				handle_client(socket_obj.fileobj, events)

except Exception as e:
	print(e) 
	for socket in list_of_sockets:
		socket.close()
	lsock.close()
	


def handle_client(socket_file, events):
	if events & select.EVENT_READ:
		recv_data = socket_file.recv(1024)

	if events & select.EVENT_WRITE:
		for socket in list_of_sockets:
			if socket != socket_file:
				socket.send(recv_data)




"""
1. send it to everybody except yourself
2. route to a specific IP address specified on the command line with an option
"""




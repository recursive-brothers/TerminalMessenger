import selectors
import socket
import types


sockets_container = selectors.DefaultSelector()
host = '0.0.0.0'
port = 3333


lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((host, port))
lsock.listen()
print('listening on', (host, port))
lsock.setblocking(False)
sockets_container.register(lsock, selectors.EVENT_READ, data=None)

def handle_client():
    pass

while True:
    ready_sockets = sockets_container.select()
    for socket_obj, events in ready_sockets:
        if not socket_obj.data:
            client_socket,address = socket_obj.accept()
            client_socket.setblocking(False)
            sockets_container.register(client_socket)
        else:
            handle_client()









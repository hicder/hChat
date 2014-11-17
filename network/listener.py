import socket, pickle, math, sys
sys.path.append('../model')
from message import Message

class Listener:
    def __init__(self, host, port):
        """
        Initialize the listener.
        Args:
            host: the host that listener listens on.
            port: the port that listener listens on.
        """
        self.host = host
        self.port = port

    def listening(self, receive): # takes in a function pointer
        """
        Listening on packet. Callback 'receive' function.
        Note that this function will NOT deserialize the message.
        Args:
            receive (function): callback function on the packet.
        """
        print 'trying to listen on', self.host, self.port
        try:
            # uses TCP
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except socket.error:
            print 'Failed to create socket'
            sys.exit()

        try:
            s.bind((self.host, self.port))
        except socket.error:
            print 'Bind failed.'
            print 'Please check your connection. It may be that the server is currently offline'
            sys.exit()

        # start listening with at most 20 requests queued
        s.listen(20)
        while True:
            conn, addr = s.accept()
            data = conn.recv(1024)
            receive(data)

        conn.close()
        s.close()

import socket, thread

class NetworkWorker:
    """
    Network worker that does the sending and receiving of message from server.
    Note that we do not check if the packet reaches the user. This should
    be taken care of by TCP/IP protocol.
    """
    def __init__(self, host, port, callback):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.connect((host, port))
        thread.start_new_thread(callback, (self.socket,))

    def talk(self, msg):
        self.socket.send(msg)
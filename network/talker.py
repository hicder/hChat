import socket, sys, thread
import pickle
sys.path.append('../model')
from message import Message

class Talker:
    """
    Network worker that does the sending of message.
    Note that we do not check if the packet reaches the user. This should
    be taken care of by TCP/IP protocol.
    """
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def talk(self, msg, host, port):
        """
        Send the message to destination.
        This will take care of serialization.
        Note that msg has to be in SERIALIZED format, and ready to send.
        Args:
            msg (Message): message that will be sent. MUST be serialized.
            host (string): address of destination.
            port (int): port of the destination.
        """
        try:
            # uses TCP
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except socket.error:
            print 'Failed to create socket.'
            sys.exit()
        try:
            s.connect((host,port))
        except socket.error:
            print 'Cannot connect to the destination.'
            # We do not quit the program here. There is a possibility that
            # the program can connect later.
            return

        try:
            # send to server
            sent = s.send(msg)
    
        except socket.error:
            #Send failed
            print 'Send failed'
        s.close()

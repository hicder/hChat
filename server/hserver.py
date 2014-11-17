import sys, pickle, threading, signal, thread, argparse, logging
sys.path.append('../network')
sys.path.append('../model')
from message import Message
from listener import Listener
from talker import Talker

class HServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.ln = Listener(host, port)
        self.tk = Talker(host, port)
        thread.start_new_thread(self.ln.listening, (self.recv_data,))
        self.client_list = {}

    def recv_data(self, data):
        """
        Callback function to receive from the server.
        Note that data is NOT deserialized yet.
        Args:
            socket (socket): the socket that is connected to the server.
        """
        self.process_packet(pickle.loads(data))

    def send_ack_message(self, msg):
        """
        Inform the client that the request succeeds.

        Args:
            msg (Message): the original message.
        """
        logging.info('Sending ACK')
        ack_msg = pickle.dumps(Message('', Message.ACK, id = msg.id))
        self.tk.talk(ack_msg, msg.origin[0], msg.origin[1])


    def send_fail_message(self, msg):
        """
        Inform the client that the request fails.

        Args:
            msg (Message): the original message.
        """
        fail_msg = pickle.dump(Message('', Message.FAIL, id = msg.id))
        self.tk.talk(fail_msg, msg.origin[0], msg.origin[1])


    def process_packet(self, data):
        """
        Process a packet after receiving.
        Args:
            data (Object): data that has been deserialized by pickle.
        """
        if data.type == Message.JOIN:
            # update user.
            username = data.msg
            if username not in self.client_list:
                self.client_list[username] = data.origin
                logging.info('User "%s" joined', username)
            else:
                logging.warning('User "%s" is already in the server.', username)
        elif data.type == Message.MESSAGE:
            # broadcast the message to all other users.
            print 'receive new message:"%s"'%data.msg
            print 'broadcasting...'
            logging.info('Receive message from (%s, %s) with id %s', data.origin[0]
                         , data.origin[1], data.id)
            data.type = Message.BROADCAST
            for username in self.client_list:
                self.tk.talk(pickle.dumps(data), self.client_list[username][0],
                             self.client_list[username][1])
        elif data.type == Message.LEAVE:
            username = data.msg
            logging.info('User "%s" is leaving.', username)
            if username not in self.client_list:
                return
            else:
                self.client_list.pop(username, None)
        elif data.type == Message.CHANGE_NAME:
            # We need to check that the new name is not used, and the old name
            # exists. If one of the condition fails, inform the sender.
            oldname, newname = data.msg.split(' ')[0], data.msg.split(' ')[1]
            print "user %s changes the name to %s" %(oldname, newname)
            logging.info('Change username from %s to %s', oldname, newname)
            if oldname not in self.client_list or newname in self.client_list:
                logging.warning('Change username from %s to %s unsuccessfully.'
                            , oldname, newname)
                self.send_fail_message(data)
            else:
                self.client_list[newname] = self.client_list.pop(oldname)
                self.send_ack_message(data)

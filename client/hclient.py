import sys, pickle, threading, signal, thread, argparse, re
sys.path.append('../network')
sys.path.append('../model')
from listener import Listener
from talker import Talker
from message import Message, MessageStatus
from client_parser import Parser
from sets import Set
from ircclient import IRCClient


class HClient:
    """
    HClient is another alternative to IRCClient. This only connects to HServer.
    The difference between this and IRCClient is that, for this, user will need
    to specify the listening port that this program will bind to.

    Example:
        c = HClient(host, port)
        c.connect_server(dhost, dport)
        c.set_username(user)
        
        while True:
            line = raw_input()
            c.on_typing(line)
    """
    def __init__(self, host, port, dhost = '', dport = 0):
        self.host = host
        self.port = port
        self.dhost = dhost
        self.dport = dport
        self.prev_cmd = ''
        self.user = ''
        self.msg_id = 0
        self.ack_status = {}
        self.irc_mode = False
        self.parser = Parser()
        self.tk = Talker(self.host, self.port)
        self.ln = Listener(self.host, self.port)
        thread.start_new_thread(self.ln.listening, (self.receive_packet,))
        if self.dhost and self.dport:
            self.connect_server(self.dhost, self.dport)

    def on_typing(self, line):
        """
        Process what user types.

        Args:
            line: input from user.
        """
        msg = self.parser.parse(line)
        if(msg.type == Message.COMMAND):
            self.dispatch_command(msg)
        elif msg.type == Message.MESSAGE:
            self.say(msg)

    def set_username(self, newname):
        """
        Set nickname
        """
        if not self.dhost or not self.dport:
            self.user = newname
        else:
            self.request_change_name(newname)

    def request_change_name(self, newname):
        """
        Request to change a new username. This method will BLOCK until it completes
        either successfully or unsuccessfully.

        Args:
            newname (string): new username.
        """
        msg = Message("%s %s"%(self.user, newname), Message.CHANGE_NAME,
                      origin = (self.host, self.port), 
                      destination = (self.dhost, self.dport))
        self.increment_msg_id(msg)
        self.ack_status[msg.id] = MessageStatus.PENDING
        self.tk.talk(pickle.dumps(msg), self.dhost, self.dport)
        while self.ack_status[msg.id] is MessageStatus.PENDING:
            pass
        if self.ack_status[msg.id] is MessageStatus.SUCCESS:
            self.ack_status.pop(msg.id)
            return True
        else:
            self.ack_status.pop(msg.id)
            return False

    def increment_msg_id(self, msg):
        """
        Give each message a unique message ID.
        Args:
            msg (Message): the message to assign ID for.
        """
        msg.id = self.msg_id
        self.msg_id += 1

    def connect_server(self, dest_host, dest_port):
        """
        Join a chat server.
        Args:
            dest_host (string): address of server.
            dest_port (int): port of server.
        """
        self.dhost = dest_host
        self.dport = dest_port
        if not self.user:
            self.user = 'anonymous'
        msg = Message(self.user, Message.JOIN, origin = (self.host, self.port), 
                    destination =(self.dhost, self.dport))
        self.tk.talk(pickle.dumps(msg), self.dhost, self.dport)

    def leave_server(self):
        """
        Leave a chat server. This function resets the dhost and dport.
        Args:
            talker (Talker): the network worker that executes the sending of packet.
        """
        msg = Message(self.user, Message.LEAVE, (self.host, self.port), 
                      (self.dhost, self.dport))
        self.tk.talk(pickle.dumps(msg), self.dhost, self.dport)
        self.dhost = ''
        self.dport = 0

    def say(self, msg):
        """
        Broadcast a message.
        Args:
            msg (Message): message to broadcast.
        """
        if not self.dhost or not self.dport:
            print 'You need to connect to a HServer.'

        msg.origin = (self.host, self.port)
        msg.destination = (self.dhost, self.dport)
        msg.author = self.user
        self.increment_msg_id(msg)
        self.tk.talk(pickle.dumps(msg), self.dhost, self.dport)

    def dispatch_command(self, msg):
        """
        Dispatch the command. Called when user type a command.
        Args:
            msg (Message): message that contains the command, after parsed.
        """
        if msg.cmd_args[0] == 'JOIN':
            dest_host = msg.cmd_args[1]
            dest_port = int(msg.cmd_args[2])
            self.connect_server(dest_host, dest_port)
        elif msg.cmd_args[0] == 'NICK':
            # this will block until username is changed, or unsuccessfully
            # reported by the server.
            if self.dhost and self.dport:
                status = self.request_change_name(msg.cmd_args[1])
            else:
                status = True
            if status is True:
                print '>>> change successfully'
                self.user = msg.cmd_args[1]
            else:
                print '>>> change of username unsuccessfully'
        elif msg.cmd_args[0] == 'LEAVE':
            self.leave_server()


    def process_packet(self, data):
        """
        Process a packet after receiving.
        Args:
            data (Object): data that has been deserialized by pickle.
        """
        if data.type is Message.BROADCAST:
            print "%s: %s" %(data.author, data.msg)
        elif data.type is Message.ACK:
            self.ack_status[data.id] = MessageStatus.SUCCESS
        elif data.type is Message.FAIL:
            self.ack_status[data.id] = MessageStatus.FAIL


    def receive_packet(self, data):
        """
        Callback function when listener receives a packet.
        Args:
            data (Object): data that has been deserialized by pickle.
        """
        
        self.process_packet(pickle.loads(data))
        
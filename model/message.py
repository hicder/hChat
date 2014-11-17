class Message:
    """
    Type of Message object:
        MESSAGE: normal message from the user.
        COMMAND: special message from the user, usually a join or leave.
        JOIN: a kind of command. this type is mostly used by the client to
            decide what to do with the message.
        BROADCAST: server broadcasts the message from one user to all others.
        LEAVE: a client wants to leave.
        CHANGE_NAME: a client request to change username.
        ACK: ack message.
        FAIL: fail message, informing the user that the request completes
            unsuccessfully.
    """
    MESSAGE = 0
    COMMAND = 1
    JOIN = 2
    BROADCAST = 3
    LEAVE = 4
    CHANGE_NAME = 5
    ACK = 6
    FAIL = 7
    def __init__(self, msg, type, origin = (), destination = (), cmd_args = [],
                 author = '', id = 0):
        """
        Message object. This object can represent a broadcast message 
        (from server), a normal message (from client), or a command.
        
        Format:
            msg (string): the message of this Message.
            type: one of the type declared in this class.
            destination: destination that this message is going to. Note that
                this only applies when the message just left the sender.
                When server relay this message and broadcasts other clients,
                this field may not change.
            cmd_args (list): if this message is a command message, this contains
                all the arguments.
            author (string): username of the sender. Also note that, when the
                server relays and broadcasts this message, the author field is
                untouched.
        """
        self.msg = msg
        self.type = type
        self.origin = origin
        self.destination = destination
        self.cmd_args = cmd_args
        self.author = author
        self.id = 0


class MessageStatus:
    """
    Message status used by client to keep track of their request.
    PENDING: the client has not received an ACK message yet.
    SUCCESS: the client receives an ACK message and the request completes.
    FAIL: the request has failed.
    """
    PENDING = 0
    SUCCESS = 1
    FAIL = 2

import sys
sys.path.append('../model')
from message import Message

class Parser:
    """
    Help parsing the input that user types on the console.
    """
    def parse(self, text):
        """
        Parse input that user types.

        Args:
            text (string): input from the user.

        Return:
            a Message object that represents either a request, or normal 
                message.
        """
        if text.startswith('/'):
            args = text[1:].split(' ')
            return Message('', Message.COMMAND, cmd_args=args)
        else:
            return Message(text, Message.MESSAGE)
import sys, pickle, threading, signal, thread, argparse, logging
sys.path.append('../network')
sys.path.append('../model')
from message import Message
from listener import Listener
from talker import Talker
from hserver import HServer

host = ''
port = 0
log_file = None


def set_up_logging():
    """
    Set up log support for the server.
    """
    global log_file
    logging.basicConfig(filename=log_file, level=logging.DEBUG,
                        format='%(asctime)s:%(levelname)s: %(message)s')

        
def parse_command_input(text):
    """
    Parse input and execute commands.
    Args:
        text (string): input by user.
    """
    args = text.split(' ')
    if args[0] == 'SHOWCLIENTS':
        print client_list


def main():
    """
    Main function for the server.
    Initialize the listener and talker.
    """
    s = HServer(host, port)
    while True:
        pass

def sig_handler(signal, frame):
    sys.exit(0)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, sig_handler)
    argparser = argparse.ArgumentParser(description='hChat server.')
    argparser.add_argument('-H','--host', dest = 'host', required = True, 
                           help='current host.')
    argparser.add_argument('-p','--port', dest = 'port', required = True, 
                           help='current port.')
    # argparser.add_argument('--log', dest = 'log', help='log file.')
    args = vars(argparser.parse_args())
    host = args['host']
    port = int(args['port'])
    # if 'log' in args:
    #     log_file = args['log']
    #     set_up_logging()
    main()

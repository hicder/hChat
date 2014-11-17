import sys, pickle, threading, signal, thread, argparse, re
sys.path.append('../network')
sys.path.append('../model')
from ircclient import IRCClient
from hclient import HClient

dhost = ''
dport = 0
host = ''
port = 0
irc_mode = False
user = ''

def clear_input_line():
    """
    A trick to clear what user typed in the console.
    """
    print "\033[A                             \033[A" 


def main():
    """
    main function.
    """
    global host, port, dhost, dport, user
    if not irc_mode:
        c = HClient(host, port)
    else:
        c = IRCClient()
    
    if dhost:
        c.connect_server(dhost, dport)

    if user:
        c.set_username(user)
    while True:
        line = raw_input()
        clear_input_line()
        c.on_typing(line)


def sig_handler(signal, frame):
    """
    Signal handler for SIGINT
    """
    print ''
    sys.exit(0)


def get_arg_parser():
    """
    Prepare an argument parser (argparse).
    """
    argparser = argparse.ArgumentParser(description='hChat client.')
    argparser.add_argument('-H','--host', dest = 'host', required = False, 
                           help='current host.')
    argparser.add_argument('-p','--port', dest = 'port', required = False, 
                           help='current port.', type = int)
    argparser.add_argument('--dhost', dest = 'dhost', help='server host')
    argparser.add_argument('--dport', dest = 'dport', help='server port')
    argparser.add_argument('-u', '--user', dest = 'username', help = 'username')
    argparser.add_argument('--irc', dest = 'irc', action='store_true')
    argparser.add_argument('--noirc', dest = 'irc', action='store_false')
    return argparser


def update_vars(args):
    """
    Update arguments into variables.
    """
    global host, port, dhost, dport, user, irc_mode
    if 'irc' in args:
        irc_mode = args['irc']
    else:
        irc_mode = False

    if not irc_mode and 'host' not in args:
        print '--host is required'
        sys.exit(1)

    if 'host' in args and args['host'] != None:
        host = args['host']

    if 'port' in args and args['port'] != None:
        port = int(args['port'])
    else:
        port = 6667
    if 'dhost' in args:
        dhost = args['dhost']

    if 'dport' in args and args['dport']:
        dport = int(args['dport'])
    elif irc_mode:
        dport = 6667

    if 'username' in args:
        user = args['username']
    ack_status = {}


if __name__ == '__main__':
    # prepare argument parser
    signal.signal(signal.SIGINT, sig_handler)
    argparser = get_arg_parser()
    # parse arguments
    args = vars(argparser.parse_args())
    update_vars(args)
    main()

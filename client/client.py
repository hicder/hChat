from tkinter import *
from tkinter import ttk
import sys, pickle, threading, signal, argparse, re
sys.path.append('../network')
sys.path.append('../model')
from ircclient import IRCClient
#from hclient import HClient

dhost = ''
dport = 0
host = ''
port = 0
irc_mode = False
user = ''

class ClientApp:
    def __init__(self, master, args):
        self.master = master
        master.title('Welcome to hChat')
        master.resizable(False, False)
        self.frame_header = ttk.Frame(master)
        self.frame_header.pack()
        self.frame_convo = ttk.Frame(master)
        self.frame_convo.pack()
        self.frame_input = ttk.Frame(master)        
        self.frame_input.pack()

        self.input_box = ttk.Entry(self.frame_input, width = 100, font =('Arial', 10))
        self.input_box.bind('<Return>', lambda e: self.process_input())
        self.master.bind_all('<Tab>', lambda e: self.autocomplete())
        self.input_box.bind('<Up>', lambda e: self.UpHistory())
        self.input_box.bind('<Down>', lambda e: self.DownHistory())
        self.input_box.pack()

        self.convo_box = Text(self.frame_convo, width = 100, font = ('Arial', 10))
        self.convo_box.config(wrap = 'word', state = DISABLED)
        self.convo_box.pack()
        self.setup_args(args)
        self.client = self.setup_client()
        self.command_list = sorted(['JOIN', 'NICK', 'PART', 'QUIT', 'LIST', 'WHOIS',
                                    'TIME', 'MOTD', 'INFO'])
        self.history = []
        self.history_point = 0
        self.current_typing = ''

    def run(self):
        self.master.mainloop()

    def send_to_client(self, line):
        self.convo_box.config(state = NORMAL)
        self.convo_box.insert('end', line)
        self.convo_box.insert('end', '\n')
        self.convo_box.config(state = DISABLED)

    def setup_client(self):
        c = IRCClient(text_callback = self.send_to_client)
        if self.dhost:
            c.connect_server(self.dhost, self.dport)
        if self.user:
            c.set_username(self.user)
        return c

    def setup_args(self, args):
        self.irc_mode = True
        if 'dhost' in args:
            self.dhost = args['dhost']

        if 'dport' in args and args['dport']:
            self.dport = int(args['dport'])
        elif self.irc_mode:
            self.dport = 6667

        if 'username' in args:
            self.user = args['username']

    def process_input(self):
        line = self.input_box.get()
        self.client.on_typing(line)
        self.insert_into_history(line)
        self.input_box.delete(0, 'end')

    def autocomplete(self):
        if not self.input_box.get():
            return
        if self.input_box.get()[0] != '/':
            return
        inp = self.input_box.get()[1:].upper()
        cmd = self.autocomplete_helper(inp, 0, 0, len(self.command_list) -1)
        if cmd:
            self.input_box.delete(0, 'end')
            self.input_box.insert(0, '/%s' % cmd)

    def autocomplete_helper(self, line, pos, start_list, end_list):
        # print("%s %s %s", pos, start_list, end_list)
        if(start_list > end_list):
            return None
        if pos >= len(line):
            return self.command_list[start_list]
        idx = start_list
        while(idx < len(self.command_list) 
              and line[pos] != self.command_list[idx][pos]):
            idx += 1
        if idx >= len(self.command_list):
            return None
        idx_start = idx

        # print("endlist: %s" %(end_list))

        while(idx <= end_list and line[pos] == self.command_list[idx][pos]):
            idx += 1
        if idx > end_list:
            idx = end_list
        return self.autocomplete_helper(line, pos + 1, idx_start, idx)

    def UpHistory(self):
        if (self.history_point > 0):
            if (self.history_point == len(self.history)):
                self.current_typing = self.input_box.get()
            self.history_point -= 1
            self.input_box.delete(0, 'end')
            self.input_box.insert(0, "%s" % self.history[self.history_point])

    def DownHistory(self):
        if self.history_point < len(self.history):
            self.history_point += 1
            if(self.history_point == len(self.history)):
                self.input_box.delete(0, 'end')
                self.input_box.insert(0, self.current_typing)
            else:
                self.input_box.delete(0, 'end')
                self.input_box.insert(0, self.history[self.history_point])

    def insert_into_history(self, line):
        self.history.append(line)
        self.history_point = len(self.history)


def sig_handler(signal, frame):
    """
    Signal handler for SIGINT
    """
    print('')
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


if __name__ == '__main__':
    # prepare argument parser
    signal.signal(signal.SIGINT, sig_handler)
    argparser = get_arg_parser()
    # parse arguments
    args = vars(argparser.parse_args())
    root = Tk()
    app = ClientApp(root, args)
    app.run()

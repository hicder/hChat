import sys, re, logging, socket
from time import gmtime, strftime, localtime
sys.path.append('../network')
from network_worker import NetworkWorker

class IRCClient:
    """
    Represents a simple IRC client. When using this client, users will need to:
        1. call connect_server().
        2. call set_username(). otherwise, nickname will be 'anonymous'
        3. In the main loop, process user's input by on_typing()

    Example:
        c = IRCClient()                 # initialize a new IRC client.
        c.connect_server(host, port)    # connect to server.
        c.set_username(nickname)        # set nickname before join channel.
        while True:
            line = raw_input()
            c.on_typing(line)           # process input from user.
    """
    def __init__(self, text_callback = None):
        """
        Client object. Note that self.channel does NOT save # character.
        """
        self.tk = None
        self.channel = ''
        self.username = ''
        self.on_typing = self.process_line_from_user
        self.on_receiving = self.process_line_from_server
        logging.basicConfig(format='%(levelname)s: %(message)s',
                            level=logging.DEBUG, filename='irc.log')
        self.text_callback = text_callback

    def tcp_recv(self, s):
        """
        Callback function to receive from the server.
        Args:
            socket (socket): the socket that is connected to the server.
        """
        while True:
            try:
                data = s.recv(100000)
                data = data.decode('UTF-8')
            except socket.error:
                print ('Connection is terminated. Please try again.')
            lines = data.split('\r\n')
            for line in lines:
                self.on_receiving(line)

    def is_channel(self, txt):
        """
        Check if txt is actually a channel or username. Channel starts with #.

        Args:
            txt (string): name to check.
        """
        return txt.startswith('#')

    def process_line_from_server(self, line):
        """
        Process message from the server.

        Args:
            line (string): message from the server.
        """
        if not line:
            return
        logging.debug(line)
        pattern = "^(:(?P<prefix>[^ ]+) +)?(?P<command>[^ ]+)( *(?P<argument> .+))?"
        compiled_pattern = re.compile(pattern)
        m = compiled_pattern.match(line)
        if not m:
            return
        pre = m.group('prefix')
        cmd = m.group('command')
        arg = m.group('argument')
        logging.info('PRE: %s', pre)
        logging.info('CMD: %s', cmd)
        logging.info('ARG: %s', arg)

        if arg:
            if not self.check_destination(arg) and cmd != 'PING':
                return
            arg = arg.strip()

        if cmd:
            if self.is_number(cmd):
                if int(cmd) >= 311 and int(cmd) <= 318:
                    self.process_whois(cmd, arg) 
                elif int(cmd) == 391:
                    self.process_time(arg)
                elif int(cmd) == 332:
                    self.process_topic(arg)
                elif int(cmd) == 322:
                    self.process_list(arg)
                elif int(cmd) == 372:
                    self.process_motd(arg)
                elif int(cmd) == 371:
                    self.process_info(arg)
                elif int(cmd) == 353:
                    self.process_names(arg)

            if cmd == 'PRIVMSG':
                self.process_privmsg(pre, cmd, arg)
            elif cmd == 'PING':
                self.tk.talk('PONG %s\r\n' % arg)
            elif cmd == 'PART':
                self.process_part(pre, arg)
            elif cmd == 'JOIN':
                self.process_join(pre)

    def process_names(self, arg):
        """
        Process list of names.
        """
        if not arg:
            return
        names = arg.split(':')[1]
        names_list = names.split(' ')
        if self.text_callback:
            self.text_callback('## [' + '] ['.join(names_list) + ']')
        print ('## [' + '] ['.join(names_list) + ']')

    def check_destination(self, arg):
        """
        Ensure that the message goes to the right address.

        Args:
            arg (string): argument to check for.
        """
        arg = arg.strip()
        newarg = arg
        if arg.startswith(':'):
            newarg = newarg[1:]
        receiver = newarg.split(' ')[0]
        if receiver != self.username and receiver != self.channel:
            return False
        return True

    def process_info(self, arg):
        """
        Process response for INFO command.
        """
        msg = ' '.join(arg.split(' ')[1:])
        if self.text_callback:
            self.text_callback("## Info %s" % msg)
        print ("## Info %s" % msg)

    def process_motd(self, arg):
        """
        Process response for MOTD command.
        """
        if not arg:
            return
        msg = ' '.join(arg.split(' ')[2:])
        if(self.text_callback):
            self.text_callback("## MOTD: %s" % msg)

    def process_list(self, arg):
        """
        Process RESPONSE for list command.
        """
        msg = ' '.join(arg.split(' ')[1:])
        if self.text_callback:
            self.text_callback("## chanel %s" % msg)

    def process_topic(self, arg):
        """
        Process response for TOPIC message.
        """
        topic = ' '.join(arg.split(' ')[2: ])
        topic = topic[1:]
        if self.text_callback:
            self.text_callback("## channel topic: %s" % topic)

    def process_time(self, arg):
        """
        PROCESS response fro TIME command
        """
        server = arg.split(' ')[1]
        time = ' '.join(arg.split(' ')[2:])
        if self.text_callback:
            self.text_callback("## time at %s %s" % (server, time))

    def process_part(self, pre, arg):
        """
        Process PART response packet.
        """
        nick = pre.split('!')[0]
        if self.text_callback:
            self.text_callback("## %s just left" % nick)

    def process_join(self, pre):
        """
        Process JOIN response packet.
        """
        logging.info('processing join')
        nick = pre.split('!')[0]
        if nick == self.username:
            return
        if self.text_callback:
            self.text_callback("## %s just joined" % nick)

    def process_privmsg(self, pre, cmd, arg):
        """
        Process PRIVMSG response packet.
        """
        # print line
        author = pre.split('!')[0]
        msg = ' '.join(arg.strip().split(' ')[1:])[1:]
        channel_or_user = arg.strip().split(' ')[0]
        logging.debug('channel_or_user: %s, self.channel %s' % (
                      channel_or_user, self.channel))
        t = self.get_time_string_hour_minute()
        if self.is_channel(channel_or_user):
            if channel_or_user == self.channel:
                if self.text_callback:
                    self.text_callback("%s < %s> %s" %(t, author, msg))
        else:
            if self.text_callback:
                self.text_callback("%s < %s> %s" %(t, author, msg))

    def process_whois(self, cmd, arg):
        """
        Process WHOIS response packet.
        """
        arg = ' '.join(arg.split(' ')[1:])
        logging.info('processing WHOIS with cmd %s', cmd)
        if int(cmd) == 311:
            real_name = arg.split(' ')[4:]
            if self.text_callback:
                self.text_callback("## Real name: %s" % (' '.join(real_name))[1:])
        elif int(cmd) == 312:
            server = arg.split(' ')[1]
            server_info = arg.split(' ')[2:]
            if self.text_callback:
                self.text_callback("## Server: %s [%s]" %(server, ' '.join(server_info)))

    def connect_server(self, host, port):
        """
        Connect to IRC channel.

        Args:
            host (string): server of IRC server
            port (int): the port in which IRC server binds to.
        """
        self.tk = NetworkWorker(host, port, callback=self.tcp_recv)
        self.host = host
        self.port = port

    def process_command_from_user(self, line):
        """
        Process command from user. This function is only called when it is sure
            that what user types is a real command.

        Args:
            line (string): command from users. line has to start with '/'.
        """
        line = line[1:] # remove the / in the front.
        cmd = line.split(' ')[0].upper()
        args = line.split(' ')
        if cmd == 'JOIN':
            self.join_channel(line.split(' ')[1])
        elif cmd == 'NICK':
            args = line.split(' ')[1:]
            self.set_username(args[0])
        elif cmd == 'PART':
            self.leave_channel()
        elif cmd == 'QUIT':
            sys.exit(0)
        elif cmd == 'LIST':
            self.list()
        elif cmd == 'WHOIS':
            if not len(args):
                print ('You need to specify who to WHOIS')
                return
            self.whois(args[1])
        elif cmd == 'TIME':
            self.get_server_time()
        elif cmd == 'MOTD':
            self.motd()
        elif cmd == 'INFO':
            self.info()

    def info(self):
        """
        Send INFO command.
        """
        self.tk.talk("INFO\r\n")

    def motd(self):
        """
        Send MOTD command.
        """
        self.tk.talk("MOTD\r\n")

    def get_server_time(self):
        """
        Send TIME command.
        """
        self.tk.talk("TIME\r\n")

    def whois(self, nick):
        """
        Send WHOIS command.

        Args:
            nick (string): nick name to find information about.
        """
        self.tk.talk("WHOIS %s\r\n" % nick)

    def list(self):
        """
        Send LIST command.
        """
        cmd = "LIST %s\r\n" % self.channel
        self.tk.talk(cmd)

    def leave_channel(self):
        """
        Send message to the server to announce the leaving of room.
        """
        msg = "PART %s :%s\r\n" % (self.channel, self.username)
        self.channel = ''
        self.tk.talk(msg)

    def process_line_from_user(self, line):
        """
        Process INPUT from user.

        Args:
            line (string): input from user.
        """
        if line.startswith('/'):
            self.process_command_from_user(line)
        else:
            t = self.get_time_string_hour_minute()
            msg = "PRIVMSG %s :%s\r\n" % (self.channel, line)
            if self.text_callback:
                self.text_callback("%s < %s> %s" % (t, self.username, line))
            print ("%s < %s> %s" % (t, self.username, line))
            self.tk.talk(msg)

    def set_username(self, username):
        """
        Announce the server about change of nickname.
        @TODO (hieu): implement the check to see if nickname is 
            successfully changed.

        Args:
            username (string): new nickname.
        """
        self.username = username
        msg = 'NICK %s\r\n' % username
        msg += 'USER %s localhost %s :%s\r\n' %(username, 'localhost', username)
        self.tk.talk(msg)

    def join_channel(self, channel):
        """
        Join a channel. Note that channel argument does NOT start with #.

        Args:
            channel (string): channel name. does NOT start with #.
        """
        # make sure you have a username. set default to anonymous.
        if not self.username:
            self.set_username('anonymous')

        msg = "JOIN %s\r\n" % channel
        self.channel = channel
        self.tk.talk(msg)

    def is_number(self, s):
        """
        Check if s is a number.
        """
        try:
            float(s)
            return True
        except ValueError:
            return False

    def get_time_string_hour_minute(self):
        """
        Get the current time in hour:minutes.
        """
        return strftime("%H:%M", localtime())

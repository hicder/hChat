hChat
=====

Welcome to hChat, a simple IRC Client written by Duc Hieu Pham from [University
of Illinois at Urbana-Champaign](http://illinois.edu).

This program can be used as a standalone program, or can be used as a library
framework.

## Table of Contents
- [Quick start](#quick-start)
- [What's included](#whats-included)

## Quick start
### Standalone
- Clone the repo `git clone https://github.com/hicder/hChat.git`
- Start the program `python client.py --dhost [host] --irc -u [username]`

### Framework
- Clone the repo `git clone https://github.com/hicder/hChat.git`
- Include the client library: `from ircclient import IRCClient`

## What's included

This program contains 2 types of clients: IRC client and hClient. It also
contains a server called hServer. The directories will look like this:
```
hChat
|--client
|  |--__init__.py
|  |--client.py
|  |--client_parser.py
|--model
|--network
|--server
|--.gitignore
|--README.md
```

### hClient

This client only works with hServer. hClient and hServer exchanges messages
serialized by Python [pickle](https://docs.python.org/2/library/pickle.html).

### hServer

This is the special type of server that only communicates with hClient. Like
hClient, it exchanges message by Python [pickle](https://docs.python.org/2/library/pickle.html).

### IRC Client

This is used to communicate with IRC Server.

[Commands](http://en.wikipedia.org/wiki/List_of_Internet_Relay_Chat_commands) supported:
- JOIN
- WHOIS
- LIST
- PART
- QUIT
- MOTD
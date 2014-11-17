hChat
=====

Welcome to hChat, a simple IRC Client written by Duc Hieu Pham from [University
of Illinois at Urbana-Champaign](http://illinois.edu).

## What's included

This program contains 2 types of clients: IRC client and hClient. It also
contains a server called hServer.

### hClient

This client only works with hServer. hClient and hServer exchanges messages
serialized by Python [pickle](https://docs.python.org/2/library/pickle.html).

### hServer

This is the special type of server that only communicates with hClient. Like
hClient, it exchanges message by Python [pickle](https://docs.python.org/2/library/pickle.html).

### IRC Client

This is used to communicate with IRC Server.

Commands supported:
- JOIN
- WHOIS
- LIST
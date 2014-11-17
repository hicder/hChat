import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('localhost', 6667))
s.send("NICK jay\r\nUSER jay localhost 127.0.0.1 :jay\r\n")
data = s.recv(1000)

print data

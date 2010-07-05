#!/usr/bin/python3

import sys

address = "192.168.1.110"
port = int(sys.argv[1])

# Test utility that acts as a websocket client
# (i.e. web browser) and connects to your websocket
# server and makes sure that your server is obeying
# protocol.

import socket

s = socket.create_connection((address,port))
s.setblocking(1)

print("Connected to " + address + ":" + str(port))

def write_string(str):
    print(str.strip())
    s.sendall((str).encode("utf-8"))
def write_line(str):
    write_string(str + "\r\n")

print ("====WRITING: ")
write_line("GET /play HTTP/1.1")
write_line("Upgrade: WebSocket")
write_line("Connection: Upgrade")
write_line("Host: 192.168.1.110:" + str(port))
write_line("Origin: http://localhost:82")
write_line("Sec-WebSocket-Key1: Uv3   \C5] 82  t00!2 64 d")
write_line("Sec-WebSocket-Key2: q rh4 1 %1 5  D k2I7 7[89  0")
write_line("")
write_string("12345678")

r = s.makefile('rb', 512)

def read_line():
    line = r.readline().decode("utf-8")
    print("RECEIVED: " + line.strip())
    if not line.endswith("\r\n"):
        raise BaseException("Line does not end with \r\n.")
    return line[:-2]

print("====RECEIVED:")
while True:
    line = read_line()
    if line == "":
        break

bytes = r.read(16)

stri = ""
for b in bytes:
     stri += str(b) + " "
print("====RECEIVED BYTES: " + stri)

s.sendall(b'\x00' + ("cbye").encode("utf-8") + b'\xff')
s.sendall(b'\x00' + ("csillly").encode("utf-8") + b'\xff')
s.sendall(b'\xff\x00')

while True:
    b = r.read(1)
    if len(b)==0: break
    print("====RECEIVED BYTE: " + str(b))
print("Connection terminated.")

#!/usr/bin/python3
"""
Speedy scrabble server
"""

# Python 3.1 documentation: http://docs.python.org/py3k/library/index.html

from datetime import datetime
import socketserver
import http.server
import logging
import os
import re
import socket
import sys
import time
import threading
import queue

#### Options ####
_HOST = "speedyscrabble.local"
_PORT = 83

#### Set up logging ####
log = logging.getLogger()
log.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(name)s: %(message)s")
handler.setFormatter(formatter)
log.addHandler(handler)

log.info("Starting server.")


class WebSocket:
    def __init__(self, socket):
        self._socket = socket
        self._send_queue = queue.Queue()
        self._receive_queue = queue.Queue()
        self._sender = threading.Thread(target=self.send_thread)
        self._sender.daemon = True
        self._sender.start()
        # TODO: self.receiver = threading.Thread(...)

    def send(self, frame):
        '''Non-blocking function that puts the frame in a queue to be sent later by the sending thread.'''
        if frame.__class__ == bytes:
            # Assumption: if frame is a list of bytes, it is a properly formatting frame already!
            bytez = frame
        else:
            bytez = bytes([0]) + frame.encode('utf-8') + bytes([0xFF])
        
        self._send_queue.put(bytez)

    def send_thread(self):
        while True:
            bytes = self._send_queue.get()
            self._socket.sendall(bytes)

class WebSocketServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    # The threads created will be daemons, which means that the process
    # will terminate even if those threads are still alive.
    socketserver.ThreadingMixIn.daemon_threads = True

    def __init__(self, server_address, RequestHandlerClass, bind_and_activate=True):
        # Store ws_host and ws_port so they can easily be accessed later (ws_host gets modified
        # by TCPServer's server_bind function, so we can't just read server_address at a later time).
        self.ws_host = server_address[0]
        self.ws_port = server_address[1]
        http.server.HTTPServer.__init__(self, server_address, RequestHandlerClass, bind_and_activate)

_myvar = 0

class WebSocketHandler(http.server.BaseHTTPRequestHandler):
    # self.rfile is an io.BufferedReader
    #    http://docs.python.org/py3k/library/io.html#io.BufferedReader
    # self.wfile is an io.BufferedWriter
    #    http://docs.python.org/py3k/library/io.html#io.BufferedWriter
    # self.headers is an http.client.HTTPMessage, implemented using email.message.Message:
    #    http://docs.python.org/py3k/library/email.message.html#email.message.Message

    def do_GET(self):
        log.debug("New websocket request, path=%s" % self.path)
        # TODO: set timeout?
        self.request.settimeout(None)
        self.request.setblocking(1)
        self.write_line("HTTP/1.1 101 Web Socket Protocol Handshake")
        self.write_line("Upgrade: WebSocket")
        self.write_line("Connection: Upgrade")
        self.write_line("WebSocket-Origin: http://"+self.server.ws_host)
        self.write_line("WebSocket-Location: ws://%s:%d/play" % (self.server.ws_host, self.server.ws_port))
        #self.write_line("WebSocket-Protocol: sample")
        self.write_line("")
        self.wfile.flush()

        ws = WebSocket(self.request)

        while True:
            time.sleep(1)
            message = 'clock!pid=%d thread=%d myvar=%d %s' % (os.getpid(), threading.current_thread().ident, _myvar, datetime.now())
            # self.send_message(message) # tmphax
            ws.send(message);

    def write_line(self, string):
        log.debug("Sending line: " + string)
        self.wfile.write((string+'\r\n').encode('utf-8'))

    def send_message(self, message):
        log.debug("Sending message: " + message)
        self.wfile.write(bytes([0]) + message.encode('utf-8') + bytes([0xFF]))
        self.wfile.flush()
        return

if __name__ == "__main__":
    server = WebSocketServer((_HOST, _PORT), WebSocketHandler)
    server.serve_forever()

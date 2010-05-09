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
import select

__all__ = ["WebSocketServer"]

#### Set up logging ####
log = logging.getLogger()
log.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(name)s: %(message)s")
handler.setFormatter(formatter)
log.addHandler(handler)

log.info("Starting server module.")

class WebSocket:
    def __init__(self, socket, rfile):
        self._socket = socket
        self._rfile = rfile
        self._send_queue = queue.Queue()
        self._receive_queue = queue.Queue()
        self._sender = threading.Thread(target=self.send_thread)
        self._sender.daemon = True
        self._sender.start()
        self._receiver = threading.Thread(target=self.receive_thread)
        self._receiver.daemon = True
        self._receiver.start()

    def send(self, frame):
        '''Non-blocking function that puts the frame in a queue to be sent later by the sending thread.'''
        if frame.__class__ == bytes:
            # Assumption: if frame is a list of bytes, it is a properly formatting frame already!
            byte_list = frame
        else:
            byte_list = bytes([0]) + frame.encode('utf-8') + bytes([0xFF])
        
        self._send_queue.put(byte_list)

    def receive(self):
        if self._receive_queue.empty():
            return None
        return self._receive_queue.get()

    def send_thread(self):
        while True:
            byte_list = self._send_queue.get()
            self._socket.sendall(byte_list)
            self._send_queue.task_done()

    def receive_thread(self):
        log.debug("Started receive_thread for this websocket.");
        while True:
            #r,w,e = select.select([self._socket], [], [])
            #assert r
            frame_type = self._rfile.read(1)[0]
            if (frame_type & 0x80) == 0x80:
                # This is a binary frame: read it and discard it.
                length = 0
                while True:
                    byte = self._read_byte()
                    length = length*128 + (byte & 0x7F)
                    if (byte & 0x80) == 0:
                        break
                self._rfile.read(length)
                if frame_type == 0xFF and length == 0:
                    log.debug("Client closed the connection.  Ending the receive thread.")
                    # TODO: do something to let the server software know
                    return
            else:
                # This is a utf-8 frame, ending with 0xFF.
                bytes_obj = bytes()
                while True:
                    ch = self._read_byte()
                    if ch == 0xFF:
                        break
                    bytes_obj += bytes([ch])
                # According to mod_pywebsocket, the Web Socket protocol
                # section 4.4 specifies that invalid characters must be
                # replaced with U+fffd REPLACEMENT CHARACTER.
                string = bytes_obj.decode('utf-8', 'replace')
                log.debug("Received UTF8 string from socket: %s" % string)
                self._receive_queue.put(string)

    def _read_byte(self):
        return self._rfile.read(1)[0]

    def block_until_closed(self):
        while True:
            pass
        # TODO: really implement this

class WebSocketServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    # The threads created will be daemons, which means that the process
    # will terminate even if those threads are still alive.
    socketserver.ThreadingMixIn.daemon_threads = True

    def __init__(self, host, port):
        # Store ws_host and ws_port so they can easily be accessed later (ws_host gets modified
        # by TCPServer's server_bind function, so we can't just read server_address at a later time).
        http.server.HTTPServer.__init__(self, (host, port), WebSocketHandler, True)
        self.ws_host = host
        self.ws_port = port
        self.thread = None
        self.new_ws_queue = queue.Queue()

    def start(self):
        '''Starts the server running in a new Daemon thread.'''
        if self.thread:
            raise Error("Server was already started.  Restart is not supported yet.")
        self.thread = threading.Thread(target=self.serve_forever)
        self.thread.daemon = True
        self.thread.start()

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

        ws = WebSocket(self.request, self.rfile)
        log.debug("Adding WS to new_ws_queue")
        self.server.new_ws_queue.put(ws)
        ws.block_until_closed()

    def write_line(self, string):
        log.debug("Sending line: " + string)
        self.wfile.write((string+'\r\n').encode('utf-8'))

#### Options ####
#_HOST = "speedyscrabble.local"
#_PORT = 83
#if __name__ == "__main__":
#    server = WebSocketServer((_HOST, _PORT), WebSocketHandler)
#    server.serve_forever()

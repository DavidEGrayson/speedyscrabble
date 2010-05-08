#!/usr/bin/python3
"""
Speedy scrabble server
"""

# Pytho 3.1 documentation: http://docs.python.org/py3k/library/index.html

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

#### Set up logging ####
log = logging.getLogger()
log.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(name)s: %(message)s")
handler.setFormatter(formatter)
log.addHandler(handler)

log.info("Starting server.")

class WebSocketServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    # The threads created will be daemons, which means that the process
    # will terminate even if those threads are still alive.
    socketserver.ThreadingMixIn.daemon_threads = True

_myvar = 0

class WebSocketHandler(http.server.BaseHTTPRequestHandler):
    # self.rfile is an io.BufferedReader
    #    http://docs.python.org/py3k/library/io.html#io.BufferedReader
    # self.wfile is an io.BufferedWriter
    #    http://docs.python.org/py3k/library/io.html#io.BufferedWriter
    # self.headers is an http.client.HTTPMessage, implemented using email.message.Message:
    #    http://docs.python.org/py3k/library/email.message.html#email.message.Message

    def do_GET(self):
        log.debug("New websocket request, path=%s, headers=%s, origin=%s" % (self.path, self.headers.keys(), self.headers['Origin']))
        self.write_line("HTTP/1.1 101 Web Socket Protocol Handshake")
        self.write_line("Upgrade: WebSocket")
        self.write_line("Connection: Upgrade")
        self.write_line("WebSocket-Origin: http://speedyscrabble.local")
        self.write_line("WebSocket-Location: ws://speedyscrabble.local:83/play")
        #self.write_line("WebSocket-Protocol: sample")
        self.write_line("")
        self.wfile.flush()
        while True:
            time.sleep(1)
            self.send_message('clock!pid=%d thread=%d myvar=%d %s' % (os.getpid(), threading.current_thread().ident, _myvar, datetime.now()))

    def write_line(self, string):
        self.wfile.write((string+'\r\n').encode('utf-8'))

    def send_message(self, message):
        log.debug("Sending message: " + message)
        self.wfile.write(bytes([0]) + message.encode('utf-8') + bytes([0xFF]))
        self.wfile.flush()
        return

if __name__ == "__main__":
    server = WebSocketServer(("speedyscrabble.local", 83), WebSocketHandler)
    server.serve_forever()

# Python 3.1 documentation: http://docs.python.org/py3k/library/index.html

import logging
import multiplexingtcpserver
import re

__all__ = ["WebsocketServer"]

_reraised_exceptions = (KeyboardInterrupt, SystemExit)

log = logging.getLogger("websocket")

class Websocket(multiplexingtcpserver.BaseConnectionHandler):
    def handle_new(self):
        pass

    def handle_frame(self, string):
        log.debug("should not be here")
        pass

    def write_frame(self, frame):
        # Make some sort of change to ensure that frames don't
        # get sent until a valid websocket connection is established.
        b = bytes([0]) + frame.encode('utf-8') + bytes([0xFF])
        self.write_bytes(b)

    def generator(self):
        # Handle the HTTP-resembling lines received from the client.

        line = yield "readline"
        m = re.match("GET (/\S+) HTTP/1.1$", line)
        if not m:
            raise BaseException("First line from client has bad syntax: " + line[:255])
        self.request_path = m.group(1)
        log.debug("Processing new request for: " + self.request_path[:255])

        line = yield "readline"
        if line != "Upgrade: WebSocket":
            raise BaseException("Upgrade line from client has bad syntax: " + line[:255])

        line = yield "readline"
        if line != "Connection: Upgrade":
            raise BaseException("Connection line from client has bad syntax: " + line[:255])

        line = yield "readline"
        m = re.match("Host: (\S+)$", line)
        if not m:
            raise BaseException("Host line from client has bad syntax: " + line[:255])
        self.host = m.group(1)

        line = yield "readline"
        m = re.match("Origin: (\S+)$", line)
        if not m:
            raise BaseException("Origin line from client has bad syntax: " + line[:255])
        self.origin = m.group(1)

        line = yield "readline"
        if line != "":
            raise BaseException("Expected blank line, but received: " + line[:255])

        self.write_line("HTTP/1.1 101 Web Socket Protocol Handshake")
        self.write_line("Upgrade: WebSocket")
        self.write_line("Connection: Upgrade")
        self.write_line("WebSocket-Origin: " + self.server.ws_origin)
        self.write_line("WebSocket-Location: " + self.server.ws_location + self.request_path)
        self.write_line("")

        self.server.websockets.add(self)

        self.handle_new()

        buf = b''
        while True:
            # Each iteration of this loop will receive one frame from
            # the client.

            frame_type = yield 'readbyte'
            if (frame_type & 0x80) == 0x80: # Binary frame.
                # Determine its length.
                length = 0
                while True:
                    byte = yield 'readbyte'
                    length = length*128 + (byte & 0x7F)
                    if (byte & 0x80) == 0:
                        break

                # Read the binary data and discard it.
                for i in range(length):
                    yield 'readbyte'

                # The sequence 0xFF,0x00 from the client closes the connection.
                if frame_type == 0xFF and length == 0:
                    log.info("Connection gracefully closed by " + str(client_address))
                    return
            else:
                # This is a utf-8 frame, ending with 0xFF.
                bytes_list = bytes()
                while True:
                    b = yield 'readbyte'
                    if b == 0xFF:
                        break
                    bytes_list += bytes([b])

                # According to mod_pywebsocket, the Web Socket protocol
                # section 4.4 specifies that invalid characters must be
                # replaced with U+fffd REPLACEMENT CHARACTER.
                string = bytes_list.decode('utf-8', 'replace')
                log.debug("Received UTF8 string from socket: %s" % string)
                self.handle_frame(string)

class WebsocketServer(multiplexingtcpserver.MultiplexingTcpServer):
    # websockets is the set of connections that have successfully
    # completed the handshaking stage, and so we can now send and
    # receive websocket frames from them.
    websockets = set()

    def close_connection(self, connection):
        MultiplexingTcpServer.close_connection(self, connection)
        self.websockets.discard(connection)

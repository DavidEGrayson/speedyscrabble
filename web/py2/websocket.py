import logging
import multiplexingtcpserver
import re
import urllib.parse

__all__ = ["WebsocketServer"]

log = logging.getLogger("websocket")

class Websocket(multiplexingtcpserver.BaseConnectionHandler):
    def handle_new(self):
        pass

    def handle_frame(self, string):
        pass

    def accept_handshake(self):
        '''Returns true if the websocket handshake information is valid.
        Returns false otherwise.
        The default implementation checks self.host and self.origin,
        but the user can over-ride this function to
        check more things such as self.request_path and self.params.'''
        # Make sure that the connection originated from the right webpage.
        # e.g. http://www.example.com:78
        if self.origin != self.server.origin:
            return False
        
        # Make sure that the Host field is correct
        # e.g. www.example.com:83
        if self.host != self.server.host:
            return False

        return True

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
        request_string = m.group(1)
        
        url_parts = urllib.parse.urlparse(request_string, 'http')
        self.request_path = url_parts.path
        self.params = urllib.parse.parse_qs(url_parts.query)

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

        if not self.accept_handshake():
            return

        self.write_line("HTTP/1.1 101 Web Socket Protocol Handshake")
        self.write_line("Upgrade: WebSocket")
        self.write_line("Connection: Upgrade")
        self.write_line("WebSocket-Origin: " + self.server.origin)
        self.write_line("WebSocket-Location: ws://" + self.server.host + request_string)
        self.write_line("")

        self.handle_new()

        self.server.websockets.add(self)

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
                log.debug("Received frame from %s: %s" % (self.name, string))
                self.handle_frame(string)

class WebsocketServer(multiplexingtcpserver.MultiplexingTcpServer):
    # websockets is the set of connections that have successfully
    # completed the handshaking stage, and so we can now send and
    # receive websocket frames from them.
    websockets = set()

    def __init__(self, server_address, origin, host, ConnectionHandlerClass):
        '''server_address should be like ('192.168.1.110', 83).
        origin should be like http://www.example.com (with port number if
        it is not port 80).
        host should be the websocket host name (www.example.com:83)'''
        multiplexingtcpserver.MultiplexingTcpServer.__init__(self, server_address, ConnectionHandlerClass)
        self.origin = origin
        self.host = host

    def get_websocket_by_name(self, name):
        for c in self.websockets:
            if c.name == name:
                return c
        return None

    def close_connection(self, connection):
        multiplexingtcpserver.MultiplexingTcpServer.close_connection(self, connection)
        self.websockets.discard(connection)

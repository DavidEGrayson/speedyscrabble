import logging
import multiplexingtcpserver
import re
import urllib.parse
import eventgenerator
import hashlib
import struct

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
        if self.origin not in self.server.origins:
            log.info("Rejected websocket because it had invalid origin: " + self.origin[:255])
            return False
        
        # Make sure that the Host field is correct
        # e.g. www.example.com:83
        if self.host not in self.server.hosts:
            log.info("Rejected websocket because it had invalid host: " + self.host)
            return False

        return True

    def write_frame(self, frame):
        # TODO: Make some sort of change to ensure that frames don't
        # get sent until a valid websocket connection is established.
        self.write_bytes(Websocket.encode_frame(frame))

    def encode_frame(frame):
        return bytes([0]) + frame.encode('utf-8') + bytes([0xFF])

    def generator(self):
        # Handle the HTTP-resembling lines received from the client.

        line = yield "readline"
        m = re.match("^GET (/\S+) HTTP/1.1$", line)
        if not m:
            log.error("First line from client has bad syntax: " + line[:255])
            return

        request_string = m.group(1)
        
        url_parts = urllib.parse.urlparse(request_string, 'http')
        self.request_path = url_parts.path
        self.params = urllib.parse.parse_qs(url_parts.query)

        log.debug("Processing new request for: " + self.request_path[:255])

        self.headers = dict()
        while True:
            line = yield "readline"
            if line is "":
                break

            m = re.match("^([\u0000-\u0009\u000B-\u000C\u000E-\u0039\u003B-\U0010FFFF]+): ?([\u0000-\u0009\u000B-\u000C\u000E-\U0010FFFF]*)$", line)
            if not m:
                log.error("Line from client has invalid syntax: " + line[:255])
                return

            header_name = m.group(1).lower()
            header_value = m.group(2)
            self.headers[header_name] = header_value
            
            log.debug("header: " + header_name + ": " + header_value)

            if len(self.headers) > 300:
                log.error("The client has sent too many headers.")
                return

        if self.headers["upgrade"].lower() != "websocket":
            log.error("Expected Upgrade header sent by client to be 'Websocket' but it was " + self.headers["upgrade"][:255])
            return

        if self.headers["connection"].lower() != "upgrade":
            log.error("Expected readline header sent by client to be 'Connection' but it was " + self.headers["connection"][:255])
            return

        if "host" not in self.headers:
            log.error("Expected to receive a 'Host' header from client, but did not get one.")
            return

        self.host = self.headers["host"]
        
        if "origin" not in self.headers:
            log.error("Expected to receive an 'Origin' header from the client, but did not get one.")
            return

        self.origin = self.headers["origin"]

        if not self.accept_handshake():
            return

        eight_bytes = bytes()
        for i in range(0,8):
            eight_bytes += bytes([(yield "readbyte")])

        byte_string = Websocket.process_key(self.headers["sec-websocket-key1"]) + Websocket.process_key(self.headers["sec-websocket-key2"]) + eight_bytes

        m = hashlib.md5()
        m.update(byte_string)
        md5sum = m.digest()

        if (len(md5sum) != 16):
            log.error("md5sum should be 16 bytes long!")
            return

        header_s = ""
        for x in self.headers:
            header_s += x + " "
        log.debug("Headers received: " + header_s)

        self.write_line("HTTP/1.1 101 WebSocket Protocol Handshake")
        self.write_line("Upgrade: WebSocket")
        self.write_line("Connection: Upgrade")
        self.write_line("Sec-WebSocket-Location: ws://" + self.host + request_string)
        self.write_line("Sec-WebSocket-Origin: " + self.origin)
        if "sec-websocket-protocol" in self.headers:
            self.write_line("Sec-WebSocket-Protocol: " + self.headers["sec-websocket-protocol"])
        self.write_line("")
        self.write_bytes(md5sum)

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

    def process_key(key_str):
        number_string = ""
        space_count = 0
        for char in key_str:
            if char.isdigit():
                number_string += char
            if char == " ":
                space_count += 1

        uint32 = int(int(number_string)/space_count)
        log.debug("Creating key for " + key_str + ": " + str(uint32))
        return struct.pack("!I", uint32) # big endian!

class WebsocketServer(multiplexingtcpserver.MultiplexingTcpServer):

    '''A server that accepts incoming websocket connections.'''

    # websockets is the set of connections that have successfully
    # completed the handshaking stage, and so we can now send and
    # receive websocket frames from them.
    websockets = set()

    def __init__(self, server_address, origins, hosts, ConnectionHandlerClass):
        '''Initializes a new WebSocket server.

        server_address is the argument passed to socket.bind() to open up
        a port and start listening on it.  Example: ('192.168.1.110', 83).
        origins is a list of allowed origin strings. The server requires
        that all clients provide an Origin header equal to one of these strings.
        It should be the domain name of the website that contains the javascript
        code for connecting to your websocket server.
        Example: http://www.example.com (with port number if it is not port 80).
        hosts should be the allowed websocket host names (www.example.com:83)'''
        multiplexingtcpserver.MultiplexingTcpServer.__init__(self, server_address, ConnectionHandlerClass)
        self.origins = origins
        self.hosts = hosts

        self.keep_alive_generator = eventgenerator.EventGenerator(30, self._send_keep_alives)



    def get_websocket_by_name(self, name):
        for c in self.websockets:
            if c.name == name:
                return c
        return None

    def close_connection(self, connection):
        multiplexingtcpserver.MultiplexingTcpServer.close_connection(self, connection)
        self.websockets.discard(connection)

    def enable_keep_alives(self, interval=30, frame=""):
        self.keep_alive_generator.interval = interval
        self.keep_alive_bytes = Websocket.encode_frame(frame)
        self.keep_alive_generator.start()
        self.register_read(self.keep_alive_generator)

    def disable_keep_alives(self):
        self.keep_alive_generator.stop()

    def _send_keep_alives(self):
        log.debug("Sending keep_alives")
        for ws in self.websockets:
            ws.write_bytes(self.keep_alive_bytes)

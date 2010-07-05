import logging
import multiplexingtcpserver
from multiplexingtcpserver import ProtocolException
from multiplexingtcpserver import ConnectionTerminatedCleanly
import re
import urllib.parse
import eventgenerator
import hashlib
import struct

__all__ = ["WebsocketServer"]

log = logging.getLogger("websocket")

class Websocket(multiplexingtcpserver.BaseConnectionHandler):
    # Websocket states:
    # 'handshaking': The websocket handshake is still occurring.
    # 'active': The websocket is active and bidirectional, and
    #    you can send and receive frames on it.  server.websockets
    #    is the set of all active websockets.
    # 'clientclosing': The client sent 0xFF,0x00 so now the we are
    #    send 0xFF,0x00 and we will close the connection when that
    #    is done.
    # 'serverclosing': For some reason, the user's server-side code
    #    wants to terminate the connection, so 0xFF,0x00 has been
    #    queued up to be sent.  All further data from the client
    #    will be ignored, and when a 0xFF,0x00 is received we will
    #    shut down the connection.
    # 'connectionclosing': There was an exception, so we are
    #    just going to close the connection without any handshakes.
    #    This is a short-lived state which the user should only
    #    encounter during his close_websocket() function.
    websocket_state = 'handshaking'

    def new_websocket(self):
        pass

    def handle_frame(self, string):
        pass

    def close_websocket(self, close_reason):
        log.info(self.name + ": Closing websocket: " + close_reason)
        if self.websocket_state == 'active': #TODO: test this
            self.websocket_state = 'serverclosing'
            self.write_bytes(b'\xff\x00')
        self.server.websockets.discard(self)

    def close_connection(self, close_reason):
        if self.websocket_state == 'active':
            self.websocket_state = 'connectionclosing'
            self.close_websocket(close_reason)
        multiplexingtcpserver.BaseConnectionHandler.close_connection(self, close_reason)

    def check_handshake(self):
        '''Returns true if the websocket handshake information is valid.
        Returns false otherwise.
        The default implementation checks self.host and self.origin,
        but the user can over-ride this function to
        check more things such as self.request_path and self.params.'''

        # Make sure that the connection originated from the right webpage.
        # e.g. http://www.example.com:78
        if self.origin not in self.server.origins:
            raise ProtocolException("Rejected websocket because it had invalid origin: " + self.origin[:255])

        # Make sure that the Host field is correct
        # e.g. www.example.com:83
        if self.host not in self.server.hosts:
            raise ProtocolException("Rejected websocket because it had invalid host: " + self.host)

    def write_frame(self, frame):
        if self.websocket_state != 'active':
            log.error(self.name + " is no longer an active websocket (websocket_state=%s), but write_frame was called (frame=%s)" % (self.websocket_state, frame))
        self.write_bytes(Websocket.encode_frame(frame))

    def encode_frame(frame):
        return bytes([0]) + frame.encode('utf-8') + bytes([0xFF])

    def generator(self):
        # Handle the HTTP-resembling lines received from the client.

        line = yield "readline"
        m = re.match("^GET (/[^ ]+) .*\r\n$", line)
        if not m:
            raise ProtocolException(self.name + ": First line from client has bad syntax: " + line[:255])
        resource = m.group(1)
        
        # Compy with section 5.1.3.  (This can be commented out if it
        # causes problems).
        if not re.match("^/[\u0021-\u007E]*$", resource):
            raise ProtocolException(self.name + ": Invalid resource (%s).  Must start with a forward slash and only include characters in the range U+0021 to U+007E." % resource)

        log.info(self.name + ": requested: " + line[:255])

        
        url_parts = urllib.parse.urlparse(resource, 'http')
        self.request_path = url_parts.path
        self.params = urllib.parse.parse_qs(url_parts.query)

        self.headers = dict()
        while True:
            line = yield "readline"
            if line == "\r\n":
                break

            m = re.match("^([\u0000-\u0009\u000B-\u000C\u000E-\u0039\u003B-\U0010FFFF]+): ?([\u0000-\u0009\u000B-\u000C\u000E-\U0010FFFF]*)\r\n$", line)
            if not m:
                raise ProtocolException("Line from client has invalid syntax: " + line[:255])

            header_name = m.group(1).lower()
            header_value = m.group(2)
            self.headers[header_name] = header_value
            
            if len(self.headers) > 300:
                raise ProtocolException("The client has sent too many headers.")

        for header_name in ("host", "origin", "upgrade", "connection"):
            if header_name not in self.headers:
                raise ProtocolException("Expected to receive a '%s' header from client, but did not get one." % header_name.capitalize())
        
        if "origin" not in self.headers:
            raise ProtocolException("Expected to receive an 'Origin' header from the client, but did not get one.")

        if self.headers["upgrade"].lower() != "websocket":
            raise ProtocolException("Expected Upgrade header sent by client to be 'Websocket' but it was " + self.headers["upgrade"][:255])

        if self.headers["connection"].lower() != "upgrade":
            raise ProtocolException("Expected readline header sent by client to be 'Connection' but it was " + self.headers["connection"][:255])

        self.host = self.headers["host"]

        self.origin = self.headers["origin"].lower()

        self.check_handshake()

        # Read 8 more bytes from the host
        eight_more_bytes = bytes()
        for i in range(0,8):
            eight_more_bytes += bytes([(yield "readbyte")])

        # Compute the 16-byte challenge response
        byte_string = Websocket.process_key(self.headers["sec-websocket-key1"]) + Websocket.process_key(self.headers["sec-websocket-key2"]) + eight_more_bytes
        m = hashlib.md5()
        m.update(byte_string)
        md5sum = m.digest()

        self.write_line("HTTP/1.1 101 WebSocket Protocol Handshake")
        self.write_line("Upgrade: WebSocket")
        self.write_line("Connection: Upgrade")
        self.write_line("Sec-WebSocket-Location: ws://" + self.host + resource)
        self.write_line("Sec-WebSocket-Origin: " + self.origin)
        if "sec-websocket-protocol" in self.headers:
            self.write_line("Sec-WebSocket-Protocol: " + self.headers["sec-websocket-protocol"])
        self.write_line("")
        self.write_bytes(md5sum)

        self.websocket_state = 'active'
        self.new_websocket()

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

                    if length > self.server.frame_length_limit:
                        raise ProtocolException("Binary frame exceeded the length limit (%d bytes)." % self.server_frame_length_limit)

                    if (byte & 0x80) == 0:
                        break

                # Read the binary data and discard it.
                for i in range(length):
                    yield 'readbyte'

                if frame_type == 0xFF and length == 0:
                    if self.websocket_state == 'active':
                        # The client sent 0xFF,0x00 which means it wants to
                        # cleanly close the connection.  We must send
                        # 0xFF,0x00 back to the client, and then stop sending
                        # data to it.
                        self.write_bytes(b'\xff\x00')
                        self.websocket_state = 'clientclosing'
                        self.close_websocket("Client sent closing handshake (0xFF,0x00).")
                        yield 'sendall'
                        raise ConnectionTerminatedCleanly("By client.")
                    elif self.websocket_state == 'serverclosing':
                        # We sent a closing handshake, and the client sent
                        # one too (probably in response to ours), so we can
                        # terminate the connection gracefully.
                        raise ConnectionTerminatedCleanly("By server.")
            else:
                # This is a utf-8 frame, ending with 0xFF.
                bytes_list = bytes()
                while True:
                    b = yield 'readbyte'
                    if b == 0xFF:
                        break
                    bytes_list += bytes([b])

                if self.websocket_state == 'active':
                    string = bytes_list.decode('utf-8', 'replace')
                    log.debug(self.name + ": Received frame: " + string)
                    self.handle_frame(string)
                else:
                    log.error(self.name + ": Ignoring frame because websocket_state=%s: %s" % (self.websocket_state, string))

    def process_key(key_str):
        number_string = ""
        space_count = 0
        for char in key_str:
            if char.isdigit():
                number_string += char
            if char == " ":
                space_count += 1

        if space_count == 0:
            raise ProtocolException("Key provided by client contains no spaces.")

        number = int(number_string)

        if number%space_count != 0:
            raise ProtocolException("The key number is not a multiple of the number of spaces in the key.")

        part = int(number/space_count)
        return struct.pack("!I", part) # big endian

class WebsocketServer(multiplexingtcpserver.MultiplexingTcpServer):

    '''A server that accepts incoming websocket connections.'''

    # websockets is the set of connections that have successfully
    # completed the handshaking stage, and so we can now send and
    # receive websocket frames from them.
    websockets = set()

    frame_length_limit = 1024*1024

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
        self.name = "WebSocketServer(%s:%d)" % server_address
        self.origins = origins
        self.hosts = hosts

        self.keep_alive_generator = eventgenerator.EventGenerator(30, self._send_keep_alives)
        self.keep_alive_generator.name = "KeepAliveGenerator(%s)" % self.name



    def get_websocket_by_name(self, name):
        for c in self.websockets:
            if c.name == name:
                return c
        return None

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

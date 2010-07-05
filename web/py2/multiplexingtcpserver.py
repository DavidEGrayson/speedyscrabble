import socket
import io
import select
import logging
import os
import socket
import sys
import time
import threading
import select
import errno
import traceback

_reraised_exceptions = (KeyboardInterrupt, SystemExit)

log = logging.getLogger("multiplexingtcpserver")

class ConnectionTerminatedByClient(Exception): pass
class ConnectionTerminatedCleanly(Exception): pass
class ProtocolException(Exception): pass
class ReadingNotDone(Exception): pass
class WritingNotDone(Exception): pass

class BaseConnectionHandler():
    rbufsize = 128

    def __init__(self, socket, client_address, server):
        self.io_operation = None
        self.server = server
        self.socket = socket
        self.fileno = self.socket.fileno
        self.client_address = client_address
        self.name = self.client_address[0] + ":" + str(self.client_address[1])
        self.rfile = self.socket.makefile('rb', self.rbufsize)
        self._write_buffer = b''

    def new_connection(self):
        '''This is called shortly after __init__.'''
        # We wouldn't want to add this code to __init__ because run_state_machine
        # might do a number of things such as close the connection.  That would make
        # the code in MultiplexingTcpServer.handle_read more complex because we'd
        # have to check if the connection has been closed yet before adding it to
        # the connections set and errorable objects.
        self.state_machine = self.generator()
        self.run_state_machine()

    def __repr__(self):
        return "<connection " + str(self.name) + ">"

    def close_connection(self, close_reason):
        log.info(self.name + ": Closing connection: " + close_reason)
        self.rfile.close()
        self.socket.close()
        self.server._readable_objects.discard(self)
        self.server._writable_objects.discard(self)
        self.server._errorable_objects.discard(self)
        self.server.connections.discard(self)
        log.debug("Total connections: " + str(len(self.server.connections)))
 
    def handle_error(self):
        log.debug(self.name + ": Error on connection.")
        self.close_connection("Error on connection.")

    def handle_read(self):
        self.run_state_machine()

    def _io_operation_result(self):
        '''Attempts to get the result of the read operation requested by
        this connection's state machine.  If the read operation can not
        be completed yet or some other error occurs, an appropriate
        exception is thrown.'''

        # read_operation will be None when the connection first starts.
        if self.io_operation == None:
            return None

        try:
            if self.io_operation == 'readline':
                return self.rfile.readline().decode('utf-8')

            if self.io_operation == 'readbyte':
                result = self.rfile.read(1)
                if len(result) is 0:
                    raise ConnectionTerminatedByClient()
                return result[0]
        except socket.error as e:
            if e.errno is errno.EWOULDBLOCK: raise ReadingNotDone()
            else: raise
    
        if self.io_operation == 'sendall':
            if len(self._write_buffer) > 0:
                raise WritingNotDone()
            log.debug(self.name + ": done with sendall")
            return None

        raise Exception("Unknown read operation: " + str(self.read_operation))

    def run_state_machine(self):
        '''Basically, this function is just:
        
            while True:
               result = self._io_operation_result()
               self.io_operation = self.state_machine.send(result)'''

        try:
            while True:
                try:
                    result = self._io_operation_result()
                except WritingNotDone:
                    self.server.unregister_read(self)
                    return
                except ReadingNotDone:
                    self.server.register_read(self)
                    return

                try:
                    self.io_operation = self.state_machine.send(result)
                except ProtocolException as e:
                    msg = "Protocol exception: " + str(e)
                    log.error(self.name + ": " + msg)
                    self.close_connection(msg)
                    return
                except ConnectionTerminatedCleanly as e:
                    self.close_connection("Connection terminated cleanly. " + str(e))
                    return
                except StopIteration:
                    self.close_connection("State machine stopped.")
                    return
        except ConnectionTerminatedByClient as e:
            self.close_connection("Connection terminated by client. " + str(e))
            return 
        except _reraised_exceptions:
            raise
        except BaseException as e:
            log.error(self.name + ": Unexpected exception: " + str(e))
            traceback.print_tb(e.__traceback__) # TODO: save it to log file instead
            self.close_connection("Unexpected exception: " + str(e))
            return

    def write_bytes(self, bytes):
        '''This is called whenever there is some new data to queue up to
        be sent on this connection's socket.'''
        self._write_buffer += bytes
        self.server.register_write(self)

    def write_line(self, line):
        '''Write a line of text to the client.  The line
        parameter should be a string object.  The line termination
        character will be appended to it, it will be encoded in
        UTF-8, and then it will be sent on the socket.'''
        self.write_bytes((line+"\r\n").encode('utf-8'))

    def handle_write(self):
        '''This is called by the MultiplexingTcpServer.handle_events
        when our socket becomes writable and we are registered as a
        writable object with the server.'''

        # Transfer data from self._write_buffer to self.socket
        if len(self._write_buffer):
            # Send as many bytes as the socket can accept.
            try:
                num_sent = self.socket.send(self._write_buffer)
            except socket.error as e:
                if e.errno is errno.EBADF:
                    self.close_connection("Connection terminated by client (while writing).")
                    return
                else: raise

            # Remove the sent bytes from the buffer.
            self._write_buffer = self._write_buffer[num_sent:]

        # If there is no more data left in the _write_buffer,
        # unregister this connection because we don't need to
        # do any more writing.
        if not len(self._write_buffer):
            self.server.unregister_write(self)
            if self.io_operation == 'sendall':
                self.run_state_machine()

class Multiplexer():
    select_timeout = None
    _readable_objects = set()
    _writable_objects = set()
    _errorable_objects = set()

    def __init__(self):
        self.register_read = self._readable_objects.add
        self.unregister_read = self._readable_objects.discard
        self.register_write = self._writable_objects.add
        self.unregister_write = self._writable_objects.discard
        self.register_error = self._errorable_objects.add
        self.unregister_error = self._errorable_objects.discard

    def handle_events(self):
        readable, writable, errorable = select.select(self._readable_objects,
            self._writable_objects, self._errorable_objects, self.select_timeout)

        for r in readable:
            log.debug("handling read: " + r.name)
            r.handle_read()

        for w in writable:
            log.debug("handling write: " + w.name)
            w.handle_write()

        for e in errorable:
            log.debug("handling error: " + e.name)
            e.handle_error()

class MultiplexingTcpServer(Multiplexer):
    address_family = socket.AF_INET
    socket_type = socket.SOCK_STREAM
    request_queue_size = 2

    connections = set()

    def __init__(self, server_address, ConnectionHandlerClass):
        Multiplexer.__init__(self)
        self.ConnectionHandlerClass = ConnectionHandlerClass
        self.socket = socket.socket(self.address_family, self.socket_type)
        self.fileno = self.socket.fileno

        # This prevents the annoying behavior where we can't restart
        # the server for about a minute after terminating it if there
        # were any clients connected when we terminated it.
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.socket.bind(server_address)
        self.socket.listen(self.request_queue_size)
        self.name = "MultiplexingTcpServer(%s:%d)" % server_address

        # Listen for incoming connections when handle_events is called.
        self.register_read(self)

    def handle_read(self):
        socket, client_address = self.socket.accept()
        log.info("New connection from %s:%d" % (client_address[0], client_address[1]))
        socket.setblocking(0)
        connection = self.ConnectionHandlerClass(socket, client_address, self)
        self.connections.add(connection)
        log.debug("Total connections: " + str(len(self.connections)))
        self.register_error(connection)
        connection.new_connection()

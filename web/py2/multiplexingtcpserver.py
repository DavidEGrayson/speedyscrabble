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

class BaseConnectionHandler():
    rbufsize = 512

    def __init__(self, socket, client_address, server):
        self.read_operation = None
        self.server = server
        self.socket = socket
        self.client_address = client_address
        self.name = self.client_address[0]
        self.rfile = self.socket.makefile('rb', self.rbufsize)
        self._write_buffer = b''

    def __repr__(self):
        return "<connection" + str(self.client_address) + ">"

    def close(self):
        self.server.close_connection(self)

    def _close(self):
        self.handle_close()
        self.rfile.close()
 
    def fileno(self):
        return self.socket.fileno()

    def handle_close(self):
        '''This can be overridden in derived classes to
        handle anything that must happen when the connection is
        closed for any reason (e.g. removing all references to
        the connection and notifying other clients that the
        user has left.'''
        pass

    def handle_error(self):
        log.debug("Error on connection.")
        self.close()

    def handle_start(self):
        self.state_machine = self.generator()
        self.run_state_machine()

    def handle_read(self):
        #log.debug("Data received on web socket")
        self.run_state_machine()

    def read_operation_result(self):
        if self.read_operation is None:
            return None

        if self.read_operation is 'readline':
            return self.rfile.readline().decode('utf-8').strip()

        if self.read_operation is 'readbyte':
            result = self.rfile.read(1)
            #if result is None:
            #    raise io.BlockingIOError()
            if len(result) is 0:
                # When rfile.read returns 0 bytes it means that the client has
                # disconnected.
                raise ConnectionTerminatedByClient()
            return result[0]

        raise BaseException("Unknown read operation: " + str(self.read_operation))

    def run_state_machine(self):
        try:
            while True:
                result = self.read_operation_result()
                self.read_operation = self.state_machine.send(result)
                # TODO: add a count limit here so that one connection
                # can not monoplize the CPU if for example the user was
                # sending bytes faster than they can be processed by the
                # server

        except StopIteration:
            log.debug("State machine ended.")
            self.close()
            return
        except ConnectionTerminatedByClient as e:
            log.debug("Connection to " + self.name + " terminated by client.")
            self.close()
            return
        except socket.error as e:
            if e.errno is errno.EWOULDBLOCK:
                #log.debug("Data not available yet.")
                pass
            else:
                log.debug("Socket error:" + str(e))
                self.close()
                return
        except _reraised_exceptions:
            raise
        except BaseException as e:
            log.error("Exception: " + str(e))
            traceback.print_tb(e.__traceback__) # TODO: save it to log file instead
            self.close()
            return

        if self.read_operation is not None:
            self.server.register_read(self)

    def handle_write(self):
        '''This is called by the MultiplexingTcpServer.handle_events
        when our socket becomes writable and we are registered as a
        writable object with the server.'''

        # Transfer data from self._write_buffer to self.socket
        self._write_bytes_if_needed()

        # If there is no more data left in the _write_buffer,
        # unregister this connection because we don't need to
        # do any more writing.
        if not len(self._write_buffer):
            self.server.unregister_write(self)

    def write_bytes(self, bytes):
        '''This is called whenever there is some new data to queue up to
        be sent on this connection's socket.'''

        self._write_buffer += bytes

        # Try sending the data immediately.  This is just to decrease the
        # latency of sending, it is not necessary.
        self._write_bytes_if_needed()

        # If not all the data could be sent immediately, then tell
        # tell the server that this object is writable.  This means
        # that our handle_write function will get called later when
        # socket is ready to be written to again.
        if len(self._write_buffer):
            self.server.register_write(self)

    def _write_bytes_if_needed(self):
        if len(self._write_buffer):
            # Send as many bytes as the socket can accept.
            num_sent = self.socket.send(self._write_buffer)

            # Remove the sent bytes from the buffer.
            self._write_buffer = self._write_buffer[num_sent:]

    def write_line(self, line):
        '''Write a line of text to the client.  The line
        parameter should be a string object.  The line termination
        character will be appended to it, it will be encoded in
        UTF-8, and then it will be sent on the socket.'''
        self.write_bytes((line+"\r\n").encode('utf-8'))

class MultiplexingTcpServer():
    address_family = socket.AF_INET
    socket_type = socket.SOCK_STREAM
    request_queue_size = 2

    select_timeout = None
    connections = set()
    _readable_objects = set()
    _writable_objects = set()
    _errorable_objects = set()

    def __init__(self, server_address, ConnectionHandlerClass):
        self.ConnectionHandlerClass = ConnectionHandlerClass
        self.socket = socket.socket(self.address_family, self.socket_type)

        # This prevents the annoying behavior where we can't restart
        # the server for about a minute after terminating it if there
        # were any clients connected when we terminated it.
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.socket.bind(server_address)
        self.server_address = self.socket.getsockname()
        self.socket.listen(self.request_queue_size)

        # Listen for incoming connections when handle_events is called.
        self._readable_objects.add(self)

    def __del__(self):
        print("Closing the server socket!")
        for connection in self.connections:
            self.close_connection(connection)
        self.socket.close()

    def register_read(self, readable):
        self._readable_objects.add(readable)

    def register_write(self, writable):
        self._writable_objects.add(writable)

    def unregister_write(self, writable):
        self._writable_objects.discard(writable)

    def close_connection(self, connection):
        log.info("Closing connection to " + str(connection.name) + ".")
        connection._close()
        connection.socket.close()
        self.connections.discard(connection)
        self._readable_objects.discard(connection)
        self._writable_objects.discard(connection)
        self._errorable_objects.discard(connection)

    def handle_events(self):
        readable, writable, errorable = select.select(self._readable_objects,
            self._writable_objects, self._errorable_objects, self.select_timeout)

        log.debug("Selected: #r=%d/%d, #w=%d/%d, #e=%d/%d" %
          (     len(readable), len(self._readable_objects),
                len(writable), len(self._writable_objects),
                len(errorable), len(self._errorable_objects) ) )

        for r in readable:
            r.handle_read()

        for w in writable:
            w.handle_write()

        for e in errorable:
            e.handle_error()

    def fileno(self):
        return self.socket.fileno()

    def handle_read(self):
        socket, client_address = self.socket.accept()
        log.info("New connection from %s:%d" % (client_address[0], client_address[1]))
        socket.setblocking(0)
        connection = self.ConnectionHandlerClass(socket, client_address, self)
        self.connections.add(connection)
        self._errorable_objects.add(connection)
        connection.handle_start()
        log.debug("Total connections: " + str(len(self.connections)))

# Python 3.1 documentation: http://docs.python.org/py3k/library/index.html

from datetime import datetime
import socket
import io
import select
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

class WebsocketTerminatedException(Exception):
    pass

class BaseConnectionHandler():
    rbufsize = 512

    def __init__(self, socket, client_address, server):
        self.read_operation = None
        self.server = server
        self.socket = socket
        self.client_address = client_address
        self.rfile = self.socket.makefile('rb', self.rbufsize)
        self._send_queue = queue.Queue()
        self._send_buffer = None
        self._send_position = 0

    def __repr__(self):
        return "<connection" + str(self.client_address) + ">"

    def close(self):
        self.server.close_connection(self)

    def _close(self):
        self.rfile.close()
 
    def fileno(self):
        return self.socket.fileno()

    def handle_error(self):
        log.debug("Error on connection.")
        self.close()

    def handle_start(self):
        self.state_machine = self.generator()
        self.run_state_machine()

    def handle_read(self):
        log.debug("Data received on web socket")
        self.run_state_machine()

    def read_operation_result(self):
        if self.read_operation is None:
            return None

        if self.read_operation is "readline":
            return self.rfile.readline()

    def run_state_machine(self):
        try:
            while True:
                self.read_operation = self.state_machine.send(self.read_operation_result())
                # TODO: add a count limit here so that one connection
                # can not monoplize the CPU if for example the user was
                # sending bytes faster than they can be processed by the
                # server

        except io.BlockingIOError:
            log.debug("Blocking IO error.")
        except StopIteration:
            log.debug("The state machine ended.")
            self.close()
            return
        except socket.error as e:
            log.debug("Socket error:" + str(e))
            # TODO: Prevent the "resource temporarily unavailable error"
            # and remove this except

        if self.read_operation is not None:
            self.server.register_read(self)


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
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(server_address)
        self.server_address = self.socket.getsockname()
        self.socket.listen(self.request_queue_size)
        self._readable_objects.add(self)

    def __del__(self):
        print("Closing the server socket!")
        for connection in self.connections:
            self.close_connection(connection)
        self.socket.close()

    def register_read(self, readable):
        if not readable in self._readable_objects:
            self._readable_objects.add(readable)

    def close_connection(self, connection):
        log.debug("Closing connection " + str(connection))
        self.connections.discard(connection)
        self._readable_objects.discard(connection)
        self._writable_objects.discard(connection)
        self._errorable_objects.discard(connection)
        connection._close()
        connection.socket.close()

    def handle_events(self):
        readable, writable, errorable = select.select(self._readable_objects,
            self._writable_objects, self._errorable_objects, self.select_timeout)

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
        log.info("New connection from " + str(client_address))
        socket.setblocking(0)
        connection = Websocket(socket, client_address, self)
        #connection = self.ConnectionHandlerClass(socket, client_address, self)
        self.connections.add(connection)
        self._errorable_objects.add(connection)
        connection.handle_start()
        log.debug("Total connections: " + str(len(self.connections)))


class Websocket(BaseConnectionHandler):
    def generator(self):
        line = yield "readline"
        log.debug("Received line 1: " + line.decode('utf-8'))
        line = yield "readline"
        log.debug("Received line 2: " + line.decode('utf-8'))

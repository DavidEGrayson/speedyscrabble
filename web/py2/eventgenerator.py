import socket
import threading
import time
import errno

__all__ = ["EventGenerator"]

class EventGeneratingThread(threading.Thread):
    daemon = True

    def __init__(self, event_generator):
        threading.Thread.__init__(self)
        self.event_generator = event_generator

    def run(self):
        while True:
            time.sleep(self.event_generator.interval)
            if self.event_generator._thread != self:
                return
            self.event_generator._wsocket.send(bytes([0]))


class EventGenerator():
    def __init__(self, interval, handle_event):
        self.interval = interval
        self.handle_event = handle_event
        self._rsocket, self._wsocket = socket.socketpair()
        self._rsocket.setblocking(0)
        self._wsocket.setblocking(1)
        self.fileno = self._rsocket.fileno

    def start(self):
        self._thread = EventGeneratingThread(self)
        self._thread.start()

    def stop(self):
        self._thread = None
        # Flush out any pending events
        try:
            while len(self._rsocket.recv(200)) > 0:
                pass
        except socket.error as e:
            if e.errno is errno.EWOULDBLOCK:
                pass
            else:
                raise

    def handle_read(self):
        self._rsocket.recv(1)
        self.handle_event()

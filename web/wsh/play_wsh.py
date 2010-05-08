from mod_pywebsocket import msgutil
from datetime import datetime
import time
import threading
import os

_GOODBYE_MESSAGE = 'Goodbye'

def web_socket_do_extra_handshake(request):
 print 'Connected.'
 pass  # Always accept.

_myvar = 0

def web_socket_transfer_data(request):
  global _myvar
  while True:
    _myvar += 1
    time.sleep(1)
    date = datetime.now()
    #line = msgutil.receive_message(request)
    #print 'Got something: %s' % line
    #msgutil.send_message(request, line)
    thread = threading.current_thread()
    msgutil.send_message(request, 'clock!pid=%d thread=%d myvar=%d %s' % (os.getpid(), thread.ident, _myvar, date))
    #if line == _GOODBYE_MESSAGE:
    #    return

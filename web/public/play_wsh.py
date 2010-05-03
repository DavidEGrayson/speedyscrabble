from mod_pywebsocket import msgutil
from datetime import datetime
import time

_GOODBYE_MESSAGE = 'Goodbye'

def web_socket_do_extra_handshake(request):
 print 'Connected.'
 pass  # Always accept.

def web_socket_transfer_data(request):
  while True:
    time.sleep(1)
    date = datetime.now()
    #try:
    #    line = msgutil.receive_message(request)
    #except Exception, e:
    #    print 'Foi com os porcos'
    #    raise e
    #print 'Got something: %s' % line
    #msgutil.send_message(request, line)
    msgutil.send_message(request, 'clock!%s' % date)
    #if line == _GOODBYE_MESSAGE:
    #    return

#!/usr/bin/python

import eventlet
from eventlet import wsgi
from eventlet import websocket

# demo app
import os
import random
import logging

log = logging.getLogger()
log.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(name)s: %(message)s")
handler.setFormatter(formatter)
log.addHandler(handler)
log.write = log.debug

@websocket.WebSocketWSGI
def handle(ws):
    print("[root] hell");
    """  This is the websocket handler function.  Note that we 
    can dispatch based on path in here, too."""
    if ws.path == '/echo':
        while True:
            m = ws.wait()
            if m is None:
                break
            ws.send(m)
            
    elif ws.path == '/data':
        for i in xrange(10000):
            ws.send("0 %s %s\n" % (i, random.random()))
            eventlet.sleep(0.1)

    print("chatting")
    while True:
        ws.send("cHeyaaaa")
        ws.wait()
                  
def dispatch(environ, start_response):
    """ This resolves to the web page or the websocket depending on
    the path."""
    print ("[root] HELLO")
    if environ['PATH_INFO'] == '/chat':
        print ("[root] calling handle")
        return handle(environ, start_response)
    else:
        start_response('200 OK', [('content-type', 'text/html')])
        return [open(os.path.join(
                     os.path.dirname(__file__), 
                     '../public/index.html')).read()]
        
if __name__ == "__main__":
    listener = eventlet.listen(('localhost', 83))
    wsgi.server(listener, dispatch, log)

#!/usr/bin/python3

import websocket
import time
from datetime import datetime

host = "speedyscrabble.local"
port = 83

server = websocket.WebSocketServer(host, port)
server.start()

websockets = set()

websocket.log.debug("Entering main loop.")
while True:
    if not server.new_ws_queue.empty():
        ws = server.new_ws_queue.get_nowait()
        websocket.log.debug("Received new WS to new_ws_queue")
        ws.send("cWelcome to the chat room.")
        websockets.add(ws)
    time.sleep(1)
    for ws in websockets:
        # ws.send("ttime=%s" % datetime.now())
        frame = ws.receive()
        if frame is not None:
            websocket.log.debug("Main loop got a frame from ws: " + frame)
            for ws2 in websockets:
                ws2.send("c"+frame)
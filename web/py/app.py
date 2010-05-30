#!/usr/bin/python3

import websocket
import time
import threading
from datetime import datetime

host = "258.graysonfamily.org"
port = 83

server = websocket.WebSocketServer(host, port)
server.start()

websockets = set()

def process_frame_chat(ws, frame):
    for ws2 in websockets:
        ws2.send(frame)
        ws2.send("s %d %d" % (len(websockets), threading.active_count()))

commands_from_client = {
  'c': process_frame_chat
}

def process_frame(ws, frame):
    websocket.log.debug("Main loop got a frame from ws: " + frame)
    action = commands_from_client.get(frame[0])
    if action is not None:
        action(ws, frame)

websocket.log.debug("Entering main loop.")
while True:
    did_work = False

    # Add new websockets to our list.
    if not server.new_ws_queue.empty():
        did_work = True
        ws = server.new_ws_queue.get_nowait()
        websocket.log.debug("Received new WS to new_ws_queue")
        ws.send("cWelcome to the chat room.")
        websockets.add(ws)

    old_websockets = set()

    for ws in websockets:
        # Process commands received from the websockets
        frame = ws.receive()
        if frame is not None:
            did_work = True
            process_frame(ws, frame)

        if ws.terminated():
            old_websockets.add(ws)

    for ws in old_websockets:
        websockets.remove(ws)

    # If appropriate, sleep to save CPU.
    if not did_work:
        time.sleep(0.1)



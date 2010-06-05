#!/usr/bin/python3

import websocket
import time
import threading
from datetime import datetime

bind_host = "192.168.1.110"
port = 83

server = websocket.MultiplexingTcpServer((bind_host,port), websocket.Websocket)

server.ws_origin = "http://258.graysonfamily.org:81"
server.ws_location = "ws://258.graysonfamily.org:83"

websocket.log.debug("Entering main loop.")
while True:
    websocket.log.debug("Handling events...")
    server.handle_events()

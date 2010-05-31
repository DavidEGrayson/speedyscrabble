#!/usr/bin/python3

import websocket
import time
import threading
from datetime import datetime

bind_host = "192.168.1.110"
port = 83

server = websocket.MultiplexingTcpServer((bind_host,port), websocket.Websocket)

websocket.log.debug("Entering main loop.")
while True:
    websocket.log.debug("Handling events...")
    server.handle_events()

#!/usr/bin/python3

import websocket
import time
import threading
from datetime import datetime

def handle_frame_chat(ws, frame):
    for ws2 in server.connections:
        ws2.write_frame(frame)

commands_from_client = {
  'c': handle_frame_chat
}

class SSWebSocket(websocket.Websocket):
    def handle_new(self):
        self.write_frame("cWelcome to the Chat Room.") # tmphax
        for ws2 in server.websockets:
            ws2.write_frame("c" + self.name() + " has entered.")
            pass

    def handle_frame(self, frame):
        action = commands_from_client.get(frame[0])
        if action is not None:
            action(self, frame)

    def name(self):
        return self.client_address[0]

bind_host = "192.168.1.110"
port = 83

websocket.log.info("Starting speedy scrabble server.  ")
server = websocket.WebsocketServer((bind_host,port), SSWebSocket)
server.ws_origin = "http://258.graysonfamily.org:81"
server.ws_location = "ws://258.graysonfamily.org:83"
while True:
    server.handle_events()

#!/usr/bin/python3

import logging
import websocket
import socket

bind_host = "192.168.1.110"
port = 83
ws_origins = ["http://258.graysonfamily.org:81", "http://localhost:81"]
ws_host = "258.graysonfamily.org:83"

log = logging.getLogger()
log.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(name)s: %(message)s")
handler.setFormatter(formatter)
log.addHandler(handler)

def sanitize_user_name(raw_name):
    if raw_name == '':
        return 'Guest'

    raw_name = raw_name[:25]   # Limit to 25 characters or fewer

    name = ''
    for char in raw_name:
        if char.isalnum():
            name += char

    return name


def handle_frame_chat(ws, frame):
    frame = "c" + ws.name + ": " + frame[1:]
    for ws2 in server.websockets:
        ws2.write_frame(frame)

commands_from_client = {
  'c': handle_frame_chat
}

class MyWebsocket(websocket.Websocket):
    def handle_new(self):
        # A new client has connected to the server.
        
        # Assign a name to the client, based on the name he requested
        if 'name' in self.params:
            name = sanitize_user_name(self.params['name'][0])
        else:
            name = 'Guest'

        # Add numbers to the name to avoid duplicates, if needed
        # Assumption: self has not been added to self.server.websockets yet!
        if self.server.get_websocket_by_name(name):
            i = 1
            while self.server.get_websocket_by_name(name + str(i)):
                i += 1
            name += str(i)

        self.name = name

        log.info("New client: " + self.name);

        # Tell the client what his assigned name is.
        self.write_frame('n' + self.name)

        names = [self.name]
        for ws in server.websockets:
            names.append(ws.name)

        status_frame = 's'
        status_frame += ','.join(names)
        self.write_frame(status_frame)

        # Sent a notification to everyone who was already connected to
        # tell them that the client has arrived.
        for ws in server.websockets:
            ws.write_frame('e' + self.name)

    def handle_close(self):
        # Notify all the clients that this person has left.
        for ws2 in server.websockets:
            if (ws2 != self):
                ws2.write_frame('l' + self.name)

    def handle_frame(self, frame):
        action = commands_from_client.get(frame[0])
        if action is not None:
            action(self, frame)

    def name(self):
        return self.name

log.info("Starting server.")
server = websocket.WebsocketServer((bind_host, port), ws_origins, ws_host, MyWebsocket)
server.enable_keep_alives()
while True:
    server.handle_events()

import socket
import logging
import time
import json
import globalState

class Networking:
    def __init__(self, isServer: bool, ip: str = None, port: int = globalState.port):
        self.isServer = isServer
        self.isConnected = False
        self.client_socket = None
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if isServer:
            while True:
                try:
                    self.socket.bind(("0.0.0.0", port))
                    break
                except OSError:
                    logging.error(f"Port {port} is already in use")
                    port += 1
                    logging.info(f"Trying port {port} instead")
            self.socket.listen(5)
            logging.info(f"Server listening on port {port}, ip: {self.socket.getsockname()[0]}")
        else:
            self.socket.connect((ip, port))
            logging.info(f"Connected to server at {ip}:{port}")
            # self.socket.send(json.dumps({"type": "hello"}).encode())
            self.isConnected = True  # Set isConnected to True for the client
        self.socket.setblocking(False)

    def try_accept_connection(self):
        if self.isServer:
            try:
                self.client_socket, client_address = self.socket.accept()
                logging.info(f"Accepted connection from {client_address}")
                self.isConnected = True  # Set isConnected to True for the server
                return self.client_socket, client_address
            except BlockingIOError:
                return None, None
        else:
            logging.error("try_accept_connection called on a client instance")
            return None, None
    
    def close(self):
        if self.isServer and self.client_socket:
            self.client_socket.close()
        self.socket.close()
        self.isConnected = False

    def receive(self):
        if not self.isConnected:
            return None
        try:
            if self.isServer and self.client_socket:
                data = json.loads(self.client_socket.recv(1024).decode())  # Use client_socket for server
            else:
                data = json.loads(self.socket.recv(1024).decode())  # Use socket for client
            return data
        except:
            return None
    
    def send(self, data: dict):
        if not self.isConnected:
            return
        try:
            if self.isServer and self.client_socket:
                self.client_socket.send(json.dumps(data).encode())  # Use client_socket for server
            else:
                self.socket.send(json.dumps(data).encode())  # Use socket for client
        except BlockingIOError:
            return
    
    def broadcastEvent(self, name: str, data: dict):
        if not self.isConnected:
            logging.error("Broadcast failed: Not connected")
            return
        try:
            if self.isServer:
                self.client_socket.send(json.dumps({"type": "event", "name": name, "data": data}).encode())  # Use client_socket for server
            else:
                self.socket.send(json.dumps({"type": "event", "name": name, "data": data}).encode())  # Use socket for client
        except BlockingIOError:
            return
    
    eventCallbacks = {}
    def onEvent(self, name: str, callback):
        if name not in self.eventCallbacks:
            self.eventCallbacks[name] = set([callback])
        else:
            self.eventCallbacks[name].add(callback)
    
    def handle_events(self):
        if not self.isConnected:
            return
        data = self.receive()
        if data is None:
            return
        if data["type"] == "event":
            for callback in self.eventCallbacks.get(data["name"], []):
                callback(data["data"])
    
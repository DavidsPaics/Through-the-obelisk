import socket
import logging
import json

validTypes = ["hello"]

class Networking:
    def __init__(self, isServer: bool, ip: str = None, port: int = 6969):
        self.isServer = isServer
        self.isConnected = False
        self.client_socket = None
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if isServer:
            self.socket.bind(("0.0.0.0", port))
            self.socket.listen(5)
            logging.info(f"Server listening on port {port}, ip: {self.socket.getsockname()[0]}")
        else:
            self.socket.connect((ip, port))
            logging.info(f"Connected to server at {ip}:{port}")
            self.socket.send(json.dumps({"type": "hello"}).encode())
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

    def receive(self):
        if not self.isConnected:
            return None
        try:
            if self.isServer and self.client_socket:
                data = json.loads(self.client_socket.recv(1024).decode())  # Use client_socket for server
            else:
                data = json.loads(self.socket.recv(1024).decode())  # Use socket for client
            if data["type"] not in validTypes:
                logging.error(f"Invalid message type: {data['type']}")
                return None
            return data
        except BlockingIOError:
            return None
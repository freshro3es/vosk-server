from flask import request
from flask_socketio import disconnect, emit
import logging

class Clients:
    def __init__(self):
        # Хранение соответствия между клиентами и их WebSocket-соединениями
        self.client_connections = {}

    def add_client(self, client_id):
        self.client_connections[client_id] = request.sid
        logging.info(f"Client connected: {client_id}")

    def remove_client(self, client_id):
        if client_id in self.client_connections:
            del self.client_connections[client_id]
            logging.info(f"Client disconnected: {client_id}")
            disconnect()
    
    def if_client(self, client_id):
        if client_id in self.client_connections:
            return True
        return False
    
    def get_client_sid(self, client_id):
        return self.client_connections.get(client_id)
    
    def send_message(self, client_id, event, data=None):
        sid = self.get_client_sid(client_id)
        if sid:
            emit(event, data, to=sid)

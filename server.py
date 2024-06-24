from flask import Flask, request, jsonify
from waitress import serve
from database_manager import DatabaseManager

class Server:
    def __init__(self, logger):
        self.logger = logger
        self.db_manager = DatabaseManager()
        self.clients = {}
        self.pending_updates = {}
        self.app = Flask(__name__)
        self.setup_routes()

    def setup_routes(self):
        self.app.add_url_rule('/register', 'register', self.handle_register, methods=['POST'])
        self.app.add_url_rule('/update', 'update', self.handle_update, methods=['POST'])
        self.app.add_url_rule('/poll/<group_id>', 'poll', self.handle_poll, methods=['GET'])

    def run(self):
        self.logger.info("Running server on port 2547")
        self.db_manager.init_db()
        serve(self.app, host='0.0.0.0', port=2547)

    def handle_register(self):
        data = request.json
        group_id = data.get('group_id')
        if group_id not in self.clients:
            self.clients[group_id] = []
        self.clients[group_id].append(request.remote_addr)
        self.logger.info(f"Client registered: {request.remote_addr} in group {group_id}")
        return jsonify({"status": "registered"}), 200

    def handle_update(self):
        data = request.json
        group_id = data.get('group_id')
        content = data.get('content')
        sender_ip = request.remote_addr
        
        self.db_manager.record_message(group_id, content, sender_ip)
        self.logger.info(f"Message received from {sender_ip} in group {group_id}")
        
        if group_id in self.clients:
            for client in self.clients[group_id]:
                if client != sender_ip:
                    if group_id not in self.pending_updates:
                        self.pending_updates[group_id] = {}
                    self.pending_updates[group_id][client] = content
        return jsonify({"status": "updated"}), 200

    def handle_poll(self, group_id):
        client_ip = request.remote_addr
        if group_id in self.pending_updates and client_ip in self.pending_updates[group_id]:
            content = self.pending_updates[group_id].pop(client_ip)
            if not self.pending_updates[group_id]:
                del self.pending_updates[group_id]
            return jsonify({"content": content}), 200
        return jsonify({"content": None}), 200

def create_server(logger):
    return Server(logger)
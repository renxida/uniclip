from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from waitress import serve
import uvicorn
import sqlite3
from datetime import datetime

class RegisterData(BaseModel):
    group_id: str
    client_id: str

class UpdateData(BaseModel):
    group_id: str
    client_id: str
    content: str
    timestamp: int

class DatabaseManager:
    def __init__(self, db_name='uniclip.db'):
        self.db_name = db_name
        self.conn = None
        self.cursor = None

    def init_db(self):
        self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id TEXT,
                content TEXT,
                client_id TEXT,
                timestamp INTEGER
            )
        ''')
        self.conn.commit()

    def record_message(self, group_id, content, client_id, timestamp):
        self.cursor.execute('''
            INSERT INTO messages (group_id, content, client_id, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (group_id, content, client_id, timestamp))
        self.conn.commit()

    def get_latest_message(self, group_id):
        self.cursor.execute('''
            SELECT * FROM messages
            WHERE group_id = ?
            ORDER BY timestamp DESC
            LIMIT 1
        ''', (group_id,))
        return self.cursor.fetchone()

class Server:
    def __init__(self, logger):
        self.logger = logger
        self.db_manager = DatabaseManager()
        self.clients = {}
        self.app = FastAPI()
        self.setup_routes()
        self.logger.info("Server initialized")

    def setup_routes(self):
        self.app.post("/register")(self.handle_register)
        self.app.post("/update")(self.handle_update)
        self.app.get("/poll/{group_id}/{client_id}")(self.handle_poll)
        self.logger.info("Routes set up")

    def run(self):
        self.logger.info("Running server on port 2547")
        self.db_manager.init_db()
        self.logger.info("Database initialized")
        uvicorn.run(self.app, host="0.0.0.0", port=2547)

    async def handle_register(self, data: RegisterData):
        group_id = data.group_id
        client_id = data.client_id
        self.logger.debug(f"Received registration request for group: {group_id}, client: {client_id}")
        if group_id not in self.clients:
            self.clients[group_id] = []
            self.logger.debug(f"Created new group: {group_id}")
        self.clients[group_id].append(client_id)
        self.logger.info(f"Client registered: {client_id} in group {group_id}")
        self.logger.debug(f"Current clients in group {group_id}: {self.clients[group_id]}")
        return {"status": "registered"}

    async def handle_update(self, data: UpdateData):
        group_id = data.group_id
        client_id = data.client_id
        content = data.content
        timestamp = data.timestamp
        
        self.logger.debug(f"Received update request from {client_id} for group: {group_id}")
        self.db_manager.record_message(group_id, content, client_id, timestamp)
        self.logger.info(f"Message received from {client_id} in group {group_id}")
        self.logger.debug(f"Message content: {content[:50]}... Timestamp: {timestamp}")
        
        return {"status": "updated"}

    async def handle_poll(self, group_id: str, client_id: str, hash: str = Query(...), timestamp: int = Query(...)):
        self.logger.debug(f"Received poll request from {client_id} for group: {group_id}")
        
        latest_message = self.db_manager.get_latest_message(group_id)
        
        if latest_message:
            _, _, content, _, server_timestamp = latest_message
            if server_timestamp > timestamp:
                self.logger.info(f"Sending update to client {client_id} in group {group_id}")
                self.logger.debug(f"Update content: {content[:50]}... Timestamp: {server_timestamp}")
                return {"status": "update_needed", "content": content, "timestamp": server_timestamp}
        
        self.logger.debug(f"No update needed for client {client_id} in group {group_id}")
        return {"status": "no_update"}

def create_server(logger):
    return Server(logger)

if __name__ == "__main__":
    import logging
    logger = logging.getLogger("uniclip")
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    server = create_server(logger)
    server.run()
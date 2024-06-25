from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from waitress import serve
from database_manager import DatabaseManager
import uvicorn

class RegisterData(BaseModel):
    group_id: str
    client_id: str

class UpdateData(BaseModel):
    group_id: str
    client_id: str
    content: str

class Server:
    def __init__(self, logger):
        self.logger = logger
        self.db_manager = DatabaseManager()
        self.clients = {}
        self.pending_updates = {}
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
        
        self.logger.debug(f"Received update request from {client_id} for group: {group_id}")
        self.db_manager.record_message(group_id, content, client_id)
        self.logger.info(f"Message received from {client_id} in group {group_id}")
        self.logger.debug(f"Message content: {content[:50]}...") # Log first 50 characters of content
        
        if group_id in self.clients:
            self.logger.debug(f"Processing update for clients in group {group_id}")
            for client in self.clients[group_id]:
                if client != client_id:
                    if group_id not in self.pending_updates:
                        self.pending_updates[group_id] = {}
                    self.pending_updates[group_id][client] = content
                    self.logger.debug(f"Queued update for client: {client}")
        else:
            self.logger.warning(f"Received update for non-existent group: {group_id}")
        
        self.logger.debug(f"Current pending updates: {self.pending_updates}")
        return {"status": "updated"}

    async def handle_poll(self, group_id: str, client_id: str):
        self.logger.debug(f"Received poll request from {client_id} for group: {group_id}")
        
        if group_id in self.pending_updates and client_id in self.pending_updates[group_id]:
            content = self.pending_updates[group_id].pop(client_id)
            self.logger.info(f"Sending update to client {client_id} in group {group_id}")
            self.logger.debug(f"Update content: {content[:50]}...") # Log first 50 characters of content
            if not self.pending_updates[group_id]:
                del self.pending_updates[group_id]
                self.logger.debug(f"Removed empty pending updates for group: {group_id}")
            return {"content": content}
        else:
            self.logger.debug(f"No pending updates for client {client_id} in group {group_id}")
            return {"content": None}

def create_server(logger):
    return Server(logger)

import json
from fastapi import WebSocket
from typing import List, Dict

from app.file_watcher import FileWatcherManager


class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()

    async def disconnect(self, websocket: WebSocket):
        for key, connections in self.active_connections.items():
            if websocket in connections:
                connections.remove(websocket)
                if not connections:
                    del self.active_connections[key]
                break

    async def subscribe(self, websocket: WebSocket, proposal: str, file_type: str):
        # key = f"{proposal}/{file_type}"
        key = "/Users/teodoro/context.py"
        if key not in self.active_connections:
            self.active_connections[key] = []
        self.active_connections[key].append(websocket)

        await websocket.send_json({
            "message": 'Subscribed',
            "proposal": proposal,
            "file_type": file_type
        })


class WebSocketHandler:
    def __init__(self, websocket: WebSocket, ws_manager: WebSocketManager, fw_manager: FileWatcherManager):
        self.websocket = websocket
        self.ws_manager = ws_manager
        self.fw_manager = fw_manager

    async def handle_event(self, event, data):
        handler = getattr(self, f"handle_{event}", self.handle_unknown)
        await handler(data)

    async def handle_ping(self, data):
        await self.websocket.send_text("pong")

    async def handle_unknown(self, data):
        await self.websocket.send_text("Unknown event")

    async def handle_subscribe(self, data):
        file_path = '/Users/teodoro/context.py'

        fw_status = self.fw_manager.watcher_status(file_path)

        if not fw_status:
            self.fw_manager.start_watcher(
                file_path=file_path,
                on_change=self.on_change)

        await self.ws_manager.subscribe(self.websocket, data.get("proposal"), data.get("file_name"))

    async def on_change(self, a, b, c):
        print("On_change triggered")
        print(a in self.ws_manager.active_connections)
        if a in self.ws_manager.active_connections:
            for connection in self.ws_manager.active_connections[a]:
                await connection.send_text(json.dumps({"checksum": c}))

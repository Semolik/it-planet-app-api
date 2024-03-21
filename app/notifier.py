import asyncio
import json
from typing import Dict
import uuid
from fastapi import WebSocket
from typing import Dict


class Notifier:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.connections = {}
            cls._instance.is_ready = False
            cls._instance.prefix = ""
            cls._instance.message_queue = []
        return cls._instance

    async def setup(self):
        if self.is_ready:
            return
        self.is_ready = True

    async def push(self, user_id: uuid.UUID, data: Dict):
        user_id_str = str(user_id)
        if user_id_str not in self.connections:
            await self.create_channel(user_id_str)
        self.message_queue.append((user_id_str, data))
        await self._notify(user_id_str)

    async def connect(self, user_id: uuid.UUID, websocket: WebSocket):
        user_id_str = str(user_id)
        if user_id_str not in self.connections:
            await self.create_channel(user_id_str)
        await websocket.accept()
        self.connections[user_id_str].append(websocket)

    async def create_channel(self, user_id: str):
        self.connections[user_id] = []

    def remove(self, user_id: uuid.UUID, websocket: WebSocket):
        user_id_str = str(user_id)
        self.connections[user_id_str].remove(websocket)

    async def _notify(self, user_id: str):
        if user_id in self.connections:
            living_connections = []
            while len(self.connections[user_id]) > 0:
                websocket = self.connections[user_id].pop()
                if self.message_queue:
                    data = json.dumps(self.message_queue.pop(0))
                    await websocket.send_text(data)
                    living_connections.append(websocket)
            self.connections[user_id] = living_connections


notifier = Notifier()


def get_notifier(prefix):

    def get_with_prefix() -> Notifier:
        notifier.prefix = prefix
        return notifier
    return get_with_prefix

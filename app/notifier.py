import asyncio
import json
from os import getenv
from typing import Dict
import uuid
from aio_pika import IncomingMessage, Message, connect
from fastapi import WebSocket
from typing import Dict


class Notifier:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.connections = {}
            cls._instance.is_ready = False
            cls._instance.channel = None
            cls._instance.prefix = ""
        return cls._instance

    async def setup(self):
        if self.is_ready:
            return
        self.rmq_conn = await connect(
            f"amqp://{getenv('RABBITMQ_DEFAULT_USER')}:{getenv('RABBITMQ_DEFAULT_PASS')}@rabbitmq/",
            loop=asyncio.get_running_loop()
        )
        self.channel = await self.rmq_conn.channel()
        self.is_ready = True

    async def push(self, user_id: uuid.UUID, data: Dict):
        user_id_str = str(user_id)
        if user_id_str not in self.connections:
            await self.create_channel(user_id_str)
        queue_name = f"queue_{user_id_str}"
        json_data = json.dumps(data)
        await self.channel.default_exchange.publish(
            Message(json_data.encode("utf-8")),
            routing_key=queue_name,
        )

    async def connect(self, user_id: uuid.UUID, websocket: WebSocket):
        user_id_str = str(user_id)
        if user_id_str not in self.connections:
            await self.create_channel(user_id_str)
        await websocket.accept()
        self.connections[user_id_str].append(websocket)

    async def create_channel(self, user_id: str):
        self.connections[user_id] = []
        queue_name = f"queue_{user_id}"
        queue = await self.channel.declare_queue(queue_name)
        await self.consume_messages(user_id, queue)

    async def consume_messages(self, user_id: str, queue):
        async for message in queue:
            await self._notify(user_id, message)
            await message.ack()

    def remove(self, user_id: uuid.UUID, websocket: WebSocket):
        user_id_str = str(user_id)
        self.connections[user_id_str].remove(websocket)

    async def _notify(self, user_id: str, message: IncomingMessage):
        living_connections = []
        while len(self.connections[user_id]) > 0:
            websocket = self.connections[user_id].pop()
            data = json.loads(message.body.decode("utf-8"))
            await websocket.send_text(data)
            living_connections.append(websocket)
        self.connections[user_id] = living_connections


notifier = Notifier()


def get_notifier(prefix):

    def get_with_prefix():
        notifier.prefix = prefix
        return notifier
    return get_with_prefix

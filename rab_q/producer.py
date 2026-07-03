import aio_pika
from typing import Any
from .serializers import Serializer, JsonSerializer
from .connection import ConnectionManager

class Producer:
    def __init__(self, conn_manager: ConnectionManager, serializer: Serializer = None):
        self.conn_manager = conn_manager
        self.serializer = serializer or JsonSerializer()

    async def publish(self, queue_name: str, data: Any, headers: dict | None = None, **kwargs):
        """Publish a single message to a queue."""
        channel = await self.conn_manager.get_channel()
        payload = self.serializer.serialize(data)
        
        message = aio_pika.Message(
            body=payload,
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            headers=headers or {}
        )
        
        # Ensure queue exists (optional, but good practice for zero-config)
        await channel.declare_queue(queue_name, durable=True)
        
        exchange = channel.default_exchange
        await exchange.publish(message, routing_key=queue_name)

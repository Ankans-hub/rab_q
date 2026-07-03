from aio_pika.abc import AbstractChannel

class QueueManager:
    """Manages queue declarations, bindings, and deletions."""
    def __init__(self, channel: AbstractChannel):
        self.channel = channel
        
    async def declare_queue(self, name: str, durable: bool = True, **kwargs):
        """Declare a queue."""
        queue = await self.channel.declare_queue(name, durable=durable, **kwargs)
        return queue
        
    async def delete_queue(self, name: str):
        """Delete a queue."""
        await self.channel.queue_delete(name)

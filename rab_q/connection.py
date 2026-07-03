import aio_pika
import logging
from .exceptions import ConnectionError

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manages the RabbitMQ connection and channel pool."""
    def __init__(self, url: str):
        self.url = url
        self.connection = None
        self.channel = None

    async def connect(self):
        """Establish the robust connection to RabbitMQ."""
        try:
            logger.info("Connecting to RabbitMQ...")
            self.connection = await aio_pika.connect_robust(self.url)
            self.channel = await self.connection.channel()
            logger.info("Connected successfully.")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise ConnectionError(f"Failed to connect: {e}")

    async def get_channel(self) -> aio_pika.abc.AbstractChannel:
        """Get the default channel, connecting if necessary."""
        if not self.channel or self.channel.is_closed:
            await self.connect()
        return self.channel

    async def close(self):
        """Close the connection gracefully."""
        if self.connection and not self.connection.is_closed:
            await self.connection.close()
            logger.info("Connection closed.")

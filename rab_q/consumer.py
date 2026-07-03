import aio_pika
import asyncio
import logging
from typing import Callable
from .serializers import Serializer, JsonSerializer
from .connection import ConnectionManager
from .producer import Producer
from .retry import RetryEngine

logger = logging.getLogger(__name__)

class Consumer:
    def __init__(self, conn_manager: ConnectionManager, producer: Producer, retry_engine: RetryEngine, enable_dlq: bool = True, serializer: Serializer = None):
        self.conn_manager = conn_manager
        self.producer = producer
        self.retry_engine = retry_engine
        self.enable_dlq = enable_dlq
        self.serializer = serializer or JsonSerializer()

    async def consume(self, queue_name: str, callback: Callable):
        """Consume messages from a queue and pass them to a callback with retry and DLQ logic."""
        channel = await self.conn_manager.get_channel()
        await channel.set_qos(prefetch_count=10)
        
        queue = await channel.declare_queue(queue_name, durable=True)
        
        async def on_message(message: aio_pika.IncomingMessage):
            # We process the message manually so we can ack/nack based on retry logic
            try:
                payload = self.serializer.deserialize(message.body)
                
                if asyncio.iscoroutinefunction(callback):
                    await callback(payload)
                else:
                    await asyncio.to_thread(callback, payload)
                    
                # Success: Acknowledge the message
                await message.ack()
                
            except Exception as e:
                logger.error(f"Error processing message in {queue_name}: {e}")
                await self._handle_failure(channel, message, queue_name)

        await queue.consume(on_message)
        logger.info(f"Started consuming from queue: {queue_name}")

    async def _handle_failure(self, channel: aio_pika.abc.AbstractChannel, message: aio_pika.IncomingMessage, queue_name: str):
        headers = message.headers or {}
        attempt = headers.get('x-retry-count', 0)
        
        if self.retry_engine.should_retry(attempt):
            # 1. Increment attempt
            next_attempt = attempt + 1
            headers['x-retry-count'] = next_attempt
            
            # 2. Calculate delay
            delay_ms = self.retry_engine.get_delay(next_attempt)
            delay_queue_name = f"{queue_name}.delay.{delay_ms}"
            
            logger.info(f"Retrying message from {queue_name} (Attempt {next_attempt}). Delaying for {delay_ms}ms.")
            
            # 3. Setup Delay Queue
            # This queue will hold the message for `delay_ms`, then dead-letter it back to the original queue.
            await channel.declare_queue(
                delay_queue_name, 
                durable=True,
                arguments={
                    'x-dead-letter-exchange': '',
                    'x-dead-letter-routing-key': queue_name,
                    'x-message-ttl': delay_ms
                }
            )
            
            # 4. Re-publish to the Delay Queue (not the original queue)
            # We construct a new message based on the old one. We serialize the original body directly?
            # No, `producer.publish` expects deserialized data to serialize it. Wait, it's better to publish raw bytes.
            # Let's bypass `producer.publish` to avoid re-serializing, or we can just deserialize first.
            # But we already deserialized it inside `try`, wait, what if deserialization failed?
            # Let's publish raw bytes using aio_pika directly to ensure we don't lose data.
            
            retry_message = aio_pika.Message(
                body=message.body,
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                headers=headers
            )
            await channel.default_exchange.publish(retry_message, routing_key=delay_queue_name)
            
            # 5. Ack the original message so it doesn't get requeued immediately
            await message.ack()
            
        else:
            # Retries exhausted -> DLQ
            logger.warning(f"Retries exhausted for message in {queue_name}.")
            if self.enable_dlq:
                dlq_name = f"{queue_name}.dlq"
                logger.info(f"Moving message to DLQ: {dlq_name}")
                await channel.declare_queue(dlq_name, durable=True)
                
                dlq_message = aio_pika.Message(
                    body=message.body,
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                    headers=headers
                )
                await channel.default_exchange.publish(dlq_message, routing_key=dlq_name)
                
            # Ack the original message to remove it from the main queue
            await message.ack()

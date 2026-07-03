import logging
from typing import Any, Callable

from .config import load_config
from .license import validate_license
from .loop import BackgroundLoop
from .connection import ConnectionManager
from .producer import Producer
from .consumer import Consumer
from .serializers import JsonSerializer

# Configure default logger for the SDK
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Messaging:
    """
    Main entry point for the rab_q Enterprise Messaging SDK.
    Provides a synchronous, easy-to-use API while managing an async connection underneath.
    """
    
    def __init__(self, api_key: str | None = None, **kwargs):
        # 1. Load Configuration
        if api_key:
            kwargs['api_key'] = api_key
            
        self.config = load_config(config_dict=kwargs)
        
        # 2. Validate License
        validate_license(self.config.api_key)
        
        # 3. Initialize Background Loop
        self._loop = BackgroundLoop()
        
        # 4. Initialize Connection Manager
        self._conn_manager = ConnectionManager(self.config.rabbitmq_url)
        
        # 5. Connect synchronously
        logger.info("Initializing Enterprise MQ SDK...")
        self._loop.run_coroutine(self._conn_manager.connect())
        
        # 6. Initialize Core Components
        self.serializer = JsonSerializer()
        self.producer = Producer(self._conn_manager, self.serializer)
        
        from .retry import RetryEngine
        self.retry_engine = RetryEngine(
            limit=self.config.retry_limit, 
            delay_ms=self.config.retry_delay_ms
        )
        
        self.consumer = Consumer(
            conn_manager=self._conn_manager, 
            producer=self.producer,
            retry_engine=self.retry_engine,
            enable_dlq=self.config.enable_dlq,
            serializer=self.serializer
        )

    def shutdown(self):
        """Close connection and shutdown the background loop gracefully."""
        self._loop.run_coroutine(self._conn_manager.close())
        self._loop.shutdown()
        logger.info("SDK shut down gracefully.")
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()

    def publish(self, queue: str, data: Any, **kwargs):
        """Publish a message to a queue."""
        self._loop.run_coroutine(self.producer.publish(queue, data, **kwargs))

    def consume(self, queue: str, callback: Callable, **kwargs):
        """Consume messages from a queue."""
        self._loop.run_coroutine(self.consumer.consume(queue, callback))

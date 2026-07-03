import logging
from typing import Any, Callable

from .config import load_config
from .license import validate_license
from .loop import BackgroundLoop
from .connection import ConnectionManager
from .producer import Producer
from .consumer import Consumer
from .serializers import JsonSerializer
from .tasks import TaskRegistry

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
        
        # 7. Initialize Task Registry
        self.task_registry = TaskRegistry()

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

    def task(self, name: str):
        """Decorator to register a task function."""
        def decorator(func):
            self.task_registry.register(name, func)
            return func
        return decorator

    def send_task(self, name: str, queue: str, args: list = None, kwargs: dict = None, delay_ms: int = 0, **publish_kwargs):
        """Send a task to a specific queue, optionally with a delay."""
        payload = {
            "task_name": name,
            "args": args or [],
            "kwargs": kwargs or {}
        }
        
        if delay_ms and delay_ms > 0:
            self._loop.run_coroutine(self.producer.publish_delayed(queue, payload, delay_ms, **publish_kwargs))
        else:
            self._loop.run_coroutine(self.producer.publish(queue, payload, **publish_kwargs))
            
    def consume_tasks(self, queue: str, **kwargs):
        """Start consuming tasks from the specified queue."""
        def task_worker(data: dict):
            if not isinstance(data, dict):
                logger.error(f"Received invalid task payload: {data}. Expected dict.")
                return
                
            task_name = data.get("task_name")
            args = data.get("args", [])
            task_kwargs = data.get("kwargs", {})
            
            if not task_name:
                logger.error("Received task payload without 'task_name'. Dropping.")
                return
                
            logger.info(f"Executing task '{task_name}'")
            self.task_registry.execute(task_name, *args, **task_kwargs)
            
        self.consume(queue, callback=task_worker, **kwargs)

import asyncio
import threading
import concurrent.futures

class BackgroundLoop:
    """
    Manages a background asyncio event loop running in a separate thread.
    This allows exposing a synchronous API while using async aio-pika internally.
    """
    def __init__(self):
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def _run_loop(self):
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    def run_coroutine(self, coro):
        """Run a coroutine in the background loop and wait for the result."""
        future = concurrent.futures.Future()

        async def wrapper():
            try:
                result = await coro
                future.set_result(result)
            except Exception as e:
                future.set_exception(e)

        asyncio.run_coroutine_threadsafe(wrapper(), self._loop)
        return future.result()

    def shutdown(self):
        """Stop the event loop and wait for the thread to exit."""
        if self._loop.is_running():
            self._loop.call_soon_threadsafe(self._loop.stop)
        self._thread.join()

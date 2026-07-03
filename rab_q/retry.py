class RetryEngine:
    def __init__(self, limit: int = 3, delay_ms: int = 5000):
        self.limit = limit
        self.delay_ms = delay_ms
        
    def should_retry(self, attempt: int) -> bool:
        return attempt < self.limit
        
    def get_delay(self, attempt: int) -> int:
        """Returns the TTL in milliseconds for the delay queue."""
        # For v1.0, we just use a fixed delay. 
        # In the future, this can be calculated exponentially (e.g. delay_ms * 2^attempt)
        return self.delay_ms

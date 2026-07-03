import json
from typing import Any

class Serializer:
    """Base serializer interface."""
    def serialize(self, data: Any) -> bytes:
        raise NotImplementedError
        
    def deserialize(self, data: bytes) -> Any:
        raise NotImplementedError

class JsonSerializer(Serializer):
    """JSON serializer implementation."""
    def serialize(self, data: Any) -> bytes:
        return json.dumps(data).encode('utf-8')
        
    def deserialize(self, data: bytes) -> Any:
        return json.loads(data.decode('utf-8'))

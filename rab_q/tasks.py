import logging
from typing import Callable, Dict, Any, Optional

logger = logging.getLogger(__name__)

class TaskRegistry:
    """
    Holds a mapping of task names to Python functions for execution.
    """
    def __init__(self):
        self._tasks: Dict[str, Callable] = {}

    def register(self, name: str, func: Callable):
        """Register a function under a specific task name."""
        if name in self._tasks:
            logger.warning(f"Task '{name}' is already registered. Overwriting.")
        self._tasks[name] = func
        logger.debug(f"Registered task: '{name}'")

    def get_task(self, name: str) -> Optional[Callable]:
        """Retrieve a function by its task name."""
        return self._tasks.get(name)

    def execute(self, name: str, *args, **kwargs) -> Any:
        """Execute a registered task by name with the given arguments."""
        func = self.get_task(name)
        if not func:
            logger.error(f"Task '{name}' not found in registry.")
            raise ValueError(f"Task '{name}' not registered.")
        
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.exception(f"Error executing task '{name}': {e}")
            raise

import pytest
from unittest.mock import MagicMock
from rab_q.tasks import TaskRegistry

def test_task_registry_registration():
    registry = TaskRegistry()
    
    def my_task(x, y):
        return x + y
        
    registry.register("add", my_task)
    
    assert registry.get_task("add") == my_task
    assert registry.execute("add", 2, 3) == 5

def test_task_registry_execute_not_found():
    registry = TaskRegistry()
    with pytest.raises(ValueError, match="Task 'missing' not registered"):
        registry.execute("missing")

def test_task_registry_exception():
    registry = TaskRegistry()
    
    def broken_task():
        raise RuntimeError("Fail")
        
    registry.register("broken", broken_task)
    
    with pytest.raises(RuntimeError, match="Fail"):
        registry.execute("broken")

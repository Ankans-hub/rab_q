from rab_q.retry import RetryEngine

def test_retry_engine_should_retry():
    engine = RetryEngine(limit=3)
    assert engine.should_retry(0) is True
    assert engine.should_retry(1) is True
    assert engine.should_retry(2) is True
    assert engine.should_retry(3) is False

def test_retry_engine_delay():
    engine = RetryEngine(delay_ms=1000)
    assert engine.get_delay(1) == 1000
    assert engine.get_delay(2) == 1000

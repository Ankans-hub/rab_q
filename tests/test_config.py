from rab_q.config import load_config, MessagingConfig

def test_load_config_defaults():
    config = load_config()
    assert config.rabbitmq_url == "amqp://guest:guest@localhost/"
    assert config.retry_limit == 3
    assert config.retry_delay_ms == 5000
    assert config.enable_dlq is True

def test_load_config_with_dict():
    config = load_config(config_dict={'retry_limit': 10, 'enable_dlq': False})
    assert config.retry_limit == 10
    assert config.enable_dlq is False
    assert config.rabbitmq_url == "amqp://guest:guest@localhost/"

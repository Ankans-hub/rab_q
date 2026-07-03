from pydantic_settings import BaseSettings
from pydantic import Field
import yaml
import os

class MessagingConfig(BaseSettings):
    api_key: str | None = None
    rabbitmq_url: str = Field(default="amqp://guest:guest@localhost/")
    retry_limit: int = Field(default=3)
    retry_delay_ms: int = Field(default=5000) # Fixed delay for v1.0
    enable_dlq: bool = Field(default=True)
    notification: bool = Field(default=False)
    
    # Prefix for multi-tenancy (to be used later)
    tenant_prefix: str = Field(default="")

    class Config:
        env_prefix = "RAB_Q_"
        env_file = ".env"

def load_config(config_dict: dict | None = None, yaml_path: str | None = None) -> MessagingConfig:
    """Load configuration in priority: Python Dict -> YAML -> Environment/Defaults"""
    # 1. Start with env vars / defaults
    config_kwargs = {}
    
    # 2. YAML file (if provided)
    if yaml_path and os.path.exists(yaml_path):
        with open(yaml_path, 'r') as f:
            yaml_data = yaml.safe_load(f)
            if yaml_data:
                config_kwargs.update(yaml_data)
                
    # 3. Python dictionary (highest priority)
    if config_dict:
        config_kwargs.update(config_dict)
        
    return MessagingConfig(**config_kwargs)

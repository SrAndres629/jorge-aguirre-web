
import os
import logging
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    evolution_api_url: str = "http://evolution_api:8080"
    evolution_api_key: str = "B89599B2-37E4-4DCA-92D3-87F8674C7D69"
    log_level: str = "INFO"

    class Config:
        env_file = ".env"

settings = Settings()

# Logging Configuration
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def get_logger(name: str):
    return logging.getLogger(f"EvoMCP.{name}")

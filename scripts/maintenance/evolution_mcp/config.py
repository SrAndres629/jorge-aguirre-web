
import logging
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator

class Settings(BaseSettings):
    evolution_api_url: str = "http://evolution_api:8080"
    evolution_api_key: str = Field(..., env="EVOLUTION_API_KEY")
    log_level: str = "INFO"

    @field_validator("evolution_api_key")
    def validate_key(cls, v):
        if not v or v == "CHANGE_ME":
             raise ValueError("Evolution API Key must be set in .env")
        return v

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

# Logging Configuration
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def get_logger(name: str):
    return logging.getLogger(f"EvoMCP.{name}")

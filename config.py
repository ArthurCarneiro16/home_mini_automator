import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    api_secret_token: str
    host: str = "0.0.0.0"
    port: int = 8000
    cast_name: str = "Setup"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

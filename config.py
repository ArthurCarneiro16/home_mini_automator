from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    api_secret_token: str
    host: str = "0.0.0.0"
    port: int = 8000
    cast_name: str = "Setup"
    sinric_app_key: str = ""
    sinric_app_secret: str = ""
    sinric_id_spotify: str = ""
    sinric_id_pc: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
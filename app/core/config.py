"""Core configuration and settings for Poll Service."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SERVICE_NAME: str = "Poll Service"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8002

    DATABASE_URL: str = "mysql+pymysql://poll_admin:poll_password@localhost:3308/poll_db"
    USER_SERVICE_URL: str = "http://localhost:8001/api/v1"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

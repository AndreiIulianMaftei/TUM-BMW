from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    mongodb_uri: str
    database_name: str
    secret_key: str
    debug: bool = False
    allowed_hosts: str = "localhost,127.0.0.1"
    max_file_size: int = 10485760
    upload_dir: str = "uploads"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()

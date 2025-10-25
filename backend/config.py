from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )
    
    mongodb_uri: str
    database_name: str
    gemini_api_key: str
    openai_api_key: str
    secret_key: str
    debug: bool = True


@lru_cache()
def get_settings():
    return Settings()

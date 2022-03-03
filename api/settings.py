from functools import lru_cache
from pydantic import BaseSettings, SecretStr


class Settings(BaseSettings):
    db_url: str = "no db loaded"
    api_tokens: list[SecretStr] = {"no api tokens loaded"}

    class Config:
        env_file = ".env"


@lru_cache
def get_settings():
    return Settings()

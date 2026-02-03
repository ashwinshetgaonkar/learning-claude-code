from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os


class Settings(BaseSettings):
    groq_api_key: str = ""
    tavily_api_key: str = ""
    youtube_api_key: str = ""
    database_url: str = "sqlite+aiosqlite:///./ai_news.db"
    cors_origins: str = "http://localhost:5173"
    reddit_client_id: str = ""
    reddit_client_secret: str = ""

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

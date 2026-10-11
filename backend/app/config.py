from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    ENVIRONMENT: str = "development"
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000", "*"]

    # Voice Agent Identity
    COMPANY_NAME: str = "Home Credit India"
    AGENT_NAME: str = "Pooja"
    AGENT_GENDER: str = "female"
    DEFAULT_LANGUAGE: str = "English"

    # Voice Platforms
    VOICE_PLATFORM: str = "retell"
    RETELL_API_KEY: str = ""
    RETELL_AGENT_ID: str = ""
    RETELL_WEBHOOK_SECRET: str = ""

    BOLNA_API_KEY: str = ""
    BOLNA_AGENT_ID: str = ""

    # Optional LLM
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()

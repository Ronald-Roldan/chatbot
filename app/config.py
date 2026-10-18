from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql://thesis:thesis@localhost:5432/electoral_rag"
    ollama_base_url: str = "http://localhost:11434"
    embedding_model: str = "jina/jina-embeddings-v2-base-es"
    generation_model: str = "qwen2.5:3b"
    top_k: int = 5
    whatsapp_verify_token: str = ""
    whatsapp_access_token: str = ""
    whatsapp_phone_number_id: str = ""
    whatsapp_app_secret: str = ""
    session_secret: str = "change-this-before-whatsapp-testing"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def settings() -> Settings:
    return Settings()

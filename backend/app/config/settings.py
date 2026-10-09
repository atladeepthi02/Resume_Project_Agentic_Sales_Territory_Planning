from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"
    database_url: str = "sqlite:///./sales_agent.db"
    redis_url: str = "redis://localhost:6379/0"
    chroma_persist_directory: str = "./.chroma"
    cors_origins: str = "http://localhost:3000"
    # FR-3: records older than this many days are flagged as stale.
    data_freshness_threshold_days: int = 30


settings = Settings()

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List, Optional


class Settings(BaseSettings):
    APP_NAME: str = "PAIOS - Platform for AI Orchestration & Self-Healing"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    SECRET_KEY: str = "paios-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    DATABASE_URL: str = "postgresql+asyncpg://paios:paios@postgres:5432/paios"
    NEO4J_URI: str = "bolt://neo4j:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "paios-neo4j"
    REDIS_URL: str = "redis://redis:6379/0"
    CELERY_BROKER_URL: str = "redis://redis:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/2"
    KAFKA_BOOTSTRAP_SERVERS: str = "kafka:9092"
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    DEFAULT_LLM_MODEL: str = "gpt-4o"
    LLM_TIMEOUT: int = 120
    LLM_MAX_RETRIES: int = 3
    PROMETHEUS_PORT: int = 9090
    JAEGER_ENDPOINT: str = "http://jaeger:14268/api/traces"
    LOG_LEVEL: str = "INFO"
    SELF_HEALING_ENABLED: bool = True
    SELF_HEALING_THRESHOLD: float = 0.75
    MAX_HEALING_ATTEMPTS: int = 3
    RELEASE_ANALYSIS_ENABLED: bool = True
    ROLLBACK_THRESHOLD: float = 0.05
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "https://paios.io"]

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()

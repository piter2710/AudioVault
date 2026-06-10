from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    # ── App ───────────────────────────────────────────────
    APP_NAME: str = "MyApp"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development | staging | production

    # ── API ───────────────────────────────────────────────
    API_V1_PREFIX: str = "/api/v1"
    # SECRET_KEY: str = "changeme"           # used for signing tokens etc.
    # ALLOWED_HOSTS: list[str] = ["*"]

    # ── Database ──────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@db:5432/database"
    SYNC_DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@db:5432/database"
    # DB_POOL_SIZE: int = 10
    # DB_MAX_OVERFLOW: int = 20
    # DB_POOL_TIMEOUT: int = 30

    # ── Redis ─────────────────────────────────────────────
    REDIS_URL: str = "redis://redis:6379/0"
    REDIS_PASSWORD: str = ""
    REDIS_TTL: int = 3600                  # default cache TTL in seconds

    # ── Celery ────────────────────────────────────────────
    CELERY_BROKER_URL: str = "redis://redis:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/2"
    CELERY_TASK_SERIALIZER: str = "json"
    CELERY_RESULT_SERIALIZER: str = "json"

    # ── Auth / JWT ────────────────────────────────────────
    # JWT_SECRET_KEY: str = "changeme"
    # JWT_ALGORITHM: str = "HS256"
    # ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    # REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── CORS ──────────────────────────────────────────────
    # CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    # CORS_ALLOW_CREDENTIALS: bool = True
    # CORS_ALLOW_METHODS: list[str] = ["*"]
    # CORS_ALLOW_HEADERS: list[str] = ["*"]

    # ── Email (SMTP) ──────────────────────────────────────
    # SMTP_HOST: str = "smtp.gmail.com"
    # SMTP_PORT: int = 587
    # SMTP_USER: str = ""
    # SMTP_PASSWORD: str = ""
    # EMAILS_FROM_EMAIL: str = "noreply@myapp.com"
    # EMAILS_FROM_NAME: str = "MyApp"

    # ── Storage (S3 / R2 / MinIO) ────────────────────────
    # S3_BUCKET: str = ""
    # S3_REGION: str = "eu-central-1"
    # S3_ACCESS_KEY: str = ""
    # S3_SECRET_KEY: str = ""
    # S3_ENDPOINT_URL: str = ""            # for MinIO / Cloudflare R2

    # ── OAuth / Social login ──────────────────────────────
    # GOOGLE_CLIENT_ID: str = ""
    # GOOGLE_CLIENT_SECRET: str = ""
    # GITHUB_CLIENT_ID: str = ""
    # GITHUB_CLIENT_SECRET: str = ""

    # ── Sentry / Observability ────────────────────────────
    # SENTRY_DSN: str = ""
    # LOG_LEVEL: str = "INFO"

    # ── Rate limiting ─────────────────────────────────────
    # RATE_LIMIT_PER_MINUTE: int = 60

    # ── LLM / AI (Ollama, OpenAI, etc.) ──────────────────
    # OLLAMA_HOST: str = "http://localhost:11434"
    # OLLAMA_MODEL: str = "mistral-nemo:12b"
    # OLLAMA_TEMPERATURE: float = 0.1
    # OPENAI_API_KEY: str = ""
    # OPENAI_MODEL: str = "gpt-4o"

    


settings = Settings()

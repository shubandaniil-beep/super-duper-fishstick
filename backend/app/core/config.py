from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost:5432/kindermanager"
    SECRET_KEY: str = "change_me_to_32_char_secret_key_!"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    TELEGRAM_BOT_TOKEN: str = ""
    WEBHOOK_URL: str = ""
    ENVIRONMENT: str = "development"

    model_config = {"env_file": ".env"}


settings = Settings()

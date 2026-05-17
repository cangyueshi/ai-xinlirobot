from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./ai_psy_counselor.db"

    SECRET_KEY: str = "change-me-to-a-random-secret-key-in-production"
    ADMIN_SECRET_KEY: str = "change-me-admin-secret-key-in-production"
    ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    MINI_PROGRAM_TOKEN_EXPIRE_MINUTES: int = 10080
    ADMIN_TOKEN_EXPIRE_MINUTES: int = 480

    DEEPSEEK_API_KEY: str = ""

    SUPER_ADMIN_USERNAME: str = "admin"
    SUPER_ADMIN_PASSWORD: str = "admin123456"
    SUPER_ADMIN_EMAIL: str = ""

    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
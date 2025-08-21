from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings using Pydantic Settings."""
    
    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://user:password@localhost:5432/auth_db",
        alias="DATABASE_URL"
    )
    
    # Security
    secret_key: str = Field(
        default="your-super-secret-key-change-in-production",
        alias="SECRET_KEY"
    )
    algorithm: str = Field(default="HS256", alias="ALGORITHM")
    access_token_expire_minutes: int = Field(default=15, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, alias="REFRESH_TOKEN_EXPIRE_DAYS")
    
    # CORS
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        alias="CORS_ORIGINS"
    )
    
    # Application
    app_name: str = Field(default="Auth Service", alias="APP_NAME")
    debug: bool = Field(default=False, alias="DEBUG")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
import os
import secrets
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, BaseSettings, EmailStr, HttpUrl, PostgresDsn, validator


class Settings(BaseSettings):
    PROJECT_NAME: Optional[str] = "OSINTBuddy"
    PROJECT_DESCRIPTION: Optional[
        str
    ] = "Analyze, collect, and store OSINT data"

    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ADMIN_BACKEND_SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = os.getenv('BACKEND_CORS_ORIGINS')

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        print(v, type(v))
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    SENTRY_DSN: Optional[HttpUrl] = None

    @validator("SENTRY_DSN", pre=True)
    def sentry_dsn_can_be_blank(cls, v: str) -> Optional[str]:
        if len(v) == 0:
            return None
        return v

    POSTGRES_PORT: str = "5432"
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None
    ENVIRONMENT: str = 'development'

    @validator('PROD_ENV', pre=True)
    def validate_environment(cls, value):
        prod_env = 'production'
        current_env = os.environ.get('MODE', prod_env)
        if current_env == prod_env:
            return True
        return False

    PROD_ENV: bool = True
    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48
    EMAIL_TEMPLATES_DIR: str = "/app/app/email-templates/build"
    EMAILS_ENABLED: bool = False

    @validator("EMAILS_ENABLED", pre=True)
    def get_emails_enabled(cls, v: bool, values: Dict[str, Any]) -> bool:
        return bool(
            values.get("SMTP_HOST")
            and values.get("SMTP_PORT")
            and values.get("EMAILS_FROM_EMAIL")
        )

    REDIS_URL: Optional[str] = "redis://queue:6379"
    REDIS_BROKER_URL: Optional[str] = "redis://queue:6379/1"
    REDIS_ENABLE_UTC: bool = True

    EMAIL_TEST_USER: EmailStr = "admin@osintbuddy.com"
    FIRST_SUPERUSER: EmailStr
    FIRST_SUPERUSER_FULLNAME: str
    FIRST_SUPERUSER_PASSWORD: str
    USERS_OPEN_REGISTRATION: bool = False
    BASE_URI: str = (
        f'postgresql://{os.getenv("POSTGRES_USER")}'
        f':{os.getenv("POSTGRES_PASSWORD")}'
        f'@{os.getenv("POSTGRES_SERVER")}'
    )

    NEO4J_URI: str
    NEO4J_USER: str
    NEO4J_PASSWORD: str

    class Config:
        case_sensitive = True


settings = Settings()
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class RunConfig(BaseModel):
    host: str = "localhost"
    port: int = 8080

class ApiPrefix(BaseModel):
    prefix: str = ""

class DatabaseConfig(BaseModel):
    user: str
    password: str
    host: str
    port: str
    db: str
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10

    @property
    def url(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=self.user,
            password=self.password,
            host=self.host,
            port=int(self.port),
            path=self.db
        )

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(BASE_DIR / ".env.template", BASE_DIR / ".env"),
        case_sensitive=False,
        env_nested_delimiter="__",
        extra="ignore"
    )

    # Bot settings
    bot_token: str
    
    # Database settings
    postgres_user: str
    postgres_password: str
    postgres_host: str
    postgres_port: str
    postgres_db: str
    
    # API settings
    api_base_url: str
    
    # Server settings
    host: str = "localhost"
    port: int = 8080
    
    # Logging settings
    log_level: str
    log_file: str
    
    # Security
    secret_key: str

    @property
    def db(self) -> DatabaseConfig:
        return DatabaseConfig(
            user=self.postgres_user,
            password=self.postgres_password,
            host=self.postgres_host,
            port=self.postgres_port,
            db=self.postgres_db
        )

    run: RunConfig = RunConfig()
    api: ApiPrefix = ApiPrefix()

settings = Settings()
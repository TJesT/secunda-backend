from enum import Enum
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import JsonValue, field_validator
import colorlog


class LogLevel(Enum):
    NOTSET = colorlog.NOTSET
    INFO = colorlog.INFO
    DEBUG = colorlog.DEBUG
    WARNING = colorlog.WARNING
    ERROR = colorlog.ERROR
    CRITICAL = colorlog.CRITICAL


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="APP_",
        extra="ignore",
        env_file=".env",
    )

    log_level: LogLevel = LogLevel.NOTSET

    @field_validator("log_level", mode="before")
    @classmethod
    def parse_log_level(cls, v):
        if isinstance(v, LogLevel):
            return v
        if isinstance(v, str):
            try:
                return LogLevel[v.upper()]
            except KeyError:
                raise ValueError(f"Invalid log level: {v}")
        raise TypeError(f"Expected str or LogLevel, got {type(v).__name__}")


class PostgresSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="PG_",
        extra="ignore",
        env_file=".env",
    )

    driver: str = "asyncpg+postgres"
    username: str
    password: str
    host: str
    port: int
    db: str

    @property
    def dsn(self) -> str:
        return (
            f"{self.driver}://{self.username}:{self.password}"
            f"@{self.host}:{self.port}/{self.db}"
        )


class TreeSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="TREE_", extra="ignore", env_file=".env"
    )

    struct: JsonValue = []
    max_height: int = 3


app_settings = AppSettings()
postgres_settings = PostgresSettings()
tree_settings = TreeSettings()

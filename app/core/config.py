"""
Configuration management for the application using Pydantic BaseSettings.

This module loads application settings from environment variables (.env files)
and defines nested configuration structures for the database, API prefixes, and
application runtime parameters.
"""

from pathlib import Path

from pydantic import BaseModel, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ENV_PATH = PROJECT_ROOT / ".env"
ENV_TEMPLATE_PATH = PROJECT_ROOT / ".env.template"


class DatabaseConfig(BaseModel):
    """
    Configuration settings for the PostgreSQL database connection.

    Attributes:
        url: The database connection URL (DSN).
        echo: If True, SQLAlchemy will log all SQL statements to stderr.
        echo_pool: If True, the connection pool will log debug information.
        pool_size: The number of connections to keep open inside the pool.
        max_overflow: The maximum number of connections that can be opened beyond the pool_size.
        naming_convention: A dictionary defining naming conventions for constraints and indexes.
    """
    url: PostgresDsn
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10

    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }


class RunConfig(BaseModel):
    """
    Configuration for the application server's host and port.

    Attributes:
        host: The network interface the server should listen on (e.g., "0.0.0.0").
        port: The port the server should listen on (e.g., 8000).
    """
    host: str = "0.0.0.0"
    port: int = 8000


class ApiV1Prefix(BaseModel):
    """
    API V1 endpoint prefixes.

    Attributes:
        prefix: The base prefix for API v1 endpoints (e.g., "/v1").
        order: The specific prefix for order-related endpoints (e.g., "/orders").
    """
    prefix: str = "/v1"
    order: str = "/orders"


class ApiPrefix(BaseModel):
    """
    Overall API prefixes structure.

    Attributes:
        prefix: The main entry prefix for the API (e.g., "/api").
        v1: Nested configuration for version 1 API endpoints.
    """
    prefix: str = "/api"
    v1: ApiV1Prefix = ApiV1Prefix()


class Settings(BaseSettings):
    """
    Main application settings loaded from environment variables.

    Settings are loaded from .env files, prefixed with APP_CONFIG__,
    and use nested delimiters for configuration hierarchy.

    Attributes:
        run: Runtime configuration (host/port).
        api: API prefix configuration.
        db: Database connection configuration.
    """
    model_config = SettingsConfigDict(
        env_file=(ENV_TEMPLATE_PATH, ENV_PATH),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
    )
    run: RunConfig = RunConfig()
    api: ApiPrefix = ApiPrefix()
    db: DatabaseConfig


settings = Settings()

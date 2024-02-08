import os

from dotenv import load_dotenv

load_dotenv(".env", verbose=True)


class DatabaseMixin:
    PG_DSN: str = os.environ.get(
        "PG_DSN", "postgresql://postgres:postgres@localhost:5432/montebot"
    )
    PG_POSTGRES_DSN: str = os.environ.get(
        "PG_POSTGRES_DSN", "postgresql://postgres:postgres@localhost:5432/postgres"
    )

    PG_SCHEMA: str = os.environ.get("PG_SCHEMA", "public")

    PGSSLMODE: str = os.environ.get("DB_ASYNCPG_SSL", "prefer")

    DB_TIMEOUT: int = os.environ.get("DB_TIMEOUT", 60)

    POOL_MAX_SIZE: int = os.environ.get("POOL_MAX_SIZE", 10)
    POOL_MIN_SIZE: int = os.environ.get("POOL_MIN_SIZE", 1)
    POOL_QUERIES: int = os.environ.get("POOL_QUERIES", 10)
    POOL_LIFETIME: int = os.environ.get("POOL_LIFETIME", 60)


class GetApiTokenBot:
    API_TOKEN_BOT: str = os.environ.get("API_TOKEN_BOT")


class EnvironmentInfo:
    MODE: str = os.environ.get("MODE", "prod")
    DEBUG: bool = os.environ.get("DEBUG", False)


class ChatBotAdminApi:
    APP_HOST: str = os.environ.get("APP_HOST", "localhost")
    APP_PORT: str = os.environ.get("APP_PORT", 8000)
    FERNET_NEXT_PAGE: str = os.environ.get(
        "FERNET_NEXT_PAGE", "lZ8sCaqR7sNi4Wt7H4wFIePV-gCfDAYGCmN8GSA1NDQ="
    )
    JWT_TOKEN_ACCESS_KEY: str = os.environ.get(
        "JWT_TOKEN_ACCESS_KEY",
        "fc3765d2f2743a6337de309901d7d61c90dbab7812b9a18d532aeaf88202a7e7",
    )
    JWT_TOKEN_ALGORITHM: str = os.environ.get("JWT_TOKEN_ALGORITHM", "HS256")


class Config(
    DatabaseMixin,
    GetApiTokenBot,
    EnvironmentInfo,
    ChatBotAdminApi,
):
    pass


config = Config()

import logging
from functools import lru_cache
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    project_name: str = "FastAPI Auth Starter"
    database_url: str
    alembic_database_url: str
    redis_url: str
    jwt_secret_key: str
    jwt_refresh_secret_key: str
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    cookie_secure: bool = True
    rate_limit_per_minute: int = 10
    log_level: str = "INFO"
    is_production: bool = False
    ENV:str="production"

    class Config:
        env_file = r"D:\\fastapi-auth-starter-main\.env"
        extra = 'ignore'
        case_sensitive = False

    @classmethod
    def for_env(cls, env_name: str):
        env_file = f".env.{env_name}"
        return cls(_env_file=env_file)


@lru_cache()
def get_settings(env: str | None = None) -> Settings:

    env = os.environ.get("ENV")
    logging.info(f"From Conf ENV: {env}")
    if env == "test":
        return Settings(
            database_url="sqlite+aiosqlite:///:memory:",
            alembic_database_url="sqlite+aiosqlite:///:memory:",
            redis_url="redis://localhost:6379/0",
            jwt_secret_key="test-secret",
            jwt_refresh_secret_key="test-refresh-secret",
            is_production=False,
            log_level="DEBUG"
        )
    else:
        return Settings()


import logging
import sys
import coloredlogs


def setup_logging(debug: bool = False):
    log_level = logging.DEBUG if debug else logging.INFO
    logger = logging.getLogger()

    logger.setLevel(log_level)
    logger.propagate = False

    if not logger.handlers:
        handler = logging.StreamHandler()
        logger.addHandler(handler)

    coloredlogs.install(
        level=log_level,
        logger=logger,
        fmt="%(asctime)s | %(name)s | %(filename)s:%(lineno)d | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        isatty=True,
        force_color=True,
        level_styles={
            'debug': {'color': 'blue'},
            'info': {'color': 'green'},
            'warning': {'color': 'yellow'},
            'error': {'color': 'red'},
            'critical': {'color': 'red', 'bold': True},
        }
    )

    return logger


logger = setup_logging(debug=True)

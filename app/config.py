import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = os.environ["DATABASE_URL"]
    echo_sql: bool = True
    test: bool = False
    project_name: str = "Auth API"
    oauth_token_secret: str = os.environ["SECRET"]
    log_level: str = "DEBUG"
    domain: str = os.environ["DOMAIN"]


settings = Settings()  # type: ignore

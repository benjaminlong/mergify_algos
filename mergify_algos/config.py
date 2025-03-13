from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings, cli_parse_none_str="void"):
    app_name: str = "Mergify Algo API"
    github_token: Optional[str] = None

    model_config = SettingsConfigDict(env_file="../.env")


settings = Settings()

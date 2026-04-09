import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings resolved from environment variables."""

    openai_api_key: str = os.environ.get("OPENAI_API_KEY", "")
    openai_model: str = "gpt-4o-mini"
    openai_whisper_model: str = "whisper-1"
    use_mocks: bool = False

    model_config = {"env_file": None, "case_sensitive": False}


settings = Settings()

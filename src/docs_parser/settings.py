from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class OpenAISettings(BaseSettings):
    api_key: str = Field(..., description="OpenAI API key")
    model: str = Field(
        default="gpt-4.5-preview-2025-02-27", description="OpenAI model name"
    )


class Settings(BaseSettings):
    openai: OpenAISettings
    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()  # type: ignore

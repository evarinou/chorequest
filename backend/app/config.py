from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Datenbank
    database_url: str = "postgresql+asyncpg://chorequest:chorequest@db:5432/chorequest"

    # API-Key für Authentifizierung
    api_key: str = "changeme"

    # Claude AI
    claude_api_key: str = ""
    claude_model: str = "claude-haiku-4-5-20250929"

    # Home Assistant
    ha_url: str = ""
    ha_webhook_id: str = ""

    # Allgemein
    timezone: str = "Europe/Berlin"
    app_name: str = "ChoreQuest"
    debug: bool = False

    model_config = {"env_file": ".env", "env_prefix": "CHOREQUEST_"}


settings = Settings()

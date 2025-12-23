from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "EvaraTDS Platform"
    API_V1_STR: str = "/api/v1"

    # ThingSpeak Secrets
    THINGSPEAK_CHANNEL_ID: str = "2713286"  # Default to your channel
    THINGSPEAK_READ_KEY: str = "EHEK3A1XD48TY98B"  # Private channel read key

    # Thresholds
    TDS_ALERT_THRESHOLD: float = 150.0

    class Config:
        env_file = ".env"


settings = Settings()

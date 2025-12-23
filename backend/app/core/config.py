from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "EvaraTDS Platform"
    API_V1_STR: str = "/api/v1"

    # ThingSpeak Secrets
    THINGSPEAK_CHANNEL_ID: str
    THINGSPEAK_READ_KEY: str = ""

    # Thresholds
    TDS_ALERT_THRESHOLD: float = 150.0

    class Config:
        env_file = ".env"


settings = Settings()
